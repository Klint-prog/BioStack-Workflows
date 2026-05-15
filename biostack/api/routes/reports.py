"""Report routes for the versioned API."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from biostack.api.schemas.reports import ReportDetailResponse, ReportSummaryResponse
from biostack.api.workspace import WorkspaceError, discover_project_configs, load_project
from biostack.reports.generator import (
    ReportNotFoundError,
    load_metadata_report,
    resolve_report_json,
)

router = APIRouter(prefix="/reports", tags=["reports"])


def _report_summary(project_name: str, json_path) -> ReportSummaryResponse:
    metadata = load_metadata_report(json_path)
    html_path = json_path.with_suffix(".html")
    return ReportSummaryResponse(
        project_name=project_name,
        run_id=metadata.run_id,
        status=metadata.status,
        workflow=metadata.workflow,
        started_at=metadata.started_at.isoformat(),
        json_path=json_path.as_posix(),
        html_path=html_path.as_posix() if html_path.is_file() else None,
    )


@router.get("", response_model=list[ReportSummaryResponse])
def list_reports(project_name: str | None = None) -> list[ReportSummaryResponse]:
    """List generated JSON reports for all projects or one project."""
    try:
        if project_name:
            projects = [load_project(project_name)]
        else:
            projects = discover_project_configs()
    except WorkspaceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    reports: list[ReportSummaryResponse] = []
    for project_dir, config in projects:
        reports_root = project_dir / config.storage.reports
        if not reports_root.is_dir():
            continue
        for json_path in sorted(reports_root.glob("run-*.json")):
            try:
                reports.append(_report_summary(config.project.name, json_path))
            except Exception:
                continue
    return sorted(reports, key=lambda item: (item.started_at, item.run_id), reverse=True)


@router.get("/{project_name}/{run}", response_model=ReportDetailResponse)
def get_report(project_name: str, run: str) -> ReportDetailResponse:
    """Return the stored JSON metadata for a run id or latest."""
    try:
        project_dir, config = load_project(project_name)
        json_path = resolve_report_json(
            project_dir=project_dir,
            run=run,
            reports_dir=config.storage.reports,
        )
    except WorkspaceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ReportNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    metadata = json.loads(json_path.read_text(encoding="utf-8"))
    return ReportDetailResponse(
        project_name=config.project.name,
        run_id=str(metadata.get("run_id", json_path.stem)),
        metadata=metadata,
    )
