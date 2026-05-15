"""CLI command for running BioStack workflows."""

from __future__ import annotations

import typer
from rich.console import Console

from biostack.core.runner import RunnerError, run_workflow

console = Console()


def run_project_command(
    workflow: str | None = typer.Option(
        None,
        "--workflow",
        "-w",
        help="Nome do workflow a executar. Se omitido, usa biostack.yml.",
    ),
    profile: str | None = typer.Option(
        None,
        "--profile",
        "-p",
        help="Profile Nextflow a usar. Se omitido, usa biostack.yml.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Mostra o comando Nextflow e registra log sem executar.",
    ),
) -> None:
    """Executa ou simula um workflow BioStack via Nextflow."""
    try:
        result = run_workflow(workflow=workflow, profile=profile, dry_run=dry_run)
    except RunnerError as exc:
        console.print(f"[red]Erro:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Run ID:[/green] {result.run_id}")
    console.print(f"Workflow: {result.workflow_name}")
    console.print(f"Profile: {result.profile}")
    console.print(f"Log: {result.log_path}")

    if dry_run:
        console.print("[yellow]Dry-run:[/yellow] comando Nextflow não executado.")
        console.print(result.command_text)
        return

    console.print("[green]Workflow concluído com sucesso.[/green]")
