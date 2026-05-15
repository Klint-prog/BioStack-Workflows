"""Execution metadata models and collectors for BioStack runs."""

from __future__ import annotations

import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from subprocess import run as subprocess_run
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from biostack import __version__
from biostack.core.checksums import FileChecksum

RunStatus = Literal["SUCCEEDED", "FAILED"]


class ToolVersions(BaseModel):
    """Tool and environment versions captured for auditability."""

    biostack: str
    python: str
    operating_system: str
    docker: str | None = None
    nextflow: str | None = None


class RunMetadata(BaseModel):
    """Auditable metadata for one BioStack workflow execution."""

    run_id: str
    started_at: datetime
    finished_at: datetime | None = None
    duration_seconds: float | None = None
    workflow: str
    profile: str
    command: list[str]
    status: RunStatus
    dry_run: bool = False
    return_code: int | None = None
    parameters: dict[str, str] = Field(default_factory=dict)
    versions: ToolVersions
    input_checksums: list[FileChecksum] = Field(default_factory=list)
    log_path: str | None = None
    log_text: str = ""
    error: str | None = None


def generate_run_id() -> str:
    """Generate a unique, time-sortable run identifier."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = uuid4().hex[:8]
    return f"run-{timestamp}-{suffix}"


def utc_now() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


def _probe_command(executable: str, args: list[str]) -> str | None:
    """Return a compact version string for an executable, or None if unavailable."""
    if shutil.which(executable) is None:
        return None
    try:
        completed = subprocess_run(
            [executable, *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = (completed.stdout or completed.stderr).strip()
    return output.splitlines()[0] if output else None


def collect_tool_versions() -> ToolVersions:
    """Collect versions without failing when optional tools are absent."""
    return ToolVersions(
        biostack=__version__,
        python=platform.python_version(),
        operating_system=f"{platform.system()} {platform.release()} ({platform.machine()})",
        docker=_probe_command("docker", ["--version"]),
        nextflow=_probe_command("nextflow", ["-version"]),
    )


def finalize_metadata(
    metadata: RunMetadata,
    *,
    status: RunStatus,
    finished_at: datetime | None = None,
    return_code: int | None = None,
    log_path: Path | None = None,
    error: str | None = None,
) -> RunMetadata:
    """Return metadata with finish timestamp, duration, logs and final status."""
    resolved_finished_at = finished_at or utc_now()
    resolved_log_path = log_path or (Path(metadata.log_path) if metadata.log_path else None)
    log_text = metadata.log_text
    if resolved_log_path and resolved_log_path.is_file():
        log_text = resolved_log_path.read_text(encoding="utf-8", errors="replace")

    return metadata.model_copy(
        update={
            "finished_at": resolved_finished_at,
            "duration_seconds": round(
                (resolved_finished_at - metadata.started_at).total_seconds(), 6
            ),
            "status": status,
            "return_code": return_code,
            "log_path": resolved_log_path.as_posix() if resolved_log_path else metadata.log_path,
            "log_text": log_text,
            "error": error,
        }
    )
