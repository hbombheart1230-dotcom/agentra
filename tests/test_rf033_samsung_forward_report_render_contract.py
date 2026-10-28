"""RF-033 C3: samsung forward_validation report renderer (pure string contract)."""
from __future__ import annotations

from libs.reporting.baseline_samsung_hynix.forward_validation import report as rp


def _render(**kw):
    base = dict(day="2026-09-07", preopen={}, reactions={}, expected_actual={}, shadow={}, cumulative={})
    base.update(kw)
    return rp.render_forward_validation_report(**base)


def test_value_formatting():
    assert rp._value(0) == "0" and rp._value(0.0) == "0.0000" and rp._value("") == ""
    assert rp._value(None) == "-" and rp._value(1.23456789, "%") == "1.2346%" and rp._value(5, "%") == "5%" and rp._value("INF") == "INF"


def test_empty_inputs_render_all_sections_without_rows():
    md = _render()
    for h in ("# Q10 Korea Lead-Market Forward Validation", "## Preopen States", "## Expected vs Actual", "## Actual Reaction Checkpoints",
              "## Forward Quality By Checkpoint", "## Shadow Entry Comparison", "## Prospective Cumulative"):
        assert h in md
    assert "Captured But Not Calculation-Usable" not in md and md.endswith("\n")
    assert "- Preopen snapshot: `WAITING`" in md and "- Evidence: `INSUFFICIENT_EVIDENCE`" in md and "- Days: `0`" in md
    assert "SAMSUNG_SPECIFIC_EVENT=False" in md and "| SK Hynix | - | - | - | - |" in md


def test_populated_rows_and_unverified_section():
    pre = {"capture_status": "CAPTURED", "signals": {"sk_hynix": {"state": "POSITIVE", "score": 1.0, "confidence": "HIGH"}, "hynix_extension": {"state": "EXTENDED"},
                                                       "samsung": {"state": "NEUTRAL", "score": 0.65, "confidence": "LOW"}, "korea_market": {"state": "RISK_ON", "score": 3.0, "evidence_status": "PARTIAL"}},
           "samsung_event": {"samsung_specific_event": True}}
    ea = {"rows": [{"target": "samsung", "expected_state": "POSITIVE", "opening_gap_pct": 0.5, "reaction_state": "FAIR_REACTION", "evaluation_bucket": "LEAD_MARKET_SIGNAL"}]}
    react = {"targets": {"kospi": {"opening_gap_pct": None, "day_high": 2.5, "day_low": None,
                                   "points": {"09:00": {"price": 100.0}, "CLOSE": {"status": "PENDING", "unverified_observation": {"price": 9.0, "capture_status": "LATE_MISSED", "observed_at_kst": None}}},
                                   "forward_windows": {"09:00": {"return_to_close_pct": 1.5, "mfe_pct": 2.0, "mae_pct": None, "status": "PARTIAL"}}}}}
    shadow = {"evidence_status": "AVAILABLE", "summary": [{"target": "samsung", "policy": "ENTRY_0900", "trade_count": 3, "win_rate": 66.6667, "average_return_pct": 0.5,
                                                          "median_return_pct": 0.4, "profit_factor": "INF", "average_mfe_pct": 1.0, "average_mae_pct": None}]}
    cum = {"day_count": 2, "observed_outcome_count": 5, "summary": [{"target": "samsung", "policy": "ENTRY_0900", "evaluation_bucket": "LEAD_MARKET_SIGNAL", "extension_state": "N/A",
                                                                     "trade_count": 5, "win_rate": 60.0, "average_return_pct": 0.1, "median_return_pct": 0.2, "profit_factor": 1.5, "max_drawdown_pct": -1.0}]}
    md = _render(preopen=pre, reactions=react, expected_actual=ea, shadow=shadow, cumulative=cum)
    assert "- Preopen snapshot: `CAPTURED`" in md and "| SK Hynix | POSITIVE | 1.0000 | HIGH | EXTENDED |" in md
    assert "SAMSUNG_SPECIFIC_EVENT=True" in md and "| KOSPI / KOSDAQ | RISK_ON | 3.0000 | PARTIAL |" in md
    assert "| samsung | POSITIVE | 0.5000% | FAIR_REACTION | LEAD_MARKET_SIGNAL |" in md
    assert "| kospi | - | 100.0000 | - | - | - | - | - | - | - | 2.5000 | - |" in md
    assert "## Captured But Not Calculation-Usable" in md and "| kospi | CLOSE | 9.0000 | LATE_MISSED | - |" in md
    assert "| kospi | 09:00 | 1.5000% | 2.0000% | - | PARTIAL |" in md
    assert "| samsung | ENTRY_0900 | 3 | 66.6667% | 0.5000% | 0.4000% | INF | 1.0000% | - |" in md
    assert "- Days: `2`" in md and "| samsung | ENTRY_0900 | LEAD_MARKET_SIGNAL | N/A | 5 | 60.0000% | 0.1000% | 0.2000% | 1.5000 | -1.0000% |" in md
