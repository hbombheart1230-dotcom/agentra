from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from libs.core import log_maintenance
from libs.core.log_maintenance import LogMoveCandidate, apply_log_move_candidates


def _candidate(source: str, target: str) -> LogMoveCandidate:
    return LogMoveCandidate(source, target, "test", "isolated boundary test")


def test_source_parent_escape_preserves_outside_file(tmp_path: Path) -> None:
    root = tmp_path / "logs"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("OUTSIDE-ORIGINAL", encoding="utf-8")
    before = hashlib.sha256(outside.read_bytes()).hexdigest()
    results = apply_log_move_candidates(root, [_candidate("../outside.txt", "dev/stolen.txt")])
    assert results == [{"src": str(root / "../outside.txt"), "dst": str(root / "dev/stolen.txt"), "category": "test", "status": "skipped_unsafe_path"}]
    assert hashlib.sha256(outside.read_bytes()).hexdigest() == before
    assert not (root / "dev/stolen.txt").exists()


def test_target_parent_escape_does_not_write_outside(tmp_path: Path) -> None:
    root = tmp_path / "logs"
    root.mkdir()
    source = root / "offhours_ok.txt"
    source.write_text("keep", encoding="utf-8")
    results = apply_log_move_candidates(root, [_candidate("offhours_ok.txt", "../created_outside.txt")])
    assert results[0]["status"] == "skipped_unsafe_path"
    assert source.read_text(encoding="utf-8") == "keep"
    assert not (tmp_path / "created_outside.txt").exists()


def test_target_symlink_parent_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "logs"
    root.mkdir()
    outside_dir = tmp_path / "outside_dir"
    outside_dir.mkdir()
    try:
        (root / "dev").symlink_to(outside_dir, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")
    source = root / "offhours_ok.txt"
    source.write_text("keep", encoding="utf-8")
    results = apply_log_move_candidates(root, [_candidate("offhours_ok.txt", "dev/analysis/offhours/offhours_ok.txt")])
    assert results[0]["status"] == "skipped_unsafe_path"
    assert source.read_text(encoding="utf-8") == "keep"
    assert list(outside_dir.iterdir()) == []


@pytest.mark.parametrize(
    "source,target",
    [
        ("/etc/passwd", "dev/stolen"),
        ("source", "/tmp/escape"),
        ("", "dev/out"),
        ("source", ""),
        (".", "dev/out"),
        ("source", "."),
    ],
)
def test_absolute_empty_or_root_paths_rejected(tmp_path: Path, source: str, target: str) -> None:
    root = tmp_path / "logs"
    root.mkdir()
    (root / "source").write_text("keep", encoding="utf-8")
    results = apply_log_move_candidates(root, [_candidate(source, target)])
    assert results[0]["status"] == "skipped_unsafe_path"
    assert (root / "source").read_text(encoding="utf-8") == "keep"


def test_unsafe_candidate_does_not_stop_valid_candidate(tmp_path: Path) -> None:
    root = tmp_path / "logs"
    root.mkdir()
    (root / "good").write_text("payload", encoding="utf-8")
    results = apply_log_move_candidates(root, [_candidate("../escape", "dev/no"), _candidate("good", "dev/good")])
    assert [item["status"] for item in results] == ["skipped_unsafe_path", "moved"]
    assert (root / "dev/good").read_text(encoding="utf-8") == "payload"


def test_existing_destination_is_preserved_and_batch_continues(tmp_path: Path) -> None:
    root = tmp_path / "logs"
    (root / "dev").mkdir(parents=True)
    (root / "a").write_text("source", encoding="utf-8")
    (root / "dev/a").write_text("existing", encoding="utf-8")
    (root / "b").write_text("move", encoding="utf-8")
    results = apply_log_move_candidates(root, [_candidate("a", "dev/a"), _candidate("b", "dev/b")])
    assert [item["status"] for item in results] == ["skipped_destination_exists", "moved"]
    assert (root / "dev/a").read_text(encoding="utf-8") == "existing"


def test_individual_move_error_does_not_stop_batch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "logs"
    root.mkdir()
    (root / "a").write_text("source", encoding="utf-8")
    (root / "b").write_text("move", encoding="utf-8")
    original_move = log_maintenance.shutil.move

    def fail_first(src: str, dst: str) -> str:
        if Path(src).name == "a":
            raise OSError("synthetic failure")
        return original_move(src, dst)

    monkeypatch.setattr(log_maintenance.shutil, "move", fail_first)
    results = apply_log_move_candidates(root, [_candidate("a", "dev/a"), _candidate("b", "dev/b")])
    assert [item["status"] for item in results] == ["failed", "moved"]
    assert (root / "a").exists()
    assert (root / "dev/b").exists()
