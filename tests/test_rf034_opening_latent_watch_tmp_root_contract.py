"""RF-034 C3: opening_rank1_shadow.latent_watch evidence rules, watch status ladder and tmp-root write contract.

``build_latent_reactivation_forward`` is stubbed (it writes a CWD-relative candle cache, covered by the latent_forward
contract), and the CWD is moved to tmp_path as a safety net so no repo-relative path can be touched.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from libs.reporting.opening_rank1_shadow import latent_forward as lf
from libs.reporting.opening_rank1_shadow import latent_watch as lw


@pytest.fixture(autouse=True)
def _cwd(tmp_path, monkeypatch):
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    seen = []

    def fake_forward(*, watch_payload, state_path, output_root, allow_fresh_fetch):
        seen.append({"payload": watch_payload, "state_path": state_path, "output_root": Path(output_root), "fetch": allow_fresh_fetch})
        return {"json": "F.json", "markdown": "F.md", "summary": {"status": "COLLECTING"}}

    monkeypatch.setattr(lf, "build_latent_reactivation_forward", fake_forward)
    return seen


# ---------- signal evidence ----------

@pytest.mark.parametrize("cand,expected", [
    ({}, (False, False, False, 0)),
    ({"score_breakdown": {"volume_surge": 0.1}}, (True, False, False, 1)),
    ({"score_breakdown": {"vwap_alignment": 0.1}}, (False, True, False, 1)),
    ({"above_vwap": True}, (False, True, False, 1)),
    ({"compact_feature_snapshot": {"above_vwap": True}}, (False, True, False, 1)),
    ({"above_vwap": 1}, (False, False, False, 0)),                                                          # strictly True only
    ({"above_vwap": "yes"}, (False, False, False, 0)),
    ({"above_vwap": False, "compact_feature_snapshot": {"above_vwap": True}}, (False, False, False, 0)),   # candidate key wins
    ({"score_breakdown": {"momentum": 1, "intraday_strength": 0}}, (False, False, False, 0)),              # both required
    ({"score_breakdown": {"momentum": 1, "intraday_strength": 1}}, (False, False, True, 1)),
    ({"score_breakdown": {"volume_surge": 1, "vwap_alignment": 1, "momentum": 1, "intraday_strength": 1}}, (True, True, True, 3)),
    ({"score_breakdown": "bad", "compact_feature_snapshot": None}, (False, False, False, 0)),
])
def test_candidate_signal_evidence(cand, expected):
    e = lw._candidate_signal_evidence(cand)
    assert (e["volume_confirmation"], e["vwap_confirmation"], e["breakout_confirmation"], e["evidence_count"]) == expected
    assert e["status"] == ("SIGNAL_EVIDENCE_OBSERVED" if expected[3] else "REDETECTED_WITHOUT_SIGNAL_EVIDENCE")


def test_decision_time_and_read_write(tmp_path):
    assert lw._decision_time(0) == "" and lw._decision_time(-5) == ""
    assert lw._decision_time(1_785_000_000).endswith("+09:00")
    p = tmp_path / "a" / "b.json"
    lw._write_json(p, {"k": "한"})
    assert lw._read_json(p) == {"k": "한"} and p.read_text(encoding="utf-8").endswith("\n")
    p.write_text("[1]", encoding="utf-8")
    assert lw._read_json(p) == {} and lw._read_json(tmp_path / "none.json") == {}
    p.write_text("{bad", encoding="utf-8")
    assert lw._read_json(p) == {}


# ---------- fixtures ----------

def _windows(reports: Path, day: str, windows):
    p = reports / "operator_summary" / "daily" / day / "q9_decision_windows.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"windows": windows}), encoding="utf-8")


def _win(symbol, epoch, rank=3, *, breakdown=None, decision_id=None, wtype="scanner_selection"):
    return {"window_type": wtype, "decision_id": decision_id or f"D{epoch}", "decision_epoch": epoch,
            "scanner_pre_strategist_universe": {"intrinsic_ranked_top20": [
                {"symbol": "OTHER", "rank": 1}, {"symbol": symbol, "rank": rank, "score_breakdown": breakdown or {}, "compact_feature_snapshot": {"engine_close_last": 123.0}}]}}


def _opening(root: Path, day: str, episodes, status="VALID"):
    p = root / day / "opening_rank1_shadow_daily.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"day_status": status, "episodes": episodes}), encoding="utf-8")


def _episode(day, symbol, ret, status="observed", eid=None):
    return {"episode_id": eid or f"E:{day}:{symbol}", "day": day, "symbol": symbol, "checkpoints": {"+30m": {"status": status, "live_net_return_pct": ret}}}


# ---------- calendar & initial episodes ----------

def test_trading_days_requires_dir_window_file_and_bound(tmp_path):
    reports = tmp_path / "reports"
    assert lw._trading_days(reports, "2026-08-31") == []
    for day in ("2026-08-03", "2026-08-05", "2026-09-01"):
        _windows(reports, day, [])
    (reports / "operator_summary" / "daily" / "2026-08-04").mkdir()                       # no windows file
    (reports / "operator_summary" / "daily" / "short").mkdir()                            # wrong length
    (reports / "operator_summary" / "daily" / "2026-08-06").write_text("x", encoding="utf-8")   # file, not dir
    assert lw._trading_days(reports, "2026-08-31") == ["2026-08-03", "2026-08-05"]
    assert lw._trading_days(reports, "2026-08-03") == ["2026-08-03"]                      # inclusive bound


def test_initial_episodes_only_valid_days_observed_nonpositive_and_first_per_day_symbol(tmp_path):
    _opening(tmp_path, "2026-08-03", [
        _episode("2026-08-03", "A", -0.5, eid="first"), _episode("2026-08-03", "A", -0.9, eid="dup"),
        _episode("2026-08-03", "B", 0.0, eid="zero"), _episode("2026-08-03", "C", 0.3),
        _episode("2026-08-03", "D", -1.0, status="pending"), "junk"])
    _opening(tmp_path, "2026-08-04", [_episode("2026-08-04", "A", -2.0)], status="INVALID")
    got = lw._initial_episodes(tmp_path)
    assert [e["episode_id"] for e in got] == ["first", "zero"]


# ---------- reappearances ----------

def test_reappearances_compact_per_day_with_first_signal_and_best_rank(tmp_path):
    reports = tmp_path / "reports"
    _windows(reports, "2026-08-04", [
        _win("A", 200, rank=5), _win("A", 100, rank=3), _win("A", 300, rank=2, breakdown={"volume_surge": 1}),
        _win("A", 50, wtype="other"), _win("B", 150), "junk"])
    _windows(reports, "2026-08-05", [_win("B", 10)])
    rows = lw._candidate_reappearances(reports_root=reports, symbol="A", days=["2026-08-04", "2026-08-05"])
    assert len(rows) == 1                                                                 # B-only day yields nothing for A
    r = rows[0]
    assert r["day"] == "2026-08-04" and r["decision_epoch"] == 100 and r["observation_count"] == 3   # earliest row is the base
    assert r["best_rank"] == 2 and r["reference_price"] == 123.0
    assert r["first_signal_evidence"]["decision_epoch"] == 300 and r["first_signal_evidence"]["signal_evidence"]["evidence_count"] == 1
    assert lw._candidate_reappearances(reports_root=reports, symbol="ZZZ", days=["2026-08-04"]) == []


# ---------- build ----------

def _setup(tmp_path):
    reports, opening = tmp_path / "reports", tmp_path / "opening"
    _opening(opening, "2026-08-03", [_episode("2026-08-03", "A", -0.5)])
    return reports, opening


def _build(reports, opening, through="2026-09-30", **kw):
    return lw.build_latent_reactivation_watch(reports_root=reports, opening_output_root=opening, through_day=through, **kw)


def test_status_watching_until_five_future_days_then_not_redetected(tmp_path, _cwd):
    reports, opening = _setup(tmp_path)
    for d in ("2026-08-03", "2026-08-04", "2026-08-05", "2026-08-06", "2026-08-07"):
        _windows(reports, d, [])
    row = json.loads(Path(_build(reports, opening)["json"]).read_text(encoding="utf-8"))["rows"][0]
    assert row["watch_status"] == "WATCHING" and row["observed_watch_day_count"] == 4          # only 4 days after the initial day
    for d in ("2026-08-10", "2026-08-11"):
        _windows(reports, d, [])
    row = json.loads(Path(_build(reports, opening)["json"]).read_text(encoding="utf-8"))["rows"][0]
    assert row["watch_status"] == "NOT_REDETECTED_D5" and row["observed_watch_days"] == ["2026-08-04", "2026-08-05", "2026-08-06", "2026-08-07", "2026-08-10"]


def test_status_redetected_with_and_without_signal_and_summary_counts(tmp_path):
    reports, opening = _setup(tmp_path)
    _opening(opening, "2026-08-03", [_episode("2026-08-03", s, -0.5) for s in ("A", "B", "C")])
    _windows(reports, "2026-08-04", [_win("A", 100, breakdown={"volume_surge": 1}), _win("B", 100), _win("C", 100, breakdown={"vwap_alignment": 1})])
    res = _build(reports, opening)
    rows = {r["symbol"]: r for r in json.loads(Path(res["json"]).read_text(encoding="utf-8"))["rows"]}
    assert rows["A"]["watch_status"] == "REDETECTED_WITH_SIGNAL_EVIDENCE" and rows["B"]["watch_status"] == "REDETECTED_WITHOUT_SIGNAL_EVIDENCE"
    assert rows["C"]["watch_status"] == "REDETECTED_WITH_SIGNAL_EVIDENCE"
    assert res["summary"] == {"watch_count": 3, "redetected_count": 3, "signal_evidence_count": 2,
                              "status_counts": {"REDETECTED_WITHOUT_SIGNAL_EVIDENCE": 1, "REDETECTED_WITH_SIGNAL_EVIDENCE": 2}}
    assert rows["A"]["policy_effect"] == "NONE_OBSERVER_ONLY" and rows["A"]["initial_30m_net_pct"] == -0.5


def test_build_writes_only_latent_watch_dir_and_hands_payload_to_forward(tmp_path, _cwd):
    reports, opening = _setup(tmp_path)
    before = {p for p in tmp_path.rglob("*") if p.is_file()}
    res = _build(reports, opening, state_path=tmp_path / "s.json", allow_fresh_fetch=False)
    new = {p for p in tmp_path.rglob("*") if p.is_file()} - before
    assert new == {opening / "latent_watch" / "latent_reactivation_watch.json", opening / "latent_watch" / "latent_reactivation_watch.md"}
    assert not (tmp_path / "cwd" / "data").exists()
    assert res["forward_json"] == "F.json" and res["forward_markdown"] == "F.md" and res["forward_summary"] == {"status": "COLLECTING"}
    call = _cwd[0]
    assert call["output_root"] == opening / "latent_watch" and call["state_path"] == tmp_path / "s.json" and call["fetch"] is False
    payload = json.loads(Path(res["json"]).read_text(encoding="utf-8"))
    assert call["payload"] == payload and payload["schema_version"] == "latent_reactivation_watch.v1" and payload["watch_horizon_trading_days"] == 5
    md = Path(res["markdown"]).read_text(encoding="utf-8")
    assert "# Latent Reactivation Watch" in md and "| 2026-08-03 | A | -0.5000% | WATCHING |" in md and "never carries the original position forward" in md


def test_build_with_no_episodes_still_writes_empty_watch(tmp_path):
    res = _build(tmp_path / "reports", tmp_path / "opening")
    payload = json.loads(Path(res["json"]).read_text(encoding="utf-8"))
    assert payload["rows"] == [] and payload["summary"]["status_counts"] == {} and payload["summary"]["watch_count"] == 0
