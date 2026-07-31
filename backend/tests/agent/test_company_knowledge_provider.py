import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone

from app.agent.knowledge.company_knowledge_provider import CompanyKnowledgeProvider
from app.agent.knowledge.registry import KnowledgeProviderRegistry
from app.agent.decision_engine.engine import ReasoningEngine


class TestCompanyKnowledgeProviderQuery:
    """Tests for CompanyKnowledgeProvider.query() implementation."""

    @pytest.mark.asyncio
    async def test_query_returns_results_from_resources(self):
        """Query returns actual results from the resources service."""
        fake_resources = [
            {
                "id": 1,
                "title": "Egyptian Export Council",
                "description": "المجلس التصديري المصري — دعم المصدرين المصريين",
                "resource_type": "government",
                "category": "export",
                "url": "https://www.eec.org.eg",
                "country": "Egypt",
                "metadata": {"tags": "export,government,support"},
                "is_active": 1,
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
            }
        ]

        with patch("app.services.resource.search_resources", return_value=fake_resources):
            provider = CompanyKnowledgeProvider()
            result = await provider.query("export")

        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["id"] == "1"
        assert result["results"][0]["content"] == "المجلس التصديري المصري — دعم المصدرين المصريين"
        assert result["results"][0]["source_id"] == "company-knowledge"
        assert result["results"][0]["confidence"] == 0.9
        assert result["results"][0]["metadata"]["title"] == "Egyptian Export Council"
        assert result["results"][0]["metadata"]["resource_type"] == "government"

    @pytest.mark.asyncio
    async def test_query_empty_results_when_no_resources(self):
        """Query returns empty results when no resources match."""
        with patch("app.services.resource.search_resources", return_value=[]):
            provider = CompanyKnowledgeProvider()
            result = await provider.query("nonexistent")

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["company-knowledge"]

    @pytest.mark.asyncio
    async def test_query_uses_search_when_query_provided(self):
        """Query uses search_resources when query string is provided."""
        fake_resources = [
            {
                "id": 1,
                "title": "ITC Trade Map",
                "description": "منصة بيانات تجارية عالمية",
                "resource_type": "b2b_platform",
                "category": "trade",
                "url": "https://www.trademap.org",
                "country": None,
                "metadata": {"tags": "trade,data,export,statistics"},
                "is_active": 1,
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
            }
        ]

        with patch("app.services.resource.search_resources", return_value=fake_resources) as mock_search:
            provider = CompanyKnowledgeProvider()
            result = await provider.query("trade")

        mock_search.assert_called_once_with(q="trade")

    @pytest.mark.asyncio
    async def test_query_respects_limit(self):
        """Query respects the limit parameter."""
        fake_resources = [
            {
                "id": i,
                "title": f"Resource {i}",
                "description": f"Description {i}",
                "resource_type": "test",
                "category": "test",
                "url": f"https://example.com/{i}",
                "country": None,
                "metadata": {},
                "is_active": 1,
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
            }
            for i in range(10)
        ]

        with patch("app.services.resource.search_resources", return_value=fake_resources):
            provider = CompanyKnowledgeProvider()
            result = await provider.query("test", limit=3)

        assert len(result["results"]) == 3

    @pytest.mark.asyncio
    async def test_query_with_scope_filter(self):
        """Query passes scope as resource_type filter to list_resources when query is empty."""
        fake_resources = [
            {
                "id": 1,
                "title": "Test",
                "description": "Test",
                "resource_type": "government",
                "category": "export",
                "url": "https://example.com",
                "country": None,
                "metadata": {},
                "is_active": 1,
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
            }
        ]

        with patch("app.services.resource.list_resources", return_value=fake_resources) as mock_list:
            provider = CompanyKnowledgeProvider()
            await provider.query("", scope="government")

        mock_list.assert_called_once_with(
            resource_type="government",
            category=None,
            country=None,
            skip=0,
            limit=10,
        )

    @pytest.mark.asyncio
    async def test_query_graceful_degradation_when_service_unavailable(self):
        """Query returns empty results when service import fails."""
        with patch("app.services.resource.search_resources", side_effect=Exception("Service error")):
            provider = CompanyKnowledgeProvider()
            result = await provider.query("test")

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["company-knowledge"]

    @pytest.mark.asyncio
    async def test_query_result_has_required_metadata(self):
        """Query results include required metadata fields."""
        fake_resources = [
            {
                "id": 42,
                "title": "GAFI",
                "description": "الهيئة العامة للاستثمار والمناطق الحرة",
                "resource_type": "government",
                "category": "investment",
                "url": "https://www.gafi.gov.eg",
                "country": "Egypt",
                "metadata": {"tags": "investment,government,license"},
                "is_active": 1,
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
            }
        ]

        with patch("app.services.resource.search_resources", return_value=fake_resources):
            provider = CompanyKnowledgeProvider()
            result = await provider.query("investment")

        item = result["results"][0]
        assert item["id"] == "42"
        assert item["content"] == "الهيئة العامة للاستثمار والمناطق الحرة"
        assert item["source_id"] == "company-knowledge"
        assert item["confidence"] == 0.9
        assert item["metadata"]["title"] == "GAFI"
        assert item["metadata"]["url"] == "https://www.gafi.gov.eg"
        assert item["metadata"]["country"] == "Egypt"
        assert item["metadata"]["tags"] == ["investment", "government", "license"]

    @pytest.mark.asyncio
    async def test_query_registered_in_registry_and_callable(self):
        """CompanyKnowledgeProvider works when registered in KnowledgeProviderRegistry."""
        fake_resources = [
            {
                "id": 1,
                "title": "Nafeza",
                "description": "منظومة نافذة الجمركية المصرية",
                "resource_type": "government",
                "category": "customs",
                "url": "https://www.nafeza.gov.eg",
                "country": "Egypt",
                "metadata": {"tags": "customs,clearance,government"},
                "is_active": 1,
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
            }
        ]

        with patch("app.services.resource.search_resources", return_value=fake_resources):
            registry = KnowledgeProviderRegistry()
            provider = CompanyKnowledgeProvider()
            await registry.register(provider)

            result = await registry.query(source_id="company-knowledge", query="customs")

        assert "results" in result
        assert len(result["results"]) == 1
        assert result["sources"] == ["company-knowledge"]

    @pytest.mark.asyncio
    async def test_query_end_to_end_with_reasoning_engine(self):
        """CompanyKnowledgeProvider feeds into ReasoningEngine via registry."""
        fake_resources = [
            {
                "id": 1,
                "title": "ETA Egypt",
                "description": "مصلحة الضرائب المصرية — الفاتورة الإلكترونية",
                "resource_type": "government",
                "category": "tax",
                "url": "https://invoicing.eta.gov.eg",
                "country": "Egypt",
                "metadata": {"tags": "tax,e-invoice,government"},
                "is_active": 1,
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
            }
        ]

        with patch("app.services.resource.search_resources", return_value=fake_resources):
            registry = KnowledgeProviderRegistry()
            provider = CompanyKnowledgeProvider()
            await registry.register(provider)

            engine = ReasoningEngine(knowledge_provider_registry=registry)
            decision = await engine.reason("session-123", {
                "intent": "Submit invoice",
                "parameters": {},
                "context": {},
            })

        assert "knowledge" in decision["context"]
        assert len(decision["context"]["knowledge"]) == 1
        assert decision["context"]["knowledge"][0]["source_id"] == "company-knowledge"
        assert "Considered 1 knowledge entries" in decision["reasoning"]

    @pytest.mark.asyncio
    async def test_query_get_sources_returns_company_knowledge(self):
        """get_sources returns company-knowledge source."""
        provider = CompanyKnowledgeProvider()
        sources = await provider.get_sources()

        assert len(sources) == 1
        assert sources[0]["id"] == "company-knowledge"
        assert sources[0]["type"] == "company"

    @pytest.mark.asyncio
    async def test_query_parallel_with_knowledge_graph_provider(self):
        """CompanyKnowledgeProvider and KnowledgeGraphProvider work in parallel."""
        from app.agent.knowledge.graph_provider import KnowledgeGraphProvider

        fake_resources = [
            {
                "id": 1,
                "title": "Test Resource",
                "description": "Test description",
                "resource_type": "test",
                "category": "test",
                "url": "https://example.com",
                "country": None,
                "metadata": {},
                "is_active": 1,
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
            }
        ]
        fake_graph_nodes = [
            {
                "id": "shipment:1",
                "entity_type": "shipment",
                "entity_id": 1,
                "label": "Shipment Node",
                "properties": {},
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
            }
        ]

        with patch("app.services.resource.search_resources", return_value=fake_resources):
            with patch("app.services.knowledge_graph.search_nodes", return_value=fake_graph_nodes):
                registry = KnowledgeProviderRegistry()
                company_provider = CompanyKnowledgeProvider()
                graph_provider = KnowledgeGraphProvider()
                await registry.register(company_provider)
                await registry.register(graph_provider)

                engine = ReasoningEngine(knowledge_provider_registry=registry)
                decision = await engine.reason("session-123", {
                    "intent": "Ship package",
                    "parameters": {},
                    "context": {},
                })

        assert "knowledge" in decision["context"]
        assert len(decision["context"]["knowledge"]) == 2
        sources = {k["source_id"] for k in decision["context"]["knowledge"]}
        assert "company-knowledge" in sources
        assert "knowledge-graph" in sources
