import asyncio
from typing import Any, Dict

import pytest
from unittest.mock import AsyncMock, patch

from app.agent.knowledge.mooadapter import MoaahExternalSourceAdapter
from app.agent.knowledge.mooadapter_client import MoaahApiClient


class TestMoaahAdapterContract:
    """Verify Moaah external source adapter contract boundaries."""

    def test_get_sources_returns_registry_compatible_entry(self):
        adapter = MoaahExternalSourceAdapter(
            config={
                "source_id": "moaah",
                "name": "Moaah External Knowledge",
                "type": "external",
                "version": "1.0.0",
                "updated_at": "2026-08-12T00:00:00Z",
            }
        )

        sources = asyncio.run(adapter.get_sources())
        assert len(sources) == 1
        source = sources[0]
        assert source["id"] == "moaah"
        assert source["name"] == "Moaah External Knowledge"
        assert source["type"] == "external"
        assert source["version"] == "1.0.0"
        assert source["updated_at"] == "2026-08-12T00:00:00Z"

    def test_default_source_metadata_when_config_is_empty(self):
        adapter = MoaahExternalSourceAdapter()

        sources = asyncio.run(adapter.get_sources())
        assert sources[0]["id"] == "moaah"
        assert sources[0]["type"] == "external"


class TestMoaahAdapterQuery:
    """Verify Moaah adapter query transformation and error handling."""

    def test_successful_response_transforms_to_contract_shape(self):
        adapter = MoaahExternalSourceAdapter(
            config={
                "base_url": "https://mtech-api.com/client/api",
                "api_key": "test-key",
                "source_id": "moaah",
                "name": "Moaah External Knowledge",
                "type": "external",
                "version": "1.0.0",
                "updated_at": "2026-08-12T00:00:00Z",
            }
        )

        raw_response = {
            "antidumping": {
                "antidumping_investigations": [
                    {
                        "uuid": "inv-1",
                        "subject_product": "Steel pipes",
                        "duty_measure_detail": "Affirmative | Measure applied",
                        "publication_date": "2025-03-25",
                        "id_link": "https://example.com/inv-1",
                        "country": "840",
                    }
                ],
                "antidumping_measures": [],
                "countervailing_investigations": [],
                "countervailing_measures": [],
            },
            "importLicensing": [],
            "qr": {"data": [], "dataOrigin": []},
            "matched_hs_codes": [],
        }

        with patch.object(MoaahApiClient, "search_regulations", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("steel pipes", context={"country": "840"}, scope="keyword", limit=10)
            )

        assert "results" in result
        assert "confidence" in result
        assert "sources" in result
        assert result["sources"] == ["moaah"]
        assert len(result["results"]) == 1
        item = result["results"][0]
        assert item["source_id"] == "moaah"
        assert 0.0 <= item["confidence"] <= 1.0
        assert "id" in item
        assert "content" in item
        assert "metadata" in item
        assert item["metadata"]["section"] == "antidumping"
        assert item["metadata"]["source_url"] == "https://example.com/inv-1"

    def test_empty_response_returns_empty_results(self):
        adapter = MoaahExternalSourceAdapter(
            config={
                "base_url": "https://mtech-api.com/client/api",
                "api_key": "test-key",
            }
        )

        with patch.object(MoaahApiClient, "search_regulations", new_callable=AsyncMock, return_value={}):
            result = asyncio.run(
                adapter.query("test", context={"country": "840"}, scope="keyword", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["moaah"]

    def test_malformed_response_returns_empty_results(self):
        adapter = MoaahExternalSourceAdapter(
            config={
                "base_url": "https://mtech-api.com/client/api",
                "api_key": "test-key",
            }
        )

        with patch.object(MoaahApiClient, "search_regulations", new_callable=AsyncMock, return_value="not-a-dict"):
            result = asyncio.run(
                adapter.query("test", context={"country": "840"}, scope="keyword", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["moaah"]

    def test_authentication_failure_returns_empty_results(self):
        adapter = MoaahExternalSourceAdapter(
            config={
                "base_url": "https://mtech-api.com/client/api",
                "api_key": "test-key",
            }
        )

        import httpx
        with patch.object(MoaahApiClient, "search_regulations", new_callable=AsyncMock, side_effect=httpx.HTTPStatusError("Unauthorized", request=None, response=None)):
            result = asyncio.run(
                adapter.query("test", context={"country": "840"}, scope="keyword", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["moaah"]

    def test_upstream_failure_returns_empty_results(self):
        adapter = MoaahExternalSourceAdapter(
            config={
                "base_url": "https://mtech-api.com/client/api",
                "api_key": "test-key",
            }
        )

        with patch.object(MoaahApiClient, "search_regulations", new_callable=AsyncMock, side_effect=Exception("Upstream error")):
            result = asyncio.run(
                adapter.query("test", context={"country": "840"}, scope="keyword", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["moaah"]

    def test_missing_country_context_returns_empty_results(self):
        adapter = MoaahExternalSourceAdapter(
            config={
                "base_url": "https://mtech-api.com/client/api",
                "api_key": "test-key",
            }
        )

        result = asyncio.run(
            adapter.query("test", context={}, scope="keyword", limit=10)
        )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["moaah"]

    def test_configuration_without_base_url_skips_api_call(self):
        adapter = MoaahExternalSourceAdapter(
            config={
                "api_key": "test-key",
            }
        )

        result = asyncio.run(
            adapter.query("test", context={"country": "840"}, scope="keyword", limit=10)
        )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["moaah"]
