"""RF-066 C1/C2: log-maintenance CLI stays inside an explicit temp root."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.maintenance import run_log_maintenance as cli


def test_rf066_log_maintenance_dry_inventory_preserves_source_and_writes_only_temp_root(tmp_path, capsys):
    log_root = tmp_path / "logs"
    log_root.mkdir()
    source = log_root / "legacy_run.jsonl"
    source.write_text('{"event":"kept"}\n', encoding="utf-8")

    if cli.main(["--log-root", str(log_root), "--json"]) != 0:
        raise AssertionError("log maintenance CLI failed")

    payload = json.loads(capsys.readouterr().out)
    if payload["apply"] is not False or payload["moved_total"] != 0:
        raise AssertionError(payload)
    if source.read_text(encoding="utf-8") != '{"event":"kept"}\n':
        raise AssertionError("non-apply inventory mutated its source")
    for reported in (payload["report_md_path"], payload["report_json_path"]):
        path = Path(reported)
        if not path.is_relative_to(log_root) or not path.is_file():
            raise AssertionError(f"inventory escaped temp log root: {path}")
