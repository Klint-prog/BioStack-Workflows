"""CLI command for initializing BioStack projects."""

from __future__ import annotations

import typer
from rich.console import Console

from biostack.core.project import (
    ProjectCreationError,
    create_project,
)

console = Console()


def init_project_command(
    name: str = typer.Argument(..., help="Nome do diretório do projeto BioStack a criar."),
    template: str = typer.Option(
        "rnaseq-basic",
        "--template",
        "-t",
        help="Template inicial do projeto.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Recria o diretório do projeto se ele já existir.",
    ),
) -> None:
    """Cria um novo projeto BioStack a partir de um template validado."""
    try:
        created = create_project(name=name, template=template, force=force)
    except ProjectCreationError as exc:
        console.print(f"[red]Erro:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Projeto BioStack criado:[/green] {created.path}")
    console.print(f"Template: {created.config.project.template}")
    console.print("Configuração validada: biostack.yml")
