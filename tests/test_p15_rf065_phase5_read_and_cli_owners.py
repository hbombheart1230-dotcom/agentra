from datetime import date
from pathlib import Path

from scripts.research import run_phase5_validation_bundle as bundle


def test_read_projection_facades_and_parser(tmp_path, monkeypatch):
    missing = tmp_path / "missing.jsonl"
    assert bundle._iter_events(missing) == []
    events = tmp_path / "events.jsonl"
    events.write_text('{"ts":"2026-10-29T12:00:00Z"}\n\nnope\n[]\n{"ts_kst":"2026-10-30T12:00:00Z"}\n', encoding="utf-8")
    assert list(bundle._iter_events(events)) == [
        {"ts": "2026-10-29T12:00:00Z"}, {"ts_kst": "2026-10-30T12:00:00Z"}
    ]
    payload = tmp_path / "payload.json"
    payload.write_text('{"a": 1}', encoding="utf-8")
    assert bundle._read_json(payload) == {"a": 1}
    assert bundle._read_json(tmp_path / "none.json") == {}
    assert bundle._to_day_key("0") == "1970-01-01"
    assert bundle._to_day_key("2026-10-30T12:00:00Z") == "2026-10-30"
    assert bundle._to_day_key("bad") is None
    assert bundle._resolve_day(events, None) == "2026-10-30"
    assert bundle._resolve_day(events, " 2030-01-01 ") == "2030-01-01"
    assert bundle._safe_rel(tmp_path, tmp_path) == "."
    root = tmp_path / "reports" / "canonical" / "2026-10-30"
    (root / "RUN_A").mkdir(parents=True)
    (root / "RUN_B").mkdir()
    assert bundle._pick_latest_canonical_run_id(tmp_path / "reports", "2026-10-30") in {"RUN_A", "RUN_B"}
    parser = bundle._build_parser()
    assert parser.parse_args([]).max_runs == 120
    assert parser.parse_args(["--day", "2026-10-30", "--json"]).json is True
