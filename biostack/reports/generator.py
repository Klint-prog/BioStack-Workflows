"""JSON and HTML report generation for BioStack runs."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from biostack.core.metadata import RunMetadata


class ReportNotFoundError(RuntimeError):
    """Raised when a requested run report cannot be found."""


def _template_environment() -> Environment:
    template_root = files("biostack.templates")
    return Environment(
        loader=FileSystemLoader(str(template_root)),
        autoescape=select_autoescape(["html", "xml"]),
        keep_trailing_newline=True,
    )


def report_paths(project_dir: Path, run_id: str, reports_dir: str = "reports") -> tuple[Path, Path]:
    """Return JSON and HTML report paths for a run."""
    root = project_dir / reports_dir
    return root / f"{run_id}.json", root / f"{run_id}.html"


def write_json_report(metadata: RunMetadata, json_path: Path) -> Path:
    """Persist metadata as pretty JSON."""
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(metadata.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return json_path


def write_html_report(metadata: RunMetadata, html_path: Path) -> Path:
    """Render a human-readable HTML report from metadata."""
    html_path.parent.mkdir(parents=True, exist_ok=True)
    template = _template_environment().get_template("report.html.j2")
    html_path.write_text(
        template.render(metadata=metadata, command_text=" ".join(metadata.command)),
        encoding="utf-8",
    )
    return html_path


def generate_reports(
    metadata: RunMetadata,
    *,
    project_dir: Path,
    reports_dir: str = "reports",
) -> tuple[Path, Path]:
    """Generate JSON and HTML reports for a run."""
    json_path, html_path = report_paths(project_dir, metadata.run_id, reports_dir)
    write_json_report(metadata, json_path)
    write_html_report(metadata, html_path)
    return json_path, html_path


def load_metadata_report(json_path: Path) -> RunMetadata:
    """Load a RunMetadata object from a JSON report."""
    return RunMetadata.model_validate_json(json_path.read_text(encoding="utf-8"))


def resolve_report_json(
    *,
    project_dir: Path,
    run: str,
    reports_dir: str = "reports",
) -> Path:
    """Resolve a run id or latest into a deterministic JSON report path."""
    reports_root = project_dir / reports_dir
    if run != "latest":
        candidate = reports_root / f"{run}.json"
        if candidate.is_file():
            return candidate
        raise ReportNotFoundError(f"Relatório JSON não encontrado para run '{run}'.")

    candidates = sorted(reports_root.glob("run-*.json"))
    if not candidates:
        raise ReportNotFoundError("Nenhum relatório encontrado em reports/.")

    def sort_key(path: Path) -> tuple[str, str]:
        try:
            metadata = load_metadata_report(path)
            started_at = metadata.started_at.isoformat()
        except Exception:
            started_at = ""
        return started_at, path.name

    return sorted(candidates, key=sort_key)[-1]


def regenerate_html_for_run(
    *,
    project_dir: Path,
    run: str,
    reports_dir: str = "reports",
) -> tuple[RunMetadata, Path]:
    """Resolve a run, load metadata and write the corresponding HTML report."""
    json_path = resolve_report_json(project_dir=project_dir, run=run, reports_dir=reports_dir)
    metadata = load_metadata_report(json_path)
    _, html_path = report_paths(project_dir, metadata.run_id, reports_dir)
    write_html_report(metadata, html_path)
    return metadata, html_path
