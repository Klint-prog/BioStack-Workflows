"""Project routes for the versioned API."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from biostack.api.schemas.projects import (
    ProjectCreateRequest,
    ProjectCreateResponse,
    ProjectResponse,
)
from biostack.api.workspace import WorkspaceError, discover_project_configs, workspace_root
from biostack.core.config import BioStackConfig
from biostack.core.project import ProjectAlreadyExistsError, ProjectCreationError, create_project
from biostack.db.repositories import get_project_by_name, list_projects as list_persisted_projects
from biostack.db.repositories import upsert_project
from biostack.db.session import get_session

router = APIRouter(prefix="/projects", tags=["projects"])


def _project_response(
    path: Path,
    config: BioStackConfig,
    *,
    database_id: str | None = None,
) -> ProjectResponse:
    reports_root = path / config.storage.reports
    reports_count = len(list(reports_root.glob("run-*.json"))) if reports_root.is_dir() else 0
    return ProjectResponse(
        name=config.project.name,
        path=path.as_posix(),
        template=config.project.template,
        workflow=config.workflow.name,
        reports_count=reports_count,
        database_id=database_id,
    )


@router.get("", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_session)) -> list[ProjectResponse]:
    """List projects, preferring database rows after persistence is enabled."""
    persisted = list_persisted_projects(db)
    if persisted:
        return [
            ProjectResponse(
                name=project.name,
                path=project.path,
                template=project.template,
                workflow=project.workflow,
                reports_count=0,
                database_id=str(project.id),
            )
            for project in persisted
        ]
    return [_project_response(path, config) for path, config in discover_project_configs()]


@router.post("", response_model=ProjectCreateResponse, status_code=201)
def create_project_endpoint(
    payload: ProjectCreateRequest,
    db: Session = Depends(get_session),
) -> ProjectCreateResponse:
    """Create a BioStack project and persist its metadata in the database."""
    try:
        created = create_project(
            payload.name,
            template=payload.template,
            force=payload.force,
            base_dir=workspace_root(),
        )
        project = upsert_project(db, path=created.path, config=created.config)
        db.commit()
        db.refresh(project)
    except ProjectAlreadyExistsError as exc:
        db.rollback()
        existing = get_project_by_name(db, payload.name)
        if existing is not None:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (ProjectCreationError, WorkspaceError) as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ProjectCreateResponse(
        status="created",
        project=_project_response(created.path, created.config, database_id=str(project.id)),
    )
