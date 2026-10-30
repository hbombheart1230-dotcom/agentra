"""P15 RF-035 (01h): daily_report_runtime.markdown.render_route_and_narrative_sections moved to markdown_route_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import hashlib
import json

import pytest

from libs.reporting.daily_report_runtime import markdown as m
from libs.reporting.daily_report_runtime import markdown_route_projection as owner

FX = json.loads("{\"snap_rich\": {\"executive_summary\": {\"summary_lines\": [\"ok\", \"two\"]}, \"system_status\": \"healthy\", \"top_issues\": [{\"severity\": \"warn\", \"code\": \"X\", \"detail\": \"demo\"}, \"bad\"], \"recommended_operator_actions\": [\"A\", \"B\"]}, \"route\": {\"route_summary\": {\"route_source\": \"sim\", \"route_source_run_count\": 1, \"route_source_missing_count\": 0}, \"narrative_axis_policy\": {\"entry_primary_for\": [\"entry\"], \"exit_primary_for\": []}}, \"integ\": {\"trade_report_integrity\": {\"status\": \"missing_reports\", \"expected_trade_count\": 3, \"checked_trade_count\": 2, \"missing_count\": 1, \"missing\": [{\"trade_id\": \"T1\", \"missing\": [\"ai_trade_summary_md\"]}, \"x\"], \"broker_closed_report_open_count\": 1, \"broker_closed_report_open\": [{\"trade_id\": \"T2\", \"symbol\": \"005930\", \"lifecycle_status\": \"open\", \"issue\": \"broker_day_trade_closed_but_report_open\"}]}}, \"align\": {\"broker_alignment\": {\"status\": \"ok\", \"summary\": {\"local_total\": 2, \"broker_total\": 2, \"matched_by_ord_no\": 2}, \"account_snapshot\": {\"api_call_count\": 2, \"ok_count\": 1}}}, \"pol\": {\"chart_structure_decision_hint_summary\": {\"applied_examples\": [{\"run_id\": \"R1\", \"entry_style\": \"pullback\"}], \"applied_count\": 1}}, \"payload\": {\"data_freshness\": {}, \"operator_summary_snapshot\": {\"executive_summary\": {\"summary_lines\": [\"ok\", \"two\"]}, \"system_status\": \"healthy\", \"top_issues\": [{\"severity\": \"warn\", \"code\": \"X\", \"detail\": \"demo\"}, \"bad\"], \"recommended_operator_actions\": [\"A\", \"B\"]}, \"residual_positions\": {\"k\": 1}, \"route_summary\": {\"route_source\": \"sim\", \"route_source_run_count\": 1, \"route_source_missing_count\": 0}, \"narrative_axis_policy\": {\"entry_primary_for\": [\"entry\"], \"exit_primary_for\": []}, \"trade_report_integrity\": {\"status\": \"missing_reports\", \"expected_trade_count\": 3, \"checked_trade_count\": 2, \"missing_count\": 1, \"missing\": [{\"trade_id\": \"T1\", \"missing\": [\"ai_trade_summary_md\"]}, \"x\"], \"broker_closed_report_open_count\": 1, \"broker_closed_report_open\": [{\"trade_id\": \"T2\", \"symbol\": \"005930\", \"lifecycle_status\": \"open\", \"issue\": \"broker_day_trade_closed_but_report_open\"}]}, \"broker_alignment\": {\"status\": \"ok\", \"summary\": {\"local_total\": 2, \"broker_total\": 2, \"matched_by_ord_no\": 2}, \"account_snapshot\": {\"api_call_count\": 2, \"ok_count\": 1}}, \"chart_structure_decision_hint_summary\": {\"applied_examples\": [{\"run_id\": \"R1\", \"entry_style\": \"pullback\"}], \"applied_count\": 1}}}")


def _h(x):
    return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


GOLDEN = ['6d700dd5cff59207a31f213fe0ea1ace311180ac24be6493fd8ca533275f4157', '04cf1c81dea23571291111078f1e681cd37346df6840f608ae5db274e5080827']


def _both(p):
    return m.render_route_and_narrative_sections(p), owner.render_route_and_narrative_sections(p, facade=m)


@pytest.mark.parametrize("i,key", [(0, "route"), (1, None)])
def test_golden_parity(i, key):
    p = FX[key] if key else {}
    snap = copy.deepcopy(p)
    a, b = _both(p)
    assert a == b and _h(a) == GOLDEN[i] and p == snap


def test_route_heading_and_source_lines():
    a, b = _both(FX["route"])
    assert a == b and any("Route Provenance" in x for x in a)
    text = "\n".join(a)
    assert "sim" in text


def test_missing_policy_calls_facade(monkeypatch):
    seen = []
    monkeypatch.setattr(m, "narrative_axis_policy", lambda: (seen.append(1), {"entry_primary_for": ["SEAM"], "exit_primary_for": []})[1])
    a, b = _both({"route_summary": {}})
    assert a == b and len(seen) == 2 and "SEAM" in "\n".join(a)


def test_facade_json_dumps_seam(monkeypatch):
    monkeypatch.setattr(m.json, "dumps", lambda *a, **k: "DUMPED")
    a, b = _both(FX["route"])
    assert a == b
