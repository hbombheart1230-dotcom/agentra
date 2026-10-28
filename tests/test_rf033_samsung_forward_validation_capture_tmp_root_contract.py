"""RF-033 C3: samsung_hynix.forward_validation preopen capture ladder, immutability, cumulative and reaction classification.

Provider is an in-memory fake (yfinance never constructed), collaborators with heavy inputs are stubbed in the pipeline
module, and every path is under tmp_path.
"""
from __future__ import annotations

import json
import socket
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from libs.reporting.baseline_samsung_hynix.forward_validation import cumulative as cum
from libs.reporting.baseline_samsung_hynix.forward_validation import expected_actual as ea
from libs.reporting.baseline_samsung_hynix.forward_validation import market_inputs as mi
from libs.reporting.baseline_samsung_hynix.forward_validation import pipeline as pl
from libs.reporting.baseline_samsung_hynix.forward_validation.contracts import ACTIVATION_DAY, PROGRAM_ID, SCHEMA_VERSION, THRESHOLDS

KST = timezone(timedelta(hours=9))
DAY = "2026-09-01"                          # >= ACTIVATION_DAY


@pytest.fixture(autouse=True)
def _guard(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("network attempt")

    monkeypatch.setattr(socket.socket, "connect", _boom)
    monkeypatch.setattr(socket, "create_connection", _boom)

    def _no_default_provider(*a, **k):
        raise AssertionError("default yfinance provider must not be constructed")

    monkeypatch.setattr(pl, "YFinanceLeadMarketProvider", _no_default_provider)


def _at(h, m, s=0, day=DAY):
    y, mo, d = map(int, day.split("-"))
    return datetime(y, mo, d, h, m, s, tzinfo=KST)


class FakeProvider:
    def __init__(self, observations):
        self.observations, self.calls = observations, []

    def capture(self, *, as_of):
        self.calls.append(as_of)
        return self.observations


def _obs(available=True):
    status = "AVAILABLE" if available else "UNAVAILABLE"
    row = {"status": status, "return_pct": 6.0, "current": 100.0, "previous": 94.0, "three_day_return_pct": 1.0}
    return {k: dict(row) for k in ("sox", "nvidia", "micron", "samsung", "sk_hynix", "nasdaq", "sp500", "us10y", "vix", "hynix_adr")}


def _capture(tmp_path, now, provider, day=DAY):
    return pl.capture_q10_preopen_snapshot(day=day, reports_root=tmp_path / "reports", state_path=tmp_path / "state.json", now=now, lead_market_provider=provider)


def _snap_path(tmp_path, day=DAY):
    return tmp_path / "reports/evaluation/baseline_samsung_hynix" / day / "q10_forward_validation/q10_preopen_signal_snapshot.json"


# ---------- preopen capture ----------

def test_before_activation_day_nothing_happens(tmp_path):
    p = FakeProvider(_obs())
    out = _capture(tmp_path, _at(8, 55, day="2026-08-30"), p, day="2026-08-30")
    assert out == {"q10_preopen_capture_status": "NOT_ACTIVE_PROSPECTIVE_ONLY", "day": "2026-08-30"}
    assert p.calls == [] and not (tmp_path / "reports").exists()
    assert "2026-08-30" < ACTIVATION_DAY


def test_waiting_before_0850_writes_nothing(tmp_path):
    p = FakeProvider(_obs())
    out = _capture(tmp_path, _at(8, 49, 59), p)
    assert out["q10_preopen_capture_status"] == "WAITING" and out["path"] == "" and p.calls == []
    assert not _snap_path(tmp_path).exists()


def test_capture_inside_window_is_persisted_and_scored(tmp_path):
    p = FakeProvider(_obs())
    out = _capture(tmp_path, _at(8, 50), p)                                    # window start is inclusive
    assert out["q10_preopen_capture_status"] == "CAPTURED" and out["path"] == str(_snap_path(tmp_path)) and len(p.calls) == 1
    snap = json.loads(_snap_path(tmp_path).read_text(encoding="utf-8"))
    assert snap["capture_status"] == "CAPTURED" and snap["evaluation_program_id"] == PROGRAM_ID and snap["schema_version"] == SCHEMA_VERSION
    assert snap["observation_summary"] == {"total": 10, "available": 10}
    assert set(snap["signals"]) == {"sk_hynix", "samsung", "hynix_extension", "korea_market"}
    assert snap["signal_inputs"]["sox_return_pct"] == 6.0 and snap["guards"]["historical_backfill_allowed"] is False
    assert snap["capture_window_kst"] == [_at(8, 50).isoformat(), _at(8, 59, 59).isoformat()]


def test_all_unavailable_is_data_unavailable_not_captured(tmp_path):
    out = _capture(tmp_path, _at(8, 55), FakeProvider(_obs(available=False)))
    assert out["q10_preopen_capture_status"] == "DATA_UNAVAILABLE" and out["reason"] == "all_lead_market_observations_unavailable"
    assert json.loads(_snap_path(tmp_path).read_text(encoding="utf-8"))["observation_summary"]["available"] == 0


def test_window_deadline_boundary_and_missed_is_immutable_no_backfill(tmp_path):
    p = FakeProvider(_obs())
    assert _capture(tmp_path / "a", _at(8, 59, 59), p)["q10_preopen_capture_status"] == "CAPTURED"      # deadline inclusive
    out = _capture(tmp_path / "b", _at(9, 0, 0), p)
    assert out["q10_preopen_capture_status"] == "MISSED" and out["reason"] == "08:50_preopen_capture_window_missed_no_backfill"
    assert len(p.calls) == 1                                                                           # provider never asked after the window
    # a later in-window-looking call cannot replace the persisted MISSED snapshot
    again = _capture(tmp_path / "b", _at(8, 55), p)
    assert again["q10_preopen_capture_status"] == "MISSED" and len(p.calls) == 1


def test_existing_snapshot_is_returned_verbatim_and_never_recaptured(tmp_path):
    p = FakeProvider(_obs())
    _capture(tmp_path, _at(8, 51), p)
    first = _snap_path(tmp_path).read_text(encoding="utf-8")
    p2 = FakeProvider(_obs(available=False))
    out = _capture(tmp_path, _at(8, 52), p2)
    assert out["q10_preopen_capture_status"] == "CAPTURED" and p2.calls == [] and _snap_path(tmp_path).read_text(encoding="utf-8") == first


def test_write_is_atomic_temp_then_replace(tmp_path):
    _capture(tmp_path, _at(8, 55), FakeProvider(_obs()))
    assert sorted(x.name for x in _snap_path(tmp_path).parent.iterdir()) == ["q10_preopen_signal_snapshot.json"]


def test_read_treats_corrupt_snapshot_as_absent(tmp_path):
    p = _snap_path(tmp_path)
    p.parent.mkdir(parents=True)
    p.write_text("{corrupt", encoding="utf-8")
    assert pl._read(p) == {}
    out = _capture(tmp_path, _at(8, 55), FakeProvider(_obs()))                                         # corrupt file is replaced by a real capture
    assert out["q10_preopen_capture_status"] == "CAPTURED"


# ---------- forward validation orchestration ----------

def test_before_activation_forward_validation_is_inactive(tmp_path):
    out = pl.build_q10_forward_validation(day="2026-08-30", output_dir=tmp_path / "d", state_path=tmp_path / "s", macro_root=tmp_path / "m", candle_map={}, cost_pct=0.1, slippage_pct=0.05)
    assert out == {"q10_forward_validation_status": "NOT_ACTIVE_PROSPECTIVE_ONLY"} and not (tmp_path / "d").exists()


def test_forward_validation_writes_expected_file_set_and_cumulative_in_parent(tmp_path, monkeypatch):
    monkeypatch.setattr(pl, "build_actual_reactions", lambda **kw: {"targets": {"samsung": {"opening_gap_pct": 1.0}}})
    monkeypatch.setattr(pl, "build_shadow_comparison", lambda **kw: {"outcomes": [{"status": "OBSERVED", "target": "samsung", "policy": "ENTRY_0900", "net_eod_return_pct": 1.5}]})
    monkeypatch.setattr(pl, "render_forward_validation_report", lambda **kw: f"REPORT {kw['day']}\n")
    root = tmp_path / "reports" / "evaluation" / "baseline_samsung_hynix"
    out_dir = root / DAY
    res = pl.build_q10_forward_validation(day=DAY, output_dir=out_dir, state_path=tmp_path / "s.json", macro_root=tmp_path / "m", candle_map={},
                                          cost_pct=0.1, slippage_pct=0.05, now=_at(8, 55), lead_market_provider=FakeProvider(_obs()))
    fv = out_dir / "q10_forward_validation"
    assert {p.name for p in fv.iterdir()} == {"q10_preopen_signal_snapshot.json", "q10_actual_market_reactions.json", "q10_expected_vs_actual.json",
                                              "q10_shadow_entry_comparison.json", "q10_forward_validation_report.md"}
    assert (root / "q10_forward_validation_cumulative.json").exists() and not (fv / "q10_forward_validation_cumulative.json").exists()
    assert res["q10_forward_validation_status"] == "CAPTURED" and res["q10_forward_validation_report"] == str(fv / "q10_forward_validation_report.md")
    assert res["q10_forward_validation_cumulative"] == str(root / "q10_forward_validation_cumulative.json")
    shadow = json.loads((fv / "q10_shadow_entry_comparison.json").read_text(encoding="utf-8"))
    assert shadow["day"] == DAY and shadow["evaluation_program_id"] == PROGRAM_ID and shadow["guards"]["prospective_only"] is True
    cumulative = json.loads((root / "q10_forward_validation_cumulative.json").read_text(encoding="utf-8"))
    assert cumulative["observed_outcome_count"] == 1 and cumulative["days"] == [DAY]
    expected = json.loads((fv / "q10_expected_vs_actual.json").read_text(encoding="utf-8"))
    assert {r["target"] for r in expected["rows"]} == {"samsung", "sk_hynix", "kospi", "kosdaq"} and expected["day"] == DAY
    assert (fv / "q10_forward_validation_report.md").read_text(encoding="utf-8") == f"REPORT {DAY}\n"


def test_forward_validation_waiting_status_when_before_window(tmp_path, monkeypatch):
    monkeypatch.setattr(pl, "build_actual_reactions", lambda **kw: {"targets": {}})
    monkeypatch.setattr(pl, "build_shadow_comparison", lambda **kw: {"outcomes": []})
    monkeypatch.setattr(pl, "render_forward_validation_report", lambda **kw: "R\n")
    out_dir = tmp_path / "root" / DAY
    res = pl.build_q10_forward_validation(day=DAY, output_dir=out_dir, state_path=tmp_path / "s", macro_root=tmp_path / "m", candle_map={}, cost_pct=0, slippage_pct=0,
                                          now=_at(8, 0), lead_market_provider=FakeProvider(_obs()))
    assert res["q10_forward_validation_status"] == "WAITING" and res["q10_preopen_snapshot"] == ""


# ---------- cumulative ----------

def _shadow(root: Path, day, outcomes):
    p = root / day / "q10_forward_validation" / "q10_shadow_entry_comparison.json"
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps({"day": day, "outcomes": outcomes}) if not isinstance(outcomes, str) else outcomes, encoding="utf-8")


def _o(target, policy, ret, status="OBSERVED", **kw):
    return {"target": target, "policy": policy, "status": status, "net_eod_return_pct": ret, **kw}


def test_cumulative_groups_metrics_and_filters(tmp_path):
    _shadow(tmp_path, "2026-08-28", [_o("samsung", "ENTRY_0900", 9.0)])                       # before activation -> ignored
    _shadow(tmp_path, "2026-09-01", [_o("samsung", "ENTRY_0900", 2.0, mfe_pct=3.0, mae_pct=-1.0), _o("samsung", "ENTRY_0900", -1.0, mfe_pct=1.0, mae_pct=-2.0),
                                     _o("samsung", "ENTRY_0900", 5.0, status="PENDING"), _o("sk_hynix", "ENTRY_0903", 1.0, extension_state="EXTENDED")])
    _shadow(tmp_path, "2026-09-02", [_o("samsung", "ENTRY_0900", 1.0, evaluation_bucket="SAMSUNG_SPECIFIC_EVENT")])
    _shadow(tmp_path, "2026-09-03", "{corrupt")
    out = cum.build_cumulative(tmp_path)
    assert out["schema_version"] == "q10_korea_lead_market_cumulative.v1" and out["prospective_start_day"] == ACTIVATION_DAY
    assert out["days"] == ["2026-09-01", "2026-09-02"] and out["day_count"] == 2 and out["observed_outcome_count"] == 4
    by = {(r["target"], r["policy"], r["evaluation_bucket"], r["extension_state"]): r for r in out["summary"]}
    g = by[("samsung", "ENTRY_0900", "LEAD_MARKET_SIGNAL", "N/A")]
    assert g["trade_count"] == 2 and g["win_rate"] == 50.0 and g["average_return_pct"] == 0.5 and g["median_return_pct"] == 0.5
    assert g["profit_factor"] == 2.0 and g["max_drawdown_pct"] == -1.0 and g["average_mfe_pct"] == 2.0 and g["average_mae_pct"] == -1.5
    assert ("samsung", "ENTRY_0900", "SAMSUNG_SPECIFIC_EVENT", "N/A") in by and ("sk_hynix", "ENTRY_0903", "LEAD_MARKET_SIGNAL", "EXTENDED") in by


def test_cumulative_profit_factor_and_drawdown_edges(tmp_path):
    _shadow(tmp_path, "2026-09-01", [_o("a", "p", 2.0), _o("a", "p", -3.0), _o("a", "p", -1.0), _o("b", "p", 1.0), _o("c", "p", -1.0), _o("d", "p", 0.0)])
    by = {r["target"]: r for r in cum.build_cumulative(tmp_path)["summary"]}
    assert by["a"]["max_drawdown_pct"] == -4.0 and by["a"]["profit_factor"] == 0.5
    assert by["b"]["profit_factor"] == "INF" and by["c"]["profit_factor"] == 0.0 and by["d"]["profit_factor"] is None


def test_cumulative_empty_root(tmp_path):
    out = cum.build_cumulative(tmp_path / "none")
    assert out["summary"] == [] and out["day_count"] == 0 and out["days"] == []


# ---------- reaction classification & expected/actual ----------

@pytest.mark.parametrize("state,gap,expected", [
    ("POSITIVE", None, "INSUFFICIENT_EVIDENCE"),
    ("NEUTRAL", THRESHOLDS["neutral_fair_gap_pct"], "FAIR_REACTION"),            # boundary inclusive
    ("NEUTRAL", -0.51, "DIVERGENCE"),
    ("UNKNOWN_STATE", 0.4, "FAIR_REACTION"),                                    # unknown state behaves as neutral
    ("POSITIVE", -0.30, "DIVERGENCE"),                                          # opposite sign at threshold
    ("POSITIVE", -0.29, "UNDERREACTION"),                                       # opposite but below divergence threshold, ratio < 0.5
    ("POSITIVE", 0.39, "UNDERREACTION"),                                        # ratio 0.4875
    ("POSITIVE", 0.4, "FAIR_REACTION"),                                         # ratio 0.5
    ("POSITIVE", 1.2, "FAIR_REACTION"),                                         # ratio 1.5
    ("POSITIVE", 1.21, "OVERREACTION"),
    ("STRONG_POSITIVE", 3.0, "FAIR_REACTION"),                                  # ratio exactly 1.5 (float-exact)
    ("STRONG_POSITIVE", 3.01, "OVERREACTION"),
    ("STRONG_NEGATIVE", 3.0, "DIVERGENCE"),
    ("STRONG_RISK_OFF", -2.0, "FAIR_REACTION"),
])
def test_classify_reaction(state, gap, expected):
    assert ea.classify_reaction(expected_state=state, opening_gap_pct=gap) == expected


def test_build_expected_actual_rows_events_and_extension():
    signals = {"samsung": {"state": "POSITIVE"}, "sk_hynix": {"state": "STRONG_POSITIVE"}, "korea_market": {"state": "RISK_OFF"}, "hynix_extension": {"state": "EXTENDED"}}
    reactions = {"targets": {"samsung": {"opening_gap_pct": 0.8}, "sk_hynix": {"opening_gap_pct": None}, "kospi": {"opening_gap_pct": -0.8}}}
    rows = {r["target"]: r for r in ea.build_expected_actual(signals=signals, reactions=reactions, samsung_event={"samsung_specific_event": True})["rows"]}
    assert rows["samsung"]["evaluation_bucket"] == "SAMSUNG_SPECIFIC_EVENT" and rows["samsung"]["excluded_from_pure_signal_comparison"] is True
    assert rows["sk_hynix"]["reaction_state"] == "INSUFFICIENT_EVIDENCE" and rows["sk_hynix"]["extension_state"] == "EXTENDED"
    assert rows["kospi"]["expected_state"] == rows["kosdaq"]["expected_state"] == "RISK_OFF" and rows["kospi"]["reaction_state"] == "FAIR_REACTION"
    assert rows["kosdaq"]["opening_gap_pct"] is None and rows["samsung"]["extension_state"] is None and rows["samsung"]["expected_gap_pct"] == 0.8
    empty = {r["target"]: r for r in ea.build_expected_actual(signals={}, reactions={}, samsung_event={})["rows"]}
    assert {r["expected_state"] for r in empty.values()} == {"NEUTRAL"} and empty["sk_hynix"]["extension_state"] == "UNKNOWN"
    assert all(r["evaluation_bucket"] == "LEAD_MARKET_SIGNAL" for r in empty.values())


def test_activation_day_itself_is_active(tmp_path, monkeypatch):
    p = FakeProvider(_obs())
    out = _capture(tmp_path, _at(8, 55, day=ACTIVATION_DAY), p, day=ACTIVATION_DAY)
    assert out["q10_preopen_capture_status"] == "CAPTURED" and len(p.calls) == 1
    monkeypatch.setattr(pl, "build_actual_reactions", lambda **kw: {"targets": {}})
    monkeypatch.setattr(pl, "build_shadow_comparison", lambda **kw: {"outcomes": []})
    monkeypatch.setattr(pl, "render_forward_validation_report", lambda **kw: "R\n")
    res = pl.build_q10_forward_validation(day=ACTIVATION_DAY, output_dir=tmp_path / "r" / ACTIVATION_DAY, state_path=tmp_path / "s", macro_root=tmp_path / "m",
                                          candle_map={}, cost_pct=0, slippage_pct=0, now=_at(8, 55, day=ACTIVATION_DAY), lead_market_provider=FakeProvider(_obs()))
    assert res["q10_forward_validation_status"] == "CAPTURED"


def test_cumulative_includes_activation_day(tmp_path):
    _shadow(tmp_path, ACTIVATION_DAY, [_o("samsung", "ENTRY_0900", 1.0)])
    assert cum.build_cumulative(tmp_path)["days"] == [ACTIVATION_DAY]
