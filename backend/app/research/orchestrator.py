from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from app.schemas.research import (
    ResearchRequest,
    ResearchResult,
    EvidenceItem,
    FindingItem,
    DiscoveryRequest,
    Evidence,
)
from app.research.retrieval.contracts import (
    ContentProcessor,
    RetrievedContent,
    RetrievalResult,
    RetrievalStatus,
    SourceRetriever,
)
from app.research.retrieval.orchestrator import RetrievalOrchestrator
from app.research.sources.registry import SourceRegistry
from app.research.sources.discovery import SourceDiscovery
from app.research.evidence.contracts import DefaultEvidenceCapture, EvidenceCapture
from app.research.result import DefaultResultStructurer, ResultStructurer
from app.research.quality import DefaultVerifier, FailureHandler, OpenArchitecturalDecision, QualityIndicator, VerificationResult, Verifier

logger = logging.getLogger(__name__)


class StageResult:
    """Result of executing a single research stage."""

    def __init__(
        self,
        stage_name: str,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        self.stage_name = stage_name
        self.success = success
        self.data = data or {}
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_name": self.stage_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
        }


class ResearchContext:
    """Mutable context passed between research lifecycle stages."""

    def __init__(
        self,
        request: ResearchRequest,
        request_id: str,
    ):
        self.request = request
        self.request_id = request_id
        self.current_stage_index = 0
        self.stage_results: List[StageResult] = []
        self.findings: List[FindingItem] = []
        self.sources_consulted: List[str] = []
        self.sources_failed: List[str] = []
        self.evidence: List[Evidence] = []
        self.errors: List[str] = []
        self.metadata: Dict[str, Any] = {}
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
            metadata={
                **self.metadata,
                "stage_results": [r.to_dict() for r in self.stage_results],
            },
        )


class ResearchStage(ABC):
    """Base class for research lifecycle stages."""

    name: str = "unnamed_stage"

    @abstractmethod
    async def execute(self, context: ResearchContext) -> ResearchContext:
        ...


class PlanningStage(ResearchStage):
    name = "planning"

    async def execute(self, context: ResearchContext) -> ResearchContext:
        try:
            sub_queries = self._build_sub_queries(context.request)
            context.metadata["plan"] = {
                "sub_queries": sub_queries,
                "source_selection_strategy": "scope_based",
                "retrieval_parameters": {},
            }
            context.record_stage_result(StageResult(stage_name=self.name, success=True))
        except Exception as exc:
            context.record_stage_result(StageResult(stage_name=self.name, success=False, error=str(exc)))
        return context

    def _build_sub_queries(self, request: ResearchRequest) -> List[str]:
        goal = request.goal.strip()
        if not goal:
            return []
        return [goal]


class DiscoveryStage(ResearchStage):
    name = "discovery"

    def __init__(self, discovery: Optional[SourceDiscovery] = None):
        self._discovery = discovery

    async def execute(self, context: ResearchContext) -> ResearchContext:
        try:
            if self._discovery is None:
                context.metadata.setdefault("discovery", {})["discovered_sources"] = []
                context.record_stage_result(StageResult(stage_name=self.name, success=True, data={"note": "no discovery dependency configured"}))
                return context
            discovery_request = DiscoveryRequest(
                goal=context.request.goal,
                scope=context.request.scope,
                source_preferences=context.request.source_preferences,
                constraints=context.request.constraints,
            )
            result = self._discovery.discover(discovery_request)
            context.sources_consulted = [source.source_id for source in result.discovered_sources]
            context.metadata.setdefault("discovery", {})["discovered_sources"] = context.sources_consulted
            context.record_stage_result(StageResult(stage_name=self.name, success=True, data=result.discovery_metadata or {}))
        except Exception as exc:
            context.record_stage_result(StageResult(stage_name=self.name, success=False, error=str(exc)))
        return context


class RetrievalStage(ResearchStage):
    name = "retrieval"

    def __init__(
        self,
        retrieval_orchestrator: Optional[RetrievalOrchestrator] = None,
        registry: Optional[SourceRegistry] = None,
    ):
        self._retrieval_orchestrator = retrieval_orchestrator
        self._registry = registry

    async def execute(self, context: ResearchContext) -> ResearchContext:
        try:
            discovered = context.metadata.get("discovery", {}).get("discovered_sources", [])
            if not discovered:
                context.sources_consulted = []
                context.record_stage_result(StageResult(stage_name=self.name, success=True, data={"note": "no sources discovered"}))
                return context

            sources = []
            for source_id in discovered:
                if self._registry:
                    source = self._registry.get(source_id)
                    if source:
                        sources.append(source)
                else:
                    context.sources_consulted = discovered
                    context.record_stage_result(StageResult(stage_name=self.name, success=True, data={"note": "no registry configured", "sources_queried": discovered}))
                    return context

            if self._retrieval_orchestrator is None:
                context.sources_consulted = [s.source_id for s in sources]
                context.sources_failed = [sid for sid in discovered if sid not in context.sources_consulted]
                context.record_stage_result(StageResult(stage_name=self.name, success=True, data={"note": "no retrieval orchestrator configured", "sources_queried": context.sources_consulted}))
                return context

            results = await self._retrieval_orchestrator.retrieve_sources(sources, context.request.goal)
            processed = await self._retrieval_orchestrator.process_results(results)

            context.sources_consulted = [r.source_id for r in processed if r.status == RetrievalStatus.SUCCESS]
            context.sources_failed = [r.source_id for r in processed if r.status != RetrievalStatus.SUCCESS]
            if context.sources_failed:
                context.errors.append(f"Retrieval failed for sources: {', '.join(context.sources_failed)}")
            context.metadata.setdefault("retrieval", {})["results"] = [r.to_dict() for r in processed]
            context.record_stage_result(StageResult(stage_name=self.name, success=True, data={
                "sources_queried": context.sources_consulted,
                "sources_failed": context.sources_failed,
            }))
        except Exception as exc:
            context.record_stage_result(StageResult(stage_name=self.name, success=False, error=str(exc)))
        return context


class ProcessingStage(ResearchStage):
    name = "processing"

    def __init__(self, processor: Optional[ContentProcessor] = None):
        self._processor = processor

    async def execute(self, context: ResearchContext) -> ResearchContext:
        try:
            retrieval_results = context.metadata.get("retrieval", {}).get("results", [])
            if not retrieval_results:
                context.metadata.setdefault("processing", {})["normalized"] = True
                context.record_stage_result(StageResult(stage_name=self.name, success=True))
                return context
            processed_items = []
            for item in retrieval_results:
                if item.get("status") == RetrievalStatus.SUCCESS and item.get("content"):
                    if self._processor:
                        content = RetrievedContent(
                            source_id=item["content"]["source_id"],
                            raw_content=item["content"]["raw_content"],
                            content_type=item["content"].get("content_type"),
                            metadata=item["content"].get("metadata", {}),
                        )
                        try:
                            processed = await self._processor.process(content)
                            if processed:
                                processed_items.append({**item, "content": processed.to_dict()})
                            else:
                                processed_items.append(item)
                        except Exception as exc:
                            context.record_stage_result(StageResult(stage_name=self.name, success=False, error=str(exc)))
                            return context
                    else:
                        processed_items.append(item)
                else:
                    processed_items.append(item)
            context.metadata.setdefault("processing", {})["normalized"] = True
            context.metadata["retrieval"]["results"] = processed_items
            context.record_stage_result(StageResult(stage_name=self.name, success=True))
        except Exception as exc:
            context.record_stage_result(StageResult(stage_name=self.name, success=False, error=str(exc)))
        return context


class EvidenceCaptureStage(ResearchStage):
    name = "evidence_capture"

    def __init__(
        self,
        registry: Optional[SourceRegistry] = None,
        capture: Optional[EvidenceCapture] = None,
    ):
        self._registry = registry
        self._capture = capture or DefaultEvidenceCapture()

    async def execute(self, context: ResearchContext) -> ResearchContext:
        try:
            retrieval_results = context.metadata.get("retrieval", {}).get("results", [])
            if not retrieval_results:
                context.metadata.setdefault("evidence", {})["captured"] = True
                context.record_stage_result(StageResult(stage_name=self.name, success=True, data={"note": "no retrieval results to capture"}))
                return context

            captured_evidence: List[Evidence] = []
            for item in retrieval_results:
                if item.get("status") != RetrievalStatus.SUCCESS:
                    continue
                content_dict = item.get("content")
                if not content_dict:
                    continue

                source_id = content_dict.get("source_id") or item.get("source_id")
                source = None
                if self._registry and source_id:
                    source = self._registry.get(source_id)

                retrieved_content = RetrievedContent(
                    source_id=source_id or "",
                    raw_content=content_dict.get("raw_content"),
                    content_type=content_dict.get("content_type"),
                    metadata=content_dict.get("metadata", {}),
                )
                transformation = "processed" if item.get("content") != content_dict else None
                evidence = await self._capture.capture(
                    content=retrieved_content,
                    source=source,
                    request_id=context.request_id,
                    transformation=transformation,
                )
                captured_evidence.append(evidence)

            context.evidence.extend(captured_evidence)
            context.metadata.setdefault("evidence", {})["captured"] = True
            context.metadata.setdefault("evidence", {})["count"] = len(captured_evidence)
            context.record_stage_result(StageResult(stage_name=self.name, success=True, data={"evidence_count": len(captured_evidence)}))
        except Exception as exc:
            context.record_stage_result(StageResult(stage_name=self.name, success=False, error=str(exc)))
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
            context.metadata.setdefault("structuring", {})["finding_count"] = len(findings)
            context.record_stage_result(StageResult(stage_name=self.name, success=True, data={"finding_count": len(findings)}))
        except Exception as exc:
            context.record_stage_result(StageResult(stage_name=self.name, success=False, error=str(exc)))
        return context


class VerificationStage(ResearchStage):
    name = "verification"

    def __init__(self, verifier: Optional[Verifier] = None):
        self._verifier = verifier or DefaultVerifier()

    async def execute(self, context: ResearchContext) -> ResearchContext:
        try:
            result = context.to_result(
                FailureHandler.determine_status(
                    context.sources_consulted,
                    context.sources_failed,
                    context.errors,
                )
            )
            verification = await self._verifier.verify(result)
            context.metadata.setdefault("verification", {})["result"] = verification.to_dict()
            context.record_stage_result(StageResult(stage_name=self.name, success=True, data=verification.to_dict()))
        except Exception as exc:
            context.record_stage_result(StageResult(stage_name=self.name, success=False, error=str(exc)))
        return context


class ResearchOrchestrator:
    """Coordinates the external research lifecycle."""

    def __init__(self):
        self._stages: List[ResearchStage] = []

    def register_stage(self, stage: ResearchStage) -> None:
        self._stages.append(stage)

    async def execute(self, request: ResearchRequest, request_id: str) -> ResearchResult:
        if not self._stages:
            failed_result = ResearchResult(
                request_id=request_id,
                status="failed",
                goal=request.goal,
                findings=[],
                sources_consulted=[],
                sources_failed=[],
                errors=["No research stages registered"],
                created_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )
            return failed_result

        context = ResearchContext(request=request, request_id=request_id)

        for stage in self._stages:
            context.current_stage_index += 1
            try:
                context = await stage.execute(context)
            except Exception as exc:
                context.record_stage_result(StageResult(stage_name=stage.name, success=False, error=str(exc)))
                break
            if context.should_stop():
                break

        status = FailureHandler.determine_status(
            context.sources_consulted,
            context.sources_failed,
            context.errors,
        )
        return context.to_result(status=status)
