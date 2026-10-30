"""P15 RF-035 (06h): intraday_trade_reports._read_json moved to intraday_report_read_projection; parity with the pre-move body."""
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

FN = "_read_json"
GOLDEN = "3b041e67cb58f8b5ab071e161c83cac3cecb7f09884bca00766669847f71989e"


def _scenarios(fn, root, mod):
    out = [_call(lambda: fn(root / "missing.json"))]
    out.append(_call(lambda: fn(_write(root, "ok.json", {"x": 1, "한": "글"}))))
    out.append(_call(lambda: fn(_write(root, "arr.json", [1]))))
    out.append(_call(lambda: fn(_write(root, "bad.json", "{oops"))))
    out.append(_call(lambda: fn(root)))
    out.append(_patched(mod.json, "loads", lambda s: (_ for _ in ()).throw(ValueError("x")), lambda: _call(lambda: fn(root / "ok.json"))))
    out.append(_patched(mod.json, "loads", lambda s: {"patched": True}, lambda: _call(lambda: fn(root / "ok.json"))))
    return out


def test_expected_values(tmp_path):
    out = _scenarios(m._read_json, tmp_path, m)
    assert out[0] == ["ok", {}] and out[1] == ["ok", {"x": 1, "한": "글"}] and out[2] == ["ok", {}] and out[3] == ["ok", {}] and out[4] == ["ok", {}]
    assert out[5] == ["ok", {}] and out[6] == ["ok", {"patched": True}]


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
