"""FastAPI application factory for the experimental local BioStack web UI."""

from __future__ import annotations

from fastapi import FastAPI

from biostack import __version__
from biostack.web.routes import router


def create_app() -> FastAPI:
    """Create the local-only BioStack web application."""
    app = FastAPI(
        title="BioStack Workflows Local Web UI",
        version=__version__,
        description="Painel web local e experimental para projetos, execuções e relatórios BioStack.",
    )
    app.include_router(router)
    return app


app = create_app()
