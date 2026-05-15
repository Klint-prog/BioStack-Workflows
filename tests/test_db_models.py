"""Tests for phase_11 persistent database models."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from biostack.core.config import load_project_config
from biostack.core.project import create_project
from biostack.db.models import AuditEvent, Base, Project, Run, RunEvent, RunFile
from biostack.db.repositories import create_run_record, upsert_project
from biostack.db.session import get_engine


def test_database_models_persist_project_run_files_and_audit_events(tmp_path: Path) -> None:
    engine = get_engine(f"sqlite:///{tmp_path / 'biostack-test.db'}")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    created = create_project("demo-db", template="rnaseq-basic", base_dir=tmp_path)
    config = load_project_config(created.path / "biostack.yml")

    with session_factory() as session:
        project = upsert_project(session, path=created.path, config=config)
        run = create_run_record(
            session,
            project=project,
            run_id="run-test-0001",
            workflow="rnaseq-basic",
            profile="docker",
            status="completed",
            dry_run=True,
            command=["nextflow", "run", "main.nf"],
            return_code=0,
            log_path="logs/run-test-0001.log",
            report_json_path="reports/run-test-0001.json",
            report_html_path="reports/run-test-0001.html",
            metadata={"source": "test"},
        )
        session.commit()

        persisted_project = session.scalar(select(Project).where(Project.name == "demo-db"))
        persisted_run = session.scalar(select(Run).where(Run.run_id == "run-test-0001"))
        assert persisted_project is not None
        assert persisted_run is not None
        assert persisted_run.project_id == persisted_project.id
        assert persisted_run.metadata_json["source"] == "test"
        assert session.scalar(select(RunEvent).where(RunEvent.run_id == run.id)) is not None
        assert len(list(session.scalars(select(RunFile).where(RunFile.run_id == run.id)))) == 3
        assert len(list(session.scalars(select(AuditEvent)))) == 2
