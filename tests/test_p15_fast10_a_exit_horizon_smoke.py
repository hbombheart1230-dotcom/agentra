"""FAST10 A10 tests: entry/exit timing evidence separation, malformed/zero handling and hot-path parity."""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

import pytest

from libs.reporting.evaluation import entry_timing_attribution as timing
from libs.reporting.evaluation import fast07_trade_projection as tp
from libs.reporting.evaluation import horizon_alignment as horizon
from libs.reporting.evaluation import loss_decomposition as loss

KST = timezone(timedelta(hours=9))
DECISION = 1780909200  # a regular-session KST instant


def _write(path: Path, payload: Any) -> None:
    import json
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


# --- timestamps: naive, aware and numeric forms read consistently -------------------------------------------


def test_naive_timestamps_are_korea_time_independent_of_the_host_zone() -> None:
    naive, aware = "2026-06-08T09:10:00", "2026-06-08T09:10:00+09:00"
    assert tp.epoch(naive) == tp.epoch(aware) == int(datetime(2026, 6, 8, 9, 10, tzinfo=KST).timestamp())
    assert tp.parse_ts(naive) == tp.parse_ts(aware) and tp.parse_ts(naive).tzinfo is not None
    assert tp.epoch("2026-06-08T00:10:00Z") == tp.epoch(aware)
    assert tp.epoch(1780909200) == tp.epoch("1780909200") == tp.epoch(1780909200.9) == DECISION
    for bad in (None, "", "unknown", "not-a-date", 0, "0"):
        assert tp.epoch(bad) == 0 or bad in (0, "0")
    assert tp.parse_ts("unknown") is None and tp.parse_ts("") is None


def test_mixed_naive_and_aware_pair_no_longer_raises() -> None:
    assert tp.holding_seconds("2026-06-08T09:00:00", "2026-06-08T09:30:00+09:00", None) == 1800
    assert tp.holding_seconds("2026-06-08T09:30:00+09:00", "2026-06-08T09:00:00", None) is None  # exit before entry stays unknown
    assert tp.holding_seconds("2026-06-08T09:00:00", "2026-06-08T09:30:00", 45) == 45  # recorded duration still wins
    assert tp.holding_seconds("2026-06-08T09:00:00", "2026-06-08T09:30:00", 0) == 1800  # zero is not a recorded duration


def _integrity(entry_ts: Any, exit_ts: Any, **kw: Any):
    args: Dict[str, Any] = dict(
        inventory={"missing_required": []}, entry={"x": 1}, realized_exit=True, entry_ts=entry_ts, exit_ts=exit_ts,
        broker_exit_authoritative=False, pnl_source="lifecycle", closeout_broker_skip={}, existing_broker_truth=False,
        partial_exit_duplicate={}, evaluation_exclusion={}, behavior_metric_excluded=False, exit_metric_excluded=False)
    args.update(kw)
    return tp.classify_trade_integrity(**args)


def test_integrity_classification_across_timestamp_forms() -> None:
    assert _integrity("2026-06-08T09:00:00", "2026-06-08T09:30:00+09:00")[0].value == "PASS"
    status, defects, _ = _integrity("2026-06-08T09:30:00+09:00", "2026-06-08T09:00:00")
    assert status.value == "BLOCKER" and defects == ["exit_before_entry"]
    status, defects, watch = _integrity("2026-06-08T09:00:00", "garbage")
    assert status.value == "FAIL" and defects == ["exit_timestamp_invalid"]
    status, defects, watch = _integrity("2026-06-08T09:00:00", "garbage", broker_exit_authoritative=True)
    assert status.value == "WATCH" and "broker_exit_timestamp_unavailable" in watch
    status, defects, watch = _integrity("2026-06-08T09:00:00", None, realized_exit=False)
    assert status.value == "WATCH" and watch == ["trade_open_or_exit_missing"]


# --- pre-entry baseline: price from another trading day is unknown, not a favorable/late signal -----------------


def test_pre_entry_move_ignores_a_baseline_from_another_trading_day() -> None:
    rows = {"A": [{"ts": DECISION - 86400 * 3, "close": 50.0}]}
    move, meta = tp.pre_entry_move_pct(symbol="A", decision_epoch=DECISION, entry_price=101.0, minute_rows_by_symbol=rows)
    assert move is None and meta == {"available": False, "reason": "decision_base_row_cross_day"}
    same_day = {"A": [{"ts": DECISION - 60, "close": 100.0}]}
    move, meta = tp.pre_entry_move_pct(symbol="A", decision_epoch=DECISION, entry_price=101.0, minute_rows_by_symbol=same_day)
    assert move == 1.0 and meta["available"] is True and meta["decision_base_price"] == 100.0


def test_pre_entry_move_midnight_boundary_uses_kst_calendar_day() -> None:
    midnight = int(datetime(2026, 6, 9, 0, 0, 5, tzinfo=KST).timestamp())
    before = {"A": [{"ts": midnight - 10, "close": 100.0}]}  # 23:59:55 KST the previous day
    assert tp.pre_entry_move_pct(symbol="A", decision_epoch=midnight, entry_price=101.0, minute_rows_by_symbol=before)[1]["reason"] == "decision_base_row_cross_day"
    after = {"A": [{"ts": midnight - 2, "close": 100.0}]}  # 00:00:03 KST, same day
    assert tp.pre_entry_move_pct(symbol="A", decision_epoch=midnight, entry_price=101.0, minute_rows_by_symbol=after)[0] == 1.0


@pytest.mark.parametrize("symbol,decision,price,rows,reason", [
    ("", DECISION, 101.0, {}, "missing_symbol_time_or_entry_price"),
    ("A", 0, 101.0, {}, "missing_symbol_time_or_entry_price"),
    ("A", DECISION, None, {}, "missing_symbol_time_or_entry_price"),
    ("A", DECISION, 0.0, {}, "missing_symbol_time_or_entry_price"),
    ("A", DECISION, 101.0, {}, "minute_row_before_decision_unavailable"),
    ("A", DECISION, 101.0, {"A": [{"ts": DECISION + 60, "close": 100.0}]}, "minute_row_before_decision_unavailable"),
    ("A", DECISION, 101.0, {"A": [{"ts": DECISION - 60, "close": 0}]}, "decision_base_price_unavailable"),
    ("A", DECISION, 101.0, {"A": [{"ts": DECISION - 60}]}, "decision_base_price_unavailable"),
])
def test_pre_entry_move_unknown_reasons(symbol: str, decision: int, price: Any, rows: Dict[str, Any], reason: str) -> None:
    move, meta = tp.pre_entry_move_pct(symbol=symbol, decision_epoch=decision, entry_price=price, minute_rows_by_symbol=rows)
    assert move is None and meta == {"available": False, "reason": reason}


# --- delays and the separation of actual fill / observed path / shadow anchor ------------------------------------


def test_delay_seconds_negative_is_a_mismatch_not_a_number() -> None:
    assert tp.delay_seconds(1000, 400) == 600 and tp.delay_seconds(1000, 1000) == 0
    assert tp.delay_seconds(1000, 1500) is None and tp.raw_delay(1000, 1500) == -500
    assert tp.delay_seconds(0, 400) is None and tp.delay_seconds(1000, 0) is None


def _model(trade_id: str, *, ts: Any, price: Any = 101.0, decision: str = "D1", **extra: Any) -> Dict[str, Any]:
    return {"trade_id": trade_id, "symbol": "005930", "entry": {"timestamp": ts, "price": price}, "outcome": {"net_return_pct": 0.5},
            "selection": {"q9_decision_id": decision}, "integrity": {"defects": []}, "horizon_contract": {}, **extra}


def _report(tmp_path: Path, models: List[Dict[str, Any]], minute: Dict[str, Any] | None = None, window: Dict[str, Any] | None = None):
    _write(tmp_path / "operator_summary" / "daily" / "2026-06-08" / "q9_decision_windows.json",
           {"windows": [window or {"decision_id": "D1", "decision_epoch": DECISION}]})
    return timing.build_entry_timing_attribution_report(
        day="2026-06-08", models=models, reports_root=tmp_path,
        minute_rows_by_symbol={"005930": [{"ts": DECISION - 60, "close": 100.0}]} if minute is None else minute)


def test_evidence_basis_separates_fill_path_and_shadow_anchor(tmp_path: Path) -> None:
    report = _report(tmp_path, [_model("FILL", ts=DECISION + 300), _model("NOPRICE", ts=DECISION + 300, price=None),
                                _model("NOTIME", ts=""), _model("NOWIN", ts=DECISION + 300, decision="MISSING")])
    rows = {r["trade_id"]: r for r in report["rows"]}
    assert rows["FILL"]["evidence_basis"] == {"actual_entry": "FILLED", "observed_forward_path": "UNAVAILABLE",
                                              "shadow_anchor": "AVAILABLE", "timing_integrity": "OK"}
    assert rows["NOPRICE"]["evidence_basis"]["actual_entry"] == "NO_FILL"
    assert rows["NOPRICE"]["evidence_basis"]["observed_forward_path"] == "NOT_APPLICABLE"
    assert rows["NOTIME"]["evidence_basis"]["actual_entry"] == "NO_FILL" and rows["NOTIME"]["actual_entry_time"] == ""
    assert rows["NOWIN"]["evidence_basis"]["shadow_anchor"] == "UNAVAILABLE"
    for row in rows.values():  # missing evidence never becomes a favorable or classifiable label
        assert row["label"] == "INSUFFICIENT_EVIDENCE"
        assert row["entry_forward_quality"]["forward_available"] is False
        assert row["entry_forward_quality"]["immediate_favorable_move"] is False


def test_evidence_basis_forward_path_states() -> None:
    timing_ok = {"entry_price": 101.0, "entry_epoch": DECISION, "decision_epoch": DECISION}
    four = len(tp.ENTRY_TIMING_HORIZONS)
    assert tp.entry_evidence_basis(timing_ok, {"available": True, "observed_checkpoint_count": four}, [])["observed_forward_path"] == "OBSERVED"
    assert tp.entry_evidence_basis(timing_ok, {"available": True, "observed_checkpoint_count": 1}, [])["observed_forward_path"] == "PARTIAL"
    assert tp.entry_evidence_basis(timing_ok, {"available": True}, [])["observed_forward_path"] == "PARTIAL"
    assert tp.entry_evidence_basis(timing_ok, {"available": False, "observed_checkpoint_count": four}, [])["observed_forward_path"] == "UNAVAILABLE"
    no_fill = tp.entry_evidence_basis({**timing_ok, "entry_price": 0}, {"available": True, "observed_checkpoint_count": four}, [])
    assert no_fill["actual_entry"] == "NO_FILL" and no_fill["observed_forward_path"] == "NOT_APPLICABLE"
    assert tp.entry_evidence_basis(timing_ok, {}, ["scanner_after_entry"])["timing_integrity"] == "MISMATCH:scanner_after_entry"


def test_stage_stamped_after_the_fill_is_unknown_and_excluded_from_the_average(tmp_path: Path) -> None:
    window = {"decision_id": "D1", "decision_epoch": DECISION, "strategist_selection": {"generated_at": DECISION + 60}}
    early = _model("EARLY", ts=DECISION - 120)       # fill before the decision window: mismatched timestamps
    normal = _model("OK", ts=DECISION + 300)
    report = _report(tmp_path, [early, normal], window=window)
    rows = {r["trade_id"]: r for r in report["rows"]}
    assert rows["EARLY"]["scanner_to_entry_delay_sec"] is None and rows["EARLY"]["decision_window_to_entry_delay_sec"] is None
    assert rows["EARLY"]["timing_anomalies"] == ["scanner_after_entry", "strategist_after_entry", "decision_window_after_entry"]
    assert rows["EARLY"]["evidence_basis"]["timing_integrity"].startswith("MISMATCH:")
    assert "timing_anomalies" not in rows["OK"] and rows["OK"]["scanner_to_entry_delay_sec"] == 300
    averages = [r["avg_scanner_to_entry_delay_sec"] for r in report["label_summary"] if r["avg_scanner_to_entry_delay_sec"] is not None]
    assert averages == [300.0]  # the mismatched row's negative delay no longer drags the average


def test_swing_horizon_and_zero_prices_do_not_become_a_timing_judgement(tmp_path: Path) -> None:
    swing = _model("SW", ts=DECISION + 300, horizon_contract={"strategy_horizon": "swing"})
    zero_price = _model("ZP", ts=DECISION + 300, price=0)
    rows = {r["trade_id"]: r for r in _report(tmp_path, [swing, zero_price])["rows"]}
    assert rows["SW"]["label"] == "INSUFFICIENT_EVIDENCE" and rows["SW"]["label_reasons"] == ["strategy_horizon_exceeds_entry_timing_observation_window"]
    assert rows["ZP"]["label"] == "INSUFFICIENT_EVIDENCE" and rows["ZP"]["evidence_basis"]["actual_entry"] == "NO_FILL"
    assert rows["ZP"]["pre_entry_move_pct"] is None


# --- entry vs shadow baseline matching: parity with an independent reference, plus boundaries -------------------


def _shadow(symbol: str, epoch: Any, price: Any = 100.0) -> Dict[str, Any]:
    return {"symbol": symbol, "reason": f"{symbol}@{epoch}", "shadow_forward_base": {"baseline_epoch": epoch, "baseline_price": price}}


def _entry_model(trade_id: str, ts: Any, price: Any = 101.0, symbol: str = "A") -> Dict[str, Any]:
    return {"trade_id": trade_id, "symbol": symbol, "day": "2026-06-08", "entry": {"timestamp": ts, "price": price}}


def _reference_match(models: List[Dict[str, Any]], candidates: List[Dict[str, Any]]) -> Dict[str, str]:
    """Independent brute force: last (in stable epoch order) same-symbol baseline within 0..900s of the fill."""
    out: Dict[str, str] = {}
    def whole(c: Dict[str, Any]) -> int:
        return int(float(c["shadow_forward_base"]["baseline_epoch"] or 0))  # whole seconds, truncated like the original

    ordered = sorted((c for c in candidates if whole(c) > 0 and (c["shadow_forward_base"]["baseline_price"] or 0) > 0), key=whole)
    for model in models:
        epoch = tp.epoch(model["entry"]["timestamp"])
        price = model["entry"]["price"]
        if epoch <= 0 or not price or price <= 0:
            continue
        eligible = [c for c in ordered if c["symbol"] == model["symbol"] and 0 <= epoch - whole(c) <= 900]
        if eligible:
            out[model["trade_id"]] = eligible[-1]["reason"]
    return out


def test_entry_baseline_matching_boundaries_and_numeric_forms() -> None:
    cands = [_shadow("A", DECISION), _shadow("A", f"{DECISION + 5}.0"), _shadow("B", DECISION)]
    models = [_entry_model("EXACT", DECISION + 900), _entry_model("LATE", DECISION + 906), _entry_model("BEFORE", DECISION - 1),
              _entry_model("NUMERIC", float(DECISION + 10)), _entry_model("ISO", "2026-06-08T09:30:30+09:00"),
              _entry_model("NOPRICE", DECISION + 10, price=None), _entry_model("NOTIME", None), _entry_model("OTHER", DECISION + 10, symbol="Z")]
    summary = loss._entry_timing_summary(models, cands)  # string epoch "…​.0" used to raise ValueError
    matched = {row["trade_id"]: row["candidate_reason"] for row in summary["examples"]}
    assert matched == _reference_match(models, cands)
    assert matched["EXACT"] == f"A@{DECISION + 5}.0" and matched["NUMERIC"] == f"A@{DECISION + 5}.0"
    assert "LATE" not in matched and "BEFORE" not in matched and "NOPRICE" not in matched and "NOTIME" not in matched
    assert summary["matched_trade_count"] == len(matched)


def test_entry_baseline_epoch_is_truncated_to_whole_seconds_like_the_original() -> None:
    fill = DECISION + 900
    cands = [_shadow("A", DECISION + 0.9, 100.0)]          # truncates to DECISION: exactly 900 s before the fill, eligible
    assert loss._entry_timing_summary([_entry_model("X", fill)], cands)["matched_trade_count"] == 1
    assert loss._entry_timing_summary([_entry_model("X", fill + 1)], cands)["matched_trade_count"] == 0  # 901 s
    assert loss._entry_timing_summary([_entry_model("X", DECISION)], [_shadow("A", DECISION + 0.9)])["matched_trade_count"] == 1
    assert loss._entry_timing_summary([_entry_model("X", DECISION - 1)], [_shadow("A", DECISION + 0.9)])["matched_trade_count"] == 0
    assert loss._entry_timing_summary([_entry_model("X", 100)], [_shadow("A", 100.9)])["matched_trade_count"] == 1
    assert loss._entry_timing_summary([_entry_model("X", 100)], [_shadow("A", 0.9)])["matched_trade_count"] == 0  # truncates to 0: no baseline
    # two baselines that truncate to the same second keep the later one in input order
    pair = [_shadow("A", DECISION + 0.2, 100.0), _shadow("A", DECISION + 0.8, 100.0)]
    example = loss._entry_timing_summary([_entry_model("X", DECISION + 5)], pair)["examples"][0]
    assert example["candidate_reason"] == f"A@{DECISION + 0.8}"
    assert example["candidate_reason"] == _reference_match([_entry_model("X", DECISION + 5)], pair)["X"]


def test_entry_baseline_matching_equals_reference_on_random_data() -> None:
    rng = random.Random(1010)
    symbols = ["A", "B", "C"]
    cands = [_shadow(rng.choice(symbols), DECISION + rng.randrange(0, 4000, 7) + rng.choice([0, 0.25, 0.5, 0.99]), rng.choice([100.0, 50.5, 0, None])) for _ in range(300)]
    cands += [_shadow("A", DECISION + 100), _shadow("A", DECISION + 100)]  # equal epochs: the later duplicate wins
    models = [_entry_model(f"T{i}", DECISION + rng.randrange(-300, 4500), rng.choice([101.0, 99.5, 0, None]), rng.choice(symbols)) for i in range(400)]
    summary = loss._entry_timing_summary(models, cands)
    matched = {row["trade_id"]: row["candidate_reason"] for row in loss._entry_timing_summary(models, cands)["examples"]}
    expected = _reference_match(models, cands)
    assert summary["matched_trade_count"] == len(expected)
    assert {k: v for k, v in matched.items()} == {k: expected[k] for k in list(expected)[:20]}


# --- exit: a post-exit price path is not an exit ----------------------------------------------------------------


def _exit_model(trade_id: str, *, post: Dict[str, Any] | None, evidence_class: Any = "REALIZED", ret: Any = -0.5) -> Dict[str, Any]:
    model: Dict[str, Any] = {"trade_id": trade_id, "symbol": "005930", "day": "2026-06-08", "outcome": {"net_return_pct": ret},
                             "monitor": {"post_exit": {"checkpoints": post}} if post is not None else {}}
    if evidence_class is not None:
        model["evidence_class"] = evidence_class
    return model


def _post(value: Any) -> Dict[str, Any]:
    return {"+5m": {"status": "observed", "return_pct": value}}


def test_unrealized_trade_price_path_is_not_counted_as_an_exit() -> None:
    models = [_exit_model("REAL", post=_post(0.01)), _exit_model("OPEN", post=_post(0.02), evidence_class="UNAVAILABLE", ret=None)]
    summary = loss._exit_hold_summary(models)
    assert summary["observed_trade_count"] == 1 and summary["unrealized_exit_excluded_count"] == 1
    assert [e["trade_id"] for e in summary["examples"]] == ["REAL"]
    assert summary["by_hold_offset"][0]["count"] == 1


def test_exit_hold_summary_is_unchanged_when_every_trade_is_realized_or_unlabeled() -> None:
    models = [_exit_model("A", post=_post(0.01)), _exit_model("B", post=_post(0.0), ret=0), _exit_model("C", post=_post(-0.01), evidence_class=None),
              _exit_model("D", post=None)]
    summary = loss._exit_hold_summary(models)
    assert "unrealized_exit_excluded_count" not in summary
    assert summary["observed_trade_count"] == 3  # a 0.0 post-exit return and a flat 0 realized return are real observations
    row = summary["by_hold_offset"][0]
    assert (row["count"], row["improved_count"], row["worsened_count"]) == (3, 1, 1)
    assert loss._exit_hold_summary([])["observed_trade_count"] == 0


def test_zero_and_false_are_values_not_missing_in_the_exit_readout() -> None:
    summary = loss._exit_hold_summary([_exit_model("Z", post=_post(0), ret=0)])
    assert summary["observed_trade_count"] == 1
    assert summary["examples"][0]["realized_net_return_pct"] == 0.0 and summary["examples"][0]["hold_improvement_pct"] == {"+5m": 0.0}
    status = _exit_model("PEND", post={"+5m": {"status": "pending", "return_pct": 0.5}})
    assert loss._exit_hold_summary([status])["observed_trade_count"] == 0  # pending is not observed even with a number


# --- hot path: one conversion per row, identical output ----------------------------------------------------------


def _candidate(i: int, day: int, symbol: str) -> Dict[str, Any]:
    ret = ((i * 37) % 11 - 4) * 0.4
    return {"symbol": symbol, "generated_at": f"2026-06-0{day}T09:30:00+09:00", "quant_tactic_id": ["t1", "t2"][i % 2],
            "entry_lane_observation": {"time_bucket": ["open", "mid"][i % 2], "primary_lane": "l", "market_regime_rail": "r"},
            "shadow_forward_outcome": {"checkpoints": {h: {"status": "observed", "return_pct": ret} for h in ("+5m", "+15m", "+30m", "+60m")}}}


def test_combo_rows_converts_each_row_once_and_keeps_output(monkeypatch: pytest.MonkeyPatch) -> None:
    candidates = [_candidate(i, 1 + i % 5, f"S{i % 9}") for i in range(300)]
    calls = {"day": 0}
    real_day = horizon.candidate_day

    def counting_day(row: Any) -> str:
        calls["day"] += 1
        return real_day(row)

    monkeypatch.setattr(horizon, "candidate_day", counting_day)
    shared = horizon._row_facts(candidates)
    assert calls["day"] == len(candidates)
    calls["day"] = 0
    a = horizon._combo_rows(candidates, dimensions=("time_bucket", "tactic"), cost_pct=0.2)
    assert calls["day"] == len(candidates)  # was twice per observation per horizon
    calls["day"] = 0
    b = horizon._combo_rows(candidates, dimensions=("time_bucket", "tactic"), cost_pct=0.2, facts=shared)
    assert calls["day"] == 0 and a == b
    assert any(row["decision"] == "CONTROLLED_ADOPTION_CANDIDATE" for row in a) or all(row["observed_count"] > 0 for row in a)


def test_horizon_review_shares_one_conversion_across_all_three_combinations(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    candidates = [_candidate(i, 1 + i % 5, f"S{i % 9}") for i in range(120)]
    monkeypatch.setattr(horizon, "load_quant_shadow_candidate_payloads_for_range", lambda **_: [])
    monkeypatch.setattr(horizon, "_candidate_rows", lambda payloads: candidates)
    monkeypatch.setattr(horizon, "load_broker_cost_profile", lambda *_: {"conservative_round_trip_cost_pct": 0.002})
    calls = {"day": 0}
    real_day = horizon.candidate_day
    monkeypatch.setattr(horizon, "candidate_day", lambda row: (calls.__setitem__("day", calls["day"] + 1), real_day(row))[1])
    review = horizon.build_horizon_alignment_review(reports_root=tmp_path, start="2026-06-01", end="2026-06-05")
    assert calls["day"] == len(candidates)  # one per row for the whole review, not per combination
    assert review["candidate_count"] == 120 and {"time_tactic", "time_lane", "time_tactic_market_rail"} <= set(review)


def test_a10_owner_stays_pure() -> None:
    source = Path(tp.__file__).read_text(encoding="utf-8")
    imports = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
    assert all(line.split()[1] in {"__future__", "bisect", "collections", "datetime", "typing", ".contracts", ".metrics"} for line in imports), imports
    for banned in ("open(", "write_text", "read_text", "read_json", "os.environ", "subprocess", ".now("):
        assert banned not in source, banned
