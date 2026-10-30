"""P15: strategist_llm_summary ``_compact_operator_summary`` moved to strategist_llm_summary_operator_projection.compact_operator_summary; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_operator_projection as owner

GOLDEN = ["a35a4cc54e95b4798084b45daa7f94d5de9212f2dd7603976c50c140eb4f8575", "3a459ea0d517f7c3edfe1dd8794816e780f07fe5e4b2be6cc15e73c2ab824827", "2c67ef5723c4d9aeb384a96f85288267bc86bfd3c2361d90e4337056ed8e0c7e", "ff7087871e42fbe4d94ac6b17ed27d4a22732cb0a76419ec085a9dd5692ff734", "EXC:AttributeError", "c4b217e1fcb3792d7db287db29ec5657ed8db03f57ae941bf4e71c7959f4e76c"]

COMPACT = [{}, {"available": 1, "status": " ok ", "artifact_path": "/p", "trade_count": 3, "closed_trade_count": 2, "win_rate": 0.5, "avg_return_pct": 1.2}, {"available": 0, "status": None, "trade_count": 0, "win_rate": 0.0}, {"status": 5, "artifact_path": ["x"], "avg_return_pct": "한글"}, None, {"available": "no"}
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(COMPACT)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = COMPACT[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._compact_operator_summary(a)) == GOLDEN[i]
    assert _safe(lambda: owner.compact_operator_summary(a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_key_order_text_fields_and_raw_values():
    full = m._compact_operator_summary(COMPACT[1])
    assert list(full) == ["available", "status", "artifact_path", "trade_count", "closed_trade_count", "win_rate", "avg_return_pct"]
    assert full == {"available": True, "status": "ok", "artifact_path": "/p", "trade_count": 3, "closed_trade_count": 2, "win_rate": 0.5, "avg_return_pct": 1.2}
    zeros = m._compact_operator_summary(COMPACT[2])
    assert zeros["available"] is False and zeros["trade_count"] == 0 and zeros["win_rate"] == 0.0 and zeros["status"] == "" and zeros["closed_trade_count"] is None
    odd = m._compact_operator_summary(COMPACT[3])
    assert odd["status"] == "5" and odd["artifact_path"] == "['x']" and odd["avg_return_pct"] == "한글"
    assert m._compact_operator_summary(COMPACT[5])["available"] is True
    with pytest.raises(AttributeError):
        m._compact_operator_summary(None)


def test_facade_text_patch_and_usage_owner_seam(monkeypatch):
    monkeypatch.setattr(m, "_text", lambda v, d="-": "T")
    assert m._compact_operator_summary({"status": "s", "artifact_path": "p"}) == {"available": False, "status": "T", "artifact_path": "T", "trade_count": None, "closed_trade_count": None, "win_rate": None, "avg_return_pct": None}
    monkeypatch.setattr(m, "_compact_operator_summary", lambda v: "COMPACT")
    out = m._memory_usage_from_canonical({"memory_usage_trace": {"layer_decisions": {"daily": {"status": "ok"}}}})
    assert out["layer_decisions"]["daily"]["operator_summary"] == "COMPACT"                 # usage owner still reaches the facade wrapper at call time


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._compact_operator_summary).splitlines()) <= 3
