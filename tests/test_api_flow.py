"""End-to-end tests for the phase_12 versioned API flow."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from biostack.api.app import create_app
from biostack.db.models import Base
from biostack.db.session import get_engine
from biostack.worker.queue import enqueue_run_job, pop_run_job
from biostack.worker.runner import process_run_job


class FakeRedis:
    def __init__(self) -> None:
        self.items: list[tuple[str, str]] = []

    def lpush(self, name: str, value: str) -> int:
        self.items.insert(0, (name, value))
        return len(self.items)

    def brpop(self, keys: str | list[str], timeout: int = 0):  # noqa: ANN001
        return self.items.pop() if self.items else None


def test_api_minimal_project_run_report_explain_flow(tmp_path, monkeypatch) -> None:
    database_url = f"sqlite:///{tmp_path / 'api-flow.db'}"
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
        json={"name": "demo-api", "template": "rnaseq-basic"},
    )
    assert create_response.status_code == 201
    assert create_response.json()["project"]["name"] == "demo-api"
    assert create_response.json()["project"]["database_id"]

    list_projects_response = client.get("/api/v1/projects")
    assert list_projects_response.status_code == 200
    assert [project["name"] for project in list_projects_response.json()] == ["demo-api"]

    run_response = client.post(
        "/api/v1/runs",
        json={"project_name": "demo-api", "dry_run": True},
    )
    assert run_response.status_code == 201
    run_payload = run_response.json()
    assert run_payload["status"] == "QUEUED"
    assert run_payload["dry_run"] is True
    assert run_payload["workflow"] == "rnaseq-basic"
    assert run_payload["run_id"].startswith("run-")
    assert run_payload["database_id"]
    assert run_payload["job_id"].startswith("job-")

    job = pop_run_job(redis_client=fake_redis, queue_name="test:runs", timeout=0)
    assert job is not None
    process_run_job(job, database_url=database_url)

    reports_response = client.get("/api/v1/reports?project_name=demo-api")
    assert reports_response.status_code == 200
    reports_payload = reports_response.json()
    assert len(reports_payload) == 1
    assert reports_payload[0]["run_id"] == run_payload["run_id"]

    report_detail_response = client.get("/api/v1/reports/demo-api/latest")
    assert report_detail_response.status_code == 200
    assert report_detail_response.json()["metadata"]["run_id"] == run_payload["run_id"]

    explain_response = client.post(
        "/api/v1/explain",
        json={"project_name": "demo-api", "run": "latest", "provider": "mock"},
    )
    assert explain_response.status_code == 200
    explain_payload = explain_response.json()
    assert explain_payload["run_id"] == run_payload["run_id"]
    assert "Não usar para diagnóstico" in explain_payload["clinical_warning"]
    assert "provider fake" in explain_payload["explanation"]

    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with session_factory() as session:
        Base.metadata.create_all(engine)
