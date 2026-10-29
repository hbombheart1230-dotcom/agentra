"""P15 A1: alpha research board ``_opening_rows`` moved to ``builder_opening_rows``; parity with the pre-move builder output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting.alpha_research_board import builder as b
from libs.reporting.alpha_research_board import builder_opening_rows as owner

GOLDEN = ["8cb7f619a8c8d2158c33758be746cf944374a252d7577be47dbac4851cf90cc2", "c29378baa3069c13037eab048da1871a503abff9f1ac8d85d19028119994fd44", "8cb7f619a8c8d2158c33758be746cf944374a252d7577be47dbac4851cf90cc2", "8cb7f619a8c8d2158c33758be746cf944374a252d7577be47dbac4851cf90cc2"]   # sha256 of the pre-move builder._opening_rows output per fixture

OPENING = [
    {},
    {"summary": {"conditional_lane_summaries": {
        "IMMEDIATE_OPENING_PROBE": {"horizons": {"+5m": {"live_net": {"count": 5, "win_rate": 0.6, "expectancy_pct": 0.4}}, "+30m": {"live_net": {"count": 99}}}},
        "CONFIRMED_RECURRENT_RANK": {"horizons": {"+30m": {"live_net": {"count": 3, "win_rate": 0.9, "expectancy_pct": 1.2}}}},
        "DISLOCATION_REBOUND": {"horizons": {"+60m": {"live_net": {"count": 8, "win_rate": 0.4, "expectancy_pct": -0.3}}}}}}},
    {"summary": {"conditional_lane_summaries": {"IMMEDIATE_OPENING_PROBE": "junk", "DISLOCATION_REBOUND": {"horizons": "x"}}}},
    {"summary": "junk", "extra": {"한글": "값"}},
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


@pytest.mark.parametrize("i", range(len(OPENING)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_are_unchanged(i):
    payload = OPENING[i]
    snap = copy.deepcopy(payload)
    got = b._opening_rows(payload)
    assert payload == snap
    assert _h(got) == GOLDEN[i]
    assert _h(owner._opening_rows(payload, facade=b)) == GOLDEN[i]
    assert payload == snap


def test_facade_use_time_patches_reach_the_owner(monkeypatch):
    calls = []
    real = b._candidate
    monkeypatch.setattr(b, "_candidate", lambda **kw: (calls.append(kw), real(**kw))[1])
    seen = []
    real_mapping = b.mapping
    monkeypatch.setattr(b, "mapping", lambda v: (seen.append(1), real_mapping(v))[1])
    out = b._opening_rows(OPENING[1])
    assert calls and seen
    assert [c["candidate_id"] for c in calls] == ["IMMEDIATE_OPENING_PROBE", "CONFIRMED_RECURRENT_RANK", "DISLOCATION_REBOUND"]
    assert [c["target_horizon"] for c in calls] == ["+5m", "+30m", "+60m"]
    assert all(c["source_status"] == "COLLECTING" and c["board_bucket"] == "OBSERVE_FIXED" for c in calls)
    assert calls[0]["evidence_note"] == "즉시 반응은 초반이 가장 강하고 EOD로 갈수록 약해짐."
    assert [r["candidate_id"] for r in out] == [c["candidate_id"] for c in calls]
    assert out is not None


def test_owner_does_not_import_the_builder_and_wrapper_is_thin():
    assert "import builder" not in inspect.getsource(owner) and "from .builder" not in inspect.getsource(owner)
    assert len(inspect.getsource(b._opening_rows).splitlines()) <= 3
