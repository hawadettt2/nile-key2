import pytest

from app.research.retrieval.contracts import (
    RetrievedContent,
    RetrievalResult,
    RetrievalStatus,
)
from app.research.retrieval.providers.adapter import SearchProviderAdapter
from app.research.retrieval.providers.capability import ProviderCapability
from app.research.retrieval.providers.router import SearchProviderRouter
from app.schemas.research import Source


def _make_adapter(provider_id, priority=100, enabled=True, supports_web_search=True, retrieve_result=None, raise_exc=None):
    capability = ProviderCapability(
        provider_id=provider_id,
        priority=priority,
        enabled=enabled,
        supports_web_search=supports_web_search,
    )

    class ConcreteAdapter(SearchProviderAdapter):
        def __init__(self, capability, retrieve_result=None, raise_exc=None):
            self._capability = capability
            self._retrieve_result = retrieve_result
            self._raise_exc = raise_exc

        @property
        def capability(self):
            return self._capability

        async def retrieve(self, source, query):
            if self._raise_exc:
                raise self._raise_exc
            return self._retrieve_result

        async def health_check(self):
            return True

    return ConcreteAdapter(capability, retrieve_result=retrieve_result, raise_exc=raise_exc)


def _make_source(source_id="src_1"):
    return Source(
        source_id=source_id,
        name="Test Source",
        source_type="market_data",
        reference="https://example.com",
        metadata={},
        status="active",
    )


def _success_result(source_id):
    return RetrievalResult(
        source_id=source_id,
        status=RetrievalStatus.SUCCESS,
        content=RetrievedContent(
            source_id=source_id,
            raw_content={"data": "success"},
            content_type="application/json",
            metadata={},
        ),
    )


def _fail_result(source_id, status=RetrievalStatus.FAILED, error="failed"):
    return RetrievalResult(
        source_id=source_id,
        status=status,
        error=error,
    )


class TestSearchProviderRouter:
    def test_register_adapter(self):
        router = SearchProviderRouter()
        adapter = _make_adapter("a")
        router.register_adapter(adapter)
        assert len(router._adapters) == 1

    def test_unregister_adapter(self):
        router = SearchProviderRouter()
        adapter = _make_adapter("a")
        router.register_adapter(adapter)
        router.unregister_adapter(adapter)
        assert len(router._adapters) == 0

    def test_priority_ordering(self):
        router = SearchProviderRouter()
        low = _make_adapter("low", priority=200)
        high = _make_adapter("high", priority=10)
        router.register_adapter(low)
        router.register_adapter(high)

        qualified = router._get_qualified_adapters()
        assert qualified[0].capability.provider_id == "high"
        assert qualified[1].capability.provider_id == "low"

    def test_enabled_filtering(self):
        router = SearchProviderRouter()
        disabled = _make_adapter("disabled", enabled=False)
        enabled = _make_adapter("enabled", enabled=True)
        router.register_adapter(disabled)
        router.register_adapter(enabled)

        qualified = router._get_qualified_adapters()
        assert len(qualified) == 1
        assert qualified[0].capability.provider_id == "enabled"

    def test_supports_web_search_filtering(self):
        router = SearchProviderRouter()
        no_web = _make_adapter("no_web", supports_web_search=False)
        web = _make_adapter("web", supports_web_search=True)
        router.register_adapter(no_web)
        router.register_adapter(web)

        qualified = router._get_qualified_adapters()
        assert len(qualified) == 1
        assert qualified[0].capability.provider_id == "web"

    @pytest.mark.asyncio
    async def test_success_first_adapter(self):
        router = SearchProviderRouter()
        source = _make_source()
        adapter = _make_adapter("a", retrieve_result=_success_result("src_1"))
        router.register_adapter(adapter)

        result = await router.retrieve_with_fallback(source, "query")
        assert result.status == RetrievalStatus.SUCCESS
        assert result.content.raw_content == {"data": "success"}

    @pytest.mark.asyncio
    async def test_failover_on_failure(self):
        router = SearchProviderRouter()
        source = _make_source()
        failing = _make_adapter("failing", retrieve_result=_fail_result("src_1", RetrievalStatus.TIMEOUT))
        succeeding = _make_adapter("succeeding", retrieve_result=_success_result("src_1"))
        router.register_adapter(failing)
        router.register_adapter(succeeding)

        result = await router.retrieve_with_fallback(source, "query")
        assert result.status == RetrievalStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_all_adapters_fail(self):
        router = SearchProviderRouter()
        source = _make_source()
        fail1 = _make_adapter("fail1", retrieve_result=_fail_result("src_1", RetrievalStatus.TIMEOUT))
        fail2 = _make_adapter("fail2", retrieve_result=_fail_result("src_1", RetrievalStatus.CONNECTION_FAILURE))
        router.register_adapter(fail1)
        router.register_adapter(fail2)

        result = await router.retrieve_with_fallback(source, "query")
        assert result.status == RetrievalStatus.FAILED
        assert "All search adapters failed" in (result.error or "")

    @pytest.mark.asyncio
    async def test_no_qualified_adapters(self):
        router = SearchProviderRouter()
        source = _make_source()
        disabled = _make_adapter("disabled", enabled=False)
        router.register_adapter(disabled)

        result = await router.retrieve_with_fallback(source, "query")
        assert result.status == RetrievalStatus.FAILED
        assert "No qualified search adapters available" in (result.error or "")

    @pytest.mark.asyncio
    async def test_no_stub_retriever_used_automatically(self):
        router = SearchProviderRouter()
        source = _make_source()
        fail = _make_adapter("fail", retrieve_result=_fail_result("src_1"))
        router.register_adapter(fail)

        result = await router.retrieve_with_fallback(source, "query")
        assert result.status == RetrievalStatus.FAILED
        assert "stub" not in (result.error or "").lower()

    def test_no_provider_is_primary(self):
        router = SearchProviderRouter()
        a = _make_adapter("a", priority=1)
        b = _make_adapter("b", priority=2)
        router.register_adapter(a)
        router.register_adapter(b)

        qualified = router._get_qualified_adapters()
        assert qualified[0].capability.provider_id == "a"
        assert qualified[1].capability.provider_id == "b"
