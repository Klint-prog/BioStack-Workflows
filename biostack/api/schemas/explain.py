"""Explain schemas for the versioned API."""

from __future__ import annotations

from pydantic import BaseModel


class ExplainRequest(BaseModel):
    """Request body for operational AI troubleshooting."""

    project_name: str
    run: str = "latest"
    provider: str = "mock"


class ExplainResponse(BaseModel):
    """Troubleshooting explanation returned by the API."""

    status: str
    project_name: str
    run_id: str
    provider: str
    clinical_warning: str
    explanation: str
