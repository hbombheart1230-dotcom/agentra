"""RF-045 C2: log-maintenance inventory writes are confined to a caller temp root."""

from __future__ import annotations

import json

from libs.core.log_maintenance import build_log_inventory, write_log_inventory


def test_rf045_log_inventory_writes_json_and_markdown_under_temp_root(tmp_path):
    """The inventory consumer receives paths only below its supplied root."""
    log_root = tmp_path / "logs"
    log_root.mkdir()
    (log_root / "offhours_probe.jsonl").write_text("{}\n", encoding="utf-8")

    inventory = build_log_inventory(log_root)
    markdown_path, json_path = write_log_inventory(log_root, inventory)

    assert json_path.is_relative_to(log_root)
    assert markdown_path.is_relative_to(log_root)
    assert json.loads(json_path.read_text(encoding="utf-8"))["summary"]["move_candidate_total"] == 1
    assert "offhours_probe.jsonl" in markdown_path.read_text(encoding="utf-8")
