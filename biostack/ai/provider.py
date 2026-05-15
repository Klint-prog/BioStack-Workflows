"""LLM provider abstractions for operational troubleshooting."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod


class ProviderConfigurationError(RuntimeError):
    """Raised when an LLM provider is not configured for use."""


class LLMProvider(ABC):
    """Abstract interface implemented by troubleshooting LLM providers."""

    @abstractmethod
    def explain(self, prompt: str) -> str:
        """Return a technical troubleshooting explanation for the provided prompt."""


class FakeTroubleshootingProvider(LLMProvider):
    """Deterministic provider used by tests and local dry checks."""

    def explain(self, prompt: str) -> str:
        """Return a stable fake explanation without external network calls."""
        lower_prompt = prompt.lower()
        findings: list[str] = []
        if "failed" in lower_prompt or "erro" in lower_prompt or "error" in lower_prompt:
            findings.append("Há indícios de falha operacional nos logs ou metadados.")
        if "nextflow" in lower_prompt:
            findings.append("Verifique disponibilidade do Nextflow, profile usado e paths do workflow.")
        if "dry_run=true" in lower_prompt:
            findings.append("A execução foi simulada; valide o comando antes de rodar em modo real.")
        if not findings:
            findings.append("Nenhum erro operacional evidente foi identificado no resumo recebido.")

        return "\n".join(
            [
                "Resumo operacional gerado por provider fake.",
                "Possível causa: revisão técnica dos logs e metadados do run é necessária.",
                "Próximos passos:",
                *[f"- {finding}" for finding in findings],
                "- Conferir arquivos em logs/ e reports/ antes de repetir a execução.",
            ]
        )


class EnvironmentLLMProvider(LLMProvider):
    """Placeholder provider gated by an environment API key.

    The MVP deliberately avoids binding to a concrete paid API client. This class
    proves the configuration boundary and fails safely when no key is present.
    A real provider can be added later without changing the CLI contract.
    """

    def __init__(self, api_key_env: str = "BIOSTACK_LLM_API_KEY") -> None:
        self.api_key_env = api_key_env
        self.api_key = os.getenv(api_key_env)
        if not self.api_key:
            raise ProviderConfigurationError(
                f"Provider de IA não configurado. Defina {api_key_env} ou use --provider mock."
            )

    def explain(self, prompt: str) -> str:
        """Fail explicitly until a real provider implementation is configured."""
        raise ProviderConfigurationError(
            "Provider real de IA ainda não foi implementado no MVP. Use --provider mock "
            "para troubleshooting local determinístico."
        )


def get_provider(name: str) -> LLMProvider:
    """Resolve a provider by CLI name."""
    normalized = name.strip().lower()
    if normalized in {"mock", "fake"}:
        return FakeTroubleshootingProvider()
    if normalized in {"env", "default", "llm"}:
        return EnvironmentLLMProvider()
    raise ProviderConfigurationError(
        f"Provider de IA desconhecido: '{name}'. Providers disponíveis: mock, env."
    )
