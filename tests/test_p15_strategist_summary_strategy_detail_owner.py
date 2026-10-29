"""P15: strategist_llm_summary ``_strategy_detail_from_sources`` moved to strategist_llm_summary_strategy.strategy_detail_from_sources; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_strategy as owner

GOLDEN = ["0c32ec0c4269e024f05202e467ff815be0d4e8df93b4f8c8d0ab86d651076e40", "1032a55f36657b8d4dc1e4e6a1ddb8ff7da20b289ad8406467264b1b24bef969", "5238a6205d812707c3cfffcfddfd80dce4bb40a4f00cb08c6cdf92ec658f5ea0", "e95b6dce44fbf4a4543a39c81a1355eb0a225136bb3d5e8eb6e0b9b0d8376baf", "EXC:AttributeError", "0c32ec0c4269e024f05202e467ff815be0d4e8df93b4f8c8d0ab86d651076e40"]

STRAT = [
    ({}, {}), ({"pre_llm_playbook": "pp", "final_playbook": "fp", "playbook": "pbk", "strategy_scores": {"s": 1}, "candidate_watch_policy": {"w": 1}},
              {"strategy_detail": {"final_playbook": "cd_final", "strategy_scores": {"cd": 1}}, "pre_llm_playbook": "c_pre", "strategy_policy": {"market_policy": {"requested_playbook": "mp_req", "tactical_strategy": "mp_ts", "rejected_strategy_reasons": {"r": 1}}, "scanner_policy": {"candidate_watch_policy": {"sp": 1}}}}),
    ({"tactical_subtype": " sub "}, {"playbook": "cplay", "strategy_policy": {"market_policy": {"final_playbook": "mp_final"}}}), ({"requested_playbook_source": 0, "strategy_scores": {}}, {"requested_playbook_source": "csrc", "strategy_scores": {"c": 1}}),
    (None, None), ({}, {"strategy_detail": "junk", "strategy_policy": "junk"}),
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(STRAT)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = STRAT[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._strategy_detail_from_sources(*a)) == GOLDEN[i]
    assert _safe(lambda: owner.strategy_detail_from_sources(*a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_precedence_and_key_order():
    out = m._strategy_detail_from_sources(*STRAT[1])
    assert list(out) == ["pre_llm_playbook", "llm_requested_playbook", "requested_playbook", "requested_playbook_source", "final_playbook", "tactical_strategy", "tactical_subtype", "strategy_scores", "rejected_strategy_reasons", "candidate_watch_policy"]
    assert out["final_playbook"] == "cd_final" and out["pre_llm_playbook"] == "c_pre" and out["requested_playbook"] == "mp_req" and out["tactical_strategy"] == "mp_ts"            # detail > canonical > market_policy > payload
    assert out["strategy_scores"] == {"cd": 1} and out["rejected_strategy_reasons"] == {"r": 1} and out["candidate_watch_policy"] == {"sp": 1}
    fb = m._strategy_detail_from_sources(*STRAT[2])
    assert fb["final_playbook"] == "mp_final" and fb["tactical_subtype"] == "sub"                                                                                         # market_policy final beats canonical.playbook
    assert m._strategy_detail_from_sources(*STRAT[3])["strategy_scores"] == {"c": 1} and m._strategy_detail_from_sources(*STRAT[3])["requested_playbook_source"] == "csrc"
    assert m._strategy_detail_from_sources({}, {}) == {k: ({} if k in ("strategy_scores", "rejected_strategy_reasons", "candidate_watch_policy") else "") for k in m._strategy_detail_from_sources({}, {})}


def test_none_inputs_keep_original_attribute_error():
    with pytest.raises(AttributeError):
        m._strategy_detail_from_sources(*STRAT[4])


def test_facade_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(m, "_first_text", lambda default, *values: "FT")
    monkeypatch.setattr(m, "_first_dict", lambda *values: {"FD": 1})
    out = m._strategy_detail_from_sources({}, {})
    assert out["final_playbook"] == "FT" and out["strategy_scores"] == {"FD": 1}


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._strategy_detail_from_sources).splitlines()) <= 3
