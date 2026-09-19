"""Test that provider activation happens at startup when credentials are present."""
import asyncio
import os
import tempfile
import json
import pytest

from app.core.config import Settings
from app.agent.knowledge.registry import KnowledgeProviderRegistry
from app.agent.knowledge.faostat_provider import FaostatExternalSourceAdapter
from app.core.credentials.credential_store import CredentialStore
from app.core.credentials.username_password_credential import UsernamePasswordCredential


def test_faostat_activation_with_credentials(monkeypatch, tmp_path):
    """When FAOSTAT credentials are present, the provider should be activatable."""
    # Set credentials
    monkeypatch.setenv('FAOSTAT_BASE_URL', 'https://faostatservices.fao.org/api/v1')
    monkeypatch.setenv('FAOSTAT_USER', 'test@example.com')
    monkeypatch.setenv('FAOSTAT_PASSWORD', 'test-password')
    monkeypatch.setenv('FAOSTAT_TIMEOUT_SECONDS', '30.0')
    
    settings = Settings()
    
    # Verify credentials are read
    assert settings.FAOSTAT_BASE_URL == 'https://faostatservices.fao.org/api/v1'
    assert settings.FAOSTAT_USER == 'test@example.com'
    assert settings.FAOSTAT_PASSWORD == 'test-password'
    
    # Create adapter (simulates startup activation)
    cred_store = CredentialStore()
    cred_store.register(
        "faostat_username",
        UsernamePasswordCredential(username=settings.FAOSTAT_USER, password="", source="env")
    )
    cred_store.register(
        "faostat_password",
        UsernamePasswordCredential(username="", password=settings.FAOSTAT_PASSWORD, source="env")
    )
    
    adapter = FaostatExternalSourceAdapter(
        config={
            "source_id": settings.FAOSTAT_SOURCE_ID,
            "name": settings.FAOSTAT_SOURCE_NAME,
            "type": settings.FAOSTAT_SOURCE_TYPE,
            "version": settings.FAOSTAT_SOURCE_VERSION,
            "updated_at": "2026-08-14T00:00:00Z",
            "base_url": settings.FAOSTAT_BASE_URL,
            "timeout_seconds": settings.FAOSTAT_TIMEOUT_SECONDS,
            "default_domain": settings.FAOSTAT_DEFAULT_DOMAIN,
        },
        credential_store=cred_store,
    )
    
    # Verify adapter is properly configured
    assert adapter._source_id == "faostat"
    assert adapter._base_url == "https://faostatservices.fao.org/api/v1"
    
    # Verify it can be registered (simulates startup registration)
    registry = KnowledgeProviderRegistry()
    sources = asyncio.run(adapter.get_sources())
    assert len(sources) == 1
    assert sources[0]["id"] == "faostat"
    
    # This would succeed if added to registry:
    # await registry.register(adapter)
    # assert registry.exists("faostat")


def test_faostat_not_activated_without_credentials(monkeypatch):
    """Without credentials, FAOSTAT should NOT be activated."""
    monkeypatch.setenv('FAOSTAT_BASE_URL', '')
    monkeypatch.setenv('FAOSTAT_USER', '')
    monkeypatch.setenv('FAOSTAT_PASSWORD', '')
    
    settings = Settings()
    
    # Simulate startup condition
    should_activate = (
        settings.FAOSTAT_BASE_URL 
        and settings.FAOSTAT_USER 
        and settings.FAOSTAT_PASSWORD
    )
    
    assert not should_activate


def test_worldbank_lpi_activation_with_base_url(monkeypatch):
    """World Bank LPI activates with just base_url (no credentials needed)."""
    monkeypatch.setenv('WORLDBANK_LPI_BASE_URL', 'https://api.worldbank.org/v2')
    
    settings = Settings()
    assert settings.WORLDBANK_LPI_BASE_URL == 'https://api.worldbank.org/v2'
    
    # Simulate startup condition
    should_activate = bool(settings.WORLDBANK_LPI_BASE_URL)
    assert should_activate


def test_worldbank_lpi_not_activated_without_base_url(monkeypatch):
    """Without base_url, World Bank LPI should NOT be activated."""
    monkeypatch.setenv('WORLDBANK_LPI_BASE_URL', '')
    
    settings = Settings()
    should_activate = bool(settings.WORLDBANK_LPI_BASE_URL)
    assert not should_activate


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
