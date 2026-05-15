"""Healthcheck route for the versioned API."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck() -> dict[str, str]:
    """Return a minimal API health status."""
    return {"status": "ok"}
