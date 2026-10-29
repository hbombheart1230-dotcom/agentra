"""RF-034 C3: opening episodes builder gap/prior-rank-1/baseline rules with entry_bar and evaluator stubbed (pure)."""
from __future__ import annotations

import pytest

from libs.reporting.opening_rank1_shadow import episodes as epm

GAP = epm.EPISODE_GAP_SEC


@pytest.fixture
def stubs(monkeypatch):
    st = {"entry_calls": []}

    def entry_bar(rows, *, decision_epoch, day, timestamps):
        st["entry_calls"].append((decision_epoch, day, timestamps))
        later = [r for r in rows if int(r["ts"]) >= decision_epoch]
        return later[0] if later else None

    monkeypatch.setattr(epm, "entry_bar", entry_bar)
    monkeypatch.setattr(epm, "evaluate_episodes", lambda eps, minute_rows_by_symbol: [dict(e, evaluated=True) for e in eps])
    monkeypatch.setattr(epm, "opening_observability", lambda **kw: {"prior": kw["prior_rank1_observations_5m"], "ref_rows": len(kw["volume_reference_rows"]), "snap": kw["market_snapshot"]["evidence_status"], "mr": kw["market_return_pct"]})
    return st


def win(epoch, symbol="A", rank=1, day="2026-09-07", did=None, **cand):
    return {"day": day, "decision_epoch": epoch, "decision_id": did or f"D{epoch}", "candidates": [{"symbol": symbol, "rank": rank, "score_total": 1.5, "risk_score": 0.2, "sources": ["s1", 2], "score_breakdown": {"x": 1}, **cand}]}


def rows(symbol_epochs, price=100.0):
    return {s: [{"ts": e, "open": price, "close": price} for e in es] for s, es in symbol_epochs.items()}


def test_basic_episode_fields_and_evaluator_applied(stubs):
    out = epm.build_opening_rank1_episodes([win(1000)], minute_rows_by_symbol=rows({"A": [1000, 1060]}))
    assert len(out) == 1
    e = out[0]
    assert e["evaluated"] is True and e["episode_id"] == f"{epm.COHORT_ID}:20260907:A:1000" and e["cohort_id"] == epm.COHORT_ID
    assert e["baseline_epoch"] == 1000 and e["baseline_price"] == 100.0 and e["rank"] == 1 and e["evidence_class"] == "PROSPECTIVE_POINT_IN_TIME_Q9"
    assert e["sources"] == ["s1", "2"] and e["score_breakdown"] == {"x": 1} and e["decision_id"] == "D1000"
    assert e["market_snapshot"]["evidence_status"].startswith("MISSING") and e["opening_observability"]["snap"].startswith("MISSING")


def test_only_rank1_candidate_is_used_and_windows_without_it_skipped(stubs):
    w = {"day": "2026-09-07", "decision_epoch": 1000, "candidates": [{"symbol": "B", "rank": 2}, "junk", {"symbol": "A"}]}
    assert epm.build_opening_rank1_episodes([w], minute_rows_by_symbol=rows({"A": [1000], "B": [1000]})) == []
    assert epm.build_opening_rank1_episodes([{"day": "d", "decision_epoch": 1}], minute_rows_by_symbol={}) == []


def test_episode_gap_is_inclusive_at_gap_and_per_day_symbol(stubs):
    base = 10_000
    ws = [win(base), win(base + GAP - 1), win(base + GAP), win(base + GAP, symbol="B"), win(base + GAP, day="2026-09-08")]
    r = rows({"A": [base, base + GAP - 1, base + GAP], "B": [base + GAP]})
    r["A"] += [{"ts": base + GAP, "open": 100.0, "close": 100.0}]
    out = epm.build_opening_rank1_episodes(ws, minute_rows_by_symbol=r)
    # A@base kept; A@base+GAP-1 suppressed (< GAP since last); A@base+GAP kept (== GAP); B kept; A on another day kept only if a bar exists
    assert [(e["symbol"], e["decision_epoch"], e["day"]) for e in out] == [("A", base, "2026-09-07"), ("A", base + GAP, "2026-09-07"), ("B", base + GAP, "2026-09-07"), ("A", base + GAP, "2026-09-08")]


def test_prior_rank1_observations_counts_only_previous_five_minutes_including_suppressed(stubs):
    t = 100_000
    ws = [win(t), win(t + GAP - 100), win(t + GAP)]                          # middle one is suppressed (inside gap) but still counts as a prior observation
    out = epm.build_opening_rank1_episodes(ws, minute_rows_by_symbol=rows({"A": [t, t + GAP - 100, t + GAP]}))
    assert [e["decision_epoch"] for e in out] == [t, t + GAP]
    assert out[0]["opening_observability"]["prior"] == 0 and out[1]["opening_observability"]["prior"] == 1
    far = epm.build_opening_rank1_episodes([win(t), win(t + GAP + 400)], minute_rows_by_symbol=rows({"A": [t, t + GAP + 400]}))
    assert far[1]["opening_observability"]["prior"] == 0                      # previous rank-1 is older than 300s
    edge = epm.build_opening_rank1_episodes([win(t), win(t + GAP - 300), win(t + GAP)], minute_rows_by_symbol=rows({"A": [t, t + GAP - 300, t + GAP]}))
    assert edge[1]["opening_observability"]["prior"] == 1                     # exactly 300s old is included (0 < delta <= 300)
    just_over = epm.build_opening_rank1_episodes([win(t), win(t + GAP - 301), win(t + GAP)], minute_rows_by_symbol=rows({"A": [t, t + GAP - 301, t + GAP]}))
    assert just_over[1]["opening_observability"]["prior"] == 0                 # 301s old is excluded


def test_missing_bar_or_nonpositive_price_skips_but_still_counts_as_observed_rank1(stubs):
    t = 50_000
    r = {"A": [{"ts": t, "open": 0.0, "close": 0.0}]}
    assert epm.build_opening_rank1_episodes([win(t)], minute_rows_by_symbol=r) == []
    assert epm.build_opening_rank1_episodes([win(t)], minute_rows_by_symbol={"A": []}) == []
    prefer_open = epm.build_opening_rank1_episodes([win(t)], minute_rows_by_symbol={"A": [{"ts": t, "open": 0.0, "close": 99.0}]})
    assert prefer_open[0]["baseline_price"] == 99.0                               # falls back to close when open is falsy


def test_snapshot_reference_rows_and_market_return_are_forwarded(stubs):
    t = 70_000
    tl = [{"snapshot_epoch": t - 10, "source_path": "p", "payload": {"index_moves": {"kospi_pct": 1.0}}}]
    out = epm.build_opening_rank1_episodes([win(t)], minute_rows_by_symbol=rows({"A": [t]}), market_return_pct=-1.5, market_snapshot_timeline=tl,
                                           volume_reference_rows_by_symbol={"A": [{"ts": 1}, {"ts": 2}]})
    o = out[0]["opening_observability"]
    assert o == {"prior": 0, "ref_rows": 2, "snap": "OBSERVED_POINT_IN_TIME", "mr": -1.5} and out[0]["market_snapshot"]["kospi_pct"] == 1.0


def test_open_preferred_over_close_and_same_epoch_repeat_is_suppressed(stubs):
    t = 90_000
    out = epm.build_opening_rank1_episodes([win(t)], minute_rows_by_symbol={"A": [{"ts": t, "open": 98.0, "close": 99.0}]})
    assert out[0]["baseline_price"] == 98.0
    dup = epm.build_opening_rank1_episodes([win(t, did="first"), win(t, did="second")], minute_rows_by_symbol=rows({"A": [t]}))
    assert [e["decision_id"] for e in dup] == ["first"]                          # same-epoch repeat is suppressed by the gap rule
