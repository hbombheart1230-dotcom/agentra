"""P15 C02-4: strategy memory tolerates malformed playbook usage_count / non-finite numbers locally."""
from __future__ import annotations

import copy
import json

import pytest

from libs.performance import strategy_memory as sm

GOOD = {"usage_count": 3, "win_rate": 0.8, "avg_return": 0.1, "stability_score": 0.7}
BAD = {"usage_count": "nan", "win_rate": "inf", "avg_return": "oops"}


def _build(playbooks, summary=None):
    return sm.build_strategy_memory(summary or {}, {"playbooks": playbooks})


def test_malformed_playbook_is_isolated_and_good_one_is_kept():
    pb = {"good": dict(GOOD), "bad": dict(BAD)}
    snap = copy.deepcopy(pb)
    mem = _build(pb, {"per_market_regime_stats": {"r": {"trade_count": "inf", "win_rate": "nan", "avg_return": "1.5"}}})
    assert pb == snap
    assert mem["best_playbooks"] == ["good"] and "bad" not in mem["worst_playbooks"]
    assert mem["playbook_performance_snapshot"]["good"] == {"usage_count": 3, "win_rate": 0.8, "avg_return": 0.1, "stability_score": 0.7}
    assert mem["playbook_performance_snapshot"]["bad"] == {"usage_count": 0, "win_rate": 0.0, "avg_return": 0.0, "stability_score": 0.0}
    assert mem["market_condition_bias"]["regime_bias"]["r"] == {"win_rate": 0.0, "avg_return": 1.5, "trade_count": 0}
    assert mem["advisory_only"] is True and mem["schema_version"] == "strategy_memory.v1"
    json.dumps(mem, allow_nan=False)


@pytest.mark.parametrize("usage", ["bad", "nan", "inf", "-inf", None, [], {}, float("nan"), float("inf")])
def test_any_bad_usage_count_never_raises_and_is_not_evidence(usage):
    mem = _build({"p": {"usage_count": usage, "win_rate": 0.9, "avg_return": 0.5, "stability_score": 1.0}})
    assert mem["best_playbooks"] == [] and mem["worst_playbooks"] == []
    assert mem["playbook_performance_snapshot"]["p"]["usage_count"] == 0
    json.dumps(mem, allow_nan=False)


def test_valid_two_playbook_ordering_and_mutual_exclusion_parity():
    pb = {
        "a": {"usage_count": 2, "win_rate": 0.6, "avg_return": 0.2, "stability_score": 0.5},
        "b": {"usage_count": 5, "win_rate": 0.9, "avg_return": 0.3, "stability_score": 0.9},
        "c": {"usage_count": 4, "win_rate": 0.2, "avg_return": -0.4, "stability_score": 0.1},
        "d": {"usage_count": 1, "win_rate": 0.1, "avg_return": -1.0, "stability_score": 0.0},     # usage < 2 -> excluded
        "unknown": {"usage_count": 9, "win_rate": 0.9, "avg_return": 1.0, "stability_score": 1.0},
    }
    mem = _build(pb)
    assert mem["best_playbooks"] == ["b", "a"] and mem["worst_playbooks"] == ["c"]
    assert not set(mem["best_playbooks"]) & set(mem["worst_playbooks"])
    assert list(mem["playbook_performance_snapshot"]) == ["unknown", "b", "a", "c"]            # stability desc, top 4
    assert mem["recent_success_patterns"] == ["playbook:unknown", "playbook:b", "playbook:a"] or mem["recent_success_patterns"][0].startswith("playbook:")
    one = _build({"solo": {"usage_count": 2, "win_rate": 0.6, "avg_return": 0.1, "stability_score": 0.5}})
    assert one["best_playbooks"] == ["solo"] and one["worst_playbooks"] == []


def test_usage_count_threshold_is_two_inclusive_and_float_strings_parse():
    mem = _build({"x": {"usage_count": "2.0", "win_rate": 0.6, "avg_return": 0.1}, "y": {"usage_count": 1.9, "win_rate": 0.6, "avg_return": 0.1}})
    assert mem["best_playbooks"] == ["x"]


@pytest.mark.parametrize("fn,v,d,exp", [("_safe_float", "nan", 1.5, 1.5), ("_safe_float", "inf", 0.0, 0.0), ("_safe_float", "2.5", 0.0, 2.5),
                                         ("_safe_int", "inf", 7, 7), ("_safe_int", "nan", 0, 0), ("_safe_int", "3.9", 0, 3), ("_safe_int", "bad", 4, 4)])
def test_safe_helpers(fn, v, d, exp):
    assert getattr(sm, fn)(v, d) == exp


def test_write_strategy_memory_only_under_explicit_temp_root(tmp_path, monkeypatch):
    monkeypatch.setenv("STRATEGY_MEMORY_PERSIST_ENABLED", "true")
    root = tmp_path / "reports"
    root.mkdir()
    out = sm.write_strategy_memory(root, day="2026-10-20", summary={"day": "2026-10-20"}, playbook_stats={"playbooks": {"good": dict(GOOD), "bad": dict(BAD)}})
    files = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*") if p.is_file())
    assert files == ["reports/performance/2026-10-20/strategy_memory.json"]
    saved = json.loads((root / "performance/2026-10-20/strategy_memory.json").read_text(encoding="utf-8"))
    assert saved["best_playbooks"] == ["good"] and out["status"] == "ok" and out["directional_bias_usable"] is True
    assert out["artifact_path"] == str(root / "performance/2026-10-20/strategy_memory.json")


def test_reporter_digest_reader_uses_temp_and_missing_is_unavailable(tmp_path):
    d = sm._load_reporter_analysis_digest(tmp_path, "2026-10-20")
    assert d["available"] is False and d["status"] == "missing" and d["artifact_path"].startswith(str(tmp_path))
