import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.knowledge.gccstat_provider import GccstatExternalSourceAdapter
from app.agent.knowledge.gccstat_client import GccstatApiClient


class TestGccstatAdapterContract:
    """Verify GCC-Stat external source adapter contract boundaries."""

    def test_get_sources_returns_registry_compatible_entry(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "source_id": "gccstat",
                "name": "GCC-Stat Data Portal",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        sources = asyncio.run(adapter.get_sources())
        assert len(sources) == 1
        source = sources[0]
        assert source["id"] == "gccstat"
        assert source["name"] == "GCC-Stat Data Portal"
        assert source["type"] == "external_trade_intelligence"
        assert source["version"] == "1.0"
        assert source["updated_at"] == "2026-08-14T00:00:00Z"

    def test_default_source_metadata_when_config_is_empty(self):
        adapter = GccstatExternalSourceAdapter()

        sources = asyncio.run(adapter.get_sources())
        assert sources[0]["id"] == "gccstat"
        assert sources[0]["type"] == "external_trade_intelligence"


class TestGccstatAdapterQuery:
    """Verify GCC-Stat adapter query transformation and error handling."""

    def test_successful_sdmx_json_response_transforms_to_contract_shape(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
                "source_id": "gccstat",
                "name": "GCC-Stat Data Portal",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        raw_response = {
            "meta": {
                "id": "IREF933718",
                "prepared": "2026-08-14T07:42:57",
                "test": False,
                "sender": {"id": "GCC_STAT"},
                "receiver": {"id": "ANONYMOUS"},
            },
            "data": {
                "dataSets": [
                    {
                        "links": [
                            {
                                "rel": "dataflow",
                                "urn": "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=GCCSTAT.PSS:DF_PSS_DEM_POP(1.0)",
                            }
                        ],
                        "action": "Information",
                        "series": {
                            "0:0:0:0:0": {
                                "attributes": [],
                                "observations": {"0": ["46"]},
                            },
                            "1:0:0:1:0": {
                                "attributes": [],
                                "observations": {"2": ["947997"]},
                            },
                        },
                    }
                ]
            },
        }

        with patch.object(GccstatApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("population", context={"country": "SA"}, scope="population", limit=10)
            )

        assert "results" in result
        assert "confidence" in result
        assert "sources" in result
        assert result["sources"] == ["gccstat"]
        assert len(result["results"]) == 2
        item = result["results"][0]
        assert item["source_id"] == "gccstat"
        assert 0.0 <= item["confidence"] <= 1.0
        assert "id" in item
        assert "content" in item
        assert "metadata" in item
        assert item["metadata"]["source_authority"] == "GCC-Stat"
        assert item["metadata"]["country"] == "SA"
        assert item["metadata"]["retrieval_status"] == "success"

    def test_empty_response_returns_empty_results(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
            }
        )

        with patch.object(GccstatApiClient, "request", new_callable=AsyncMock, return_value={"meta": {}, "data": {}}):
            result = asyncio.run(
                adapter.query("population", context={"country": "SA"}, scope="population", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["gccstat"]

    def test_non_dict_response_returns_empty_results(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
            }
        )

        with patch.object(GccstatApiClient, "request", new_callable=AsyncMock, return_value=None):
            result = asyncio.run(
                adapter.query("population", context={"country": "SA"}, scope="population", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["gccstat"]

    def test_missing_base_url_returns_empty_results(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "source_id": "gccstat",
            }
        )

        result = asyncio.run(
            adapter.query("population", context={"country": "SA"}, scope="population", limit=10)
        )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["gccstat"]

    def test_missing_country_context_returns_empty_results(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
            }
        )

        result = asyncio.run(
            adapter.query("population", context={}, scope="population", limit=10)
        )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["gccstat"]


class TestGccstatAdapterConfidence:
    """Verify GCC-Stat adapter confidence scoring rules."""

    def test_confidence_scores_within_valid_range(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
            }
        )

        raw_response = {
            "meta": {"prepared": "2026-08-14T07:42:57"},
            "data": {
                "dataSets": [
                    {
                        "series": {
                            "SA:0:0:0:0": {
                                "observations": {"2024": ["12345"]},
                            }
                        }
                    }
                ]
            },
        }

        with patch.object(GccstatApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("population", context={"country": "SA"}, scope="population", limit=10)
            )

        assert len(result["results"]) == 1
        confidence = result["results"][0]["confidence"]
        assert 0.0 <= confidence <= 1.0

    def test_confidence_0_85_when_all_fields_present(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        raw_response = {
            "meta": {"prepared": "2026-08-14T07:42:57"},
            "data": {
                "dataSets": [
                    {
                        "series": {
                            "SA:0:0:0:0": {
                                "observations": {"2024": ["12345"]},
                            }
                        }
                    }
                ]
            },
        }

        with patch.object(GccstatApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("population", context={"country": "SA"}, scope="population", limit=10)
            )

        assert result["results"][0]["confidence"] == 0.85

    def test_confidence_0_75_when_timestamp_missing(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
            }
        )

        raw_response = {
            "meta": {},
            "data": {
                "dataSets": [
                    {
                        "series": {
                            "SA:0:0:0:0": {
                                "observations": {"": ["12345"]},
                            }
                        }
                    }
                ]
            },
        }

        with patch.object(GccstatApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("population", context={"country": "SA"}, scope="population", limit=10)
            )

        assert result["results"][0]["confidence"] == 0.75

    def test_confidence_0_75_when_only_source_authority_present(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
            }
        )

        raw_response = {
            "meta": {},
            "data": {
                "dataSets": [
                    {
                        "series": {
                            "": {
                                "observations": {"": [""]},
                            }
                        }
                    }
                ]
            },
        }

        with patch.object(GccstatApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("population", context={}, scope="population", limit=10)
            )

        assert result["results"][0]["confidence"] == 0.75


class TestGccstatAdapterProvenance:
    """Verify GCC-Stat adapter provenance metadata."""

    def test_provenance_metadata_populated(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
                "source_id": "gccstat",
                "name": "GCC-Stat Data Portal",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        raw_response = {
            "meta": {"prepared": "2026-08-14T07:42:57"},
            "data": {
                "dataSets": [
                    {
                        "series": {
                            "SA:0:0:0:0": {
                                "observations": {"2024": ["12345"]},
                            }
                        }
                    }
                ]
            },
        }

        with patch.object(GccstatApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("population", context={"country": "SA"}, scope="population", limit=10)
            )

        item = result["results"][0]
        assert item["metadata"]["source_authority"] == "GCC-Stat"
        assert item["metadata"]["country"] == "SA"
        assert item["metadata"]["updated_at"] == "2026-08-14T00:00:00Z"
        assert item["metadata"]["version"] == "1.0"
        assert item["metadata"]["retrieval_status"] == "success"
        assert "record_hash" in item["metadata"]
        assert "source_url" in item["metadata"]

    def test_record_hash_is_deterministic(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
            }
        )

        raw_response = {
            "meta": {},
            "data": {
                "dataSets": [
                    {
                        "series": {
                            "SA:0:0:0:0": {
                                "observations": {"2024": ["12345"]},
                            }
                        }
                    }
                ]
            },
        }

        with patch.object(GccstatApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result1 = asyncio.run(
                adapter.query("population", context={"country": "SA"}, scope="population", limit=10)
            )
            result2 = asyncio.run(
                adapter.query("population", context={"country": "SA"}, scope="population", limit=10)
            )

        assert result1["results"][0]["metadata"]["record_hash"] == result2["results"][0]["metadata"]["record_hash"]


class TestGccstatAdapterGracefulDegradation:
    """Verify GCC-Stat adapter graceful degradation."""

    def test_network_error_returns_empty_results(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
            }
        )

        with patch.object(GccstatApiClient, "request", new_callable=AsyncMock, side_effect=Exception("Network error")):
            result = asyncio.run(
                adapter.query("population", context={"country": "SA"}, scope="population", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["gccstat"]

    def test_malformed_response_returns_empty_results(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
            }
        )

        with patch.object(GccstatApiClient, "request", new_callable=AsyncMock, return_value={"unexpected": "structure"}):
            result = asyncio.run(
                adapter.query("population", context={"country": "SA"}, scope="population", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["gccstat"]

    def test_missing_data_section_returns_empty_results(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
            }
        )

        with patch.object(GccstatApiClient, "request", new_callable=AsyncMock, return_value={"meta": {}}):
            result = asyncio.run(
                adapter.query("population", context={"country": "SA"}, scope="population", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["gccstat"]
