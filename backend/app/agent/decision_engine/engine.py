from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid

from ..schemas.decision import Decision
from ..schemas.enums import MissionType
from ..exceptions import DecisionEngineException
from ..approval.gate import ApprovalGate


class ReasoningEngine:
    """Reasoning Engine for the Digital Export Manager.
    
    Produces Decisions from user requests by querying Company Knowledge Layer
    and Memory Interface, evaluating options against company rules.
    """

    def __init__(self, knowledge_provider_registry=None, memory_provider=None, approval_gate=None, knowledge_provider=None):
        self.knowledge_provider_registry = knowledge_provider_registry
        self.knowledge_provider = knowledge_provider
        self.memory_provider = memory_provider
        self.approval_gate = approval_gate or ApprovalGate()

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

            candidates = self._apply_memory_biases(candidates, memories)
            scored_candidates = self._evaluate_options(candidates, memories, knowledge, parameters)
            chosen_path, alternatives = self._select_best_option(scored_candidates)

            is_destructive, approval_status = self._check_approval(chosen_path, intent, parameters)

            reasoning = self._build_reasoning(
                chosen_path=chosen_path,
                scored_candidates=scored_candidates,
                memories=memories,
                knowledge=knowledge,
            )

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

    async def _query_knowledge(self, intent: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query KnowledgeProviderRegistry or single KnowledgeProvider with graceful degradation."""
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
