"""RF-054 libs/performance/strategy_memory C2/C3, tmp reports root only.

Env switch ``STRATEGY_MEMORY_PERSIST_ENABLED`` is set through monkeypatch; no
operational reports tree is read or written. Explicit raises keep the checks
live under ``python -O``.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from libs.performance import performance_aggregator as pa
from libs.performance import strategy_memory as sm

DAY = "2026-10-28"


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


@pytest.fixture(autouse=True)
def _persist_on(monkeypatch):
    monkeypatch.delenv("STRATEGY_MEMORY_PERSIST_ENABLED", raising=False)


def _bundle(root: Path, day: str, trade: str, ret: float, playbook: str, regime: str = ""):
    d = root / "trades" / day / trade
    d.mkdir(parents=True, exist_ok=True)
    summ = {"playbook": playbook}
    if regime:
        summ["market_regime"] = regime
    (d / "lifecycle_bundle.json").write_text(json.dumps({"day": day, "trade_id": trade, "symbol": "s" + trade,
                                                         "trade_outcome": {"return_pct": ret}, "strategist_summary": summ}), encoding="utf-8")


def _root(tmp_path, day=DAY):
    root = tmp_path / "reports"
    _bundle(root, day, "a1", 2.0, "alpha", "bull")
    _bundle(root, day, "a2", 1.0, "alpha", "bull")
    _bundle(root, day, "b1", -1.0, "beta", "bear")
    _bundle(root, day, "b2", -2.0, "beta", "bear")
    _bundle(root, day, "u1", 5.0, "")   # unknown playbook never qualifies
    return root


def test_top_counter_keys_and_list_unique_helpers():
    _eq(sm._top_counter_keys({"b": 2, "a": 2, "c": "x", "": 9, "d": 5}, limit=3), ["d", "a", "b"])
    _eq(sm._top_counter_keys("notdict"), [])
    _eq(sm._top_counter_keys({"a": 1}, limit=0), ["a"])  # limit floors at 1
    _eq(sm._list_unique([" a ", "a", "", None, "b"], limit=8), ["a", "b"])
    _eq(sm._list_unique(["a", "b", "c"], limit=2), ["a", "b"])


def test_build_memory_buckets_are_evidence_qualified_and_exclusive():
    playbooks = {
        "alpha": {"usage_count": 3, "win_rate": 0.8, "avg_return": 1.5, "stability_score": 0.9},
        "beta": {"usage_count": 2, "win_rate": 0.0, "avg_return": -1.5, "stability_score": 0.2},
        "solo": {"usage_count": 1, "win_rate": 1.0, "avg_return": 9.0, "stability_score": 0.99},   # < 2 uses
        "unknown": {"usage_count": 9, "win_rate": 1.0, "avg_return": 9.0, "stability_score": 1.0},
        "mid": {"usage_count": 4, "win_rate": 0.45, "avg_return": 0.1, "stability_score": 0.5},    # neither best nor worst
    }
    m = sm.build_strategy_memory({}, {"playbooks": playbooks})
    _eq((m["best_playbooks"], m["worst_playbooks"]), (["alpha"], ["beta"]))
    # Quirk pinned: recent_* patterns have no usage_count / "unknown" filter (unlike best/worst), so an
    # "unknown" playbook and a single-use one can appear in recent_success_patterns.
    _eq(m["recent_success_patterns"], ["playbook:unknown", "playbook:solo", "playbook:alpha"])
    _eq(m["recent_failures"], ["playbook:beta"])
    _eq((m["schema_version"], m["advisory_only"], m["reporter_analysis_digest"]), ("strategy_memory.v1", True, {}))
    _eq(list(m["playbook_performance_snapshot"]), ["unknown", "solo", "alpha", "mid"])  # stability-sorted (1.0, 0.99, 0.9, 0.5), top 4
    # one playbook can never be both best and worst
    one = sm.build_strategy_memory({}, {"playbooks": {"x": {"usage_count": 5, "win_rate": 0.5, "avg_return": 0.0, "stability_score": 0.5}}})
    _eq((one["best_playbooks"], one["worst_playbooks"]), (["x"], []))


def test_recent_pattern_selection_thresholds():
    pb = {"w": {"win_rate": 0.5, "avg_return": 0.0, "stability_score": 0.1}, "l1": {"win_rate": 0.4, "avg_return": 1.0, "stability_score": 0.2},
          "l2": {"win_rate": 0.9, "avg_return": -0.1, "stability_score": 0.3}, "ok": {"win_rate": 0.45, "avg_return": 0.5, "stability_score": 0.4}}
    _eq(sorted(sm._recent_patterns_from_playbooks(pb, success=True)), ["w"])
    _eq(sorted(sm._recent_patterns_from_playbooks(pb, success=False)), ["l1", "l2"])


def test_pattern_snapshot_ranks_labels_and_skips_unknown():
    summary = {
        "per_entry_pattern_stats": {"breakout": {"trade_count": 3, "win_rate": 0.7, "avg_return": 1.0}, "unknown": {"trade_count": 9, "win_rate": 0.0, "avg_return": -5.0}},
        "per_exit_pattern_stats": {"stop": {"trade_count": 2, "win_rate": 0.0, "avg_return": -2.0}, "target": {"trade_count": 0, "win_rate": 1.0, "avg_return": 3.0}},
        "per_entry_exit_combo_stats": {"breakout -> stop": {"trade_count": 2, "win_rate": 0.0, "avg_return": -2.0}, "unknown -> stop": {"trade_count": 5, "win_rate": 0.0, "avg_return": -1.0}},
    }
    snap = sm._build_pattern_performance_snapshot(summary)
    _eq(snap["problem_patterns"], ["entry_exit:breakout->stop", "exit:stop"])
    _eq(snap["working_patterns"], ["entry:breakout"])
    _eq(snap["advisory_only"], True)
    _eq(list(snap["entry_pattern_types"]), ["unknown", "breakout"])  # sorted by trade_count desc
    _eq(sm._build_pattern_performance_snapshot({})["problem_patterns"], [])


def test_write_strategy_memory_end_to_end_on_tmp_root(tmp_path):
    root = _root(tmp_path)
    m = sm.write_strategy_memory(root, day=DAY)
    _eq((m["status"], m["directional_bias_usable"], m["best_playbooks"], m["worst_playbooks"]), ("ok", True, ["alpha"], ["beta"]))
    p = pa.performance_artifact_paths(root, DAY)["strategy_memory_json"]
    _eq(m["artifact_path"], str(p))
    _eq(json.loads(p.read_text(encoding="utf-8"))["day"], DAY)
    # missing reporter analysis is explicit, not silent
    _eq((m["reporter_analysis_digest"]["available"], m["reporter_analysis_digest"]["status"]), (False, "missing"))
    # Quirk pinned: the "unknown" regime (u1 has no regime, avg 5.0) takes one of the two slots BEFORE being
    # filtered out, so only one preferred regime survives, and "bull" also shows up in avoid_regimes.
    _eq(m["market_condition_bias"]["preferred_regimes"], ["bull"])
    _eq(m["market_condition_bias"]["avoid_regimes"], ["bear", "bull"])
    if (root / "performance" / DAY / "playbook_stats.json").exists() is False:
        raise AssertionError("playbook stats are written when none were supplied")


def test_empty_root_status_is_ok_but_bias_not_usable(tmp_path):
    m = sm.write_strategy_memory(tmp_path / "reports", day=DAY)
    # Quirk pinned: status is "ok" even with zero trades, because the always-populated
    # pattern_performance_snapshot counts as "directional evidence"; directional_bias_usable is the honest flag.
    _eq((m["status"], m["directional_bias_usable"], m["best_playbooks"], m["worst_playbooks"]), ("ok", False, [], []))
    _eq(sm._memory_has_directional_evidence({"best_playbooks": [], "pattern_performance_snapshot": {"advisory_only": True}}), True)
    _eq(sm._memory_has_directional_evidence({}), False)
    _eq(sm._memory_has_directional_evidence("x"), False)


@pytest.mark.parametrize("val", ["0", "false", "No", "n", "OFF", " off "])
def test_persist_disabled_writes_nothing_and_sync_is_skipped(tmp_path, monkeypatch, val):
    monkeypatch.setenv("STRATEGY_MEMORY_PERSIST_ENABLED", val)
    root = _root(tmp_path)
    m = sm.write_strategy_memory(root, day=DAY)
    _eq((m["status"], m["disabled_reason"], m["day"]), ("disabled", "strategy_memory_persist_disabled_by_env", DAY))
    s = sm.sync_strategy_memory_artifacts(root, day=DAY)
    _eq((s["status"], s["reason"], s["schema_version"]), ("skipped", "strategy_memory_persist_disabled_by_env", "strategy_memory_sync.v1"))
    _eq((root / "performance").exists(), False)


def test_sync_missing_day_ok_path_and_error_path(tmp_path, monkeypatch):
    root = _root(tmp_path)
    _eq(sm.sync_strategy_memory_artifacts(root, day="  ")["reason"], "missing_day")
    out = sm.sync_strategy_memory_artifacts(root, day=DAY, source="unit")
    _eq((out["status"], out["source"], out["total_trades"], out["playbook_count"], out["strategy_memory_status"]), ("ok", "unit", 5, 3, "ok"))
    _eq(sorted(Path(v).name for v in out["artifacts"].values()), ["playbook_stats.json", "strategy_memory.json", "summary.json", "symbol_stats.json"])
    _eq(sorted(x.name for x in (root / "performance" / DAY).iterdir()), ["playbook_stats.json", "strategy_memory.json", "summary.json", "symbol_stats.json"])
    monkeypatch.setattr(sm, "write_playbook_stats", lambda *a, **k: (_ for _ in ()).throw(OSError("disk full")))
    err = sm.sync_strategy_memory_artifacts(root, day=DAY)
    _eq((err["status"], err["reason"]), ("error", "disk full"))   # swallowed into a status, not raised


def test_reporter_digest_with_route_mix(tmp_path):
    root = tmp_path / "reports"
    ra = root / "dev" / "analysis" / "reporter_analysis"
    ra.mkdir(parents=True)
    te = root / "trade_explain.json"
    te.write_text(json.dumps({"route_summary": {"route_selected_total": {"monitor_only": 3, "full_cycle": 1, "x": "bad"}, "route_source": "events"}}), encoding="utf-8")
    (ra / f"reporter_analysis_{DAY}.json").write_text(json.dumps({
        "ai_run_grade": "B", "ai_summary": "s" * 400, "ai_improvement_suggestions": ["i1", "", "i2", "i3", "i4"],
        "report_focus_targets": ["t1", " ", "t2", "t3", "t4", "t5"], "source_reports": {"trade_explain_json": "trade_explain.json"},
        "operator_facing_summary": {"system_health": " green ", "recommended_actions": ["r1", "r2", "r3", "r4"]},
        "monitor_evaluation": {"monitor_status": "ok", "monitor_reason_top": {"a": 2, "b": 5}},
        "incident_postmortem": {"incident_total": "2"}}), encoding="utf-8")
    d = sm._load_reporter_analysis_digest(root, DAY)
    _eq((d["available"], d["ai_run_grade"], len(d["ai_summary"]), d["top_improvement_suggestions"]), (True, "B", 280, ["i1", "i2", "i3"]))
    _eq((d["recommended_actions"], d["report_focus_targets"], d["system_health"], d["incident_total"]), (["r1", "r2", "r3"], ["t1", "t2", "t3", "t4"], "green", 2))
    _eq(d["top_monitor_reasons"], ["b", "a"])
    _eq(d["route_mix"], {"route_selected_total": {"monitor_only": 3, "full_cycle": 1, "x": 0}, "monitor_only_ratio": 0.75,
                         "cached_strategist_ratio": 0.0, "full_cycle_ratio": 0.25, "route_source": "events"})


def test_load_hint_empty_current_stale_fallback_and_auto_build(tmp_path):
    root = _root(tmp_path)
    empty = sm.load_strategy_memory_hint(reports_root=tmp_path / "nothing")
    _eq((empty["status"], empty["day"], empty["best_playbooks"]), ("empty", "", []))
    sm.write_strategy_memory(root, day=DAY)
    cur = sm.load_strategy_memory_hint(reports_root=root, day=DAY)
    _eq((cur["status"], cur["freshness_status"], cur["age_days"], cur["day"], cur["best_playbooks"]), ("ok", "current", 0, DAY, ["alpha"]))
    # a later requested day with no memory falls back to the latest usable earlier day and is marked stale
    stale = sm.load_strategy_memory_hint(reports_root=root, day="2026-11-02")
    _eq((stale["resolved_day"], stale["requested_day"], stale["freshness_status"], stale["age_days"], stale["day"]), (DAY, "2026-11-02", "stale", 5, DAY))
    # a day before any usable memory has no fallback -> empty-memory shell
    early = sm.load_strategy_memory_hint(reports_root=root, day="2026-01-01")
    _eq((early["status"], early["best_playbooks"], early["freshness_status"]), ("empty", [], "current"))
    # auto_build creates the artifacts for a day that had none
    other = root / "trades" / "2026-10-30" / "z1"
    _bundle(root, "2026-10-30", "z1", 1.0, "gamma")
    _bundle(root, "2026-10-30", "z2", 2.0, "gamma")
    built = sm.load_strategy_memory_hint(reports_root=root, day="2026-10-30", auto_build=True)
    _eq((built["day"], built["freshness_status"]), ("2026-10-30", "current"))
    _eq(sorted(x.name for x in (root / "performance" / "2026-10-30").iterdir()), ["playbook_stats.json", "summary.json", "symbol_stats.json"])
    _eq(sm._resolve_latest_day(root / "performance"), "2026-10-30")
    _eq(sm._resolve_latest_usable_day(root / "performance", at_or_before="2026-10-29"), DAY)
