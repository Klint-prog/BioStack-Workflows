"""End-to-end tests for the phase_10 versioned API flow."""

from __future__ import annotations

from fastapi.testclient import TestClient

from biostack.api.app import create_app


def test_api_minimal_project_run_report_explain_flow(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("BIOSTACK_WORKSPACE", tmp_path.as_posix())
    client = TestClient(create_app())

    create_response = client.post(
        "/api/v1/projects",
        json={"name": "demo-api", "template": "rnaseq-basic"},
    )
    assert create_response.status_code == 201
    assert create_response.json()["project"]["name"] == "demo-api"

    list_projects_response = client.get("/api/v1/projects")
    assert list_projects_response.status_code == 200
    assert [project["name"] for project in list_projects_response.json()] == ["demo-api"]

    run_response = client.post(
        "/api/v1/runs",
        json={"project_name": "demo-api", "dry_run": True},
    )
    assert run_response.status_code == 201
    run_payload = run_response.json()
    assert run_payload["status"] == "completed"
    assert run_payload["dry_run"] is True
    assert run_payload["workflow"] == "rnaseq-basic"
    assert run_payload["run_id"].startswith("run-")

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
