"""CLI command for launching the optional local web UI."""

from __future__ import annotations

import typer
from rich.console import Console

console = Console()


def web_command(
    host: str = typer.Option("127.0.0.1", "--host", help="Endereço local para o servidor web."),
    port: int = typer.Option(8000, "--port", help="Porta local para o servidor web."),
) -> None:
    """Inicia o painel web local e experimental do BioStack."""
    try:
        import uvicorn
    except ImportError as exc:
        console.print(
            "[red]Erro:[/red] dependências web não instaladas. "
            "Instale com: python -m pip install -e '.[web]'"
        )
        raise typer.Exit(code=1) from exc

    console.print(f"[green]BioStack web local:[/green] http://{host}:{port}")
    uvicorn.run("biostack.web.app:app", host=host, port=port, reload=False)
