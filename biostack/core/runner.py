"""Nextflow command construction and execution helpers."""

from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from biostack.core.config import BioStackConfig, load_project_config


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
    """Structured result returned by the BioStack workflow runner."""

    run_id: str
    command: list[str]
    log_path: Path
    project_dir: Path
    workflow_name: str
    profile: str
    dry_run: bool
    return_code: int | None = None

    @property
    def command_text(self) -> str:
        """Return shell-escaped command text for display and logs."""
        return shlex.join(self.command)


def generate_run_id() -> str:
    """Generate a unique, sortable run identifier."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = uuid4().hex[:8]
    return f"run-{timestamp}-{suffix}"


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


def _write_log_header(log_path: Path, result: RunResult, config: BioStackConfig) -> None:
    """Write an auditable log header before dry-run or real execution."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        "\n".join(
            [
                "BioStack workflow run",
                f"run_id={result.run_id}",
                f"project={config.project.name}",
                f"workflow={result.workflow_name}",
                f"profile={result.profile}",
                f"dry_run={result.dry_run}",
                f"command={result.command_text}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def run_workflow(
    *,
    project_dir: Path | None = None,
    workflow: str | None = None,
    profile: str | None = None,
    dry_run: bool = False,
) -> RunResult:
    """Build and optionally execute a configured Nextflow workflow."""
    resolved_project_dir = (project_dir or Path.cwd()).resolve()
    config_path = find_project_config(resolved_project_dir)
    config = load_project_config(config_path)

    workflow_name = workflow or config.workflow.name
    selected_profile = profile or config.workflow.profile
    run_id = generate_run_id()
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

    result = RunResult(
        run_id=run_id,
        command=command,
        log_path=log_path,
        project_dir=resolved_project_dir,
        workflow_name=workflow_name,
        profile=selected_profile,
        dry_run=dry_run,
    )
    _write_log_header(log_path, result, config)

    if dry_run:
        return result

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
        raise NextflowNotAvailableError(
            "Nextflow não foi encontrado no PATH. Instale o Nextflow ou use "
            "'biostack run --dry-run' para auditar o comando sem executar."
        ) from exc

    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write("stdout:\n")
        log_file.write(completed.stdout or "")
        log_file.write("\nstderr:\n")
        log_file.write(completed.stderr or "")
        log_file.write(f"\nreturn_code={completed.returncode}\n")

    if completed.returncode != 0:
        raise RunnerError(
            f"Nextflow retornou código {completed.returncode}. Consulte o log em {log_path}."
        )

    return RunResult(
        run_id=run_id,
        command=command,
        log_path=log_path,
        project_dir=resolved_project_dir,
        workflow_name=workflow_name,
        profile=selected_profile,
        dry_run=dry_run,
        return_code=completed.returncode,
    )
