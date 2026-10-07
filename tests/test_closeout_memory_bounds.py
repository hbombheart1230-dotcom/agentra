"""Closeout memory fix (P1.3): streaming / per-symbol loaders must be output-equivalent.

The 10-06/10-07 closeouts were OOM-killed at the 1 GiB container cap. These tests pin that the
memory-bounded rewrites of the closeout-path loaders return exactly what the loaders they replace
returned (the real-data byte-for-byte comparison is recorded in the patch note).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
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


# --------------------------------------------------------------------- q9 row-key projection (drop_q9_row_keys)


def _q9_row(symbol, role, rank, decision="d1", **extra):
    row = {"symbol": symbol, "q9_decision_role": role, "q9_decision_id": decision, "rank": rank, "q9_semantic_role": role,
           "shadow_forward_base": {"available": True, "baseline_epoch": 1791331200, "baseline_price": 100.0},
           "q9_candidate_sources": ["top_value"], "q9_candidate_source_scores": {"top_value": 1.0},
           "entry_lane_observation": {"lane": "x" * 400}, "score_breakdown": {"a": 1, "b": [2] * 50},
           "compact_feature_snapshot": {"c": 3}, "below_vwap_reclaim_observation": {"d": 4}}
    row.update(extra)
    return row


def _q9_world(tmp_path: Path, day="2026-10-07", count=4):
    shadow = tmp_path / "data" / "logs" / "quant_shadow_candidates" / day
    shadow.mkdir(parents=True)
    for index in range(count):
        payload = {"generated_at": f"{day}T00:{index:02d}:00+00:00", "q9_decision_id": f"d{index}", "candidates": [],
                   "q9_decision_candidates": [_q9_row("005930", "P_SCANNER_PRE_STRATEGIST_UNIVERSE", 1, f"d{index}"),
                                              _q9_row("000660", "A_SCANNER_CONTROL", 1, f"d{index}"),
                                              _q9_row("005930", "B_STRATEGIST_RANKED", 1, f"d{index}", q9_selected=True)]}
        (shadow / f"2026100700{index}000Z_x.json").write_text(json.dumps(payload), encoding="utf-8")
    (tmp_path / "reports").mkdir()
    return tmp_path / "reports"


def test_drop_q9_row_keys_removes_only_the_listed_keys(tmp_path):
    reports = _q9_world(tmp_path)
    full = qsce.load_quant_shadow_candidate_payloads(reports_root=reports, days=["2026-10-07"])
    slim = qsce.load_quant_shadow_candidate_payloads(
        reports_root=reports, days=["2026-10-07"], drop_q9_row_keys=qsce.Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN
    )
    assert len(full) == len(slim) == 4
    for a, b in zip(full, slim):
        assert [set(r) - set(qsce.Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN) for r in a["q9_decision_candidates"]] == [set(r) for r in b["q9_decision_candidates"]]
        for ra, rb in zip(a["q9_decision_candidates"], b["q9_decision_candidates"]):
            assert {k: v for k, v in ra.items() if k not in qsce.Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN} == rb
    # default keeps everything, and the range wrapper forwards the option
    assert "entry_lane_observation" in full[0]["q9_decision_candidates"][0]
    ranged = qsce.load_quant_shadow_candidate_payloads_for_range(
        reports_root=reports, start="2026-10-07", end="2026-10-07", drop_q9_row_keys=("score_breakdown",)
    )
    assert "score_breakdown" not in ranged[0]["q9_decision_candidates"][0] and "entry_lane_observation" in ranged[0]["q9_decision_candidates"][0]


class _Trap(dict):
    """A value that records (and rejects) any attempt to look inside it."""

    hits: list = []

    def _hit(self, how):
        _Trap.hits.append(how)
        raise AssertionError(f"consumer read a key declared unused ({how})")

    def __getitem__(self, key): self._hit("getitem")
    def get(self, *args): self._hit("get")
    def items(self): self._hit("items")
    def keys(self): self._hit("keys")
    def values(self): self._hit("values")
    def __iter__(self): self._hit("iter")
    def __contains__(self, key): self._hit("contains")


def test_full_chain_review_never_reads_the_dropped_q9_keys_and_output_is_unchanged(tmp_path, monkeypatch):
    from libs.reporting.evaluation import full_chain_component_review as fc

    monkeypatch.chdir(tmp_path)
    reports = _q9_world(tmp_path)
    baseline = fc.build_full_chain_component_review(reports_root=reports, start="2026-10-07", end="2026-10-07")
    real_loader = fc.load_quant_shadow_candidate_payloads_for_range

    def trapping_loader(**kwargs):
        assert kwargs.get("drop_q9_row_keys") == qsce.Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN  # the review opts in
        payloads = real_loader(**{k: v for k, v in kwargs.items() if k != "drop_q9_row_keys"})
        for payload in payloads:
            for row in payload["q9_decision_candidates"]:
                for key in qsce.Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN:
                    row[key] = _Trap()
        return payloads

    _Trap.hits.clear()
    monkeypatch.setattr(fc, "load_quant_shadow_candidate_payloads_for_range", trapping_loader)
    trapped = fc.build_full_chain_component_review(reports_root=reports, start="2026-10-07", end="2026-10-07")
    assert _Trap.hits == []
    assert json.dumps(trapped, sort_keys=True, default=str) == json.dumps(baseline, sort_keys=True, default=str)


def test_dropped_key_names_are_not_referenced_by_the_modules_that_opt_in():
    import re

    paths = [
        "libs/reporting/evaluation/full_chain_component_review.py",
        "libs/reporting/evaluation/scanner_quality.py",
        "libs/reporting/evaluation/cost_basis_comparison.py",
        "libs/reporting/quant_shadow_forward_outcomes.py",
        "libs/reporting/q8_evaluation_contract.py",
    ]
    for path in paths:
        text = (ROOT / path).read_text(encoding="utf-8")
        for key in qsce.Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN:
            assert not re.search(rf"""["']{key}["']""", text), (path, key)


def test_stage2_authority_payload_projection_matches_full_load(tmp_path):
    from libs.reporting.evaluation.full_chain_component_review import _q9_decision_candidate_rows

    reports = _q9_world(tmp_path)
    full = qsce.load_quant_shadow_candidate_payloads_for_range(reports_root=reports, start="2026-10-07", end="2026-10-07")
    slim = qsce.load_quant_shadow_candidate_payloads_for_range(
        reports_root=reports, start="2026-10-07", end="2026-10-07", keys=("q9_decision_candidates", "generated_at")
    )
    assert set(slim[0]) == {"q9_decision_candidates", "generated_at"}
    assert _q9_decision_candidate_rows(slim) == _q9_decision_candidate_rows(full)


def test_evaluation_lens_opts_in_and_never_reads_dropped_q9_keys(tmp_path, monkeypatch):
    from libs.reporting.evaluation import evaluation_lens_report as lens

    monkeypatch.chdir(tmp_path)
    reports = _q9_world(tmp_path)
    baseline = lens.build_evaluation_lens_report(reports_root=reports, start="2026-10-07", end="2026-10-07")
    real_loader = lens.load_quant_shadow_candidate_payloads_for_range

    def trapping(**kwargs):
        assert kwargs.get("drop_q9_row_keys") == qsce.Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN
        payloads = real_loader(**{k: v for k, v in kwargs.items() if k != "drop_q9_row_keys"})
        for payload in payloads:
            for row in payload["q9_decision_candidates"]:
                for key in qsce.Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN:
                    row[key] = _Trap()
        return payloads

    _Trap.hits.clear()
    monkeypatch.setattr(lens, "load_quant_shadow_candidate_payloads_for_range", trapping)
    trapped = lens.build_evaluation_lens_report(reports_root=reports, start="2026-10-07", end="2026-10-07")
    assert _Trap.hits == []
    assert json.dumps(trapped, sort_keys=True, default=str) == json.dumps(baseline, sort_keys=True, default=str)


# --------------------------------------------------------------------- evaluation lens: streaming accumulators


def _lens_outcome(seed: int):
    horizons = {"+5m": 0, "+15m": 1, "+30m": 2, "EOD": 3}
    checkpoints = {}
    for name, offset in horizons.items():
        value = (seed * 7 + offset * 3) % 11 - 5
        if (seed + offset) % 5 == 0:
            checkpoints[name] = {"status": "pending"}  # not observed -> excluded, like the real outcomes
        else:
            checkpoints[name] = {"status": "observed", "return_pct": value * 0.37, "mfe_pct": abs(value) * 0.5 + 0.1, "mae_pct": -abs(value) * 0.3}
    return {"available": True, "checkpoints": checkpoints}


def _lens_candidate_rows(day_index: int, count: int):
    blockers = ["breakout_not_ready", "pullback_not_mature", "other_reason", "volume_confirmation_missing", ""]
    rows = []
    for i in range(count):
        seed = day_index * 100 + i
        row = {
            "symbol": f"{(seed % 7):06d}", "reason": blockers[seed % len(blockers)], "shadow_role": "top_pick",
            "_payload_generated_at": f"2026-10-0{day_index + 1}T00:{i % 60:02d}:00+00:00",
            "shadow_forward_base": {"baseline_raw_ts": f"2026100{day_index + 1}090000" if i % 3 else ""},
            "entry_lane_observation": {"market_regime_rail": ["risk_on", "risk_off", ""][seed % 3]},
            "shadow_forward_outcome": _lens_outcome(seed),
        }
        rows.append(row)
    return rows


def _lens_q9_rows(day_index: int, decisions: int):
    roles = ["P_SCANNER_PRE_STRATEGIST_UNIVERSE", "A_SCANNER_CONTROL", "B_STRATEGIST_RANKED", "R1_PRE_REFRESH_SCANNER", "C_COMMANDER_FINAL"]
    rows = []
    for d in range(decisions):
        for r, role in enumerate(roles):
            for rank in (1, 2, 3):
                seed = day_index * 1000 + d * 17 + r * 5 + rank
                rows.append({
                    "q9_decision_id": f"D{day_index}-{d % 4}" if d != 3 else "", "q9_decision_role": role, "rank": rank if (seed % 9) else "",
                    "q9_selected": bool(role == "B_STRATEGIST_RANKED" and rank == 2 and d % 2), "shadow_forward_outcome": _lens_outcome(seed),
                })
    return rows


def test_lens_streaming_accumulators_equal_the_materialised_reviews():
    from libs.reporting.evaluation import evaluation_lens_report as lens

    days = [(_lens_candidate_rows(i, 40), _lens_q9_rows(i, 9)) for i in range(3)]
    all_candidates = [row for cands, _ in days for row in cands]
    all_q9 = [row for _, q9 in days for row in q9]
    for cost_floor in (0.0, 0.9):
        blocker = lens._BlockerReviewAccumulator(cost_floor)
        strategist = lens._StrategistDeltaAccumulator()
        for cands, q9 in days:  # day-sized chunks, in order, like build_evaluation_lens_report
            blocker.add_rows(cands)
            strategist.add_rows(q9)
        assert blocker.result() == lens._blocker_forward_review(all_candidates, cost_floor_pct=cost_floor)
        assert strategist.result() == lens._strategist_delta_review(all_q9)
    assert blocker.result()["by_blocker"] and blocker.result()["by_market_rail"]  # the fixture exercises real groups
    assert strategist.result()["decision_window_count"] > 0


def test_lens_report_is_built_day_by_day_without_materialising_the_range(tmp_path, monkeypatch):
    from libs.reporting.evaluation import evaluation_lens_report as lens

    monkeypatch.chdir(tmp_path)
    reports = tmp_path / "reports"
    reports.mkdir()
    for day in ("2026-10-05", "2026-10-06", "2026-10-07"):
        shadow = tmp_path / "data" / "logs" / "quant_shadow_candidates" / day
        shadow.mkdir(parents=True)
        for index in range(3):
            payload = {"generated_at": f"{day}T00:0{index}:00+00:00", "candidates": [_q9_row("005930", "x", 1)], "q9_decision_candidates": [
                _q9_row("005930", "P_SCANNER_PRE_STRATEGIST_UNIVERSE", 1, f"{day}-{index}"), _q9_row("000660", "B_STRATEGIST_RANKED", 1, f"{day}-{index}")]}
            (shadow / f"{day.replace('-', '')}00{index}000Z_x.json").write_text(json.dumps(payload), encoding="utf-8")
    loads = []
    real = lens.load_quant_shadow_candidate_payloads_for_range

    def spy(**kwargs):
        loads.append((kwargs["start"], kwargs["end"]))
        return real(**kwargs)

    monkeypatch.setattr(lens, "load_quant_shadow_candidate_payloads_for_range", spy)
    report = lens.build_evaluation_lens_report(reports_root=reports, start="2026-10-05", end="2026-10-07")
    assert loads == [("2026-10-05", "2026-10-05"), ("2026-10-06", "2026-10-06"), ("2026-10-07", "2026-10-07")]  # one day resident at a time
    assert report["evidence"]["shadow_payload_count"] == 9 and report["evidence"]["candidate_count"] == 9
    assert report["evidence"]["q9_candidate_count"] == 18


# --------------------------------------------------------------------- inventory window diagnostics / per-trade snapshot (streamed)


def _inventory_windows():
    base_ts = "2026-10-07T00:{m:02d}:00+00:00"  # 09:xx KST
    windows = []
    for i in range(6):
        windows.append({
            "decision_id": f"D{i}", "run_id": f"r{i}", "generated_at": base_ts.format(m=i),
            "scanner_control": {"top1_symbol": "005930"}, "strategist_selection": {"selected_symbol": "005930", "post_strategist_top10": [1]} if i % 2 else {"selected_symbol": ""},
            "commander_final": {"decision": "BUY"} if i != 3 else "x", "scanner_pre_strategist_universe": {"intrinsic_ranked_top20": [1]} if i % 3 else {},
        })
    windows.append({"decision_id": "test-1", "run_id": "r9", "generated_at": base_ts.format(m=9), "scanner_control": {"top1_symbol": "005930"}})  # synthetic id
    windows.append({"decision_id": "D7", "run_id": "r7", "generated_at": "2026-10-07T07:00:00+00:00", "scanner_control": {"top1_symbol": "000660"}})  # 16:00 KST: post-session
    windows.append({"decision_id": "D8", "run_id": "r8", "generated_at": base_ts.format(m=10), "scanner_control": {"top1_symbol": "NOT-A-SYMBOL"}})  # non-KRX symbol -> synthetic
    windows.append({"decision_id": "D9", "run_id": "r10", "generated_at": base_ts.format(m=11)})  # no scanner_control
    windows.append("junk")
    return windows


def _reference_q9_daily_diagnostics_counts(windows):
    """The pre-fix list/equality based classification, on whole-file windows."""
    from libs.reporting.evaluation import artifact_inventory as inv

    dict_windows = [w for w in windows if isinstance(w, dict)]
    scanner = [w for w in dict_windows if isinstance(w.get("scanner_control"), dict)]
    synthetic = [w for w in scanner if inv._synthetic_identity(w)]
    post = [w for w in scanner if w not in synthetic and not inv._regular_session_window(w)]
    trusted = [w for w in scanner if w not in synthetic and w not in post]
    return {
        "window_count": len(dict_windows), "scanner_selection_window_count": len(trusted),
        "complete_abc_window_count": sum(1 for r in trusted if isinstance(r.get("strategist_selection"), dict) and isinstance(r.get("commander_final"), dict)),
        "complete_pabc_window_count": sum(1 for r in trusted if isinstance(r.get("scanner_pre_strategist_universe"), dict) and isinstance(r.get("scanner_control"), dict)
                                          and isinstance(r.get("strategist_selection"), dict) and isinstance(r.get("commander_final"), dict)),
        "pre_strategist_universe_window_count": sum(1 for r in trusted if isinstance(r.get("scanner_pre_strategist_universe"), dict)
                                                    and bool((r.get("scanner_pre_strategist_universe") or {}).get("intrinsic_ranked_top20"))),
        "missing_selected_candidate_count": sum(1 for r in trusted if bool((r.get("strategist_selection") or {}).get("post_strategist_top10"))
                                                and not str((r.get("strategist_selection") or {}).get("selected_symbol") or "")),
        "synthetic_window_count": len(synthetic), "post_session_window_count": len(post),
    }


def test_inventory_q9_window_diagnostics_stream_equals_whole_file_classification(tmp_path):
    from libs.reporting.evaluation import artifact_inventory as inv

    windows = _inventory_windows()
    path = tmp_path / "q9_decision_windows.json"
    _write(path, {"schema_version": inv.Q9_DECISION_SCHEMA, "windows": windows})
    reports = tmp_path / "reports"
    (reports / "operator_summary" / "daily" / "2026-10-07").mkdir(parents=True)
    record = inv._q9_daily_diagnostics(reports, "2026-10-07", {"path": str(path), "schema_version": inv.Q9_DECISION_SCHEMA})
    expected = _reference_q9_daily_diagnostics_counts(windows)
    assert {k: record[k] for k in expected} == expected
    assert expected["synthetic_window_count"] == 2 and expected["post_session_window_count"] == 1 and expected["scanner_selection_window_count"] > 0


def test_inventory_q9_window_diagnostics_missing_or_corrupt_file_counts_nothing(tmp_path):
    from libs.reporting.evaluation import artifact_inventory as inv

    reports = tmp_path / "reports"
    (reports / "operator_summary" / "daily" / "2026-10-07").mkdir(parents=True)
    missing = inv._q9_daily_diagnostics(reports, "2026-10-07", {"path": str(tmp_path / "nope.json")})
    text = json.dumps({"windows": _inventory_windows()}, indent=2)
    bad = tmp_path / "bad.json"
    bad.write_text(text[: len(text) // 2], encoding="utf-8")
    corrupt = inv._q9_daily_diagnostics(reports, "2026-10-07", {"path": str(bad)})
    for record in (missing, corrupt):
        assert record["window_count"] == 0 and record["scanner_selection_window_count"] == 0 and record["synthetic_window_count"] == 0


def _reference_daily_q9_snapshot(windows_payload, scanner_context, entry, selected_symbol):
    from libs.reporting.evaluation import trade_read_model as trm

    windows = [dict(row) for row in windows_payload.get("windows") or [] if isinstance(row, dict)]
    if not windows:
        return {}, ""
    decision_id = str(scanner_context.get("q9_decision_id") or "").strip()
    if decision_id:
        exact = next((row for row in windows if str(row.get("decision_id") or "") == decision_id), None)
        if exact:
            return exact, "daily_q9_window.decision_id"
    run_ids = {str(v or "").strip() for v in (entry.get("run_id"), scanner_context.get("run_id"), scanner_context.get("entry_run_id")) if str(v or "").strip()}
    for row in windows:
        if str(row.get("run_id") or "").strip() in run_ids:
            return row, "daily_q9_window.run_id"
    entry_ts = trm._parse_ts(entry.get("timestamp") or entry.get("ts"))
    if entry_ts is None or not selected_symbol:
        return {}, ""
    nearest = None
    for row in windows:
        strategist = row.get("strategist_selection") if isinstance(row.get("strategist_selection"), dict) else {}
        commander = row.get("commander_final") if isinstance(row.get("commander_final"), dict) else {}
        if selected_symbol not in {str(strategist.get("selected_symbol") or ""), str(commander.get("selected_symbol") or ""), str(commander.get("candidate_symbol") or "")}:
            continue
        generated_at = trm._parse_ts(row.get("generated_at"))
        if generated_at is None:
            continue
        delta = abs((generated_at - entry_ts).total_seconds())
        if delta <= 600 and (nearest is None or delta < nearest[0]):
            nearest = (delta, row)
    return (nearest[1], "daily_q9_window.nearest_symbol_time") if nearest else ({}, "")


@pytest.mark.parametrize(
    "context,entry,symbol",
    [
        ({"q9_decision_id": "W2"}, {}, "005930"),                      # exact decision id
        ({"q9_decision_id": "W2"}, {"run_id": "run-1"}, "005930"),     # exact id beats an earlier run match
        ({"q9_decision_id": "missing"}, {"run_id": "run-1"}, "005930"),  # run id (first in file order)
        ({}, {"timestamp": "2026-10-07T00:03:10+00:00"}, "000660"),    # nearest same-symbol window
        ({}, {"timestamp": "2026-10-07T00:03:10+00:00"}, ""),          # no symbol -> nothing
        ({}, {"timestamp": "bad"}, "005930"),
        ({"q9_decision_id": "nope"}, {"run_id": "nope", "timestamp": "2000-01-01T00:00:00+00:00"}, "005930"),
    ],
)
def test_daily_q9_snapshot_streamed_search_equals_whole_file_search(tmp_path, context, entry, symbol):
    from libs.reporting.evaluation import trade_read_model as trm

    windows = [
        {"decision_id": "W0", "run_id": "run-1", "generated_at": "2026-10-07T00:01:00+00:00", "strategist_selection": {"selected_symbol": "005930"}},
        {"decision_id": "W1", "run_id": "run-1", "generated_at": "2026-10-07T00:02:00+00:00", "commander_final": {"candidate_symbol": "000660"}},
        {"decision_id": "W2", "run_id": "run-2", "generated_at": "2026-10-07T00:03:00+00:00", "commander_final": {"selected_symbol": "000660"}},
        {"decision_id": "W3", "run_id": "run-3", "generated_at": "2026-10-07T00:03:05+00:00", "commander_final": {"selected_symbol": "000660"}},
        "junk",
    ]
    payload = {"windows": windows}
    reports = tmp_path / "reports"
    path = reports / "operator_summary" / "daily" / "2026-10-07" / "q9_decision_windows.json"
    path.parent.mkdir(parents=True)
    _write(path, payload)
    trade_dir = reports / "trades" / "2026-10-07" / "TRD1" / "x"
    got = trm._daily_q9_snapshot(trade_dir, day="2026-10-07", entry=entry, scanner_context=context, selected_symbol=symbol)
    assert got == _reference_daily_q9_snapshot(payload, context, entry, symbol)


def test_daily_q9_snapshot_missing_or_corrupt_windows_file_is_empty(tmp_path):
    from libs.reporting.evaluation import trade_read_model as trm

    reports = tmp_path / "reports"
    trade_dir = reports / "trades" / "2026-10-07" / "TRD1" / "x"
    assert trm._daily_q9_snapshot(trade_dir, day="2026-10-07", entry={}, scanner_context={"q9_decision_id": "W1"}, selected_symbol="005930") == ({}, "")
    path = reports / "operator_summary" / "daily" / "2026-10-07" / "q9_decision_windows.json"
    path.parent.mkdir(parents=True)
    text = json.dumps({"windows": [{"decision_id": f"W{i}", "blob": "x" * 200} for i in range(20)]}, indent=2)
    path.write_text(text[: len(text) // 2], encoding="utf-8")
    assert trm._daily_q9_snapshot(trade_dir, day="2026-10-07", entry={}, scanner_context={"q9_decision_id": "W19"}, selected_symbol="005930") == ({}, "")
