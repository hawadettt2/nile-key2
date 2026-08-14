import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.knowledge.faostat_provider import FaostatExternalSourceAdapter
from app.agent.knowledge.faostat_client import FaostatApiClient


class TestFaostatAdapterContract:
    """Verify FAOSTAT external source adapter contract boundaries."""

    def test_get_sources_returns_registry_compatible_entry(self):
        adapter = FaostatExternalSourceAdapter(
            config={
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        sources = asyncio.run(adapter.get_sources())
        assert len(sources) == 1
        source = sources[0]
        assert source["id"] == "faostat"
        assert source["name"] == "FAOSTAT External Knowledge"
        assert source["type"] == "external_agrifood_intelligence"
        assert source["version"] == "1.0.0"
        assert source["updated_at"] == "2026-08-14T00:00:00Z"

    def test_default_source_metadata_when_config_is_empty(self):
        adapter = FaostatExternalSourceAdapter()

        sources = asyncio.run(adapter.get_sources())
        assert sources[0]["id"] == "faostat"
        assert sources[0]["type"] == "external_agrifood_intelligence"


class TestFaostatAdapterQuery:
    """Verify FAOSTAT adapter query transformation and error handling."""

    def test_successful_response_transforms_to_contract_shape(self):
        adapter = FaostatExternalSourceAdapter(
            config={
                "base_url": "https://faostatservices.fao.org/api/v1",
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
                "default_domain": "QC",
            }
        )

        raw_response = {
            "data": [
                {
                    "area": "Egypt",
                    "areaCode": "EGY",
                    "item": "Wheat",
                    "itemCode": "15",
                    "element": "Production",
                    "elementCode": "5510",
                    "year": "2023",
                    "unit": "Tonnes",
                    "value": "1234567",
                    "flag": "A",
                }
            ],
            "message": {
                "total": 1,
            },
        }

        with patch.object(FaostatApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("wheat production", context={"area": "Egypt", "item": "Wheat", "element": "Production", "year": "2023"}, scope="QC", limit=10)
            )

        assert "results" in result
        assert "confidence" in result
        assert "sources" in result
        assert result["sources"] == ["faostat"]
        assert len(result["results"]) == 1
        item = result["results"][0]
        assert item["source_id"] == "faostat"
        assert 0.0 <= item["confidence"] <= 1.0
        assert "id" in item
        assert "content" in item
        assert "metadata" in item
        assert item["metadata"]["area"] == "Egypt"
        assert item["metadata"]["area_code"] == "EGY"
        assert item["metadata"]["item"] == "Wheat"
        assert item["metadata"]["year"] == "2023"
        assert item["metadata"]["source_authority"] == "FAO"
        assert item["metadata"]["retrieval_status"] == "success"

    def test_empty_response_returns_empty_results(self):
        adapter = FaostatExternalSourceAdapter(
            config={
                "base_url": "https://faostatservices.fao.org/api/v1",
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        with patch.object(FaostatApiClient, "request", new_callable=AsyncMock, return_value={}):
            result = asyncio.run(
                adapter.query("test", context={"area": "Egypt"}, scope="QC", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["faostat"]

    def test_malformed_response_returns_empty_results(self):
        adapter = FaostatExternalSourceAdapter(
            config={
                "base_url": "https://faostatservices.fao.org/api/v1",
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        with patch.object(FaostatApiClient, "request", new_callable=AsyncMock, return_value="not-a-dict"):
            result = asyncio.run(
                adapter.query("test", context={"area": "Egypt"}, scope="QC", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["faostat"]

    def test_upstream_failure_returns_empty_results(self):
        adapter = FaostatExternalSourceAdapter(
            config={
                "base_url": "https://faostatservices.fao.org/api/v1",
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        with patch.object(FaostatApiClient, "request", new_callable=AsyncMock, side_effect=Exception("Upstream error")):
            result = asyncio.run(
                adapter.query("test", context={"area": "Egypt"}, scope="QC", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["faostat"]

    def test_missing_area_context_returns_empty_results(self):
        adapter = FaostatExternalSourceAdapter(
            config={
                "base_url": "https://faostatservices.fao.org/api/v1",
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        result = asyncio.run(
            adapter.query("test", context={}, scope="QC", limit=10)
        )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["faostat"]

    def test_configuration_without_base_url_skips_api_call(self):
        adapter = FaostatExternalSourceAdapter(
            config={
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        result = asyncio.run(
            adapter.query("test", context={"area": "Egypt"}, scope="QC", limit=10)
        )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["faostat"]


class TestFaostatSourceUrl:
    """Verify source_url construction matches live API structure."""

    def test_source_url_contains_en_data_path_with_scope(self):
        adapter = FaostatExternalSourceAdapter(
            config={
                "base_url": "https://faostatservices.fao.org/api/v1",
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
                "default_domain": "QCL",
            }
        )

        raw_response = {
            "data": [
                {
                    "area": "Egypt",
                    "areaCode": "EGY",
                    "item": "Wheat",
                    "itemCode": "15",
                    "element": "Production",
                    "elementCode": "5510",
                    "year": "2023",
                    "unit": "Tonnes",
                    "value": "1234567",
                    "flag": "A",
                }
            ],
            "message": {"total": 1},
        }

        with patch.object(FaostatApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("wheat production", context={"area": "Egypt"}, scope="QCL", limit=10)
            )

        item = result["results"][0]
        assert item["metadata"]["source_url"] == "https://faostatservices.fao.org/api/v1/en/data/QCL?format=json"

    def test_source_url_uses_default_domain_when_scope_missing(self):
        adapter = FaostatExternalSourceAdapter(
            config={
                "base_url": "https://faostatservices.fao.org/api/v1",
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
                "default_domain": "QCL",
            }
        )

        raw_response = {
            "data": [
                {
                    "area": "Egypt",
                    "areaCode": "EGY",
                    "item": "Wheat",
                    "itemCode": "15",
                    "element": "Production",
                    "elementCode": "5510",
                    "year": "2023",
                    "unit": "Tonnes",
                    "value": "1234567",
                    "flag": "A",
                }
            ],
            "message": {"total": 1},
        }

        with patch.object(FaostatApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("wheat production", context={"area": "Egypt"}, limit=10)
            )

        item = result["results"][0]
        assert item["metadata"]["source_url"] == "https://faostatservices.fao.org/api/v1/en/data/QCL?format=json"

    def test_source_url_uses_scope_over_default_domain(self):
        adapter = FaostatExternalSourceAdapter(
            config={
                "base_url": "https://faostatservices.fao.org/api/v1",
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
                "default_domain": "QCL",
            }
        )

        raw_response = {
            "data": [
                {
                    "area": "Egypt",
                    "areaCode": "EGY",
                    "item": "Wheat",
                    "itemCode": "15",
                    "element": "Production",
                    "elementCode": "5510",
                    "year": "2023",
                    "unit": "Tonnes",
                    "value": "1234567",
                    "flag": "A",
                }
            ],
            "message": {"total": 1},
        }

        with patch.object(FaostatApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("wheat production", context={"area": "Egypt"}, scope="QC", limit=10)
            )

        item = result["results"][0]
        assert item["metadata"]["source_url"] == "https://faostatservices.fao.org/api/v1/en/data/QC?format=json"
