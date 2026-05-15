from pathlib import Path

from biostack.core.checksums import collect_input_checksums, sha256_file


def test_sha256_file_streams_expected_digest(tmp_path: Path) -> None:
    sample = tmp_path / "sample.fastq"
    sample.write_text("ACGT\n", encoding="utf-8")

    assert sha256_file(sample) == "a4b0723993d3751f3d530e3c20da4c24ccdd32e65820fba897cc5f119e85ca55"


def test_collect_input_checksums_is_sorted_and_project_relative(tmp_path: Path) -> None:
    project = tmp_path / "project"
    raw = project / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / "b.fastq").write_text("B", encoding="utf-8")
    (raw / "a.fq").write_text("A", encoding="utf-8")
    (raw / "ignore.txt").write_text("x", encoding="utf-8")

    checksums = collect_input_checksums(raw, project_dir=project)

    assert [item.path for item in checksums] == ["data/raw/a.fq", "data/raw/b.fastq"]
    assert all(len(item.sha256) == 64 for item in checksums)
    assert [item.size_bytes for item in checksums] == [1, 1]
