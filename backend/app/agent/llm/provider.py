from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)


class LLMResponse(BaseModel):
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


class BaseLLMProvider:
    provider_name: str = "base"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None) -> LLMResponse:
        raise NotImplementedError("BaseLLMProvider.generate() is not implemented in Phase 1.")

    async def chat(self, messages: List[Dict[str, str]], parameters: Optional[Dict[str, Any]] = None) -> LLMResponse:
        raise NotImplementedError("BaseLLMProvider.chat() is not implemented in Phase 1.")


class LLMProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, BaseLLMProvider] = {}

    def register(self, provider: BaseLLMProvider) -> None:
        self._providers[provider.provider_name] = provider

    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        return self._providers.get(name)

    def list_providers(self) -> List[str]:
        return list(self._providers.keys())


llm_registry = LLMProviderRegistry()


class GeminiProvider(BaseLLMProvider):
    provider_name: str = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self._api_key = api_key
        self._model_name = model
        self._model = None

    def _get_client(self):
        if self._model is None:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            self._model = genai.GenerativeModel(self._model_name)
        return self._model

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None) -> LLMResponse:
        try:
            model = self._get_client()
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            response = await model.generate_content_async(
                full_prompt,
                generation_config=parameters or {}
            )

            usage = {}
            if response.usage_metadata:
                usage = {
                    "prompt_token_count": response.usage_metadata.prompt_token_count or 0,
                    "candidates_token_count": response.usage_metadata.candidates_token_count or 0,
                    "total_token_count": response.usage_metadata.total_token_count or 0,
                }

            finish_reason = "stop"
            if response.candidates and response.candidates[0].finish_reason:
                finish_reason = response.candidates[0].finish_reason.name.lower()

            return LLMResponse(
                content=response.text or "",
                model=self._model_name,
                usage=usage,
                finish_reason=finish_reason,
            )
        except Exception as exc:
            logger.error("GeminiProvider.generate failed: %s", exc)
            raise RuntimeError("LLM generation failed") from exc

    async def chat(self, messages: List[Dict[str, str]], parameters: Optional[Dict[str, Any]] = None) -> LLMResponse:
        try:
            model = self._get_client()

            gemini_history = []
            system_instruction = None
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    system_instruction = content
                elif role == "user":
                    gemini_history.append({"role": "user", "parts": [content]})
                elif role == "assistant":
                    gemini_history.append({"role": "model", "parts": [content]})

            if system_instruction:
                model = model.with_system_instruction(system_instruction)

            chat = model.start_chat(history=gemini_history[:-1] if gemini_history else [])
            last_message = gemini_history[-1]["parts"][0] if gemini_history else ""

            response = await chat.send_message_async(
                last_message,
                generation_config=parameters or {}
            )

            usage = {}
            if response.usage_metadata:
                usage = {
                    "prompt_token_count": response.usage_metadata.prompt_token_count or 0,
                    "candidates_token_count": response.usage_metadata.candidates_token_count or 0,
                    "total_token_count": response.usage_metadata.total_token_count or 0,
                }

            finish_reason = "stop"
            if response.candidates and response.candidates[0].finish_reason:
                finish_reason = response.candidates[0].finish_reason.name.lower()

            return LLMResponse(
                content=response.text or "",
                model=self._model_name,
                usage=usage,
                finish_reason=finish_reason,
            )
        except Exception as exc:
            logger.error("GeminiProvider.chat failed: %s", exc)
            raise RuntimeError("LLM chat failed") from exc
