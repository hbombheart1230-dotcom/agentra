"""P15 A1: reporter_feedback ``_extract_route_summary`` moved to reporter_feedback_route_summary; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import reporter_feedback as f
from libs.reporting import reporter_feedback_route_summary as owner

GOLDEN = ["4bd3900f345e13d32daada9cec0c675c8f621752f3c2207cc91585d34e176847", "4bd3900f345e13d32daada9cec0c675c8f621752f3c2207cc91585d34e176847", "40586a93f34ec172468728cbf23b097e3dbce6d7af2f198056e87e9e5263746e", "062cf21ce2f8da02cea1cceccec8c1468c112fb69dcc87e4a983a3159bda2a80", "EXC:ValueError", "4bd3900f345e13d32daada9cec0c675c8f621752f3c2207cc91585d34e176847"]

ROUTE = [
    None, {}, {"route_summary": {"route_selected_total": {"monitor_only": 3, "full_cycle": 1}, "strategy_generation_mode_total": {"llm": 2}, "strategist_fallback_total": 0, "route_source": "nested_src", "route_source_run_count": "4",
                                 "route_source_missing_count": None, "route_source_breakdown": {"a": 1}},
             "route_selected_total": {"cached_strategist": 9}, "strategist_fallback_total": 7, "route_source": "direct", "route_source_run_count": 8, "route_source_missing_count": 2},
    {"route_selected_total": {"cached_strategist": 2}, "strategist_mode_total": {"rule": 1}, "strategist_fallback_total": "3", "route_source": "direct", "route_source_run_count": "x", "route_source_breakdown": {"b": 2}},
    {"route_summary": "junk", "route_selected_total": "junk", "strategist_mode_total": [1], "strategist_fallback_total": [1], "route_source_breakdown": "bad"},
    {"route_summary": {"route_selected_total": None, "strategist_fallback_total": 0}, "strategist_fallback_total": 5},
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(ROUTE)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    payload = ROUTE[i]
    snap = copy.deepcopy(payload)
    assert _safe(lambda: f._extract_route_summary(payload)) == GOLDEN[i]
    assert _safe(lambda: owner.extract_route_summary(payload, facade=f)) == GOLDEN[i]
    assert payload == snap


def test_explicit_values_nested_priority_and_fallbacks():
    assert f._extract_route_summary(None) == {"route_source": "unavailable", "route_source_run_count": 0, "route_source_missing_count": 0, "route_source_breakdown": {},
                                              "route_selected_total": {}, "strategy_generation_mode_total": {}, "strategist_fallback_total": 0}
    out = f._extract_route_summary(ROUTE[2])
    assert list(out) == ["route_source", "route_source_run_count", "route_source_missing_count", "route_source_breakdown", "route_selected_total", "strategy_generation_mode_total", "strategist_fallback_total"]
    assert out["route_source"] == "nested_src" and out["route_source_run_count"] == 4 and out["route_source_missing_count"] == 2      # None/0 nested falls through to direct
    assert out["route_selected_total"] == {"monitor_only": 3, "full_cycle": 1} and out["strategy_generation_mode_total"] == {"llm": 2} and out["strategist_fallback_total"] == 0
    direct = f._extract_route_summary(ROUTE[3])
    assert direct["route_selected_total"] == {"cached_strategist": 2} and direct["strategy_generation_mode_total"] == {"rule": 1} and direct["strategist_fallback_total"] == 3
    assert f._extract_route_summary(ROUTE[5])["strategist_fallback_total"] == 0                                                   # nested 0 is not None -> kept


def test_malformed_values_keep_original_exceptions():
    with pytest.raises(ValueError):
        f._extract_route_summary(ROUTE[4])                                                                                        # route_source_breakdown "bad" -> dict("bad")


def test_facade_safe_int_use_time_patch_reaches_the_owner(monkeypatch):
    seen = []
    monkeypatch.setattr(f, "_safe_int", lambda v, d=0: (seen.append(v), 99)[1])
    out = f._extract_route_summary(ROUTE[2])
    assert out["route_source_run_count"] == 99 and out["strategist_fallback_total"] == 99 and len(seen) == 3


def test_owner_does_not_import_the_facade_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.reporter_feedback import" not in src and "import reporter_feedback\n" not in src
    assert len(inspect.getsource(f._extract_route_summary).splitlines()) <= 3
