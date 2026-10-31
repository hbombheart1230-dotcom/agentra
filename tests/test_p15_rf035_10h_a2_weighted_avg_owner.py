"""P15 RF-035 (10h): q8_historical_review._weighted_avg moved to q8_historical_scalar_projection; parity with the pre-move body (stdlib unittest)."""
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

FN = "_weighted_avg"
FACADE = False
GOLDEN = "eb5aa2d13269267942c97675f587c56b14690fb64fa1e1450441314ce513d384"


def _scenarios(fn, root, mod):
    cases = [(3, 2), (1, 3), (5, 0), (5, -1), (0, 4), (1.23456, 1), (-3, 2), (1, 7), ("a", 1), (1, None), (None, 1), (2, 1.5)]
    return [_call(lambda c=c: fn(*c)) for c in cases]


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", 1.5])
    tc.assertEqual(out[1], ["ok", 0.3333])
    tc.assertEqual(out[2:5], [["ok", 0.0]] * 3)
    tc.assertEqual(out[5], ["ok", 1.2346])
    tc.assertEqual(out[6], ["ok", -1.5])
    tc.assertEqual(out[8][0], "exc")
    tc.assertEqual(out[9][0], "exc")


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
