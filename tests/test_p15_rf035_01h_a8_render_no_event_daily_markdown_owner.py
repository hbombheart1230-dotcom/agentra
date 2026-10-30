"""P15 RF-035 (01h): daily_report_runtime.markdown.render_no_event_daily_markdown moved to markdown_daily_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import hashlib
import json

import pytest

from libs.reporting.daily_report_runtime import markdown as m
from libs.reporting.daily_report_runtime import markdown_daily_projection as owner

FX = json.loads("{\"snap_rich\": {\"executive_summary\": {\"summary_lines\": [\"ok\", \"two\"]}, \"system_status\": \"healthy\", \"top_issues\": [{\"severity\": \"warn\", \"code\": \"X\", \"detail\": \"demo\"}, \"bad\"], \"recommended_operator_actions\": [\"A\", \"B\"]}, \"route\": {\"route_summary\": {\"route_source\": \"sim\", \"route_source_run_count\": 1, \"route_source_missing_count\": 0}, \"narrative_axis_policy\": {\"entry_primary_for\": [\"entry\"], \"exit_primary_for\": []}}, \"integ\": {\"trade_report_integrity\": {\"status\": \"missing_reports\", \"expected_trade_count\": 3, \"checked_trade_count\": 2, \"missing_count\": 1, \"missing\": [{\"trade_id\": \"T1\", \"missing\": [\"ai_trade_summary_md\"]}, \"x\"], \"broker_closed_report_open_count\": 1, \"broker_closed_report_open\": [{\"trade_id\": \"T2\", \"symbol\": \"005930\", \"lifecycle_status\": \"open\", \"issue\": \"broker_day_trade_closed_but_report_open\"}]}}, \"align\": {\"broker_alignment\": {\"status\": \"ok\", \"summary\": {\"local_total\": 2, \"broker_total\": 2, \"matched_by_ord_no\": 2}, \"account_snapshot\": {\"api_call_count\": 2, \"ok_count\": 1}}}, \"pol\": {\"chart_structure_decision_hint_summary\": {\"applied_examples\": [{\"run_id\": \"R1\", \"entry_style\": \"pullback\"}], \"applied_count\": 1}}, \"payload\": {\"data_freshness\": {}, \"operator_summary_snapshot\": {\"executive_summary\": {\"summary_lines\": [\"ok\", \"two\"]}, \"system_status\": \"healthy\", \"top_issues\": [{\"severity\": \"warn\", \"code\": \"X\", \"detail\": \"demo\"}, \"bad\"], \"recommended_operator_actions\": [\"A\", \"B\"]}, \"residual_positions\": {\"k\": 1}, \"route_summary\": {\"route_source\": \"sim\", \"route_source_run_count\": 1, \"route_source_missing_count\": 0}, \"narrative_axis_policy\": {\"entry_primary_for\": [\"entry\"], \"exit_primary_for\": []}, \"trade_report_integrity\": {\"status\": \"missing_reports\", \"expected_trade_count\": 3, \"checked_trade_count\": 2, \"missing_count\": 1, \"missing\": [{\"trade_id\": \"T1\", \"missing\": [\"ai_trade_summary_md\"]}, \"x\"], \"broker_closed_report_open_count\": 1, \"broker_closed_report_open\": [{\"trade_id\": \"T2\", \"symbol\": \"005930\", \"lifecycle_status\": \"open\", \"issue\": \"broker_day_trade_closed_but_report_open\"}]}, \"broker_alignment\": {\"status\": \"ok\", \"summary\": {\"local_total\": 2, \"broker_total\": 2, \"matched_by_ord_no\": 2}, \"account_snapshot\": {\"api_call_count\": 2, \"ok_count\": 1}}, \"chart_structure_decision_hint_summary\": {\"applied_examples\": [{\"run_id\": \"R1\", \"entry_style\": \"pullback\"}], \"applied_count\": 1}}}")


def _h(x):
    return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


GOLDEN = ['f451a825e3a61108c244bfd20cdbe1b7b5df41e416cd317cb8cf99cfc2d0bead']


def _kw(**o):
    base = dict(day="2026-10-30", payload=copy.deepcopy(FX["payload"]), operator_snapshot_freshness={"stale": False}, render_residual_positions=lambda r: ["RES"])
    base.update(o)
    return base


def _both(**o):
    return m.render_no_event_daily_markdown(**_kw(**o)), owner.render_no_event_daily_markdown(facade=m, **_kw(**o))


def test_golden_parity():
    a, b = _both()
    assert a == b and _h(a) == GOLDEN[0] and a.startswith("# Daily Report (2026-10-30)\n\nNo events found.") and a.endswith("\n")


def test_missing_data_freshness_keyerror():
    payload = copy.deepcopy(FX["payload"])
    payload.pop("data_freshness")
    for fn in (lambda: m.render_no_event_daily_markdown(**_kw(payload=payload)), lambda: owner.render_no_event_daily_markdown(facade=m, **_kw(payload=payload))):
        with pytest.raises(KeyError):
            fn()


def test_facade_helper_seams(monkeypatch):
    order = []
    for name in ("render_trade_report_integrity", "render_broker_alignment", "render_route_and_narrative_sections", "render_policy_surface_sections"):
        monkeypatch.setattr(m, name, (lambda n: (lambda p: (order.append(n), ["SEAM:" + n])[1]))(name))
    monkeypatch.setattr(m, "render_data_freshness_markdown", lambda d: ["FRESH"])
    monkeypatch.setattr(m, "render_operator_summary_snapshot", lambda s, include_system_status: ["SNAP", str(include_system_status)])
    a, b = _both()
    assert a == b and "FRESH" in a and "SNAP\nFalse" in a and "RES" in a
    assert order == ["render_trade_report_integrity", "render_broker_alignment", "render_route_and_narrative_sections", "render_policy_surface_sections"] * 2


def test_residual_callback_passed_through():
    seen = []
    a, b = _both(render_residual_positions=lambda r: (seen.append(r), ["CB"])[1])
    assert a == b and seen == [FX["payload"]["residual_positions"]] * 2 and "CB" in a


def test_keyword_only():
    with pytest.raises(TypeError):
        m.render_no_event_daily_markdown("d", {}, {}, lambda r: [])
