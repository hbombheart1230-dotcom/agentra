"""P15 RF-035 (10h): post_exit_shadow_recap._as_dict moved to post_exit_shadow_scalar_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import post_exit_shadow_scalar_projection as owner

FN = "_as_dict"
FACADE = False
GOLDEN = "0399e71849d0a1134548ad11cbc1cc7b32311ecde0296ebdf3f5843459452ad2"


class _D(dict):
    pass


def _scenarios(fn, root, mod):
    src = {"x": {"n": 1}}
    d = _D(a=1)
    out = [_call(lambda v=v: fn(v)) for v in [src, [], None, "x", 5, (1, 2), d, {}]]
    r = fn(src)
    out.append([r == src, r is not src, r["x"] is src["x"], type(fn(d)).__name__])
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", {"x": {"n": 1}}])
    tc.assertEqual(out[1:5], [["ok", {}]] * 4)
    tc.assertEqual(out[6], ["ok", {"a": 1}])
    tc.assertEqual(out[8], [True, True, True, "dict"])


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
