from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid

from ..schemas.decision import Decision
from ..schemas.enums import MissionType
from ..exceptions import DecisionEngineException
from ..approval.gate import ApprovalGate
from app.schemas.research import ResearchRequest


class ReasoningEngine:
    """Reasoning Engine for the Digital Export Manager.
    
    Produces Decisions from user requests by querying Company Knowledge Layer
    and Memory Interface, evaluating options against company rules.
    """

    def __init__(self, knowledge_provider_registry=None, memory_provider=None, approval_gate=None, knowledge_provider=None, llm_registry=None):
        self.knowledge_provider_registry = knowledge_provider_registry
        self.knowledge_provider = knowledge_provider
        self.memory_provider = memory_provider
        self.approval_gate = approval_gate or ApprovalGate()
        self.llm_registry = llm_registry

    async def _get_llm_provider(self):
        if not self.llm_registry:
            return None
        return self.llm_registry.get_provider("gemini")

    async def _enhance_candidates_with_llm(self, intent: str, scored_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        provider = await self._get_llm_provider()
        if not provider or not scored_candidates:
            return scored_candidates

        best = scored_candidates[0]
        if best.get("confidence", 0) >= 0.5:
            return scored_candidates

        try:
            paths = [c["path"] for c in scored_candidates]
            prompt = f"Which path best matches this intent? Options: {', '.join(paths)}. Intent: {intent}. Answer with only the path name."
            response = await provider.generate(prompt=prompt, parameters={"max_output_tokens": 20})
            suggested = response.content.strip().lower()
            for c in scored_candidates:
                if c["path"] in suggested:
                    c["score"] = max(c.get("score", c["confidence"]), 0.6)
                    break
        except Exception:
            pass

        scored_candidates.sort(key=lambda c: c.get("score", c.get("confidence", 0)), reverse=True)
        return scored_candidates

    async def _enhance_reasoning_with_llm(self, intent: str, chosen_path: str, base_reasoning: str, research: Optional[Dict[str, Any]] = None) -> str:
        provider = await self._get_llm_provider()
        if not provider:
            return base_reasoning

        try:
            research_summary = self._summarize_research_for_prompt(research or {})
            prompt = f"Improve this reasoning text to be more natural and helpful. Keep it brief. Original: {base_reasoning}. Research evidence: {research_summary}. Keep the research findings and evidence references accurate; do not invent numbers or sources."
            response = await provider.generate(prompt=prompt, parameters={"max_output_tokens": 100})
            enhanced = response.content.strip()
            if enhanced and len(enhanced) > 10:
                return enhanced
        except Exception:
            pass

        return base_reasoning

    @staticmethod
    def _summarize_research_for_prompt(research: Dict[str, Any]) -> str:
        if not research:
            return ""

        parts = []

        status = research.get("status")
        if status:
            parts.append(f"Research status: {status}")

        sources_consulted = research.get("sources_consulted") or []
        if sources_consulted:
            parts.append(f"Sources consulted: {', '.join(sources_consulted)}")

        findings = research.get("findings") or []
        if findings:
            parts.append(f"Findings count: {len(findings)}")
            for finding in findings[:3]:
                if isinstance(finding, dict):
                    topic = finding.get("topic") or finding.get("title") or ""
                    content = finding.get("content") or finding.get("summary") or ""
                    if topic:
                        parts.append(f"- {topic}")
                    if content:
                        parts.append(f"  {content}")
                    evidence = finding.get("evidence") or []
                    if evidence:
                        evidence_items = []
                        for ev in evidence[:3]:
                            if isinstance(ev, dict):
                                source_id = ev.get("source_id") or ""
                                excerpt = ev.get("content_excerpt") or ev.get("summary") or ""
                                if source_id:
                                    evidence_items.append(f"{source_id}: {excerpt[:120]}")
                        if evidence_items:
                            parts.append(f"  Evidence: {' | '.join(evidence_items)}")

        errors = research.get("errors")
        if errors:
            parts.append(f"Errors: {errors}")

        return "; ".join(parts)

    async def reason(self, session_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Produce a Decision from a user request.

        Args:
            session_id: Session identifier
            request: Dict containing:
                - intent: str - user request text
                - parameters: Optional[Dict[str, Any]]
                - context: Optional[Dict[str, Any]]

        Returns:
            Dict conforming to Decision schema
        """
        try:
            intent = request.get("intent", "")
            parameters = request.get("parameters", {}) or {}
            request_context = request.get("context", {}) or {}

            candidates = self._map_intent_to_candidates(intent, parameters)
            if not candidates:
                candidates = [{"path": "search", "mission_type": MissionType.SEARCH_ENTITIES.value, "confidence": 0.5, "match_count": 0, "score": 0.5}]

            memories = await self._query_memory(session_id, intent)
            knowledge = await self._query_knowledge(intent, parameters)
            research = await self._query_external_research(intent, parameters)

            # Preserve orchestration metadata in request_context
            orchestration_meta = getattr(self, "_last_orchestration_meta", None)
            if orchestration_meta:
                request_context["knowledge_orchestration"] = orchestration_meta

            candidates = self._apply_memory_biases(candidates, memories)
            scored_candidates = self._evaluate_options(candidates, memories, knowledge, parameters)

            scored_candidates = self._apply_goal_plan_awareness(scored_candidates, request_context)

            scored_candidates = await self._enhance_candidates_with_llm(intent, scored_candidates)

            chosen_path, alternatives = self._select_best_option(scored_candidates)

            if (
                isinstance(research, dict)
                and research.get("status") == "completed"
                and self._should_trigger_external_research(intent)
            ):
                chosen_path = "research"
                alternatives = [alt for alt in alternatives if alt != "research"]

            is_destructive, approval_status = self._check_approval(chosen_path, intent, parameters)

            reasoning = self._build_reasoning(
                chosen_path=chosen_path,
                scored_candidates=scored_candidates,
                memories=memories,
                knowledge=knowledge,
                research=research,
            )

            reasoning = await self._enhance_reasoning_with_llm(intent, chosen_path, reasoning, research=research)

            decision = Decision(
                decision_id=str(uuid.uuid4()),
                session_id=session_id,
                reasoning=reasoning,
                chosen_path=chosen_path,
                alternatives=alternatives,
                context={
                    "intent": intent,
                    "parameters": parameters,
                    "request_context": request_context,
                    "memories": memories,
                    "knowledge": knowledge,
                    "research": research,
                    "candidates": scored_candidates,
                    "requires_approval": is_destructive,
                },
                created_at=datetime.now(timezone.utc),
                requires_approval=is_destructive,
                approval_status=approval_status,
            )

            # Persistence hook: Store significant decisions
            if self.memory_provider:
                try:
                    await self.memory_provider.store(
                        session_id=session_id,
                        key=f"decision:{decision.decision_id}",
                        value=decision.model_dump(mode="json"),
                        memory_type="decision",
                        importance=8,
                    )
                except Exception:
                    # Graceful degradation: Decision still returns to user even if persistence fails
                    pass

            return decision.model_dump()
        except DecisionEngineException:
            raise
        except Exception as e:
            raise DecisionEngineException(f"Reasoning failed: {e}")

    def _map_intent_to_candidates(self, intent: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map intent to candidate chosen_path values with deterministic scoring."""
        intent_lower = intent.lower().strip()
        candidates = []

        path_patterns = [
            ("shipping", MissionType.CREATE_SHIPMENT, ["شحن", "shipment", "shipping", "ship", "إرسال"]),
            ("eta", MissionType.SUBMIT_INVOICE, ["فاتورة", "invoice", "eta", "قيمة مضافة"]),
            ("customs", MissionType.FILE_CUSTOMS, ["جمارك", "customs", "تصريح", "declaration"]),
            ("document", MissionType.GENERATE_DOCUMENT, ["وثيقة", "document", "مستند", "paperwork"]),
            ("search", MissionType.SEARCH_ENTITIES, ["بحث", "search", "ابحث", "اعثر"]),
            ("dashboard", MissionType.GET_DASHBOARD, ["لوحة", "dashboard", "إحصائيات", "stats"]),
            ("notification", MissionType.SEND_NOTIFICATION, ["إشعار", "notification", "تنبيه", "alert"]),
            ("workflow", MissionType.TRANSITION_WORKFLOW, ["إجراء", "workflow", "procedure", "sop"]),
        ]

        for path_key, mission_type, keywords in path_patterns:
            match_score = 0
            for keyword in keywords:
                if keyword in intent_lower:
                    match_score += 1

            if match_score > 0:
                confidence = min(match_score / len(keywords), 1.0)
                candidates.append({
                    "path": path_key,
                    "mission_type": mission_type.value,
                    "confidence": confidence,
                    "match_count": match_score,
                })

        candidates.sort(key=lambda c: c["confidence"], reverse=True)
        return candidates

    def _apply_memory_biases(self, candidates: List[Dict[str, Any]], memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Active recall: Apply biases/constraints based on memory content."""
        if not memories:
            return candidates

        for memory in memories:
            mem_type = memory.get("memory_type")
            value = memory.get("value", {})
            if isinstance(value, str):
                import json
                try:
                    value = json.loads(value)
                except Exception:
                    value = {}

            if not isinstance(value, dict):
                continue

            for candidate in candidates:
                path = candidate.get("path")
                candidate.setdefault("score", candidate["confidence"])

                if mem_type == "standing_order" and value.get("forbidden_path") == path:
                    candidate["score"] = -100.0

                elif mem_type == "preference" and value.get("preferred_path") == path:
                    candidate["score"] += 0.5

                elif mem_type == "decision" and value.get("chosen_path") == path:
                    candidate["score"] += 0.3

        return candidates

    def _evaluate_options(
        self,
        candidates: List[Dict[str, Any]],
        memories: List[Dict[str, Any]],
        knowledge: List[Dict[str, Any]],
        parameters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Evaluate and score candidates using deterministic rules and provider data."""
        evaluated = []

        for candidate in candidates:
            score = candidate.get("score", candidate["confidence"])

            if parameters:
                score += 0.1

            for k in knowledge:
                if isinstance(k, dict):
                    if k.get("path") == candidate["path"]:
                        score += 0.15

            evaluated.append({
                **candidate,
                "score": score,
            })

        evaluated.sort(key=lambda c: c["score"], reverse=True)
        return evaluated

    def _apply_goal_plan_awareness(
        self,
        candidates: List[Dict[str, Any]],
        request_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Goal/Plan-aware qualification pass.

        - Reads goal_id/plan_id from request_context as opaque hints.
        - Reads plan_constraints from request_context if present.
        - Filters out candidates whose path is explicitly forbidden by Plan constraints.
        - Does NOT change baseline scoring formula or weights.
        - Returns candidates unchanged if no Goal/Plan context.
        """
        if not request_context:
            return candidates

        goal_id = request_context.get("goal_id")
        plan_id = request_context.get("plan_id")
        if not goal_id or not plan_id:
            return candidates

        plan_constraints = request_context.get("plan_constraints") or []
        if not plan_constraints:
            return candidates

        forbidden_paths = set()
        for constraint in plan_constraints:
            if isinstance(constraint, dict):
                for path in constraint.get("forbidden_paths", []):
                    forbidden_paths.add(path)

        if not forbidden_paths:
            return candidates

        filtered = [c for c in candidates if c.get("path") not in forbidden_paths]
        return filtered if filtered else candidates

    def _select_best_option(self, scored_candidates: List[Dict[str, Any]]) -> tuple[str, List[str]]:
        """Select the best option and return alternatives."""
        if not scored_candidates:
            raise DecisionEngineException("No candidates available for selection")

        best = scored_candidates[0]
        best_score = best.get("score", best.get("confidence", 0))

        if best_score < 0:
            return "search", [c["path"] for c in scored_candidates]

        if best_score < 0.3:
            return "search", [c["path"] for c in scored_candidates]

        chosen_path = best["path"]
        alternatives = [c["path"] for c in scored_candidates[1:]]

        return chosen_path, alternatives

    def _check_approval(self, chosen_path: str, intent: str, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Check if the chosen path requires approval."""
        return self.approval_gate.check_approval(chosen_path, intent, parameters)

    def _build_reasoning(
        self,
        chosen_path: str,
        scored_candidates: List[Dict[str, Any]],
        memories: List[Dict[str, Any]],
        knowledge: List[Dict[str, Any]],
        research: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build human-readable reasoning for the decision."""
        if not scored_candidates:
            return "No candidates available for decision."

        best = scored_candidates[0]
        confidence = best.get("confidence", 0)
        score = best.get("score", 0)
        match_count = best.get("match_count", 0)
        is_fallback = match_count == 0

        if is_fallback:
            reasoning_parts = [
                f"No matching intent found. Using fallback: '{chosen_path}' (confidence {confidence:.2f})."
            ]
        else:
            reasoning_parts = [
                f"Selected '{chosen_path}' with confidence {confidence:.2f} (score {score:.2f})."
            ]

        if memories:
            memory_types = [m.get("memory_type") for m in memories if isinstance(m, dict)]
            memory_types = [t for t in memory_types if t]
            if memory_types:
                unique_types = sorted(set(memory_types))
                reasoning_parts.append(f"Memory: {len(memories)} entries from {', '.join(unique_types)}.")
            else:
                reasoning_parts.append(f"Memory: {len(memories)} entries considered.")

        if knowledge:
            sources = []
            for k in knowledge:
                if isinstance(k, dict):
                    source = k.get("source_id") or k.get("path")
                    if source:
                        sources.append(source)
            if sources:
                unique_sources = sorted(set(sources))[:3]
                reasoning_parts.append(f"Knowledge: {len(knowledge)} entries from {', '.join(unique_sources)}.")
            else:
                reasoning_parts.append(f"Knowledge: {len(knowledge)} entries considered.")

        if research and isinstance(research, dict):
            research_parts = self._summarize_research_for_prompt(research)
            if research_parts:
                reasoning_parts.append(f"Research: {research_parts}")

        if len(scored_candidates) > 1:
            alternatives = [c["path"] for c in scored_candidates[1:]]
            reasoning_parts.append(f"Alternatives: {', '.join(alternatives)}.")

        return " ".join(reasoning_parts)

    async def _query_memory(self, session_id: str, intent: str) -> List[Dict[str, Any]]:
        """Query MemoryProvider with graceful degradation."""
        if not self.memory_provider:
            return []

        try:
            return await self.memory_provider.recall(session_id, intent, limit=10)
        except Exception:
            return []

    async def _query_knowledge_legacy(self, intent: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Legacy knowledge query — iterates all providers, extends results blindly.

        Byte-for-byte equivalent to the original _query_knowledge() at lines 336-379.
        Used only as fallback when KnowledgeOrchestrator is not attached.
        """
        results: List[Dict[str, Any]] = []

        if self.knowledge_provider_registry is not None:
            try:
                providers_info = await self.knowledge_provider_registry.list_providers()
                for source in providers_info:
                    source_id = source.get("id")
                    if not source_id:
                        continue
                    try:
                        data = await self.knowledge_provider_registry.query(
                            source_id=source_id,
                            query=intent,
                            context=parameters,
                            limit=10,
                        )
                        if isinstance(data, dict):
                            source_results = data.get("results")
                            if isinstance(source_results, list):
                                results.extend(source_results)
                    except Exception:
                        continue
            except Exception:
                pass

        if not results and self.knowledge_provider is not None:
            try:
                data = await self.knowledge_provider.query(
                    intent,
                    context=parameters,
                    limit=10,
                )
                if isinstance(data, dict):
                    provider_results = data.get("results")
                    if isinstance(provider_results, list):
                        results.extend(provider_results)
                elif isinstance(data, list):
                    results.extend(data)
            except Exception:
                pass

        return results

    @staticmethod
    def _extract_research_parameters(intent: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        intent_lower = intent.lower()
        extracted: Dict[str, Any] = {}

        country_map = {
            "مصر": "818",
            "Egypt": "818",
            "الأردن": "400",
            "Jordan": "400",
        }

        commodity_map = {
            "خضر": "07",
            "vegetables": "07",
            "فواكه": "08",
            "fruits": "08",
        }

        for name, code in country_map.items():
            if name.lower() in intent_lower:
                if name.lower() in ["مصر", "egypt"]:
                    extracted["reporter"] = code
                elif name.lower() in ["الأردن", "jordan"]:
                    extracted["partner"] = code

        for name, code in commodity_map.items():
            if name.lower() in intent_lower:
                extracted.setdefault("commodities", []).append(code)

        if "commodities" in extracted:
            unique = list(dict.fromkeys(extracted["commodities"]))
            extracted["commodities"] = unique

        return extracted

    async def _query_external_research(self, intent: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query External Research Capability (WP-34) when request is suitable."""
        orchestrator = getattr(self, "_research_orchestrator", None)
        if orchestrator is None:
            return []

        if not self._should_trigger_external_research(intent):
            return []

        extracted = self._extract_research_parameters(intent, parameters)

        context = {
            "session_id": parameters.get("session_id"),
            "user_id": parameters.get("user_id"),
            "request_context": parameters.get("context", {}),
        }
        if extracted.get("reporter"):
            context["reporter"] = extracted["reporter"]
        if extracted.get("partner"):
            context["partner"] = extracted["partner"]

        scope = parameters.get("scope") or {
            "domains": parameters.get("domains"),
            "regions": parameters.get("regions"),
            "time_ranges": parameters.get("time_ranges"),
        }
        if extracted.get("commodities"):
            scope["commodities"] = extracted["commodities"]
        if not scope.get("regions") and (extracted.get("reporter") or extracted.get("partner")):
            scope["regions"] = [
                code for code in [extracted.get("reporter"), extracted.get("partner")] if code
            ]

        request = ResearchRequest(
            goal=intent,
            context=context,
            scope=scope,
            constraints=parameters.get("constraints"),
        )
        request_id = f"req_{uuid.uuid4().hex[:12]}"

        try:
            result = await orchestrator.execute(request, request_id)
        except Exception:
            return []

        if hasattr(result, "model_dump"):
            return result.model_dump(mode="json")
        if isinstance(result, dict):
            return result
        return []

    @staticmethod
    def _should_trigger_external_research(intent: str) -> bool:
        """Return True only when the request likely needs external market/buyer/research data."""
        intent_lower = intent.lower().strip()
        keywords = [
            "market", "buyer", "buyers", "opportunity", "opportunities",
            "study", "research", "external", "potential", "demand", "export",
            "سوق", "مشترين", "مشتر", "فرص", "فرصة", "دراسة", "بحث", "تصدير",
        ]
        return any(keyword in intent_lower for keyword in keywords)

    async def _query_knowledge(self, intent: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query knowledge providers via KnowledgeOrchestrator if attached, else legacy fallback."""
        orchestrator = getattr(self, "_knowledge_orchestrator", None)
        if orchestrator is not None and self.knowledge_provider_registry is not None:
            result = await orchestrator.orchestrate(
                query=intent,
                context=parameters,
                limit=10,
            )

            # Cache orchestration metadata for Decision.context
            self._last_orchestration_meta = result.get("orchestration")

            return result.get("results", [])

        return await self._query_knowledge_legacy(intent, parameters)
