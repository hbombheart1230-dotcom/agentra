"""Closeout memory fix (P1.3): streaming / per-symbol loaders must be output-equivalent.

The 10-06/10-07 closeouts were OOM-killed at the 1 GiB container cap. These tests pin that the
memory-bounded rewrites of the closeout-path loaders return exactly what the loaders they replace
returned (the real-data byte-for-byte comparison is recorded in the patch note).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import libs.reporting.json_array_stream as jas
import libs.reporting.quant_shadow_candidate_evaluation as qsce
import libs.research.rank1_feature_mart.loaders as loaders
from libs.reporting.evaluation import artifact_inventory as inventory


# --------------------------------------------------------------------- streaming JSON array


def _windows_doc(count: int, *, pad: int = 0) -> dict:
    return {
        "schema_version": "q9_decision_windows.v1",
        "day": "2026-10-01",
        "windows": [{"decision_id": f"D{i}", "run_id": f"r{i}", "blob": "x" * pad, "n": i} for i in range(count)],
        "window_count": count,
        "recovery": {"windows": "not the array"},
    }


def _write(path: Path, doc: dict, *, indent=2) -> Path:
    path.write_text(json.dumps(doc, indent=indent, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.mark.parametrize("chunk", [64, 1000, 10_000_000])
def test_iter_json_array_matches_json_loads_across_chunk_sizes(tmp_path, monkeypatch, chunk):
    monkeypatch.setattr(jas, "_STREAM_CHUNK_CHARS", chunk)
    doc = _windows_doc(40, pad=300)
    doc["windows"][3]["blob"] = "한글 ✓ " * 50  # non-ASCII, multi-byte
    path = _write(tmp_path / "w.json", doc)
    assert list(loaders.iter_json_array(path, "windows")) == doc["windows"]


def test_iter_json_array_falls_back_for_other_layouts(tmp_path):
    doc = _windows_doc(5)
    compact = _write(tmp_path / "compact.json", doc, indent=None)
    assert list(loaders.iter_json_array(compact, "windows")) == doc["windows"]
    assert list(loaders.iter_json_array(tmp_path / "missing.json", "windows")) == []
    (tmp_path / "bad.json").write_text("{not json", encoding="utf-8")
    assert list(loaders.iter_json_array(tmp_path / "bad.json", "windows")) == []


def test_iter_json_array_empty_array_and_absent_key(tmp_path):
    assert list(loaders.iter_json_array(_write(tmp_path / "e.json", {"windows": []}), "windows")) == []
    assert list(loaders.iter_json_array(_write(tmp_path / "n.json", {"other": [1]}), "windows")) == []


def test_iter_json_array_truncated_file_raises_value_error(tmp_path):
    text = json.dumps(_windows_doc(10, pad=200), indent=2)
    path = tmp_path / "t.json"
    path.write_text(text[: len(text) // 2], encoding="utf-8")
    with pytest.raises(ValueError):
        list(loaders.iter_json_array(path, "windows"))


# --------------------------------------------------------------------- q9_windows loader


def _canonical(root: Path, day: str, run_id: str, strategist, scanner) -> None:
    folder = root / "canonical" / day / run_id
    folder.mkdir(parents=True, exist_ok=True)
    if strategist is not None:
        (folder / "strategist.json").write_text(json.dumps(strategist), encoding="utf-8")
    if scanner is not None:
        (folder / "scanner.json").write_text(json.dumps(scanner), encoding="utf-8")


def _reference_q9_windows(reports_root: Path, episodes) -> dict:
    """The pre-fix implementation, verbatim (whole-file json + full retention)."""
    wanted: dict[str, set[str]] = {}
    for row in episodes:
        day = str(row.get("day") or "")
        decision_id = str(row.get("decision_id") or "")
        if day and decision_id:
            wanted.setdefault(day, set()).add(decision_id)
    found = {}
    for day, decision_ids in sorted(wanted.items()):
        payload = loaders.read_json(reports_root / "operator_summary" / "daily" / day / "q9_decision_windows.json")
        for row in (payload.get("windows") or []) if isinstance(payload, dict) else []:
            if not isinstance(row, dict):
                continue
            decision_id = str(row.get("decision_id") or "")
            if decision_id in decision_ids:
                enriched = dict(row)
                run_id = str(row.get("run_id") or "")
                root = reports_root / "canonical" / day / run_id
                enriched["_canonical_strategist"] = loaders.read_json(root / "strategist.json")
                enriched["_canonical_scanner"] = loaders.read_json(root / "scanner.json")
                found[decision_id] = enriched
    return found


FIELDS_READ_BY_BUILDER = ("strategist_selection", "commander_final", "_canonical_strategist")


def test_q9_windows_projection_preserves_everything_the_builder_reads(tmp_path):
    reports = tmp_path / "reports"
    day = "2026-10-01"
    windows = []
    for i in range(6):
        windows.append(
            {
                "decision_id": f"D{i}",
                "run_id": f"r{i}",
                "strategist_selection": {"selected_symbol": "005930", "scenario": "s"},
                "commander_final": {"decision": "BUY", "reason": "x"},
                "scanner_pre_strategist_universe": {
                    "intrinsic_ranked_top20": [{"symbol": "005930", "rank": 1}],
                    "huge": ["y" * 100] * 50,
                },
                "unused_big_block": ["z" * 500] * 40,
            }
        )
        _canonical(
            reports, day, f"r{i}",
            {"playbook": "p", "strategy_scores": {"a": 1}} if i != 2 else None,
            {"candidate_ranking_table": {"rows": [{"symbol": "005930", "score": i}]}, "noise": ["n" * 400] * 30} if i != 3 else {"other": 1},
        )
    path = reports / "operator_summary" / "daily" / day / "q9_decision_windows.json"
    path.parent.mkdir(parents=True)
    _write(path, {"windows": windows})
    episodes = [{"day": day, "decision_id": f"D{i}"} for i in (0, 2, 3, 5)] + [{"day": day, "decision_id": "NOPE"}]

    got = loaders.q9_windows(reports, episodes)
    ref = _reference_q9_windows(reports, episodes)
    assert set(got) == set(ref) == {"D0", "D2", "D3", "D5"}
    for decision_id, window in got.items():
        full = ref[decision_id]
        # every field build_episode/intrinsic_candidate/canonical_scanner_candidate reads is identical
        for key in FIELDS_READ_BY_BUILDER:
            assert window.get(key) == full.get(key), (decision_id, key)
        for symbol in ("005930", "000660"):
            assert loaders.intrinsic_candidate(window, symbol) == loaders.intrinsic_candidate(full, symbol)
            assert loaders.canonical_scanner_candidate(window, symbol) == loaders.canonical_scanner_candidate(full, symbol)
        assert bool(window) == bool(full)
        assert bool(window.get("_canonical_scanner")) == bool(full.get("_canonical_scanner"))
        assert bool(window.get("_canonical_strategist")) == bool(full.get("_canonical_strategist"))
        assert "unused_big_block" not in window  # the point: unused bulk is not retained


def test_q9_windows_corrupt_file_yields_no_windows_for_that_day(tmp_path):
    reports = tmp_path / "reports"
    path = reports / "operator_summary" / "daily" / "2026-10-01" / "q9_decision_windows.json"
    path.parent.mkdir(parents=True)
    text = json.dumps(_windows_doc(10, pad=100), indent=2)
    path.write_text(text[: len(text) // 2], encoding="utf-8")
    assert loaders.q9_windows(reports, [{"day": "2026-10-01", "decision_id": "D1"}]) == {}


# --------------------------------------------------------------------- per-symbol source rows


def _write_cache(root: Path, symbol: str, rows) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{symbol}.json").write_text(json.dumps({"rows": rows}), encoding="utf-8")


def _minute(ts: int, close: float, day="20261001") -> dict:
    return {"ts": ts, "close": close, "open": close, "high": close, "low": close, "volume": 10, "raw_ts": f"{day}09{ts % 60:02d}00"}


def test_source_rows_wrapper_equals_per_symbol_composition(tmp_path):
    minute_root, extra_root, daily_root = tmp_path / "m", tmp_path / "m2", tmp_path / "d"
    for symbol, base in (("005930", 100), ("000660", 200)):
        _write_cache(minute_root, symbol, [_minute(1790000000 + k * 60, base + k) for k in range(5)])
        _write_cache(extra_root, symbol, [_minute(1790000120 + k * 60, base + 50 + k) for k in range(3)])  # overlaps epochs
        _write_cache(daily_root, symbol, [{"day": "2026-09-30", "close": base - 1, "ts": 1789000000}])
    symbols = {"005930", "000660", "999999"}  # last one has no cache files at all
    minutes, daily = loaders.source_rows(
        minute_cache_root=minute_root, daily_cache_root=daily_root, symbols=symbols, additional_minute_cache_roots=(extra_root,)
    )
    assert set(minutes) == set(daily) == symbols
    for symbol in symbols:
        m, d = loaders.source_rows_for_symbol(
            symbol=symbol, minute_cache_root=minute_root, daily_cache_root=daily_root, additional_minute_cache_roots=(extra_root,)
        )
        assert minutes[symbol] == m and daily[symbol] == d
    # later source wins on a shared epoch, and epochs are sorted + unique
    epochs = [row["ts"] for row in minutes["005930"]]
    assert epochs == sorted(set(epochs))
    assert next(r for r in minutes["005930"] if r["ts"] == 1790000120)["close"] == 150
    assert [r["day"] for r in daily["005930"]] == ["2026-09-30", "2026-10-01"]
    assert minutes["999999"] == [] and daily["999999"] == []


# --------------------------------------------------------------------- artifact inventory streaming


def _shadow_world(tmp_path: Path) -> Path:
    reports = tmp_path / "reports"
    reports.mkdir()
    shadow = tmp_path / "data" / "logs" / "quant_shadow_candidates" / "2026-10-07"
    shadow.mkdir(parents=True)
    payloads = [
        {"generated_at": "2026-10-07T00:10:00+00:00", "q9_decision_candidates": [
            {"symbol": "005930", "q9_decision_role": "P_SCANNER_PRE_STRATEGIST_UNIVERSE", "rank": 1},
            {"symbol": "000660", "q9_decision_role": "B_STRATEGIST_RANKED"}]},
        {"generated_at": "2026-10-07T00:20:00+00:00", "q9_decision_candidates": []},
        {"generated_at": "2026-10-07T00:30:00+00:00"},
        {},
        {"generated_at": "2026-10-07T00:40:00+00:00", "q9_decision_candidates": [
            {"symbol": "035720", "q9_decision_role": "P_SCANNER_PRE_STRATEGIST_UNIVERSE", "rank": 2}]},
    ]
    for index, payload in enumerate(payloads):
        (shadow / f"2026100700{index}0_x.json").write_text(json.dumps(payload), encoding="utf-8")
    (shadow / "latest.json").write_text(json.dumps({"generated_at": "2026-10-07T09:00:00+00:00", "q9_decision_candidates": [1]}), encoding="utf-8")
    return reports


def test_iter_shadow_payloads_streams_non_empty_in_file_order_and_skips_latest(tmp_path):
    reports = _shadow_world(tmp_path)
    streamed = list(inventory._iter_shadow_payloads(reports, "2026-10-07"))
    assert [p.get("generated_at") for p in streamed] == [
        "2026-10-07T00:10:00+00:00", "2026-10-07T00:20:00+00:00", "2026-10-07T00:30:00+00:00", "2026-10-07T00:40:00+00:00"
    ]  # the empty {} payload and latest.json are excluded, as before
    assert list(inventory._iter_shadow_payloads(reports, "2000-01-01")) == []


def test_pre_strategist_rows_unchanged_by_streaming(tmp_path):
    reports = _shadow_world(tmp_path)
    rows = inventory.load_q9_pre_strategist_rows(reports, "2026-10-07")
    # reference: the pre-fix list-then-filter logic
    shadow_root = tmp_path / "data" / "logs" / "quant_shadow_candidates" / "2026-10-07"
    payloads = []
    for path in sorted(shadow_root.glob("*.json")):
        if path.name == "latest.json":
            continue
        payload = inventory.read_json(path)
        if payload:
            payloads.append(payload)
    expected = []
    for shadow in payloads:
        generated_at = str(shadow.get("generated_at") or "")
        for raw in shadow.get("q9_decision_candidates") or []:
            if not isinstance(raw, dict) or str(raw.get("q9_decision_role") or "") != "P_SCANNER_PRE_STRATEGIST_UNIVERSE":
                continue
            row = dict(raw)
            row.setdefault("_payload_generated_at", generated_at)
            if inventory._synthetic_identity(row) or not inventory._regular_session_window({"generated_at": generated_at}):
                continue
            expected.append(row)
    assert rows == expected


# --------------------------------------------------------------------- stage memory logging


def test_closeout_memory_snapshot_is_best_effort_and_logged(monkeypatch):
    from libs.reporting import closeout_maintenance as cm

    snapshot = cm._closeout_memory_snapshot()
    assert isinstance(snapshot, dict)  # {} off Linux; cgroup/rss fields inside the container

    captured: dict = {}

    class FakeLogger:
        def __init__(self, *_a, **_k):
            pass

        def log(self, **kwargs):
            captured.update(kwargs)

    import libs.core.event_logger as event_logger

    monkeypatch.setattr(event_logger, "EventLogger", FakeLogger)
    monkeypatch.setattr(event_logger, "resolve_event_log_path", lambda: "ignored")
    cm.log_closeout_stage(run_id="r", day="2026-10-07", stage="q8_shadow_blocker_review", phase="start")
    assert captured["payload"]["closeout_stage"] == "q8_shadow_blocker_review"
    assert "memory" in captured["payload"]

    def boom():
        raise RuntimeError("diagnostics must never raise")

    monkeypatch.setattr(cm, "_closeout_memory_snapshot", boom)
    cm.log_closeout_stage(run_id="r", day="2026-10-07", stage="x", phase="start")  # swallowed


# --------------------------------------------------------------------- read_json_array_and_rest / q9 repair writer


@pytest.mark.parametrize("chunk", [64, 1000, 10_000_000])
@pytest.mark.parametrize("position", ["middle", "first", "last"])
def test_read_json_array_and_rest_equals_json_loads(tmp_path, monkeypatch, chunk, position):
    monkeypatch.setattr(jas, "_STREAM_CHUNK_CHARS", chunk)
    windows = _windows_doc(25, pad=200)["windows"]
    if position == "middle":
        doc = {"schema_version": "v1", "day": "2026-10-01", "windows": windows, "window_count": 25, "recovery": {"a": [1, 2]}}
    elif position == "first":
        doc = {"windows": windows, "window_count": 25}
    else:
        doc = {"schema_version": "v1", "updated_at": "x", "windows": windows}
    path = _write(tmp_path / "w.json", doc)
    items, rest = jas.read_json_array_and_rest(path, "windows")
    expected = json.loads(path.read_text(encoding="utf-8"))
    assert items == expected["windows"]
    assert rest == {**expected, "windows": []}
    assert list(rest) == list(expected)  # key order (hence rewritten-file layout) preserved


def test_read_json_array_and_rest_layout_fallback_and_errors(tmp_path):
    doc = {"a": 1, "windows": [{"x": 1}], "b": 2}
    compact = _write(tmp_path / "c.json", doc, indent=None)
    assert jas.read_json_array_and_rest(compact, "windows") == ([{"x": 1}], {"a": 1, "windows": [], "b": 2})
    assert jas.read_json_array_and_rest(tmp_path / "missing.json", "windows") == ([], {})
    text = json.dumps(_windows_doc(10, pad=200), indent=2)
    (tmp_path / "t.json").write_text(text[: len(text) // 2], encoding="utf-8")
    assert jas.read_json_array_and_rest(tmp_path / "t.json", "windows") == ([], {})


def test_q9_repair_writer_is_byte_identical_to_json_dumps(tmp_path):
    from libs.reporting.evaluation import q9_artifact_repair as repair

    payload = {"schema_version": "q9_decision_windows.v1", "windows": _windows_doc(5, pad=50)["windows"], "note": "한글", "when": Path("x")}
    target = tmp_path / "out" / "q9_decision_windows.json"
    repair._write_json_atomic(target, payload)
    reference = tmp_path / "reference.json"  # the pre-fix writer: write_text(json.dumps(...) + newline), same platform newline handling
    reference.write_text(json.dumps(dict(payload), ensure_ascii=False, indent=2, default=str) + chr(10), encoding="utf-8")
    assert target.read_bytes() == reference.read_bytes()
    assert not target.with_suffix(".json.tmp").exists()


# --------------------------------------------------------------------- operator visibility: streamed day rows


def _visibility_world(tmp_path: Path, day: str = "2026-04-08"):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import benchmark_operator_visibility_memory as bench

    events = tmp_path / "events.jsonl"
    bench.gen_fixture(events, history_mb=0.3, day_mb=0.2, day=day)
    return events, tmp_path / "reports", tmp_path / "metrics"


def test_restreamed_day_rows_is_repeatable_filtered_and_truthy(tmp_path, monkeypatch):
    import libs.reporting.operator_visibility as ov

    monkeypatch.setenv("EVENT_LOG_DAY_CACHE_DIR", str(tmp_path / "cache"))
    events, _reports, _metrics = _visibility_world(tmp_path)
    rows = ov._RestreamedDayRows(events, "2026-04-08", "2026-04-08")
    first = [r["_epoch"] for r in rows]
    assert first and first == [r["_epoch"] for r in rows]  # re-iterable, same order each time
    assert all(r["_day"] == "2026-04-08" for r in rows)
    assert bool(rows) is True
    assert bool(ov._RestreamedDayRows(events, "2026-04-08", "2000-01-01")) is False  # nothing for that day


def test_daily_summary_payload_identical_with_streamed_and_materialised_rows(tmp_path, monkeypatch):
    import libs.reporting.operator_visibility as ov

    monkeypatch.setenv("EVENT_LOG_DAY_CACHE_DIR", str(tmp_path / "cache"))
    events, reports, metrics = _visibility_world(tmp_path)
    streamed = ov.build_operator_daily_summary_payload(events, reports, day="2026-04-08", metrics_report_dir=metrics)

    original = ov._RestreamedDayRows

    class Materialised(list):  # the pre-fix behaviour: the whole day held as a list
        def __init__(self, events_path, day, target_day):
            super().__init__(original(events_path, day, target_day))

    monkeypatch.setattr(ov, "_RestreamedDayRows", Materialised)
    materialised = ov.build_operator_daily_summary_payload(events, reports, day="2026-04-08", metrics_report_dir=metrics)
    assert streamed == materialised
    assert streamed["day"] == "2026-04-08" and streamed["source_run_count"] > 0


# --------------------------------------------------------------------- q9 effectiveness windows (20-day load)


def _effectiveness_windows():
    return [
        {"decision_id": "D1", "scanner_control": {"full_strategist_control_eligibility": {"eligible": True}, "top1_symbol": "005930", "junk": [1] * 50},
         "strategist_selection": {"selected_symbol": "000660", "scenario": "x", "big": ["y"] * 100},
         "strategist_provenance": {"feedback": {"feedback_id": "F1", "adoption_status": "CHANGE_OBSERVED_WITH_FEEDBACK_EXPOSURE",
                                                  "source_day": "2026-09-30", "consumed": True, "changed_fields": ["a"]}, "other": 1},
         "scanner_pre_strategist_universe": {"rows": ["z" * 100] * 200}},
        {"q9_decision_id": "Q2", "scanner_control": {"full_strategist_control_eligibility": {"eligible": False}, "top1_symbol": "035720"},
         "strategist_selection": {"selected_symbol": "035720"}, "strategist_provenance": {"feedback": {"feedback_id": "F2"}}},
        {"decision_id": "D3", "scanner_control": "not-a-dict", "strategist_selection": None, "strategist_provenance": {"feedback": "nope"}},
        {"decision_id": "D4"},
        {"decision_id": "D1", "strategist_provenance": {"feedback": {"feedback_id": "F1"}}},  # duplicate identity for the feedback builder
        "not-a-window",
    ]


def test_effectiveness_windows_reduction_gives_builders_identical_results(tmp_path):
    from libs.reporting.evaluation.feedback_effectiveness import build_feedback_effectiveness
    from libs.reporting.evaluation.pipeline import _q9_windows_for_effectiveness
    from libs.reporting.evaluation.strategist_effectiveness import build_strategist_effectiveness

    full = [w for w in _effectiveness_windows() if isinstance(w, dict)]
    path = _write(tmp_path / "q9_decision_windows.json", {"schema_version": "v1", "windows": _effectiveness_windows(), "window_count": 6})
    reduced = _q9_windows_for_effectiveness(path)
    assert len(reduced) == len(full)
    assert build_strategist_effectiveness([], [], reduced) == build_strategist_effectiveness([], [], full)
    assert build_feedback_effectiveness([], reduced) == build_feedback_effectiveness([], full)
    assert "scanner_pre_strategist_universe" not in reduced[0] and "other" not in reduced[0]["strategist_provenance"]


def test_effectiveness_windows_unreadable_or_missing_file_is_no_windows(tmp_path):
    from libs.reporting.evaluation.pipeline import _q9_windows_for_effectiveness

    assert _q9_windows_for_effectiveness(tmp_path / "missing.json") == []
    text = json.dumps({"windows": _effectiveness_windows()}, indent=2)
    (tmp_path / "bad.json").write_text(text[: len(text) // 2], encoding="utf-8")
    assert _q9_windows_for_effectiveness(tmp_path / "bad.json") == []


# --------------------------------------------------------------------- candidate decision summary (streamed)


def _reference_candidate_summary(path: Path):
    """The pre-fix computation: json.loads the whole file, same folding."""
    from collections import Counter

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    decisions, reasons = Counter(), Counter()
    for raw in (payload.get("windows") if isinstance(payload, dict) else []) or []:
        if not isinstance(raw, dict):
            continue
        commander = raw.get("commander_final") if isinstance(raw.get("commander_final"), dict) else {}
        decisions[str(commander.get("decision") or "unknown").strip().lower()] += 1
        reasons[str(commander.get("reason") or "unspecified").strip()] += 1
    return decisions, reasons


@pytest.mark.parametrize("variant", ["valid", "compact", "list-top", "windows-dict", "corrupt", "empty", "missing"])
def test_candidate_decision_summary_equals_whole_file_reading(tmp_path, variant):
    from libs.reporting.operator_candidate_decisions import load_candidate_decision_summary

    day = "2026-02-02"
    path = tmp_path / "operator_summary" / "daily" / day / "q9_decision_windows.json"
    path.parent.mkdir(parents=True)
    good = {"windows": [{"commander_final": {"decision": "Approve", "reason": "r1"}}, {"commander_final": {"decision": "reject", "reason": "r2"}},
                        {"commander_final": "x"}, "junk", {}]}
    text = {
        "valid": json.dumps(good, indent=2), "compact": json.dumps(good), "list-top": json.dumps([1, 2]),
        "windows-dict": json.dumps({"windows": {"a": 1}}, indent=2), "corrupt": json.dumps(good, indent=2)[:50], "empty": "",
    }.get(variant)
    if text is not None:
        path.write_text(text, encoding="utf-8")
    result = load_candidate_decision_summary(reports_root=tmp_path, day=day)
    reference = _reference_candidate_summary(path)
    if reference is None:
        assert result["available"] is False and result["window_count"] == 0
    else:
        decisions, reasons = reference
        assert result["available"] is True
        assert result["decision_counts"] == dict(decisions)
        assert result["reason_counts"] == dict(reasons.most_common(10))
        assert result["window_count"] == sum(decisions.values())


def test_iter_json_array_strict_raises_for_unreadable(tmp_path):
    with pytest.raises(OSError):
        list(jas.iter_json_array(tmp_path / "missing.json", "windows", strict=True))
    (tmp_path / "bad.json").write_text("{nope", encoding="utf-8")
    with pytest.raises(ValueError):
        list(jas.iter_json_array(tmp_path / "bad.json", "windows", strict=True))
    assert list(jas.iter_json_array(tmp_path / "bad.json", "windows")) == []  # default stays lenient


# --------------------------------------------------------------------- q9 windows consumers reduced to the fields they read


def _windows_world(tmp_path: Path, day="2026-10-05"):
    path = tmp_path / "operator_summary" / "daily" / day / "q9_decision_windows.json"
    path.parent.mkdir(parents=True)
    windows = [
        {"decision_id": "A", "run_id": "r1", "commander_final": {"decision": "BUY"}, "decision_epoch": 5, "generated_at": "g1", "blob": ["x"] * 100},
        {"decision_id": "B", "run_id": "r2", "commander_final": None, "generated_at": "g2"},
        {"decision_id": " ", "run_id": "skip"},
        {"decision_id": "A", "run_id": "r3", "commander_final": {"decision": "SELL"}, "decision_epoch": 9, "generated_at": "g3"},  # later duplicate wins
        "junk",
    ]
    _write(path, {"windows": windows})
    return tmp_path, windows


def test_stage2_load_q9_windows_matches_whole_file_semantics(tmp_path):
    from libs.reporting.evaluation.stage2_authority.loaders import load_q9_windows

    reports, windows = _windows_world(tmp_path)
    result = load_q9_windows(reports, "2026-10-05", "2026-10-05")
    expected = {}
    for raw in windows:
        if isinstance(raw, dict) and str(raw.get("decision_id") or "").strip():
            row = dict(raw)
            row["_day"] = "2026-10-05"
            expected[str(raw["decision_id"]).strip()] = row
    assert set(result) == set(expected) == {"A", "B"}
    for key in ("_day", "run_id", "commander_final", "decision_epoch", "generated_at"):
        assert [result[k].get(key) for k in sorted(result)] == [expected[k].get(key) for k in sorted(expected)]
    assert "blob" not in result["A"]
    assert load_q9_windows(reports, "2030-01-01", "2030-01-02") == {}


def test_quant_shadow_windows_by_id_reduced_but_augmentation_unchanged(tmp_path):
    reports, windows = _windows_world(tmp_path, day="2026-10-05")
    by_id = qsce._q9_windows_by_id(reports, "2026-10-05")
    assert set(by_id) == {" ", "A", "B"} and by_id["A"] == {"commander_final": {"decision": "SELL"}}  # keys are not stripped here, as before
    payload = {"q9_decision_id": "A", "q9_decision_candidates": [{"symbol": "005930", "q9_decision_role": "B_STRATEGIST_RANKED"}]}
    full = {str(w["decision_id"]): dict(w) for w in windows if isinstance(w, dict) and str(w.get("decision_id") or "")}
    got = qsce._augment_missing_q9_commander_candidate(json.loads(json.dumps(payload)), windows_by_id=by_id)
    ref = qsce._augment_missing_q9_commander_candidate(json.loads(json.dumps(payload)), windows_by_id=full)
    assert got == ref
    assert qsce._q9_windows_by_id(reports, "2000-01-01") == {}


def test_q16_incremental_dedupe_equals_collect_then_dedupe(tmp_path, monkeypatch):
    from libs.reporting.evaluation import q16_proxy_rejection_review as q16

    reports = tmp_path / "reports"
    daily = reports / "evaluation" / "daily"
    rows_by_day = {
        "2026-10-01": [{"q16_day": "2026-10-01", "q9_decision_id": "a", "symbol": "1", "v": 1}],
        "2026-10-02": [{"q16_day": "2026-10-01", "q9_decision_id": "a", "symbol": "1", "v": 2},  # overlaps day 1 (cumulative review)
                       {"q16_day": "2026-10-02", "q9_decision_id": "b", "symbol": "2", "v": 3}],
    }
    for day, rows in rows_by_day.items():
        (daily / day).mkdir(parents=True)
        (daily / day / "q16_proxy_rejection_review.json").write_text(json.dumps({"samples": rows + ["junk"]}), encoding="utf-8")
    monkeypatch.setattr(q16, "_load_day_rows", lambda root, day: [{"q16_day": "2026-10-03", "q9_decision_id": "c", "symbol": "3", "v": 4},
                                                                  {"q16_day": "2026-10-01", "q9_decision_id": "a", "symbol": "1", "v": 9}])
    captured = {}
    real = q16._forward_integrity

    def spy(row):
        captured.setdefault("order", []).append((row["q9_decision_id"], row["v"]))
        return real(row)

    monkeypatch.setattr(q16, "_forward_integrity", spy)
    q16.build_q16_proxy_rejection_review(reports_root=reports, day="2026-10-03", start_day="2026-10-01")
    # same order/values as: all rows collected in order, then dict-deduped (first position, last value wins)
    assert captured["order"] == [("a", 9), ("b", 3), ("c", 4)]
