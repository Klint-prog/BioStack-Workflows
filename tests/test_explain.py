from pathlib import Path

from typer.testing import CliRunner

from biostack.core.project import create_project
from biostack.core.runner import run_workflow
from biostack.main import app

runner = CliRunner()


def test_explain_latest_with_mock_provider(tmp_path: Path, monkeypatch) -> None:
    create_project("demo", base_dir=tmp_path)
    project_dir = tmp_path / "demo"
    (project_dir / "data" / "raw" / "sample.fastq").write_text("ACGT", encoding="utf-8")
    run_workflow(project_dir=project_dir, dry_run=True)
    monkeypatch.chdir(project_dir)

    result = runner.invoke(app, ["explain", "--run", "latest", "--provider", "mock"])

    assert result.exit_code == 0
    assert "AVISO: Não usar para diagnóstico ou interpretação clínica." in result.output
    assert "Run analisado:" in result.output
    assert "Resumo operacional gerado por provider fake." in result.output


def test_explain_without_api_key_fails_friendly(tmp_path: Path, monkeypatch) -> None:
    create_project("demo", base_dir=tmp_path)
    project_dir = tmp_path / "demo"
    run_workflow(project_dir=project_dir, dry_run=True)
    monkeypatch.chdir(project_dir)
    monkeypatch.delenv("BIOSTACK_LLM_API_KEY", raising=False)

    result = runner.invoke(app, ["explain", "--run", "latest"])

    assert result.exit_code == 1
    assert "AVISO: Não usar para diagnóstico ou interpretação clínica." in result.output
    assert "Provider de IA não configurado" in result.output
    assert "Traceback" not in result.output


def test_explain_missing_report_fails_friendly(tmp_path: Path, monkeypatch) -> None:
    create_project("demo", base_dir=tmp_path)
    monkeypatch.chdir(tmp_path / "demo")

    result = runner.invoke(app, ["explain", "--run", "latest", "--provider", "mock"])

    assert result.exit_code == 1
    assert "AVISO: Não usar para diagnóstico ou interpretação clínica." in result.output
    assert "Nenhum relatório encontrado" in result.output
    assert "Traceback" not in result.output
