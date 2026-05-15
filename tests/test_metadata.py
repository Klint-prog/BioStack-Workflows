from datetime import timezone
from pathlib import Path

from biostack.core.metadata import (
    RunMetadata,
    collect_tool_versions,
    finalize_metadata,
    generate_run_id,
    utc_now,
)


def test_generate_run_id_is_prefixed_and_unique() -> None:
    first = generate_run_id()
    second = generate_run_id()

    assert first.startswith("run-")
    assert second.startswith("run-")
    assert first != second


def test_collect_tool_versions_is_tolerant() -> None:
    versions = collect_tool_versions()

    assert versions.biostack
    assert versions.python
    assert versions.operating_system


def test_finalize_metadata_adds_duration_and_log_text(tmp_path: Path) -> None:
    log_path = tmp_path / "run.log"
    log_path.write_text("hello log", encoding="utf-8")
    metadata = RunMetadata(
        run_id="run-test",
        started_at=utc_now(),
        workflow="rnaseq-basic",
        profile="local",
        command=["nextflow", "run"],
        status="SUCCEEDED",
        versions=collect_tool_versions(),
        log_path=log_path.as_posix(),
    )

    finalized = finalize_metadata(metadata, status="FAILED", log_path=log_path, error="boom")

    assert finalized.finished_at is not None
    assert finalized.finished_at.tzinfo == timezone.utc
    assert finalized.duration_seconds is not None
    assert finalized.status == "FAILED"
    assert finalized.log_text == "hello log"
    assert finalized.error == "boom"
