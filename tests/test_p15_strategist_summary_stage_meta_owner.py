"""P15 A2: strategist_llm_summary ``_stage_meta`` moved to strategist_llm_summary_stage; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_stage as owner

GOLDEN = ["a4011f6485a5fb902b1b4355be43e0acdff8b41b276e8228807a38a15fb21126", "d0aacf2dcd957fcbed469148c343e01cb6b9759874723d1f2d4b4107151a98d7", "2959742d2256c479a358b9b9a80e28b5871b8d957c1d4b47bb861cb044e3c02b", "e8589d866e6a1bc948c5300e7df37c429aadf06ed49fcc7dc2310fd54bc79500", "ff1cb3f67f3e747a1c0a630ffe65e0f168b42ea7588e75aab14e3cbc33a48908", "616c898f7bdb2a1429d1d5b89ca54126403f0ecd16ebeb99210b961b56a3b989", "d0aacf2dcd957fcbed469148c343e01cb6b9759874723d1f2d4b4107151a98d7", "d0aacf2dcd957fcbed469148c343e01cb6b9759874723d1f2d4b4107151a98d7"]

STAGE = [
    ({}, {}, None), ({"selected_symbol_decision": {}}, {}, None), ({}, {"call_kind": "stale_intraday_hold_review"}, None), ({}, {"call_kind": "end_of_day_carry_review", "stage_index": 0}, {"stage_index": 9}),
    ({}, {"stage_index": 0}, {"stage_index": 5, "call_kind": "selected_symbol_tactical_refresh"}), ({"call_kind": "unknown_kind"}, {"stage_name": " N "}, {"stage_component": "SC"}),
    ({}, {"call_kind": "selected_symbol_tactical_refresh", "component": "cmp"}, {"component": "c2"}), ({}, {"call_kind": "selected_symbol_tactical_refresh"}, "junk"),
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(STAGE)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = STAGE[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._stage_meta(*a)) == GOLDEN[i]
    assert _safe(lambda: owner.stage_meta(*a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_default_metadata_precedence_and_key_order():
    out = m._stage_meta({"selected_symbol_decision": {}}, {}, None)
    assert list(out) == ["call_kind", "stage_index", "stage_name", "stage_component"] and out["call_kind"] == "selected_symbol_tactical_refresh"
    assert out == {"call_kind": "selected_symbol_tactical_refresh", **{k: v for k, v in m._STAGE_META_BY_CALL_KIND["selected_symbol_tactical_refresh"].items() if k in ("stage_index", "stage_name", "stage_component")}}
    over = m._stage_meta({}, {"stage_index": 0}, {"stage_index": 5, "call_kind": "selected_symbol_tactical_refresh"})
    assert over["stage_index"] == 5                                                    # raw 0 is falsy -> sidecar wins (truthy-or precedence)
    unknown = m._stage_meta({"call_kind": "unknown_kind"}, {"stage_name": " N "}, {"stage_component": "SC"})
    assert unknown["stage_name"] == "N" and unknown["stage_component"] == "SC" and unknown["stage_index"] is None and unknown["call_kind"] == "unknown_kind"
    empty = m._stage_meta({}, {}, None)
    assert empty == {"call_kind": "", "stage_index": None, "stage_name": "", "stage_component": ""}


def test_facade_helpers_and_constant_use_time_patches(monkeypatch):
    monkeypatch.setattr(m, "_infer_call_kind", lambda p, r, s: "patched")
    monkeypatch.setattr(m, "_STAGE_META_BY_CALL_KIND", {"patched": {"stage_index": 7, "stage_name": "SN", "stage_component": "SC"}})
    assert m._stage_meta({}, {}, None) == {"call_kind": "patched", "stage_index": 7, "stage_name": "SN", "stage_component": "SC"}
    monkeypatch.setattr(m, "_first_text", lambda default, *values: "FT")
    assert m._stage_meta({}, {}, None)["stage_name"] == "FT"


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._stage_meta).splitlines()) <= 3
