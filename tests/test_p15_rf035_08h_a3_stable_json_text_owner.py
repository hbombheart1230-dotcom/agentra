"""P15 RF-035 (08h): intraday_trade_reports._stable_json_text moved to intraday_report_scalar_projection; parity with the pre-move body (stdlib unittest)."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return p


def _patched(mod, name, value, fn):
    with mock.patch.object(mod, name, value):
        return fn()

from libs.reporting import intraday_trade_reports as m
from libs.reporting import intraday_report_scalar_projection as owner

FN = "_stable_json_text"
FACADE = True
GOLDEN = "eea8e2df51f0154cd1a42e5078052d708742cc7c3e54a275b9676528b8d96a14"


class _NoJson:
    pass


def _scenarios(fn, root, mod):
    out = [_call(lambda v=v: fn(v)) for v in [{"b": 2, "a": 1}, {"한": "글", "x": [1, 2, {"z": None}]}, [3, 1], "s", None, 5, {"a": {"c": 1, "b": 2}}, {1: "a", "b": 2}, _NoJson(), float("nan")]]
    out.append(_patched(mod.json, "dumps", lambda *a, **k: "PATCHED", lambda: _call(lambda: fn({"a": 1}))))
    out.append(_patched(mod.json, "dumps", lambda *a, **k: (_ for _ in ()).throw(ValueError("x")), lambda: _call(lambda: fn({"a": 1}))))
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", '{"a":1,"b":2}'])
    tc.assertEqual(out[1], ["ok", '{"x":[1,2,{"z":null}],"한":"글"}'])
    tc.assertEqual(out[2], ["ok", "[3,1]"])
    tc.assertEqual(out[7][0], "exc")
    tc.assertEqual(out[8][0], "exc")
    tc.assertEqual(out[10], ["ok", "PATCHED"])
    tc.assertEqual(out[11][:2], ["exc", "ValueError"])


def _run(fn, root, mod):
    return _norm(_scenarios(fn, root, mod), root)


class Test(unittest.TestCase):
    def test_wrapper_owner_and_pre_move_golden(self):
        with tempfile.TemporaryDirectory() as ta, tempfile.TemporaryDirectory() as tb:
            a = _run(getattr(m, FN), Path(ta), m)
            b = _run(lambda *x, **k: getattr(owner, FN)(*x, facade=m, **k), Path(tb), m)
        self.assertEqual(a, b)
        self.assertEqual(_h(a), GOLDEN)

    def test_wrapper_is_thin_and_owner_does_not_import_source(self):
        import ast
        import inspect
        fn = ast.parse(inspect.getsource(getattr(m, FN))).body[0]
        stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
        self.assertTrue(len(stmts) == 1 and isinstance(stmts[0], ast.Return))
        self.assertNotIn("import " + m.__name__.split(".")[-1], inspect.getsource(owner))

    def test_expected_values(self):
        with tempfile.TemporaryDirectory() as t:
            _expected(self, _scenarios(getattr(m, FN), Path(t), m), Path(t))


if __name__ == "__main__":
    unittest.main()
