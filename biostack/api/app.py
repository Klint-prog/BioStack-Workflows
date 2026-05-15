"""FastAPI application factory for the BioStack versioned API."""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from biostack.api.routes import explain, health, projects, reports, runs

API_V1_PREFIX = "/api/v1"


def _configure_logging() -> None:
    """Configure predictable container-friendly logging for the API."""
    log_level = os.getenv("BIOSTACK_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def _cors_origins() -> list[str]:
    """Read comma-separated CORS origins from the environment."""
    raw_origins = os.getenv("BIOSTACK_CORS_ORIGINS", "http://localhost:8080,http://localhost:5173")
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def create_app() -> FastAPI:
    """Create the BioStack FastAPI application with versioned routes."""
    _configure_logging()
    logger = logging.getLogger("biostack.api")
    app = FastAPI(
        title="BioStack Workflows API",
        version="0.2.0",
        description="Versioned local-first API for BioStack workflow operations.",
    )
    origins = _cors_origins()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    logger.info("BioStack API starting with CORS origins: %s", origins)
    app.include_router(health.router, prefix=API_V1_PREFIX)
    app.include_router(projects.router, prefix=API_V1_PREFIX)
    app.include_router(runs.router, prefix=API_V1_PREFIX)
    app.include_router(reports.router, prefix=API_V1_PREFIX)
    app.include_router(explain.router, prefix=API_V1_PREFIX)
    return app


app = create_app()
