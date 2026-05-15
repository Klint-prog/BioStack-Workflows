"""Tests for the versioned API healthcheck."""

from __future__ import annotations

from fastapi.testclient import TestClient

from biostack.api.app import create_app


def test_api_health_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
