"""Run routes for the versioned API."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from biostack.api.schemas.runs import RunCreateRequest, RunResponse
from biostack.api.workspace import WorkspaceError, load_project
from biostack.core.runner import RunnerError, run_workflow
from biostack.db.repositories import create_run_record, upsert_project
from biostack.db.session import get_session
from biostack.reports.generator import load_metadata_report

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=RunResponse, status_code=201)
def create_run(
    payload: RunCreateRequest,
    db: Session = Depends(get_session),
) -> RunResponse:
    """Start a synchronous workflow run and persist its metadata.

    Phase 11 intentionally keeps execution synchronous and does not introduce
    queues, workers, Redis or distributed orchestration.
    """
    try:
        project_dir, config = load_project(payload.project_name)
        result = run_workflow(
            project_dir=project_dir,
            workflow=payload.workflow,
            profile=payload.profile,
            dry_run=payload.dry_run,
        )
        metadata = load_metadata_report(result.report_json_path)
        project = upsert_project(db, path=project_dir, config=config)
        run = create_run_record(
            db,
            project=project,
            run_id=result.run_id,
            workflow=result.workflow_name,
            profile=result.profile,
            status="completed",
            dry_run=result.dry_run,
            command=result.command,
            return_code=result.return_code,
            log_path=result.log_path.as_posix(),
            report_json_path=result.report_json_path.as_posix(),
            report_html_path=result.report_html_path.as_posix(),
            metadata=json.loads(metadata.model_dump_json()),
        )
        db.commit()
        db.refresh(run)
    except WorkspaceError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RunnerError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return RunResponse(
        status="completed",
        project_name=config.project.name,
        run_id=result.run_id,
        workflow=result.workflow_name,
        profile=result.profile,
        dry_run=result.dry_run,
        command=result.command,
        log_path=result.log_path.as_posix(),
        report_json_path=result.report_json_path.as_posix(),
        report_html_path=result.report_html_path.as_posix(),
        return_code=result.return_code,
        database_id=str(run.id),
    )
