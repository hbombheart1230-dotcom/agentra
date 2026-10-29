"""P15 A6: reporter_ai_review ``_default_result`` moved to reporter_ai_review_result.default_result; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import reporter_ai_review as rv
from libs.reporting import reporter_ai_review_result as owner

GOLDEN = ["30893ced37f150dc43c0d375fc17af0c784b6f9a944f9bdbf3d0f439aebc1470", "0eb76085d5c8e5e5a3e90df6d967d5e026333dd4bd776ecf08e1482a1f48283f", "952d0379710702b0050f66d4e88beba4e754d6609958282af15e8d3d9b17e57b", "1f522f3443529445ec266c5b5f03c517b5d6191c4a0081c6bb05ae37bce60f87"]

DEFAULTS = [dict(enabled=False, status="fallback"), dict(enabled=True, status="ok", reason="r" * 400, model="m/x"), dict(enabled=1, status="DRY_RUN", reason="한글 사유", model=None), dict(enabled=0, status="", reason=None, model="")]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(DEFAULTS)))
def test_wrapper_and_owner_match_pre_move_golden(i):
    kw = DEFAULTS[i]
    snap = copy.deepcopy(kw)
    assert _safe(lambda: rv._default_result(**kw)) == GOLDEN[i]
    assert _safe(lambda: owner.default_result(facade=rv, **kw)) == GOLDEN[i]
    assert kw == snap


def test_default_shape_key_order_and_reason_cap():
    d = rv._default_result(enabled=False, status="fallback")
    assert d["enabled"] is False and d["status"] == "fallback" and d["parse_mode"] == "none" and d["ai_run_grade"] == "N/A" and d["model"] == "" and d["reason"] == ""
    keys = list(d)
    assert keys[:6] == ["enabled", "status", "llm_status", "model", "reason", "parse_mode"] and keys[-7:] == ["ai_summary", "ai_findings", "ai_root_causes", "ai_improvement_suggestions", "ai_run_grade", "ai_agent_evaluations", "ai_evidence_links"]
    assert d["ai_evidence_links"] == {"findings": [], "root_causes": [], "improvements": []} and list(d["ai_evidence_links"]) == ["findings", "root_causes", "improvements"]
    big = rv._default_result(enabled=True, status="ok", reason="r" * 400, model="m/x")
    assert len(big["reason"]) == 320 and big["reason"].endswith("...") and big["model"] == "m/x" and big["enabled"] is True


def test_two_calls_return_independent_nested_objects():
    a = rv._default_result(enabled=True, status="ok")
    b = rv._default_result(enabled=True, status="ok")
    assert a == b and a is not b and a["ai_findings"] is not b["ai_findings"] and a["ai_evidence_links"] is not b["ai_evidence_links"]
    a["ai_evidence_links"]["findings"].append("x")
    assert b["ai_evidence_links"]["findings"] == [] and rv._default_result(enabled=True, status="ok")["ai_evidence_links"]["findings"] == []


def test_facade_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(rv, "required_key_metadata", lambda obj, keys: {"required_marker": list(keys)[:1]})
    monkeypatch.setattr(rv, "_normalize_llm_status", lambda s: "NORM:" + s)
    monkeypatch.setattr(rv, "_clip_str", lambda v, *, max_len=400: f"CLIP{max_len}")
    d = rv._default_result(enabled=True, status="ok", reason="x")
    assert d["required_marker"] == ["ai_summary"] and d["llm_status"] == "NORM:ok" and d["reason"] == "CLIP320"
    monkeypatch.setattr(rv, "REPORTER_AI_REVIEW_REQUIRED_KEYS", ["only"])
    assert rv._default_result(enabled=True, status="ok")["required_marker"] == ["only"]


def test_existing_owner_functions_are_untouched_and_wrapper_is_thin():
    assert owner.normalize_result.__name__ == "normalize_result" and owner.normalize_evidence_link_items.__name__ == "normalize_evidence_link_items"
    src = inspect.getsource(owner)
    assert "import reporter_ai_review\n" not in src and "from libs.reporting.reporter_ai_review import" not in src
    assert len(inspect.getsource(rv._default_result).splitlines()) <= 3
