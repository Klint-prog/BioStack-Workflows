"""Explain routes for the versioned API."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from biostack.ai.prompts import CLINICAL_WARNING, build_troubleshooting_prompt
from biostack.ai.provider import ProviderConfigurationError, get_provider
from biostack.api.schemas.explain import ExplainRequest, ExplainResponse
from biostack.api.workspace import WorkspaceError, load_project
from biostack.reports.generator import (
    ReportNotFoundError,
    load_metadata_report,
    resolve_report_json,
)

MAX_LOG_CHARS = 12_000
router = APIRouter(prefix="/explain", tags=["explain"])


@router.post("", response_model=ExplainResponse)
def explain_run(payload: ExplainRequest) -> ExplainResponse:
    """Explain logs and metadata with the safe mock provider by default."""
    try:
        project_dir, config = load_project(payload.project_name)
        report_path = resolve_report_json(
            project_dir=project_dir,
            run=payload.run,
            reports_dir=config.storage.reports,
        )
        metadata = load_metadata_report(report_path)
        log_path = project_dir / metadata.log_path if metadata.log_path else None
        if log_path and log_path.is_file():
            log_text = log_path.read_text(encoding="utf-8", errors="replace")[-MAX_LOG_CHARS:]
        else:
            log_text = f"Log não encontrado no caminho registrado: {metadata.log_path}"
        metadata_json = json.dumps(metadata.model_dump(mode="json"), indent=2, ensure_ascii=False)
        prompt = build_troubleshooting_prompt(metadata_json=metadata_json, log_text=log_text)
        provider = get_provider(payload.provider)
        explanation = provider.explain(prompt)
    except WorkspaceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ReportNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProviderConfigurationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ExplainResponse(
        status="ok",
        project_name=config.project.name,
        run_id=metadata.run_id,
        provider=payload.provider,
        clinical_warning=CLINICAL_WARNING,
        explanation=explanation,
    )
