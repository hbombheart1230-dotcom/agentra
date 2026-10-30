"""P15: strategist_llm_summary ``_playbook_flow_label`` moved to strategist_llm_summary_playbook_flow.playbook_flow_label; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_playbook_flow as owner

GOLDEN = ["0933fb667296882d8c45abca58ac52e01c8db6f19e626b30de88f0f4ed143ec5", "30f8b180d63559f2512b744f60449e1245803dd6b6af9766e11acac8ddca0aae", "6df383705a36e5816ead180c7071b293ed5c673c42454c3c9c06b38a0ac0b38c", "b624599c4a9d53b0e5af2f6d850a9e3165aef99f6c9bf3dc5f5b85c740aafe53", "0933fb667296882d8c45abca58ac52e01c8db6f19e626b30de88f0f4ed143ec5", "1cc922ded06536d47f2307fa0600f1b837d294efaa034163892f8c6ce8efcffc", "d10a4bc9e0c1fa4e8f3d7ce2512b8756e47ca5fa451f373c39a1431bb88db49f", "EXC:AttributeError", "a68659bdf3c11e816ee0864c9244089a42faf75397a90e1729bcc64a9d724f03"]

FLOW = [{}, {"final_playbook": "f"}, {"pre_llm_playbook": "p", "requested_playbook": "r", "final_playbook": "f", "requested_playbook_source": "src"}, {"pre_llm_playbook": " p ", "final_playbook": "f"}, {"requested_playbook_source": "only_src"},
        {"pre_llm_playbook": "한글", "requested_playbook": "", "final_playbook": "f"}, {"pre_llm_playbook": 5}, None, {"requested_playbook": ["x"]}
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(FLOW)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = FLOW[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._playbook_flow_label(a)) == GOLDEN[i]
    assert _safe(lambda: owner.playbook_flow_label(a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_flow_order_suffix_and_dash():
    f = m._playbook_flow_label
    assert f({}) == "-" and f({"requested_playbook_source": "only_src"}) == "-" and f({"final_playbook": "f"}) == "f"
    assert f({"pre_llm_playbook": "p", "requested_playbook": "r", "final_playbook": "f", "requested_playbook_source": "src"}) == "p -> r -> f (source=src)"
    assert f({"pre_llm_playbook": " p ", "final_playbook": "f"}) == "p -> f" and f({"pre_llm_playbook": "한글", "requested_playbook": "", "final_playbook": "f"}) == "한글 -> f"
    assert f({"pre_llm_playbook": 5}) == "5"
    with pytest.raises(AttributeError):
        f(None)


def test_facade_text_use_time_patch_reaches_the_owner(monkeypatch):
    monkeypatch.setattr(m, "_text", lambda v, d="-": "T" if v else "")
    assert m._playbook_flow_label({"pre_llm_playbook": "a", "requested_playbook": "b", "final_playbook": "c", "requested_playbook_source": "s"}) == "T -> T -> T (source=T)"


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._playbook_flow_label).splitlines()) <= 3
