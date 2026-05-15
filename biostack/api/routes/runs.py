"""Run routes for the versioned API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from biostack.api.schemas.runs import RunCreateRequest, RunResponse
from biostack.api.workspace import WorkspaceError, load_project
from biostack.core.runner import RunnerError, run_workflow

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=RunResponse, status_code=201)
def create_run(payload: RunCreateRequest) -> RunResponse:
    """Start a synchronous workflow run.

    Phase 10 intentionally defaults to dry-run and does not introduce queues,
    workers, Redis or distributed orchestration.
    """
    try:
        project_dir, config = load_project(payload.project_name)
        result = run_workflow(
            project_dir=project_dir,
            workflow=payload.workflow,
            profile=payload.profile,
            dry_run=payload.dry_run,
        )
    except WorkspaceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RunnerError as exc:
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
    )
