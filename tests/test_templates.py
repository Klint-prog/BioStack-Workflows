from pathlib import Path

from typer.testing import CliRunner

from biostack.core.config import SUPPORTED_TEMPLATES, load_project_config
from biostack.main import app

runner = CliRunner()

EXPECTED_TEMPLATES = {"rnaseq-basic", "variant-calling-basic"}
EXPECTED_DIRECTORIES = [
    "data/raw",
    "data/reference",
    "workflows",
    "results",
    "reports",
    "logs",
    "config",
]


def test_supported_templates_are_declared() -> None:
    assert SUPPORTED_TEMPLATES == EXPECTED_TEMPLATES


def test_init_creates_valid_project_for_each_supported_template() -> None:
    with runner.isolated_filesystem():
        for template in sorted(EXPECTED_TEMPLATES):
            project_name = template.replace("-basic", "")
            result = runner.invoke(app, ["init", project_name, "--template", template])

            assert result.exit_code == 0
            project_path = Path(project_name)
            assert (project_path / "biostack.yml").is_file()
            assert (project_path / "README.md").is_file()

            for relative_dir in EXPECTED_DIRECTORIES:
                assert (project_path / relative_dir).is_dir()

            config = load_project_config(project_path / "biostack.yml")
            assert config.project.name == project_name
            assert config.project.template == template
            assert config.workflow.name == template
            assert config.workflow.engine == "nextflow"
            assert config.reports.formats == ["html", "json"]


def test_variant_calling_template_is_explicitly_supported_by_cli() -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["init", "demo-vc", "--template", "variant-calling-basic"])

        assert result.exit_code == 0
        config = load_project_config(Path("demo-vc/biostack.yml"))
        assert config.project.template == "variant-calling-basic"
        assert config.workflow.name == "variant-calling-basic"
