"""Nextflow command construction and execution helpers."""

from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

from biostack.core.checksums import collect_input_checksums
from biostack.core.config import BioStackConfig, load_project_config
from biostack.core.metadata import (
    RunMetadata,
    collect_tool_versions,
    finalize_metadata,
    generate_run_id,
    utc_now,
)
from biostack.reports.generator import generate_reports


class RunnerError(RuntimeError):
    """Base exception for workflow runner failures."""


class ProjectConfigNotFoundError(RunnerError):
    """Raised when biostack.yml is absent from the project root."""


class WorkflowNotFoundError(RunnerError):
    """Raised when the requested workflow cannot be resolved."""


class NextflowNotAvailableError(RunnerError):
    """Raised when Nextflow is not available during real execution."""


@dataclass(frozen=True)
class RunResult:
    """Structured result returned after running or simulating a workflow."""

    run_id: str
    command: list[str]
    log_path: Path
    project_dir: Path
    workflow_name: str
    profile: str
    dry_run: bool
    report_json_path: Path
    report_html_path: Path
    return_code: int | None = None

    @property
    def command_text(self) -> str:
        """Return shell-escaped command text for display and logs."""
        return shlex.join(self.command)


def find_project_config(project_dir: Path) -> Path:
    """Locate biostack.yml in the current BioStack project directory."""
    config_path = project_dir / "biostack.yml"
    if not config_path.is_file():
        raise ProjectConfigNotFoundError(
            "Arquivo biostack.yml não encontrado no diretório atual. "
            "Execute este comando dentro de um projeto criado com 'biostack init'."
        )
    return config_path


def resolve_workflow_path(project_dir: Path, workflow_name: str, storage_workflows: str) -> Path:
    """Resolve a workflow path from project-local or repository-bundled workflows."""
    project_workflow = project_dir / storage_workflows / workflow_name
    if (project_workflow / "main.nf").is_file():
        return project_workflow

    package_root = Path(__file__).resolve().parents[2]
    bundled_workflow = package_root / "workflows" / workflow_name
    if (bundled_workflow / "main.nf").is_file():
        return bundled_workflow

    raise WorkflowNotFoundError(
        f"Workflow '{workflow_name}' não encontrado. Caminhos verificados: "
        f"{project_workflow} e {bundled_workflow}."
    )


def build_nextflow_command(
    *,
    workflow_path: Path,
    profile: str,
    project_dir: Path,
    run_id: str,
) -> list[str]:
    """Build a Nextflow command using an argument list instead of shell interpolation."""
    return [
        "nextflow",
        "run",
        str(workflow_path),
        "-profile",
        profile,
        "--input",
        str(project_dir / "data" / "raw"),
        "--outdir",
        str(project_dir / "results" / run_id),
        "--run_id",
        run_id,
    ]


def _write_log_header(
    log_path: Path,
    config: BioStackConfig,
    command_text: str,
    run_id: str,
    workflow: str,
    profile: str,
    dry_run: bool,
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        "\n".join(
            [
                "BioStack workflow run",
                f"run_id={run_id}",
                f"project={config.project.name}",
                f"workflow={workflow}",
                f"profile={profile}",
                f"dry_run={dry_run}",
                f"command={command_text}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _initial_metadata(
    *,
    run_id: str,
    command: list[str],
    workflow: str,
    profile: str,
    dry_run: bool,
    project_dir: Path,
    log_path: Path,
) -> RunMetadata:
    input_dir = project_dir / "data" / "raw"
    return RunMetadata(
        run_id=run_id,
        started_at=utc_now(),
        workflow=workflow,
        profile=profile,
        command=command,
        status="SUCCEEDED",
        dry_run=dry_run,
        parameters={
            "input": str(input_dir),
            "outdir": str(project_dir / "results" / run_id),
            "run_id": run_id,
        },
        versions=collect_tool_versions(),
        input_checksums=collect_input_checksums(input_dir, project_dir=project_dir),
        log_path=log_path.as_posix(),
    )


def _write_reports(
    metadata: RunMetadata,
    *,
    project_dir: Path,
    reports_dir: str,
    status: str,
    return_code: int | None = None,
    log_path: Path | None = None,
    error: str | None = None,
) -> tuple[Path, Path]:
    finalized = finalize_metadata(
        metadata,
        status=status,  # type: ignore[arg-type]
        return_code=return_code,
        log_path=log_path,
        error=error,
    )
    return generate_reports(finalized, project_dir=project_dir, reports_dir=reports_dir)


def run_workflow(
    *,
    project_dir: Path | None = None,
    workflow: str | None = None,
    profile: str | None = None,
    dry_run: bool = False,
) -> RunResult:
    """Build and optionally execute a configured Nextflow workflow."""
    return run_workflow_with_run_id(
        project_dir=project_dir,
        workflow=workflow,
        profile=profile,
        dry_run=dry_run,
    )


def run_workflow_with_run_id(
    *,
    project_dir: Path | None = None,
    workflow: str | None = None,
    profile: str | None = None,
    dry_run: bool = False,
    run_id_override: str | None = None,
) -> RunResult:
    """Run a workflow, optionally reusing a pre-created run id for async jobs."""
    resolved_project_dir = (project_dir or Path.cwd()).resolve()
    config = load_project_config(find_project_config(resolved_project_dir))
    workflow_name = workflow or config.workflow.name
    selected_profile = profile or config.workflow.profile
    run_id = run_id_override or generate_run_id()
    workflow_path = resolve_workflow_path(
        resolved_project_dir,
        workflow_name,
        config.storage.workflows,
    )
    command = build_nextflow_command(
        workflow_path=workflow_path,
        profile=selected_profile,
        project_dir=resolved_project_dir,
        run_id=run_id,
    )
    log_path = resolved_project_dir / config.storage.logs / f"{run_id}.log"
    command_text = shlex.join(command)
    _write_log_header(
        log_path,
        config,
        command_text,
        run_id,
        workflow_name,
        selected_profile,
        dry_run,
    )
    metadata = _initial_metadata(
        run_id=run_id,
        command=command,
        workflow=workflow_name,
        profile=selected_profile,
        dry_run=dry_run,
        project_dir=resolved_project_dir,
        log_path=log_path,
    )

    if dry_run:
        json_path, html_path = _write_reports(
            metadata,
            project_dir=resolved_project_dir,
            reports_dir=config.storage.reports,
            status="SUCCEEDED",
            log_path=log_path,
        )
        return RunResult(
            run_id,
            command,
            log_path,
            resolved_project_dir,
            workflow_name,
            selected_profile,
            dry_run,
            json_path,
            html_path,
        )

    try:
        completed = subprocess.run(
            command,
            cwd=resolved_project_dir,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write("Erro: Nextflow não encontrado no PATH.\n")
        json_path, html_path = _write_reports(
            metadata,
            project_dir=resolved_project_dir,
            reports_dir=config.storage.reports,
            status="FAILED",
            log_path=log_path,
            error="Nextflow não encontrado no PATH.",
        )
        raise NextflowNotAvailableError(
            "Nextflow não foi encontrado no PATH. Instale o Nextflow ou use "
            "'biostack run --dry-run' para auditar o comando sem executar. "
            f"Relatório gerado em {json_path} e {html_path}."
        ) from exc

    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write("stdout:\n")
        log_file.write(completed.stdout or "")
        log_file.write("\nstderr:\n")
        log_file.write(completed.stderr or "")
        log_file.write(f"\nreturn_code={completed.returncode}\n")

    status = "SUCCEEDED" if completed.returncode == 0 else "FAILED"
    error = None
    if completed.returncode != 0:
        error = f"Nextflow retornou código {completed.returncode}."

    json_path, html_path = _write_reports(
        metadata,
        project_dir=resolved_project_dir,
        reports_dir=config.storage.reports,
        status=status,
        return_code=completed.returncode,
        log_path=log_path,
        error=error,
    )
    if completed.returncode != 0:
        raise RunnerError(
            f"Nextflow retornou código {completed.returncode}. Consulte o log em "
            f"{log_path}. Relatório gerado em {json_path}."
        )

    return RunResult(
        run_id=run_id,
        command=command,
        log_path=log_path,
        project_dir=resolved_project_dir,
        workflow_name=workflow_name,
        profile=selected_profile,
        dry_run=dry_run,
        report_json_path=json_path,
        report_html_path=html_path,
        return_code=completed.returncode,
    )
