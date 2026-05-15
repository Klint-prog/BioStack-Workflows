"""Project routes for the versioned API."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from biostack.api.schemas.projects import (
    ProjectCreateRequest,
    ProjectCreateResponse,
    ProjectResponse,
)
from biostack.api.workspace import WorkspaceError, discover_project_configs, workspace_root
from biostack.core.config import BioStackConfig
from biostack.core.project import ProjectAlreadyExistsError, ProjectCreationError, create_project

router = APIRouter(prefix="/projects", tags=["projects"])


def _project_response(path: Path, config: BioStackConfig) -> ProjectResponse:
    reports_root = path / config.storage.reports
    reports_count = len(list(reports_root.glob("run-*.json"))) if reports_root.is_dir() else 0
    return ProjectResponse(
        name=config.project.name,
        path=path.as_posix(),
        template=config.project.template,
        workflow=config.workflow.name,
        reports_count=reports_count,
    )


@router.get("", response_model=list[ProjectResponse])
def list_projects() -> list[ProjectResponse]:
    """List BioStack projects detected in the configured workspace."""
    return [_project_response(path, config) for path, config in discover_project_configs()]


@router.post("", response_model=ProjectCreateResponse, status_code=201)
def create_project_endpoint(payload: ProjectCreateRequest) -> ProjectCreateResponse:
    """Create a BioStack project using the existing filesystem scaffolder."""
    try:
        created = create_project(
            payload.name,
            template=payload.template,
            force=payload.force,
            base_dir=workspace_root(),
        )
    except ProjectAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (ProjectCreationError, WorkspaceError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ProjectCreateResponse(
        status="created",
        project=_project_response(created.path, created.config),
    )
