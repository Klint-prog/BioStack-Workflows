"""Tests for API persistence added in phase_11."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from biostack.api.app import create_app
from biostack.db.models import AuditEvent, Base, Project, Run
from biostack.db.session import get_engine


def test_api_persists_project_and_run_while_keeping_reports_on_filesystem(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "api-persistence.db"
    database_url = f"sqlite:///{database_path}"
    monkeypatch.setenv("BIOSTACK_WORKSPACE", tmp_path.as_posix())
    monkeypatch.setenv("BIOSTACK_DATABASE_URL", database_url)

    engine = get_engine(database_url)
    Base.metadata.create_all(engine)

    client = TestClient(create_app())

    create_response = client.post(
        "/api/v1/projects",
        json={"name": "demo-api-db", "template": "rnaseq-basic"},
    )
    assert create_response.status_code == 201
    create_payload = create_response.json()
    assert create_payload["project"]["database_id"]

    run_response = client.post(
        "/api/v1/runs",
        json={"project_name": "demo-api-db", "dry_run": True},
    )
    assert run_response.status_code == 201
    run_payload = run_response.json()
    assert run_payload["database_id"]

    assert (tmp_path / "demo-api-db" / run_payload["report_json_path"]).is_file()
    assert (tmp_path / "demo-api-db" / run_payload["report_html_path"]).is_file()

    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with session_factory() as session:
        project = session.scalar(select(Project).where(Project.name == "demo-api-db"))
        assert project is not None
        run = session.scalar(select(Run).where(Run.run_id == run_payload["run_id"]))
        assert run is not None
        assert run.project_id == project.id
        assert run.dry_run is True
        assert run.report_json_path == run_payload["report_json_path"]
        actions = [event.action for event in session.scalars(select(AuditEvent))]
        assert "project.upserted" in actions
        assert "run.created" in actions
