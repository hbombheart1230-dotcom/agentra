from __future__ import annotations

import hashlib
import json

from graphs.nodes.strategist_node import _stage_specific_llm_contract
from libs.runtime.strategist.llm.stage_contracts import build_stage_specific_contract


def _digest(value):
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def test_stage_contract_owner_matches_facade_and_golden_shapes():
    base = {"base": "계약"}
    expected = {
        "selected_symbol_tactical_refresh": "selected_symbol_decision",
        "stale_intraday_hold_review": "hold_review_decision",
        "end_of_day_carry_review": "carry_review",
    }
    for kind, first_key in expected.items():
        owner = build_stage_specific_contract(kind, base)
        wrapped = _stage_specific_llm_contract(kind, base)
        assert owner == wrapped
        assert next(iter(owner)) == first_key
        assert len(_digest(owner)) == 64
    assert base == {"base": "계약"}


def test_unknown_stage_preserves_base_identity():
    base = {"nested": {"unchanged": True}}
    assert build_stage_specific_contract("unknown", base) is base
    assert _stage_specific_llm_contract("unknown", base) is base
