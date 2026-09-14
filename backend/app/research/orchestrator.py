from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
import uuid

from app.schemas.research import ResearchRequest, ResearchResult, FindingItem, DiscoveryRequest, Evidence
from app.research.retrieval.contracts import ContentProcessor, RetrievedContent, RetrievalResult, RetrievalStatus, SourceExecutionStatus
from app.research.retrieval.orchestrator import RetrievalOrchestrator
from app.research.sources.registry import SourceRegistry
from app.research.sources.discovery import SourceDiscovery
from app.research.evidence.contracts import DefaultEvidenceCapture, EvidenceCapture
from app.research.result import DefaultResultStructurer, ResultStructurer
from app.research.quality import DefaultVerifier, FailureHandler, Verifier
from app.research.retrieval.query_enhancer import QueryEnhancer
from app.research.query_planner import ResearchQueryPlanner, _stable_hash
from app.schemas.research_query import ResearchQuery, ResearchQueryPlan

logger = logging.getLogger(__name__)


def _is_meaningful_retrieval_content(raw_content: Any) -> bool:
    if raw_content is None:
        return False
    if isinstance(raw_content, str):
        return bool(raw_content.strip())
    if isinstance(raw_content, dict):
        results = raw_content.get("results")
        if isinstance(results, list) and len(results) == 0:
            return False
        return bool(raw_content)
    if isinstance(raw_content, list):
        return len(raw_content) > 0
    return True


class StageResult:
    def __init__(self, stage_name: str, success: bool, data: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        self.stage_name = stage_name
        self.success = success
        self.data = data or {}
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {"stage_name": self.stage_name, "success": self.success, "data": self.data, "error": self.error}


class ResearchContext:
    def __init__(self, request: ResearchRequest, request_id: str):
        self.request = request
        self.request_id = request_id
        self.current_stage_index = 0
        self.stage_results: List[StageResult] = []
        self.findings: List[FindingItem] = []
        self.sources_consulted: List[str] = []
        self.sources_failed: List[str] = []
        self.source_execution_statuses: Dict[str, str] = {}
        self.evidence: List[Evidence] = []
        self.errors: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self.query_plan: Optional[ResearchQueryPlan] = None
        self._stop = False

    def mark_stop(self, reason: str) -> None:
        self._stop = True
        self.errors.append(reason)

    def should_stop(self) -> bool:
        return self._stop

    def record_stage_result(self, result: StageResult) -> None:
        self.stage_results.append(result)
        if not result.success:
            self.errors.append(f"{result.stage_name} failed: {result.error}")
            self._stop = True

    def to_result(self, status: str) -> ResearchResult:
        now = datetime.utcnow()
        return ResearchResult(
            request_id=self.request_id,
            status=status,
            goal=self.request.goal,
            findings=self.findings,
            sources_consulted=self.sources_consulted,
            sources_failed=self.sources_failed,
            errors=self.errors if self.errors else None,
            created_at=now,
            completed_at=now,
            metadata={**self.metadata, "stage_results": [r.to_dict() for r in self.stage_results]},
            source_execution_statuses=self.source_execution_statuses or None,
        )


class ResearchStage(ABC):
    name: str = "unnamed_stage"

    @abstractmethod
    async def execute(self, context: ResearchContext) -> ResearchContext:
        ...


class PlanningStage(ResearchStage):
    name = "planning"

    def __init__(self, planner: Optional[ResearchQueryPlanner] = None):
        self._planner = planner

    async def execute(self, context: ResearchContext) -> ResearchContext:
        try:
            if self._planner is not None:
                query_plan = self._planner.plan(context.request)
                context.query_plan = query_plan
                context.metadata["plan"] = {
                    "sub_queries": [q.query for q in query_plan.queries],
                    "source_selection_strategy": "scope_based",
                    "retrieval_parameters": {},
                    "intent_profile": query_plan.intent_profile,
                    "decomposition_strategy": query_plan.decomposition_strategy,
                    "query_count": len(query_plan.queries),
                }
            else:
                sub_queries = self._build_sub_queries(context.request)
                context.metadata["plan"] = {"sub_queries": sub_queries, "source_selection_strategy": "scope_based", "retrieval_parameters": {}}
            context.record_stage_result(StageResult(self.name, True))
        except Exception as exc:
            context.record_stage_result(StageResult(self.name, False, error=str(exc)))
        return context

    def _build_sub_queries(self, request: ResearchRequest) -> List[str]:
        goal = request.goal.strip()
        return [goal] if goal else []


class DiscoveryStage(ResearchStage):
    name = "discovery"

    def __init__(self, discovery: Optional[SourceDiscovery] = None):
        self._discovery = discovery

    async def execute(self, context: ResearchContext) -> ResearchContext:
        try:
            metadata = context.metadata.setdefault("discovery", {})
            if self._discovery is None:
                metadata["discovered_sources"] = []
                metadata["queries"] = {}
                context.record_stage_result(StageResult(self.name, True, {"note": "no discovery dependency configured"}))
                return context

            queries = self._get_queries(context)
            query_discoveries: Dict[str, Dict[str, Any]] = {}
            union_source_ids: List[str] = []

            for query in queries:
                discovery_request = DiscoveryRequest(
                    goal=query.query,
                    scope=query.scope,
                    source_preferences=query.source_preferences or context.request.source_preferences,
                    constraints=context.request.constraints,
                )
                result = self._discovery.discover(discovery_request)
                source_ids = [source.source_id for source in result.discovered_sources]
                query_discoveries[query.query_id] = {
                    "query_id": query.query_id,
                    "dimension": query.dimension,
                    "source_ids": source_ids,
                    "metadata": result.discovery_metadata or {},
                }
                for source_id in source_ids:
                    if source_id not in union_source_ids:
                        union_source_ids.append(source_id)

            metadata["queries"] = query_discoveries
            metadata["discovered_sources"] = union_source_ids
            context.sources_consulted = union_source_ids
            context.record_stage_result(StageResult(self.name, True, {"queries": query_discoveries, "discovered_sources": union_source_ids}))
        except Exception as exc:
            context.record_stage_result(StageResult(self.name, False, error=str(exc)))
        return context

    def _get_queries(self, context: ResearchContext) -> List[ResearchQuery]:
        if context.query_plan and context.query_plan.queries:
            return context.query_plan.queries
        goal = context.request.goal.strip()
        if not goal:
            return []
        return [ResearchQuery(
            query_id=f"fallback_{_stable_hash(goal)}",
            dimension="general",
            purpose="Fallback query when no query plan is available",
            query=goal,
            context=context.request.context or {},
            scope=context.request.scope,
        )]


class RetrievalStage(ResearchStage):
    name = "retrieval"

    def __init__(self, retrieval_orchestrator: Optional[RetrievalOrchestrator] = None, registry: Optional[SourceRegistry] = None, query_enhancer: Optional[QueryEnhancer] = None):
        self._retrieval_orchestrator = retrieval_orchestrator
        self._registry = registry
        self._query_enhancer = query_enhancer

    def _sources_for_query(self, context: ResearchContext, query: ResearchQuery):
        discovery = context.metadata.get("discovery", {})
        query_map = discovery.get("queries", {})
        entry = query_map.get(query.query_id)
        if entry is not None:
            source_ids = entry.get("source_ids", [])
        else:
            source_ids = discovery.get("discovered_sources", []) if query.dimension == "general" else []
        if not self._registry:
            return None, source_ids
        return [source for source_id in source_ids if (source := self._registry.get(source_id))], source_ids

    async def execute(self, context: ResearchContext) -> ResearchContext:
        try:
            if self._retrieval_orchestrator is None:
                context.record_stage_result(StageResult(self.name, True, {"note": "no retrieval orchestrator configured"}))
                return context

            queries = self._get_queries(context)
            all_results: List[RetrievalResult] = []
            query_routing: Dict[str, List[str]] = {}
            for query in queries:
                sources, source_ids = self._sources_for_query(context, query)
                query_routing[query.query_id] = list(source_ids)
                if sources is None:
                    context.record_stage_result(StageResult(self.name, True, {"note": "no registry configured", "query_routing": query_routing}))
                    return context
                if not sources:
                    continue
                query_results = await self._retrieval_orchestrator.retrieve_sources(sources, query.query, context=query.context, scope=query.scope)
                for result in query_results:
                    result.metadata = result.metadata or {}
                    result.metadata["query_id"] = query.query_id
                    result.metadata["dimension"] = query.dimension
                    result.metadata["purpose"] = query.purpose
                all_results.extend(query_results)

            if self._query_enhancer is not None:
                enhanced_results = []
                for query in queries:
                    sources, _ = self._sources_for_query(context, query)
                    if sources is None or not sources:
                        continue
                    query_results = [r for r in all_results if r.metadata and r.metadata.get("query_id") == query.query_id]
                    enhanced_results.extend(await self._query_enhancer.enhance_empty_results(
                        sources=sources,
                        results=query_results,
                        query=query.query,
                        context=query.context,
                        scope=query.scope,
                    ))
                all_results = enhanced_results

            processed = await self._retrieval_orchestrator.process_results(all_results)
            context.sources_consulted = list(dict.fromkeys(
                r.source_id for r in processed
                if r.status == RetrievalStatus.SUCCESS and _is_meaningful_retrieval_content(r.content.raw_content if r.content else None)
            ))
            context.sources_failed = list(dict.fromkeys(r.source_id for r in processed if r.status != RetrievalStatus.SUCCESS))
            context.source_execution_statuses = {}
            for r in processed:
                meaningful = r.status == RetrievalStatus.SUCCESS and _is_meaningful_retrieval_content(r.content.raw_content if r.content else None)
                context.source_execution_statuses[r.source_id] = SourceExecutionStatus.SUCCESS_WITH_DATA if meaningful else (SourceExecutionStatus.SUCCESS_EMPTY if r.status == RetrievalStatus.SUCCESS else SourceExecutionStatus.FAILED)
            if context.sources_failed:
                context.errors.append(f"Retrieval failed for sources: {', '.join(context.sources_failed)}")
            context.metadata.setdefault("retrieval", {})["results"] = [r.to_dict() for r in processed]
            context.metadata["retrieval"]["query_routing"] = query_routing
            context.record_stage_result(StageResult(self.name, True, {"sources_queried": context.sources_consulted, "sources_failed": context.sources_failed, "query_routing": query_routing}))
        except Exception as exc:
            context.record_stage_result(StageResult(self.name, False, error=str(exc)))
        return context

    def _get_queries(self, context: ResearchContext) -> List[ResearchQuery]:
        if context.query_plan and context.query_plan.queries:
            return context.query_plan.queries
        goal = context.request.goal.strip()
        if not goal:
            return []
        return [ResearchQuery(query_id=f"fallback_{_stable_hash(goal)}", dimension="general", purpose="Fallback query when no query plan is available", query=goal, context=context.request.context or {}, scope=context.request.scope)]


class ProcessingStage(ResearchStage):
    name = "processing"

    def __init__(self, processor: Optional[ContentProcessor] = None):
        self._processor = processor

    async def execute(self, context: ResearchContext) -> ResearchContext:
        try:
            retrieval_results = context.metadata.get("retrieval", {}).get("results", [])
            if not retrieval_results:
                context.metadata.setdefault("processing", {})["normalized"] = True
                context.record_stage_result(StageResult(self.name, True))
                return context
            processed_items = []
            for item in retrieval_results:
                if item.get("status") == RetrievalStatus.SUCCESS and item.get("content") and self._processor:
                    content = RetrievedContent(source_id=item["content"]["source_id"], raw_content=item["content"]["raw_content"], content_type=item["content"].get("content_type"), metadata=item["content"].get("metadata", {}))
                    try:
                        processed = await self._processor.process(content)
                        processed_items.append({**item, "content": processed.to_dict()} if processed else item)
                    except Exception as exc:
                        context.record_stage_result(StageResult(self.name, False, error=str(exc)))
                        return context
                else:
                    processed_items.append(item)
            context.metadata.setdefault("processing", {})["normalized"] = True
            context.metadata["retrieval"]["results"] = processed_items
            context.record_stage_result(StageResult(self.name, True))
        except Exception as exc:
            context.record_stage_result(StageResult(self.name, False, error=str(exc)))
        return context


class EvidenceCaptureStage(ResearchStage):
    name = "evidence_capture"

    def __init__(self, registry: Optional[SourceRegistry] = None, capture: Optional[EvidenceCapture] = None):
        self._registry = registry
        self._capture = capture or DefaultEvidenceCapture()

    async def execute(self, context: ResearchContext) -> ResearchContext:
        try:
            retrieval_results = context.metadata.get("retrieval", {}).get("results", [])
            if not retrieval_results:
                context.metadata.setdefault("evidence", {})["captured"] = True
                context.record_stage_result(StageResult(self.name, True, {"note": "no retrieval results to capture"}))
                return context
            captured_evidence: List[Evidence] = []
            for item in retrieval_results:
                if item.get("status") != RetrievalStatus.SUCCESS or not item.get("content"):
                    continue
                content_dict = item["content"]
                raw_content = content_dict.get("raw_content")
                if not _is_meaningful_retrieval_content(raw_content):
                    continue
                source_id = content_dict.get("source_id") or item.get("source_id")
                source = self._registry.get(source_id) if self._registry and source_id else None
                retrieved_content = RetrievedContent(source_id=source_id or "", raw_content=raw_content, content_type=content_dict.get("content_type"), metadata=content_dict.get("metadata", {}))
                evidence = await self._capture.capture(content=retrieved_content, source=source, request_id=context.request_id, transformation="processed" if item.get("content") != content_dict else None)
                evidence.metadata = evidence.metadata or {}
                query_id = (item.get("metadata") or {}).get("query_id")
                dimension = (item.get("metadata") or {}).get("dimension")
                if query_id:
                    evidence.metadata["query_id"] = query_id
                if dimension:
                    evidence.metadata["dimension"] = dimension
                captured_evidence.append(evidence)
            context.evidence.extend(captured_evidence)
            context.metadata.setdefault("evidence", {})["captured"] = True
            context.metadata["evidence"]["count"] = len(captured_evidence)
            context.record_stage_result(StageResult(self.name, True, {"evidence_count": len(captured_evidence)}))
        except Exception as exc:
            context.record_stage_result(StageResult(self.name, False, error=str(exc)))
        return context


class StructuringStage(ResearchStage):
    name = "structuring"

    def __init__(self, structurer: Optional[ResultStructurer] = None):
        self._structurer = structurer or DefaultResultStructurer()

    async def execute(self, context: ResearchContext) -> ResearchContext:
        try:
            findings = await self._structurer.structure(context)
            context.findings = findings
            context.metadata.setdefault("structuring", {})["structured"] = True
            context.metadata["structuring"]["finding_count"] = len(findings)
            context.record_stage_result(StageResult(self.name, True, {"finding_count": len(findings)}))
        except Exception as exc:
            context.record_stage_result(StageResult(self.name, False, error=str(exc)))
        return context


class VerificationStage(ResearchStage):
    name = "verification"

    def __init__(self, verifier: Optional[Verifier] = None):
        self._verifier = verifier or DefaultVerifier()

    async def execute(self, context: ResearchContext) -> ResearchContext:
        try:
            result = context.to_result(FailureHandler.determine_status(context.sources_consulted, context.sources_failed, context.errors))
            verification = await self._verifier.verify(result)
            context.metadata.setdefault("verification", {})["result"] = verification.to_dict()
            context.record_stage_result(StageResult(self.name, True, verification.to_dict()))
        except Exception as exc:
            context.record_stage_result(StageResult(self.name, False, error=str(exc)))
        return context


class ResearchOrchestrator:
    def __init__(self):
        self._stages: List[ResearchStage] = []

    def register_stage(self, stage: ResearchStage) -> None:
        self._stages.append(stage)

    async def execute(self, request: ResearchRequest, request_id: str) -> ResearchResult:
        if not self._stages:
            return ResearchResult(request_id=request_id, status="failed", goal=request.goal, findings=[], sources_consulted=[], sources_failed=[], errors=["No research stages registered"], created_at=datetime.utcnow(), completed_at=datetime.utcnow(), source_execution_statuses=None)
        context = ResearchContext(request=request, request_id=request_id)
        for stage in self._stages:
            context.current_stage_index += 1
            try:
                context = await stage.execute(context)
            except Exception as exc:
                context.record_stage_result(StageResult(stage.name, False, error=str(exc)))
                break
            if context.should_stop():
                break
        status = FailureHandler.determine_status(context.sources_consulted, context.sources_failed, context.errors)
        return context.to_result(status=status)
