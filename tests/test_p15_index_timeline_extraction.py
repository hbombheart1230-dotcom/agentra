"""P15 order 3: load_index_timeline MOVE to index_timeline.py - parity with the frozen pre-extraction output plus the
non-object / malformed-schema skip fix. Files only under tmp_path; inputs are never modified."""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

import pytest

from libs.reporting.baseline_samsung_hynix.forward_validation import index_timeline as it
from libs.reporting.baseline_samsung_hynix.forward_validation import reaction_reader as rr

DAY = "2026-09-07"
EXPECTED = json.loads(r'''[{"close":102.0,"high":102.0,"low":102.0,"open":102.0,"previous_close":null,"source_path":"<ROOT>/2026-09-07/b_macro_indicators.json","ts":1788739200,"volume":null},{"close":103.0,"high":103.0,"low":103.0,"open":103.0,"previous_close":null,"source_path":"<ROOT>/2026-09-07/g_macro_indicators.json","ts":1788739800,"volume":7.0}]''')


def put(root, name, payload):
    d = root / DAY
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")


def snap(generated_at, idx):
    return {"generated_at": generated_at, "korea_indices": {"indices": idx}}


def build_frozen_inputs(root):
    put(root, "a_macro_indicators.json", snap("2026-09-07T00:00:00Z", {"KOSPI": {"current": 100, "previous_close": 99, "high": 101}}))
    put(root, "b_macro_indicators.json", snap("2026-09-07T00:00:00+00:00", {"KOSPI": {"current": 102}}))
    put(root, "c_macro_indicators.json", snap("2026-09-07T00:05:00Z", {"KOSDAQ": {"current": 5}}))
    put(root, "d_macro_indicators.json", snap("garbage", {"KOSPI": {"current": 1}}))
    put(root, "e_macro_indicators.json", "{bad")
    put(root, "g_macro_indicators.json", snap("2026-09-07T00:10:00Z", {"KOSPI": {"current": 103, "open": 0, "volume": 7}}))
    put(root, "h_macro_indicators.json", snap("2026-09-07T00:15:00Z", {"KOSPI": {"current": "x"}}))
    put(root, "i_macro_indicators.json", {"korea_indices": {"indices": {"KOSPI": {"current": 4}}}})


def digest(root):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((root / DAY).glob("*"))}


def norm(rows, root):
    out = json.loads(json.dumps(rows, sort_keys=True))
    for r in out:
        r["source_path"] = r["source_path"].replace(str(root), "<ROOT>")
    return out


def test_wrapper_and_owner_equal_frozen_pre_extraction_output_and_inputs_untouched(tmp_path):
    build_frozen_inputs(tmp_path)
    before = digest(tmp_path)
    w = rr.load_index_timeline(day=DAY, macro_root=tmp_path, index_name="KOSPI")
    o = it.load_index_timeline_impl(day=DAY, macro_root=tmp_path, index_name="KOSPI", facade=rr)
    assert norm(w, tmp_path) == EXPECTED == norm(o, tmp_path) and digest(tmp_path) == before
    assert [r["close"] for r in w] == [102.0, 103.0] and w[0]["open"] == 102.0 and w[1]["open"] == 103.0 and w[1]["volume"] == 7.0       # falsy open/high/low fall back to current


def test_same_timestamp_keeps_the_last_file_and_output_is_time_sorted(tmp_path):
    put(tmp_path, "z_macro_indicators.json", snap("2026-09-07T00:20:00Z", {"KOSPI": {"current": 1}}))
    put(tmp_path, "a_macro_indicators.json", snap("2026-09-07T00:10:00Z", {"KOSPI": {"current": 2}}))
    put(tmp_path, "b_macro_indicators.json", snap("2026-09-07T00:10:00Z", {"KOSPI": {"current": 3}}))
    rows = rr.load_index_timeline(day=DAY, macro_root=tmp_path, index_name="KOSPI")
    assert [r["close"] for r in rows] == [3.0, 1.0] and [r["ts"] for r in rows] == sorted(r["ts"] for r in rows)


def test_empty_missing_day_and_no_index_entries_give_empty_list(tmp_path):
    assert rr.load_index_timeline(day=DAY, macro_root=tmp_path, index_name="KOSPI") == []
    (tmp_path / DAY).mkdir()
    assert rr.load_index_timeline(day=DAY, macro_root=tmp_path, index_name="KOSPI") == []
    put(tmp_path, "a_macro_indicators.json", snap("2026-09-07T00:00:00Z", {"KOSDAQ": {"current": 5}}))
    assert rr.load_index_timeline(day=DAY, macro_root=tmp_path, index_name="KOSPI") == []


@pytest.mark.parametrize("bad", ["[]", "[1, 2]", '"text"', "42", "null", json.dumps({"generated_at": "2026-09-07T00:00:00Z", "korea_indices": []}),
                                 json.dumps({"generated_at": "2026-09-07T00:00:00Z", "korea_indices": "x"}), json.dumps({"generated_at": "2026-09-07T00:00:00Z", "korea_indices": {"indices": []}}),
                                 json.dumps({"generated_at": "2026-09-07T00:00:00Z", "korea_indices": {"indices": {"KOSPI": [1]}}}),
                                 json.dumps({"generated_at": "2026-09-07T00:00:00Z", "korea_indices": {"indices": {"KOSPI": "x"}}})])
def test_malformed_schema_file_is_skipped_and_good_file_still_read(tmp_path, bad):
    put(tmp_path, "a_macro_indicators.json", bad)
    put(tmp_path, "b_macro_indicators.json", snap("2026-09-07T00:10:00Z", {"KOSPI": {"current": 7}}))
    before = digest(tmp_path)
    rows = rr.load_index_timeline(day=DAY, macro_root=tmp_path, index_name="KOSPI")
    assert [r["close"] for r in rows] == [7.0] and digest(tmp_path) == before


def test_previously_fatal_list_payload_regression_exact(tmp_path):
    """Pre-fix behaviour: AttributeError('list' object has no attribute 'get') aborted the whole timeline."""
    put(tmp_path, "a_macro_indicators.json", "[]")
    put(tmp_path, "b_macro_indicators.json", snap("2026-09-07T00:10:00Z", {"KOSPI": {"current": 1.5, "previous_close": 1.0}}))
    rows = it.load_index_timeline_impl(day=DAY, macro_root=tmp_path, index_name="KOSPI", facade=rr)
    assert len(rows) == 1 and rows[0]["close"] == 1.5 and rows[0]["previous_close"] == 1.0


def test_existing_exception_scope_and_facade_number_resolution(tmp_path, monkeypatch):
    put(tmp_path, "a_macro_indicators.json", snap(None, {"KOSPI": {"current": 1}}))                      # missing generated_at -> ValueError -> skipped
    put(tmp_path, "b_macro_indicators.json", snap("2026-09-07T00:10:00Z", {"KOSPI": {"current": 4}}))
    assert [r["close"] for r in rr.load_index_timeline(day=DAY, macro_root=tmp_path, index_name="KOSPI")] == [4.0]
    monkeypatch.setattr(rr, "_number", lambda v: 9.0)
    assert [r["close"] for r in rr.load_index_timeline(day=DAY, macro_root=tmp_path, index_name="KOSPI")] == [9.0]


def test_import_is_io_free_wrapper_delegates_and_owner_is_small(monkeypatch):
    path = Path(it.__file__)
    tree = ast.parse(path.read_text(encoding="utf-8"))
    mods = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert "reaction_reader" not in " ".join(m or "" for m in mods) and len(path.read_text(encoding="utf-8").splitlines()) <= 350
    seen = {}
    monkeypatch.setattr(rr, "load_index_timeline_impl", lambda **kw: seen.update(kw) or ["X"])
    assert rr.load_index_timeline(day=DAY, macro_root=Path("/nonexistent"), index_name="K") == ["X"] and seen["facade"] is sys.modules[rr.__name__]
