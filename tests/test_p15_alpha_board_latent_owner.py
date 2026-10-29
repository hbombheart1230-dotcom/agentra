"""P15 A3: alpha research board ``_latent`` moved to ``builder_latent``; parity with the pre-move builder output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting.alpha_research_board import builder as b
from libs.reporting.alpha_research_board import builder_latent as owner

GOLDEN = ["95683036b1bb282582e05abdddae83731b64e4749a4fb31e2ab1ec7d7abf36d3", "0ad8e82ce339bc40ef62a08c9c912b038c3013c8d87b9d499b2c090325d748dc", "95683036b1bb282582e05abdddae83731b64e4749a4fb31e2ab1ec7d7abf36d3", "95683036b1bb282582e05abdddae83731b64e4749a4fb31e2ab1ec7d7abf36d3"]   # sha256 of the pre-move builder._latent output per fixture

LATENT = [
    {},
    {"summary": {"status": "COLLECTING", "horizons": {"+30m": {"live_net": {"count": 12, "win_rate": 0.7, "expectancy_pct": 0.5}}},
                 "largest_day_share": 0.3, "largest_symbol_share": 0.4, "positive_day_ratio": 0.5}},
    {"summary": {"horizons": {"+30m": "junk"}}},
    {"summary": "junk"},
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


@pytest.mark.parametrize("i", range(len(LATENT)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_are_unchanged(i):
    payload = LATENT[i]
    snap = copy.deepcopy(payload)
    got = b._latent(payload)
    assert payload == snap
    assert _h(got) == GOLDEN[i]
    assert _h(owner._latent(payload, facade=b)) == GOLDEN[i]
    assert payload == snap


def test_facade_use_time_patches_reach_the_owner(monkeypatch):
    calls = []
    real = b._candidate
    monkeypatch.setattr(b, "_candidate", lambda **kw: (calls.append(kw), real(**kw))[1])
    seen = []
    real_mapping = b.mapping
    monkeypatch.setattr(b, "mapping", lambda v: (seen.append(1), real_mapping(v))[1])
    out = b._latent(LATENT[1])
    assert calls and seen
    c = calls[0]
    assert c["candidate_id"] == "LATENT_REACTIVATION_FRESH_TRIGGER" and c["source_status"] == "COLLECTING"
    assert list(c["concentration"]) == ["largest_day_share", "largest_symbol_share", "positive_day_ratio"] and c["concentration"]["largest_day_share"] == 0.3
    assert c["evidence_note"] == "수익률은 양수지만 날짜·종목 집중도와 양수 일자 gate를 통과하지 못함."
    assert out is not None


def test_owner_does_not_import_the_builder_and_wrapper_is_thin():
    assert "import builder" not in inspect.getsource(owner) and "from .builder" not in inspect.getsource(owner)
    assert len(inspect.getsource(b._latent).splitlines()) <= 3
