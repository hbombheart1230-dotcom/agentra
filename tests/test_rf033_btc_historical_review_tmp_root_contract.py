"""RF-033 C3: baseline_btc_woori_tech.historical_review on a tmp reports root (evaluation-only replay, no network).

All reads/writes stay under ``tmp_path``; the module's default ``Path('reports')`` is never used.
"""
from __future__ import annotations

import json
import socket
from pathlib import Path

import pytest

from libs.reporting.baseline_btc_woori_tech import historical_review as hr

DAY = "2026-10-28"
T0 = 1_792_000_000  # arbitrary epoch; only relative offsets matter here


@pytest.fixture(autouse=True)
def _deny_network(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("network attempt")

    monkeypatch.setattr(socket.socket, "connect", _boom)
    monkeypatch.setattr(socket, "create_connection", _boom)


def _decision(did, ts, price, *, m5, vol=1.5, trend=True, day=DAY, name="btc_usd", stale=False, available=True):
    return {
        "decision_id": did,
        "day": day,
        "as_of_epoch": ts,
        "btc_signal": {"momentum_5m_pct": m5, "observations": [{"name": name, "ts": ts, "price": price, "stale": stale}]},
        "local_features": {"available": available, "volume_ratio": vol, "price_above_vwap_or_short_ma": trend},
    }


def _fwd(did, ret30=1.0):
    ok = lambda v: {"status": "observed", "return_pct": v}  # noqa: E731
    return {"baseline_decision_id": did, "returns": {"+5m": ok(0.5), "+15m": ok(0.8), "+30m": ok(ret30), "EOD": {"status": "missing"}}}


def _write_day(root: Path, day, decisions, forwards, *, cost=(0.1, 0.05)):
    d = root / "evaluation" / "baseline_btc_woori_tech" / day
    d.mkdir(parents=True)
    (d / "baseline_btc_woori_decisions.json").write_text(json.dumps({"decisions": decisions}), encoding="utf-8")
    (d / "baseline_btc_woori_forward_returns.json").write_text(
        json.dumps({"rows": forwards, "cost_model": {"round_trip_cost_pct": cost[0], "slippage_pct": cost[1]}}), encoding="utf-8")
    return d


# ---------- pure helpers ----------

def test_pct_prior_price_krx_open_metric():
    assert hr._pct(110.0, 100.0) == 10.0
    assert hr._pct(0.0, 100.0) is None and hr._pct(1.0, None) is None and hr._pct(1.0, 0.0) is None
    epochs, prices = [100, 200, 300], [1.0, 2.0, 3.0]
    assert hr._prior_price(epochs=epochs, prices=prices, epoch=500, seconds=200) == 3.0       # target 300 exact
    assert hr._prior_price(epochs=epochs, prices=prices, epoch=400, seconds=250) == 1.0       # target 150 -> idx 100, gap 50
    assert hr._prior_price(epochs=epochs, prices=prices, epoch=1000, seconds=200) is None     # 800-300 > 300 tolerance
    assert hr._prior_price(epochs=epochs, prices=prices, epoch=150, seconds=200) is None      # before first
    m = hr._metric([1.0, -0.5, 0.0])
    assert m["trade_count"] == 3 and m["win_rate"] == pytest.approx(0.3333, abs=1e-4) and m["avg_return_pct"] == pytest.approx(0.1667, abs=1e-4)
    assert m["max_drawdown_pct"] == -0.5
    assert hr._metric([]) == {"trade_count": 0, "win_rate": 0.0, "avg_return_pct": 0.0, "profit_factor": 0.0, "max_drawdown_pct": 0.0}


def test_krx_open_price_same_kst_day_only():
    from datetime import datetime

    kst = hr.KST
    open_ts = int(datetime(2026, 10, 28, 9, 0, tzinfo=kst).timestamp())
    prev_ts = open_ts - 3600
    cur = open_ts + 600
    assert hr._krx_open_price(epochs=[prev_ts, open_ts + 60, cur], prices=[1.0, 2.0, 3.0], epoch=cur) == 2.0
    assert hr._krx_open_price(epochs=[prev_ts], prices=[1.0], epoch=cur) is None                 # no index >= open
    assert hr._krx_open_price(epochs=[cur + 10], prices=[1.0], epoch=cur) is None                # first >= open is after epoch


def test_krx_open_price_rejects_other_day_observation():
    from datetime import datetime

    open_ts = int(datetime(2026, 10, 28, 9, 0, tzinfo=hr.KST).timestamp())
    cur = open_ts + 3600 * 20  # still 28th KST? 05:00 on 29th -> different date than the observation
    obs_prev_day = open_ts - 7200  # before open on the same day -> not >= opening, skipped
    assert hr._krx_open_price(epochs=[obs_prev_day], prices=[1.0], epoch=cur) is None


def test_direct_observation_prefers_btc_usd_and_skips_stale_or_zero():
    d = {"btc_signal": {"observations": [
        {"name": "btc_krw", "price": 5.0},
        {"name": "btc_usd", "price": 9.0, "stale": True},
    ]}}
    assert hr._direct_observation(d)["name"] == "btc_krw"
    d["btc_signal"]["observations"].append({"name": "btc_usd", "price": 7.0})
    assert hr._direct_observation(d)["price"] == 7.0
    assert hr._direct_observation({"btc_signal": {"observations": [{"name": "btc_usd", "price": 0}]}}) is None
    assert hr._direct_observation({}) is None


def test_read_write_roundtrip_and_failsoft(tmp_path):
    p = tmp_path / "a" / "b.json"
    hr._write(p, {"k": "한글"})
    assert json.loads(p.read_text(encoding="utf-8")) == {"k": "한글"} and p.read_text(encoding="utf-8").endswith("\n")
    assert hr._read(p) == {"k": "한글"}
    assert hr._read(tmp_path / "none.json") == {}
    p.write_text("[1]", encoding="utf-8")
    assert hr._read(p) == {}
    p.write_text("{bad", encoding="utf-8")
    assert hr._read(p) == {}


# ---------- build_historical_review ----------

def test_build_review_v1_v2_split_costs_and_outputs(tmp_path):
    root = tmp_path / "reports"
    t = T0
    decisions = [
        _decision("E0", t, 100.0, m5=0.0),                 # observation only (no forward row)
        _decision("E1", t + 2700, 100.5, m5=0.0),          # provides the 15m prior for D2
        _decision("D1", t + 3000, 100.0, m5=0.5),          # v1 + v2 eligible
        _decision("D2", t + 3600, 101.0, m5=-0.1),         # v2 only (strong_bull via 60m +1.0%, shallow pullback)
        _decision("D3", t + 4200, 100.0, m5=0.5, vol=0.5, trend=False),  # fails confirmations
        _decision("", t + 4300, 100.0, m5=0.5),            # no id -> ignored
    ]
    _write_day(root, DAY, decisions, [_fwd("D1", 1.0), _fwd("D2", 2.0), _fwd("D3", 3.0)])
    (root / "evaluation" / "baseline_btc_woori_tech" / "notes").mkdir()                   # non-digit dir ignored
    out = hr.build_historical_review(reports_root=root)
    jp, mp = Path(out["json"]), Path(out["markdown"])
    assert jp == root / "evaluation" / "baseline_btc_woori_tech" / "historical" / "q12_v1_v2_historical_review.json"
    payload = json.loads(jp.read_text(encoding="utf-8"))
    assert mp.read_text(encoding="utf-8") == hr.render_historical_review(payload)

    assert payload["behavior_effect"] == "evaluation_only" and payload["policies"] == {"v1": hr.POLICY_V1, "v2": hr.POLICY_V2}
    assert payload["source_days"] == [{"day": DAY, "decision_count": 6}]  # counted before id filtering
    by_id = {r["decision_id"]: r for r in payload["rows"]}
    assert set(by_id) == {"D1", "D2", "D3"}
    assert by_id["D1"]["v1_eligible"] and by_id["D1"]["v2_eligible"] and not by_id["D1"]["v2_only"]
    assert not by_id["D2"]["v1_eligible"] and by_id["D2"]["v2_eligible"] and by_id["D2"]["v2_only"]
    assert by_id["D2"]["btc"]["momentum_60m_pct"] == pytest.approx(1.0) and by_id["D2"]["btc"]["market_regime"] == "strong_bull"
    assert by_id["D2"]["btc"]["leading_signal_reason"] == "bull_regime_short_pullback"
    assert not by_id["D3"]["v1_eligible"] and not by_id["D3"]["v2_eligible"]
    assert payload["eligibility"] == {"v1_count": 1, "v2_count": 2, "v2_only_count": 1}
    assert by_id["D1"]["round_trip_drag_pct"] == pytest.approx(0.15)

    h30 = next(h for h in payload["horizons"] if h["horizon"] == "+30m")
    assert h30["v1_gross"]["avg_return_pct"] == 1.0
    assert h30["v1_net"]["avg_return_pct"] == pytest.approx(0.85)                       # artifact mock drag 0.15
    assert h30["v1_real_net"]["avg_return_pct"] == pytest.approx(1.0 - hr.REAL_ACCOUNT_TOTAL_DRAG_PCT)
    assert h30["v2_gross"]["trade_count"] == 2 and h30["v2_gross"]["avg_return_pct"] == 1.5
    assert h30["v2_only_gross"]["avg_return_pct"] == 2.0
    assert h30["v2_minus_v1_gross"] == {"trade_count": 1, "win_rate": 0.0, "avg_return_pct": 0.5}
    eod = next(h for h in payload["horizons"] if h["horizon"] == "EOD")
    assert eod["v1_gross"]["trade_count"] == 0                                           # EOD status != observed
    assert payload["episode_count"] == 1 and payload["episodes"][0]["episode_id"] == f"Q12V2_20261028_{t + 3600}"
    assert payload["conclusion"] == "INSUFFICIENT_OR_NONPOSITIVE_EPISODE_EVIDENCE"
    cov = payload["coverage"]
    assert cov["day_count"] == 1 and cov["decision_count"] == 3 and 0.0 <= cov["multihorizon_complete_rate"] <= 1.0
    md = mp.read_text(encoding="utf-8")
    assert md.startswith("# Q12 v1 vs v2 Historical Review") and "Main execution impact: none" in md
    for section in ("## Gross Performance", "## Independent v2-only Episodes", "## Real Account Cost Performance", "## Artifact Mock Cost Performance"):
        assert section in md


def test_build_review_output_dir_override_and_nothing_else_written(tmp_path):
    root = tmp_path / "reports"
    _write_day(root, DAY, [_decision("D1", T0, 100.0, m5=0.5)], [_fwd("D1")])
    out_dir = tmp_path / "elsewhere"
    out = hr.build_historical_review(reports_root=root, output_dir=out_dir)
    assert Path(out["json"]).parent == out_dir and Path(out["markdown"]).parent == out_dir
    assert not (root / "evaluation" / "baseline_btc_woori_tech" / "historical").exists()
    assert sorted(p.name for p in out_dir.iterdir()) == ["q12_v1_v2_historical_review.json", "q12_v1_v2_historical_review.md"]


def test_build_review_skips_days_without_decisions_and_corrupt_files(tmp_path):
    root = tmp_path / "reports"
    _write_day(root, "2026-10-27", [], [])
    bad = root / "evaluation" / "baseline_btc_woori_tech" / "2026-10-26"
    bad.mkdir()
    (bad / "baseline_btc_woori_decisions.json").write_text("{bad", encoding="utf-8")
    out = hr.build_historical_review(reports_root=root)
    payload = json.loads(Path(out["json"]).read_text(encoding="utf-8"))
    assert payload["source_days"] == [] and payload["rows"] == [] and payload["coverage"]["multihorizon_complete_rate"] == 0.0
    assert payload["conclusion"] == "INSUFFICIENT_OR_NONPOSITIVE_EPISODE_EVIDENCE"


def test_build_review_missing_source_root_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        hr.build_historical_review(reports_root=tmp_path / "reports")


def test_episode_merge_gap_and_promising_conclusion(tmp_path, monkeypatch):
    monkeypatch.setattr(hr, "evaluate_multihorizon_leading_signal", lambda **kw: {"market_regime": "bull", "leading_positive": True, "leading_signal_reason": "stub"})
    root = tmp_path / "reports"
    decisions, forwards = [], []
    # 10 episodes spaced 40 min apart, each followed by a second v2-only decision 10 min later (merged, gap <= 30 min)
    for i in range(10):
        base = T0 + i * 2400 * 2
        for j, off in enumerate((0, 600)):
            did = f"X{i}_{j}"
            decisions.append(_decision(did, base + off, 100.0, m5=-0.1))
            forwards.append(_fwd(did, 1.0))
    _write_day(root, DAY, decisions, forwards)
    out = hr.build_historical_review(reports_root=root)
    payload = json.loads(Path(out["json"]).read_text(encoding="utf-8"))
    assert payload["eligibility"]["v2_only_count"] == 20 and payload["episode_count"] == 10
    assert all(len(e["decision_ids"]) == 2 for e in payload["episodes"])
    h30 = next(h for h in payload["episode_horizons"] if h["horizon"] == "+30m")
    assert h30["real_net"]["trade_count"] == 10 and h30["real_net"]["avg_return_pct"] == pytest.approx(1.0 - hr.REAL_ACCOUNT_TOTAL_DRAG_PCT)
    assert payload["conclusion"] == "PROMISING_SUBSET_PROSPECTIVE_SHADOW_REQUIRED"


def test_episode_gap_over_30min_starts_new_episode_and_non_positive_blocks_promising(tmp_path, monkeypatch):
    monkeypatch.setattr(hr, "evaluate_multihorizon_leading_signal", lambda **kw: {"market_regime": "bull", "leading_positive": True, "leading_signal_reason": "stub"})
    root = tmp_path / "reports"
    decisions, forwards = [], []
    for i in range(10):
        did = f"Y{i}"
        decisions.append(_decision(did, T0 + i * (31 * 60), 100.0, m5=-0.1))   # 31 min apart -> 10 episodes
        forwards.append(_fwd(did, 0.2))                                        # 0.2 - 0.28 < 0 after real drag
    _write_day(root, DAY, decisions, forwards)
    payload = json.loads(Path(hr.build_historical_review(reports_root=root)["json"]).read_text(encoding="utf-8"))
    assert payload["episode_count"] == 10 and all(len(e["decision_ids"]) == 1 for e in payload["episodes"])
    assert payload["conclusion"] == "INSUFFICIENT_OR_NONPOSITIVE_EPISODE_EVIDENCE"


def test_render_handles_empty_payload():
    md = hr.render_historical_review({})
    assert "Source days: None (None decisions)" in md and md.endswith("\n")


def test_real_account_drag_constant_is_pinned():
    assert hr.REAL_ACCOUNT_TOTAL_DRAG_PCT == 0.28


def _episodes_for(tmp_path, monkeypatch, specs):
    monkeypatch.setattr(hr, "evaluate_multihorizon_leading_signal", lambda **kw: {"market_regime": "bull", "leading_positive": True, "leading_signal_reason": "stub"})
    root = tmp_path / "reports"
    by_day: dict = {}
    for did, day, ts in specs:
        by_day.setdefault(day, []).append((did, ts))
    for day, items in by_day.items():
        _write_day(root, day, [_decision(d, ts, 100.0, m5=-0.1, day=day) for d, ts in items], [_fwd(d) for d, _ in items])
    out = hr.build_historical_review(reports_root=root)
    return json.loads(Path(out["json"]).read_text(encoding="utf-8"))["episodes"]


def test_episode_merge_gap_boundary_is_inclusive_at_1800s(tmp_path, monkeypatch):
    eps = _episodes_for(tmp_path, monkeypatch, [("A", DAY, T0), ("B", DAY, T0 + 1800), ("C", DAY, T0 + 1800 + 1801)])
    assert [e["decision_ids"] for e in eps] == [["A", "B"], ["C"]]


def test_episodes_never_merge_across_days(tmp_path, monkeypatch):
    eps = _episodes_for(tmp_path, monkeypatch, [("A", "2026-10-27", T0), ("B", "2026-10-28", T0 + 60)])
    assert [e["decision_ids"] for e in eps] == [["A"], ["B"]]
