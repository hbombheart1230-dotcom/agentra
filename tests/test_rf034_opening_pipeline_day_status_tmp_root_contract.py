"""RF-034 C3: opening_rank1_shadow.pipeline day-status ladder, path derivation and tmp-root write contract.

Every collaborator that could touch the network or repo-relative data (extraction, symbol metadata, candle loaders,
episode builder, latent watch) is replaced in the pipeline module; the pipeline's own decisions and writes are pinned.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from libs.reporting.opening_rank1_shadow import pipeline as pl

FIRST = pl.FIRST_ELIGIBLE_DAY
DAY = "2099-01-05"          # always >= FIRST_ELIGIBLE_DAY


def _kst_epoch(hh, mm):
    return int(datetime(2026, 8, 5, hh, mm, tzinfo=pl.KST).timestamp())


# ---------- small helpers ----------

def test_time_kst():
    assert pl._time_kst(0) == "" and pl._time_kst(-1) == ""
    assert pl._time_kst(_kst_epoch(9, 5)) == "2026-08-05T09:05:00+09:00"


def test_candles_complete_for_close_requires_every_symbol_at_or_after_1520():
    row = lambda h, m: [{"ts": _kst_epoch(h, m)}]  # noqa: E731
    assert pl._candles_complete_for_close({}, ()) is True
    assert pl._candles_complete_for_close({"A": row(15, 20)}, ("A",)) is True
    assert pl._candles_complete_for_close({"A": row(15, 19)}, ("A",)) is False
    assert pl._candles_complete_for_close({"A": row(15, 30), "B": row(15, 19)}, ("A", "B")) is False
    assert pl._candles_complete_for_close({"A": row(15, 30)}, ("A", "B")) is False          # B missing
    assert pl._candles_complete_for_close({"A": [{"ts": 0}]}, ("A",)) is False
    assert pl._candles_complete_for_close({"A": []}, ("A",)) is False


def _daily_file(root, day, payload):
    p = root / day / "opening_rank1_shadow_daily.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")


def test_load_daily_episodes_only_valid_eligible_deduped_sorted(tmp_path):
    ok = {"eligible_for_validation": True, "day_status": "VALID"}
    _daily_file(tmp_path, "2026-08-03", {**ok, "episodes": [{"episode_id": "b", "v": 1}, {"episode_id": "a"}, {"v": "no id"}, "junk"]})
    _daily_file(tmp_path, "2026-08-04", {**ok, "episodes": [{"episode_id": "b", "v": 2}]})               # later file wins for dup id
    _daily_file(tmp_path, "2026-08-05", {"eligible_for_validation": False, "day_status": "VALID", "episodes": [{"episode_id": "x"}]})
    _daily_file(tmp_path, "2026-08-06", {"eligible_for_validation": True, "day_status": "FORWARD_INCOMPLETE", "episodes": [{"episode_id": "y"}]})
    _daily_file(tmp_path, "2026-08-07", "{corrupt")
    _daily_file(tmp_path, "2026-08-08", "[1]")
    assert pl._load_daily_episodes(tmp_path) == [{"episode_id": "a"}, {"episode_id": "b", "v": 2}]
    assert pl._load_daily_episodes(tmp_path / "none") == []


# ---------- build ----------

class Harness:
    def __init__(self):
        self.calls = {}
        self.extraction = {"windows": [{"w": 1}], "symbols": ["005930"], "source_exists": True, "missing_universe_count": 0, "missing_rank1_count": 0}
        self.candles = {"005930": [{"ts": 1}]}
        self.episodes = [{"episode_id": "E1", "decision_epoch": _kst_epoch(9, 1), "baseline_epoch": _kst_epoch(9, 2)}]
        self.summary = {"episode_count": 1, "observed_30m_count": 1}


@pytest.fixture
def h(monkeypatch):
    hx = Harness()

    def rec(name, ret):
        def f(*a, **k):
            hx.calls[name] = (a, k)
            return ret() if callable(ret) else ret
        return f

    monkeypatch.setattr(pl, "extract_opening_rank1_windows", rec("extract", lambda: hx.extraction))
    monkeypatch.setattr(pl, "load_or_refresh_symbol_metadata", rec("meta", lambda: ({"005930": {}}, {"provider": "stub"})))
    monkeypatch.setattr(pl, "enrich_windows_with_symbol_metadata", lambda w, m: w)
    monkeypatch.setattr(pl, "load_opening_candles", rec("candles", lambda: (hx.candles, {"historical_fallback_requested_symbols": []})))
    monkeypatch.setattr(pl, "load_historical_reference_rows", rec("refrows", {}))
    monkeypatch.setattr(pl, "load_market_snapshot_timeline", rec("snap", []))
    monkeypatch.setattr(pl, "build_opening_rank1_episodes", rec("episodes", lambda: [dict(e) for e in hx.episodes]))
    monkeypatch.setattr(pl, "summarize_episodes", lambda eps: hx.summary if eps is not None and len(eps) == len(hx.episodes) and eps and "cohort_id" in eps[0] else {"episode_count": len(eps), "observed_30m_count": len(eps)})
    monkeypatch.setattr(pl, "evaluate_promotion", lambda s: {"status": "COLLECTING"})
    monkeypatch.setattr(pl, "render_daily", lambda p: f"DAILY {p['day_status']}\n")
    monkeypatch.setattr(pl, "render_cumulative", lambda p: "CUM\n")
    monkeypatch.setattr(pl, "build_latent_reactivation_watch", rec("watch", {"json": "W.json", "markdown": "W.md", "forward_json": "F.json", "forward_markdown": "F.md", "summary": {"watch_count": 0}}))
    return hx


def _run(tmp_path, day=DAY, **kw):
    return pl.build_opening_rank1_shadow(day=day, reports_root=tmp_path / "reports", state_path=tmp_path / "data" / "state.json", **kw)


@pytest.mark.parametrize("mutate,expected", [
    (lambda h: None, "VALID"),
    (lambda h: h.extraction.update(source_exists=False), "Q9_ARTIFACT_MISSING"),
    (lambda h: h.extraction.update(missing_universe_count=1), "ARTIFACT_INCOMPLETE"),
    (lambda h: h.extraction.update(missing_rank1_count=2), "ARTIFACT_INCOMPLETE"),
    (lambda h: h.extraction.update(windows=[]), "NO_OPENING_RANK1"),
    (lambda h: setattr(h, "episodes", []), "MINUTE_HISTORY_MISSING"),
    (lambda h: h.summary.update(observed_30m_count=0), "FORWARD_INCOMPLETE"),
])
def test_day_status_ladder(tmp_path, h, mutate, expected):
    mutate(h)
    out = _run(tmp_path)
    assert out["day_status"] == expected and out["ok"] is True
    daily = json.loads(Path(out["daily_json_path"]).read_text(encoding="utf-8"))
    assert daily["day_status"] == expected and daily["eligible_for_validation"] is True


def test_implementation_day_is_excluded_before_first_eligible_day(tmp_path, h):
    out = _run(tmp_path, day="2000-01-01")
    assert out["day_status"] == "IMPLEMENTATION_DAY_EXCLUDED"
    daily = json.loads(Path(out["daily_json_path"]).read_text(encoding="utf-8"))
    assert daily["eligible_for_validation"] is False and all(e["prospective_eligible"] is False for e in daily["episodes"])
    assert _run(tmp_path, day=FIRST)["day_status"] != "IMPLEMENTATION_DAY_EXCLUDED"           # boundary day is eligible


def test_day_is_normalized_and_outputs_land_under_reports_evaluation(tmp_path, h):
    out = _run(tmp_path, day=f"  {DAY}T09:00:00  ")
    base = tmp_path / "reports" / "evaluation" / "opening_rank1_shadow"
    assert Path(out["daily_json_path"]) == base / DAY / "opening_rank1_shadow_daily.json"
    assert Path(out["daily_md_path"]).read_text(encoding="utf-8") == "DAILY VALID\n"
    assert Path(out["cumulative_json_path"]) == base / "opening_rank1_shadow_cumulative.json"
    assert h.calls["extract"][1]["day"] == DAY
    assert out["five_session_review_json_path"].endswith("five_session_review/opening_alpha_five_session_review.json")
    assert out["latent_watch_json_path"] == "W.json" and out["latent_forward_md_path"] == "F.md"
    assert out["promotion_status"] == "COLLECTING" and out["episode_count"] == 1


def test_state_path_parent_roots_are_used_for_caches_and_macro(tmp_path, h):
    _run(tmp_path, allow_fresh_fetch=False)
    data = tmp_path / "data"
    assert h.calls["meta"][1]["cache_path"] == data / "research/opening_rank1_shadow/symbol_metadata.json"
    assert h.calls["meta"][1]["allow_refresh"] is False
    assert h.calls["candles"][1]["cache_root"] == data / "research/opening_rank1_shadow/minute_cache"
    assert h.calls["candles"][1]["allow_fresh_fetch"] is False and h.calls["candles"][1]["state_path"] == data / "state.json"
    assert h.calls["refrows"][1]["cache_root"] == data / "research/opening_rank1_shadow/minute_cache"
    assert h.calls["snap"][1]["macro_root"] == data / "logs/macro_indicators"
    assert h.calls["watch"][1]["opening_output_root"] == tmp_path / "reports/evaluation/opening_rank1_shadow"
    assert h.calls["watch"][1]["allow_fresh_fetch"] is False


def test_episode_rows_are_annotated_with_cohort_times_and_prospective_flag(tmp_path, h):
    out = _run(tmp_path)
    ep = json.loads(Path(out["daily_json_path"]).read_text(encoding="utf-8"))["episodes"][0]
    assert ep["cohort_id"] == pl.COHORT_ID and ep["decision_time_kst"] == "2026-08-05T09:01:00+09:00"
    assert ep["entry_time_kst"] == "2026-08-05T09:02:00+09:00" and ep["prospective_eligible"] is True


def test_provider_block_reports_fetch_flags_and_symbol_counts(tmp_path, h):
    h.candles = {"005930": [{"ts": 1}], "000660": []}
    h.extraction["symbols"] = ["005930", "000660"]
    daily = json.loads(Path(_run(tmp_path, allow_fresh_fetch=True)["daily_json_path"]).read_text(encoding="utf-8"))
    p = daily["provider"]
    assert p["requested_symbol_count"] == 2 and p["symbols_with_rows"] == 1 and p["fresh_fetch_allowed"] is True and p["fresh_fetch_used"] is False
    assert "windows" not in daily["extraction"] and daily["extraction"]["source_exists"] is True


def test_cumulative_accumulates_across_days_and_only_valid_days(tmp_path, h):
    _run(tmp_path, day="2099-01-05")
    h.summary = {"episode_count": 1, "observed_30m_count": 0}
    h.episodes = [{"episode_id": "E2", "decision_epoch": 1, "baseline_epoch": 1}]
    out = _run(tmp_path, day="2099-01-06")                                                       # FORWARD_INCOMPLETE -> excluded
    cum = json.loads(Path(out["cumulative_json_path"]).read_text(encoding="utf-8"))
    assert cum["through_day"] == "2099-01-06" and [e["episode_id"] for e in cum["episodes"]] == ["E1"]
    assert cum["promotion_decision"] == {"status": "COLLECTING"} and cum["behavior_effect"] == pl.BEHAVIOR_EFFECT


def test_nothing_is_written_outside_reports_and_state_parent(tmp_path, h):
    before = {p for p in tmp_path.rglob("*") if p.is_file()}
    _run(tmp_path)
    new = {p.relative_to(tmp_path).parts[0] for p in tmp_path.rglob("*") if p.is_file() and p not in before}
    assert new == {"reports"}                                                                    # loaders are stubbed -> data/ stays untouched
