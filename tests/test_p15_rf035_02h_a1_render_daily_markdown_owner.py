"""P15 RF-035 (02h): daily_report_runtime.markdown.render_daily_markdown moved to markdown_daily_full_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter

import pytest

from libs.reporting.daily_report_runtime import markdown as m
from libs.reporting.daily_report_runtime import markdown_daily_full_projection as owner

FX = json.loads("{\"snap_rich\": {\"executive_summary\": {\"summary_lines\": [\"ok\", \"two\"]}, \"system_status\": \"healthy\", \"top_issues\": [{\"severity\": \"warn\", \"code\": \"X\", \"detail\": \"demo\"}, \"bad\"], \"recommended_operator_actions\": [\"A\", \"B\"]}, \"route\": {\"route_summary\": {\"route_source\": \"sim\", \"route_source_run_count\": 1, \"route_source_missing_count\": 0}, \"narrative_axis_policy\": {\"entry_primary_for\": [\"entry\"], \"exit_primary_for\": []}}, \"integ\": {\"trade_report_integrity\": {\"status\": \"missing_reports\", \"expected_trade_count\": 3, \"checked_trade_count\": 2, \"missing_count\": 1, \"missing\": [{\"trade_id\": \"T1\", \"missing\": [\"ai_trade_summary_md\"]}, \"x\"], \"broker_closed_report_open_count\": 1, \"broker_closed_report_open\": [{\"trade_id\": \"T2\", \"symbol\": \"005930\", \"lifecycle_status\": \"open\", \"issue\": \"broker_day_trade_closed_but_report_open\"}]}}, \"align\": {\"broker_alignment\": {\"status\": \"ok\", \"summary\": {\"local_total\": 2, \"broker_total\": 2, \"matched_by_ord_no\": 2}, \"account_snapshot\": {\"api_call_count\": 2, \"ok_count\": 1}}}, \"pol\": {\"chart_structure_decision_hint_summary\": {\"applied_examples\": [{\"run_id\": \"R1\", \"entry_style\": \"pullback\"}], \"applied_count\": 1}}, \"payload\": {\"data_freshness\": {}, \"operator_summary_snapshot\": {\"executive_summary\": {\"summary_lines\": [\"ok\", \"two\"]}, \"system_status\": \"healthy\", \"top_issues\": [{\"severity\": \"warn\", \"code\": \"X\", \"detail\": \"demo\"}, \"bad\"], \"recommended_operator_actions\": [\"A\", \"B\"]}, \"residual_positions\": {\"k\": 1}, \"route_summary\": {\"route_source\": \"sim\", \"route_source_run_count\": 1, \"route_source_missing_count\": 0}, \"narrative_axis_policy\": {\"entry_primary_for\": [\"entry\"], \"exit_primary_for\": []}, \"trade_report_integrity\": {\"status\": \"missing_reports\", \"expected_trade_count\": 3, \"checked_trade_count\": 2, \"missing_count\": 1, \"missing\": [{\"trade_id\": \"T1\", \"missing\": [\"ai_trade_summary_md\"]}, \"x\"], \"broker_closed_report_open_count\": 1, \"broker_closed_report_open\": [{\"trade_id\": \"T2\", \"symbol\": \"005930\", \"lifecycle_status\": \"open\", \"issue\": \"broker_day_trade_closed_but_report_open\"}]}, \"broker_alignment\": {\"status\": \"ok\", \"summary\": {\"local_total\": 2, \"broker_total\": 2, \"matched_by_ord_no\": 2}, \"account_snapshot\": {\"api_call_count\": 2, \"ok_count\": 1}}, \"chart_structure_decision_hint_summary\": {\"applied_examples\": [{\"run_id\": \"R1\", \"entry_style\": \"pullback\"}], \"applied_count\": 1}}}")
GOLDEN = ["4949fb8b2476cccb2c561fa0fc5345fb3d6013a5840f3fb30dd2f66df821ee52", "d2d779d01bb7fd8a1ad35eb8e184c7f49c21b4e603ae1405fecde5bf77004867"]


def _cases():
    return [
        dict(day="2026-10-30", summary=dict(copy.deepcopy(FX["payload"]), events=7), operator_summary_snapshot_freshness={"stale": True}, approvals=3, blocks=1,
             symbols_for_day=["A", "B"], actions=Counter({"approve": 2, "deny": 1}), stage_counter=Counter({"monitor": 2, "entry": 1}), render_residual_positions=lambda r: ["RES"]),
        dict(day="d", summary={"data_freshness": {}, "events": 0}, operator_summary_snapshot_freshness={"stale": False}, approvals=0, blocks=0, symbols_for_day=[],
             actions=Counter(), stage_counter=Counter(), render_residual_positions=lambda r: []),
    ]


def _both(**kw):
    return m.render_daily_markdown(**kw), owner.render_daily_markdown(facade=m, **kw)


@pytest.mark.parametrize("i", [0, 1])
def test_golden_parity(i):
    kw = _cases()[i]
    snap = copy.deepcopy(kw["summary"])
    a, b = _both(**kw)
    assert a == b and hashlib.sha256(a.encode()).hexdigest() == GOLDEN[i] and kw["summary"] == snap and a.endswith("\n")


def test_counter_order_and_none_branch():
    a, b = _both(**_cases()[0])
    assert a.index("- approve: 2") < a.index("- deny: 1") and a.index("- monitor: 2") < a.index("- entry: 1")
    a, b = _both(**_cases()[1])
    assert "- (none)" in a and "- symbols observed: **0**" in a


def test_all_facade_helpers_seamed(monkeypatch):
    for name in ("render_trade_report_integrity", "render_broker_alignment", "render_route_and_narrative_sections", "render_policy_surface_sections", "render_top_issues", "render_recommended_operator_actions"):
        monkeypatch.setattr(m, name, (lambda n: (lambda p: ["SEAM:" + n]))(name))
    monkeypatch.setattr(m, "render_data_freshness_markdown", lambda d: ["FRESH"])
    monkeypatch.setattr(m, "render_operator_summary_snapshot", lambda s, include_system_status: ["SNAP", str(include_system_status)])
    a, b = _both(**_cases()[1])
    assert a == b
    lines = a.split("\n")
    assert lines[:4] == ["# Daily Report (d)", "", "FRESH", "- operator_summary_snapshot_stale: **False**"] and "SNAP" in lines and "True" in lines


def test_missing_data_freshness_keyerror():
    kw = _cases()[1]
    kw["summary"] = {"events": 0}
    for fn in (lambda: m.render_daily_markdown(**kw), lambda: owner.render_daily_markdown(facade=m, **kw)):
        with pytest.raises(KeyError):
            fn()


def test_keyword_only():
    with pytest.raises(TypeError):
        m.render_daily_markdown("d")
