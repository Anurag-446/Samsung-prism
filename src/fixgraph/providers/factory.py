"""LLM Provider Factory to instantiate configured LLM provider."""

from fixgraph.config import Settings
from fixgraph.providers.base import LLMProvider
from fixgraph.providers.exceptions import ProviderError
from fixgraph.providers.live import LiveLLMProvider
from fixgraph.providers.mock import MockLLMProvider


def create_llm_provider(settings: Settings) -> LLMProvider:
    provider_name = settings.llm_provider.lower()
    if provider_name == "mock":
        return MockLLMProvider()
    elif provider_name == "gemma_local":
        from fixgraph.providers.gemma import GemmaLocalProvider
        return GemmaLocalProvider(model_name=settings.llm_model_name)
    elif provider_name in ["openai", "azure"]:
        if not settings.llm_api_key:
            raise ProviderError(f"API key is required for {provider_name} provider")
        return LiveLLMProvider(
            api_key=settings.llm_api_key,
            model_name=settings.llm_model_name,
            temperature=settings.llm_temperature,
            timeout=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
        )
    else:
        raise ProviderError(f"Unsupported provider: {provider_name}")
