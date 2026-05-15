"""Repository helpers for persistent BioStack metadata."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from biostack.core.config import BioStackConfig
from biostack.db.models import AuditEvent, Project, Run, RunEvent, RunFile


def upsert_project(
    session: Session,
    *,
    path: Path,
    config: BioStackConfig,
    metadata: dict[str, Any] | None = None,
) -> Project:
    """Create or update a project row from a filesystem project."""
    project = session.scalar(select(Project).where(Project.name == config.project.name))
    payload = metadata or {}
    if project is None:
        project = Project(
            name=config.project.name,
            path=path.as_posix(),
            template=config.project.template,
            workflow=config.workflow.name,
            metadata_json=payload,
        )
        session.add(project)
    else:
        project.path = path.as_posix()
        project.template = config.project.template
        project.workflow = config.workflow.name
        project.metadata_json = payload
    session.flush()
    add_audit_event(
        session,
        action="project.upserted",
        entity_type="project",
        entity_id=str(project.id),
        payload={"name": project.name, "path": project.path},
    )
    return project


def list_projects(session: Session) -> list[Project]:
    """Return persisted projects ordered by name."""
    return list(session.scalars(select(Project).order_by(Project.name)))


def get_project_by_name(session: Session, name: str) -> Project | None:
    """Return one persisted project by name."""
    return session.scalar(select(Project).where(Project.name == name))


def create_run_record(
    session: Session,
    *,
    project: Project,
    run_id: str,
    workflow: str,
    profile: str,
    status: str,
    dry_run: bool,
    command: list[str],
    return_code: int | None,
    log_path: str,
    report_json_path: str,
    report_html_path: str,
    metadata: dict[str, Any] | None = None,
) -> Run:
    """Persist a completed run and its core audit/file records."""
    run = Run(
        project_id=project.id,
        run_id=run_id,
        workflow=workflow,
        profile=profile,
        status=status,
        dry_run=dry_run,
        command=command,
        return_code=return_code,
        log_path=log_path,
        report_json_path=report_json_path,
        report_html_path=report_html_path,
        metadata_json=metadata or {},
    )
    session.add(run)
    session.flush()
    session.add(
        RunEvent(
            run_id=run.id,
            event_type="run.completed",
            message=f"Run {run.run_id} persisted with status {status}.",
            payload={"dry_run": dry_run, "return_code": return_code},
        )
    )
    session.add(RunFile(run_id=run.id, path=log_path, role="log"))
    session.add(RunFile(run_id=run.id, path=report_json_path, role="report_json"))
    session.add(RunFile(run_id=run.id, path=report_html_path, role="report_html"))
    add_audit_event(
        session,
        action="run.created",
        entity_type="run",
        entity_id=str(run.id),
        payload={"project": project.name, "run_id": run.run_id, "status": status},
    )
    session.flush()
    return run


def add_audit_event(
    session: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    payload: dict[str, Any] | None = None,
    actor: str = "system",
) -> AuditEvent:
    """Append an audit event."""
    event = AuditEvent(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload or {},
    )
    session.add(event)
    return event
