import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone

from app.agent.knowledge.graph_provider import KnowledgeGraphProvider
from app.agent.knowledge.registry import KnowledgeProviderRegistry
from app.agent.decision_engine.engine import ReasoningEngine


class TestKnowledgeGraphProviderQuery:
    """Tests for KnowledgeGraphProvider.query() implementation."""

    @pytest.mark.asyncio
    async def test_query_returns_results_from_graph(self):
        """Query returns actual results from the knowledge graph service."""
        fake_nodes = [
            {
                "id": "shipment:1",
                "entity_type": "shipment",
                "entity_id": 1,
                "label": "Test Shipment",
                "properties": {"status": "in_transit"},
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
            }
        ]

        with patch("app.services.knowledge_graph.search_nodes", return_value=fake_nodes):
            provider = KnowledgeGraphProvider()
            result = await provider.query("shipment")

        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["id"] == "shipment:1"
        assert result["results"][0]["content"] == "Test Shipment"
        assert result["results"][0]["source_id"] == "knowledge-graph"
        assert result["results"][0]["confidence"] == 0.8
        assert result["results"][0]["path"] == "shipping"

    @pytest.mark.asyncio
    async def test_query_empty_results_when_no_nodes(self):
        """Query returns empty results when graph has no matching nodes."""
        with patch("app.services.knowledge_graph.search_nodes", return_value=[]):
            provider = KnowledgeGraphProvider()
            result = await provider.query("nonexistent")

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["knowledge-graph"]

    @pytest.mark.asyncio
    async def test_query_with_scope_filter(self):
        """Query passes scope as entity_type filter to search_nodes."""
        fake_nodes = [
            {
                "id": "shipment:1",
                "entity_type": "shipment",
                "entity_id": 1,
                "label": "Test Shipment",
                "properties": {},
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
            }
        ]

        with patch("app.services.knowledge_graph.search_nodes", return_value=fake_nodes) as mock_search:
            provider = KnowledgeGraphProvider()
            result = await provider.query("test", scope="shipment")

        mock_search.assert_called_once_with(query="test", entity_type="shipment", skip=0, limit=10)

    @pytest.mark.asyncio
    async def test_query_respects_limit(self):
        """Query passes limit to search_nodes."""
        with patch("app.services.knowledge_graph.search_nodes", return_value=[]) as mock_search:
            provider = KnowledgeGraphProvider()
            await provider.query("test", limit=5)

        mock_search.assert_called_once_with(query="test", entity_type=None, skip=0, limit=5)

    @pytest.mark.asyncio
    async def test_query_graceful_degradation_when_service_unavailable(self):
        """Query returns empty results when service import fails."""
        with patch("app.services.knowledge_graph.search_nodes", side_effect=Exception("Service error")):
            provider = KnowledgeGraphProvider()
            result = await provider.query("test")

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["knowledge-graph"]

    @pytest.mark.asyncio
    async def test_query_maps_entity_type_to_path(self):
        """Query maps entity types to ReasoningEngine paths."""
        test_cases = [
            ("shipment", "shipping"),
            ("invoice", "eta"),
            ("customs_declaration", "customs"),
            ("document", "document"),
            ("export_workflow", "workflow"),
            ("customer", None),
            ("supplier", None),
        ]

        for entity_type, expected_path in test_cases:
            fake_nodes = [
                {
                    "id": f"{entity_type}:1",
                    "entity_type": entity_type,
                    "entity_id": 1,
                    "label": "Test",
                    "properties": {},
                    "created_at": "2026-07-20T00:00:00Z",
                    "updated_at": "2026-07-20T00:00:00Z",
                }
            ]

            with patch("app.services.knowledge_graph.search_nodes", return_value=fake_nodes):
                provider = KnowledgeGraphProvider()
                result = await provider.query("test")

            assert result["results"][0]["path"] == expected_path

    @pytest.mark.asyncio
    async def test_query_result_has_required_metadata(self):
        """Query results include required metadata fields."""
        fake_nodes = [
            {
                "id": "shipment:1",
                "entity_type": "shipment",
                "entity_id": 1,
                "label": "Test Shipment",
                "properties": {"status": "in_transit"},
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
            }
        ]

        with patch("app.services.knowledge_graph.search_nodes", return_value=fake_nodes):
            provider = KnowledgeGraphProvider()
            result = await provider.query("shipment")

        item = result["results"][0]
        assert item["id"] == "shipment:1"
        assert item["content"] == "Test Shipment"
        assert item["source_id"] == "knowledge-graph"
        assert item["confidence"] == 0.8
        assert "metadata" in item
        assert item["metadata"]["entity_type"] == "shipment"
        assert item["metadata"]["entity_id"] == 1

    @pytest.mark.asyncio
    async def test_query_registered_in_registry_and_callable(self):
        """KnowledgeGraphProvider works when registered in KnowledgeProviderRegistry."""
        fake_nodes = [
            {
                "id": "shipment:1",
                "entity_type": "shipment",
                "entity_id": 1,
                "label": "Test Shipment",
                "properties": {},
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
            }
        ]

        with patch("app.services.knowledge_graph.search_nodes", return_value=fake_nodes):
            registry = KnowledgeProviderRegistry()
            provider = KnowledgeGraphProvider()
            await registry.register(provider)

            result = await registry.query(source_id="knowledge-graph", query="shipment")

        assert "results" in result
        assert len(result["results"]) == 1
        assert result["sources"] == ["knowledge-graph"]

    @pytest.mark.asyncio
    async def test_query_end_to_end_with_reasoning_engine(self):
        """KnowledgeGraphProvider feeds into ReasoningEngine via registry."""
        fake_nodes = [
            {
                "id": "shipment:1",
                "entity_type": "shipment",
                "entity_id": 1,
                "label": "Priority Shipment",
                "properties": {"priority": "high"},
                "created_at": "2026-07-20T00:00:00Z",
                "updated_at": "2026-07-20T00:00:00Z",
            }
        ]

        with patch("app.services.knowledge_graph.search_nodes", return_value=fake_nodes):
            registry = KnowledgeProviderRegistry()
            provider = KnowledgeGraphProvider()
            await registry.register(provider)

            engine = ReasoningEngine(knowledge_provider_registry=registry)
            decision = await engine.reason("session-123", {
                "intent": "Ship package",
                "parameters": {},
                "context": {},
            })

        assert "knowledge" in decision["context"]
        assert len(decision["context"]["knowledge"]) == 1
        assert decision["context"]["knowledge"][0]["path"] == "shipping"
        assert "Considered 1 knowledge entries" in decision["reasoning"]
