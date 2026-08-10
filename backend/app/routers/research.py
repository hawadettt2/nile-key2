from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.routers.auth import get_current_user
from app.research.orchestrator import ResearchOrchestrator, PlanningStage, DiscoveryStage, RetrievalStage, ProcessingStage, EvidenceCaptureStage, StructuringStage, VerificationStage
from app.research.sources.registry import SourceRegistry
from app.research.sources.discovery import SourceDiscovery
from app.research.retrieval.orchestrator import RetrievalOrchestrator
from app.research.retrieval.providers.router import SearchProviderRouter
from app.research.retrieval.stubs import StubRetriever, StubProcessor
from app.schemas.research import (
    ResearchRequest,
    ResearchResult,
    ErrorResponse,
    Source,
    SourceRegistration,
)
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/api/v1/research", tags=["External Research"])

_source_registry = SourceRegistry()
_source_discovery = SourceDiscovery(registry=_source_registry)

if settings.SEARCH_STUB_FALLBACK:
    _retrieval_orchestrator = RetrievalOrchestrator(
        retriever=StubRetriever(),
        processor=StubProcessor(),
    )
else:
    _retrieval_orchestrator = RetrievalOrchestrator(
        retriever=SearchProviderRouter(),
        processor=StubProcessor(),
    )

_orchestrator = ResearchOrchestrator()
_orchestrator.register_stage(PlanningStage())
_orchestrator.register_stage(DiscoveryStage(discovery=_source_discovery))
_orchestrator.register_stage(RetrievalStage(retrieval_orchestrator=_retrieval_orchestrator, registry=_source_registry))
_orchestrator.register_stage(ProcessingStage(processor=StubProcessor()))
_orchestrator.register_stage(EvidenceCaptureStage())
_orchestrator.register_stage(StructuringStage())
_orchestrator.register_stage(VerificationStage())


def _raise_http_error(result: dict) -> None:
    if not isinstance(result, dict):
        return
    error_code = result.get("error_code")
    if not error_code:
        return
    category = result.get("category", "internal")
    status_map = {
        "not_found": 404,
        "validation": 422,
        "dependency": 503,
        "internal": 500,
        "permission": 403,
    }
    status_code = status_map.get(category, 400)
    raise HTTPException(status_code=status_code, detail=result)


_in_memory_store: dict[str, ResearchResult] = {}


@router.post("/requests", response_model=ResearchResult)
async def create_research_request(
    request: ResearchRequest,
    current_user: dict = Depends(get_current_user),
):
    request_id = _generate_request_id()
    now = datetime.utcnow()

    initial_result = ResearchResult(
        request_id=request_id,
        status="pending",
        goal=request.goal,
        findings=[],
        sources_consulted=[],
        sources_failed=[],
        errors=None,
        created_at=now,
        completed_at=None,
        metadata={
            "context": request.context,
            "scope": request.scope,
            "source_preferences": request.source_preferences,
            "constraints": request.constraints,
            "requested_by": current_user.get("username", "unknown"),
            "user_id": current_user.get("id"),
        },
    )

    _in_memory_store[request_id] = initial_result

    result = await _orchestrator.execute(request, request_id)
    result.metadata = {
        **(result.metadata or {}),
        "context": request.context,
        "scope": request.scope,
        "source_preferences": request.source_preferences,
        "constraints": request.constraints,
        "requested_by": current_user.get("username", "unknown"),
        "user_id": current_user.get("id"),
    }
    _in_memory_store[request_id] = result
    return result


@router.get("/requests/{request_id}", response_model=ResearchResult)
async def get_research_request(
    request_id: str,
    current_user: dict = Depends(get_current_user),
):
    result = _in_memory_store.get(request_id)
    if not result:
        raise HTTPException(status_code=404, detail="Research request not found")
    return result


@router.post("/requests/{request_id}/cancel", response_model=MessageResponse)
async def cancel_research_request(
    request_id: str,
    current_user: dict = Depends(get_current_user),
):
    result = _in_memory_store.get(request_id)
    if not result:
        raise HTTPException(status_code=404, detail="Research request not found")
    if result.status in ("completed", "failed", "cancelled"):
        raise HTTPException(status_code=400, detail=f"Cannot cancel research in status: {result.status}")
    result.status = "cancelled"
    result.completed_at = datetime.utcnow()
    return MessageResponse(message="Research request cancelled")


@router.post("/sources", response_model=Source)
async def register_source(
    registration: SourceRegistration,
    current_user: dict = Depends(get_current_user),
):
    try:
        source = _source_registry.register(registration)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return source


@router.get("/sources", response_model=list[Source])
async def list_sources(
    current_user: dict = Depends(get_current_user),
):
    return _source_registry.list()


@router.get("/sources/{source_id}", response_model=Source)
async def get_source(
    source_id: str,
    current_user: dict = Depends(get_current_user),
):
    source = _source_registry.get(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.delete("/sources/{source_id}", response_model=MessageResponse)
async def unregister_source(
    source_id: str,
    current_user: dict = Depends(get_current_user),
):
    if not _source_registry.unregister(source_id):
        raise HTTPException(status_code=404, detail="Source not found")
    return MessageResponse(message="Source unregistered")


def _generate_request_id() -> str:
    return f"req_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
