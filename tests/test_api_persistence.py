"""Tests for API persistence added in phase_11 and queued runs in phase_12."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from biostack.api.app import create_app
from biostack.db.models import AuditEvent, Base, Project, Run
from biostack.db.session import get_engine
from biostack.worker.queue import enqueue_run_job


class FakeRedis:
    def __init__(self) -> None:
        self.items: list[tuple[str, str]] = []

    def lpush(self, name: str, value: str) -> int:
        self.items.insert(0, (name, value))
        return len(self.items)

    def brpop(self, keys: str | list[str], timeout: int = 0):  # noqa: ANN001
        return self.items.pop() if self.items else None


def test_api_persists_project_and_queued_run(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "api-persistence.db"
    database_url = f"sqlite:///{database_path}"
    monkeypatch.setenv("BIOSTACK_WORKSPACE", tmp_path.as_posix())
    monkeypatch.setenv("BIOSTACK_DATABASE_URL", database_url)

    fake_redis = FakeRedis()

    def fake_enqueue_run_job(**kwargs):  # noqa: ANN003, ANN202
        return enqueue_run_job(**kwargs, redis_client=fake_redis, queue_name="test:runs")

    monkeypatch.setattr("biostack.api.routes.runs.enqueue_run_job", fake_enqueue_run_job)

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
    assert run_payload["status"] == "QUEUED"
    assert fake_redis.items

    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with session_factory() as session:
        project = session.scalar(select(Project).where(Project.name == "demo-api-db"))
        assert project is not None
        run = session.scalar(select(Run).where(Run.run_id == run_payload["run_id"]))
        assert run is not None
        assert run.project_id == project.id
        assert run.dry_run is True
        assert run.status == "QUEUED"
        actions = [event.action for event in session.scalars(select(AuditEvent))]
        assert "project.upserted" in actions
        assert "run.queued" in actions
