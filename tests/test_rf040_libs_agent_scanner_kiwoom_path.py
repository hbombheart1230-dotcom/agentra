"""RF-040 libs/agent/scanner: kiwoom/hybrid candidate path with a faked provider.

Measured 68% before (lines 29-38, 86-90, 102, 106-107 uncovered). The Kiwoom
provider ``build_kiwoom_candidate_rows`` is replaced in the scanner module's
namespace, so no network/broker/state is touched. Explicit raises keep the
checks live under ``python -O``.
"""
from __future__ import annotations

import pytest

from libs.agent import scanner as sc
from libs.agent.scanner import Scanner
from libs.agent.strategist import Plan


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


@pytest.fixture()
def provider(monkeypatch):
    calls = []
    state = {"rows": []}

    def fake(*, state, top_pool, condition_limit, include_change_rate):
        calls.append({"top_pool": top_pool, "condition_limit": condition_limit, "include_change_rate": include_change_rate})
        return list(provider_rows["rows"]), {"meta": 1}

    provider_rows = state
    monkeypatch.setattr(sc, "build_kiwoom_candidate_rows", fake)
    monkeypatch.delenv("TOP_N_CANDIDATES", raising=False)
    return calls, provider_rows


def test_helpers():
    _eq((sc._to_int("7.9", 1), sc._to_int("x", 5), sc._to_int(None, 3)), (7, 5, 3))
    _eq(sc._norm_symbol(" 005930 "), sc.normalize_symbol(" 005930 "))


def test_extract_theme_map_merges_sources_and_ignores_bad_shapes():
    ctx = {"theme_map": {" AI ": ["005930", "000660", ""], "": ["x"], "bad": "notalist"},
           "sector_map": {"ai": ["035420"], "chips": ["000660"]}}
    out = sc._extract_theme_map(ctx)
    _eq(sorted(out), ["ai", "bad", "chips"])
    _eq(out["ai"], {sc._norm_symbol("005930"), sc._norm_symbol("000660"), sc._norm_symbol("035420")})
    _eq(out["bad"], set())                       # non-list symbols leave an empty bucket
    _eq(sc._extract_theme_map({"theme_map": "x", "sector_map": None}), {})
    _eq(sc._extract_theme_map({}), {})


def test_kiwoom_source_ranks_provider_rows_and_passes_limits(provider):
    calls, state = provider
    state["rows"] = [{"symbol": "000660", "score": 1.0, "why": "rank"}, {"symbol": "005930", "score": 3.0, "score_breakdown": {"a": 1}},
                     {"symbol": "", "score": 9.0}, {"symbol": "035420", "score": "bad"}]
    out = Scanner().scan(plan=Plan("t", {}), context={"top_n_candidates": 3, "top_candidate_pool": "10", "candidate_condition_limit": 4})
    # Quirk pinned: the top_n slice (3) is applied to the RAW provider rows before blank symbols are dropped, so the
    # blank-symbol row consumes one of the 3 slots and 035420 (4th row) is cut off.
    _eq([r["symbol"] for r in out["ranked"]], [sc._norm_symbol("005930"), sc._norm_symbol("000660")])
    _eq([r["score"] for r in out["ranked"]], [3.0, 1.0])
    _eq(out["candidates"], ["000660", "005930", ""])                          # the raw (unranked, unfiltered) slice
    _eq((out["ranked"][0]["score_breakdown"], out["ranked"][0]["source"], out["ranked"][1]["source"]), ({"a": 1}, "kiwoom", "rank"))
    _eq((out["intents"], out["candidate_source"], out["top_stock"], out["candidate_pool_size"]), ([], "kiwoom", sc._norm_symbol("005930"), 2))
    _eq(calls, [{"top_pool": 10, "condition_limit": 10, "include_change_rate": True}])   # condition_limit floors at top_pool; change-rate default True
    # a non-numeric score is kept as 0.0 (4th row visible once the limit allows it)
    again = Scanner().scan(plan=Plan("t", {}), context={"top_n_candidates": 4})
    _eq([r["score"] for r in again["ranked"]], [3.0, 1.0, 0.0])


def test_candidate_limit_truncates_before_scoring_overrides(provider):
    calls, state = provider
    state["rows"] = [{"symbol": f"{i:06d}", "score": float(i)} for i in range(1, 8)]
    out = Scanner().scan(plan=Plan("t", {}), context={"top_n_candidates": 2})
    _eq(len(out["ranked"]), 2)                                                      # only the first 2 provider rows are considered
    _eq(out["candidates"], ["000001", "000002"])
    # candidate_scores can reorder within the kept rows
    out2 = Scanner().scan(plan=Plan("t", {}), context={"top_n_candidates": 2, "candidate_scores": {"000001": 99}})
    _eq(out2["top_stock"], "000001")
    _eq(Scanner().scan(plan=Plan("t", {}), context={"top_n_candidates": 0})["candidate_pool_size"], 1)   # limit floors at 1


def test_theme_filter_applies_only_when_themes_and_index_intersect(provider):
    calls, state = provider
    state["rows"] = [{"symbol": "005930", "score": 2.0}, {"symbol": "000660", "score": 1.0}]
    ctx = {"theme_map": {"ai": ["000660"]}}
    filtered = Scanner().scan(plan=Plan("t", {}, themes=["AI"]), context=dict(ctx))
    _eq([r["symbol"] for r in filtered["ranked"]], ["000660"])
    unmatched = Scanner().scan(plan=Plan("t", {}, themes=["other"]), context=dict(ctx))
    _eq(len(unmatched["ranked"]), 2)                                                # no allowed symbols -> no filtering
    no_index = Scanner().scan(plan=Plan("t", {}, themes=["ai"]), context={})
    _eq(len(no_index["ranked"]), 2)
    _eq(filtered["themes"], ["AI"])


def test_strategist_candidates_are_the_fallback_when_provider_returns_nothing(provider):
    calls, state = provider
    state["rows"] = []
    out = Scanner().scan(plan=Plan("t", {}, candidates=["005930", "000660", ""]), context={"candidate_scores": {"000660": 5}})
    _eq([r["symbol"] for r in out["ranked"]], [sc._norm_symbol("000660"), sc._norm_symbol("005930")])
    _eq(out["ranked"][0]["source"], "kiwoom")
    _eq(Scanner().scan(plan=Plan("t", {}), context={})["ranked"], [])


def test_hybrid_and_market_data_sources_call_the_provider_but_static_does_not(provider):
    calls, state = provider
    state["rows"] = [{"symbol": "005930", "score": 1.0}]
    for src, expect_calls in (("hybrid", 1), ("static", 0), ("strategist", 0), ("auto", 1)):
        calls.clear()
        out = Scanner().scan(plan=Plan("t", {}), context={"candidate_source": src})
        _eq((src, len(calls)), (src, expect_calls))
        _eq(out["candidate_source"], {"auto": "hybrid"}.get(src, "static" if src in {"strategist"} else src))


def test_include_change_rate_flag_comes_from_runtime_policy(provider):
    calls, state = provider
    Scanner().scan(plan=Plan("t", {}), context={"kiwoom_candidate_include_change_rate": False})
    _eq(calls[-1]["include_change_rate"], False)
    Scanner().scan(plan=Plan("t", {}), context={})
    _eq(calls[-1]["include_change_rate"], True)


def test_explicit_intents_pass_through_without_calling_the_provider(provider):
    calls, state = provider
    intents = [{"side": "buy"}]
    _eq(Scanner().scan(plan=Plan("t", {}), context={"intents": intents}), intents)
    _eq(calls, [])
    # a non-dict element disables the pass-through
    out = Scanner().scan(plan=Plan("t", {}), context={"intents": [{"a": 1}, "x"], "candidate_source": "static"})
    _eq(out["intents"], [])
