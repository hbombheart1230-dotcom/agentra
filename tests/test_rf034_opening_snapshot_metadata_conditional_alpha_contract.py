"""RF-034 C3: opening market_snapshot / symbol_metadata (refresh collector stubbed) and quant conditional_alpha (tmp only)."""
from __future__ import annotations

import json
import sys
import types
from datetime import datetime, timedelta, timezone

import pytest

from libs.reporting.opening_rank1_shadow import market_snapshot as ms
from libs.reporting.opening_rank1_shadow import symbol_metadata as sm
from libs.reporting.quant_trade_diagnosis import conditional_alpha as ca

KST = timezone(timedelta(hours=9))
DAY = "2026-09-07"


def ep(h, m, s=0):
    return int(datetime(2026, 9, 7, h, m, s, tzinfo=KST).timestamp())


# ---------- market snapshot ----------

def _snap_file(root, name, payload):
    d = root / DAY
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")


def test_snapshot_epoch_prefers_generated_at_then_filename_clock(tmp_path):
    p = tmp_path / "090500_macro_indicators.json"
    assert ms._snapshot_epoch(p, {"generated_at": "2026-09-07T00:05:00Z"}, day=DAY) == ep(9, 5)
    assert ms._snapshot_epoch(p, {"generated_at": "garbage"}, day=DAY) == ep(9, 5)               # falls back to filename clock
    assert ms._snapshot_epoch(p, {}, day=DAY) == ep(9, 5)
    assert ms._snapshot_epoch(tmp_path / "xx.json", {}, day=DAY) == 0
    assert ms._snapshot_epoch(tmp_path / "256100_x.json", {}, day=DAY) == 0                       # invalid clock


def test_timeline_sorted_and_skips_bad_files(tmp_path):
    _snap_file(tmp_path, "090500_macro_indicators.json", {"index_moves": {"kospi_pct": 1.0}})
    _snap_file(tmp_path, "090000_macro_indicators.json", {"index_moves": {"kospi_pct": 0.5}})
    _snap_file(tmp_path, "bad_macro_indicators.json", "{nope")
    _snap_file(tmp_path, "list_macro_indicators.json", "[1]")
    _snap_file(tmp_path, "noclock_macro_indicators.json", {})
    tl = ms.load_market_snapshot_timeline(day=DAY, macro_root=tmp_path)
    assert [t["snapshot_epoch"] for t in tl] == [ep(9, 0), ep(9, 5)] and tl[0]["payload"]["index_moves"]["kospi_pct"] == 0.5
    assert ms.load_market_snapshot_timeline(day="2026-01-01", macro_root=tmp_path) == []


def _tl(*pairs):
    return [{"snapshot_epoch": e, "source_path": f"p{e}", "payload": {"index_moves": {"kospi_pct": v}}} for e, v in pairs]


def test_select_latest_at_or_before_decision_fresh_stale_boundary():
    tl = _tl((ep(9, 0), 0.5), (ep(9, 5), 1.0), (ep(9, 20), 2.0))
    s = ms.select_market_snapshot(tl, decision_epoch=ep(9, 10))
    assert s["evidence_status"] == "OBSERVED_POINT_IN_TIME" and s["snapshot_epoch"] == ep(9, 5) and s["kospi_pct"] == 1.0
    assert s["snapshot_age_sec"] == 300 and s["freshness_status"] == "FRESH"                      # 300s inclusive
    assert ms.select_market_snapshot(tl, decision_epoch=ep(9, 10, 1))["freshness_status"] == "STALE"
    assert s["next_snapshot_epoch"] == ep(9, 20) and s["next_snapshot_delay_sec"] == ep(9, 20) - ep(9, 10)
    assert s["eligible_snapshot_count"] == 2 and s["timeline_snapshot_count"] == 3 and s["snapshot_time_kst"].endswith("+09:00")
    assert ms.select_market_snapshot(tl, decision_epoch=ep(9, 5))["snapshot_epoch"] == ep(9, 5)   # at-decision snapshot is eligible
    last = ms.select_market_snapshot(tl, decision_epoch=ep(10, 0))
    assert last["next_snapshot_epoch"] is None and last["next_snapshot_delay_sec"] is None


def test_select_missing_when_only_future_or_empty_and_ignores_nonpositive_epochs():
    tl = _tl((ep(9, 20), 2.0), (0, 9.0))
    s = ms.select_market_snapshot(tl, decision_epoch=ep(9, 0))
    assert s["evidence_status"] == "MISSING_NO_SNAPSHOT_AT_OR_BEFORE_DECISION" and s["freshness_status"] == "MISSING" and s["snapshot_epoch"] is None
    assert s["next_snapshot_epoch"] == ep(9, 20) and s["next_snapshot_usage"] == "POST_DECISION_OBSERVABILITY_ONLY" and s["timeline_snapshot_count"] == 1
    assert ms.select_market_snapshot([], decision_epoch=ep(9, 0))["next_snapshot_delay_sec"] is None
    nonmap = ms.select_market_snapshot([{"snapshot_epoch": ep(9, 0), "payload": "x"}], decision_epoch=ep(9, 1))
    assert nonmap["kospi_pct"] is None and nonmap["evidence_status"] == "OBSERVED_POINT_IN_TIME"


# ---------- symbol metadata ----------

def _cache(path, symbols):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"symbols": symbols}), encoding="utf-8")


@pytest.fixture
def collector(monkeypatch):
    calls = []
    mod = types.ModuleType("libs.research.opening_rank1_deep_dive.metadata")

    def collect(symbols, *, output_path, request_interval_sec, collect_themes):
        calls.append({"symbols": list(symbols), "output_path": output_path, "interval": request_interval_sec, "themes": collect_themes})
        if calls[-1].get("raise"):
            raise RuntimeError("boom")
        _cache(output_path, {s: {"name": f"N{s}"} for s in symbols})

    mod.collect_current_symbol_metadata = collect
    monkeypatch.setitem(sys.modules, "libs.research.opening_rank1_deep_dive.metadata", mod)
    return calls, mod


def test_load_cache_fail_soft(tmp_path):
    assert sm._load(tmp_path / "none.json") == {}
    p = tmp_path / "c.json"
    p.write_text("{bad", encoding="utf-8")
    assert sm._load(p) == {}
    p.write_text("[1]", encoding="utf-8")
    assert sm._load(p) == {}
    _cache(p, {"A": {"name": "a"}, "B": "bad", "C": None})
    assert sm._load(p) == {"A": {"name": "a"}}


def test_no_refresh_when_not_allowed_or_nothing_missing(tmp_path, collector):
    calls, _ = collector
    cache = tmp_path / "c.json"
    _cache(cache, {"A": {"name": "a"}})
    rows, info = sm.load_or_refresh_symbol_metadata(symbols=("A", "B"), cache_path=cache, allow_refresh=False)
    assert calls == [] and info["missing_symbols"] == ["B"] and info["resolved_name_count"] == 1 and info["refresh_allowed"] is False and info["refresh_error"] == ""
    sm.load_or_refresh_symbol_metadata(symbols=("A",), cache_path=cache, allow_refresh=True)
    assert calls == []


def test_refresh_collects_union_sorted_and_reloads(tmp_path, collector):
    calls, _ = collector
    cache = tmp_path / "x" / "c.json"
    _cache(cache, {"Z": {"name": "z"}})
    rows, info = sm.load_or_refresh_symbol_metadata(symbols=("B", "A"), cache_path=cache, allow_refresh=True)
    assert calls == [{"symbols": ["A", "B", "Z"], "output_path": cache, "interval": 1.05, "themes": False}]
    assert rows["A"]["name"] == "NA" and info["resolved_name_count"] == 2 and info["missing_symbols"] == []


def test_refresh_failure_is_recorded_not_raised(tmp_path, collector):
    _, mod = collector

    def boom(*a, **k):
        raise RuntimeError("down")

    mod.collect_current_symbol_metadata = boom
    rows, info = sm.load_or_refresh_symbol_metadata(symbols=("A",), cache_path=tmp_path / "c.json", allow_refresh=True)
    assert rows == {} and info["refresh_error"] == "RuntimeError:down" and info["missing_symbols"] == ["A"]


def test_name_less_cache_entry_counts_as_missing_and_triggers_refresh(tmp_path, collector):
    calls, _ = collector
    cache = tmp_path / "c.json"
    _cache(cache, {"A": {"name": ""}})
    sm.load_or_refresh_symbol_metadata(symbols=("A",), cache_path=cache, allow_refresh=True)
    assert len(calls) == 1


def test_enrich_adds_name_only_when_absent_and_does_not_mutate_input():
    windows = [{"candidates": [{"symbol": "A"}, {"symbol": "B", "name": "keep"}, {"symbol": "C"}]}, {"x": 1}]
    meta = {"A": {"name": "Alpha"}, "B": {"name": "Beta", "name_authority": "X"}, "C": {"name": "Gamma", "name_authority": "SRC"}}
    out = sm.enrich_windows_with_symbol_metadata(windows, meta)
    c = out[0]["candidates"]
    assert c[0] == {"symbol": "A", "name": "Alpha", "name_authority": "CURRENT_REFERENCE"} and c[1] == {"symbol": "B", "name": "keep"}
    assert c[2]["name_authority"] == "SRC" and out[1] == {"x": 1, "candidates": []}
    assert windows[0]["candidates"][0] == {"symbol": "A"}


# ---------- conditional alpha ----------

def test_load_episodes_variants(tmp_path):
    p = tmp_path / "e.json"
    p.write_text("﻿" + json.dumps([{"a": 1}, "x", {"b": 2}]), encoding="utf-8")
    assert ca.load_conditional_alpha_episodes(p) == [{"a": 1}, {"b": 2}]
    p.write_text(json.dumps({"a": 1}), encoding="utf-8")
    assert ca.load_conditional_alpha_episodes(p) == []
    p.write_text("{bad", encoding="utf-8")
    assert ca.load_conditional_alpha_episodes(p) == [] and ca.load_conditional_alpha_episodes(tmp_path / "none.json") == []


def test_timestamp_parse():
    assert ca._timestamp("2026-09-07T00:00:00Z") == ca._timestamp("2026-09-07T00:00:00+00:00") and ca._timestamp("x") is None and ca._timestamp(None) is None


def _ep(**kw):
    base = {"decision_id": "D1", "day": DAY, "symbol": "005930", "decision_time_kst": "2026-09-07T09:00:00+09:00", "stage_attribution": {"root_cause": "RC"},
            "conditional_alpha_cohorts": ["c1"], "opening_archetype": "A", "return_5m_pct": 1, "return_15m_pct": 2, "net_return_30m_pct": 3, "return_60m_pct": 4, "return_eod_pct": 5,
            "mfe_30m_pct": 6, "mae_30m_pct": -1}
    base.update(kw)
    return base


def test_exact_decision_id_match_is_authoritative():
    out = ca.resolve_conditional_alpha_context({"selection": {"q9_decision_id": "D1"}}, [_ep(), _ep(decision_id="D2")])
    assert out["match_status"] == "EXACT_DECISION_ID" and out["authority"] == "AUTHORITATIVE_POINT_IN_TIME_LINK" and out["warning"] is None
    assert out["stage_root_cause"] == "RC" and out["cohort_ids"] == ["c1"] and out["forward_returns_pct"] == {"5m": 1, "15m": 2, "30m": 3, "60m": 4, "EOD": 5}
    assert out["mfe_30m_pct"] == 6 and out["mae_30m_pct"] == -1 and out["opening_archetype"] == "A"


def test_time_symbol_fallback_picks_nearest_and_is_context_only():
    model = {"day": DAY, "symbol": "5930", "entry": {"timestamp": "2026-09-07T09:06:00+09:00"}}
    eps = [_ep(decision_id="far", decision_time_kst="2026-09-07T09:00:00+09:00"), _ep(decision_id="near", decision_time_kst="2026-09-07T09:05:00+09:00"),
           _ep(decision_id="other", symbol="000660"), _ep(decision_id="day", day="2026-09-08")]
    out = ca.resolve_conditional_alpha_context(model, eps)
    assert out["decision_id"] == "near" and out["match_status"] == "TIME_SYMBOL_CONTEXT_ONLY" and out["authority"] == "CONTEXT_ONLY_NOT_CAUSAL"
    assert "Same-day/symbol proximity only" in out["warning"]                                    # '5930' zero-filled to 005930


def test_not_matched_and_duplicate_child_paths():
    assert ca.resolve_conditional_alpha_context({"day": DAY, "symbol": "005930"}, []) == {"match_status": "NOT_MATCHED", "authority": "UNAVAILABLE"}
    assert ca.resolve_conditional_alpha_context({"selection": {"q9_decision_id": "ZZ"}, "day": DAY, "symbol": "1"}, [_ep()])["match_status"] == "NOT_MATCHED"
    model = {"selection": {"q9_decision_id": "D1"}, "integrity": {"partial_exit_duplicate": {"status": "duplicate_partial_exit_child"}}}
    out = ca.resolve_conditional_alpha_context(model, [_ep()])
    assert out["match_status"] == "EXACT_DECISION_ID_DUPLICATE_CHILD" and out["authority"] == "DUPLICATE_PARTIAL_EXIT_CHILD_CONTEXT" and "Duplicate partial-exit child" in out["warning"]
    fallback_dup = {"day": DAY, "symbol": "005930", "integrity": {"partial_exit_duplicate": {"status": "duplicate_partial_exit_child"}}}
    assert ca.resolve_conditional_alpha_context(fallback_dup, [_ep()])["match_status"] == "TIME_SYMBOL_CONTEXT_ONLY"       # only exact links are relabeled


def test_episode_symbol_without_leading_zeros_still_matches_by_zfill():
    model = {"day": DAY, "symbol": "005930", "entry": {"timestamp": "2026-09-07T09:00:00+09:00"}}
    assert ca.resolve_conditional_alpha_context(model, [_ep(decision_id="short", symbol="5930")])["decision_id"] == "short"


def test_symbol_metadata_refresh_unions_cached_symbols_into_collector_call(tmp_path, collector):
    calls, _ = collector
    cache = tmp_path / "c.json"
    _cache(cache, {"Z": {"name": "z"}, "Y": {"name": ""}})
    sm.load_or_refresh_symbol_metadata(symbols=("A",), cache_path=cache, allow_refresh=True)
    assert calls[0]["symbols"] == ["A", "Y", "Z"]
