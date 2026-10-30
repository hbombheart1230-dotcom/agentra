"""P15 RF-035 (01h): daily_report_runtime.markdown.render_operator_summary_snapshot moved to markdown_snapshot_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import hashlib
import json

import pytest

from libs.reporting.daily_report_runtime import markdown as m
from libs.reporting.daily_report_runtime import markdown_snapshot_projection as owner

FX = json.loads("{\"snap_rich\": {\"executive_summary\": {\"summary_lines\": [\"ok\", \"two\"]}, \"system_status\": \"healthy\", \"top_issues\": [{\"severity\": \"warn\", \"code\": \"X\", \"detail\": \"demo\"}, \"bad\"], \"recommended_operator_actions\": [\"A\", \"B\"]}, \"route\": {\"route_summary\": {\"route_source\": \"sim\", \"route_source_run_count\": 1, \"route_source_missing_count\": 0}, \"narrative_axis_policy\": {\"entry_primary_for\": [\"entry\"], \"exit_primary_for\": []}}, \"integ\": {\"trade_report_integrity\": {\"status\": \"missing_reports\", \"expected_trade_count\": 3, \"checked_trade_count\": 2, \"missing_count\": 1, \"missing\": [{\"trade_id\": \"T1\", \"missing\": [\"ai_trade_summary_md\"]}, \"x\"], \"broker_closed_report_open_count\": 1, \"broker_closed_report_open\": [{\"trade_id\": \"T2\", \"symbol\": \"005930\", \"lifecycle_status\": \"open\", \"issue\": \"broker_day_trade_closed_but_report_open\"}]}}, \"align\": {\"broker_alignment\": {\"status\": \"ok\", \"summary\": {\"local_total\": 2, \"broker_total\": 2, \"matched_by_ord_no\": 2}, \"account_snapshot\": {\"api_call_count\": 2, \"ok_count\": 1}}}, \"pol\": {\"chart_structure_decision_hint_summary\": {\"applied_examples\": [{\"run_id\": \"R1\", \"entry_style\": \"pullback\"}], \"applied_count\": 1}}, \"payload\": {\"data_freshness\": {}, \"operator_summary_snapshot\": {\"executive_summary\": {\"summary_lines\": [\"ok\", \"two\"]}, \"system_status\": \"healthy\", \"top_issues\": [{\"severity\": \"warn\", \"code\": \"X\", \"detail\": \"demo\"}, \"bad\"], \"recommended_operator_actions\": [\"A\", \"B\"]}, \"residual_positions\": {\"k\": 1}, \"route_summary\": {\"route_source\": \"sim\", \"route_source_run_count\": 1, \"route_source_missing_count\": 0}, \"narrative_axis_policy\": {\"entry_primary_for\": [\"entry\"], \"exit_primary_for\": []}, \"trade_report_integrity\": {\"status\": \"missing_reports\", \"expected_trade_count\": 3, \"checked_trade_count\": 2, \"missing_count\": 1, \"missing\": [{\"trade_id\": \"T1\", \"missing\": [\"ai_trade_summary_md\"]}, \"x\"], \"broker_closed_report_open_count\": 1, \"broker_closed_report_open\": [{\"trade_id\": \"T2\", \"symbol\": \"005930\", \"lifecycle_status\": \"open\", \"issue\": \"broker_day_trade_closed_but_report_open\"}]}, \"broker_alignment\": {\"status\": \"ok\", \"summary\": {\"local_total\": 2, \"broker_total\": 2, \"matched_by_ord_no\": 2}, \"account_snapshot\": {\"api_call_count\": 2, \"ok_count\": 1}}, \"chart_structure_decision_hint_summary\": {\"applied_examples\": [{\"run_id\": \"R1\", \"entry_style\": \"pullback\"}], \"applied_count\": 1}}}")


def _h(x):
    return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


GOLDEN = ['16e2b42f2ab69227dd9f9d0c848be04f03413c4277191f9b7305ebefc392e1b9', '16e2b42f2ab69227dd9f9d0c848be04f03413c4277191f9b7305ebefc392e1b9', '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945']
CASES = [(FX["snap_rich"], True), (FX["snap_rich"], False), ({}, True)]


@pytest.mark.parametrize("i", range(3))
def test_golden_parity_and_input_unchanged(i):
    p, flag = CASES[i]
    snap = copy.deepcopy(p)
    a = m.render_operator_summary_snapshot(p, include_system_status=flag)
    b = owner.render_operator_summary_snapshot(p, include_system_status=flag)
    assert a == b and _h(a) == GOLDEN[i] and p == snap


def test_system_status_flag():
    snap = {"executive_summary": {"summary_lines": ["ok"], "system_status": "healthy"}}
    exp_on = ["", "## Operator Summary Snapshot", "", "- system_status: **healthy**", "- ok"]
    exp_off = ["", "## Operator Summary Snapshot", "", "- ok"]
    for fn in (m.render_operator_summary_snapshot, owner.render_operator_summary_snapshot):
        assert fn(snap, include_system_status=True) == exp_on
        assert fn(snap, include_system_status=False) == exp_off
        assert fn({"executive_summary": {"system_status": "x"}}, include_system_status=True) == []
        assert fn({"executive_summary": "x"}, include_system_status=True) == []


def test_keyword_only_flag():
    for fn in (m.render_operator_summary_snapshot, owner.render_operator_summary_snapshot):
        with pytest.raises(TypeError):
            fn({}, True)
