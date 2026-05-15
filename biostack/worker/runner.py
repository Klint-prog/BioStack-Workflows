"""Worker runner for asynchronous BioStack workflow execution."""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

from biostack.core.runner import RunnerError, run_workflow_with_run_id
from biostack.db.repositories import (
    complete_run_record,
    get_run_by_database_id,
    update_run_status,
)
from biostack.db.session import session_scope
from biostack.reports.generator import load_metadata_report
from biostack.worker.queue import RunJob, pop_run_job

logger = logging.getLogger("biostack.worker")


def configure_logging() -> None:
    """Configure predictable container-friendly logging for the worker."""
    log_level = os.getenv("BIOSTACK_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def process_run_job(job: RunJob, *, database_url: str | None = None) -> None:
    """Execute one queued run job and persist lifecycle transitions."""
    logger.info("Processing run job %s for database_id=%s", job.job_id, job.database_id)
    with session_scope(database_url) as session:
        run = get_run_by_database_id(session, job.database_id)
        if run is None:
            raise RuntimeError(f"Run database_id={job.database_id} não encontrada.")
        queued_run_id = run.run_id
        update_run_status(
            session,
            run=run,
            status="RUNNING",
            message=f"Worker iniciou processamento do job {job.job_id}.",
            payload={"job_id": job.job_id},
        )

    try:
        result = run_workflow_with_run_id(
            project_dir=Path(job.project_path),
            workflow=job.workflow,
            profile=job.profile,
            dry_run=job.dry_run,
            run_id_override=queued_run_id,
        )
        metadata = load_metadata_report(result.report_json_path)
        status = "SUCCEEDED" if (result.return_code in (None, 0)) else "FAILED"
        with session_scope(database_url) as session:
            run = get_run_by_database_id(session, job.database_id)
            if run is None:
                raise RuntimeError(f"Run database_id={job.database_id} não encontrada.")
            complete_run_record(
                session,
                run=run,
                command=result.command,
                return_code=result.return_code,
                log_path=result.log_path.as_posix(),
                report_json_path=result.report_json_path.as_posix(),
                report_html_path=result.report_html_path.as_posix(),
                metadata=json.loads(metadata.model_dump_json()),
                status=status,
            )
        logger.info("Completed run job %s with status=%s", job.job_id, status)
    except Exception as exc:
        logger.exception("Failed to process run job %s", job.job_id)
        with session_scope(database_url) as session:
            run = get_run_by_database_id(session, job.database_id)
            if run is not None:
                update_run_status(
                    session,
                    run=run,
                    status="FAILED",
                    message=f"Worker falhou ao processar o job {job.job_id}: {exc}",
                    payload={"job_id": job.job_id, "error": str(exc)},
                )
        if isinstance(exc, RunnerError):
            return
        raise


def run_worker_loop(*, once: bool = False, poll_timeout: int = 5) -> None:
    """Run the worker loop and process queued jobs."""
    logger.info("BioStack worker started once=%s poll_timeout=%s", once, poll_timeout)
    while True:
        job = pop_run_job(timeout=poll_timeout)
        if job is not None:
            process_run_job(job)
        if once:
            break
        if job is None:
            time.sleep(1)


def main() -> None:
    """Entrypoint used by the biostack-worker console script."""
    configure_logging()
    run_worker_loop()


if __name__ == "__main__":
    main()
