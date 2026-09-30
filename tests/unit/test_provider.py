"""Unit tests for LLM provider abstraction and factory."""
import os

import pytest

from fixgraph.config import Settings
from fixgraph.providers.exceptions import ProviderError
from fixgraph.providers.factory import create_llm_provider
from fixgraph.providers.live import LiveLLMProvider
from fixgraph.providers.mock import MockLLMProvider


def test_mock_provider_selected():
    settings = Settings(llm_provider="mock")
    provider = create_llm_provider(settings)
    assert isinstance(provider, MockLLMProvider)
    assert provider.provider_id == "mock"

def test_live_provider_selected():
    # Must use env="production" to bypass test-mode mock override
    settings = Settings(llm_provider="openai", llm_api_key="test-key", env="production")
    provider = create_llm_provider(settings)
    assert isinstance(provider, LiveLLMProvider)
    assert provider.provider_id == "openai"
    assert provider.api_key == "test-key"

def test_live_provider_missing_key():
    # Must use env="production" to bypass test-mode mock override
    settings = Settings(llm_provider="openai", llm_api_key="", env="production")
    with pytest.raises(ProviderError) as excinfo:
        create_llm_provider(settings)
    assert "API key is required" in str(excinfo.value)

def test_invalid_provider_fails():
    # Must use env="production" to bypass test-mode mock override
    settings = Settings(llm_provider="unknown", env="production")
    with pytest.raises(ProviderError):
        create_llm_provider(settings)

@pytest.mark.skipif(not os.environ.get("RUN_LIVE_LLM_TESTS"), reason="Opt-in only")
def test_live_provider_network_call():
    # Only runs if RUN_LIVE_LLM_TESTS=1
    pass
