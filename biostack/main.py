"""Main Typer application for the BioStack Workflows CLI."""

from __future__ import annotations

import typer
from rich.console import Console

from biostack import __version__
from biostack.cli.doctor import doctor_app
from biostack.cli.init import init_project_command

app = typer.Typer(
    name="biostack",
    help="BioStack Workflows: CLI para workflows de bioinformática reprodutíveis.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def version() -> None:
    """Exibe a versão instalada do BioStack Workflows."""
    console.print(__version__)


app.command(name="init")(init_project_command)
app.add_typer(doctor_app, name="doctor")


if __name__ == "__main__":
    app()
