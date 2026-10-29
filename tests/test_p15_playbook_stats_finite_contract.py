"""P15 C02-3 (FAST-3): playbook stats ignore non-finite returns and tolerate bad recent_window."""
from __future__ import annotations

import copy
import json

import pytest

from libs.performance import playbook_stats as ps


def _bundle(trade_id, outcome=None, playbook="pb", day="2026-10-20"):
    return {"day": day, "trade_id": trade_id, "strategist_summary": {"playbook": playbook}, "trade_outcome": outcome or {}}


@pytest.fixture
def truth(monkeypatch):
    table = {}
    monkeypatch.setattr(ps, "extract_truth_outcome_from_bundle", lambda b: table.get(b["trade_id"], {"available": False}))
    return table


def test_nonfinite_returns_are_excluded_but_finite_ones_kept(truth):
    truth["t1"] = {"available": True, "return": "nan"}
    truth["t2"] = {"available": True, "return": 0.2}
    bundles = [
        _bundle("t1"), _bundle("t2"),
        _bundle("t3", {"return_pct": "inf"}),
        _bundle("t4", {"return_pct": "bad", "realized_return_pct": "0.1"}),
        _bundle("t5", {"pnl": "-inf"}),
        _bundle("t6", {"return_pct": float("nan"), "pnl": "0.3"}),
    ]
    snap = copy.deepcopy(bundles)
    out = ps.calculate_playbook_stats(bundles, day="2026-10-20")
    assert bundles == snap
    row = out["playbooks"]["pb"]
    assert row["usage_count"] == 6                                              # every bundle still counts as a use
    assert row["recent_performance"] == [0.2, 0.1, 0.3]                          # t2, t4 fallback, t6 pnl fallback
    assert row["avg_return"] == pytest.approx(0.2) and row["win_rate"] == 1.0
    json.dumps(out, allow_nan=False)


def test_truth_available_but_nonfinite_does_not_fall_back_to_trade_outcome(truth):
    truth["t1"] = {"available": True, "return": "inf"}
    out = ps.calculate_playbook_stats([_bundle("t1", {"return_pct": "5"})])
    assert out["playbooks"]["pb"]["recent_performance"] == [] and out["playbooks"]["pb"]["avg_return"] == 0.0


def test_extract_return_unit_cases(truth):
    truth["a"] = {"available": True, "return": ""}
    assert ps._extract_return(_bundle("a")) is None
    assert ps._extract_return(_bundle("b", {"return_pct": "", "realized_return_pct": "0.7"})) == 0.7
    assert ps._extract_return(_bundle("c", {"pnl": "x"})) is None
    assert ps._extract_return(_bundle("d")) is None


@pytest.mark.parametrize("window,expected", [("nan", 5), ("inf", 5), ("bad", 5), (None, 5), (0, 1), (-2, 1), ("3", 3), (2.9, 2), (True, 1)])
def test_recent_window_normalization(truth, window, expected):
    bundles = [_bundle(f"t{i}", {"return_pct": str(i)}) for i in range(1, 8)]
    out = ps.calculate_playbook_stats(bundles, recent_window=window)
    assert out["recent_window"] == expected
    assert out["playbooks"]["pb"]["recent_performance"] == [float(i) for i in range(1, 8)][-expected:]


def test_valid_window_three_parity_and_stability_bounds(truth):
    bundles = [_bundle(f"t{i}", {"return_pct": r}) for i, r in enumerate([1, -2, 3, 0.5], start=1)]
    out = ps.calculate_playbook_stats(bundles, day="2026-10-20", recent_window=3)
    row = out["playbooks"]["pb"]
    assert out["schema_version"] == "playbook_stats.v1" and out["day"] == "2026-10-20" and out["recent_window"] == 3
    assert row["recent_performance"] == [-2.0, 3.0, 0.5] and row["usage_count"] == 4 and row["win_rate"] == 0.75
    assert row["avg_return"] == pytest.approx(0.625) and row["drawdown"] == 2.0 and 0.0 <= row["stability_score"] <= 1.0
    assert out["generated_at"].endswith("+00:00")


def test_safe_float_nonfinite_default():
    assert ps._safe_float("nan", 2.0) == 2.0 and ps._safe_float("inf") == 0.0 and ps._safe_float("1.5") == 1.5
