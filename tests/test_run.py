from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from typer.testing import CliRunner

from biostack.core.project import create_project
from biostack.core.runner import build_nextflow_command, run_workflow
from biostack.main import app

runner = CliRunner()


def test_build_nextflow_command_uses_argument_list() -> None:
    command = build_nextflow_command(
        workflow_path=Path("/repo/workflows/rnaseq-basic"),
        profile="local",
        project_dir=Path("/project"),
        run_id="run-123",
    )

    assert command == [
        "nextflow",
        "run",
        "/repo/workflows/rnaseq-basic",
        "-profile",
        "local",
        "--input",
        "/project/data/raw",
        "--outdir",
        "/project/results/run-123",
        "--run_id",
        "run-123",
    ]


def test_run_dry_run_uses_project_config_and_creates_log(tmp_path, monkeypatch) -> None:
    create_project("demo", base_dir=tmp_path)
    project_dir = tmp_path / "demo"
    monkeypatch.chdir(project_dir)

    result = runner.invoke(app, ["run", "--dry-run"])

    assert result.exit_code == 0
    assert "Dry-run" in result.output
    assert "nextflow run" in result.output
    logs = list((project_dir / "logs").glob("run-*.log"))
    assert len(logs) == 1
    assert "dry_run=True" in logs[0].read_text(encoding="utf-8")


def test_run_dry_run_accepts_workflow_and_profile_options(tmp_path, monkeypatch) -> None:
    create_project("demo", base_dir=tmp_path)
    project_dir = tmp_path / "demo"
    monkeypatch.chdir(project_dir)

    result = runner.invoke(
        app,
        ["run", "--dry-run", "--workflow", "rnaseq-basic", "--profile", "local"],
    )

    assert result.exit_code == 0
    assert "Workflow: rnaseq-basic" in result.output
    assert "Profile: local" in result.output
    assert "-profile local" in result.output


def test_run_reports_missing_project_config_without_traceback(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["run", "--dry-run"])

    assert result.exit_code == 1
    assert "biostack.yml não encontrado" in result.output
    assert "Traceback" not in result.output


def test_run_real_execution_uses_subprocess_and_writes_log(tmp_path) -> None:
    create_project("demo", base_dir=tmp_path)
    project_dir = tmp_path / "demo"

    completed = CompletedProcess(
        args=["nextflow"],
        returncode=0,
        stdout="ok\n",
        stderr="",
    )

    with patch("biostack.core.runner.subprocess.run", return_value=completed) as mocked_run:
        result = run_workflow(project_dir=project_dir, workflow="rnaseq-basic", profile="local")

    nextflow_calls = [call for call in mocked_run.call_args_list if call.args[0][0] == "nextflow"]
    assert len(nextflow_calls) == 1
    assert result.return_code == 0
    assert result.log_path.is_file()
    log_text = result.log_path.read_text(encoding="utf-8")
    assert "stdout:" in log_text
    assert "ok" in log_text


def test_run_missing_nextflow_returns_friendly_error(tmp_path, monkeypatch) -> None:
    create_project("demo", base_dir=tmp_path)
    project_dir = tmp_path / "demo"
    monkeypatch.chdir(project_dir)

    with patch("biostack.core.runner.subprocess.run", side_effect=FileNotFoundError):
        result = runner.invoke(app, ["run", "--workflow", "rnaseq-basic", "--profile", "local"])

    assert result.exit_code == 1
    assert "Nextflow não foi encontrado" in result.output
    assert "Traceback" not in result.output
