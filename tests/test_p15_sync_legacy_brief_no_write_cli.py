"""RF-066: the deprecated brief LLM CLI inspects explicit temp roots without writes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.maintenance import sync_legacy_brief_llm


def _snapshot(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def _call(capsys, root: Path, day: str, *, dry_run: bool) -> dict:
    argv = ["--day", day, "--reports-root", str(root), "--json"]
    if dry_run:
        argv.append("--dry-run")
    assert sync_legacy_brief_llm.main(argv) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["ok"] is True
    assert result["day"] == day
    assert result["reports_root"] == str(root)
    assert result["dry_run"] is dry_run
    assert result["trade_count"] == len(result["rows"])
    return result


@pytest.mark.parametrize("dry_run", [False, True])
def test_absent_day_returns_zero_and_creates_nothing(tmp_path: Path, capsys, monkeypatch, dry_run: bool) -> None:
    root = tmp_path / "reports"
    root.mkdir()
    monkeypatch.chdir(tmp_path)
    before = _snapshot(tmp_path)
    result = _call(capsys, root, "2026-10-01", dry_run=dry_run)
    assert result["rows"] == []
    assert result["trade_count"] == 0
    assert _snapshot(tmp_path) == before


@pytest.mark.parametrize("dry_run", [False, True])
def test_primary_present_and_missing_have_distinct_statuses_without_writes(
    tmp_path: Path, capsys, monkeypatch, dry_run: bool
) -> None:
    root = tmp_path / "reports"
    day_root = root / "trades" / "2026-10-01"
    primary = day_root / "TRD_A" / "reports" / "brief_llm_response.json"
    primary.parent.mkdir(parents=True)
    primary.write_bytes(b'{"summary":"canonical"}\\n')
    # TRD_ prefix is part of llm_artifacts.iter_trade_dirs discovery contract.
    (day_root / "TRD_B").mkdir()
    monkeypatch.chdir(tmp_path)
    before = _snapshot(tmp_path)
    result = _call(capsys, root, "2026-10-01", dry_run=dry_run)
    assert result["trade_count"] == 2
    assert [row["trade_id"] for row in result["rows"]] == ["TRD_A", "TRD_B"]
    assert result["rows"][0] == {
        "trade_id": "TRD_A",
        "status": "canonical_present",
        "canonical_path": str(primary),
        "deprecated_legacy_sync": "true",
        "dry_run": str(dry_run).lower(),
    }
    assert result["rows"][1] == {"trade_id": "TRD_B", "status": "skip_no_primary"}
    assert _snapshot(tmp_path) == before
    assert not (day_root / "TRD_A" / "brief_llm_response.json").exists()


@pytest.mark.parametrize("dry_run", [False, True])
def test_repeat_execution_has_no_filesystem_effects(tmp_path: Path, capsys, monkeypatch, dry_run: bool) -> None:
    root = tmp_path / "reports"
    primary = root / "trades" / "2026-10-01" / "TRD_Z" / "reports" / "brief_llm_response.json"
    primary.parent.mkdir(parents=True)
    primary.write_bytes(b'{"response":1}')
    monkeypatch.chdir(tmp_path)
    before = _snapshot(tmp_path)
    first = _call(capsys, root, "2026-10-01", dry_run=dry_run)
    second = _call(capsys, root, "2026-10-01", dry_run=dry_run)
    assert first == second
    assert _snapshot(tmp_path) == before
