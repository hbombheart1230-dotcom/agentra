"""P15 RF-035 (09h): q8_historical_review._pct_from_ratio moved to q8_historical_scalar_projection; parity with the pre-move body (stdlib unittest)."""
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

FN = "_pct_from_ratio"
FACADE = True
GOLDEN = "6a950496738c3ae346b43c9872d9af22bcdf5206d8f8c808182a4762971db290"


def _scenarios(fn, root, mod):
    vals = [0.25, 15, None, "", "bad", "50%", 1, -1, -0.5, 1.5, "0.5%", 0, "1,5"]
    out = [_call(lambda v=v: fn(v)) for v in vals]
    out.append(_patched(mod, "_float", lambda v: 0.5, lambda: _call(lambda: fn("anything"))))
    out.append(_patched(mod, "_float", lambda v: None, lambda: _call(lambda: fn(0.25))))
    out.append(_patched(mod, "_float", lambda v: (_ for _ in ()).throw(KeyError("k")), lambda: _call(lambda: fn(0.25))))
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", 25.0])
    tc.assertEqual(out[1], ["ok", 15.0])
    tc.assertEqual(out[2:5], [["ok", None]] * 3)
    tc.assertEqual(out[5], ["ok", 50.0])
    tc.assertEqual(out[6], ["ok", 100.0])
    tc.assertEqual(out[9], ["ok", 1.5])
    tc.assertEqual(out[13], ["ok", 50.0])
    tc.assertEqual(out[14], ["ok", None])
    tc.assertEqual(out[15][:2], ["exc", "KeyError"])


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
