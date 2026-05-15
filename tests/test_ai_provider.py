import pytest

from biostack.ai.prompts import CLINICAL_WARNING, build_troubleshooting_prompt
from biostack.ai.provider import (
    FakeTroubleshootingProvider,
    ProviderConfigurationError,
    get_provider,
)


def test_fake_provider_returns_deterministic_operational_summary() -> None:
    provider = FakeTroubleshootingProvider()

    response = provider.explain("status=FAILED\nNextflow retornou erro\ndry_run=True")

    assert "provider fake" in response
    assert "Nextflow" in response
    assert "Dry-run" in response or "simulada" in response


def test_get_provider_resolves_mock_without_environment_key() -> None:
    provider = get_provider("mock")

    assert isinstance(provider, FakeTroubleshootingProvider)


def test_unknown_provider_fails_with_clear_message() -> None:
    with pytest.raises(ProviderConfigurationError, match="Provider de IA desconhecido"):
        get_provider("missing")


def test_env_provider_requires_api_key(monkeypatch) -> None:
    monkeypatch.delenv("BIOSTACK_LLM_API_KEY", raising=False)

    with pytest.raises(ProviderConfigurationError, match="BIOSTACK_LLM_API_KEY"):
        get_provider("env")


def test_prompt_contains_scope_limits_and_clinical_warning() -> None:
    prompt = build_troubleshooting_prompt(metadata_json='{"status":"FAILED"}', log_text="erro")

    assert CLINICAL_WARNING in prompt
    assert "Fora do escopo" in prompt
    assert "interpretar resultados biológicos" in prompt
    assert "Metadados do run" in prompt
    assert "Logs do run" in prompt
