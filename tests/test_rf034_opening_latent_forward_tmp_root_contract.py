"""RF-034 C3: opening_rank1_shadow.latent_forward summary gates, forward observation edges and write/cache contract.

The CWD is switched to tmp_path for every build call because ``build_latent_reactivation_forward`` writes its candle
cache to the CWD-relative ``data/research/opening_rank1_shadow/latent_forward_candles`` (pinned below, see last tests).
Candle loading and broker cost profile are stubbed: no network, no repo-relative state.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from libs.reporting.opening_rank1_shadow import latent_forward as lf

CACHE_REL = Path("data/research/opening_rank1_shadow/latent_forward_candles")
KST = lf.KST


def _ts(day, hh, mm):
    y, m, d = map(int, day.split("-"))
    return int(datetime(y, m, d, hh, mm, tzinfo=KST).timestamp())


# ---------- _observe edges ----------

def _candles(start, n, price=100.0, step=0.0):
    return [{"ts": start + 60 * i, "open": price + step * i, "high": price + step * i + 1, "low": price + step * i - 1, "close": price + step * i} for i in range(n)]


def test_observe_missing_forward_reasons():
    row = {"trigger_epoch": 1000}
    out = lf._observe(row, _candles(500, 3))                                              # nothing after trigger
    assert out["forward_status"] == "MISSING_FORWARD_PRICE" and out["forward_reason"] == "next_tradable_minute_unavailable"
    out = lf._observe(row, [{"ts": 1060, "open": 0, "close": 0}])
    assert out["forward_reason"] == "reference_entry_price_unavailable"
    out = lf._observe(row, [{"ts": 1060, "open": None, "close": "x"}])
    assert out["forward_reason"] == "reference_entry_price_unavailable"
    out = lf._observe(row, [{"ts": 1060, "open": None, "close": 50.0}])                   # close fallback for entry
    assert out["reference_entry"]["price"] == 50.0


def test_observe_horizon_delay_tolerance_is_180s():
    start = 10_000
    row = {"trigger_epoch": start - 1}
    ok = [{"ts": start, "open": 100, "high": 100, "low": 100, "close": 100}, {"ts": start + 300 + 180, "open": 110, "high": 110, "low": 110, "close": 110}]
    late = [ok[0], {**ok[1], "ts": start + 300 + 181}]
    assert lf._observe(row, ok)["checkpoints"]["+5m"]["status"] == "observed"
    assert lf._observe(row, late)["checkpoints"]["+5m"] == {"status": "pending"}
    assert lf._observe(row, late)["forward_status"] == "MISSING_FORWARD_PRICE"            # no horizon observed at all


def test_observe_mfe_mae_and_eod_checkpoint():
    day = "2026-08-04"
    t0 = _ts(day, 9, 5)
    candles = [{"ts": t0 + 60 * i, "open": 100.0, "high": 100.0 + (3 if i == 2 else 1), "low": 100.0 - (2 if i == 4 else 1), "close": 100.0 + i * 0.1} for i in range(8)]
    candles.append({"ts": _ts(day, 15, 20), "open": 105.0, "high": 106.0, "low": 104.0, "close": 105.0})
    candles.append({"ts": _ts(day, 15, 21), "open": 106.0, "high": 107.0, "low": 105.0, "close": 106.0})
    out = lf._observe({"trigger_epoch": t0 - 1}, candles)
    cp = out["checkpoints"]
    assert out["forward_status"] == "OBSERVED" and out["reference_entry"] == {"epoch": t0, "price": 100.0, "source": "next_available_minute_open"}
    assert cp["+5m"]["mfe_pct"] == 3.0 and cp["+5m"]["mae_pct"] == -2.0
    assert cp["EOD"]["exit_price"] == 106.0 and cp["EOD"]["observed_epoch"] == _ts(day, 15, 21)  # last candle at/after 15:20
    # without a >=15:20 candle EOD stays pending
    assert lf._observe({"trigger_epoch": t0 - 1}, candles[:8])["checkpoints"]["EOD"] == {"status": "pending"}


# ---------- _summary gates ----------

def _row(day, symbol, gross):
    return {"trigger_day": day, "symbol": symbol, "checkpoints": {"+30m": {"status": "observed", "gross_return_pct": gross}}}


COST = {"live_deployment_equity": {"total_drag_with_slippage_pct": 0.1}, "mock_observed": {"total_drag_with_slippage_pct": 0.05}}


def _good_rows(n=12):
    days = [f"2026-08-0{d}" for d in (3, 4, 5, 6, 7)]
    return [_row(days[i % 5], f"S{i:02d}", 0.4 if i % 3 else -0.1) for i in range(n)]


def test_summary_collecting_below_decision_count():
    s = lf._summary(_good_rows(11), COST)
    assert s["status"] == "COLLECTING" and s["observed_30m_count"] == 11 and s["gates"]["minimum_observed_count"] is False
    assert s["decision_at_observed_count"] == 12


def test_summary_eligible_when_every_gate_passes_and_costs_applied():
    s = lf._summary(_good_rows(), COST)
    assert s["status"] == "ELIGIBLE_FOR_REINJECTION_SHADOW" and all(s["gates"].values())
    h = s["horizons"]["+30m"]
    assert h["gross"]["count"] == 12
    assert h["live_net"]["average_return_pct"] == pytest.approx(h["gross"]["average_return_pct"] - 0.1, abs=1e-3)
    assert h["mock_net"]["average_return_pct"] == pytest.approx(h["gross"]["average_return_pct"] - 0.05, abs=1e-3)
    assert s["largest_day_share"] == pytest.approx(0.25) and s["largest_symbol_share"] == pytest.approx(1 / 12, abs=1e-4)


@pytest.mark.parametrize("mutate,gate", [
    (lambda r: [dict(x, trigger_day="2026-08-03") for x in r], "minimum_day_count"),
    (lambda r: [dict(x, symbol="SAME") for x in r], "maximum_symbol_concentration"),
    (lambda r: [_row("2026-08-03" if i < 4 else f"2026-08-0{3 + i % 5}", f"S{i}", 0.4) for i, _ in enumerate(r)], "maximum_day_concentration"),
    (lambda r: [_row(x["trigger_day"], x["symbol"], -0.5) for x in r], "positive_expectancy"),
])
def test_summary_rejected_when_a_single_gate_fails(mutate, gate):
    s = lf._summary(mutate(_good_rows()), COST)
    assert s["gates"][gate] is False and s["status"] == "REJECTED"


def test_summary_empty_rows_is_collecting_with_zero_shares():
    s = lf._summary([], {})
    assert s["status"] == "COLLECTING" and s["positive_day_ratio"] == 0.0 and s["largest_day_share"] == 0.0 and s["fresh_trigger_count"] == 0


# ---------- cache helpers & trigger-day status ----------

def test_cache_roundtrip_skips_empty_symbols_and_reads_fail_soft(tmp_path):
    lf._cache_write(tmp_path, "2026-08-04", {"AAA": [{"ts": 1}], "EMPTY": []})
    assert sorted(p.name for p in (tmp_path / "2026-08-04").iterdir()) == ["AAA.json"]
    got = lf._cache_read(tmp_path, "2026-08-04", ("AAA", "EMPTY", "MISSING"))
    assert got == {"AAA": [{"ts": 1}], "EMPTY": [], "MISSING": []}
    (tmp_path / "2026-08-04" / "BAD.json").write_text("{bad", encoding="utf-8")
    assert lf._cache_read(tmp_path, "2026-08-04", ("BAD",)) == {"BAD": []}


def test_trigger_day_status(tmp_path):
    d = tmp_path / "2026-08-04"
    d.mkdir()
    (d / "opening_rank1_shadow_daily.json").write_text(json.dumps({"day_status": "VALID"}), encoding="utf-8")
    assert lf._trigger_day_status(tmp_path, "2026-08-04") == "VALID"
    (d / "opening_rank1_shadow_daily.json").write_text(json.dumps({}), encoding="utf-8")
    assert lf._trigger_day_status(tmp_path, "2026-08-04") == "MISSING"
    (d / "opening_rank1_shadow_daily.json").write_text("{bad", encoding="utf-8")
    assert lf._trigger_day_status(tmp_path, "2026-08-04") == "MISSING"
    assert lf._trigger_day_status(tmp_path, "2026-08-09") == "MISSING"


# ---------- build ----------

def _watch(day="2026-08-04", epoch=None, symbol="005930"):
    epoch = epoch or _ts(day, 9, 5) - 1
    return {"through_day": day, "rows": [{"watch_id": "W", "initial_episode_id": "E", "initial_day": "2026-08-03", "symbol": symbol,
                                          "redetections": [{"first_signal_evidence": {"day": day, "decision_id": "D", "decision_epoch": epoch, "rank": 1}}]}]}


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    calls = []
    t0 = _ts("2026-08-04", 9, 5)

    def loader(*, state_path, day, symbols, allow_fresh_fetch):
        calls.append((day, tuple(symbols), allow_fresh_fetch, Path(state_path)))
        return {s: _candles(t0, 40, 100.0, 0.1) for s in symbols}, {}

    monkeypatch.setattr(lf, "load_opening_candles", loader)
    monkeypatch.setattr(lf, "load_broker_cost_profile", lambda p: {})
    monkeypatch.setattr(lf, "build_evaluation_cost_bases", lambda profile: COST)
    root = tmp_path / "evaluation" / "opening_rank1_shadow"
    out = root / "latent"
    out.mkdir(parents=True)
    (root / "2026-08-04").mkdir()
    (root / "2026-08-04" / "opening_rank1_shadow_daily.json").write_text(json.dumps({"day_status": "VALID"}), encoding="utf-8")
    return tmp_path, out, calls


def test_build_writes_outputs_and_cwd_relative_candle_cache(env):
    tmp, out, calls = env
    res = lf.build_latent_reactivation_forward(watch_payload=_watch(), state_path=tmp / "state.json", output_root=out, allow_fresh_fetch=False)
    assert Path(res["json"]) == out / "latent_reactivation_forward.json" and Path(res["markdown"]) == out / "latent_reactivation_forward.md"
    payload = json.loads(Path(res["json"]).read_text(encoding="utf-8"))
    assert payload["schema_version"] == "latent_reactivation_forward.v1" and payload["policy_change_authorized"] is False
    assert payload["rows"][0]["forward_status"] == "OBSERVED" and payload["summary"]["raw_fresh_trigger_count"] == 1
    assert calls == [("2026-08-04", ("005930",), False, tmp / "state.json")]
    # the candle cache lands under the CWD (tmp here), NOT under output_root: current behavior
    assert (tmp / CACHE_REL / "2026-08-04" / "005930.json").exists()
    assert not list(out.rglob("005930.json"))
    md = Path(res["markdown"]).read_text(encoding="utf-8")
    assert "This artifact cannot submit an order or reinject a candidate." in md and "Original position carry: false" in md


def test_build_second_run_uses_cache_and_does_not_reload_candles(env):
    tmp, out, calls = env
    kw = dict(watch_payload=_watch(), state_path=tmp / "state.json", output_root=out, allow_fresh_fetch=True)
    lf.build_latent_reactivation_forward(**kw)
    lf.build_latent_reactivation_forward(**kw)
    assert len(calls) == 1


def test_build_excludes_triggers_on_invalid_or_missing_days(env):
    tmp, out, calls = env
    res = lf.build_latent_reactivation_forward(watch_payload=_watch(day="2026-08-05"), state_path=tmp / "s.json", output_root=out, allow_fresh_fetch=False)
    payload = json.loads(Path(res["json"]).read_text(encoding="utf-8"))
    row = payload["rows"][0]
    assert row["forward_status"] == "EXCLUDED_TRIGGER_DAY_INTEGRITY" and row["forward_reason"] == "opening_day_status:MISSING"
    assert payload["summary"]["excluded_trigger_count"] == 1 and payload["summary"]["fresh_trigger_count"] == 0
    assert calls == [] and not (tmp / "data").exists()                                   # no candle load, no cache write


def test_build_requires_existing_output_root(env):
    tmp, out, calls = env
    with pytest.raises(FileNotFoundError):
        lf.build_latent_reactivation_forward(watch_payload=_watch(), state_path=tmp / "s.json", output_root=tmp / "missing" / "latent", allow_fresh_fetch=False)


# ---------- gate boundaries (each gate flips at its documented threshold, others held passing) ----------

def _gates(rows):
    return lf._summary(rows, {})["gates"]            # zero cost so gross == net


def _spread(returns, days=5):
    """one row per return, distinct symbols, days assigned round-robin."""
    return [_row(f"2026-08-{3 + i % days:02d}", f"S{i:02d}", r) for i, r in enumerate(returns)]


def test_gate_minimum_day_count_boundary():
    rets = [0.5] * 12
    assert _gates(_spread(rets, days=5))["minimum_day_count"] is True
    assert _gates(_spread(rets, days=4))["minimum_day_count"] is False


def test_gate_day_concentration_boundary_is_inclusive_at_25pct():
    rets = [0.5] * 12
    rows = [_row("2026-08-03" if i < 3 else f"2026-08-{4 + (i - 3) % 4:02d}", f"S{i:02d}", r) for i, r in enumerate(rets)]   # 3/12 = 0.25
    assert _gates(rows)["maximum_day_concentration"] is True
    rows[3] = _row("2026-08-03", "S03", 0.5)                                                                               # 4/12 > 0.25
    assert _gates(rows)["maximum_day_concentration"] is False


def test_gate_symbol_concentration_boundary_is_inclusive_at_25pct():
    rows = _spread([0.5] * 12)
    for i in range(3):
        rows[i]["symbol"] = "DUP"                                                                                          # 3/12 = 0.25
    assert _gates(rows)["maximum_symbol_concentration"] is True
    rows[3]["symbol"] = "DUP"
    assert _gates(rows)["maximum_symbol_concentration"] is False


def test_gate_win_rate_and_profit_factor_thresholds():
    # 6 wins / 6 losses -> win_rate 0.5 passes; 5 / 7 fails
    assert _gates(_spread([2.0] * 6 + [-1.0] * 6))["minimum_win_rate"] is True
    assert _gates(_spread([2.0] * 5 + [-1.0] * 7))["minimum_win_rate"] is False
    # PF = gain/loss: 12/10 = 1.2 passes, 11/10 fails
    assert _gates(_spread([2.0] * 6 + [-1.0] * 6 + []))["minimum_profit_factor"] is True            # 12/6 = 2.0
    pf12 = _spread([1.2] + [0.0001] * 0 + [-1.0] * 1 + [0.0] * 10)                                  # 1.2/1.0
    assert lf._summary(pf12, {})["horizons"]["+30m"]["live_net"]["profit_factor"] == pytest.approx(1.2)
    assert _gates(pf12)["minimum_profit_factor"] is True
    pf11 = _spread([1.1] + [-1.0] * 1 + [0.0] * 10)
    assert _gates(pf11)["minimum_profit_factor"] is False


def test_gate_positive_day_ratio_threshold():
    # 5 days; per-day mean > 0 on 3/5 days = 0.6 passes (>= 0.55), on 2/5 = 0.4 fails
    def rows_for(pos_days):
        out = []
        for d in range(5):
            val = 1.0 if d < pos_days else -1.0
            out += [_row(f"2026-08-{3 + d:02d}", f"S{d}{k}", val) for k in range(3)]
        return out[:15]

    assert lf._summary(rows_for(3), {})["positive_day_ratio"] == 0.6 and _gates(rows_for(3))["minimum_positive_day_ratio"] is True
    assert _gates(rows_for(2))["minimum_positive_day_ratio"] is False


def test_observe_entry_is_strictly_after_trigger_epoch():
    candles = [{"ts": 100, "open": 90.0, "high": 90.0, "low": 90.0, "close": 90.0}, {"ts": 160, "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0}]
    assert lf._observe({"trigger_epoch": 100}, candles)["reference_entry"]["epoch"] == 160                # candle AT trigger is skipped


def test_gate_concentration_threshold_is_25pct_not_30pct():
    rows = [_row("2026-08-03" if i < 7 else f"2026-08-{4 + (i - 7) % 4:02d}", f"S{i:02d}", 0.5) for i in range(24)]   # 7/24 = 0.2917
    g = _gates(rows)
    assert g["maximum_day_concentration"] is False
    rows = _spread([0.5] * 24)
    for i in range(7):
        rows[i]["symbol"] = "DUP"
    assert _gates(rows)["maximum_symbol_concentration"] is False
