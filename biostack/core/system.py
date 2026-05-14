"""System and dependency detection helpers."""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class DiagnosticCheck:
    """Single environment diagnostic result."""

    name: str
    available: bool
    details: str


def get_python_details() -> DiagnosticCheck:
    """Return current Python runtime information."""
    version = platform.python_version()
    implementation = platform.python_implementation()
    minimum_supported = sys.version_info >= (3, 11)
    return DiagnosticCheck(
        name="Python",
        available=minimum_supported,
        details=f"{implementation} {version} ({sys.executable})",
    )


def get_operating_system_details() -> DiagnosticCheck:
    """Return operating system information."""
    return DiagnosticCheck(
        name="Sistema operacional",
        available=True,
        details=f"{platform.system()} {platform.release()} ({platform.machine()})",
    )


def detect_executable(name: str, version_args: tuple[str, ...] = ("--version",)) -> DiagnosticCheck:
    """Detect an executable and capture a compact version string when possible."""
    executable_path = shutil.which(name)
    if executable_path is None:
        return DiagnosticCheck(
            name=name,
            available=False,
            details=f"{name} não encontrado no PATH",
        )

    try:
        completed = subprocess.run(
            [executable_path, *version_args],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return DiagnosticCheck(
            name=name,
            available=True,
            details=f"{executable_path}; versão indisponível: {exc}",
        )

    output = (completed.stdout or completed.stderr).strip().splitlines()
    version = output[0] if output else "versão não informada"
    return DiagnosticCheck(
        name=name,
        available=True,
        details=f"{executable_path}; {version}",
    )


def collect_environment_diagnostics() -> list[DiagnosticCheck]:
    """Collect baseline diagnostics without requiring heavy external tools."""
    return [
        get_python_details(),
        get_operating_system_details(),
        detect_executable("docker"),
        detect_executable("nextflow", ("-version",)),
    ]
