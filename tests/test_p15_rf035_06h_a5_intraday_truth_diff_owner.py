"""P15 RF-035 (06h): intraday_trade_reports._truth_surface_differs moved to intraday_report_quality_projection; parity with the pre-move body."""
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
from libs.reporting import intraday_report_quality_projection as owner

FN = "_truth_surface_differs"
GOLDEN = "3b8e2d80a48bf008b9a6ec442d7bee30c0a45384945401263e122bd15cb1de66"


def _scenarios(fn, root, mod):
    out = [_call(lambda: fn({}, {}))]
    out.append(_call(lambda: fn({"execution_details": {"order_id": "a"}}, {"execution_details": {"order_id": "b"}})))
    out.append(_call(lambda: fn({"execution_details": {"order_id": "a"}}, {"execution_details": {"order_id": "a"}})))
    out.append(_call(lambda: fn({"entry_execution_details": {"filled_price": 1}}, {"entry_execution_details": {"filled_price": 2}})))
    out.append(_call(lambda: fn({"exit_execution_details": {"broker_fee": 1}}, {})))
    calls = []
    out.append(_patched(mod, "_execution_truth_surface", lambda d: (calls.append(d), "same")[1], lambda: _call(lambda: fn({"execution_details": 1}, {"execution_details": 2}))))
    out.append(len(calls))
    out.append(_patched(mod, "_execution_truth_surface", lambda d: d, lambda: _call(lambda: fn({"execution_details": 1}, {"execution_details": 2}))))
    out.append(_call(lambda: fn(None, {})))
    return out


def test_expected_values(tmp_path):
    out = _scenarios(m._truth_surface_differs, tmp_path, m)
    assert out[0] == ["ok", False] and out[2] == ["ok", False] and out[5] == ["ok", False] and out[6] == 6 and out[7] == ["ok", True]
    assert out[8][0] == "exc"


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
