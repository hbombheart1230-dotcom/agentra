"""P15 RF-035 (13h): q8_shadow_blocker_review._avg moved to q8_shadow_blocker_scalar_projection; parity with the pre-move body (stdlib unittest)."""
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

from libs.reporting import q8_shadow_blocker_review as m
from libs.reporting import q8_shadow_blocker_scalar_projection as owner

FN = "_avg"
FACADE = False
GOLDEN = "c68ecf27ae97474a3648850e78dba6f04b34ec43cee9bfcd6543ad1685fbb1eb"


def _scenarios(fn, root, mod):
    vals = [[], [1.0, 2.0], [0.1, 0.2], [1.23456, 1.23454], (4, 5), [-1, 1], ["a"], None, [True, False], [10 ** 6, 1], [1e-9]]
    return [_call(lambda v=v: fn(v)) for v in vals]


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", 0.0])
    tc.assertEqual(out[1], ["ok", 1.5])
    tc.assertEqual(out[2], ["ok", 0.15])
    tc.assertEqual(out[4], ["ok", 4.5])
    tc.assertEqual(out[6][0], "exc")
    tc.assertEqual(out[7], ["ok", 0.0])


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
