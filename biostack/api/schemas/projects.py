"""Project schemas for the versioned API."""

from __future__ import annotations

from pydantic import BaseModel, Field

from biostack.core.config import TemplateName


class ProjectCreateRequest(BaseModel):
    """Request body for creating a BioStack project."""

    name: str = Field(min_length=1)
    template: TemplateName = "rnaseq-basic"
    force: bool = False


class ProjectResponse(BaseModel):
    """Project summary returned by API endpoints."""

    name: str
    path: str
    template: str
    workflow: str
    reports_count: int


class ProjectCreateResponse(BaseModel):
    """Response returned after creating a project."""

    status: str
    project: ProjectResponse
