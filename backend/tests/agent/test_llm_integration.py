import pytest
import time
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from app.agent.decision_engine.engine import ReasoningEngine
from app.agent.llm.provider import LLMProviderRegistry, GeminiProvider
from app.agent.session.manager import SessionManager
from app.core.database import get_db


class TestDEMLLMIntegration:
    """Integration tests for DEM with LLM provider (Phase 4)."""

    def setup_method(self):
        self.session_id = "integration-session-123"

    @pytest.mark.asyncio
    async def test_dem_works_with_llm_provider_available(self):
        """DEM reasoning works when LLM provider is available."""
        mock_response = MagicMock()
        mock_response.content = "shipping"
        mock_response.usage_metadata = MagicMock(
            prompt_token_count=5,
            candidates_token_count=10,
            total_token_count=15,
        )
        mock_candidate = MagicMock()
        mock_candidate.finish_reason.name = "STOP"
        mock_response.candidates = [mock_candidate]

        registry = LLMProviderRegistry()
        provider = GeminiProvider(api_key="test-key")
        provider.generate = AsyncMock(return_value=mock_response)
        registry.register(provider)

        engine = ReasoningEngine(llm_registry=registry)

        request = {
            "intent": "Ship my package to Germany",
            "parameters": {"destination": "Germany"},
            "context": {},
        }

        result = await engine.reason(self.session_id, request)

        assert isinstance(result, dict)
        assert "decision_id" in result
        assert "chosen_path" in result
        assert "reasoning" in result
        assert result["chosen_path"] == "shipping"

    @pytest.mark.asyncio
    async def test_dem_works_without_llm_provider(self):
        """DEM reasoning works when LLM provider is not available (graceful degradation)."""
        engine = ReasoningEngine(llm_registry=None)

        request = {
            "intent": "Ship my package to Germany",
            "parameters": {"destination": "Germany"},
            "context": {},
        }

        result = await engine.reason(self.session_id, request)

        assert isinstance(result, dict)
        assert "decision_id" in result
        assert "chosen_path" in result
        assert "reasoning" in result
        assert result["chosen_path"] == "shipping"

    @pytest.mark.asyncio
    async def test_dem_graceful_degradation_when_llm_fails(self):
        """DEM reasoning falls back to deterministic behavior when LLM fails."""
        registry = LLMProviderRegistry()
        provider = GeminiProvider(api_key="test-key")
        provider.generate = AsyncMock(side_effect=Exception("LLM service unavailable"))
        registry.register(provider)

        engine = ReasoningEngine(llm_registry=registry)

        request = {
            "intent": "Ship my package to Germany",
            "parameters": {"destination": "Germany"},
            "context": {},
        }

        result = await engine.reason(self.session_id, request)

        assert isinstance(result, dict)
        assert "decision_id" in result
        assert "chosen_path" in result
        assert "reasoning" in result
        assert result["chosen_path"] == "shipping"

    @pytest.mark.asyncio
    async def test_dem_behavior_unchanged_without_llm(self):
        """Existing DEM behavior is unchanged when LLM is not configured."""
        engine = ReasoningEngine()

        request = {
            "intent": "Submit invoice to ETA",
            "parameters": {},
            "context": {},
        }

        result = await engine.reason(self.session_id, request)

        assert result["chosen_path"] == "eta"
        assert isinstance(result["reasoning"], str)
        assert len(result["reasoning"]) > 0

    @pytest.mark.asyncio
    async def test_dem_multiple_requests_without_llm(self):
        """Multiple DEM requests work correctly without LLM."""
        engine = ReasoningEngine()

        requests = [
            {"intent": "Ship my package to Germany", "parameters": {"destination": "Germany"}, "context": {}},
            {"intent": "Submit invoice to ETA", "parameters": {}, "context": {}},
            {"intent": "Search for customers", "parameters": {}, "context": {}},
        ]

        results = []
        for req in requests:
            result = await engine.reason(self.session_id, req)
            results.append(result)

        assert len(results) == 3
        assert results[0]["chosen_path"] == "shipping"
        assert results[1]["chosen_path"] == "eta"
        assert results[2]["chosen_path"] == "search"

    @pytest.mark.asyncio
    async def test_dem_llm_does_not_break_existing_paths(self):
        """LLM integration does not alter existing deterministic path selection."""
        registry = LLMProviderRegistry()
        provider = GeminiProvider(api_key="test-key")
        provider.generate = AsyncMock(return_value=MagicMock(content="unknown"))
        registry.register(provider)

        engine = ReasoningEngine(llm_registry=registry)

        test_cases = [
            ("Ship my package to Germany", "shipping", {"destination": "Germany"}),
            ("Submit invoice to ETA", "eta", {}),
            ("File customs declaration", "customs", {}),
            ("Search for customers", "search", {}),
            ("Show dashboard statistics", "dashboard", {"view": "summary"}),
            ("Send notification to user", "notification", {"user_id": 1}),
            ("Transition workflow to next step", "workflow", {"workflow_id": "wf-123"}),
        ]

        for intent, expected_path, params in test_cases:
            request = {
                "intent": intent,
                "parameters": params,
                "context": {},
            }
            result = await engine.reason(self.session_id, request)
            assert result["chosen_path"] == expected_path, f"Failed for intent: {intent}"
