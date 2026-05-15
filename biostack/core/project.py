"""Project scaffolding helpers for BioStack Workflows."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from biostack.core.config import SUPPORTED_TEMPLATES, BioStackConfig, load_project_config

DEFAULT_PROJECT_DIRECTORIES = (
    "data/raw",
    "data/reference",
    "workflows",
    "results",
    "reports",
    "logs",
    "config",
)


class ProjectCreationError(RuntimeError):
    """Base exception for project scaffolding failures."""


class ProjectAlreadyExistsError(ProjectCreationError):
    """Raised when the target project directory already exists."""


class UnsupportedTemplateError(ProjectCreationError):
    """Raised when a requested template is not available."""


@dataclass(frozen=True)
class CreatedProject:
    """Result returned after creating a project scaffold."""

    path: Path
    config: BioStackConfig


def _validate_project_directory_name(name: str) -> str:
    """Validate project names accepted by the CLI scaffolder."""
    normalized = name.strip()
    if not normalized:
        raise ProjectCreationError("O nome do projeto não pode ser vazio.")

    project_path = Path(normalized)
    if project_path.is_absolute() or project_path.name != normalized:
        raise ProjectCreationError(
            "Use um nome simples de diretório, sem caminho absoluto ou separadores."
        )

    if normalized in {".", ".."}:
        raise ProjectCreationError("Use um nome de projeto explícito, diferente de '.' ou '..'.")

    return normalized


def _remove_project_tree(project_path: Path) -> None:
    """Remove an existing project tree before a deliberate --force recreation."""
    for child in sorted(project_path.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if child.is_file() or child.is_symlink():
            child.unlink()
        elif child.is_dir():
            child.rmdir()
    project_path.rmdir()


def _template_environment() -> Environment:
    """Build a strict Jinja2 environment for bundled project templates."""
    template_root = files("biostack.templates")
    return Environment(
        loader=FileSystemLoader(str(template_root)),
        undefined=StrictUndefined,
        autoescape=select_autoescape(enabled_extensions=()),
        keep_trailing_newline=True,
    )


def _render_template(template_name: str, context: dict[str, str]) -> str:
    """Render a bundled template using the provided context."""
    environment = _template_environment()
    template = environment.get_template(template_name)
    return template.render(**context)


def create_project(
    name: str,
    template: str = "rnaseq-basic",
    *,
    force: bool = False,
    base_dir: Path | None = None,
) -> CreatedProject:
    """Create a reproducible BioStack project scaffold on the local filesystem."""
    if template not in SUPPORTED_TEMPLATES:
        available = ", ".join(sorted(SUPPORTED_TEMPLATES))
        raise UnsupportedTemplateError(
            f"Template '{template}' não suportado. Templates disponíveis: {available}."
        )

    project_name = _validate_project_directory_name(name)
    root_dir = base_dir or Path.cwd()
    project_path = root_dir / project_name

    if project_path.exists():
        if not force:
            raise ProjectAlreadyExistsError(
                f"O diretório '{project_path}' já existe. Use --force para recriar."
            )
        _remove_project_tree(project_path)

    project_path.mkdir(parents=True, exist_ok=False)

    for relative_dir in DEFAULT_PROJECT_DIRECTORIES:
        (project_path / relative_dir).mkdir(parents=True, exist_ok=True)

    context = {
        "project_name": project_name,
        "template": template,
        "description": f"Projeto BioStack criado a partir do template {template}.",
    }

    (project_path / "biostack.yml").write_text(
        _render_template("biostack.yml.j2", context),
        encoding="utf-8",
    )
    (project_path / "README.md").write_text(
        _render_template("project_README.md.j2", context),
        encoding="utf-8",
    )

    config = load_project_config(project_path / "biostack.yml")
    return CreatedProject(path=project_path, config=config)
