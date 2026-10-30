"""P15: strategist_llm_summary ``_strategy_patch_status_clean`` moved to strategist_llm_summary_watch_status.strategy_patch_status_clean; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_watch_status as owner

GOLDEN = ["c18c29c1b8f79439b074625efb562abc5e72d7595a6037d11dc5c7040903ef40", "0fb3ce9f9887fb8aa98c2185e24452329b1179f09b56aa16e43e69c622ac9c10", "0022f02d1609944348156cd7e8b1cff1a8f9285b10787ce30f5283b3ee778e42", "98edace81116caa7753073ca3c21a895729b63e1772c46bd14c88518743029dd", "EXC:AttributeError", "EXC:AttributeError", "d7f3062b1e94712ad0e875aa449ef70c68dbce25766ea451e15868e7fdaf8e00"]

PATCH = [{}, {"pre_llm_playbook": "p", "llm_requested_playbook": "l", "requested_playbook": "r", "requested_playbook_source": "s", "final_playbook": "f", "tactical_strategy": "t", "strategy_scores": {"a": 1}, "rejected_strategy_reasons": {"b": "c"}, "candidate_watch_policy": {"w": 1}},
         {"pre_llm_playbook": "p", "strategy_scores": {}, "rejected_strategy_reasons": [], "candidate_watch_policy": 0, "final_playbook": ""}, {"final_playbook": "f", "tactical_strategy": "t"}, None, "junk", {"strategy_scores": {"x": 0}}
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(PATCH)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = PATCH[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._strategy_patch_status_clean(a)) == GOLDEN[i]
    assert _safe(lambda: owner.strategy_patch_status_clean(a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_nine_keys_order_and_truthiness():
    f = m._strategy_patch_status_clean
    keys = ["pre_llm_playbook", "llm_requested_playbook", "requested_playbook", "requested_playbook_source", "final_playbook", "tactical_strategy", "strategy_scores", "rejected_strategy_reasons", "candidate_watch_policy"]
    assert f(PATCH[1]) == "적용됨" and f({}) == "일부 누락 (" + ", ".join(keys) + ")"
    assert f(PATCH[2]) == "일부 누락 (" + ", ".join(keys[1:]) + ")"                                         # empty dict/list/0/"" count as missing
    assert f(PATCH[6]) == "일부 누락 (" + ", ".join(k for k in keys if k != "strategy_scores") + ")"


def test_non_mapping_inputs_keep_original_attribute_error():
    for bad in (PATCH[4], PATCH[5]):
        with pytest.raises(AttributeError):
            m._strategy_patch_status_clean(bad)


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._strategy_patch_status_clean).splitlines()) <= 3
