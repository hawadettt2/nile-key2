import pytest
import time
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from app.agent.llm.provider import LLMProviderRegistry, GeminiProvider


class TestLLMPerformance:
    """Performance tests for LLM provider per DR-004 (Phase 4)."""

    def setup_method(self):
        self.provider = GeminiProvider(api_key="test-key", model="gemini-2.0-flash")

    @pytest.mark.asyncio
    async def test_generate_latency_under_threshold(self):
        """Verify generate() latency is within acceptable bounds."""
        mock_response = MagicMock()
        mock_response.text = "Performance test response"
        mock_response.usage_metadata = MagicMock(
            prompt_token_count=10,
            candidates_token_count=20,
            total_token_count=30,
        )
        mock_candidate = MagicMock()
        mock_candidate.finish_reason.name = "STOP"
        mock_response.candidates = [mock_candidate]

        with patch("app.agent.llm.provider.genai") as mock_genai:
            mock_model = AsyncMock()
            mock_model.generate_content_async.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            self.provider._model = mock_model

            start = time.perf_counter()
            result = await self.provider.generate("Test prompt for latency")
            elapsed_ms = (time.perf_counter() - start) * 1000

        assert result.content == "Performance test response"
        assert elapsed_ms < 5000, f"generate() latency {elapsed_ms:.1f}ms exceeds 5000ms threshold"

    @pytest.mark.asyncio
    async def test_chat_latency_under_threshold(self):
        """Verify chat() latency is within acceptable bounds."""
        mock_response = MagicMock()
        mock_response.text = "Chat performance response"
        mock_response.usage_metadata = MagicMock(
            prompt_token_count=5,
            candidates_token_count=15,
            total_token_count=20,
        )
        mock_candidate = MagicMock()
        mock_candidate.finish_reason.name = "STOP"
        mock_response.candidates = [mock_candidate]

        with patch("app.agent.llm.provider.genai") as mock_genai:
            mock_model = MagicMock()
            mock_chat = AsyncMock()
            mock_chat.send_message_async.return_value = mock_response
            mock_model.start_chat.return_value = mock_chat
            mock_genai.GenerativeModel.return_value = mock_model
            self.provider._model = mock_model

            messages = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi"},
                {"role": "user", "content": "How are you?"},
            ]

            start = time.perf_counter()
            result = await self.provider.chat(messages)
            elapsed_ms = (time.perf_counter() - start) * 1000

        assert result.content == "Chat performance response"
        assert elapsed_ms < 5000, f"chat() latency {elapsed_ms:.1f}ms exceeds 5000ms threshold"

    @pytest.mark.asyncio
    async def test_generate_throughput(self):
        """Verify generate() can handle multiple sequential requests."""
        mock_response = MagicMock()
        mock_response.text = "Throughput response"
        mock_response.usage_metadata = MagicMock(
            prompt_token_count=5,
            candidates_token_count=10,
            total_token_count=15,
        )
        mock_candidate = MagicMock()
        mock_candidate.finish_reason.name = "STOP"
        mock_response.candidates = [mock_candidate]

        with patch("app.agent.llm.provider.genai") as mock_genai:
            mock_model = AsyncMock()
            mock_model.generate_content_async.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            self.provider._model = mock_model

            start = time.perf_counter()
            tasks = [self.provider.generate(f"Prompt {i}") for i in range(10)]
            results = await asyncio.gather(*tasks)
            elapsed_ms = (time.perf_counter() - start) * 1000

        assert len(results) == 10
        for r in results:
            assert r.content == "Throughput response"
        assert elapsed_ms < 10000, f"10 sequential requests took {elapsed_ms:.1f}ms"

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Verify provider handles slow responses gracefully."""
        with patch("app.agent.llm.provider.genai") as mock_genai:
            mock_model = AsyncMock()
            
            async def slow_response(*args, **kwargs):
                await asyncio.sleep(0.1)
                raise TimeoutError("Request timed out")
            
            mock_model.generate_content_async = slow_response
            mock_genai.GenerativeModel.return_value = mock_model
            self.provider._model = mock_model

            with pytest.raises(RuntimeError) as exc_info:
                await self.provider.generate("Slow prompt")
            
            assert "LLM generation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_concurrent_requests_do_not_degrade(self):
        """Verify concurrent requests maintain performance."""
        mock_response = MagicMock()
        mock_response.text = "Concurrent response"
        mock_response.usage_metadata = MagicMock(
            prompt_token_count=5,
            candidates_token_count=10,
            total_token_count=15,
        )
        mock_candidate = MagicMock()
        mock_candidate.finish_reason.name = "STOP"
        mock_response.candidates = [mock_candidate]

        with patch("app.agent.llm.provider.genai") as mock_genai:
            mock_model = AsyncMock()
            mock_model.generate_content_async.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            self.provider._model = mock_model

            start = time.perf_counter()
            tasks = [self.provider.generate(f"Concurrent prompt {i}") for i in range(5)]
            results = await asyncio.gather(*tasks)
            elapsed_ms = (time.perf_counter() - start) * 1000

        assert len(results) == 5
        for r in results:
            assert r.content == "Concurrent response"
        assert elapsed_ms < 8000, f"5 concurrent requests took {elapsed_ms:.1f}ms"

    @pytest.mark.asyncio
    async def test_error_handling_does_not_expose_sensitive_data(self):
        """Verify error handling does not expose API keys or sensitive data."""
        with patch("app.agent.llm.provider.genai") as mock_genai:
            mock_genai.GenerativeModel.side_effect = Exception("Authentication failed")
            self.provider._model = None

            with pytest.raises(RuntimeError) as exc_info:
                await self.provider.generate("Test prompt")
            
            error_str = str(exc_info.value)
            assert "test-key" not in error_str
            assert "api_key" not in error_str.lower()
            assert "LLM generation failed" in error_str
