from __future__ import annotations

import json
from pathlib import Path

from libs.core.log_maintenance import apply_log_move_candidates
from libs.core.log_maintenance import build_log_inventory
from libs.core.log_maintenance import detect_log_move_candidates
from libs.core.log_maintenance import write_log_inventory


def test_log_inventory_detects_legacy_root_entries(tmp_path: Path) -> None:
    log_root = tmp_path / "data" / "logs"
    log_root.mkdir(parents=True)
    (log_root / "events.jsonl").write_text("", encoding="utf-8")
    (log_root / "intents.jsonl").write_text("", encoding="utf-8")
    (log_root / "offhours_demo.jsonl").write_text("", encoding="utf-8")
    (log_root / "events_live.jsonl").write_text("", encoding="utf-8")
    (log_root / "m25_notify_events.jsonl").write_text("", encoding="utf-8")
    (log_root / "m30_golive").mkdir()

    inventory = build_log_inventory(log_root)
    rel_paths = {item["rel_path"] for item in inventory["move_candidates"]}
    assert "offhours_demo.jsonl" in rel_paths
    assert "events_live.jsonl" in rel_paths
    assert "m25_notify_events.jsonl" in rel_paths
    assert "m30_golive" in rel_paths


def test_apply_log_move_candidates_moves_files_and_dirs(tmp_path: Path) -> None:
    log_root = tmp_path / "data" / "logs"
    log_root.mkdir(parents=True)
    (log_root / "events.jsonl").write_text("", encoding="utf-8")
    (log_root / "intents.jsonl").write_text("", encoding="utf-8")
    (log_root / "offhours_demo.jsonl").write_text("{}", encoding="utf-8")
    (log_root / "m30_golive").mkdir()
    (log_root / "m30_golive" / "sample.jsonl").write_text("{}", encoding="utf-8")

    moved = apply_log_move_candidates(log_root, detect_log_move_candidates(log_root))

    assert moved
    assert {result["status"] for result in moved} == {"moved"}
    assert (log_root / "dev" / "analysis" / "offhours" / "offhours_demo.jsonl").exists()
    assert (log_root / "milestones" / "m30" / "golive" / "sample.jsonl").exists()
    assert not (log_root / "offhours_demo.jsonl").exists()
    assert not (log_root / "m30_golive").exists()


def test_apply_log_move_candidates_preserves_destination_and_continues_after_conflict(tmp_path: Path) -> None:
    log_root = tmp_path / "data" / "logs"
    log_root.mkdir(parents=True)
    (log_root / "offhours_demo.jsonl").write_text("source", encoding="utf-8")
    destination = log_root / "dev" / "analysis" / "offhours" / "offhours_demo.jsonl"
    destination.parent.mkdir(parents=True)
    destination.write_text("existing", encoding="utf-8")
    (log_root / "events_live.jsonl").write_text("move-me", encoding="utf-8")

    results = apply_log_move_candidates(log_root, detect_log_move_candidates(log_root))

    by_source = {Path(result["src"]).name: result for result in results}
    assert by_source["offhours_demo.jsonl"]["status"] == "skipped_destination_exists"
    assert (log_root / "offhours_demo.jsonl").read_text(encoding="utf-8") == "source"
    assert destination.read_text(encoding="utf-8") == "existing"
    assert by_source["events_live.jsonl"]["status"] == "moved"
    assert (log_root / "dev" / "live" / "events_live.jsonl").exists()


def test_write_log_inventory_outputs_catalog(tmp_path: Path) -> None:
    log_root = tmp_path / "data" / "logs"
    log_root.mkdir(parents=True)
    (log_root / "events.jsonl").write_text("", encoding="utf-8")
    (log_root / "intents.jsonl").write_text("", encoding="utf-8")

    inventory = build_log_inventory(log_root)
    md_path, js_path = write_log_inventory(log_root, inventory)

    assert md_path.exists()
    assert js_path.exists()
    obj = json.loads(js_path.read_text(encoding="utf-8"))
    assert obj["summary"]["warning_total"] == 0
