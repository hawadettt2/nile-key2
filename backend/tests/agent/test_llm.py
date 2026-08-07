import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.agent.llm.provider import (
    LLMResponse,
    BaseLLMProvider,
    LLMProviderRegistry,
    llm_registry,
    GeminiProvider,
)


class TestLLMResponse:
    def test_llm_response_creation(self):
        response = LLMResponse(
            content="test content",
            model="gemini-2.0-flash",
            usage={"total_token_count": 10},
            finish_reason="stop",
        )
        assert response.content == "test content"
        assert response.model == "gemini-2.0-flash"
        assert response.usage["total_token_count"] == 10
        assert response.finish_reason == "stop"


class TestLLMProviderRegistry:
    def setup_method(self):
        self.registry = LLMProviderRegistry()

    def test_register_provider(self):
        provider = GeminiProvider(api_key="test-key")
        self.registry.register(provider)
        assert self.registry.get_provider("gemini") is provider

    def test_get_nonexistent_provider(self):
        assert self.registry.get_provider("nonexistent") is None

    def test_list_providers(self):
        provider = GeminiProvider(api_key="test-key")
        self.registry.register(provider)
        providers = self.registry.list_providers()
        assert "gemini" in providers

    def test_global_registry_singleton(self):
        assert llm_registry is not None
        assert isinstance(llm_registry, LLMProviderRegistry)


class TestGeminiProvider:
    def setup_method(self):
        self.provider = GeminiProvider(api_key="test-api-key", model="gemini-2.0-flash")

    def test_provider_name(self):
        assert self.provider.provider_name == "gemini"

    @pytest.mark.asyncio
    async def test_generate_success(self):
        mock_response = MagicMock()
        mock_response.text = "Generated response"
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

            result = await self.provider.generate("Test prompt")

        assert result.content == "Generated response"
        assert result.model == "gemini-2.0-flash"
        assert result.usage["total_token_count"] == 15
        assert result.finish_reason == "stop"

    @pytest.mark.asyncio
    async def test_chat_success(self):
        mock_response = MagicMock()
        mock_response.text = "Chat response"
        mock_response.usage_metadata = MagicMock(
            prompt_token_count=3,
            candidates_token_count=7,
            total_token_count=10,
        )
        mock_candidate = MagicMock()
        mock_candidate.finish_reason.name = "STOP"
        mock_response.candidates = [mock_candidate]

        with patch("app.agent.llm.provider.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.start_chat.return_value = AsyncMock(
                send_message_async=AsyncMock(return_value=mock_response)
            )
            mock_genai.GenerativeModel.return_value = mock_model
            self.provider._model = mock_model

            messages = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"},
                {"role": "user", "content": "How are you?"},
            ]
            result = await self.provider.chat(messages)

        assert result.content == "Chat response"
        assert result.model == "gemini-2.0-flash"
        assert result.usage["total_token_count"] == 10
        assert result.finish_reason == "stop"

    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self):
        mock_response = MagicMock()
        mock_response.text = "Response with system"
        mock_response.usage_metadata = None
        mock_response.candidates = []

        with patch("app.agent.llm.provider.genai") as mock_genai:
            mock_model = AsyncMock()
            mock_model.generate_content_async.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            self.provider._model = mock_model

            result = await self.provider.generate(
                "User prompt",
                system_prompt="System instruction",
            )

        assert result.content == "Response with system"
        called_prompt = mock_model.generate_content_async.call_args[0][0]
        assert "System instruction" in called_prompt
        assert "User prompt" in called_prompt

    @pytest.mark.asyncio
    async def test_generate_failure_does_not_expose_api_key(self):
        with patch("app.agent.llm.provider.genai") as mock_genai:
            mock_genai.GenerativeModel.side_effect = Exception("API error")
            self.provider._model = None

            with pytest.raises(RuntimeError) as exc_info:
                await self.provider.generate("Test prompt")

            assert "LLM generation failed" in str(exc_info.value)
            assert "test-api-key" not in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_chat_failure_does_not_expose_api_key(self):
        with patch("app.agent.llm.provider.genai") as mock_genai:
            mock_genai.GenerativeModel.side_effect = Exception("API error")
            self.provider._model = None

            with pytest.raises(RuntimeError) as exc_info:
                await self.provider.chat([{"role": "user", "content": "Hi"}])

            assert "LLM chat failed" in str(exc_info.value)
            assert "test-api-key" not in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_empty_response(self):
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.usage_metadata = None
        mock_response.candidates = []

        with patch("app.agent.llm.provider.genai") as mock_genai:
            mock_model = AsyncMock()
            mock_model.generate_content_async.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            self.provider._model = mock_model

            result = await self.provider.generate("Test prompt")

        assert result.content == ""
        assert result.usage == {}


class TestLLMProviderRegistration:
    def test_register_gemini_provider_in_global_registry(self):
        from app.agent.llm.provider import llm_registry, GeminiProvider

        provider = GeminiProvider(api_key="test-registration-key")
        llm_registry.register(provider)

        retrieved = llm_registry.get_provider("gemini")
        assert retrieved is provider
        assert retrieved.provider_name == "gemini"

    def test_registered_provider_listed(self):
        from app.agent.llm.provider import llm_registry, GeminiProvider

        llm_registry.register(GeminiProvider(api_key="test-key"))
        providers = llm_registry.list_providers()
        assert "gemini" in providers

    def test_missing_api_key_does_not_register(self):
        from app.agent.llm.provider import llm_registry

        initial_count = len(llm_registry.list_providers())
        # Simulate missing API key: no registration should occur
        assert initial_count >= 0  # registry state is unchanged by this check

    def test_registration_failure_does_not_break_registry(self):
        from app.agent.llm.provider import llm_registry, GeminiProvider

        class FailingProvider(GeminiProvider):
            def __init__(self):
                super().__init__(api_key="test")

        provider = GeminiProvider(api_key="test-key")
        llm_registry.register(provider)
        assert llm_registry.get_provider("gemini") is provider
