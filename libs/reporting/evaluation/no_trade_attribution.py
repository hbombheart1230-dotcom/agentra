from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from libs.reporting.json_array_stream import iter_json_array
from libs.reporting.evaluation import fast07_attribution_projection as _attr
from libs.reporting.evaluation import fast07_chain_render_projection as _render
from libs.reporting.evaluation.artifact_inventory import (
    is_regular_session_evaluation_row,
    is_synthetic_evaluation_row,
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


_mapping = _attr.mapping
_num = _attr.num
_pct = _render.no_trade_pct
_top = _attr.top
_q9_window_view = _attr.q9_window_view


def _q9_windows(reports_root: Path, day: str) -> list[dict[str, Any]]:
    # Streamed and reduced to the fields the report reads: the ~120 MB windows file is no longer parsed
    # whole (and its regular rows are not all kept) just to count a handful of fields per window.
    path = reports_root / "operator_summary" / "daily" / day / "q9_decision_windows.json"
    windows: list[dict[str, Any]] = []
    try:
        for row in iter_json_array(path, "windows"):
            if isinstance(row, dict) and not is_synthetic_evaluation_row(row) and is_regular_session_evaluation_row(row):
                windows.append(_q9_window_view(row))
    except ValueError:
        return []  # unreadable windows file == no windows (what _read_json -> {} gave)
    return windows


def _baseline_samsung(reports_root: Path, day: str) -> dict[str, Any]:
    payload = _read_json(
        reports_root
        / "evaluation"
        / "baseline_samsung_hynix"
        / day
        / "baseline_samsung_hynix_forward_returns.json"
    )
    return _attr.samsung_baseline(payload)


def _q11_opening(reports_root: Path, day: str) -> dict[str, Any]:
    root = reports_root / "evaluation" / "opportunity_engine_shadow" / day
    payload = _read_json(root / "opportunity_engine_daily_report.json")
    signals = _read_json(root / "opportunity_engine_signals.json")
    virtual = _read_json(root / "opportunity_engine_virtual_trades.json")
    return _attr.q11_opening(payload, signals, virtual)


def _q12_btc_woori(reports_root: Path, day: str) -> dict[str, Any]:
    payload = _read_json(
        reports_root
        / "evaluation"
        / "baseline_btc_woori_tech"
        / day
        / "baseline_btc_woori_forward_returns.json"
    )
    return _attr.btc_woori_baseline(payload)


def build_no_trade_attribution_report(
    *,
    day: str,
    reports_root: Path,
    trade_count: int,
) -> dict[str, Any]:
    reports_root = Path(reports_root)
    windows = _q9_windows(reports_root, day)
    surface = _attr.q9_decision_surface(windows)
    counters = surface["counters"]
    commander_decisions = counters["commander_decisions"]
    approve_noop = surface["approve_noop"]
    approve_buy = surface["approve_buy"]

    q11 = _q11_opening(reports_root, day)
    no_trade_class = "NOT_NO_TRADE_DAY"
    primary_issue = ""
    if trade_count <= 0:
        if not windows:
            no_trade_class = "MISSING_Q9_EVIDENCE"
            primary_issue = "q9_windows_missing"
        elif approve_noop > 0:
            q11_avg_net = _num(q11.get("avg_net_return_pct"))
            if int(q11.get("virtual_trades") or 0) > 0 and (
                q11_avg_net is not None and q11_avg_net > 0
            ):
                no_trade_class = "POSSIBLE_OVER_FILTERING"
                primary_issue = "positive_net_shadow_blocked_after_commander_approval"
            else:
                no_trade_class = "FILTERING_REVIEW_REQUIRED"
                primary_issue = (
                    "commander_approved_monitor_noop_requires_forward_review"
                )
        elif commander_decisions.get("reject", 0) > 0:
            no_trade_class = "UPSTREAM_REJECTED"
            primary_issue = "commander_rejected_candidates"
        else:
            no_trade_class = "NO_ACTIONABLE_CANDIDATE"
            primary_issue = "no_commander_approved_candidate"

    shadow_opportunity = "UNAVAILABLE"
    if q11.get("available"):
        virtual_trades = int(q11.get("virtual_trades") or 0)
        avg_net = _num(q11.get("avg_net_return_pct"))
        avg_mfe = _num(q11.get("avg_mfe_pct"))
        if virtual_trades <= 0:
            shadow_opportunity = "NO_SHADOW_TRADES"
        elif avg_net is not None and avg_net > 0:
            shadow_opportunity = "POSITIVE_NET_SHADOW"
        elif avg_mfe is not None and avg_mfe > 0:
            shadow_opportunity = "MFE_ONLY_SHADOW"
        else:
            shadow_opportunity = "NEGATIVE_SHADOW"

    return {
        "schema_version": "no_trade_attribution_report.v1",
        "behavior_effect": "observation_only",
        "day": day,
        "trade_count": int(trade_count),
        "q9_window_count": int(len(windows)),
        "no_trade_class": no_trade_class,
        "primary_issue": primary_issue,
        "commander_approve_monitor_noop_count": int(approve_noop),
        "commander_approve_monitor_buy_count": int(approve_buy),
        "commander_decisions": _top(commander_decisions),
        "commander_reasons": _top(counters["commander_reasons"]),
        "commander_details": _top(counters["commander_details"]),
        "monitor_intents": _top(counters["monitor_intents"]),
        "monitor_noop_reasons": _top(counters["monitor_noop_reasons"]),
        "scanner_top1": _top(counters["scanner_top1"]),
        "strategist_selected": _top(counters["strategist_selected"]),
        "commander_selected": _top(counters["commander_selected"]),
        "shadow_opportunity_status": shadow_opportunity,
        "q10_samsung_hynix": _baseline_samsung(reports_root, day),
        "q11_opening_opportunity": q11,
        "q12_btc_woori": _q12_btc_woori(reports_root, day),
        "interpretation": {
            "scope": "Explains no-trade or sparse-trade days without changing execution behavior.",
            "q13_q14_boundary": "If trade_count is zero, Q13/Q14 trade attribution remains insufficient; use this report for over-filtering and missed-opportunity validation.",
        },
    }


render_no_trade_attribution_report = _render.render_no_trade_attribution_report
