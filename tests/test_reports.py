from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from typer.testing import CliRunner

from biostack.core.metadata import RunMetadata, collect_tool_versions, utc_now
from biostack.core.project import create_project
from biostack.core.runner import run_workflow
from biostack.main import app
from biostack.reports.generator import (
    generate_reports,
    regenerate_html_for_run,
    resolve_report_json,
)

runner = CliRunner()


def _metadata(run_id: str) -> RunMetadata:
    return RunMetadata(
        run_id=run_id,
        started_at=utc_now(),
        finished_at=utc_now(),
        duration_seconds=0.1,
        workflow="rnaseq-basic",
        profile="local",
        command=["nextflow", "run", "workflow"],
        status="SUCCEEDED",
        versions=collect_tool_versions(),
        parameters={"input": "data/raw"},
        log_text="log body",
    )


def test_generate_reports_writes_json_and_html(tmp_path: Path) -> None:
    metadata = _metadata("run-20260101T000000Z-test")

    json_path, html_path = generate_reports(metadata, project_dir=tmp_path)

    assert json_path.is_file()
    assert html_path.is_file()
    assert '"run_id": "run-20260101T000000Z-test"' in json_path.read_text(encoding="utf-8")
    assert "BioStack Run Report" in html_path.read_text(encoding="utf-8")


def test_report_latest_resolves_deterministically_and_regenerates_html(tmp_path: Path) -> None:
    older = _metadata("run-20260101T000000Z-old")
    newer = _metadata("run-20260102T000000Z-new")
    generate_reports(older, project_dir=tmp_path)
    generate_reports(newer, project_dir=tmp_path)

    latest_json = resolve_report_json(project_dir=tmp_path, run="latest")
    metadata, html_path = regenerate_html_for_run(project_dir=tmp_path, run="latest")

    assert latest_json.name == "run-20260102T000000Z-new.json"
    assert metadata.run_id == "run-20260102T000000Z-new"
    assert html_path.is_file()


def test_run_dry_run_generates_metadata_reports_and_report_command(
    tmp_path: Path,
    monkeypatch,
) -> None:
    create_project("demo", base_dir=tmp_path)
    project_dir = tmp_path / "demo"
    (project_dir / "data" / "raw" / "sample.fastq").write_text("ACGT", encoding="utf-8")
    monkeypatch.chdir(project_dir)

    run_result = runner.invoke(app, ["run", "--dry-run"])
    report_result = runner.invoke(app, ["report", "--run", "latest"])

    assert run_result.exit_code == 0
    assert report_result.exit_code == 0
    reports = sorted((project_dir / "reports").glob("run-*.*"))
    assert any(path.suffix == ".json" for path in reports)
    assert any(path.suffix == ".html" for path in reports)
    json_text = next(path for path in reports if path.suffix == ".json").read_text(
        encoding="utf-8"
    )
    assert '"status": "SUCCEEDED"' in json_text
    assert '"sha256"' in json_text


def test_failed_execution_generates_failed_report(tmp_path: Path) -> None:
    create_project("demo", base_dir=tmp_path)
    project_dir = tmp_path / "demo"
    completed = CompletedProcess(args=["nextflow"], returncode=2, stdout="", stderr="bad")

    with patch("biostack.core.runner.subprocess.run", return_value=completed):
        try:
            run_workflow(project_dir=project_dir, workflow="rnaseq-basic", profile="local")
        except Exception:
            pass

    json_report = next((project_dir / "reports").glob("run-*.json"))
    assert '"status": "FAILED"' in json_report.read_text(encoding="utf-8")
