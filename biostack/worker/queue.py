"""Simple Redis list based queue for BioStack worker jobs."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Any, Protocol
from uuid import uuid4

DEFAULT_REDIS_URL = "redis://redis:6379/0"
DEFAULT_QUEUE_NAME = "biostack:runs"


class QueueClient(Protocol):
    """Minimal Redis client protocol used by the queue helpers and tests."""

    def lpush(self, name: str, value: str) -> Any: ...

    def brpop(self, keys: str | list[str], timeout: int = 0) -> Any: ...


@dataclass(frozen=True)
class RunJob:
    """Serialized job payload consumed by the worker."""

    job_id: str
    database_id: str
    project_name: str
    project_path: str
    workflow: str | None
    profile: str | None
    dry_run: bool


def get_redis_url() -> str:
    """Return the configured Redis URL."""
    return os.getenv("BIOSTACK_REDIS_URL", DEFAULT_REDIS_URL)


def get_queue_name() -> str:
    """Return the configured Redis queue name."""
    return os.getenv("BIOSTACK_QUEUE_NAME", DEFAULT_QUEUE_NAME)


def create_redis_client(url: str | None = None) -> Any:
    """Create a Redis client lazily so tests can avoid importing Redis."""
    from redis import Redis

    return Redis.from_url(url or get_redis_url(), decode_responses=True)


def serialize_job(job: RunJob) -> str:
    """Serialize a job as deterministic JSON."""
    return json.dumps(asdict(job), sort_keys=True)


def deserialize_job(payload: str | bytes) -> RunJob:
    """Deserialize one queued job payload."""
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")
    data = json.loads(payload)
    return RunJob(**data)


def enqueue_run_job(
    *,
    database_id: str,
    project_name: str,
    project_path: str,
    workflow: str | None,
    profile: str | None,
    dry_run: bool,
    redis_client: QueueClient | None = None,
    queue_name: str | None = None,
) -> RunJob:
    """Push a run job to the Redis list queue."""
    job = RunJob(
        job_id=f"job-{uuid4()}",
        database_id=database_id,
        project_name=project_name,
        project_path=project_path,
        workflow=workflow,
        profile=profile,
        dry_run=dry_run,
    )
    client = redis_client or create_redis_client()
    client.lpush(queue_name or get_queue_name(), serialize_job(job))
    return job


def pop_run_job(
    *,
    redis_client: QueueClient | None = None,
    queue_name: str | None = None,
    timeout: int = 5,
) -> RunJob | None:
    """Pop one run job from the queue, blocking for timeout seconds."""
    client = redis_client or create_redis_client()
    item = client.brpop(queue_name or get_queue_name(), timeout=timeout)
    if item is None:
        return None
    _queue, payload = item
    return deserialize_job(payload)
