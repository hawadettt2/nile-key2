from typing import Optional, Dict, Any, List
from pydantic import BaseModel


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
