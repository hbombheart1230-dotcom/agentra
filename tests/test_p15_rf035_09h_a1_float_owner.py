"""P15 RF-035 (09h): q8_historical_review._float moved to q8_historical_scalar_projection; parity with the pre-move body (stdlib unittest)."""
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

from libs.reporting import q8_historical_review as m
from libs.reporting import q8_historical_scalar_projection as owner

FN = "_float"
FACADE = False
GOLDEN = "02b83cc84ea1fae185c8c9ff7425a9fdbf4c8235c25d7f9c73bbedcd76455062"


class _Boom:
    def __bool__(self):
        return True

    def __str__(self):
        raise RuntimeError("boom")


def _scenarios(fn, root, mod):
    vals = ["12.5%", "", "bad", None, "1,234.5", " 7 ", "%", ",", 0, 3, True, "nan", "inf", "-0.5%", [], _Boom(), "1e3", "١٢"]
    return [_call(lambda v=v: fn(v)) for v in vals]


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", 12.5])
    tc.assertEqual(out[1:4], [["ok", None]] * 3)
    tc.assertEqual(out[4], ["ok", 1234.5])
    tc.assertEqual(out[5], ["ok", 7.0])
    tc.assertEqual(out[6:8], [["ok", None]] * 2)
    tc.assertEqual(out[8], ["ok", 0.0])
    tc.assertEqual(out[13], ["ok", -0.5])
    tc.assertEqual(out[15], ["ok", None])


def _run(fn, root, mod):
    return _norm(_scenarios(fn, root, mod), root)


class Test(unittest.TestCase):
    def test_wrapper_owner_and_pre_move_golden(self):
        with tempfile.TemporaryDirectory() as ta, tempfile.TemporaryDirectory() as tb:
            a = _run(getattr(m, FN), Path(ta), m)
            b = _run(lambda *x, **k: getattr(owner, FN)(*x, **k), Path(tb), m)
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
