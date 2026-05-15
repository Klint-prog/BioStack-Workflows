"""SHA256 checksum helpers for BioStack input files."""

from __future__ import annotations

import hashlib
from pathlib import Path

from pydantic import BaseModel, Field

DEFAULT_INPUT_PATTERNS = ("*.fastq", "*.fq", "*.fastq.gz", "*.fq.gz")
CHUNK_SIZE = 1024 * 1024


class FileChecksum(BaseModel):
    """Checksum metadata for one input file."""

    path: str = Field(description="Project-relative file path when possible.")
    sha256: str
    size_bytes: int


def sha256_file(path: Path, *, chunk_size: int = CHUNK_SIZE) -> str:
    """Calculate a SHA256 digest using streaming reads for large files."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_input_checksums(
    input_dir: Path,
    *,
    project_dir: Path | None = None,
    patterns: tuple[str, ...] = DEFAULT_INPUT_PATTERNS,
) -> list[FileChecksum]:
    """Collect deterministic SHA256 checksums for configured input files."""
    if not input_dir.exists():
        return []

    root = project_dir or input_dir.parent
    files: dict[Path, None] = {}
    for pattern in patterns:
        for candidate in input_dir.rglob(pattern):
            if candidate.is_file():
                files[candidate.resolve()] = None

    checksums: list[FileChecksum] = []
    for file_path in sorted(files):
        try:
            display_path = file_path.relative_to(root.resolve()).as_posix()
        except ValueError:
            display_path = file_path.as_posix()
        checksums.append(
            FileChecksum(
                path=display_path,
                sha256=sha256_file(file_path),
                size_bytes=file_path.stat().st_size,
            )
        )
    return checksums
