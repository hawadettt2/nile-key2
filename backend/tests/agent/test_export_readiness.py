import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.export_readiness import ExportReadinessService, ExportReadinessRequest
from app.agent.knowledge.orchestrator import KnowledgeOrchestrator
from app.agent.llm.provider import LLMProviderRegistry, BaseLLMProvider, LLMResponse


class _FakeLLM(BaseLLMProvider):
    provider_name = "gemini"

    def __init__(self, content="Test recommendation"):
        self._content = content

    async def generate(self, prompt=None, system_prompt=None, parameters=None):
        return LLMResponse(
            content=self._content,
            model="fake-model",
            usage={},
            finish_reason="stop",
        )


class _FailingLLM(BaseLLMProvider):
    provider_name = "gemini"

    async def generate(self, prompt=None, system_prompt=None, parameters=None):
        raise RuntimeError("LLM generation failed")


def _make_result(results, confidence=0.8, source_id="test"):
    return {
        "results": results,
        "confidence": confidence,
        "sources": [source_id],
    }


@pytest.mark.asyncio
async def test_successful_report_assembly():
    llm_registry = LLMProviderRegistry()
    llm_registry.register(_FakeLLM("Test recommendation"))

    service = ExportReadinessService(llm_registry_instance=llm_registry)
    request = ExportReadinessRequest(
        product_id=1,
        hs_code="080510",
        product_name="Oranges",
        target_market="DE",
    )

    fake_orchestrator = AsyncMock(spec=KnowledgeOrchestrator)
    fake_orchestrator.orchestrate.return_value = _make_result(
        [{"content": "MRL: 0.05 ppm", "confidence": 0.85, "source_id": "moaah"}],
        confidence=0.85,
        source_id="moaah",
    )

    fake_registry = MagicMock()
    fake_registry.query.return_value = _make_result(
        [{"content": "LPI score: 3.5", "confidence": 0.75, "source_id": "worldbank-lpi"}],
        confidence=0.75,
        source_id="worldbank-lpi",
    )

    service._orchestrator = fake_orchestrator

    report = await service.analyze(request=request, user_id=1)

    assert report.product["hs_code"] == "080510"
    assert report.target_market == "DE"
    assert len(report.sections) == 4
    assert report.recommendation == "Test recommendation"
    assert len(report.action_checklist) > 0
    assert report.data_quality_note != ""


@pytest.mark.asyncio
async def test_availability_labels():
    service = ExportReadinessService()
    request = ExportReadinessRequest(
        product_id=1,
        hs_code="080510",
        product_name="Oranges",
        target_market="DE",
    )

    fake_orchestrator = AsyncMock(spec=KnowledgeOrchestrator)
    fake_orchestrator.orchestrate.return_value = _make_result(
        [{"content": "low confidence", "confidence": 0.3, "source_id": "moaah"}],
        confidence=0.3,
        source_id="moaah",
    )

    service._orchestrator = fake_orchestrator

    llm_registry = LLMProviderRegistry()
    llm_registry.register(_FakeLLM())

    with patch.object(service, "_llm_registry", llm_registry):
        report = await service.analyze(request=request, user_id=1)

    regulatory = next(s for s in report.sections if s.title == "Regulatory Requirements")
    assert regulatory.availability in ("available", "partial", "not_available")


@pytest.mark.asyncio
async def test_lpi_direct_query():
    service = ExportReadinessService()
    request = ExportReadinessRequest(
        product_id=1,
        hs_code="080510",
        product_name="Oranges",
        target_market="DE",
    )

    fake_registry = MagicMock()
    fake_registry.query.return_value = _make_result(
        [{"content": "LPI: 3.5", "confidence": 0.75, "source_id": "worldbank-lpi"}],
        confidence=0.75,
        source_id="worldbank-lpi",
    )

    section = await service._query_logistics(registry=fake_registry, target_market="DE")

    assert section.title == "Logistics Profile"
    assert section.source == "World Bank LPI"
    fake_registry.query.assert_called_once()
    call_kwargs = fake_registry.query.call_args[1]
    assert call_kwargs["context"] == {"country": "DE"}
    assert call_kwargs["scope"] == "LP.LPI.OVRL.XQ"


@pytest.mark.asyncio
async def test_llm_runtime_error_returns_none():
    service = ExportReadinessService()
    request = ExportReadinessRequest(
        product_id=1,
        hs_code="080510",
        product_name="Oranges",
        target_market="DE",
    )

    llm_registry = LLMProviderRegistry()
    llm_registry.register(_FailingLLM())

    with patch.object(service, "_llm_registry", llm_registry):
        recommendation = await service._generate_recommendation(
            product_name="Oranges",
            target_market="DE",
            sections=[],
        )

    assert recommendation is None


@pytest.mark.asyncio
async def test_llm_unavailable_returns_none():
    service = ExportReadinessService()
    request = ExportReadinessRequest(
        product_id=1,
        hs_code="080510",
        product_name="Oranges",
        target_market="DE",
    )

    with patch.object(service, "_llm_registry", None):
        recommendation = await service._generate_recommendation(
            product_name="Oranges",
            target_market="DE",
            sections=[],
        )

    assert recommendation is None


@pytest.mark.asyncio
async def test_provider_empty_fallback():
    service = ExportReadinessService()
    request = ExportReadinessRequest(
        product_id=1,
        hs_code="080510",
        product_name="Oranges",
        target_market="DE",
    )

    fake_orchestrator = AsyncMock(spec=KnowledgeOrchestrator)
    fake_orchestrator.orchestrate.return_value = _make_result([])

    results, source_label = await service._orchestrate_with_fallback(
        orchestrator=fake_orchestrator,
        registry=MagicMock(),
        query="test",
        context={"country": "DE"},
        primary_sources=["moaah"],
        fallback_sources=["moaah", "zatca", "gccstat"],
    )

    assert results == []
    assert source_label == "none"


def test_router_requires_auth():
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)
    response = client.post("/api/v1/export-readiness/analyze", json={})
    assert response.status_code in (401, 403, 422)
