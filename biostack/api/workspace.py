"""Filesystem helpers for the local-first BioStack API."""

from __future__ import annotations

import os
from pathlib import Path

from biostack.core.config import BioStackConfig, load_project_config


class WorkspaceError(RuntimeError):
    """Raised when a workspace or project path is invalid."""


def workspace_root() -> Path:
    """Return the API workspace root, defaulting to the current directory."""
    return Path(os.getenv("BIOSTACK_WORKSPACE", ".")).expanduser().resolve()


def validate_project_name(name: str) -> str:
    """Validate project names accepted by API endpoints."""
    normalized = name.strip()
    if not normalized:
        raise WorkspaceError("O nome do projeto não pode ser vazio.")
    project_path = Path(normalized)
    if project_path.is_absolute() or project_path.name != normalized:
        raise WorkspaceError("Use um nome simples de diretório, sem caminho ou separadores.")
    if normalized in {".", ".."}:
        raise WorkspaceError("Use um nome de projeto explícito, diferente de '.' ou '..'.")
    return normalized


def project_path(project_name: str) -> Path:
    """Resolve a project directory below the configured workspace."""
    return workspace_root() / validate_project_name(project_name)


def load_project(project_name: str) -> tuple[Path, BioStackConfig]:
    """Load a BioStack project by name from the workspace."""
    path = project_path(project_name)
    config_path = path / "biostack.yml"
    if not config_path.is_file():
        raise WorkspaceError(f"Projeto BioStack não encontrado: {project_name}.")
    return path, load_project_config(config_path)


def discover_project_configs() -> list[tuple[Path, BioStackConfig]]:
    """Discover valid BioStack projects in the workspace root and direct children."""
    root = workspace_root()
    root.mkdir(parents=True, exist_ok=True)
    candidates = [root]
    candidates.extend(
        path for path in sorted(root.iterdir()) if path.is_dir() and not path.name.startswith(".")
    )

    projects: list[tuple[Path, BioStackConfig]] = []
    for candidate in candidates:
        config_path = candidate / "biostack.yml"
        if not config_path.is_file():
            continue
        try:
            config = load_project_config(config_path)
        except Exception:
            continue
        projects.append((candidate, config))
    return sorted(projects, key=lambda item: (item[1].project.name, item[0].as_posix()))
