from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Any, Dict, Optional

from app.core.config import settings
from app.routers.auth import get_current_user
from app.research.orchestrator import ResearchOrchestrator, PlanningStage, DiscoveryStage, RetrievalStage, ProcessingStage, EvidenceCaptureStage, StructuringStage, VerificationStage
from app.research.sources.registry import SourceRegistry
from app.research.sources.discovery import SourceDiscovery
from app.research.retrieval.contracts import (
    ContentProcessor,
    RetrievedContent,
    RetrievalResult,
    RetrievalStatus,
    SourceRetriever,
)
from app.research.retrieval.orchestrator import RetrievalOrchestrator
from app.research.retrieval.providers.capability import ProviderCapability
from app.research.retrieval.providers.router import SearchProviderRouter
from app.research.retrieval.providers.searxng_adapter import SearXNGAdapter
from app.research.retrieval.stubs import StubRetriever, StubProcessor
from app.research.retrieval.composite_retriever import CompositeSourceRetriever, KnowledgeProviderSourceRetriever
from app.research.retrieval.query_enhancer import QueryEnhancer
from app.research.query_planner import ResearchQueryPlanner
from app.schemas.research_query import ResearchQueryPlan
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

# Build web search retriever if configured
_web_search_retriever: Optional[SourceRetriever] = None
if settings.SEARXNG_BASE_URL:
    _search_router = SearchProviderRouter()
    _search_router.register_adapter(
        SearXNGAdapter(
            capability=ProviderCapability(
                provider_id="searxng",
                supports_web_search=True,
                supports_snippets=True,
                supports_source_urls=True,
                requires_api_key=bool(settings.SEARXNG_API_KEY),
                priority=10,
                enabled=True,
            ),
            base_url=settings.SEARXNG_BASE_URL,
            api_key=settings.SEARXNG_API_KEY or "",
            timeout=settings.SEARXNG_TIMEOUT_SECONDS,
        )
    )
    _web_search_retriever = _search_router

# Build composite retriever: knowledge providers first, then web search, then optional stub fallback
_fallback_retriever: Optional[SourceRetriever] = None
if settings.SEARCH_STUB_FALLBACK:
    _fallback_retriever = StubRetriever()

_composite_retriever = CompositeSourceRetriever(
    knowledge_retrievers={},
    web_search_retriever=_web_search_retriever,
    fallback_retriever=_fallback_retriever,
)

_retrieval_orchestrator = RetrievalOrchestrator(
    retriever=_composite_retriever,
    processor=StubProcessor(),
)

_orchestrator = ResearchOrchestrator()
_orchestrator.register_stage(PlanningStage(planner=ResearchQueryPlanner()))
_orchestrator.register_stage(DiscoveryStage(discovery=_source_discovery))
_orchestrator.register_stage(RetrievalStage(retrieval_orchestrator=_retrieval_orchestrator, registry=_source_registry, query_enhancer=QueryEnhancer(retriever=_composite_retriever)))
_orchestrator.register_stage(ProcessingStage(processor=StubProcessor()))
_orchestrator.register_stage(EvidenceCaptureStage(registry=_source_registry))
_orchestrator.register_stage(StructuringStage())
_orchestrator.register_stage(VerificationStage())


def _get_provider_readiness(provider: Any) -> str:
    config = getattr(provider, "_config", {}) or {}
    base_url = config.get("base_url", "")
    api_key = config.get("api_key")
    username = config.get("username")
    password = config.get("password")

    if not base_url:
        return "unconfigured"

    provider_id = config.get("source_id", "")
    if provider_id == "un-comtrade":
        return "available"
    if provider_id == "worldbank-lpi":
        return "available"
    if provider_id == "faostat":
        if username and password:
            return "available"
        return "unconfigured"
    if provider_id in {"zatca", "tradedata", "gccstat"}:
        if api_key:
            return "available"
        return "unconfigured"

    if api_key or (username and password):
        return "available"
    return "unconfigured"


def _knowledge_source_to_research_source(source_meta: Dict[str, Any], provider: Any) -> Source:
    source_id = source_meta.get("id") or ""
    name = source_meta.get("name") or source_id
    source_type = source_meta.get("type") or "other"
    valid_types = {"market_data", "regulation", "news", "trade_statistics", "external_trade_intelligence", "external_agrifood_intelligence", "other"}
    if source_type not in valid_types:
        source_type = "other"
    reference = source_meta.get("source_url") or source_meta.get("updated_at") or source_meta.get("reference")
    metadata = {
        "provider_class": getattr(provider, "__class__", type(provider)).__name__,
        "version": source_meta.get("version"),
        "updated_at": source_meta.get("updated_at"),
        "readiness": _get_provider_readiness(provider),
    }
    return Source(
        source_id=source_id,
        name=name,
        source_type=source_type,
        reference=reference,
        metadata=metadata,
        status="active",
    )


async def sync_knowledge_providers_to_research_registry(knowledge_registry: Any, source_registry: Optional[SourceRegistry] = None, composite_retriever: Optional[CompositeSourceRetriever] = None) -> None:
    target_registry = source_registry if source_registry is not None else _source_registry
    if knowledge_registry is None:
        return
    try:
        providers_info = await knowledge_registry.list_providers()
    except Exception:
        providers_info = []

    for source_meta in providers_info:
        source_id = source_meta.get("id")
        if not source_id:
            continue
        provider = knowledge_registry.get(source_id)
        if provider is None:
            continue
        try:
            source = _knowledge_source_to_research_source(source_meta, provider)
            if source_id not in target_registry._sources:
                target_registry.register(SourceRegistration(source=source, overwrite=False))
        except Exception:
            continue

    # Update composite retriever with knowledge provider retrievers
    if composite_retriever is not None:
        knowledge_retrievers: Dict[str, KnowledgeProviderSourceRetriever] = {}
        for source_meta in providers_info:
            source_id = source_meta.get("id")
            if not source_id:
                continue
            provider = knowledge_registry.get(source_id)
            if provider is None:
                continue
            try:
                knowledge_retrievers[source_id] = KnowledgeProviderSourceRetriever(
                    provider=provider,
                    source_id=source_id,
                )
            except Exception:
                continue
        composite_retriever.update_knowledge_retrievers(knowledge_retrievers)


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
