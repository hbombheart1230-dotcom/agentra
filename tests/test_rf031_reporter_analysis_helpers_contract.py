"""RF-031 reporter_analysis: pure helpers and intent-flow aggregation on tmp files (no AI, no network, no reports tree)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from libs.reporting import reporter_analysis as ra

DAY = "2026-10-28"


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def _ts(hour=3):
    return int(datetime(2026, 10, 28, hour, tzinfo=timezone.utc).timestamp())


def test_safe_number_fallbacks():
    _eq((ra._safe_int("7.9"), ra._safe_int(None, 5), ra._safe_int("x", 3)), (7, 5, 3))
    _eq((ra._safe_float("2.5"), ra._safe_float(None, 1.5), ra._safe_float([], 9)), (2.5, 1.5, 9.0))
    _eq((ra._reason_text(None), ra._reason_text("  "), ra._reason_text(" why ")), ("unspecified", "unspecified", "why"))


def test_iter_jsonl_and_read_json_tolerate_missing_blank_and_corrupt_input(tmp_path):
    _eq(ra._iter_jsonl(tmp_path / "missing.jsonl"), [])
    p = tmp_path / "rows.jsonl"
    p.write_text(json.dumps({"a": 1}) + "\n\n   \n{broken\n" + json.dumps([1, 2]) + "\n" + json.dumps({"b": 2}, ensure_ascii=False) + "\n", encoding="utf-8")
    _eq(ra._iter_jsonl(p), [{"a": 1}, {"b": 2}])                       # blanks, bad JSON and non-dict rows are dropped
    _eq(ra._read_json(tmp_path / "none.json"), {})
    j = tmp_path / "o.json"
    j.write_text("{oops", encoding="utf-8")
    _eq(ra._read_json(j), {})
    j.write_text(json.dumps([1]), encoding="utf-8")
    _eq(ra._read_json(j), {})
    j.write_text(json.dumps({"k": "한글"}, ensure_ascii=False), encoding="utf-8")
    _eq(ra._read_json(j), {"k": "한글"})


def test_canonical_reports_root_walks_up_to_a_reports_directory():
    _eq(ra._canonical_reports_root(Path("/x/reports/dev/analysis")), Path("/x/reports"))
    _eq(ra._canonical_reports_root(Path("/x/reports")), Path("/x/reports"))
    _eq(ra._canonical_reports_root(Path("/x/other/dir")), Path("/x/other/dir"))     # no "reports" ancestor -> unchanged


def test_utc_day_and_epoch_boundaries():
    _eq(ra._utc_day(_ts(23)), DAY)
    _eq(ra._utc_day(None), None)
    _eq(ra._utc_day("not-a-time"), None)


def test_intent_flow_counts_statuses_for_the_requested_day_only(tmp_path):
    intents = tmp_path / "intents.jsonl"
    rows = [
        {"ts": _ts(1), "status": "approved"},
        {"ts": _ts(2), "status": "Executed"},
        {"ts": _ts(3), "status": "rejected", "reason": "risk"},
        {"ts": _ts(4), "status": "failed", "reason": ""},
        {"ts": _ts(5)},                                              # no status -> created
        {"ts": int(datetime(2026, 10, 27, 12, tzinfo=timezone.utc).timestamp()), "status": "approved"},   # other day: skipped
    ]
    intents.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    day_rows = [
        {"stage": "execute_from_packet", "event": "verdict", "payload": {"allowed": False, "reason": "guard"}},
        {"stage": "execute_from_packet", "event": "verdict", "payload": {"allowed": True}},
        {"stage": "monitor", "event": "summary", "payload": {"min_hold_blocked": True, "sell_cooldown_blocked": 1, "monitor_reason": "trail"}},
        {"stage": "monitor", "event": "summary", "payload": "junk"},
    ]
    out = ra._build_intent_flow_analysis(day_rows=day_rows, intents_path=intents, day=DAY, operator_summary_obj={})
    _eq((out["intents_created"], out["intents_approved"], out["intents_executed"], out["intents_blocked"]), (1, 1, 1, 3))
    _eq(out["status_counts"], {"approved": 1, "executed": 1, "rejected": 1, "failed": 1})
    _eq(out["reason_top"], {"risk": 1, "unspecified": 1, "guard": 1, "min_hold_blocked": 1, "sell_cooldown_blocked": 1, "monitor:trail": 1})


def test_intent_flow_falls_back_to_operator_metrics_when_nothing_was_counted(tmp_path):
    summary = {"raw_snapshot": {"metrics_execution": {"intents_created": "4", "intents_blocked": 2, "intents_approved": "x", "intents_executed": 1}}}
    out = ra._build_intent_flow_analysis(day_rows=[], intents_path=None, day=DAY, operator_summary_obj=summary)
    _eq((out["intents_created"], out["intents_blocked"], out["intents_approved"], out["intents_executed"]), (4, 2, 0, 1))
    zero = ra._build_intent_flow_analysis(day_rows=[], intents_path=tmp_path / "none.jsonl", day=DAY, operator_summary_obj={"raw_snapshot": "x"})
    _eq((zero["intents_created"], zero["status_counts"], zero["reason_top"]), (0, {}, {}))


def test_latest_day_picks_the_newest_day_and_handles_missing_or_empty_logs(tmp_path):
    _eq(ra._latest_day(tmp_path / "none.jsonl"), None)
    p = tmp_path / "events.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in [
        {"ts": "2026-10-27T10:00:00+00:00"}, {"ts": "2026-10-28T01:00:00+00:00"},
        {"payload": {"ts": "2026-10-26T01:00:00+00:00"}}, {"x": 1}]) + "\n", encoding="utf-8")
    _eq(ra._latest_day(p), DAY)
    p.write_text("", encoding="utf-8")
    _eq(ra._latest_day(p), None)
