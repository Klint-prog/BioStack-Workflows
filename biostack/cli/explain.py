"""CLI command for AI-assisted operational troubleshooting."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from biostack.ai.prompts import CLINICAL_WARNING, build_troubleshooting_prompt
from biostack.ai.provider import ProviderConfigurationError, get_provider
from biostack.core.config import load_project_config
from biostack.core.runner import ProjectConfigNotFoundError, find_project_config
from biostack.reports.generator import (
    ReportNotFoundError,
    load_metadata_report,
    resolve_report_json,
)

console = Console()
MAX_LOG_CHARS = 12_000


def _read_run_context(project_dir: Path, run: str) -> tuple[str, str, str]:
    """Return run id, metadata JSON and bounded log text for troubleshooting."""
    config_path = find_project_config(project_dir)
    config = load_project_config(config_path)
    report_path = resolve_report_json(
        project_dir=project_dir,
        run=run,
        reports_dir=config.storage.reports,
    )
    metadata = load_metadata_report(report_path)
    metadata_json = json.dumps(metadata.model_dump(mode="json"), indent=2, ensure_ascii=False)

    log_path = project_dir / metadata.log_path
    if log_path.is_file():
        log_text = log_path.read_text(encoding="utf-8", errors="replace")[-MAX_LOG_CHARS:]
    else:
        log_text = f"Log não encontrado no caminho registrado: {metadata.log_path}"

    return metadata.run_id, metadata_json, log_text


def explain_command(
    run: str = typer.Option(
        "latest",
        "--run",
        "-r",
        help="Run ID a explicar ou 'latest' para a execução mais recente.",
    ),
    provider: str = typer.Option(
        "env",
        "--provider",
        help="Provider de IA: 'env' exige BIOSTACK_LLM_API_KEY; 'mock' usa resposta fake.",
    ),
) -> None:
    """Explica logs e metadados de um run com escopo estritamente operacional."""
    project_dir = Path.cwd().resolve()
    console.print(f"[bold yellow]{CLINICAL_WARNING}[/bold yellow]")

    try:
        run_id, metadata_json, log_text = _read_run_context(project_dir, run)
        llm_provider = get_provider(provider)
        prompt = build_troubleshooting_prompt(metadata_json=metadata_json, log_text=log_text)
        explanation = llm_provider.explain(prompt)
    except (ProjectConfigNotFoundError, ReportNotFoundError, ProviderConfigurationError) as exc:
        console.print(f"[red]Erro:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Run analisado:[/green] {run_id}")
    console.print(Panel(explanation, title="IA operacional — troubleshooting", expand=False))
