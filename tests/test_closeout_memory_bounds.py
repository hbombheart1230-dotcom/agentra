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
