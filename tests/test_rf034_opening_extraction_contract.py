"""RF-034 C3: opening_rank1_shadow.extraction window selection (09:00-09:20 KST, rank-1 only) on a tmp reports root."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from libs.reporting.opening_rank1_shadow import extraction as ex

KST = timezone(timedelta(hours=9))
DAY = "2026-09-07"


def ep(h, m, s=0, day=DAY):
    y, mo, d = map(int, day.split("-"))
    return int(datetime(y, mo, d, h, m, s, tzinfo=KST).timestamp())


def win(epoch, cands, *, wtype="scanner_selection", did=None):
    return {"window_type": wtype, "decision_id": did or f"D{epoch}", "decision_epoch": epoch, "scanner_pre_strategist_universe": {"intrinsic_ranked_top20": cands}}


def put(tmp, windows, day=DAY):
    p = tmp / "operator_summary" / "daily" / day / "q9_decision_windows.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(windows if isinstance(windows, str) else json.dumps({"windows": windows}), encoding="utf-8")
    return p


def test_valid_opening_epoch_boundaries():
    v = ex._valid_opening_epoch
    assert v(ep(9, 0), DAY) and v(ep(9, 19, 59), DAY) and not v(ep(9, 20), DAY) and not v(ep(8, 59, 59), DAY)
    assert not v(0, DAY) and not v(-5, DAY) and not v(ep(9, 5, day="2026-09-08"), DAY) and not v(10**20, DAY)


def test_missing_or_corrupt_file_yields_empty_result(tmp_path):
    out = ex.extract_opening_rank1_windows(reports_root=tmp_path, day=DAY)
    assert out["source_exists"] is False and out["windows"] == [] and out["symbols"] == [] and out["raw_scanner_window_count"] == 0
    put(tmp_path, "{bad")
    out = ex.extract_opening_rank1_windows(reports_root=tmp_path, day=DAY)
    assert out["source_exists"] is True and out["windows"] == []
    put(tmp_path, "[1]")
    assert ex.extract_opening_rank1_windows(reports_root=tmp_path, day=DAY)["raw_scanner_window_count"] == 0


def test_rank1_only_sorted_candidates_and_counters(tmp_path):
    put(tmp_path, [
        win(ep(9, 5), [{"symbol": "B", "rank": 2}, {"symbol": "A", "rank": 1}, {"symbol": " ", "rank": 1}, "junk"], did="W1"),
        win(ep(9, 6), [{"symbol": "C", "rank": 2}]),                                   # no rank-1
        win(ep(9, 7), []),                                                             # empty universe
        win(ep(9, 8), [{"symbol": "Z"}]),                                              # rank missing -> 999, not rank-1
        win(0, [{"symbol": "Q", "rank": 1}]),                                          # invalid epoch
        win(ep(9, 30), [{"symbol": "L", "rank": 1}]),                                  # outside opening window (not counted invalid)
        win(ep(9, 9), [{"symbol": "X", "rank": 1}], wtype="other"),                    # wrong window type
        "junk",
        win(ep(9, 10), [{"symbol": "T", "rank": 1}, {"symbol": "A", "rank": 1}]),      # tie on rank -> symbol order
    ])
    out = ex.extract_opening_rank1_windows(reports_root=tmp_path, day=DAY)
    assert out["raw_scanner_window_count"] == 7 and out["invalid_epoch_count"] == 1
    assert out["missing_rank1_count"] == 2 and out["missing_universe_count"] == 1 and out["opening_window_count"] == 2
    assert [w["candidates"] for w in out["windows"]] == [[{"symbol": "A", "rank": 1}], [{"symbol": "A", "rank": 1}]]
    assert out["windows"][0]["decision_id"] == "W1" and out["windows"][0]["day"] == DAY and out["windows"][0]["source_path"] == out["source_path"]
    assert out["symbols"] == ["A"]


def test_duplicate_epochs_collapse_to_last_and_windows_are_epoch_sorted(tmp_path):
    put(tmp_path, [win(ep(9, 10), [{"symbol": "S2", "rank": 1}], did="late"), win(ep(9, 2), [{"symbol": "S1", "rank": 1}], did="early"), win(ep(9, 10), [{"symbol": "S3", "rank": 1}], did="dup")])
    out = ex.extract_opening_rank1_windows(reports_root=tmp_path, day=DAY)
    assert [w["decision_id"] for w in out["windows"]] == ["early", "dup"] and out["symbols"] == ["S1", "S3"]
