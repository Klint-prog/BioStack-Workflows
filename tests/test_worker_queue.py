"""Tests for the phase_12 Redis queue helpers."""

from __future__ import annotations

from biostack.worker.queue import deserialize_job, enqueue_run_job, pop_run_job, serialize_job


class FakeRedis:
    """Small in-memory fake implementing the Redis list methods used by the queue."""

    def __init__(self) -> None:
        self.items: list[tuple[str, str]] = []

    def lpush(self, name: str, value: str) -> int:
        self.items.insert(0, (name, value))
        return len(self.items)

    def brpop(self, keys: str | list[str], timeout: int = 0):  # noqa: ANN001
        if not self.items:
            return None
        return self.items.pop()


def test_enqueue_and_pop_run_job_roundtrip() -> None:
    redis = FakeRedis()

    job = enqueue_run_job(
        database_id="run-db-id",
        project_name="demo",
        project_path="/workspace/demo",
        workflow="rnaseq-basic",
        profile="docker",
        dry_run=True,
        redis_client=redis,
        queue_name="test:runs",
    )

    assert job.job_id.startswith("job-")
    popped = pop_run_job(redis_client=redis, queue_name="test:runs", timeout=0)
    assert popped == job


def test_job_serialization_is_json_roundtrippable() -> None:
    redis = FakeRedis()
    job = enqueue_run_job(
        database_id="abc",
        project_name="demo",
        project_path="/tmp/demo",
        workflow=None,
        profile=None,
        dry_run=False,
        redis_client=redis,
        queue_name="test:runs",
    )

    payload = serialize_job(job)
    restored = deserialize_job(payload)

    assert restored == job
