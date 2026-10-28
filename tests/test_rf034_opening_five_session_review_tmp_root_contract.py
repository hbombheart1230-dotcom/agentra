"""RF-034 C3: opening_rank1_shadow.five_session_review decision ladder, session filtering and tmp-root write contract."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from libs.reporting.opening_rank1_shadow import five_session_review as fs

LANES = ("IMMEDIATE_OPENING_PROBE", "CONFIRMED_RECURRENT_RANK", "DISLOCATION_REBOUND")


def _summary(**per_lane):
    """per_lane: lane -> (eligible_count, avg_return, metric_count)."""
    out = {}
    for lane, (count, avg, mcount) in per_lane.items():
        horizon = fs.LANE_HORIZONS[lane]
        out[lane] = {"eligible_episode_count": count, "horizons": {horizon: {"live_net": {"average_return_pct": avg, "count": mcount}}}}
    return {"conditional_lane_summaries": out}


def _eval(through, summary, sessions=(), latent=None):
    return fs.evaluate_five_session_review(through_day=through, cumulative_summary=summary, session_rows=list(sessions), latent_summary=latent or {})


def test_constants_are_pinned():
    assert (fs.WINDOW_START, fs.WINDOW_END, fs.REQUIRED_SESSIONS, fs.MINIMUM_NEW_EPISODES) == ("2026-08-03", "2026-08-07", 5, 5)
    assert fs.LANE_HORIZONS == {"IMMEDIATE_OPENING_PROBE": "+15m", "CONFIRMED_RECURRENT_RANK": "+30m", "DISLOCATION_REBOUND": "+60m"}


def test_window_open_is_collecting_and_selects_nothing_even_if_positive():
    s = _summary(CONFIRMED_RECURRENT_RANK=(99, 5.0, 99))
    out = _eval("2026-08-06", s)
    assert out["status"] == "COLLECTING" and out["selected_behavior_candidate"] == "NONE" and out["window"]["window_closed"] is False
    assert {r["outcome"] for r in out["lane_results"].values()} == {"COLLECTING"}


def test_window_closes_exactly_on_end_day_boundary():
    s = _summary(CONFIRMED_RECURRENT_RANK=(5, 0.1, 5))
    assert _eval("2026-08-06", s)["window"]["window_closed"] is False
    out = _eval("2026-08-07", s)
    assert out["window"]["window_closed"] is True and out["status"] == "SELECT_BEHAVIOR_CANDIDATE"
    assert out["selected_behavior_candidate"] == "CONFIRMED_RECURRENT_RANK_PRESERVATION"
    assert _eval("2026-09-30", s)["status"] == "SELECT_BEHAVIOR_CANDIDATE"                 # stays closed, no extension
    assert out["window"]["no_extension"] is True


@pytest.mark.parametrize("count,avg,expected", [
    (4, 9.0, "RETAIN_LANE_SHADOW_ONLY"),                       # below minimum episodes regardless of return
    (5, 0.0001, "HISTORICAL_DIRECTION_CONFIRMED_SHADOW_ONLY"),
    (5, 0.0, "REJECT_CANDIDATE"),                              # zero is not positive
    (12, -1.0, "REJECT_CANDIDATE"),
])
def test_lane_outcome_ladder(count, avg, expected):
    out = _eval("2026-08-07", _summary(CONFIRMED_RECURRENT_RANK=(count, avg, count)))
    assert out["lane_results"]["CONFIRMED_RECURRENT_RANK"]["outcome"] == expected


def test_only_recurrent_lane_can_become_the_behavior_candidate():
    s = _summary(IMMEDIATE_OPENING_PROBE=(50, 9.0, 50), DISLOCATION_REBOUND=(50, 9.0, 50), CONFIRMED_RECURRENT_RANK=(50, -1.0, 50))
    out = _eval("2026-08-07", s)
    assert out["lane_results"]["IMMEDIATE_OPENING_PROBE"]["outcome"] == "HISTORICAL_DIRECTION_CONFIRMED_SHADOW_ONLY"
    assert out["status"] == "CLOSED_NO_BEHAVIOR_CANDIDATE" and out["selected_behavior_candidate"] == "NONE"
    assert out["behavior_change_authorized"] is False and out["behavior_candidate_scope"] == "CONFIRMED_RECURRENT_RANK_ONLY"


def test_missing_lane_data_defaults_and_average_none_without_metrics():
    out = _eval("2026-08-07", {})
    for lane in LANES:
        r = out["lane_results"][lane]
        assert r["eligible_episode_count"] == 0 and r["average_net_return_pct"] is None and r["outcome"] == "RETAIN_LANE_SHADOW_ONLY"
        assert r["primary_horizon"] == fs.LANE_HORIZONS[lane] and r["minimum_episode_count"] == 5
    out = _eval("2026-08-07", _summary(CONFIRMED_RECURRENT_RANK=(7, 0.5, 0)))             # avg present but metric count 0 -> None
    assert out["lane_results"]["CONFIRMED_RECURRENT_RANK"]["average_net_return_pct"] is None


def test_invalid_days_session_count_and_latent_passthrough():
    sessions = [{"day": "2026-08-03", "status": "VALID"}, {"day": "2026-08-04", "status": "MISSING"}, {"day": "2026-08-05", "status": "BAD"}]
    out = _eval("2026-08-07", {}, sessions, {"watch_count": "3", "signal_evidence_count": None})
    assert out["invalid_artifact_days"] == ["2026-08-04", "2026-08-05"] and out["window"]["observed_session_count"] == 3
    assert out["latent_watch"] == {"watch_count": 3, "signal_evidence_count": 0, "outcome": "RETAIN_SHADOW_ONLY",
                                   "reason": "fresh-trigger forward outcomes are not yet part of the live watch contract"}


def _daily(root: Path, day: str, payload):
    p = root / day / "opening_rank1_shadow_daily.json"
    p.parent.mkdir(parents=True)
    p.write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")


def test_session_statuses_filter_window_and_fail_soft(tmp_path):
    _daily(tmp_path, "2026-08-02", {"day_status": "VALID"})                               # before window
    _daily(tmp_path, "2026-08-03", {"day_status": "VALID", "summary": {"episode_count": "4"}})
    _daily(tmp_path, "2026-08-04", {"summary": None})                                    # no status -> MISSING
    _daily(tmp_path, "2026-08-05", "{corrupt")                                           # unreadable -> MISSING
    _daily(tmp_path, "2026-08-06", [1])                                                  # non-object -> MISSING
    _daily(tmp_path, "2026-08-08", {"day_status": "VALID"})                              # after window end
    (tmp_path / "notes").mkdir()
    rows = fs._session_statuses(tmp_path, "2026-08-30")
    assert [(r["day"], r["status"], r["episode_count"]) for r in rows] == [
        ("2026-08-03", "VALID", 4), ("2026-08-04", "MISSING", 0), ("2026-08-05", "MISSING", 0), ("2026-08-06", "MISSING", 0)]
    # through_day earlier than window end truncates
    assert [r["day"] for r in fs._session_statuses(tmp_path, "2026-08-03")] == ["2026-08-03"]
    assert fs._session_statuses(tmp_path / "nope", "2026-08-30") == []


def test_build_writes_only_review_dir_and_matches_payload(tmp_path):
    root = tmp_path / "opening"
    _daily(root, "2026-08-03", {"day_status": "VALID", "summary": {"episode_count": 2}})
    before = {p for p in tmp_path.rglob("*") if p.is_file()}
    cum = _summary(CONFIRMED_RECURRENT_RANK=(6, 0.4, 6))
    res = fs.build_five_session_review(opening_output_root=root, through_day="2026-08-07", cumulative_summary=cum, latent_summary={"watch_count": 1})
    jp, mp = Path(res["json"]), Path(res["markdown"])
    assert jp == root / "five_session_review" / "opening_alpha_five_session_review.json"
    assert mp == root / "five_session_review" / "opening_alpha_five_session_review.md"
    assert {p for p in tmp_path.rglob("*") if p.is_file()} - before == {jp, mp}
    payload = json.loads(jp.read_text(encoding="utf-8"))
    assert payload["status"] == "SELECT_BEHAVIOR_CANDIDATE" and payload["window"]["observed_session_count"] == 1
    md = mp.read_text(encoding="utf-8")
    assert md.startswith("# Opening Alpha Five-Session Review") and "CONFIRMED_RECURRENT_RANK | +30m | 6 | +0.4000% |" in md
    assert "Behavior change authorized by this report: **false**" in md
    empty = fs._render_markdown({})                                                       # renders without data, no lane rows
    assert "- Status: **None**" in empty and "| Lane | Horizon |" in empty and "CONFIRMED_RECURRENT_RANK |" not in empty
