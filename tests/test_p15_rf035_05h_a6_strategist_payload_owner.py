"""P15 RF-035 (05h): strategist_llm_summary.build_strategist_llm_summary_payload moved to strategist_llm_summary_payload_projection; parity with the pre-move body."""
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

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_payload_projection as owner

FN = "build_strategist_llm_summary_payload"
GOLDEN = "d6e28342e78c16338abefdaeb71a40a9ef68224899b3a6713961a974f15785a2"


def _scenarios(fn, root, mod):
    out = []
    _patch = lambda f: _patched(mod, "_utc_now_iso", lambda: "2026-10-30T00:00:00+00:00", f)
    r1 = _write(root, "a/response.json", {"stage": "strategist", "status": "ok"})
    out.append(_patch(lambda: _call(lambda: fn(r1))))
    r2 = _write(root, "b/response.json", {"stage": "strategist", "status": "ok", "model": "m", "run_id": "R", "day": "2026-10-30", "payload": {"playbook": "opening_gap", "selected_themes": ["t"], "rationale": "why"}})
    _write(root, "b/meta.json", {"provider": "P", "saved_at": "S"})
    out.append(_patch(lambda: _call(lambda: fn(str(r2)))))
    r3 = _write(root, "c/response.json", "{not json")
    out.append(_patch(lambda: _call(lambda: fn(r3))))
    out.append(_patch(lambda: _call(lambda: fn(root / "c" / "missing.json"))))
    out.append(_patch(lambda: _patched(mod, "_load_canonical_strategist", lambda p: (p.with_name("canon.json"), {"generated_at": "G", "run_id": "CR"}), lambda: _call(lambda: fn(r1)))))
    out.append(_patch(lambda: _patched(mod, "_read_json", lambda p: {"stage": "from_sidecar"}, lambda: _call(lambda: fn(r1)))))
    return out


def test_expected_values(tmp_path):
    out = _scenarios(m.build_strategist_llm_summary_payload, tmp_path, m)
    first = out[0][1]
    assert first["schema_version"] == "strategist_llm_summary.v1" and first["artifact_type"] == "strategist_llm_summary" and first["llm_meta"]["status"] == "ok"
    assert first["generated_at"] == "2026-10-30T00:00:00+00:00"
    assert out[2][0] == "exc" and out[2][1] == "JSONDecodeError" and out[3][1] == "FileNotFoundError"
    assert out[5][1]["llm_meta"]["status"] == "ok"


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
