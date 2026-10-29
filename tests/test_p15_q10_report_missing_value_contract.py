"""P15-5 (2026-10-29 C02): render_forward_validation_report missing / unobservable value display contract (pure, input-immutable)."""
from __future__ import annotations

import copy

from libs.reporting.baseline_samsung_hynix.forward_validation.report import _value, render_forward_validation_report

REACTIONS = {"targets": {"KOSPI": {"points": {"CLOSE": {"price": None, "unverified_observation": {"price": 101.2, "capture_status": "PENDING", "observed_at_kst": "2026-10-29T15:25:00+09:00"}}},
                                    "forward_windows": {"09:00": {"return_to_close_pct": None, "mfe_pct": None, "mae_pct": None, "status": "PARTIAL"}}}}}
PREOPEN = {"capture_status": "DATA_UNAVAILABLE", "signals": {}}


def render(**over):
    kw = dict(day="2026-10-29", preopen=PREOPEN, reactions=REACTIONS, expected_actual={}, shadow={}, cumulative={})
    kw.update(over)
    return render_forward_validation_report(**kw)


def section(md, title):
    head = f"## {title}"
    start = md.index(head)
    rest = md[start + len(head):]
    nxt = rest.find("\n## ")
    return rest if nxt < 0 else rest[:nxt]


def test_unavailable_snapshot_and_unverified_close_are_shown_but_labeled_not_calculation_usable():
    md = render()
    assert "- Preopen snapshot: `DATA_UNAVAILABLE`" in md and "## Captured But Not Calculation-Usable" in md
    unverified = section(md, "Captured But Not Calculation-Usable")
    assert "These values are shown for operations only and are excluded from returns and scoring." in unverified
    assert "| KOSPI | CLOSE | 101.2000 | PENDING | 2026-10-29T15:25:00+09:00 |" in unverified
    assert "prospective_shadow_only" in md and "Historical backfill / threshold optimization / ML / orders: disabled" in md


def test_missing_returns_are_dashes_never_zero_and_status_is_kept():
    md = render()
    forward = section(md, "Forward Quality By Checkpoint")
    assert "| KOSPI | 09:00 | - | - | - | PARTIAL |" in forward and "0.0000" not in forward
    checkpoints = section(md, "Actual Reaction Checkpoints")
    row = next(l for l in checkpoints.splitlines() if l.startswith("| KOSPI "))
    assert row == "| KOSPI | - | - | - | - | - | - | - | - | - | - | - |"                                  # gap, 8 checkpoint prices (CLOSE price None -> '-'), high, low
    assert "101.2" not in checkpoints                                                                       # the unverified value never appears as a CLOSE price


def test_unverified_price_is_not_promoted_into_calculation_sections():
    md = render()
    for title in ("Expected vs Actual", "Actual Reaction Checkpoints", "Forward Quality By Checkpoint", "Shadow Entry Comparison", "Prospective Cumulative"):
        assert "101.2" not in section(md, title), title


def test_numeric_return_one_point_two_five_renders_with_four_decimals_and_percent():
    reactions = copy.deepcopy(REACTIONS)
    reactions["targets"]["KOSPI"]["forward_windows"]["09:00"].update({"return_to_close_pct": 1.25, "mfe_pct": 2.0, "mae_pct": -0.5, "status": "OBSERVED"})
    reactions["targets"]["KOSPI"]["opening_gap_pct"] = 0.4
    md = render(reactions=reactions)
    forward = section(md, "Forward Quality By Checkpoint")
    assert "| KOSPI | 09:00 | 1.2500% | 2.0000% | -0.5000% | OBSERVED |" in forward
    assert "| KOSPI | 0.4000% |" in section(md, "Actual Reaction Checkpoints")


def test_zero_values_are_not_dashes_and_none_is_not_zero():
    assert _value(None) == "-" and _value(0) == "0" and _value(0.0) == "0.0000" and _value(1.25, "%") == "1.2500%" and _value("") == ""
    reactions = copy.deepcopy(REACTIONS)
    reactions["targets"]["KOSPI"]["forward_windows"]["09:00"].update({"return_to_close_pct": 0.0, "mfe_pct": 0.0, "mae_pct": None})
    forward = section(render(reactions=reactions), "Forward Quality By Checkpoint")
    assert "| KOSPI | 09:00 | 0.0000% | 0.0000% | - | PARTIAL |" in forward


def test_headers_order_and_final_newline_are_stable():
    md = render()
    titles = [l for l in md.splitlines() if l.startswith("## ")]
    assert titles == ["## Preopen States", "## Expected vs Actual", "## Actual Reaction Checkpoints", "## Captured But Not Calculation-Usable", "## Forward Quality By Checkpoint", "## Shadow Entry Comparison", "## Prospective Cumulative"]
    assert md.startswith("# Q10 Korea Lead-Market Forward Validation\n") and md.endswith("\n") and not md.endswith("\n\n")
    assert "| Target | Gap | 09:00 | 09:03 | 09:05 | 09:10 | 09:15 | 09:30 | 10:00 | Close | High | Low |" in md


def test_inputs_are_not_mutated_and_rendering_is_deterministic():
    pre, rea, exp, sh, cu = copy.deepcopy(PREOPEN), copy.deepcopy(REACTIONS), {"rows": []}, {"summary": []}, {"summary": []}
    snapshot = copy.deepcopy((pre, rea, exp, sh, cu))
    a = render_forward_validation_report(day="d", preopen=pre, reactions=rea, expected_actual=exp, shadow=sh, cumulative=cu)
    b = render_forward_validation_report(day="d", preopen=pre, reactions=rea, expected_actual=exp, shadow=sh, cumulative=cu)
    assert (pre, rea, exp, sh, cu) == snapshot and a == b


def test_empty_inputs_default_to_waiting_and_insufficient_evidence_without_error():
    md = render_forward_validation_report(day="d", preopen={}, reactions={}, expected_actual={}, shadow={}, cumulative={})
    assert "- Preopen snapshot: `WAITING`" in md and "- Evidence: `INSUFFICIENT_EVIDENCE`" in md and "- Days: `0`" in md and "Captured But Not Calculation-Usable" not in md


def test_expected_vs_actual_and_shadow_rows_render_none_gap_as_dash():
    ea = {"rows": [{"target": "kospi", "expected_state": "RISK_ON", "opening_gap_pct": None, "reaction_state": "INSUFFICIENT_EVIDENCE", "evaluation_bucket": "LEAD_MARKET_SIGNAL"}]}
    shadow = {"evidence_status": "INSUFFICIENT_EVIDENCE", "summary": [{"target": "kospi", "policy": "ENTRY_0900", "trade_count": 0, "win_rate": None, "average_return_pct": None, "median_return_pct": None,
                                                                    "profit_factor": None, "average_mfe_pct": None, "average_mae_pct": None}]}
    md = render(expected_actual=ea, shadow=shadow)
    assert "| kospi | RISK_ON | - | INSUFFICIENT_EVIDENCE | LEAD_MARKET_SIGNAL |" in section(md, "Expected vs Actual")
    assert "| kospi | ENTRY_0900 | 0 | - | - | - | - | - | - |" in section(md, "Shadow Entry Comparison")
