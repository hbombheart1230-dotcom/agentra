"""Emergency RF-066: inventory reports must not escape the selected temporary root."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from libs.core.log_maintenance import write_log_inventory
from scripts.maintenance import run_log_maintenance


def _link(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=target.is_dir())
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlinks unavailable: {exc}")


@pytest.mark.parametrize("symlink_level", ["dev", "catalog"])
def test_catalog_directory_symlink_cannot_write_outside_root(
    tmp_path: Path, symlink_level: str
) -> None:
    root = tmp_path / "logs"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (outside / "sentinel.txt").write_bytes(b"outside-stays-untouched")
    if symlink_level == "dev":
        _link(root / "dev", outside)
    else:
        (root / "dev").mkdir()
        _link(root / "dev" / "catalog", outside)
    with pytest.raises(ValueError, match="unsafe log inventory"):
        write_log_inventory(root, {"summary": {"warning_total": 0}})
    assert sorted(path.name for path in outside.iterdir()) == ["sentinel.txt"]
    assert (outside / "sentinel.txt").read_bytes() == b"outside-stays-untouched"


@pytest.mark.parametrize("filename", ["log_inventory_latest.json", "log_inventory_latest.md"])
def test_existing_output_symlink_cannot_clobber_external_file(
    tmp_path: Path, filename: str
) -> None:
    root = tmp_path / "logs"
    catalog = root / "dev" / "catalog"
    catalog.mkdir(parents=True)
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"original-bytes")
    _link(catalog / filename, outside)
    with pytest.raises(ValueError, match="unsafe log inventory"):
        write_log_inventory(root, {"summary": {"warning_total": 0}})
    assert outside.read_bytes() == b"original-bytes"
    assert sorted(x.name for x in catalog.iterdir()) == [filename]


def test_normal_temp_inventory_outputs_are_unchanged(tmp_path: Path) -> None:
    root = tmp_path / "logs"
    root.mkdir()
    payload = {
        "generated_at_utc": "2026-10-29T00:00:00Z",
        "log_root": str(root),
        "summary": {"top_level_entry_total": 0, "move_candidate_total": 0, "warning_total": 0},
        "canonical_top_level": [],
        "top_level": [],
        "move_candidates": [],
        "warnings": [],
    }
    md_path, js_path = write_log_inventory(root, payload)
    assert md_path == root / "dev" / "catalog" / "log_inventory_latest.md"
    assert js_path == root / "dev" / "catalog" / "log_inventory_latest.json"
    assert json.loads(js_path.read_text(encoding="utf-8")) == payload
    assert "# Log Inventory" in md_path.read_text(encoding="utf-8")


def test_dry_cli_fails_closed_without_writing_through_dev_symlink(
    tmp_path: Path, capsys
) -> None:
    root = tmp_path / "logs"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    _link(root / "dev", outside)
    with pytest.raises(ValueError, match="unsafe log inventory"):
        run_log_maintenance.main(["--log-root", str(root), "--json"])
    assert list(outside.iterdir()) == []
    assert capsys.readouterr().out == ""
