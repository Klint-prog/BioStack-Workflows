"""Configuration models and loaders for BioStack project files."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator

TemplateName = Literal["rnaseq-basic", "variant-calling-basic"]
SUPPORTED_TEMPLATES: set[str] = {"rnaseq-basic", "variant-calling-basic"}


class ProjectMetadata(BaseModel):
    """Project-level metadata stored in biostack.yml."""

    name: str = Field(min_length=1)
    template: TemplateName
    description: str = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Reject names that are empty after trimming."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("project name must not be blank")
        return normalized


class WorkflowConfig(BaseModel):
    """Workflow identity and engine configuration."""

    name: TemplateName
    engine: Literal["nextflow"] = "nextflow"
    profile: str = Field(default="docker", min_length=1)


class StorageConfig(BaseModel):
    """Local filesystem layout expected by the MVP."""

    raw_data: str = "data/raw"
    reference_data: str = "data/reference"
    workflows: str = "workflows"
    results: str = "results"
    reports: str = "reports"
    logs: str = "logs"
    config: str = "config"


class ReportConfig(BaseModel):
    """Report formats planned for generated runs."""

    formats: list[Literal["html", "json"]] = Field(default_factory=lambda: ["html", "json"])


class BioStackConfig(BaseModel):
    """Top-level schema for a BioStack project configuration file."""

    schema_version: str = "1.0"
    project: ProjectMetadata
    workflow: WorkflowConfig
    storage: StorageConfig = Field(default_factory=StorageConfig)
    reports: ReportConfig = Field(default_factory=ReportConfig)


def load_project_config(path: Path) -> BioStackConfig:
    """Load and validate a BioStack YAML configuration file."""
    with path.open("r", encoding="utf-8") as config_file:
        raw_data: Any = yaml.safe_load(config_file) or {}

    return BioStackConfig.model_validate(raw_data)
