"""P15 A4: alpha research board ``_fresh_change`` moved to ``builder_fresh_change``; parity with the pre-move builder output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting.alpha_research_board import builder as b
from libs.reporting.alpha_research_board import builder_fresh_change as owner

GOLDEN = ["c23562ccf844a98abdb2100df5e78d804e8c5cb09e040a0f27a1ed6be4d3485d", "5695b346307b00aa5d92da8d1ebc3a878c24e87be81f195bf809aaaa29b9bfd1", "c23562ccf844a98abdb2100df5e78d804e8c5cb09e040a0f27a1ed6be4d3485d", "c23562ccf844a98abdb2100df5e78d804e8c5cb09e040a0f27a1ed6be4d3485d"]   # sha256 of the pre-move builder._fresh_change output per fixture

FRESH = [
    {},
    {"historical_reference": {"branch": {"horizons": {"+30m": {"count": 20, "win_rate": 0.6, "expectancy_pct": 0.8}}}},
     "branch": {"horizons": {"+30m": {"count": 9, "win_rate": 0.2, "expectancy_pct": -0.9}}}, "decision": {"status": "REJECTED"}},
    {"historical_reference": "junk", "branch": {"horizons": None}},
    {"decision": {"status": ""}},
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


@pytest.mark.parametrize("i", range(len(FRESH)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_are_unchanged(i):
    payload = FRESH[i]
    snap = copy.deepcopy(payload)
    got = b._fresh_change(payload)
    assert payload == snap
    assert _h(got) == GOLDEN[i]
    assert _h(owner._fresh_change(payload, facade=b)) == GOLDEN[i]
    assert payload == snap


def test_facade_use_time_patches_reach_the_owner(monkeypatch):
    calls = []
    real = b._candidate
    monkeypatch.setattr(b, "_candidate", lambda **kw: (calls.append(kw), real(**kw))[1])
    seen = []
    real_mapping = b.mapping
    monkeypatch.setattr(b, "mapping", lambda v: (seen.append(1), real_mapping(v))[1])
    out = b._fresh_change(FRESH[1])
    assert calls and seen
    c = calls[0]
    assert c["candidate_id"] == "R1_FRESH_CHANGE_ACTIVATION_V1" and c["source_status"] == "REJECTED"
    assert c["historical"] != c["prospective"] and c["evidence_note"] == "과거 양수 결과가 prospective에서 음수로 뒤집힘."
    assert b._fresh_change({})["source_status"] == "INSUFFICIENT_EVIDENCE"
    assert out is not None


def test_owner_does_not_import_the_builder_and_wrapper_is_thin():
    assert "import builder" not in inspect.getsource(owner) and "from .builder" not in inspect.getsource(owner)
    assert len(inspect.getsource(b._fresh_change).splitlines()) <= 3
