"""P15 RF-035 (05h): strategist_llm_summary.generate_strategist_llm_summary moved to strategist_llm_summary_writer_projection; parity with the pre-move body."""
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
from libs.reporting import strategist_llm_summary_writer_projection as owner

FN = "generate_strategist_llm_summary"
GOLDEN = "3a57d69cb282f131ddea31d31497de566ff2c3f9520a86e59e4b64e8b453d506"


def _files(d):
    return {p.name: p.read_bytes().decode("utf-8") for p in sorted(d.iterdir())}


def _scenarios(fn, root, mod):
    out = []
    r = _write(root, "s1/response.json", {"stage": "strategist", "status": "ok"})
    stub = {"schema_version": "strategist_llm_summary.v1", "llm_meta": {"status": "ok"}, "한글": "값"}

    def stubbed():
        res = fn(str(r))
        return [[p.name for p in res[:2]], res[2], _files(r.parent)]

    out.append(_patched(mod, "build_strategist_llm_summary_payload", lambda p: dict(stub), lambda: _patched(mod, "render_strategist_llm_summary_markdown", lambda payload: "# stub\n", lambda: _call(stubbed))))
    r2 = _write(root, "s2/response.json", {"stage": "strategist", "status": "ok"})

    def boom(p):
        raise ValueError("builder")

    out.append(_patched(mod, "build_strategist_llm_summary_payload", boom, lambda: _call(lambda: [fn(r2), None])))
    out.append({"left_after_error": sorted(p.name for p in r2.parent.iterdir())})
    r3 = _write(root, "s3/response.json", {"stage": "strategist", "status": "ok", "model": "m"})

    def real():
        res = fn(r3)
        return [[p.name for p in res[:2]], res[2]["llm_meta"]["status"], _files(r3.parent)]

    out.append(_patched(mod, "_utc_now_iso", lambda: "2026-10-30T00:00:00+00:00", lambda: _call(real)))
    out.append(_call(lambda: fn(root / "s4" / "response.json")))
    return out


def test_expected_values(tmp_path):
    out = _scenarios(m.generate_strategist_llm_summary, tmp_path, m)
    names, payload, files = out[0][1]
    assert names == ["strategist_summary.md", "strategist_summary.json"]
    assert json.loads(files["strategist_summary.json"]) == payload
    md = files["strategist_summary.md"]
    assert md == "\ufeff# stub\n" and "\r" not in md
    assert out[1][0] == "exc" and out[1][1] == "ValueError" and out[2] == {"left_after_error": ["response.json"]}
    assert out[4][0] == "exc"


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
