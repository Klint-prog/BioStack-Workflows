from pathlib import Path

from fastapi.testclient import TestClient

from biostack.core.project import create_project
from biostack.core.runner import run_workflow
from biostack.web.app import create_app
from biostack.web.routes import discover_projects, discover_reports


def test_web_index_and_reports_routes_render_empty_state(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    client = TestClient(create_app())

    index_response = client.get("/")
    reports_response = client.get("/reports")

    assert index_response.status_code == 200
    assert "BioStack Workflows" in index_response.text
    assert reports_response.status_code == 200
    assert "Relatórios BioStack" in reports_response.text


def test_web_discovers_project_and_generated_report(tmp_path: Path, monkeypatch) -> None:
    create_project("demo", base_dir=tmp_path)
    project_dir = tmp_path / "demo"
    (project_dir / "data" / "raw" / "sample.fastq").write_text("ACGT", encoding="utf-8")
    run_workflow(project_dir=project_dir, dry_run=True)
    monkeypatch.chdir(tmp_path)

    projects = discover_projects()
    reports = discover_reports()
    client = TestClient(create_app())
    index_response = client.get("/")
    reports_response = client.get("/reports")
    detail_response = client.get(f"/reports/{reports[0].run_id}")

    assert [project.name for project in projects] == ["demo"]
    assert len(reports) == 1
    assert reports[0].project_name == "demo"
    assert index_response.status_code == 200
    assert "demo" in index_response.text
    assert reports_response.status_code == 200
    assert reports[0].run_id in reports_response.text
    assert detail_response.status_code == 200
    assert "BioStack Run Report" in detail_response.text


def test_unknown_report_returns_404(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    client = TestClient(create_app())

    response = client.get("/reports/run-missing")

    assert response.status_code == 404
