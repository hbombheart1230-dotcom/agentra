"""P15 A4: reporter_feedback ``_extract_reporter_analysis_blocker_totals`` moved to reporter_feedback_analysis_blockers; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import reporter_feedback as f
from libs.reporting import reporter_feedback_analysis_blockers as owner

GOLDEN = ["44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "a00b860a34fae8c9293257589c40454d38fa30fbec2fd5840fea69c420a992d6", "929fe9fa78088a48a6d9fe030c92dab010e6a9e7ff260b356ea60678b0861038", "EXC:TypeError", "EXC:TypeError", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"]

ANALYSIS = [
    None, {}, {"monitor_evaluation": {"monitor_reason_top": {"b1": 2, "": 5, " b2 ": "3"}}, "supervisor_activity": {"blocked_reason_top": {"b1": "4", "  ": 1}},
               "intent_flow_analysis": {"reason_top": {"b1": 1, "monitor:x": 9, "i1": "2", "": 3}}},
    {"monitor_evaluation": {"monitor_reason_top": {"b": "x"}}}, {"monitor_evaluation": {"monitor_reason_top": [1]}}, {"supervisor_activity": {"blocked_reason_top": 5}},
    {"monitor_evaluation": "junk", "intent_flow_analysis": {"reason_top": {"monitor:a": 1}}},
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(ANALYSIS)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    payload = ANALYSIS[i]
    snap = copy.deepcopy(payload)
    assert _safe(lambda: f._extract_reporter_analysis_blocker_totals(payload)) == GOLDEN[i]
    assert _safe(lambda: owner.extract_reporter_analysis_blocker_totals(payload, facade=f)) == GOLDEN[i]
    assert payload == snap


def test_accumulation_order_skips_and_prefix_rule():
    assert f._extract_reporter_analysis_blocker_totals(None) == {} and f._extract_reporter_analysis_blocker_totals({}) == {}
    out = f._extract_reporter_analysis_blocker_totals(ANALYSIS[2])
    assert out == {"b1": 7, "b2": 3, "i1": 2} and list(out) == ["b1", "b2", "i1"]                                                # monitor + supervisor + intent summed; monitor:* and blank names skipped
    assert f._extract_reporter_analysis_blocker_totals(ANALYSIS[6]) == {}


def test_malformed_sources_keep_original_exceptions():
    for bad in (ANALYSIS[4], ANALYSIS[5]):
        with pytest.raises(TypeError):
            f._extract_reporter_analysis_blocker_totals(bad)
    assert f._extract_reporter_analysis_blocker_totals(ANALYSIS[3]) == {"b": 0}


def test_facade_safe_int_use_time_patch_reaches_the_owner(monkeypatch):
    monkeypatch.setattr(f, "_safe_int", lambda v, d=0: 1)
    assert f._extract_reporter_analysis_blocker_totals(ANALYSIS[2]) == {"b1": 3, "b2": 1, "i1": 1}


def test_owner_does_not_import_the_facade_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.reporter_feedback import" not in src and "import reporter_feedback\n" not in src
    assert len(inspect.getsource(f._extract_reporter_analysis_blocker_totals).splitlines()) <= 3
