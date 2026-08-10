import pytest
from app.research.retrieval.contracts import SourceRetriever
from app.research.retrieval.providers.capability import ProviderCapability
from app.research.retrieval.providers.adapter import SearchProviderAdapter
from app.schemas.research import Source


class TestProviderCapability:
    def test_defaults(self):
        capability = ProviderCapability(provider_id="test")
        assert capability.provider_id == "test"
        assert capability.supports_web_search is True
        assert capability.supports_source_urls is False
        assert capability.supports_snippets is False
        assert capability.supports_content_fetch is False
        assert capability.supports_time_range is False
        assert capability.supports_domain_filter is False
        assert capability.requires_api_key is False
        assert capability.has_usage_limit is False
        assert capability.usage_limit_description is None
        assert capability.priority == 100
        assert capability.enabled is True

    def test_custom_values(self):
        capability = ProviderCapability(
            provider_id="custom",
            supports_source_urls=True,
            supports_snippets=True,
            requires_api_key=True,
            priority=10,
        )
        assert capability.supports_source_urls is True
        assert capability.supports_snippets is True
        assert capability.requires_api_key is True
        assert capability.priority == 10

    def test_to_dict_serialization(self):
        capability = ProviderCapability(
            provider_id="serial",
            supports_source_urls=True,
            priority=5,
        )
        data = capability.to_dict()
        assert data["provider_id"] == "serial"
        assert data["supports_source_urls"] is True
        assert data["priority"] == 5
        assert data["enabled"] is True

    def test_provider_id_required(self):
        with pytest.raises(TypeError):
            ProviderCapability()

    def test_disabled_provider(self):
        capability = ProviderCapability(provider_id="disabled", enabled=False)
        assert capability.enabled is False


class ConcreteAdapter(SearchProviderAdapter):
    """Concrete implementation for testing the adapter interface."""

    def __init__(self, capability: ProviderCapability):
        self._capability = capability

    @property
    def capability(self) -> ProviderCapability:
        return self._capability

    async def retrieve(self, source: Source, query: str):
        pass

    async def health_check(self) -> bool:
        return True


class TestSearchProviderAdapter:
    def test_is_source_retriever(self):
        capability = ProviderCapability(provider_id="adapter_test")
        adapter = ConcreteAdapter(capability)
        assert isinstance(adapter, SourceRetriever)

    def test_capability_exposed(self):
        capability = ProviderCapability(provider_id="adapter_test", priority=1)
        adapter = ConcreteAdapter(capability)
        assert adapter.capability.provider_id == "adapter_test"
        assert adapter.capability.priority == 1

    @pytest.mark.asyncio
    async def test_health_check_true(self):
        capability = ProviderCapability(provider_id="healthy")
        adapter = ConcreteAdapter(capability)
        assert await adapter.health_check() is True

    def test_abstract_methods_must_be_implemented(self):
        with pytest.raises(TypeError):
            SearchProviderAdapter()

    def test_multiple_adapters_are_independent(self):
        cap_a = ProviderCapability(provider_id="a", priority=1)
        cap_b = ProviderCapability(provider_id="b", priority=2)
        adapter_a = ConcreteAdapter(cap_a)
        adapter_b = ConcreteAdapter(cap_b)
        assert adapter_a.capability.provider_id == "a"
        assert adapter_b.capability.provider_id == "b"
        assert adapter_a.capability.priority != adapter_b.capability.priority
