import pytest
from app.agent.knowledge.orchestrator import KnowledgeOrchestrator


class FakeRegistry:
    def __init__(self, providers=None):
        self._providers = {p["id"]: p for p in (providers or [])}

    def exists(self, source_id):
        return source_id in self._providers

    def list_providers(self):
        return list(self._providers.values())


class FakeConfig:
    KNOWLEDGE_ORCHESTRATION_DEDUP_ENABLED = True
    KNOWLEDGE_ORCHESTRATION_CONFLICT_STRATEGY = "latest_official_wins"


@pytest.fixture
def orchestrator():
    registry = FakeRegistry()
    config = FakeConfig()
    return KnowledgeOrchestrator(registry, config)


class TestClassification:
    def test_agrifood_english(self, orchestrator):
        assert orchestrator._classify_query("agriculture export") == "agrifood"

    def test_agrifood_food(self, orchestrator):
        assert orchestrator._classify_query("food commodity") == "agrifood"

    def test_agrifood_crop_livestock(self, orchestrator):
        assert orchestrator._classify_query("crop livestock") == "agrifood"

    def test_customs_english(self, orchestrator):
        assert orchestrator._classify_query("customs declaration HS code") == "customs"

    def test_customs_arabic(self, orchestrator):
        assert orchestrator._classify_query("جمارك تصريح") == "customs"

    def test_regulatory_english(self, orchestrator):
        assert orchestrator._classify_query("regulation law") == "regulatory"

    def test_regulatory_arabic(self, orchestrator):
        assert orchestrator._classify_query("قانون لائحة") == "regulatory"

    def test_market_access_english(self, orchestrator):
        assert orchestrator._classify_query("market access duty") == "market_access"

    def test_market_access_arabic(self, orchestrator):
        assert orchestrator._classify_query("requirement متطلبات") == "market_access"

    def test_market_access_overlap_tariff(self, orchestrator):
        assert orchestrator._classify_query("duty requirement") == "market_access"

    def test_trade_statistics_english(self, orchestrator):
        assert orchestrator._classify_query("trade statistics export") == "trade_statistics"

    def test_trade_statistics_arabic(self, orchestrator):
        assert orchestrator._classify_query("import إحصائيات") == "trade_statistics"

    def test_rules_of_origin_english(self, orchestrator):
        assert orchestrator._classify_query("origin certificate") == "rules_of_origin"

    def test_rules_of_origin_arabic(self, orchestrator):
        assert orchestrator._classify_query("شهادة منشأ") == "rules_of_origin"

    def test_general_no_match(self, orchestrator):
        assert orchestrator._classify_query("random unrelated text") == "general"

    def test_market_access_overlap_export_tariff_regulation(self, orchestrator):
        assert orchestrator._classify_query("market access regulation") == "market_access"

    def test_deterministic_same_output(self, orchestrator):
        query = "export tariff regulation"
        results = [orchestrator._classify_query(query) for _ in range(100)]
        assert len(set(results)) == 1
