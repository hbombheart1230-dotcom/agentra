"""RF-034 C3: immediate_opening runtime_validation threshold boundaries and fixed-window rules (tmp root)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from libs.reporting.alpha_research_board import runtime_validation as rvm

DAYS = ["2026-08-24", "2026-08-25", "2026-08-26", "2026-08-27", "2026-08-28"]


def w(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")


def ep(day, symbol, ret, *, eligible=True, asset="common_stock", kospi=0.5):
    return {"day": day, "symbol": symbol, "decision_epoch": 1,
            "opening_observability": {"conditional_lanes": {"IMMEDIATE_OPENING_PROBE": {"eligible": eligible}}, "asset_observation": {"asset_class": asset} if asset else {}, "market_snapshot": {"kospi_pct": kospi}},
            "checkpoints": {"+5m": {"live_net_return_pct": ret}}}


def build(tmp_path, episodes, *, days=DAYS, statuses=None, through="2026-08-31", cumulative=True):
    root = tmp_path / "reports"
    for d in days:
        w(root / "evaluation/opening_rank1_shadow" / d / "opening_rank1_shadow_daily.json", {"day_status": (statuses or {}).get(d, "VALID")})
    if cumulative:
        w(root / "evaluation/opening_rank1_shadow/opening_rank1_shadow_cumulative.json", {"episodes": episodes})
    return rvm.build_immediate_opening_runtime_validation(reports_root=root, through_day=through)


def good(n=10, **kw):
    out = []
    for i in range(n):
        out.append(ep(DAYS[i % 5], f"S{i}", 0.8 if i % 4 else -0.4, **kw))
    return out


def test_baseline_good_fixture_passes_with_all_checks_true(tmp_path):
    out = build(tmp_path, good())
    assert out["decision"] == "PASS_RUNTIME_VALIDATION" and all(out["checks"].values()) and out["behavior_change_authorized"] is False
    assert out["window_complete"] is True and out["remaining_session_count"] == 0 and out["observed_session_count"] == 5


def test_window_filter_excludes_contract_date_and_future_and_keeps_first_five(tmp_path):
    days = ["2026-08-21", *DAYS, "2026-08-31", "2026-09-30"]
    out = build(tmp_path, good(), days=days, through="2026-08-31")
    assert [s["day"] for s in out["sessions"]] == DAYS                                   # contract date excluded; only first 5 fixed
    short = build(tmp_path / "s", good(), days=DAYS[:3])
    assert short["decision"] == "COLLECTING" and short["remaining_session_count"] == 2 and "3세션" in short["rationale"]
    early = build(tmp_path / "e", good(), through="2026-08-26")
    assert early["observed_session_count"] == 3 and early["decision"] == "COLLECTING"            # through_day inclusive bound


@pytest.mark.parametrize("status,ok", [("VALID", True), ("NO_OPENING_RANK1", True), ("VALID_NO_EPISODES", True), ("FORWARD_INCOMPLETE", False), ("MISSING", False)])
def test_session_status_whitelist(tmp_path, status, ok):
    out = build(tmp_path, good(), statuses={DAYS[2]: status})
    assert (out["decision"] == "FAIL_RUNTIME_INTEGRITY") is (not ok) and bool(out["checks"]["session_integrity"]) is ok


def test_corrupt_daily_or_cumulative_source_fails_integrity(tmp_path):
    root = tmp_path / "reports"
    for d in DAYS:
        w(root / "evaluation/opening_rank1_shadow" / d / "opening_rank1_shadow_daily.json", {"day_status": "VALID"})
    w(root / "evaluation/opening_rank1_shadow" / DAYS[0] / "opening_rank1_shadow_daily.json", "{bad")
    w(root / "evaluation/opening_rank1_shadow/opening_rank1_shadow_cumulative.json", {"episodes": good()})
    out = rvm.build_immediate_opening_runtime_validation(reports_root=root, through_day="2026-08-31")
    assert out["decision"] == "FAIL_RUNTIME_INTEGRITY" and out["invalid_sessions"][0]["source_error"].startswith("INVALID_ARTIFACT")
    missing = build(tmp_path / "m", good(), cumulative=False)
    assert missing["decision"] == "FAIL_RUNTIME_INTEGRITY" and "누적 source" in missing["rationale"]


def test_minimum_episode_count_boundary(tmp_path):
    assert build(tmp_path / "a", good(4))["decision"] == "INSUFFICIENT_RUNTIME_SAMPLE"
    assert build(tmp_path / "b", good(5))["checks"]["minimum_episode_count"] is True


def test_episodes_outside_fixed_days_or_ineligible_are_ignored_and_forward_coverage(tmp_path):
    eps = good(10) + [ep("2026-08-31", "OUT", 9.0), ep(DAYS[0], "NOTELIG", 9.0, eligible=False)]
    out = build(tmp_path, eps)
    assert out["eligible_episode_count"] == 10 and out["metrics"]["sample_count"] == 10 and out["coverage"]["forward"] == 1.0
    # 10 eligible, 9 with +5m -> 0.9 (inclusive) ; 8 -> 0.8 fails
    def with_missing(n_missing):
        e = good(10)
        for i in range(n_missing):
            e[i]["checkpoints"]["+5m"]["live_net_return_pct"] = None
        return e

    nine = build(tmp_path / "n", with_missing(1))
    assert nine["coverage"]["forward"] == 0.9 and nine["checks"]["forward_coverage"] is True
    eight = build(tmp_path / "e8", with_missing(2))
    assert eight["coverage"]["forward"] == 0.8 and eight["decision"] == "FAIL_RUNTIME_INTEGRITY"
    assert build(tmp_path / "z", [])["coverage"]["forward"] == 1.0                           # no eligible -> vacuous 1.0


def test_metadata_coverage_boundaries_0_80_inclusive(tmp_path):
    def mix(n_unknown_asset, n_no_market):
        e = good(10)
        for i in range(n_unknown_asset):
            e[i]["opening_observability"]["asset_observation"] = {}
        for i in range(n_no_market):
            e[i]["opening_observability"]["market_snapshot"] = {"kospi_pct": None}
        return e

    ok = build(tmp_path / "ok", mix(2, 2))
    assert ok["coverage"]["asset_metadata"] == 0.8 and ok["coverage"]["market_metadata"] == 0.8 and ok["checks"]["asset_metadata"] and ok["checks"]["market_metadata"]
    assert build(tmp_path / "a", mix(3, 0))["decision"] == "FAIL_RUNTIME_INTEGRITY"
    assert build(tmp_path / "m", mix(0, 3))["decision"] == "FAIL_RUNTIME_INTEGRITY"
    assert build(tmp_path / "zero", [])["coverage"]["asset_metadata"] == 0.0


def test_win_rate_boundary_0_55_inclusive_and_pf_threshold(tmp_path):
    def rows(wins, losses, win=1.0, loss=-0.5):
        e = [ep(DAYS[i % 5], f"W{i}", win) for i in range(wins)] + [ep(DAYS[i % 5], f"L{i}", loss) for i in range(losses)]
        return e

    ok = build(tmp_path / "ok", rows(11, 9))                             # 0.55
    assert ok["metrics"]["win_rate"] == 0.55 and ok["checks"]["win_rate"] is True
    bad = build(tmp_path / "bad", rows(10, 10))                           # 0.50
    assert bad["checks"]["win_rate"] is False and bad["decision"] == "FAIL_RUNTIME_EFFECT"
    pf_ok = build(tmp_path / "pf", rows(11, 9, win=0.12, loss=-0.1))        # PF 1.32 passes
    assert pf_ok["checks"]["profit_factor"] is True
    pf_fail = build(tmp_path / "pf3", rows(11, 9, win=0.1, loss=-0.1) + [ep(DAYS[0], "X", -0.05)])          # PF 1.1/0.95 < 1.2
    assert pf_fail["checks"]["profit_factor"] is False


def test_symbol_concentration_boundary_0_40_inclusive(tmp_path):
    def conc(n_same):
        e = [ep(DAYS[i % 5], "SAME" if i < n_same else f"S{i}", 0.8 if i % 4 else -0.4) for i in range(10)]
        return e

    ok = build(tmp_path / "ok", conc(4))
    assert ok["largest_symbol_share"] == 0.4 and ok["checks"]["symbol_concentration"] is True
    bad = build(tmp_path / "bad", conc(5))
    assert bad["largest_symbol_share"] == 0.5 and bad["checks"]["symbol_concentration"] is False and bad["decision"] == "FAIL_RUNTIME_EFFECT"
    assert build(tmp_path / "none", [])["largest_symbol_share"] is None


def test_median_must_be_strictly_positive(tmp_path):
    # mean>0 via a large outlier but median negative
    e = [ep(DAYS[i % 5], f"S{i}", -0.1) for i in range(6)] + [ep(DAYS[i % 5], f"B{i}", 5.0) for i in range(4)]
    out = build(tmp_path, e)
    assert out["checks"]["average_return"] is True and out["checks"]["median_return"] is False and out["decision"] == "FAIL_RUNTIME_EFFECT"


def test_render_lists_sessions_and_handles_empty(tmp_path):
    out = build(tmp_path, good())
    md = rvm.render_immediate_opening_runtime_validation(out)
    assert md.startswith("# Immediate Opening Probe Runtime Validation") and "PASS_RUNTIME_VALIDATION" in md and f"| {DAYS[0]} | `VALID` | `-` |" in md
    assert "- 세션: 0 / 5" in rvm.render_immediate_opening_runtime_validation({})


def test_symbol_concentration_threshold_is_40_not_45_pct(tmp_path):
    e = [ep(DAYS[i % 5], "SAME" if i < 5 else f"S{i}", 0.8 if i % 4 else -0.4) for i in range(12)]          # 5/12 = 0.4167
    out = build(tmp_path, e)
    assert out["largest_symbol_share"] == 0.4167 and out["checks"]["symbol_concentration"] is False


def test_median_exactly_zero_fails(tmp_path):
    e = [ep(DAYS[i % 5], f"Z{i}", 0.0) for i in range(5)] + [ep(DAYS[i % 5], f"P{i}", 2.0) for i in range(5, 9)] + [ep(DAYS[0], "N0", -0.5)]
    out = build(tmp_path, e)
    assert out["checks"]["average_return"] is True and out["checks"]["median_return"] is False
