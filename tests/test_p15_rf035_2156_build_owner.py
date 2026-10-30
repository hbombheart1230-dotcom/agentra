"""P15 RF-035 (2156): controlled_validation_daily.build_controlled_validation_daily moved to controlled_validation_daily_build_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json
from datetime import datetime as real_datetime

import pytest

from libs.reporting import controlled_validation_daily as m
from libs.reporting import controlled_validation_daily_build_projection as owner


def _both(root, day):
    return m.build_controlled_validation_daily(reports_root=root, day=day), owner.build_controlled_validation_daily(reports_root=root, day=day, facade=m)


class _FakeDT(real_datetime):
    @classmethod
    def now(cls, tz=None):
        return real_datetime(2026, 10, 31, 12, 0, tzinfo=tz)


def _dump(root, rel, payload):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload), encoding="utf-8")


def test_empty(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    a, b = _both(reports, "2026-10-30")
    assert a == b and a["schema_version"] == "controlled_validation_daily.v1"
    assert [r["lane_id"] for r in a["lanes"]] == ["Q10_SEMICONDUCTOR", "Q10_INDEX", "BTC_WOORI"]
    assert a["opening_alpha"]["submission_count"] == 0 and a["opening_alpha"]["broker_submission_attempted_count"] == 0
    assert list(a) == ["schema_version", "day", "lanes", "opening_alpha"]
    assert a["lanes"][0]["evaluation_status"] == "NOT_EVALUATED" and a["lanes"][0]["label"] == "Q10 Semiconductor"


def test_fake_artifacts_and_clock(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "datetime", _FakeDT)
    reports = tmp_path / "reports"
    day = "2026-10-30"
    ctl = f"data/logs/controlled_mock_lanes/{day}"
    op = f"data/logs/opening_rank1_controlled_probe/{day}"
    _dump(tmp_path, f"{ctl}/lane_evaluations.json", {"evaluations": [
        {"lane_id": "BTC_WOORI", "status": "INPUT_DELAY", "reason": "q12_candidate_input_stale", "observation_count": 3}]})
    _dump(tmp_path, f"{ctl}/lane_attempts.json", {"attempts": [{"lane_id": "BTC_WOORI", "status": "BROKER_REJECTED"}, {"lane_id": "BTC_WOORI"}]})
    _dump(tmp_path, f"{ctl}/lane_submissions.json", {"submissions": [{"lane_id": "BTC_WOORI", "status": "ACCEPTED"}]})
    _dump(tmp_path, f"{op}/probe_evaluations.json", {"evaluations": [{"eligible": True, "applied": True, "reason": "ok"}, {"reason": "late"}]})
    _dump(tmp_path, f"{op}/probe_submissions.json", {"submissions": [{"run_id": "r1"}, {"run_id": "r2"}]})
    _dump(reports, f"canonical/{day}/r1/executor.json", {"broker_outcome": "REJECTED", "submission_attempts": 1})
    a, b = _both(reports, day)
    assert a == b
    btc = a["lanes"][2]
    assert btc["evaluation_status"] == "WINDOW_CLOSED" and btc["attempt_count"] == 2 and btc["submission_count"] == 1
    assert btc["attempt_status_counts"] == {"BROKER_REJECTED": 1, "UNKNOWN": 1} and btc["latest_submission_status"] == "ACCEPTED"
    oa = a["opening_alpha"]
    assert oa["evaluation_count"] == 2 and oa["eligible_count"] == 1 and oa["applied_count"] == 1 and oa["submission_count"] == 2
    assert oa["broker_submission_attempted_count"] == 1 and oa["broker_outcome_counts"] == {"REJECTED": 1, "UNKNOWN_ARTIFACT": 1}
    assert oa["reason_counts"] == {"late": 1, "ok": 1}


def test_facade_helper_seams(monkeypatch, tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    monkeypatch.setattr(m, "_display_evaluation_status", lambda **kw: ("SEAM", kw["lane_id"]))
    a, b = _both(reports, "2026-10-30")
    assert a == b and a["lanes"][1]["evaluation_status"] == "SEAM" and a["lanes"][1]["reason"] == "Q10_INDEX"
    monkeypatch.undo()
    monkeypatch.setattr(m, "LANE_LABELS", {"BTC_WOORI": "b", "Q10_SEMICONDUCTOR": "s", "Q10_INDEX": "i"})
    a, b = _both(reports, "2026-10-30")
    assert a == b and [r["label"] for r in a["lanes"]] == ["s", "i", "b"]


def test_keyword_only():
    with pytest.raises(TypeError):
        m.build_controlled_validation_daily("x", "d")
