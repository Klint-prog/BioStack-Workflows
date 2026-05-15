"""FastAPI application factory for the BioStack versioned API."""

from __future__ import annotations

from fastapi import FastAPI

from biostack.api.routes import explain, health, projects, reports, runs

API_V1_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    """Create the BioStack FastAPI application with versioned routes."""
    app = FastAPI(
        title="BioStack Workflows API",
        version="0.2.0-phase-10",
        description="Versioned local-first API for BioStack workflow operations.",
    )
    app.include_router(health.router, prefix=API_V1_PREFIX)
    app.include_router(projects.router, prefix=API_V1_PREFIX)
    app.include_router(runs.router, prefix=API_V1_PREFIX)
    app.include_router(reports.router, prefix=API_V1_PREFIX)
    app.include_router(explain.router, prefix=API_V1_PREFIX)
    return app


app = create_app()
