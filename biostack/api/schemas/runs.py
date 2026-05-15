"""Run schemas for the versioned API."""

from __future__ import annotations

from pydantic import BaseModel


class RunCreateRequest(BaseModel):
    """Request body for synchronously starting a run."""

    project_name: str
    workflow: str | None = None
    profile: str | None = None
    dry_run: bool = True


class RunResponse(BaseModel):
    """Workflow run response returned by the API."""

    status: str
    project_name: str
    run_id: str
    workflow: str
    profile: str
    dry_run: bool
    command: list[str]
    log_path: str
    report_json_path: str
    report_html_path: str
    return_code: int | None = None
    database_id: str | None = None
