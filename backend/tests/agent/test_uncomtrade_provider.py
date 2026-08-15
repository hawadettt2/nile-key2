import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.knowledge.uncomtrade_provider import UnComtradeExternalSourceAdapter
from app.agent.knowledge.uncomtrade_client import UnComtradeApiClient


class TestUnComtradeAdapterContract:
    """Verify UN Comtrade external source adapter contract boundaries."""

    def test_get_sources_returns_registry_compatible_entry(self):
        adapter = UnComtradeExternalSourceAdapter(
            config={
                "source_id": "un-comtrade",
                "name": "UN Comtrade External Knowledge",
                "type": "external_trade_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-15T00:00:00Z",
            }
        )

        sources = asyncio.run(adapter.get_sources())
        assert len(sources) == 1
        source = sources[0]
        assert source["id"] == "un-comtrade"
        assert source["name"] == "UN Comtrade External Knowledge"
        assert source["type"] == "external_trade_intelligence"
        assert source["version"] == "1.0.0"
        assert source["updated_at"] == "2026-08-15T00:00:00Z"

    def test_default_source_metadata_when_config_is_empty(self):
        adapter = UnComtradeExternalSourceAdapter()

        sources = asyncio.run(adapter.get_sources())
        assert sources[0]["id"] == "un-comtrade"
        assert sources[0]["type"] == "external_trade_intelligence"


class TestUnComtradeAdapterQuery:
    """Verify UN Comtrade adapter query transformation and error handling."""

    def test_successful_response_transforms_to_contract_shape(self):
        adapter = UnComtradeExternalSourceAdapter(
            config={
                "base_url": "https://comtradeapi.un.org",
                "source_id": "un-comtrade",
                "name": "UN Comtrade External Knowledge",
                "type": "external_trade_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-15T00:00:00Z",
            }
        )

        raw_response = {
            "data": [
                {
                    "typeCode": "C",
                    "freqCode": "A",
                    "refYear": 2023,
                    "reporterCode": 156,
                    "reporterDesc": "China",
                    "partnerCode": 842,
                    "partnerDesc": "World",
                    "classificationCode": "HS",
                    "cmdCode": "090111",
                    "cmdDesc": "Tea, green, in packages",
                    "flowCode": "X",
                    "fobvalue": 12494.0,
                    "netWgt": 8226.0,
                    "qty": 0.0,
                    "altQty": 23534.0,
                    "isReported": True,
                    "isAggregate": False,
                }
            ]
        }

        with patch.object(UnComtradeApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("tea exports", context={"reporter": 156, "partner": 842, "period": 2023}, limit=10)
            )

        assert "results" in result
        assert "confidence" in result
        assert "sources" in result
        assert result["sources"] == ["un-comtrade"]
        assert len(result["results"]) == 1
        item = result["results"][0]
        assert item["source_id"] == "un-comtrade"
        assert item["confidence"] == 0.9
        assert "id" in item
        assert "content" in item
        assert "metadata" in item
        assert item["metadata"]["reporter_code"] == 156
        assert item["metadata"]["reporter_desc"] == "China"
        assert item["metadata"]["partner_code"] == 842
        assert item["metadata"]["cmd_code"] == "090111"
        assert item["metadata"]["cmd_desc"] == "Tea, green, in packages"
        assert item["metadata"]["ref_year"] == 2023
        assert item["metadata"]["fobvalue"] == 12494.0
        assert item["metadata"]["source_authority"] == "UN"
        assert item["metadata"]["retrieval_status"] == "success"

    def test_empty_dataset_returns_empty_results(self):
        adapter = UnComtradeExternalSourceAdapter(
            config={
                "base_url": "https://comtradeapi.un.org",
                "source_id": "un-comtrade",
            }
        )

        with patch.object(UnComtradeApiClient, "request", new_callable=AsyncMock, return_value={"data": []}):
            result = asyncio.run(
                adapter.query("test", context={"reporter": 156}, limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["un-comtrade"]

    def test_malformed_response_returns_empty_results(self):
        adapter = UnComtradeExternalSourceAdapter(
            config={
                "base_url": "https://comtradeapi.un.org",
                "source_id": "un-comtrade",
            }
        )

        with patch.object(UnComtradeApiClient, "request", new_callable=AsyncMock, return_value="not-a-dict"):
            result = asyncio.run(
                adapter.query("test", context={"reporter": 156}, limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["un-comtrade"]

    def test_upstream_failure_returns_empty_results(self):
        adapter = UnComtradeExternalSourceAdapter(
            config={
                "base_url": "https://comtradeapi.un.org",
                "source_id": "un-comtrade",
            }
        )

        with patch.object(UnComtradeApiClient, "request", new_callable=AsyncMock, side_effect=Exception("Upstream error")):
            result = asyncio.run(
                adapter.query("test", context={"reporter": 156}, limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["un-comtrade"]

    def test_missing_base_url_returns_empty_results(self):
        adapter = UnComtradeExternalSourceAdapter(
            config={
                "source_id": "un-comtrade",
            }
        )

        result = asyncio.run(
            adapter.query("test", context={"reporter": 156}, limit=10)
        )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["un-comtrade"]

    def test_sources_parameter_is_accepted_but_not_used(self):
        adapter = UnComtradeExternalSourceAdapter(
            config={
                "base_url": "https://comtradeapi.un.org",
                "source_id": "un-comtrade",
            }
        )

        raw_response = {
            "data": [
                {
                    "typeCode": "C",
                    "freqCode": "A",
                    "refYear": 2023,
                    "reporterCode": 156,
                    "reporterDesc": "China",
                    "partnerCode": 842,
                    "partnerDesc": "World",
                    "classificationCode": "HS",
                    "cmdCode": "090111",
                    "cmdDesc": "Tea, green, in packages",
                    "flowCode": "X",
                    "fobvalue": 12494.0,
                    "netWgt": 8226.0,
                    "qty": 0.0,
                    "altQty": 23534.0,
                    "isReported": True,
                    "isAggregate": False,
                }
            ]
        }

        with patch.object(UnComtradeApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("test", context={"reporter": 156}, sources=["other-source"], limit=10)
            )

        assert result["sources"] == ["un-comtrade"]


class TestUnComtradeContextMapping:
    """Verify context to UN Comtrade parameter mapping."""

    def test_default_parameters_when_context_empty(self):
        adapter = UnComtradeExternalSourceAdapter(
            config={
                "base_url": "https://comtradeapi.un.org",
                "source_id": "un-comtrade",
            }
        )

        path, params = adapter._build_request("test", {}, None, 10)
        assert path == "/public/v1/preview/C/A/HS"
        assert params["flowCode"] == "X"
        assert params["maxrecords"] == 10

    def test_context_maps_to_parameters(self):
        adapter = UnComtradeExternalSourceAdapter(
            config={
                "base_url": "https://comtradeapi.un.org",
                "source_id": "un-comtrade",
            }
        )

        path, params = adapter._build_request(
            "test",
            {"reporter": 156, "partner": 842, "flow": "M", "period": "2022", "frequency": "M", "classification": "SITC"},
            None,
            10,
        )
        assert path == "/public/v1/preview/C/M/SITC"
        assert params["reporterCode"] == 156
        assert params["partnerCode"] == 842
        assert params["flowCode"] == "M"
        assert params["period"] == "2022"
        assert params["maxrecords"] == 10

    def test_scope_maps_to_type_code(self):
        adapter = UnComtradeExternalSourceAdapter(
            config={
                "base_url": "https://comtradeapi.un.org",
                "source_id": "un-comtrade",
            }
        )

        path, params = adapter._build_request("test", {}, "S", 10)
        assert path == "/public/v1/preview/S/A/HS"

    def test_limit_capped_at_500_for_preview(self):
        adapter = UnComtradeExternalSourceAdapter(
            config={
                "base_url": "https://comtradeapi.un.org",
                "source_id": "un-comtrade",
            }
        )

        _, params = adapter._build_request("test", {}, None, 1000)
        assert params["maxrecords"] == 500


class TestUnComtradeConfidence:
    """Verify confidence calculation."""

    def test_reported_record_has_high_confidence(self):
        adapter = UnComtradeExternalSourceAdapter(
            config={
                "base_url": "https://comtradeapi.un.org",
                "source_id": "un-comtrade",
            }
        )

        entry = {
            "reporterCode": 156,
            "partnerCode": 842,
            "cmdCode": "090111",
            "refYear": 2023,
            "fobvalue": 12494.0,
            "isReported": True,
        }
        result = adapter._transform_entry(entry)
        assert result["confidence"] == 0.9

    def test_unreported_record_has_lower_confidence(self):
        adapter = UnComtradeExternalSourceAdapter(
            config={
                "base_url": "https://comtradeapi.un.org",
                "source_id": "un-comtrade",
            }
        )

        entry = {
            "reporterCode": 156,
            "partnerCode": 842,
            "cmdCode": "090111",
            "refYear": 2023,
            "fobvalue": 12494.0,
            "isReported": False,
        }
        result = adapter._transform_entry(entry)
        assert result["confidence"] == 0.7


class TestUnComtradeContent:
    """Verify content string construction."""

    def test_content_with_description(self):
        adapter = UnComtradeExternalSourceAdapter(
            config={
                "base_url": "https://comtradeapi.un.org",
                "source_id": "un-comtrade",
            }
        )

        entry = {
            "cmdDesc": "Tea, green, in packages",
            "cmdCode": "090111",
            "fobvalue": 12494.0,
        }
        result = adapter._transform_entry(entry)
        assert result["content"] == "Tea, green, in packages (090111) — 12494.0 USD"

    def test_content_without_description_falls_back_to_hs_code(self):
        adapter = UnComtradeExternalSourceAdapter(
            config={
                "base_url": "https://comtradeapi.un.org",
                "source_id": "un-comtrade",
            }
        )

        entry = {
            "cmdCode": "090111",
            "fobvalue": 12494.0,
        }
        result = adapter._transform_entry(entry)
        assert result["content"] == "HS 090111 — 12494.0 USD"

