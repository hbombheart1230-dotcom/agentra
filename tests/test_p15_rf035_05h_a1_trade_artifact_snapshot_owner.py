"""P15 RF-035 (05h): symbol_trade_report._extract_trade_artifact_snapshot moved to symbol_trade_artifact_projection; parity with the pre-move body."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

import pytest


def _norm(obj, root):
    return json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).replace(str(root), "<T>")


def _h(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _call(fn):
    try:
        return ["ok", fn()]
    except BaseException as exc:  # noqa: BLE001 - parity of exception type/message is the point
        return ["exc", type(exc).__name__, str(exc)]


def _write(root, rel, payload):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return p


def _patched(mod, name, value, fn):
    orig = getattr(mod, name)
    setattr(mod, name, value)
    try:
        return fn()
    finally:
        setattr(mod, name, orig)

from libs.reporting import symbol_trade_report as m
from libs.reporting import symbol_trade_artifact_projection as owner

FN = "_extract_trade_artifact_snapshot"
GOLDEN = "071193d423651ee85ceac3ced31cce8ba52f6e4d8e2969bffd9649a9aaaef754"


def _scenarios(fn, root, mod):
    out = []
    kw = lambda d: dict(report_path=root / d / "ai_trade_report.json", operator_brief_path=root / d / "operator_brief.json", lifecycle_bundle_path=root / d / "lifecycle_bundle.json")
    out.append(_call(lambda: fn(**kw("missing"))))
    _write(root, "full/ai_trade_report.json", {
        "executive_summary": {"headline": "H", "summary": "S"}, "market_context_at_entry": {"summary": " market "}, "entry_decision": {"summary": "breakout entry above vwap"},
        "final_operator_conclusion": {"summary": "closed on stop"}, "shared_facts": {"return_pct": 0.5}})
    _write(root, "full/operator_brief.json", {"headline": "BH", "executive_summary": "BS", "risk_summary": "BR", "next_checkpoints": ["a", "b", "c", "d"]})
    _write(root, "full/lifecycle_bundle.json", {"trade_outcome": {"return_pct": 1.25}, "strategist_feedback_input": {"entry_pattern_type": "", "exit_pattern_type": "stop_loss", "thesis_invalidation_code": " unknown ",
           "improvement_tags": ["t1", "t2"], "review_flags": ["r1"]}, "shared_facts": {"exit_reason": "stop hit", "return_pct": 2.0}})
    out.append(_call(lambda: fn(**kw("full"))))
    _write(root, "lists/ai_trade_report.json", [1])
    _write(root, "lists/operator_brief.json", "{bad")
    _write(root, "lists/lifecycle_bundle.json", {"trade_outcome": 5, "shared_facts": []})
    out.append(_call(lambda: fn(**kw("lists"))))
    out.append(_patched(mod, "_pick_result_pct", lambda *a: 99.0, lambda: _call(lambda: fn(**kw("full")))))
    out.append(_patched(mod, "_read_json", lambda p: {}, lambda: _call(lambda: fn(**kw("full")))))
    return out


def test_expected_values(tmp_path):
    out = _scenarios(m._extract_trade_artifact_snapshot, tmp_path, m)
    assert out[0][0] == "ok" and out[1][0] == "ok" and out[1][1]["artifact_result_pct"] == 1.25
    assert out[1][1]["brief_next_checkpoints"] == ["a", "b", "c"] and out[1][1]["improvement_tags"] == ["t1", "t2"] and out[1][1]["report_market_summary"] == "market"
    assert out[3][1]["artifact_result_pct"] == 99.0
    assert list(out[1][1])[0] == "report_headline" and list(out[1][1])[-1] == "artifact_result_pct"


def test_keyword_only():
    with pytest.raises(TypeError):
        m._extract_trade_artifact_snapshot(Path("a"), Path("b"), Path("c"))


def _run(fn, root, mod):
    return _norm(_scenarios(fn, root, mod), root)


def _owner_fn(**fixed):
    return lambda *a, **k: getattr(owner, FN)(*a, facade=m, **k)


def test_wrapper_owner_and_pre_move_golden(tmp_path):
    a = _run(getattr(m, FN), tmp_path / "a", m)
    b = _run(_owner_fn(), tmp_path / "b", m)
    assert a == b and _h(a) == GOLDEN


def test_wrapper_is_thin():
    import inspect
    assert len(inspect.getsource(getattr(m, FN)).strip().splitlines()) <= 12
    assert "import symbol_trade_report" not in inspect.getsource(owner) and "import report_source_helpers" not in inspect.getsource(owner)
