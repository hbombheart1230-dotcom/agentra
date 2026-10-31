"""P15 RF-035 (10h): post_exit_shadow_recap._pct moved to post_exit_shadow_format_projection; parity with the pre-move body (stdlib unittest)."""
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

from libs.reporting import post_exit_shadow_recap as m
from libs.reporting import post_exit_shadow_format_projection as owner

FN = "_pct"
FACADE = False
GOLDEN = "4afa8e074da673f0aaa1294746db4e50f2e6700bad27b52c2ebab9ff4feb3f42"


def _scenarios(fn, root, mod):
    vals = [0.125, "bad", 1, 0, -0.5, "0.1", None, float("nan"), float("inf"), True, [], "1e-3", 0.00005, 12345.678]
    return [_call(lambda v=v: fn(v)) for v in vals]


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", "12.50%"])
    tc.assertEqual(out[1], ["ok", "-"])
    tc.assertEqual(out[2], ["ok", "100.00%"])
    tc.assertEqual(out[4], ["ok", "-50.00%"])
    tc.assertEqual(out[5], ["ok", "10.00%"])
    tc.assertEqual(out[6], ["ok", "-"])
    tc.assertEqual(out[7], ["ok", "nan%"])
    tc.assertEqual(out[10], ["ok", "-"])


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
