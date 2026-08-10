import pytest
import httpx
from unittest.mock import patch, MagicMock

from app.research.retrieval.contracts import (
    RetrievedContent,
    RetrievalResult,
    RetrievalStatus,
)
from app.research.retrieval.providers.capability import ProviderCapability
from app.research.retrieval.providers.router import SearchProviderRouter
from app.research.retrieval.providers.searxng_adapter import SearXNGAdapter
from app.schemas.research import Source


def _make_adapter(base_url="http://localhost:8080", api_key="", timeout=10.0):
    capability = ProviderCapability(
        provider_id="searxng",
        supports_web_search=True,
        supports_snippets=True,
        supports_source_urls=True,
        requires_api_key=bool(api_key),
        priority=10,
        enabled=True,
    )
    return SearXNGAdapter(
        capability=capability,
        base_url=base_url,
        api_key=api_key,
        timeout=timeout,
    )


def _make_source(source_id="src_1"):
    return Source(
        source_id=source_id,
        name="Test Source",
        source_type="market_data",
        reference="https://example.com",
        metadata={},
        status="active",
    )


def _make_response(status_code=200, json_data=None, text=None):
    response = MagicMock()
    response.status_code = status_code
    if json_data is not None:
        response.json.return_value = json_data
    if text is not None:
        response.text = text
    return response


def _patch_async_client(mock_client_cls, response=None, side_effect=None):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    calls = []

    async def _mock_get(*args, **kwargs):
        calls.append((args, kwargs))
        if side_effect is not None:
            raise side_effect
        return response

    mock_client.get = _mock_get
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client._calls = calls
    return mock_client


class TestSearXNGAdapterRetrieve:
    @pytest.mark.asyncio
    async def test_retrieve_success(self):
        adapter = _make_adapter()
        source = _make_source()
        json_data = {
            "results": [
                {"title": "Result 1", "url": "https://example.com/1", "content": "Content 1"},
                {"title": "Result 2", "url": "https://example.com/2", "content": "Content 2"},
            ]
        }

        with patch("app.research.retrieval.providers.searxng_adapter.httpx.AsyncClient") as mock_client_cls:
            mock_response = _make_response(status_code=200, json_data=json_data)
            _patch_async_client(mock_client_cls, response=mock_response)

            result = await adapter.retrieve(source, "test query")

        assert result.status == RetrievalStatus.SUCCESS
        assert result.source_id == "src_1"
        assert result.content is not None
        assert result.content.raw_content["query"] == "test query"
        assert len(result.content.raw_content["results"]) == 2
        assert result.content.metadata["provider"] == "searxng"
        assert result.content.metadata["result_count"] == 2

    @pytest.mark.asyncio
    async def test_retrieve_timeout(self):
        adapter = _make_adapter()
        source = _make_source()

        with patch("app.research.retrieval.providers.searxng_adapter.httpx.AsyncClient") as mock_client_cls:
            _patch_async_client(mock_client_cls, side_effect=httpx.TimeoutException("timeout"))

            result = await adapter.retrieve(source, "test query")

        assert result.status == RetrievalStatus.TIMEOUT
        assert result.source_id == "src_1"
        assert "timed out" in (result.error or "").lower()

    @pytest.mark.asyncio
    async def test_retrieve_connection_failure(self):
        adapter = _make_adapter()
        source = _make_source()

        with patch("app.research.retrieval.providers.searxng_adapter.httpx.AsyncClient") as mock_client_cls:
            _patch_async_client(mock_client_cls, side_effect=httpx.ConnectError("connection failed"))

            result = await adapter.retrieve(source, "test query")

        assert result.status == RetrievalStatus.CONNECTION_FAILURE
        assert result.source_id == "src_1"
        assert "connection failed" in (result.error or "").lower()

    @pytest.mark.asyncio
    async def test_retrieve_http_error(self):
        adapter = _make_adapter()
        source = _make_source()

        with patch("app.research.retrieval.providers.searxng_adapter.httpx.AsyncClient") as mock_client_cls:
            _patch_async_client(mock_client_cls, side_effect=httpx.HTTPError("HTTP error"))

            result = await adapter.retrieve(source, "test query")

        assert result.status == RetrievalStatus.CONNECTION_FAILURE
        assert result.source_id == "src_1"

    @pytest.mark.asyncio
    async def test_retrieve_non_200_status(self):
        adapter = _make_adapter()
        source = _make_source()

        with patch("app.research.retrieval.providers.searxng_adapter.httpx.AsyncClient") as mock_client_cls:
            mock_response = _make_response(status_code=500)
            _patch_async_client(mock_client_cls, response=mock_response)

            result = await adapter.retrieve(source, "test query")

        assert result.status == RetrievalStatus.CONNECTION_FAILURE
        assert result.source_id == "src_1"
        assert "500" in (result.error or "")

    @pytest.mark.asyncio
    async def test_retrieve_invalid_json(self):
        adapter = _make_adapter()
        source = _make_source()

        with patch("app.research.retrieval.providers.searxng_adapter.httpx.AsyncClient") as mock_client_cls:
            mock_response = _make_response(status_code=200)
            mock_response.json.side_effect = ValueError("invalid json")
            _patch_async_client(mock_client_cls, response=mock_response)

            result = await adapter.retrieve(source, "test query")

        assert result.status == RetrievalStatus.INVALID_RESPONSE
        assert result.source_id == "src_1"
        assert "invalid json" in (result.error or "").lower()

    @pytest.mark.asyncio
    async def test_retrieve_missing_results_list(self):
        adapter = _make_adapter()
        source = _make_source()

        with patch("app.research.retrieval.providers.searxng_adapter.httpx.AsyncClient") as mock_client_cls:
            mock_response = _make_response(status_code=200, json_data={"message": "ok"})
            _patch_async_client(mock_client_cls, response=mock_response)

            result = await adapter.retrieve(source, "test query")

        assert result.status == RetrievalStatus.INVALID_RESPONSE
        assert result.source_id == "src_1"
        assert "results list" in (result.error or "").lower()

    @pytest.mark.asyncio
    async def test_retrieve_with_api_key(self):
        adapter = _make_adapter(api_key="secret-key")
        source = _make_source()
        json_data = {"results": [{"title": "R1", "url": "https://example.com", "content": "C1"}]}

        with patch("app.research.retrieval.providers.searxng_adapter.httpx.AsyncClient") as mock_client_cls:
            mock_response = _make_response(status_code=200, json_data=json_data)
            mock_client = _patch_async_client(mock_client_cls, response=mock_response)

            await adapter.retrieve(source, "test query")

        call_args = mock_client._calls[0]
        assert call_args is not None
        headers = call_args[1].get("headers", {})
        assert headers.get("Authorization") == "Bearer secret-key"


class TestSearXNGAdapterHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        adapter = _make_adapter()

        with patch("app.research.retrieval.providers.searxng_adapter.httpx.AsyncClient") as mock_client_cls:
            mock_response = _make_response(status_code=200)
            _patch_async_client(mock_client_cls, response=mock_response)

            result = await adapter.health_check()

        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        adapter = _make_adapter()

        with patch("app.research.retrieval.providers.searxng_adapter.httpx.AsyncClient") as mock_client_cls:
            _patch_async_client(mock_client_cls, side_effect=Exception("connection error"))

            result = await adapter.health_check()

        assert result is False


class TestSearXNGAdapterWithRouter:
    @pytest.mark.asyncio
    async def test_searxng_adapter_with_router_success(self):
        adapter = _make_adapter()
        router = SearchProviderRouter()
        router.register_adapter(adapter)
        source = _make_source()
        json_data = {"results": [{"title": "R1", "url": "https://example.com", "content": "C1"}]}

        with patch("app.research.retrieval.providers.searxng_adapter.httpx.AsyncClient") as mock_client_cls:
            mock_response = _make_response(status_code=200, json_data=json_data)
            _patch_async_client(mock_client_cls, response=mock_response)

            result = await router.retrieve_with_fallback(source, "query")

        assert result.status == RetrievalStatus.SUCCESS
        assert result.content is not None

    @pytest.mark.asyncio
    async def test_searxng_failure_does_not_use_stub_retriever(self):
        adapter = _make_adapter()
        router = SearchProviderRouter()
        router.register_adapter(adapter)
        source = _make_source()

        with patch("app.research.retrieval.providers.searxng_adapter.httpx.AsyncClient") as mock_client_cls:
            _patch_async_client(mock_client_cls, side_effect=httpx.ConnectError("connection failed"))

            result = await router.retrieve_with_fallback(source, "query")

        assert result.status == RetrievalStatus.FAILED
        assert "stub" not in (result.error or "").lower()
