"""Repository helpers for persistent BioStack metadata."""

from __future__ import annotations

import uuid
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


def list_runs(session: Session, project_name: str | None = None, limit: int = 100) -> list[Run]:
    """Return persisted runs ordered from newest to oldest."""
    statement = select(Run).join(Project).order_by(Run.created_at.desc(), Run.run_id.desc()).limit(limit)
    if project_name:
        statement = statement.where(Project.name == project_name)
    return list(session.scalars(statement))


def get_run_by_database_id(session: Session, database_id: str | uuid.UUID) -> Run | None:
    """Return a persisted run by its database UUID."""
    return session.get(Run, uuid.UUID(str(database_id)))


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
    """Persist a run and its core audit/file records."""
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
    add_run_event(
        session,
        run=run,
        event_type=f"run.{status.lower()}",
        message=f"Run {run.run_id} persisted with status {status}.",
        payload={"dry_run": dry_run, "return_code": return_code},
    )
    _sync_run_files(session, run)
    add_audit_event(
        session,
        action="run.created",
        entity_type="run",
        entity_id=str(run.id),
        payload={"project": project.name, "run_id": run.run_id, "status": status},
    )
    session.flush()
    return run


def create_queued_run_record(
    session: Session,
    *,
    project: Project,
    run_id: str,
    workflow: str,
    profile: str,
    dry_run: bool,
) -> Run:
    """Persist a queued run before asynchronous worker execution."""
    run = Run(
        project_id=project.id,
        run_id=run_id,
        workflow=workflow,
        profile=profile,
        status="QUEUED",
        dry_run=dry_run,
        command=[],
        return_code=None,
        log_path="",
        report_json_path="",
        report_html_path="",
        metadata_json={},
    )
    session.add(run)
    session.flush()
    add_run_event(
        session,
        run=run,
        event_type="run.queued",
        message=f"Run {run.run_id} enfileirada para execução assíncrona.",
        payload={"dry_run": dry_run},
    )
    add_audit_event(
        session,
        action="run.queued",
        entity_type="run",
        entity_id=str(run.id),
        payload={"project": project.name, "run_id": run.run_id, "status": run.status},
    )
    session.flush()
    return run


def update_run_status(
    session: Session,
    *,
    run: Run,
    status: str,
    message: str | None = None,
    payload: dict[str, Any] | None = None,
) -> Run:
    """Update run status and append lifecycle/audit events."""
    run.status = status
    session.flush()
    add_run_event(
        session,
        run=run,
        event_type=f"run.{status.lower()}",
        message=message or f"Run {run.run_id} atualizada para {status}.",
        payload=payload or {},
    )
    add_audit_event(
        session,
        action=f"run.{status.lower()}",
        entity_type="run",
        entity_id=str(run.id),
        payload={"run_id": run.run_id, "status": status, **(payload or {})},
    )
    session.flush()
    return run


def complete_run_record(
    session: Session,
    *,
    run: Run,
    command: list[str],
    return_code: int | None,
    log_path: str,
    report_json_path: str,
    report_html_path: str,
    metadata: dict[str, Any] | None,
    status: str,
) -> Run:
    """Persist worker execution outputs for an existing queued run."""
    run.command = command
    run.return_code = return_code
    run.log_path = log_path
    run.report_json_path = report_json_path
    run.report_html_path = report_html_path
    run.metadata_json = metadata or {}
    update_run_status(
        session,
        run=run,
        status=status,
        message=f"Run {run.run_id} finalizada pelo worker com status {status}.",
        payload={"return_code": return_code},
    )
    _sync_run_files(session, run)
    session.flush()
    return run


def add_run_event(
    session: Session,
    *,
    run: Run,
    event_type: str,
    message: str,
    payload: dict[str, Any] | None = None,
) -> RunEvent:
    """Append one structured run event."""
    event = RunEvent(
        run_id=run.id,
        event_type=event_type,
        message=message,
        payload=payload or {},
    )
    session.add(event)
    return event


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


def _sync_run_files(session: Session, run: Run) -> None:
    """Persist non-empty file references linked to a run."""
    files = [
        (run.log_path, "log"),
        (run.report_json_path, "report_json"),
        (run.report_html_path, "report_html"),
    ]
    for path, role in files:
        if path:
            session.add(RunFile(run_id=run.id, path=path, role=role))
