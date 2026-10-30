"""P15 RF-035 (06h): intraday_trade_reports._load_story_input moved to intraday_report_read_projection; parity with the pre-move body."""
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

from libs.reporting import intraday_trade_reports as m
from libs.reporting import intraday_report_read_projection as owner

FN = "_load_story_input"
GOLDEN = "6c72664d91fb2a26c49ec73fda387e15219ad999ea62def86c586d490196dd4b"


def _scenarios(fn, root, mod):
    out = [_call(lambda: fn(root / "none"))]
    both = root / "both"
    _write(both, "ai_trade_report_input.json", {"k": 1})
    _write(both, "trade_story_input.json", {"k": 2})
    _write(both, "ai_trade_report/ai_trade_report_input.json", {"k": 3})
    out.append(_call(lambda: fn(both)))
    (both / "ai_trade_report_input.json").unlink()
    out.append(_call(lambda: fn(both)))
    (both / "ai_trade_report" / "ai_trade_report_input.json").unlink()
    out.append(_call(lambda: fn(both)))
    empty = root / "emptyfiles"
    _write(empty, "ai_trade_report_input.json", {})
    out.append(_call(lambda: fn(empty)))
    seen = []
    out.append(_patched(mod, "_read_json", lambda p: (seen.append(p.name), {"seam": 1} if p.name == "trade_story_input.json" else {})[1], lambda: _call(lambda: fn(root / "x"))))
    out.append(seen)
    return out


def test_expected_values(tmp_path):
    out = _scenarios(m._load_story_input, tmp_path, m)
    assert out[0] == ["ok", ({}, "")]
    assert out[1][1] == ({"k": 1}, str(tmp_path / "both" / "ai_trade_report_input.json"))
    assert out[2][1][0] == {"k": 3} and out[3][1][0] == {"k": 2} and out[4][1] == ({}, "")
    assert out[5][1][0] == {"seam": 1} and out[6] == ["ai_trade_report_input.json", "ai_trade_report_input.json", "trade_story_input.json"]


def _run(fn, root, mod):
    return _norm(_scenarios(fn, root, mod), root)


def test_wrapper_owner_and_pre_move_golden(tmp_path):
    a = _run(getattr(m, FN), tmp_path / "a", m)
    b = _run(lambda *a, **k: getattr(owner, FN)(*a, facade=m, **k), tmp_path / "b", m)
    assert a == b and _h(a) == GOLDEN


def test_wrapper_is_thin():
    import ast
    import inspect
    fn = ast.parse(inspect.getsource(getattr(m, FN))).body[0]
    stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
    assert len(stmts) == 1 and isinstance(stmts[0], ast.Return)
    assert "import intraday_trade_reports" not in inspect.getsource(owner)
