"""Run routes for the versioned API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from biostack.api.schemas.runs import RunCreateRequest, RunResponse
from biostack.api.workspace import WorkspaceError, load_project
from biostack.core.metadata import generate_run_id
from biostack.db.models import Run
from biostack.db.repositories import create_queued_run_record, list_runs, upsert_project
from biostack.db.session import get_session
from biostack.worker.queue import enqueue_run_job

router = APIRouter(prefix="/runs", tags=["runs"])


def _run_response(run: Run) -> RunResponse:
    """Convert a persisted run row into an API response."""
    return RunResponse(
        status=run.status,
        project_name=run.project.name,
        run_id=run.run_id,
        workflow=run.workflow,
        profile=run.profile,
        dry_run=run.dry_run,
        command=run.command,
        log_path=run.log_path,
        report_json_path=run.report_json_path,
        report_html_path=run.report_html_path,
        return_code=run.return_code,
        database_id=str(run.id),
        job_id=None,
        created_at=run.created_at.isoformat() if run.created_at else None,
        updated_at=run.updated_at.isoformat() if run.updated_at else None,
    )


@router.get("", response_model=list[RunResponse])
def list_run_records(
    project_name: str | None = None,
    db: Session = Depends(get_session),
) -> list[RunResponse]:
    """List persisted workflow runs for the frontend status table."""
    return [_run_response(run) for run in list_runs(db, project_name=project_name)]


@router.post("", response_model=RunResponse, status_code=201)
def create_run(
    payload: RunCreateRequest,
    db: Session = Depends(get_session),
) -> RunResponse:
    """Create a queued workflow run and enqueue it for worker processing."""
    try:
        project_dir, config = load_project(payload.project_name)
        workflow = payload.workflow or config.workflow.name
        profile = payload.profile or config.workflow.profile
        project = upsert_project(db, path=project_dir, config=config)
        run = create_queued_run_record(
            db,
            project=project,
            run_id=generate_run_id(),
            workflow=workflow,
            profile=profile,
            dry_run=payload.dry_run,
        )
        job = enqueue_run_job(
            database_id=str(run.id),
            project_name=config.project.name,
            project_path=project_dir.as_posix(),
            workflow=workflow,
            profile=profile,
            dry_run=payload.dry_run,
        )
        db.commit()
        db.refresh(run)
    except WorkspaceError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return RunResponse(
        status="QUEUED",
        project_name=config.project.name,
        run_id=run.run_id,
        workflow=workflow,
        profile=profile,
        dry_run=payload.dry_run,
        command=[],
        log_path="",
        report_json_path="",
        report_html_path="",
        return_code=None,
        database_id=str(run.id),
        job_id=job.job_id,
        created_at=run.created_at.isoformat() if run.created_at else None,
        updated_at=run.updated_at.isoformat() if run.updated_at else None,
    )
