from pathlib import Path

from typer.testing import CliRunner

from biostack.core.config import load_project_config
from biostack.main import app

runner = CliRunner()

EXPECTED_DIRECTORIES = [
    "data/raw",
    "data/reference",
    "workflows",
    "results",
    "reports",
    "logs",
    "config",
]


def test_init_creates_project_structure_and_valid_config() -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["init", "demo", "--template", "rnaseq-basic"])

        assert result.exit_code == 0
        project_path = Path("demo")
        assert (project_path / "biostack.yml").is_file()
        assert (project_path / "README.md").is_file()

        for relative_dir in EXPECTED_DIRECTORIES:
            assert (project_path / relative_dir).is_dir()

        config = load_project_config(project_path / "biostack.yml")
        assert config.project.name == "demo"
        assert config.project.template == "rnaseq-basic"
        assert config.workflow.engine == "nextflow"
        assert config.reports.formats == ["html", "json"]


def test_init_refuses_to_overwrite_existing_project_without_force() -> None:
    with runner.isolated_filesystem():
        first = runner.invoke(app, ["init", "demo", "--template", "rnaseq-basic"])
        second = runner.invoke(app, ["init", "demo", "--template", "rnaseq-basic"])

        assert first.exit_code == 0
        assert second.exit_code == 1
        assert "Use --force" in second.output


def test_init_force_recreates_existing_project() -> None:
    with runner.isolated_filesystem():
        runner.invoke(app, ["init", "demo", "--template", "rnaseq-basic"])
        marker = Path("demo/results/old-result.txt")
        marker.write_text("stale", encoding="utf-8")

        result = runner.invoke(app, ["init", "demo", "--template", "rnaseq-basic", "--force"])

        assert result.exit_code == 0
        assert not marker.exists()
        assert (Path("demo") / "biostack.yml").is_file()


def test_init_rejects_unsupported_template() -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["init", "demo", "--template", "unknown"])

        assert result.exit_code == 1
        assert "não suportado" in result.output
