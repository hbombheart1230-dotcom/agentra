"""P15 RF-035 (01h): daily_report_runtime.markdown.render_broker_alignment moved to markdown_alignment_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import hashlib
import json

import pytest

from libs.reporting.daily_report_runtime import markdown as m
from libs.reporting.daily_report_runtime import markdown_alignment_projection as owner

FX = json.loads("{\"snap_rich\": {\"executive_summary\": {\"summary_lines\": [\"ok\", \"two\"]}, \"system_status\": \"healthy\", \"top_issues\": [{\"severity\": \"warn\", \"code\": \"X\", \"detail\": \"demo\"}, \"bad\"], \"recommended_operator_actions\": [\"A\", \"B\"]}, \"route\": {\"route_summary\": {\"route_source\": \"sim\", \"route_source_run_count\": 1, \"route_source_missing_count\": 0}, \"narrative_axis_policy\": {\"entry_primary_for\": [\"entry\"], \"exit_primary_for\": []}}, \"integ\": {\"trade_report_integrity\": {\"status\": \"missing_reports\", \"expected_trade_count\": 3, \"checked_trade_count\": 2, \"missing_count\": 1, \"missing\": [{\"trade_id\": \"T1\", \"missing\": [\"ai_trade_summary_md\"]}, \"x\"], \"broker_closed_report_open_count\": 1, \"broker_closed_report_open\": [{\"trade_id\": \"T2\", \"symbol\": \"005930\", \"lifecycle_status\": \"open\", \"issue\": \"broker_day_trade_closed_but_report_open\"}]}}, \"align\": {\"broker_alignment\": {\"status\": \"ok\", \"summary\": {\"local_total\": 2, \"broker_total\": 2, \"matched_by_ord_no\": 2}, \"account_snapshot\": {\"api_call_count\": 2, \"ok_count\": 1}}}, \"pol\": {\"chart_structure_decision_hint_summary\": {\"applied_examples\": [{\"run_id\": \"R1\", \"entry_style\": \"pullback\"}], \"applied_count\": 1}}, \"payload\": {\"data_freshness\": {}, \"operator_summary_snapshot\": {\"executive_summary\": {\"summary_lines\": [\"ok\", \"two\"]}, \"system_status\": \"healthy\", \"top_issues\": [{\"severity\": \"warn\", \"code\": \"X\", \"detail\": \"demo\"}, \"bad\"], \"recommended_operator_actions\": [\"A\", \"B\"]}, \"residual_positions\": {\"k\": 1}, \"route_summary\": {\"route_source\": \"sim\", \"route_source_run_count\": 1, \"route_source_missing_count\": 0}, \"narrative_axis_policy\": {\"entry_primary_for\": [\"entry\"], \"exit_primary_for\": []}, \"trade_report_integrity\": {\"status\": \"missing_reports\", \"expected_trade_count\": 3, \"checked_trade_count\": 2, \"missing_count\": 1, \"missing\": [{\"trade_id\": \"T1\", \"missing\": [\"ai_trade_summary_md\"]}, \"x\"], \"broker_closed_report_open_count\": 1, \"broker_closed_report_open\": [{\"trade_id\": \"T2\", \"symbol\": \"005930\", \"lifecycle_status\": \"open\", \"issue\": \"broker_day_trade_closed_but_report_open\"}]}, \"broker_alignment\": {\"status\": \"ok\", \"summary\": {\"local_total\": 2, \"broker_total\": 2, \"matched_by_ord_no\": 2}, \"account_snapshot\": {\"api_call_count\": 2, \"ok_count\": 1}}, \"chart_structure_decision_hint_summary\": {\"applied_examples\": [{\"run_id\": \"R1\", \"entry_style\": \"pullback\"}], \"applied_count\": 1}}}")


def _h(x):
    return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


GOLDEN = ['1c6a6f6b4df4d875ab6392a6caf8ebbd7475cd3e518b660b5a0e1e14f740ea4c', '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945']


def _both(p):
    return m.render_broker_alignment(p), owner.render_broker_alignment(p)


def test_golden_parity_and_empty():
    snap = copy.deepcopy(FX["align"])
    a, b = _both(FX["align"])
    assert a == b and _h(a) == GOLDEN[0] and FX["align"] == snap
    assert _both({}) == ([], []) and _h([]) == GOLDEN[1]


def test_fields_rendered():
    a, b = _both(FX["align"])
    text = "\n".join(a)
    assert "OK" in text and "local_total" in text and "broker_total" in text and "1/2 ok" in text


def test_malformed_count_raises_same():
    bad = {"broker_alignment": {"status": "ok", "summary": {"local_total": "bad"}}}
    outcomes = []
    for fn in (lambda: m.render_broker_alignment(bad), lambda: owner.render_broker_alignment(bad)):
        try:
            outcomes.append(("ok", tuple(fn())))
        except Exception as exc:
            outcomes.append((type(exc).__name__, str(exc)))
    assert outcomes[0] == outcomes[1]
