"""RF-066 C1/C2: report-maintenance CLI confines dry inventory effects."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.maintenance import run_report_maintenance as cli


def test_rf066_report_maintenance_nonapply_preserves_temp_source_and_reports_in_root(tmp_path, capsys):
    report_root = tmp_path / "reports"
    report_root.mkdir()
    source = report_root / "daily_report_2026-10-29.json"
    source.write_text('{"day":"2026-10-29"}\n', encoding="utf-8")
    event_log = tmp_path / "events.jsonl"
    event_log.write_text("", encoding="utf-8")

    if cli.main(["--report-root", str(report_root), "--event-log-path", str(event_log), "--json"]) != 0:
        raise AssertionError("report maintenance CLI failed")

    payload = json.loads(capsys.readouterr().out)
    if payload["apply"] is not False or payload["moved_total"] != 0:
        raise AssertionError(payload)
    if source.read_text(encoding="utf-8") != '{"day":"2026-10-29"}\n':
        raise AssertionError("non-apply inventory mutated its source")
    for reported in (payload["report_md_path"], payload["report_json_path"]):
        path = Path(reported)
        if not path.is_relative_to(report_root) or not path.is_file():
            raise AssertionError(f"inventory escaped temp report root: {path}")
