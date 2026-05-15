"""Report schemas for the versioned API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ReportSummaryResponse(BaseModel):
    """Summary for a generated BioStack report."""

    project_name: str
    run_id: str
    status: str
    workflow: str
    started_at: str
    json_path: str
    html_path: str | None = None


class ReportDetailResponse(BaseModel):
    """Detailed JSON report response."""

    project_name: str
    run_id: str
    metadata: dict[str, Any]
