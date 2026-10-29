"""P15 A2: alpha research board ``_broad_opening`` moved to ``builder_broad_opening``; parity with the pre-move builder output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting.alpha_research_board import builder as b
from libs.reporting.alpha_research_board import builder_broad_opening as owner

GOLDEN = ["8e4934378535eb861447291fdc9c825f0d732c356ffa6b6eeb3dbfcee457fc54", "321fc9027251e0ef5a346154816e63b5bd63598b21d0d3be2f898ebe0346f722", "8e4934378535eb861447291fdc9c825f0d732c356ffa6b6eeb3dbfcee457fc54", "8e4934378535eb861447291fdc9c825f0d732c356ffa6b6eeb3dbfcee457fc54"]   # sha256 of the pre-move builder._broad_opening output per fixture

BROAD = [
    {},
    {"promotion_decision": {"status": "REJECTED", "values": {"observed_count": 7, "win_rate": 0.5, "average_net_return_pct": 0.2, "profit_factor": 1.1, "coverage": 0.8, "largest_day_share": 0.6, "largest_symbol_share": 0.3}}},
    {"promotion_decision": {"values": "junk"}},
    {"promotion_decision": {"status": "", "values": {"observed_count": 0}}},
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


@pytest.mark.parametrize("i", range(len(BROAD)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_are_unchanged(i):
    payload = BROAD[i]
    snap = copy.deepcopy(payload)
    got = b._broad_opening(payload)
    assert payload == snap
    assert _h(got) == GOLDEN[i]
    assert _h(owner._broad_opening(payload, facade=b)) == GOLDEN[i]
    assert payload == snap


def test_facade_use_time_patches_reach_the_owner(monkeypatch):
    calls = []
    real = b._candidate
    monkeypatch.setattr(b, "_candidate", lambda **kw: (calls.append(kw), real(**kw))[1])
    seen = []
    real_mapping = b.mapping
    monkeypatch.setattr(b, "mapping", lambda v: (seen.append(1), real_mapping(v))[1])
    out = b._broad_opening(BROAD[1])
    assert calls and seen
    c = calls[0]
    assert c["candidate_id"] == "OPEN_0_20_RANK1_30M" and c["source_status"] == "REJECTED" and c["board_bucket"] == "CLOSED"
    assert list(c["prospective"]) == ["sample_count", "window_count", "win_rate", "avg_net_return_pct", "profit_factor", "coverage"]
    assert c["prospective"]["sample_count"] == 7 and c["prospective"]["win_rate"] == 0.5 and c["concentration"]["largest_day_share"] == 0.6
    assert out is not None


def test_owner_does_not_import_the_builder_and_wrapper_is_thin():
    assert "import builder" not in inspect.getsource(owner) and "from .builder" not in inspect.getsource(owner)
    assert len(inspect.getsource(b._broad_opening).splitlines()) <= 3
