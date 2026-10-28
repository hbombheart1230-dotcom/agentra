"""RF-054 libs/performance C2/C3: aggregator and playbook stats, tmp reports root only.

Builds ``reports/trades/<day>/<trade>/lifecycle_bundle.json`` fixtures under
tmp_path; ``strategy_memory`` is not exercised here. Explicit raises keep the
checks live under ``python -O``.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import libs.performance as perf
from libs.performance import performance_aggregator as pa
from libs.performance import playbook_stats as ps


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def _bundle(root: Path, day: str, trade: str, **fields):
    d = root / "trades" / day / trade
    d.mkdir(parents=True, exist_ok=True)
    (d / "lifecycle_bundle.json").write_text(json.dumps({"day": day, "trade_id": trade, **fields}), encoding="utf-8")
    return d


def _fixture(tmp_path):
    root = tmp_path / "reports"
    _bundle(root, "2026-10-27", "t1", symbol="aaa", trade_outcome={"return_pct": 2.0},
            strategist_summary={"playbook": " Breakout ", "market_regime": "Bull"})
    _bundle(root, "2026-10-28", "t2", symbol="bbb", trade_outcome={"return_pct": -1.0},
            strategist_summary={"playbook": "breakout", "regime": "bear"})
    _bundle(root, "2026-10-28", "t3", symbol="ccc", summary={"realized_pnl": 4.0})  # pnl only, no playbook
    _bundle(root, "2026-10-28", "t4")  # nothing usable
    bad = root / "trades" / "2026-10-28" / "t5"
    bad.mkdir(parents=True)
    (bad / "lifecycle_bundle.json").write_text("{bad", encoding="utf-8")
    (root / "trades" / "2026-10-28" / "t6").mkdir()
    (root / "trades" / "2026-10-28" / "t6" / "lifecycle_bundle.json").write_text("[1]", encoding="utf-8")
    return root


def test_package_exports_pinned():
    _eq(perf.__all__, ["aggregate_performance_from_bundles", "aggregate_performance_from_reports_root", "write_performance_summary",
                       "calculate_playbook_stats", "write_playbook_stats", "build_strategy_memory", "load_strategy_memory_hint",
                       "sync_strategy_memory_artifacts", "write_strategy_memory"])
    for n in perf.__all__:
        if not callable(getattr(perf, n)):
            raise AssertionError(n)


def test_load_bundles_day_filter_skips_corrupt_and_non_dict(tmp_path):
    root = _fixture(tmp_path)
    all_rows = pa.load_lifecycle_bundles(root)
    _eq(sorted(b["trade_id"] for b in all_rows), ["t1", "t2", "t3", "t4"])
    _eq(sorted(b["trade_id"] for b in pa.load_lifecycle_bundles(root, day="2026-10-28")), ["t2", "t3", "t4"])
    _eq(pa.load_lifecycle_bundles(root, day="2000-01-01"), [])
    _eq(pa.load_lifecycle_bundles(tmp_path / "nowhere"), [])
    if not all(b["_bundle_path"].endswith("lifecycle_bundle.json") for b in all_rows):
        raise AssertionError("_bundle_path must be recorded")


def test_summary_numbers_for_mixed_bundles(tmp_path):
    root = _fixture(tmp_path)
    s = pa.aggregate_performance_from_reports_root(root)
    _eq((s["schema_version"], s["day"], s["total_trades"]), ("performance_summary.v1", "2026-10-28", 4))
    # returns: t1=2.0, t2=-1.0, t3 falls back to pnl 4.0, t4 unavailable
    _eq((s["return_sample_count"], s["unavailable_return_count"]), (3, 1))
    _eq((s["win_rate"], s["avg_return"], s["avg_win"], s["avg_loss"]), (round(2 / 3, 6), round(5 / 3, 6), 3.0, -1.0))
    _eq((s["profit_factor"], s["max_drawdown"]), (6.0, 1.0))
    _eq(sorted(s["per_playbook_stats"]), ["breakout", "unknown"])
    _eq(s["per_playbook_stats"]["breakout"]["trade_count"], 2)
    _eq(s["per_playbook_stats"]["breakout"]["symbols"], ["AAA", "BBB"])
    _eq(sorted(s["per_market_regime_stats"]), ["bear", "bull", "unknown"])
    _eq(s["source"], {"bundle_count": 4, "reports_root": str(root)})
    _eq([r["trade_id"] for r in s["trade_rows"]], [b["trade_id"] for b in pa.load_lifecycle_bundles(root)])


def test_day_defaults_and_explicit_day_and_empty_input():
    e = pa.aggregate_performance_from_bundles([])
    _eq((e["total_trades"], e["win_rate"], e["profit_factor"], e["max_drawdown"], e["avg_return"]), (0, 0.0, 0.0, 0.0, 0.0))
    _eq(len(e["day"]), 10)
    _eq(pa.aggregate_performance_from_bundles([{"day": "2026-01-02"}, {"day": "2026-01-09"}, "junk"])["day"], "2026-01-09")
    _eq(pa.aggregate_performance_from_bundles([{"day": "2026-01-02"}], day=" 2026-02-02 ")["day"], "2026-02-02")


def test_profit_factor_and_drawdown_helpers():
    _eq(pa._compute_profit_factor([]), 0.0)
    _eq(pa._compute_profit_factor([-1.0]), 0.0)
    _eq(pa._compute_profit_factor([3.0]), 3.0)  # no losses -> gains itself
    _eq(pa._compute_profit_factor([3.0, -1.0, -0.5]), 2.0)
    _eq(pa._compute_max_drawdown([1, -2, 1, -3, 5]), 4.0)
    _eq(pa._compute_max_drawdown([]), 0.0)


def test_truth_surface_overrides_lifecycle_and_distinguishes_observation_only(tmp_path):
    root = tmp_path / "reports"
    d1 = _bundle(root, "2026-10-28", "ta", trade_outcome={"return_pct": 9.0})
    (d1 / "reports").mkdir()
    (d1 / "reports" / "ai_trade_summary_input.json").write_text(json.dumps({"truth_surface": {"pnl": 5.0, "pnl_pct": 1.5, "result_label": "win", "truth_source": "broker"}}), encoding="utf-8")
    d2 = _bundle(root, "2026-10-28", "tb", trade_outcome={"return_pct": 7.0})
    (d2 / "reports").mkdir()
    (d2 / "reports" / "ai_trade_summary_input.json").write_text(json.dumps({"truth_surface": {"pnl_pct": 0.7}}), encoding="utf-8")
    rows = {r["trade_id"]: r for r in pa.aggregate_performance_from_reports_root(root)["trade_rows"]}
    _eq((rows["ta"]["return"], rows["ta"]["pnl"], rows["ta"]["return_basis"]), (1.5, 5.0, "truth_surface_net"))
    # pnl missing -> pct is only an observation: return stays None and the lifecycle 7.0 is NOT used
    _eq((rows["tb"]["return"], rows["tb"]["observed_return"], rows["tb"]["return_basis"]), (None, 0.7, "truth_surface_observation_only"))
    # Quirk pinned as current behaviour: `_truth_input_path_from_bundle` returns ``Path()`` (always truthy) when no
    # truth file exists, so the "no path" early return never fires and the path is reported as ".".
    _eq(pa.extract_truth_outcome_from_bundle({}), {"available": False, "path": "."})
    _eq(pa.aggregate_performance_from_bundles([{"trade_id": "z"}])["trade_rows"][0]["truth_surface_path"], ".")
    _eq(pa.extract_truth_outcome_from_bundle({"_bundle_path": str(d1 / "lifecycle_bundle.json")})["truth_source"], "broker")


def test_write_performance_summary_writes_two_files_only(tmp_path):
    root = _fixture(tmp_path)
    out = pa.write_performance_summary(root, day=" 2026-10-28 ")
    paths = pa.performance_artifact_paths(root, "2026-10-28")
    _eq(sorted(p.name for p in paths["root_dir"].iterdir()), ["summary.json", "symbol_stats.json"])
    _eq(out["artifacts"], {"summary_json": str(paths["summary_json"]), "symbol_stats_json": str(paths["symbol_stats_json"])})
    _eq(json.loads(paths["symbol_stats_json"].read_text(encoding="utf-8"))["schema_version"], "symbol_stats.v1")
    _eq(json.loads(paths["summary_json"].read_text(encoding="utf-8"))["day"], "2026-10-28")
    # an explicit summary is written as given, day overridden by the argument; the caller's dict is copied
    given = {"day": "x", "per_symbol_stats": {"A": {}}}
    out2 = pa.write_performance_summary(root, day="2026-10-29", summary=given)
    _eq((out2["day"], given["day"], "artifacts" in given), ("2026-10-29", "x", False))
    _eq(json.loads(pa.performance_artifact_paths(root, "2026-10-29")["symbol_stats_json"].read_text(encoding="utf-8"))["symbol_stats"], {"A": {}})


def test_write_performance_summary_oserror_propagates(tmp_path, monkeypatch):
    root = _fixture(tmp_path)
    orig = Path.write_text

    def wt(self, *a, **k):
        if self.name == "symbol_stats.json":
            raise OSError("synthetic")
        return orig(self, *a, **k)

    monkeypatch.setattr(Path, "write_text", wt)
    with pytest.raises(OSError):
        pa.write_performance_summary(root, day="2026-10-28")
    if not (pa.performance_artifact_paths(root, "2026-10-28")["summary_json"]).exists():
        raise AssertionError("summary.json is written before symbol_stats.json fails (partial output)")


def test_playbook_stats_ordering_window_and_pnl_as_return_fallback():
    bundles = [
        {"day": "2026-10-02", "trade_id": "b", "trade_outcome": {"return_pct": -1.0}, "strategist_summary": {"playbook": "Alpha"}},
        {"day": "2026-10-01", "trade_id": "a", "trade_outcome": {"realized_return_pct": 2.0}, "strategist_summary": {"playbook": "alpha"}},
        {"day": "2026-10-03", "trade_id": "c", "trade_outcome": {"pnl": 3.0}},   # playbook-stats treats pnl as the return
        {"day": "2026-10-03", "trade_id": "d"},                                    # no return at all
        "junk",
    ]
    out = ps.calculate_playbook_stats(bundles, recent_window=2)
    _eq((out["schema_version"], out["day"], out["recent_window"]), ("playbook_stats.v1", "2026-10-03", 2))
    _eq(sorted(out["playbooks"]), ["alpha", "unknown"])
    a = out["playbooks"]["alpha"]
    _eq((a["usage_count"], a["win_rate"], a["avg_return"], a["recent_performance"], a["drawdown"]), (2, 0.5, 0.5, [2.0, -1.0], 1.0))
    u = out["playbooks"]["unknown"]
    _eq((u["usage_count"], u["win_rate"], u["recent_performance"]), (2, 1.0, [3.0]))
    _eq(ps.calculate_playbook_stats([], recent_window=0)["recent_window"], 1)  # floors at 1


def test_stability_score_bounds_and_monotonic_inputs():
    f = ps._stability_score
    lo = f(win_rate=0.0, drawdown=100.0, avg_return=-100.0, usage_count=0)
    hi = f(win_rate=1.0, drawdown=0.0, avg_return=100.0, usage_count=100)
    _eq((lo, hi), (0.0, 1.0))
    if not f(win_rate=0.6, drawdown=1.0, avg_return=1.0, usage_count=5) > f(win_rate=0.4, drawdown=1.0, avg_return=1.0, usage_count=5):
        raise AssertionError("higher win rate must not lower the score")
    if not f(win_rate=0.5, drawdown=0.0, avg_return=0.0, usage_count=5) > f(win_rate=0.5, drawdown=5.0, avg_return=0.0, usage_count=5):
        raise AssertionError("higher drawdown must lower the score")


def test_write_playbook_stats_and_reports_root_builder(tmp_path):
    root = _fixture(tmp_path)
    out = ps.write_playbook_stats(root, day="2026-10-28")
    p = pa.performance_artifact_paths(root, "2026-10-28")["playbook_stats_json"]
    _eq(out["artifact_path"], str(p))
    _eq(sorted(json.loads(p.read_text(encoding="utf-8"))["playbooks"]), ["breakout", "unknown"])
    out2 = ps.build_playbook_stats_from_reports_root(root, day="2026-10-28")
    _eq(out2["artifact_path"], str(p))
    # build_playbook_stats_from_reports_root computes the summary but writes only playbook_stats.json
    _eq(sorted(x.name for x in p.parent.iterdir()), ["playbook_stats.json"])
    # an explicit empty bundle list falls back to loading from disk (falsy `or`)
    _eq(sorted(ps.write_playbook_stats(root, day="2026-10-28", bundles=[])["playbooks"]), ["breakout", "unknown"])
