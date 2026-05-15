from __future__ import annotations

from fastapi.testclient import TestClient

from biostack.api.app import create_app
from biostack.core.runner import run_workflow_with_run_id
from biostack.db.models import Base
from biostack.db.session import get_engine


def test_platform_e2e_flow_with_mock_explain(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    database_url = f"sqlite:///{tmp_path / 'platform.db'}"
    monkeypatch.setenv("BIOSTACK_WORKSPACE", workspace.as_posix())
    monkeypatch.setenv("BIOSTACK_DATABASE_URL", database_url)
    monkeypatch.setenv("BIOSTACK_LLM_PROVIDER", "mock")

    engine = get_engine(database_url)
    Base.metadata.create_all(engine)

    client = TestClient(create_app())

    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    project_response = client.post(
        "/api/v1/projects",
        json={"name": "e2e-api", "template": "rnaseq-basic", "force": True},
    )
    assert project_response.status_code == 201
    assert project_response.json()["project"]["name"] == "e2e-api"

    run_result = run_workflow_with_run_id(
        project_dir=workspace / "e2e-api",
        dry_run=True,
        run_id_override="run-e2e-platform",
    )
    assert run_result.report_json_path.is_file()
    assert run_result.report_html_path.is_file()

    reports_response = client.get("/api/v1/reports?project_name=e2e-api")
    assert reports_response.status_code == 200
    reports = reports_response.json()
    assert reports[0]["run_id"] == "run-e2e-platform"

    report_response = client.get("/api/v1/reports/e2e-api/run-e2e-platform")
    assert report_response.status_code == 200
    assert report_response.json()["metadata"]["dry_run"] is True

    explain_response = client.post(
        "/api/v1/explain",
        json={"project_name": "e2e-api", "run": "run-e2e-platform", "provider": "mock"},
    )
    assert explain_response.status_code == 200
    explain = explain_response.json()
    assert explain["provider"] == "mock"
    assert "diagnóstico" in explain["clinical_warning"].lower()
