import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.knowledge.worldbank_lpi_provider import WorldBankLpiExternalSourceAdapter
from app.agent.knowledge.worldbank_lpi_client import WorldBankLpiApiClient


class TestWorldBankLpiAdapterContract:
    """Verify World Bank LPI external source adapter contract boundaries."""

    def test_get_sources_returns_registry_compatible_entry(self):
        adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "source_id": "worldbank-lpi",
                "name": "World Bank Logistics Performance Index",
                "type": "external_logistics_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-18T00:00:00Z",
            }
        )

        sources = asyncio.run(adapter.get_sources())
        assert len(sources) == 1
        source = sources[0]
        assert source["id"] == "worldbank-lpi"
        assert source["name"] == "World Bank Logistics Performance Index"
        assert source["type"] == "external_logistics_intelligence"
        assert source["version"] == "1.0.0"
        assert source["updated_at"] == "2026-08-18T00:00:00Z"

    def test_default_source_metadata_when_config_is_empty(self):
        adapter = WorldBankLpiExternalSourceAdapter()

        sources = asyncio.run(adapter.get_sources())
        assert sources[0]["id"] == "worldbank-lpi"
        assert sources[0]["type"] == "external_logistics_intelligence"


class TestWorldBankLpiAdapterQuery:
    """Verify World Bank LPI adapter query transformation and error handling."""

    def test_successful_response_transforms_to_contract_shape(self):
        adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "base_url": "https://api.worldbank.org/v2",
                "source_id": "worldbank-lpi",
                "name": "World Bank Logistics Performance Index",
                "type": "external_logistics_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-18T00:00:00Z",
            }
        )

        raw_response = [
            {
                "page": 1,
                "pages": 1,
                "per_page": 10,
                "total": 1,
                "sourceid": "2",
                "lastupdated": "2026-07-13",
            },
            [
                {
                    "indicator": {
                        "id": "LP.LPI.OVRL.XQ",
                        "value": "Logistics performance index: Overall (1=low to 5=high)"
                    },
                    "country": {
                        "id": "EG",
                        "value": "Egypt, Arab Rep."
                    },
                    "countryiso3code": "EGY",
                    "date": "2022",
                    "value": 3.1,
                    "unit": "",
                    "obs_status": "",
                    "decimal": 2
                }
            ]
        ]

        with patch.object(WorldBankLpiApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("Egypt logistics performance", context={"country": "EG", "indicator": "LP.LPI.OVRL.XQ", "year": "2022"}, limit=10)
            )

        assert "results" in result
        assert "confidence" in result
        assert "sources" in result
        assert result["sources"] == ["worldbank-lpi"]
        assert len(result["results"]) == 1
        item = result["results"][0]
        assert item["source_id"] == "worldbank-lpi"
        assert item["confidence"] == 0.95
        assert "id" in item
        assert "content" in item
        assert "metadata" in item
        assert item["metadata"]["indicator_id"] == "LP.LPI.OVRL.XQ"
        assert item["metadata"]["indicator_name"] == "Logistics performance index: Overall (1=low to 5=high)"
        assert item["metadata"]["country_code"] == "EG"
        assert item["metadata"]["country_name"] == "Egypt, Arab Rep."
        assert item["metadata"]["countryiso3code"] == "EGY"
        assert item["metadata"]["year"] == "2022"
        assert item["metadata"]["value"] == 3.1
        assert item["metadata"]["source_authority"] == "World Bank"
        assert item["metadata"]["retrieval_status"] == "success"

    def test_empty_dataset_returns_empty_results(self):
        adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "base_url": "https://api.worldbank.org/v2",
                "source_id": "worldbank-lpi",
            }
        )

        with patch.object(WorldBankLpiApiClient, "request", new_callable=AsyncMock, return_value=[{"page": 1, "pages": 1, "per_page": 10, "total": 0, "sourceid": "2", "lastupdated": "2026-07-13"}, []]):
            result = asyncio.run(
                adapter.query("test", context={"country": "EG", "indicator": "LP.LPI.OVRL.XQ"}, limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["worldbank-lpi"]

    def test_malformed_response_returns_empty_results(self):
        adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "base_url": "https://api.worldbank.org/v2",
                "source_id": "worldbank-lpi",
            }
        )

        with patch.object(WorldBankLpiApiClient, "request", new_callable=AsyncMock, return_value="not-a-list"):
            result = asyncio.run(
                adapter.query("test", context={"country": "EG", "indicator": "LP.LPI.OVRL.XQ"}, limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["worldbank-lpi"]

    def test_upstream_failure_returns_empty_results(self):
        adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "base_url": "https://api.worldbank.org/v2",
                "source_id": "worldbank-lpi",
            }
        )

        with patch.object(WorldBankLpiApiClient, "request", new_callable=AsyncMock, side_effect=Exception("Upstream error")):
            result = asyncio.run(
                adapter.query("test", context={"country": "EG", "indicator": "LP.LPI.OVRL.XQ"}, limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["worldbank-lpi"]

    def test_missing_base_url_returns_empty_results(self):
        adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "source_id": "worldbank-lpi",
            }
        )

        result = asyncio.run(
            adapter.query("test", context={"country": "EG", "indicator": "LP.LPI.OVRL.XQ"}, limit=10)
        )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["worldbank-lpi"]

    def test_missing_country_returns_empty_results(self):
        adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "base_url": "https://api.worldbank.org/v2",
                "source_id": "worldbank-lpi",
            }
        )

        result = asyncio.run(
            adapter.query("test", context={"indicator": "LP.LPI.OVRL.XQ"}, limit=10)
        )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["worldbank-lpi"]

    def test_sources_parameter_is_accepted_but_not_used(self):
        adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "base_url": "https://api.worldbank.org/v2",
                "source_id": "worldbank-lpi",
            }
        )

        raw_response = [
            {
                "page": 1,
                "pages": 1,
                "per_page": 10,
                "total": 1,
                "sourceid": "2",
                "lastupdated": "2026-07-13",
            },
            [
                {
                    "indicator": {
                        "id": "LP.LPI.OVRL.XQ",
                        "value": "Logistics performance index: Overall (1=low to 5=high)"
                    },
                    "country": {
                        "id": "EG",
                        "value": "Egypt, Arab Rep."
                    },
                    "countryiso3code": "EGY",
                    "date": "2022",
                    "value": 3.1,
                    "unit": "",
                    "obs_status": "",
                    "decimal": 2
                }
            ]
        ]

        with patch.object(WorldBankLpiApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("test", context={"country": "EG", "indicator": "LP.LPI.OVRL.XQ"}, sources=["other-source"], limit=10)
            )

        assert result["sources"] == ["worldbank-lpi"]

    def test_default_indicator_when_not_provided(self):
        adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "base_url": "https://api.worldbank.org/v2",
                "source_id": "worldbank-lpi",
            }
        )

        raw_response = [
            {
                "page": 1,
                "pages": 1,
                "per_page": 10,
                "total": 1,
                "sourceid": "2",
                "lastupdated": "2026-07-13",
            },
            [
                {
                    "indicator": {
                        "id": "LP.LPI.OVRL.XQ",
                        "value": "Logistics performance index: Overall (1=low to 5=high)"
                    },
                    "country": {
                        "id": "EG",
                        "value": "Egypt, Arab Rep."
                    },
                    "countryiso3code": "EGY",
                    "date": "2022",
                    "value": 3.1,
                    "unit": "",
                    "obs_status": "",
                    "decimal": 2
                }
            ]
        ]

        with patch.object(WorldBankLpiApiClient, "request", new_callable=AsyncMock, return_value=raw_response) as mock_request:
            result = asyncio.run(
                adapter.query("test", context={"country": "EG"}, limit=10)
            )

        assert len(result["results"]) == 1
        called_path = mock_request.call_args.kwargs["path"]
        assert "LP.LPI.OVRL.XQ" in called_path

    def test_scope_parameter_sets_indicator(self):
        adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "base_url": "https://api.worldbank.org/v2",
                "source_id": "worldbank-lpi",
            }
        )

        raw_response = [
            {
                "page": 1,
                "pages": 1,
                "per_page": 10,
                "total": 1,
                "sourceid": "2",
                "lastupdated": "2026-07-13",
            },
            [
                {
                    "indicator": {
                        "id": "LP.LPI.CUST.XQ",
                        "value": "Efficiency of customs clearance process (1=low to 5=high)"
                    },
                    "country": {
                        "id": "EG",
                        "value": "Egypt, Arab Rep."
                    },
                    "countryiso3code": "EGY",
                    "date": "2022",
                    "value": 3.0,
                    "unit": "",
                    "obs_status": "",
                    "decimal": 2
                }
            ]
        ]

        with patch.object(WorldBankLpiApiClient, "request", new_callable=AsyncMock, return_value=raw_response) as mock_request:
            result = asyncio.run(
                adapter.query("test", context={"country": "EG"}, scope="LP.LPI.CUST.XQ", limit=10)
            )

        assert len(result["results"]) == 1
        assert result["results"][0]["metadata"]["indicator_id"] == "LP.LPI.CUST.XQ"

    def test_confidence_lower_for_missing_value(self):
        adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "base_url": "https://api.worldbank.org/v2",
                "source_id": "worldbank-lpi",
            }
        )

        raw_response = [
            {
                "page": 1,
                "pages": 1,
                "per_page": 10,
                "total": 1,
                "sourceid": "2",
                "lastupdated": "2026-07-13",
            },
            [
                {
                    "indicator": {
                        "id": "LP.LPI.OVRL.XQ",
                        "value": "Logistics performance index: Overall (1=low to 5=high)"
                    },
                    "country": {
                        "id": "EG",
                        "value": "Egypt, Arab Rep."
                    },
                    "countryiso3code": "EGY",
                    "date": "2022",
                    "value": None,
                    "unit": "",
                    "obs_status": "",
                    "decimal": 2
                }
            ]
        ]

        with patch.object(WorldBankLpiApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("test", context={"country": "EG", "indicator": "LP.LPI.OVRL.XQ"}, limit=10)
            )

        assert result["results"][0]["confidence"] == 0.6

    def test_confidence_lower_for_non_empty_obs_status(self):
        adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "base_url": "https://api.worldbank.org/v2",
                "source_id": "worldbank-lpi",
            }
        )

        raw_response = [
            {
                "page": 1,
                "pages": 1,
                "per_page": 10,
                "total": 1,
                "sourceid": "2",
                "lastupdated": "2026-07-13",
            },
            [
                {
                    "indicator": {
                        "id": "LP.LPI.OVRL.XQ",
                        "value": "Logistics performance index: Overall (1=low to 5=high)"
                    },
                    "country": {
                        "id": "EG",
                        "value": "Egypt, Arab Rep."
                    },
                    "countryiso3code": "EGY",
                    "date": "2022",
                    "value": 3.1,
                    "unit": "",
                    "obs_status": "X",
                    "decimal": 2
                }
            ]
        ]

        with patch.object(WorldBankLpiApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("test", context={"country": "EG", "indicator": "LP.LPI.OVRL.XQ"}, limit=10)
            )

        assert result["results"][0]["confidence"] == 0.75

    def test_envelope_response_extracts_real_egypt_lpi_2022(self):
        """Prove that the real World Bank API envelope [metadata, records] extracts Egypt 2022 LPI correctly."""
        adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "base_url": "https://api.worldbank.org/v2",
                "source_id": "worldbank-lpi",
                "name": "World Bank Logistics Performance Index",
                "type": "external_logistics_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-18T00:00:00Z",
            }
        )

        raw_response = [
            {
                "page": 1,
                "pages": 1,
                "per_page": 10,
                "total": 1,
                "sourceid": "2",
                "lastupdated": "2026-07-13",
            },
            [
                {
                    "indicator": {
                        "id": "LP.LPI.OVRL.XQ",
                        "value": "Logistics performance index: Overall (1=low to 5=high)"
                    },
                    "country": {
                        "id": "EG",
                        "value": "Egypt, Arab Rep."
                    },
                    "countryiso3code": "EGY",
                    "date": "2022",
                    "value": 3.1,
                    "unit": "",
                    "obs_status": "",
                    "decimal": 2
                }
            ]
        ]

        with patch.object(WorldBankLpiApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("Egypt logistics", context={"country": "EG", "indicator": "LP.LPI.OVRL.XQ", "year": "2022"}, limit=10)
            )

        assert result["sources"] == ["worldbank-lpi"]
        assert len(result["results"]) == 1
        item = result["results"][0]
        assert item["confidence"] == 0.95
        assert item["source_id"] == "worldbank-lpi"
        assert item["metadata"]["indicator_id"] == "LP.LPI.OVRL.XQ"
        assert item["metadata"]["indicator_name"] == "Logistics performance index: Overall (1=low to 5=high)"
        assert item["metadata"]["country_code"] == "EG"
        assert item["metadata"]["country_name"] == "Egypt, Arab Rep."
        assert item["metadata"]["countryiso3code"] == "EGY"
        assert item["metadata"]["year"] == "2022"
        assert item["metadata"]["value"] == 3.1
        assert item["metadata"]["source_authority"] == "World Bank"
        assert item["metadata"]["retrieval_status"] == "success"
        assert item["metadata"]["updated_at"] == "2026-08-18T00:00:00Z"
        assert item["metadata"]["version"] == "1.0.0"
        assert "id" in item
        assert "content" in item
        assert "World Bank LPI" not in item["content"]
        assert "2022" in item["content"]
        assert "3.1" in item["content"]
        assert "record_hash" in item["metadata"]
        assert item["metadata"]["record_hash"] != ""
