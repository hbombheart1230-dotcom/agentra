"""FAST11 A11 tests: Q13 evidence-quality aggregation, evidence-separating Markdown, exclusion consistency, hot paths."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Dict, List

import pytest

from libs.reporting.evaluation import entry_timing_attribution as timing
from libs.reporting.evaluation import fast07_chain_render_projection as render
from libs.reporting.evaluation import fast07_trade_projection as tp
from libs.reporting.evaluation import loss_decomposition as loss
from tests.test_p15_fast10_a_exit_horizon_smoke import DECISION, _exit_model, _model, _report

DIMENSIONS = ("actual_entry", "observed_forward_path", "shadow_anchor")


def _row(label: str = "INSUFFICIENT_EVIDENCE", basis: Any = "default", **extra: Any) -> Dict[str, Any]:
    row: Dict[str, Any] = {"label": label, "entry_return_pct": 0.5}
    if basis == "default":
        basis = {"actual_entry": "FILLED", "observed_forward_path": "OBSERVED", "shadow_anchor": "AVAILABLE", "timing_integrity": "OK"}
    if basis is not None:
        row["evidence_basis"] = basis
    row.update(extra)
    return row


# --- aggregation: every category is a partition of the analyzed rows ---------------------------------------------


def test_entry_report_aggregates_each_evidence_kind_separately(tmp_path: Path) -> None:
    window = {"decision_id": "D1", "decision_epoch": DECISION, "strategist_selection": {"generated_at": DECISION + 60}}
    models = [_model("FILL", ts=DECISION + 300), _model("EARLY", ts=DECISION - 120), _model("NOPRICE", ts=DECISION + 300, price=None),
              _model("NOTIME", ts=""), _model("NOWIN", ts=DECISION + 300, decision="MISSING"),
              _model("DEFECT", ts=DECISION + 300, integrity={"defects": ["confirmed_runtime_defect"]}),
              _model("DUP", ts=DECISION + 300, integrity={"defects": ["broker_day_partial_exit_duplicate"]})]
    report = _report(tmp_path, models, window=window)
    quality = report["evidence_quality"]
    assert report["trade_count"] == 5 and report["excluded_trade_count"] == 2
    assert quality["reconciliation"] == {"model_count": 7, "analyzed_count": 5, "excluded_count": 2, "reconciled": True}
    assert quality["actual_entry"] == {"FILLED": 3, "NO_FILL": 2, "UNKNOWN": 0}
    # EARLY has one minute row after its fill, so its forward path is genuinely partial; FILL/NOWIN have none after the fill.
    assert quality["observed_forward_path"] == {"OBSERVED": 0, "PARTIAL": 1, "UNAVAILABLE": 2, "NOT_APPLICABLE": 2, "UNKNOWN": 0}
    assert quality["shadow_anchor"] == {"AVAILABLE": 4, "UNAVAILABLE": 1, "UNKNOWN": 0}
    assert quality["timing_integrity"] == {"OK": 4, "MISMATCH": 1, "UNKNOWN": 0}
    assert quality["rows_with_timing_anomalies"] == 1
    assert quality["timing_anomaly_codes"] == {"decision_window_after_entry": 1, "scanner_after_entry": 1, "strategist_after_entry": 1}
    assert quality["insufficient_evidence_count"] == 5  # no minute rows were offered: nothing is classifiable
    assert quality["shadow_only_count"] == 2  # NOPRICE and NOTIME have a decision anchor but no actual fill
    assert quality["evidence_classes"]["NO_ACTUAL_FILL"] == 2 and quality["evidence_classes"]["ACTUAL_FILL_NO_OBSERVED_PATH"] == 2
    assert quality["evidence_classes"]["ACTUAL_FILL_PARTIAL_PATH"] == 1
    assert sum(quality["evidence_classes"].values()) == 5
    assert quality["actual_return_observed_count"] == 3 and quality["actual_return_missing_on_fill_count"] == 0


def test_every_dimension_partitions_the_rows_on_random_input() -> None:
    rng = random.Random(11)
    pick = lambda options: rng.choice(options)
    rows = []
    for _ in range(400):
        basis: Any = {
            "actual_entry": pick(["FILLED", "NO_FILL", "weird", None, 3]),
            "observed_forward_path": pick(["OBSERVED", "PARTIAL", "UNAVAILABLE", "NOT_APPLICABLE", "?", None]),
            "shadow_anchor": pick(["AVAILABLE", "UNAVAILABLE", "x", None]),
            "timing_integrity": pick(["OK", "MISMATCH:scanner_after_entry", "MISMATCH:", "bad", None, 7]),
        }
        basis = pick([basis, basis, None, "garbage", [], 5])
        rows.append(_row(label=pick(["INSUFFICIENT_EVIDENCE", "ENTRY_APPROPRIATE"]), basis=basis,
                         timing_anomalies=pick([["a"], ["a", "b"], [], None, "oops", 3]), entry_return_pct=pick([None, 0, 0.3])))
    quality = tp.entry_evidence_quality(rows, model_count=len(rows) + 5, excluded_count=5)
    for name in DIMENSIONS:
        assert sum(quality[name].values()) == len(rows), name
    assert sum(quality["timing_integrity"].values()) == len(rows)
    assert sum(quality["evidence_classes"].values()) == len(rows)
    assert quality["reconciliation"]["reconciled"] is True
    assert quality["insufficient_evidence_count"] == sum(1 for r in rows if r["label"] == "INSUFFICIENT_EVIDENCE")
    assert quality["rows_with_timing_anomalies"] == sum(1 for r in rows if isinstance(r["timing_anomalies"], list) and r["timing_anomalies"])


@pytest.mark.parametrize("model_count,excluded,expected", [(10, 2, True), (11, 2, False), (9, 2, False), (8, 0, True), (7, 0, False)])
def test_reconciliation_fails_when_analyzed_plus_excluded_is_not_the_offered_total(model_count: int, excluded: int, expected: bool) -> None:
    quality = tp.entry_evidence_quality([_row() for _ in range(8)], model_count=model_count, excluded_count=excluded)
    assert quality["reconciliation"]["reconciled"] is expected


def test_legacy_and_malformed_rows_are_unknown_never_filled() -> None:
    quality = tp.entry_evidence_quality([_row(basis=None), _row(basis="garbage"), _row(basis={"actual_entry": "FILLED"})],
                                        model_count=3, excluded_count=0)
    assert quality["evidence_classes"]["LEGACY_NO_EVIDENCE_BASIS"] == 2 and quality["evidence_classes"]["UNCLASSIFIED"] == 1
    assert quality["actual_entry"] == {"FILLED": 1, "NO_FILL": 0, "UNKNOWN": 2}
    assert quality["timing_integrity"]["UNKNOWN"] == 3 and quality["shadow_anchor"]["UNKNOWN"] == 3
    assert quality["actual_return_observed_count"] == 1  # only the one row that claims a fill
    empty = tp.entry_evidence_quality([], model_count=0, excluded_count=0)
    assert empty["reconciliation"]["reconciled"] is True and sum(empty["evidence_classes"].values()) == 0


def test_fill_without_a_realized_return_is_counted_apart_from_a_fill_with_one() -> None:
    quality = tp.entry_evidence_quality([_row(entry_return_pct=None), _row(entry_return_pct=0), _row(entry_return_pct=-0.2)],
                                        model_count=3, excluded_count=0)
    assert quality["actual_return_observed_count"] == 2 and quality["actual_return_missing_on_fill_count"] == 1  # 0 is a value


# --- Markdown: actual results, observed path and shadow anchors are labeled apart -----------------------------------


def test_markdown_separates_actual_result_from_virtual_observation(tmp_path: Path) -> None:
    window = {"decision_id": "D1", "decision_epoch": DECISION, "strategist_selection": {"generated_at": DECISION + 60}}
    report = _report(tmp_path, [_model("FILL", ts=DECISION + 300), _model("EARLY", ts=DECISION - 120), _model("NOPRICE", ts=DECISION + 300, price=None)], window=window)
    md = timing.render_entry_timing_attribution_report(report)
    assert "## Evidence Quality" in md
    assert "Models offered: 3 = analyzed 3 + excluded 0 (reconciled: **yes**)" in md
    assert "+5m Return (observed path)" in md and "Realized (actual)" in md
    assert "fill=FILLED / path=UNAVAILABLE / shadow-anchor=AVAILABLE / timing=OK" in md
    assert "fill=NO_FILL / path=NOT_APPLICABLE" in md
    assert "timing=MISMATCH:scanner_after_entry,strategist_after_entry,decision_window_after_entry" in md
    assert "Timing mismatches (1 rows): decision_window_after_entry=1, scanner_after_entry=1, strategist_after_entry=1" in md
    assert "Shadow-only rows (decision anchor but no actual fill): 1" in md
    assert md.index("## Evidence Quality") < md.index("## Trade Rows")


def test_markdown_flags_an_unreconciled_total() -> None:
    quality = tp.entry_evidence_quality([_row()], model_count=9, excluded_count=1)
    md = render.render_entry_timing_attribution_report({"day": "d", "rows": [_row(trade_id="T")], "evidence_quality": quality})
    assert "(reconciled: **NO**)" in md


def _legacy_payload() -> Dict[str, Any]:
    return {"day": "2026-06-08", "behavior_effect": "observation_only", "trade_count": 1, "limitations": ["L"],
            "label_summary": [{"label": "ENTRY_APPROPRIATE", "trade_count": 1, "performance": {"win_rate": 1.0, "average_return_pct": 0.5},
                               "avg_scanner_to_entry_delay_sec": 10.0, "avg_5m_mfe_pct": 0.6, "avg_5m_mae_pct": -0.1}],
            "rows": [{"trade_id": "T1", "symbol": "A", "label": "ENTRY_APPROPRIATE", "scanner_to_entry_delay_sec": 10, "pre_entry_move_pct": 0.1,
                      "entry_forward_quality": {"+5m_return_pct": 0.2, "+5m_mfe_pct": 0.6, "+5m_mae_pct": -0.1}, "entry_return_pct": 0.5,
                      "label_reasons": ["favorable_forward_response"]}]}


def test_payload_without_new_fields_renders_with_the_original_layout() -> None:
    md = render.render_entry_timing_attribution_report(_legacy_payload())
    assert "## Evidence Quality" not in md and "(observed path)" not in md and "Evidence |" not in md
    assert ("| Trade | Symbol | Label | Delay Sec | Pre-entry Move | +5m Return | +5m MFE | +5m MAE | Realized | Reasons |\n"
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |") in md
    assert "| T1 | A | ENTRY_APPROPRIATE | 10.0000 | 0.1000% | 0.2000% | 0.6000% | -0.1000% | 0.5000% | favorable_forward_response |" in md
    assert render.render_entry_timing_attribution_report({}).startswith("# Q13 Entry Timing Attribution - ")


def test_mixed_legacy_and_new_rows_render_without_error() -> None:
    payload = _legacy_payload()
    payload["rows"].append({**payload["rows"][0], "trade_id": "T2", "evidence_basis": {"actual_entry": "FILLED", "observed_forward_path": "OBSERVED",
                                                                                      "shadow_anchor": "AVAILABLE", "timing_integrity": "OK|bad"}})
    md = render.render_entry_timing_attribution_report(payload)
    assert "legacy (no evidence basis)" in md and "fill=FILLED / path=OBSERVED" in md
    assert "OK/bad" in md and "OK|bad" not in md  # a pipe in a value cannot break the table


# --- loss decomposition: only independent, really-exited trades are aggregated -------------------------------------


def _loss_models() -> List[Dict[str, Any]]:
    def model(trade_id: str, defects: List[str], ret: float, **extra: Any) -> Dict[str, Any]:
        m = _exit_model(trade_id, post={"+5m": {"status": "observed", "return_pct": 0.01}}, ret=ret)
        m.update({"integrity": {"defects": defects}, "selection": {"selected_rank": 1}, "entry": {"timestamp": DECISION, "price": 100.0}, **extra})
        return m
    return [model("OK", [], -1.0), model("DUP", ["broker_day_partial_exit_duplicate"], -1.0), model("BAD", ["confirmed_runtime_defect"], -3.0)]


def _build_loss(monkeypatch: pytest.MonkeyPatch, models: List[Dict[str, Any]], tmp_path: Path) -> Dict[str, Any]:
    monkeypatch.setattr(loss, "_load_trade_models", lambda *a: models)
    monkeypatch.setattr(loss, "load_quant_shadow_candidate_payloads_for_range", lambda **k: [])
    monkeypatch.setattr(loss, "build_quant_shadow_candidate_evaluation", lambda p: {})
    monkeypatch.setattr(loss, "attach_forward_outcomes", lambda rows: rows)
    monkeypatch.setattr(loss, "dedupe_q8_candidates", lambda rows: rows)
    return loss.build_loss_decomposition(reports_root=tmp_path, start="2026-06-08", end="2026-06-08")


def test_loss_decomposition_excludes_split_sell_children_and_runtime_defects(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    payload = _build_loss(monkeypatch, _loss_models(), tmp_path)
    assert payload["realized_system"]["comparable_trade_count"] == 1
    assert payload["realized_system"]["performance"]["average_return_pct"] == -1.0  # the -3.0 defect trade is not averaged in
    assert payload["monitor_exit"]["observed_trade_count"] == 1
    assert payload["evidence"]["trade_model_count"] == 1
    assert payload["evidence"]["excluded_trade_model_count"] == 2 and payload["evidence"]["total_trade_model_count"] == 3
    assert payload["evidence"]["trade_model_count"] + payload["evidence"]["excluded_trade_model_count"] == payload["evidence"]["total_trade_model_count"]
    md = loss.render_loss_decomposition(payload)
    assert "- excluded trade models (split-sell child / confirmed runtime defect): 2 of 3" in md


def test_loss_decomposition_output_is_unchanged_when_nothing_is_excluded(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    payload = _build_loss(monkeypatch, _loss_models()[:1], tmp_path)
    assert "excluded_trade_model_count" not in payload["evidence"] and "total_trade_model_count" not in payload["evidence"]
    assert "excluded trade models" not in loss.render_loss_decomposition(payload)
    empty = _build_loss(monkeypatch, [], tmp_path)
    assert empty["evidence"]["trade_model_count"] == 0 and "excluded_trade_model_count" not in empty["evidence"]


def test_exit_summary_keeps_realized_and_virtual_observations_apart(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    models = _loss_models()[:1] + [_exit_model("OPEN", post={"+5m": {"status": "observed", "return_pct": 0.02}}, evidence_class="UNAVAILABLE", ret=None)]
    for m in models:
        m.setdefault("integrity", {"defects": []}); m.setdefault("selection", {}); m.setdefault("entry", {})
    payload = _build_loss(monkeypatch, models, tmp_path)
    assert payload["monitor_exit"]["observed_trade_count"] == 1 and payload["monitor_exit"]["unrealized_exit_excluded_count"] == 1
    md = loss.render_loss_decomposition(payload)
    assert "Post-exit price observations are virtual (not a realized result); trades without a realized exit are not counted: 1" in md


# --- hot paths: index and batch return what the linear/single calls return ------------------------------------------


def _linear_reference(rows: List[Dict[str, Any]], epoch: int) -> Any:
    """Independent reference: the last row, in list order, whose whole-second ts is at or before the epoch."""
    found = None
    for row in rows:
        try:
            stamp = int(float(row.get("ts") or 0))
        except (TypeError, ValueError):
            continue
        if stamp <= epoch:
            found = row
    return found


@pytest.mark.parametrize("kind", ["sorted", "unsorted", "duplicates", "malformed", "empty", "single"])
def test_minute_index_matches_the_linear_scan(kind: str) -> None:
    rng = random.Random(hash(kind) % 1000)
    stamps = sorted(rng.randrange(1000, 5000) for _ in range(60))
    rows: List[Dict[str, Any]] = [{"ts": s, "close": float(i)} for i, s in enumerate(stamps)]
    if kind == "unsorted":
        rng.shuffle(rows)
    elif kind == "duplicates":
        rows = [{"ts": 2000 + (i // 4), "close": float(i)} for i in range(40)]
    elif kind == "malformed":
        rows[10]["ts"] = "abc"; rows[20]["ts"] = None; rows[30]["ts"] = "1500.9"
    elif kind == "empty":
        rows = []
    elif kind == "single":
        rows = rows[:1]
    index = tp.MinuteIndex({"A": rows})
    for epoch in [0, 999, 1000, 1500, 2000, 2001, 2010, 3333, 4999, 5000, 9999] + [rng.randrange(900, 5200) for _ in range(40)]:
        expected = _linear_reference(rows, epoch)
        assert index.at_or_before("A", epoch) is expected, (kind, epoch)
        assert tp.row_at_or_before(rows, epoch) is expected
    assert index.at_or_before("MISSING", 3000) is None


def test_pre_entry_move_with_index_equals_without() -> None:
    rows = {"A": [{"ts": DECISION - 600 + 60 * i, "close": 100.0 + i} for i in range(20)]}
    index = tp.MinuteIndex(rows)
    for decision in (DECISION - 900, DECISION - 300, DECISION, DECISION + 500):
        for price in (101.0, None, 0):
            with_index = tp.pre_entry_move_pct(symbol="A", decision_epoch=decision, entry_price=price, minute_rows_by_symbol=rows, index=index)
            assert with_index == tp.pre_entry_move_pct(symbol="A", decision_epoch=decision, entry_price=price, minute_rows_by_symbol=rows)


def _minutes(symbol_index: int) -> List[Dict[str, Any]]:
    return [{"ts": DECISION - 3600 + 60 * m, "raw_ts": None, "close": 100.0 + ((m * 7 + symbol_index) % 11) * 0.1, "high": 101.0, "low": 99.0}
            for m in range(0, 200)]


def test_batched_forward_readouts_equal_single_fill_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    rng = random.Random(77)
    minute = {f"S{i}": _minutes(i) for i in range(6)}
    specs = []
    for n in range(80):
        symbol = rng.choice([f"S{i}" for i in range(6)] + ["NOROWS", "", " S1"])
        specs.append((f"T{n}", symbol, DECISION + rng.randrange(-2000, 5000) if n % 13 else 0, rng.choice([100.2, 101.0, None, 0])))
    batched = timing._entry_forwards(specs, minute)
    single = [timing._entry_forward(trade_id=t, symbol=s, entry_epoch=e, entry_price=p, minute_rows_by_symbol=minute) for t, s, e, p in specs]
    assert batched == single
    calls: List[int] = []
    real = timing.attach_forward_outcomes
    monkeypatch.setattr(timing, "attach_forward_outcomes", lambda rows, **kw: (calls.append(len(rows)), real(rows, **kw))[1])
    timing._entry_forwards([s for s in specs if s[1] in minute and s[2] > 0 and s[3]], minute)
    assert len(calls) == 1 and calls[0] > 10  # one call shared by every fill that has minute rows


def test_fills_without_minute_rows_never_borrow_other_fills_as_a_price_series() -> None:
    specs = [("A1", "NOROWS", DECISION, 100.0), ("A2", "NOROWS", DECISION + 120, 101.0), ("A3", "NOROWS", DECISION + 240, 102.0)]
    forwards = timing._entry_forwards(specs, {"OTHER": _minutes(0)})
    assert all(f["available"] is False and f["reason"] == "minute_rows_unavailable" for f in forwards)


def test_full_report_is_identical_for_batched_and_single_forward(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    minute = {"005930": _minutes(1)}
    models = [_model(f"T{i}", ts=DECISION + 60 * i) for i in range(12)]
    batched = _report(tmp_path, models, minute=minute)
    monkeypatch.setattr(timing, "_entry_forwards", lambda specs, rows: [timing._entry_forward(trade_id=t, symbol=s, entry_epoch=e, entry_price=p, minute_rows_by_symbol=rows) for t, s, e, p in specs])
    single = _report(tmp_path, models, minute=minute)
    assert batched == single
    assert any(r["entry_forward_quality"]["forward_available"] for r in batched["rows"])


def test_a11_owner_stays_pure() -> None:
    source = Path(tp.__file__).read_text(encoding="utf-8")
    imports = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
    assert all(line.split()[1] in {"__future__", "bisect", "collections", "datetime", "typing", ".contracts", ".metrics"} for line in imports), imports
    for banned in ("open(", "write_text", "read_text", "read_json", "os.environ", "subprocess", ".now("):
        assert banned not in source, banned
