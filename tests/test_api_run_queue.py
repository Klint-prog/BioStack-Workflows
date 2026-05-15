"""Tests for API run enqueueing added in phase_12."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from biostack.api.app import create_app
from biostack.db.models import AuditEvent, Base, Run
from biostack.db.session import get_engine


class FakeRedis:
    def __init__(self) -> None:
        self.items: list[tuple[str, str]] = []

    def lpush(self, name: str, value: str) -> int:
        self.items.insert(0, (name, value))
        return len(self.items)

    def brpop(self, keys: str | list[str], timeout: int = 0):  # noqa: ANN001
        return self.items.pop() if self.items else None


def test_api_creates_queued_run_and_enqueues_job(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "api-run-queue.db"
    database_url = f"sqlite:///{database_path}"
    monkeypatch.setenv("BIOSTACK_WORKSPACE", tmp_path.as_posix())
    monkeypatch.setenv("BIOSTACK_DATABASE_URL", database_url)

    fake_redis = FakeRedis()
    monkeypatch.setattr(
        "biostack.api.routes.runs.enqueue_run_job",
        lambda **kwargs: __import__("biostack.worker.queue", fromlist=["enqueue_run_job"]).enqueue_run_job(
            **kwargs,
            redis_client=fake_redis,
            queue_name="test:runs",
        ),
    )

    engine = get_engine(database_url)
    Base.metadata.create_all(engine)
    client = TestClient(create_app())

    create_response = client.post(
        "/api/v1/projects",
        json={"name": "demo-api-queue", "template": "rnaseq-basic"},
    )
    assert create_response.status_code == 201

    run_response = client.post(
        "/api/v1/runs",
        json={"project_name": "demo-api-queue", "dry_run": True},
    )

    assert run_response.status_code == 201
    payload = run_response.json()
    assert payload["status"] == "QUEUED"
    assert payload["database_id"]
    assert payload["job_id"].startswith("job-")
    assert payload["command"] == []
    assert fake_redis.items

    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with session_factory() as session:
        run = session.scalar(select(Run).where(Run.id == payload["database_id"]))
        assert run is not None
        assert run.status == "QUEUED"
        assert run.dry_run is True
        actions = [event.action for event in session.scalars(select(AuditEvent))]
        assert "run.queued" in actions
