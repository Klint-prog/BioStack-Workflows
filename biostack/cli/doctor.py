"""Environment diagnostics for BioStack Workflows."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from biostack.core.system import collect_environment_diagnostics

console = Console()
doctor_app = typer.Typer(
    help="Verifica dependências locais usadas pelo BioStack Workflows.",
    invoke_without_command=True,
)


@doctor_app.callback()
def doctor() -> None:
    """Executa diagnóstico tolerante do ambiente local."""
    diagnostics = collect_environment_diagnostics()

    table = Table(title="BioStack environment doctor")
    table.add_column("Item", style="bold")
    table.add_column("Status")
    table.add_column("Detalhes")

    for check in diagnostics:
        status_label = "OK" if check.available else "AUSENTE"
        table.add_row(check.name, status_label, check.details)

    console.print(table)
