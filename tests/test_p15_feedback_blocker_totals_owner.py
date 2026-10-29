"""P15 A2: reporter_feedback ``_extract_blocker_totals`` moved to reporter_feedback_blocker_totals; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import reporter_feedback as f
from libs.reporting import reporter_feedback_blocker_totals as owner

GOLDEN = ["44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "68638b172de11b717c9cee333139e67a14bafcc5ce0d88f0d639a51f96497d0f", "d42c8bed22a72404fbdb979300e8d3472abb4480dcdd2c7b8635c52d8565ce42", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "EXC:TypeError"]

BLOCKER = [
    None, {}, {"dominant_blocker_total": {"a": "3", "b": 2, 5: "x"}, "no_trade_summary": {"dominant_blocker_topN": [{"reason": "z", "count": 9}]}},
    {"dominant_blocker_total": {}, "no_trade_summary": {"dominant_blocker_topN": [{"reason": " r1 ", "count": 2}, {"reason": "", "count": 5}, "junk", {"reason": "r1", "count": "7"}, {"reason": "r2", "count": None}, {"count": 1}]}},
    {"dominant_blocker_total": "junk", "no_trade_summary": {"dominant_blocker_topN": "abc"}},
    {"no_trade_summary": {"dominant_blocker_topN": [1, 2]}}, {"no_trade_summary": "x"}, {"no_trade_summary": {"dominant_blocker_topN": 5}},
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(BLOCKER)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    payload = BLOCKER[i]
    snap = copy.deepcopy(payload)
    assert _safe(lambda: f._extract_blocker_totals(payload)) == GOLDEN[i]
    assert _safe(lambda: owner.extract_blocker_totals(payload, facade=f)) == GOLDEN[i]
    assert payload == snap


def test_direct_total_wins_then_topn_fallback_with_last_duplicate():
    assert f._extract_blocker_totals(None) == {} and f._extract_blocker_totals({}) == {}
    assert f._extract_blocker_totals(BLOCKER[2]) == {"a": 3, "b": 2, "5": 0}                                                        # direct wins; keys stringified; "x" -> 0
    assert f._extract_blocker_totals(BLOCKER[3]) == {"r1": 7, "r2": 0}                                                             # strip, skip empty/non-dict, last duplicate overwrites
    assert f._extract_blocker_totals(BLOCKER[4]) == {}                                                                              # non-dict direct and non-list topN -> empty


def test_malformed_topn_original_exceptions():
    with pytest.raises(TypeError):
        f._extract_blocker_totals(BLOCKER[7])
    assert f._extract_blocker_totals(BLOCKER[5]) == {} and f._extract_blocker_totals(BLOCKER[6]) == {}


def test_facade_safe_int_use_time_patch_reaches_the_owner(monkeypatch):
    seen = []
    monkeypatch.setattr(f, "_safe_int", lambda v, d=0: (seen.append(v), -1)[1])
    assert f._extract_blocker_totals(BLOCKER[3]) == {"r1": -1, "r2": -1} and seen == [2, "7", None]


def test_owner_does_not_import_the_facade_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.reporter_feedback import" not in src and "import reporter_feedback\n" not in src
    assert len(inspect.getsource(f._extract_blocker_totals).splitlines()) <= 3
