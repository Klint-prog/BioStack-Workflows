"""CLI command for generating or reopening BioStack run reports."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from biostack.core.config import load_project_config
from biostack.core.runner import ProjectConfigNotFoundError, find_project_config
from biostack.reports.generator import ReportNotFoundError, regenerate_html_for_run

console = Console()


def report_command(
    run: str = typer.Option(
        "latest",
        "--run",
        "-r",
        help="Run ID a renderizar ou 'latest' para a execução mais recente.",
    ),
) -> None:
    """Gera novamente o HTML legível de um relatório salvo em JSON."""
    project_dir = Path.cwd().resolve()
    try:
        config_path = find_project_config(project_dir)
        config = load_project_config(config_path)
        metadata, html_path = regenerate_html_for_run(
            project_dir=project_dir,
            run=run,
            reports_dir=config.storage.reports,
        )
    except (ProjectConfigNotFoundError, ReportNotFoundError) as exc:
        console.print(f"[red]Erro:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Relatório HTML gerado:[/green] {html_path}")
    console.print(f"Run ID: {metadata.run_id}")
    console.print(f"Status: {metadata.status}")
