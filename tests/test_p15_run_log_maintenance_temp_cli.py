"""RF-066: maintenance dry/apply CLI only manipulates its explicit temp log root."""

from __future__ import annotations

import json
from pathlib import Path

from libs.core import log_maintenance
from scripts.maintenance import run_log_maintenance


def _run(log_root: Path, capsys, *, apply: bool = False) -> dict:
    argv = ["--log-root", str(log_root), "--json"]
    if apply:
        argv.append("--apply")
    assert run_log_maintenance.main(argv) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["ok"] is True
    assert result["log_root"] == str(log_root)
    assert result["apply"] is apply
    assert result["moved_total"] == sum(x["status"] == "moved" for x in result["move_results"])
    assert Path(result["report_json_path"]).is_relative_to(log_root)
    assert Path(result["report_md_path"]).is_relative_to(log_root)
    assert Path(result["report_json_path"]).is_file()
    assert Path(result["report_md_path"]).is_file()
    stored = json.loads(Path(result["report_json_path"]).read_text(encoding="utf-8"))
    assert result["warning_total"] == stored["summary"]["warning_total"]
    return result


def test_dry_inspection_preserves_source_and_writes_only_temp_catalog(tmp_path: Path, capsys) -> None:
    root = tmp_path / "logs"
    root.mkdir()
    source = root / "offhours_a.jsonl"
    source.write_text("payload", encoding="utf-8")
    result = _run(root, capsys)
    assert result["move_candidate_total"] == 1
    assert result["moved_total"] == 0
    assert result["move_results"] == []
    assert source.read_text(encoding="utf-8") == "payload"
    assert sorted(x.relative_to(root).as_posix() for x in root.rglob("*") if x.is_file()) == [
        "dev/catalog/log_inventory_latest.json",
        "dev/catalog/log_inventory_latest.md",
        "offhours_a.jsonl",
    ]


def test_apply_moves_once_and_second_apply_is_idempotent(tmp_path: Path, capsys) -> None:
    root = tmp_path / "logs"
    root.mkdir()
    (root / "offhours_a.jsonl").write_text("payload", encoding="utf-8")
    first = _run(root, capsys, apply=True)
    assert first["move_candidate_total"] == 1
    assert first["moved_total"] == 1
    assert [x["status"] for x in first["move_results"]] == ["moved"]
    target = root / "dev" / "analysis" / "offhours" / "offhours_a.jsonl"
    assert target.read_text(encoding="utf-8") == "payload"
    assert not (root / "offhours_a.jsonl").exists()
    second = _run(root, capsys, apply=True)
    assert second["move_candidate_total"] == 0
    assert second["moved_total"] == 0
    assert second["move_results"] == []
    assert target.read_text(encoding="utf-8") == "payload"


def test_apply_keeps_existing_target_and_original(tmp_path: Path, capsys) -> None:
    root = tmp_path / "logs"
    root.mkdir()
    original = root / "offhours_a.jsonl"
    original.write_text("original", encoding="utf-8")
    target = root / "dev" / "analysis" / "offhours" / "offhours_a.jsonl"
    target.parent.mkdir(parents=True)
    target.write_text("existing", encoding="utf-8")
    result = _run(root, capsys, apply=True)
    assert result["moved_total"] == 0
    assert result["move_results"][0]["status"] == "skipped_destination_exists"
    assert original.read_text(encoding="utf-8") == "original"
    assert target.read_text(encoding="utf-8") == "existing"


def test_apply_failure_does_not_prevent_next_move(tmp_path: Path, capsys, monkeypatch) -> None:
    root = tmp_path / "logs"
    root.mkdir()
    source_a = root / "offhours_a.jsonl"
    source_b = root / "offhours_b.jsonl"
    source_a.write_text("a", encoding="utf-8")
    source_b.write_text("b", encoding="utf-8")
    old_move = log_maintenance.shutil.move

    def injected(src: str, dst: str) -> str:
        if Path(src).name == "offhours_a.jsonl":
            raise OSError("synthetic failure")
        return old_move(src, dst)

    monkeypatch.setattr(log_maintenance.shutil, "move", injected)
    result = _run(root, capsys, apply=True)
    assert result["moved_total"] == 1
    assert [x["status"] for x in result["move_results"]] == ["failed", "moved"]
    assert source_a.read_text(encoding="utf-8") == "a"
    assert not source_b.exists()
    assert (root / "dev" / "analysis" / "offhours" / "offhours_b.jsonl").read_text(encoding="utf-8") == "b"
    assert result["move_results"][0]["error"] == "synthetic failure"
