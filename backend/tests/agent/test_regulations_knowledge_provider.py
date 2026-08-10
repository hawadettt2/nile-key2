import json
import os
from pathlib import Path

import pytest
from unittest.mock import patch

from app.agent.knowledge.regulations_provider import RegulationsKnowledgeProvider


FIXTURE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "fixtures", "regulations.json")
)


class TestRegulationsKnowledgeProvider:
    """Unit tests for RegulationsKnowledgeProvider."""

    @pytest.mark.asyncio
    async def test_get_sources_returns_expected_structure(self):
        provider = RegulationsKnowledgeProvider(file_path=FIXTURE_PATH)
        sources = await provider.get_sources()

        assert len(sources) == 1
        source = sources[0]
        assert source["id"] == "regulations"
        assert source["name"] == "Regulations Knowledge"
        assert source["type"] == "regulation"
        assert source["version"] == "1.0.0"
        assert "updated_at" in source
        assert source["updated_at"].endswith("Z")

    @pytest.mark.asyncio
    async def test_query_with_matching_query_returns_correct_shape(self):
        provider = RegulationsKnowledgeProvider(file_path=FIXTURE_PATH)
        result = await provider.query("ETA")

        assert "results" in result
        assert "confidence" in result
        assert "sources" in result
        assert isinstance(result["results"], list)
        assert result["sources"] == ["regulations"]
        if result["results"]:
            item = result["results"][0]
            assert "id" in item
            assert "content" in item
            assert "source_id" in item
            assert "confidence" in item
            assert "metadata" in item

    @pytest.mark.asyncio
    async def test_query_with_no_query_returns_all_records_up_to_limit(self):
        provider = RegulationsKnowledgeProvider(file_path=FIXTURE_PATH)
        result = await provider.query("", limit=2)

        assert len(result["results"]) <= 2
        assert len(result["results"]) == 2

    @pytest.mark.asyncio
    async def test_query_returns_empty_list_when_no_matches(self):
        provider = RegulationsKnowledgeProvider(file_path=FIXTURE_PATH)
        result = await provider.query("nonexistent regulation xyz")

        assert result["results"] == []

    @pytest.mark.asyncio
    async def test_confidence_scores_within_range(self):
        provider = RegulationsKnowledgeProvider(file_path=FIXTURE_PATH)
        result = await provider.query("")

        for item in result["results"]:
            assert 0.0 <= item["confidence"] <= 1.0

        if result["results"]:
            assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_query_handles_missing_file_gracefully(self, tmp_path):
        missing_path = str(tmp_path / "missing.json")
        provider = RegulationsKnowledgeProvider(file_path=missing_path)
        result = await provider.query("anything")

        assert result["results"] == []
        assert result["sources"] == ["regulations"]

    @pytest.mark.asyncio
    async def test_query_handles_malformed_json_gracefully(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not valid json", encoding="utf-8")
        provider = RegulationsKnowledgeProvider(file_path=str(bad_file))
        result = await provider.query("anything")

        assert result["results"] == []
        assert result["sources"] == ["regulations"]

    @pytest.mark.asyncio
    async def test_get_sources_raises_value_error_when_no_sources(self):
        """Contract requirement: registry raises ValueError if provider exposes no sources."""
        from app.agent.knowledge.registry import KnowledgeProviderRegistry

        class EmptyProvider(RegulationsKnowledgeProvider):
            async def get_sources(self):
                return []

        provider = EmptyProvider(file_path=FIXTURE_PATH)
        registry = KnowledgeProviderRegistry()
        with pytest.raises(ValueError, match="must expose at least one source"):
            await registry.register(provider)
