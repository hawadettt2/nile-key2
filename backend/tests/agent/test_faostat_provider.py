import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

import httpx
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
                "username": "test@example.com",
                "password": "test-password",
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

        with patch.object(FaostatApiClient, "_login", new_callable=AsyncMock):
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
                "username": "test@example.com",
                "password": "test-password",
            }
        )

        with patch.object(FaostatApiClient, "_login", new_callable=AsyncMock):
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
                "username": "test@example.com",
                "password": "test-password",
            }
        )

        with patch.object(FaostatApiClient, "_login", new_callable=AsyncMock):
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
                "username": "test@example.com",
                "password": "test-password",
            }
        )

        with patch.object(FaostatApiClient, "_login", new_callable=AsyncMock):
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
                "username": "test@example.com",
                "password": "test-password",
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

    def test_login_failure_returns_empty_results(self):
        adapter = FaostatExternalSourceAdapter(
            config={
                "base_url": "https://faostatservices.fao.org/api/v1",
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
                "username": "test@example.com",
                "password": "wrong-password",
            }
        )

        with patch.object(FaostatApiClient, "_login", new_callable=AsyncMock, side_effect=ValueError("Login failed")):
            result = asyncio.run(
                adapter.query("test", context={"area": "Egypt"}, scope="QC", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["faostat"]


class TestFaostatApiClientAuth:
    """Verify FaostatApiClient authentication lifecycle."""

    def test_login_sends_correct_request(self):
        client = FaostatApiClient(
            base_url="https://faostatservices.fao.org/api/v1",
            username="test@example.com",
            password="test-password",
        )

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={
            "AuthenticationResult": {
                "AccessToken": "test-access-token",
                "RefreshToken": "test-refresh-token",
            }
        })

        async def mock_post(url, **kwargs):
            assert url == "https://faostatservices.fao.org/api/v1/auth/login"
            assert kwargs["headers"]["Content-Type"] == "application/x-www-form-urlencoded"
            assert kwargs["data"] == {
                "username": "test@example.com",
                "password": "test-password",
            }
            return mock_response

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, side_effect=mock_post):
            asyncio.run(client._login())

        assert client._access_token == "test-access-token"
        assert client._token_expires_at is not None

    def test_login_handles_missing_credentials(self):
        client = FaostatApiClient(
            base_url="https://faostatservices.fao.org/api/v1",
            username=None,
            password=None,
        )

        asyncio.run(client._login())
        assert client._access_token is None
        assert client._token_expires_at is None

    def test_login_handles_http_error(self):
        client = FaostatApiClient(
            base_url="https://faostatservices.fao.org/api/v1",
            username="test@example.com",
            password="wrong-password",
        )

        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.raise_for_status = Mock(side_effect=httpx.HTTPStatusError("401", request=Mock(), response=mock_response))

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(httpx.HTTPStatusError):
                asyncio.run(client._login())

        assert client._access_token is None
        assert client._token_expires_at is None

    def test_login_handles_missing_access_token_in_response(self):
        client = FaostatApiClient(
            base_url="https://faostatservices.fao.org/api/v1",
            username="test@example.com",
            password="test-password",
        )

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={"AuthenticationResult": {}})

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(ValueError, match="missing AccessToken"):
                asyncio.run(client._login())

        assert client._access_token is None
        assert client._token_expires_at is None

    def test_headers_include_authorization_after_login(self):
        client = FaostatApiClient(
            base_url="https://faostatservices.fao.org/api/v1",
            username="test@example.com",
            password="test-password",
        )
        client._access_token = "test-token"
        client._token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

        headers = client._headers()
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Accept"] == "application/json"

    def test_headers_exclude_authorization_before_login(self):
        client = FaostatApiClient(
            base_url="https://faostatservices.fao.org/api/v1",
            username="test@example.com",
            password="test-password",
        )

        headers = client._headers()
        assert "Authorization" not in headers
        assert headers["Accept"] == "application/json"

    def test_reauth_on_401(self):
        client = FaostatApiClient(
            base_url="https://faostatservices.fao.org/api/v1",
            username="test@example.com",
            password="test-password",
        )
        client._access_token = "expired-token"
        client._token_expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)

        mock_data_response = AsyncMock()
        mock_data_response.status_code = 200
        mock_data_response.json = Mock(return_value={"data": []})
        mock_data_response.raise_for_status = Mock()

        mock_login_response = AsyncMock()
        mock_login_response.status_code = 200
        mock_login_response.json = Mock(return_value={
            "AuthenticationResult": {
                "AccessToken": "new-token",
            }
        })
        mock_login_response.raise_for_status = Mock()

        call_count = 0

        async def mock_post(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            url = args[0] if args else kwargs.get("url", "")
            if url.endswith("/auth/login"):
                return mock_login_response
            return mock_data_response

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, side_effect=mock_post):
            with patch("httpx.AsyncClient.request", new_callable=AsyncMock, side_effect=mock_post):
                result = asyncio.run(client.request("GET", "/en/data/QCL", params={"format": "json"}))

        assert result == {"data": []}
        assert client._access_token == "new-token"

    def test_no_infinite_reauth_loop_on_login_failure(self):
        client = FaostatApiClient(
            base_url="https://faostatservices.fao.org/api/v1",
            username="test@example.com",
            password="wrong-password",
        )

        mock_login_response = AsyncMock()
        mock_login_response.status_code = 401
        mock_login_response.raise_for_status = Mock(side_effect=httpx.HTTPStatusError("401", request=Mock(), response=mock_login_response))

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_login_response):
            with pytest.raises(httpx.HTTPStatusError):
                asyncio.run(client.request("GET", "/en/data/QCL", params={"format": "json"}))

    def test_credentials_not_logged(self):
        client = FaostatApiClient(
            base_url="https://faostatservices.fao.org/api/v1",
            username="secret-user",
            password="secret-password",
        )

        with patch("logging.Logger.info") as mock_log:
            client._login = AsyncMock(side_effect=ValueError("Login failed"))
            try:
                asyncio.run(client.request("GET", "/en/data/QCL"))
            except ValueError:
                pass

        for call in mock_log.call_args_list:
            assert "secret-user" not in str(call)
            assert "secret-password" not in str(call)


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
                "username": "test@example.com",
                "password": "test-password",
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

        with patch.object(FaostatApiClient, "_login", new_callable=AsyncMock):
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
                "username": "test@example.com",
                "password": "test-password",
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

        with patch.object(FaostatApiClient, "_login", new_callable=AsyncMock):
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
                "username": "test@example.com",
                "password": "test-password",
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

        with patch.object(FaostatApiClient, "_login", new_callable=AsyncMock):
            with patch.object(FaostatApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
                result = asyncio.run(
                    adapter.query("wheat production", context={"area": "Egypt"}, scope="QC", limit=10)
                )

        item = result["results"][0]
        assert item["metadata"]["source_url"] == "https://faostatservices.fao.org/api/v1/en/data/QC?format=json"
