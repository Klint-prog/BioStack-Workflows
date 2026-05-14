from typer.testing import CliRunner

from biostack import __version__
from biostack.main import app

runner = CliRunner()


def test_help_displays_available_commands() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "version" in result.output
    assert "doctor" in result.output


def test_version_command_uses_centralized_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert __version__ in result.output


def test_doctor_does_not_fail_without_external_tools() -> None:
    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "Python" in result.output
    assert "docker" in result.output
    assert "nextflow" in result.output
