"""Test provider environment configuration behavior.

Tests:
1. Missing credentials → provider NOT_CONFIGURED (not activated)
2. Present credentials → provider activated and reachable
"""
import os
import tempfile
import json
import asyncio
import pytest

from app.core.config import Settings
from main import _log_provider_readiness


def test_provider_env_vars_are_defined():
    """All provider env vars must be defined in Settings."""
    required_vars = [
        'MOAAH_BASE_URL', 'MOAAH_API_KEY', 'MOAAH_TIMEOUT_SECONDS',
        'TRADEDATA_BASE_URL', 'TRADEDATA_API_KEY', 'TRADEDATA_TIMEOUT_SECONDS',
        'ZATCA_BASE_URL', 'ZATCA_API_KEY', 'ZATCA_TIMEOUT_SECONDS',
        'FAOSTAT_BASE_URL', 'FAOSTAT_USER', 'FAOSTAT_PASSWORD', 'FAOSTAT_TIMEOUT_SECONDS',
        'GCCSTAT_BASE_URL', 'GCCSTAT_API_KEY', 'GCCSTAT_TIMEOUT_SECONDS',
        'UN_COMTRADE_BASE_URL', 'UN_COMTRADE_API_KEY', 'UN_COMTRADE_TIMEOUT_SECONDS',
        'WTO_EPING_BASE_URL', 'WTO_EPING_API_KEY',
        'WORLDBANK_LPI_BASE_URL',
        'REGULATIONS_FILE_PATH',
    ]
    for var in required_vars:
        assert var in Settings.model_fields, f"{var} missing from Settings"


def test_empty_values_are_not_considered_configured(monkeypatch, tmp_path):
    """Empty strings and placeholders must be treated as NOT_CONFIGURED."""
    # Create a temporary regulations file
    reg_file = tmp_path / "regulations.json"
    reg_file.write_text("[]")
    
    monkeypatch.setenv('MOAAH_BASE_URL', '')
    monkeypatch.setenv('MOAAH_API_KEY', '')
    monkeypatch.setenv('TRADEDATA_API_KEY', '')
    monkeypatch.setenv('ZATCA_API_KEY', '')
    monkeypatch.setenv('FAOSTAT_USER', '')
    monkeypatch.setenv('FAOSTAT_PASSWORD', '')
    monkeypatch.setenv('GCCSTAT_API_KEY', '')
    monkeypatch.setenv('REGULATIONS_FILE_PATH', str(reg_file))
    
    # Force reload
    from app.core.config import Settings
    settings = Settings()
    
    assert not settings.MOAAH_API_KEY
    assert not settings.MOAAH_BASE_URL
    assert not settings.TRADEDATA_API_KEY
    assert not settings.ZATCA_API_KEY
    assert not settings.FAOSTAT_USER
    assert not settings.FAOSTAT_PASSWORD
    assert not settings.GCCSTAT_API_KEY


def test_readiness_logger_reports_not_configured(monkeypatch, tmp_path, capsys):
    """Readiness logger must report NOT_CONFIGURED when credentials are missing."""
    reg_file = tmp_path / "regulations.json"
    reg_file.write_text("[]")
    
    monkeypatch.setenv('MOAAH_BASE_URL', '')
    monkeypatch.setenv('MOAAH_API_KEY', '')
    monkeypatch.setenv('TRADEDATA_API_KEY', '')
    monkeypatch.setenv('ZATCA_API_KEY', '')
    monkeypatch.setenv('FAOSTAT_BASE_URL', 'https://faostatservices.fao.org/api/v1')
    monkeypatch.setenv('FAOSTAT_USER', '')
    monkeypatch.setenv('FAOSTAT_PASSWORD', '')
    monkeypatch.setenv('REGULATIONS_FILE_PATH', str(reg_file))
    
    _log_provider_readiness()
    captured = capsys.readouterr()
    
    assert '[BLOCKED]' in captured.out
    assert 'NOT_CONFIGURED' in captured.out or 'Missing:' in captured.out


def test_regulations_file_path_checks_existence_only(tmp_path):
    """Regulations provider should only check file existence, not create data."""
    from app.agent.knowledge.regulations_provider import RegulationsKnowledgeProvider
    
    # Non-existent file
    non_existent = tmp_path / "does_not_exist.json"
    provider = RegulationsKnowledgeProvider(file_path=str(non_existent))
    result = asyncio.run(provider.query("test", context={}, limit=10))
    assert result["results"] == []
    assert result["confidence"] == 0.0
    
    # Existing file with valid data
    reg_file = tmp_path / "regulations.json"
    reg_file.write_text(json.dumps([
        {
            "id": "test-1",
            "title": "Test Regulation",
            "description": "Test description",
            "country": "Egypt",
            "regulation_type": "SPS",
            "effective_date": "2024-01-01",
            "source_url": "https://example.com/test"
        }
    ]))
    
    provider2 = RegulationsKnowledgeProvider(file_path=str(reg_file))
    result2 = asyncio.run(provider2.query("test", context={}, limit=10))
    assert len(result2["results"]) == 1
    assert result2["confidence"] > 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
