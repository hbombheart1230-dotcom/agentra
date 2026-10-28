"""RF-054 libs/performance/performance_aggregator: reason→pattern classification and extraction order.

Closes the measured gaps (lines 19, 23-26, 39, 60, 122-123, 145-146, 180-208 of
the aggregator, lines 23-24 / 50-58 of playbook_stats). Pure dicts and tmp_path
only. Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import pytest

from libs.performance import performance_aggregator as pa
from libs.performance import playbook_stats as ps


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


@pytest.mark.parametrize("reason,want", [
    (None, ""), ("", ""), ("  ", ""), ("Pullback entry", "pullback"), ("REBOUND from low", "pullback"), ("clean breakout", "breakout"),
    ("near recent_high", "breakout"), ("trend reversal", "reversal"), ("vwap reclaim", "vwap_reclaim"), ("reclaim of ma", "vwap_reclaim"),
    ("pullback breakout", "pullback"),      # first matching rule wins
    ("unrelated words", ""),
])
def test_entry_pattern_classification(reason, want):
    _eq(pa._classify_entry_pattern(reason), want)


@pytest.mark.parametrize("reason,want", [
    (None, ""), ("", ""), ("peak_drawdown hit", "peak_drawdown"), ("hard_stop", "hard_stop"), ("take_profit", "take_profit"),
    ("locked profit", "take_profit"), ("intraday_low_break", "intraday_low_break"), ("time limit", "time_exit"),
    ("no_position left", "no_position"), ("something else", ""),
    ("hard_stop at time", "hard_stop"),       # rule order: hard_stop before time
    ("profit by time", "take_profit"),        # profit before time
])
def test_exit_pattern_classification(reason, want):
    _eq(pa._classify_exit_pattern(reason), want)


def test_conversion_helpers_and_text_dict():
    _eq((pa._safe_float("1.5"), pa._safe_float("x"), pa._safe_float(None, None), pa._safe_float("x", 7.0)), (1.5, 0.0, None, 7.0))
    _eq((pa._safe_int("3.9"), pa._safe_int("x"), pa._safe_int(None, 4)), (3, 0, 4))
    _eq((pa._text(None), pa._text("  a "), pa._text(5)), ("", "a", "5"))
    _eq((pa._dict({"a": 1}), pa._dict("x"), pa._dict(None)), ({"a": 1}, {}, {}))


def test_entry_exit_reason_extraction_priority():
    feedback = {"strategist_feedback_input": {"entry_reason": "FB", "exit_reason": "FBX"}, "entry_reason": "top", "exit_reason": "topx"}
    _eq((pa._extract_entry_reason(feedback), pa._extract_exit_reason(feedback)), ("FB", "FBX"))
    _eq((pa._extract_entry_reason({"entry_reason": "top"}), pa._extract_exit_reason({"exit_reason": "topx"})), ("top", "topx"))
    _eq(pa._extract_exit_reason({"trade_outcome": {"exit_reason": "outcome"}, "exit": {"reason_human": "h"}}), "outcome")
    _eq(pa._extract_entry_reason({"entry": {"reason_human": "h", "summary": "s"}}), "h")
    _eq(pa._extract_entry_reason({"lifecycle": {"entry": {"summary": "from lifecycle"}}}), "from lifecycle")
    _eq(pa._extract_exit_reason({"lifecycle": {"exit": {"summary": "lx"}}}), "lx")
    _eq((pa._extract_entry_reason({}), pa._extract_exit_reason({})), ("", ""))
    # a top-level "entry" dict outranks lifecycle.entry
    _eq(pa._extract_entry_reason({"entry": {"summary": "top"}, "lifecycle": {"entry": {"summary": "life"}}}), "top")


def test_pattern_type_extraction_prefers_explicit_value_then_classification_and_lowercases():
    _eq(pa._extract_entry_pattern_type({"strategist_feedback_input": {"entry_pattern_type": "FB_Type"}, "entry_pattern_type": "top"}), "fb_type")
    _eq(pa._extract_entry_pattern_type({"entry_pattern_type": "TopType"}), "toptype")
    _eq(pa._extract_entry_pattern_type({"entry_reason": "a breakout"}), "breakout")
    _eq(pa._extract_exit_pattern_type({"exit_pattern_type": "Custom"}), "custom")
    _eq(pa._extract_exit_pattern_type({"exit_reason": "hard_stop reached"}), "hard_stop")
    _eq((pa._extract_entry_pattern_type({}), pa._extract_exit_pattern_type({})), ("", ""))


def test_symbol_and_playbook_market_regime_extraction():
    _eq(pa._extract_symbol({"symbol": " abc ", "lifecycle": {"entry": {"symbol": "zzz"}}}), "ABC")
    _eq(pa._extract_symbol({"lifecycle": {"entry": {"symbol": "zzz"}}}), "ZZZ")
    _eq(pa._extract_symbol({}), "")
    _eq(pa._extract_playbook({"strategist_summary": {"playbook": " Alpha "}}), "alpha")
    _eq(pa._extract_playbook({"lifecycle": {"entry": {"strategist_context": {"playbook": "Ctx"}}}}), "ctx")
    _eq(pa._extract_playbook({}), "")
    _eq(pa._extract_market_regime({"strategist_summary": {"market_regime": "Bull", "regime": "x"}}), "bull")
    _eq(pa._extract_market_regime({"strategist_summary": {"regime": "Bear"}}), "bear")


def test_return_and_pnl_candidates_skip_blank_and_non_numeric():
    _eq(pa._extract_return_value({"trade_outcome": {"return_pct": "bad", "realized_return_pct": "2.5"}}), 2.5)
    _eq(pa._extract_return_value({"summary": {"return_pct": 1.0}}), 1.0)
    _eq(pa._extract_return_value({"trade_outcome": {"return_pct": ""}, "summary": {}}), None)
    _eq(pa._extract_pnl_value({"trade_outcome": {"pnl": "x", "realized_pnl": 3}}), 3.0)
    _eq(pa._extract_pnl_value({"summary": {"realized_pnl": "", "pnl": "4"}}), 4.0)
    _eq(pa._extract_pnl_value({}), None)


def test_combo_stats_label_unknown_halves():
    rows = [{"entry_pattern_type": "breakout", "exit_pattern_type": "hard_stop", "return": -1.0, "symbol": "A"},
            {"entry_pattern_type": "", "exit_pattern_type": "", "return": 2.0, "symbol": "B"},
            {"entry_pattern_type": "breakout", "exit_pattern_type": "hard_stop", "return": 1.0, "symbol": "C"}]
    out = pa._aggregate_entry_exit_combo_stats(rows)
    _eq(sorted(out), ["breakout -> hard_stop", "unknown -> unknown"])
    _eq((out["breakout -> hard_stop"]["trade_count"], out["breakout -> hard_stop"]["win_count"], out["breakout -> hard_stop"]["loss_count"]), (2, 1, 1))
    _eq(out["unknown -> unknown"]["symbols"], ["B"])
    _eq(pa._is_win({"return": None, "pnl": None}), None)
    _eq((pa._is_win({"return": 0.0}), pa._is_win({"return": "", "pnl": 1.0})), (False, True))


def test_playbook_stats_helper_gaps():
    _eq((ps._safe_float("x"), ps._safe_float("2"), ps._safe_float(None, 9)), (0.0, 2.0, 9.0))
    _eq(ps._extract_playbook({}), "unknown")
    _eq(ps._extract_playbook({"strategist_summary": {"playbook": " Beta "}}), "beta")
    _eq(ps._extract_return({"trade_outcome": {"return_pct": "bad", "pnl": "5"}}), 5.0)         # bad return falls through to pnl
    _eq(ps._extract_return({"trade_outcome": {"return_pct": "bad", "pnl": "also bad"}}), None)
    _eq(ps._extract_return({"trade_outcome": {"realized_return_pct": 1.5}}), 1.5)
    _eq(ps._extract_return({}), None)
    _eq(ps._max_drawdown([1, -2, -1, 3]), 3.0)
