"""P15 RF-035 (11h): post_exit_shadow_recap._rows_reach_epoch moved to post_exit_shadow_freshness_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import post_exit_shadow_freshness_projection as owner

FN = "_rows_reach_epoch"
FACADE = True
GOLDEN = "b385bfc18275e572b0c8e85d8cb94cc62212005cc449199f30ece248c6cc67a3"


def _scenarios(fn, root, mod):
    rows = [{"ts": 100}, {"ts": 200.5}, "bad", {"ts": None}, {"nots": 1}]
    out = [_call(lambda c=c: fn(rows, c)) for c in (None, 50, 100, 200.5, 201, "150", "bad", 0, -1)]
    out.append(_call(lambda: fn([], 1)))
    out.append(_call(lambda: fn(iter(rows), 150)))
    out.append(_call(lambda: fn([{"ts": "bad"}], 0)))
    out.append(_patched(mod, "_epoch_seconds", lambda v: 999.0, lambda: _call(lambda: fn([{"ts": 1}], 500))))
    out.append(_patched(mod, "_epoch_seconds", lambda v: None, lambda: _call(lambda: fn([{"ts": 1}], 0.5))))
    out.append(_call(lambda: fn(None, 1)))
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", False])
    tc.assertEqual([o[1] for o in out[1:5]], [True, True, True, False])
    tc.assertEqual(out[5], ["ok", True])
    tc.assertEqual(out[6][0], "exc")
    tc.assertEqual(out[9], ["ok", False])
    tc.assertEqual(out[10], ["ok", True])
    tc.assertEqual(out[12], ["ok", True])
    tc.assertEqual(out[13], ["ok", False])
    tc.assertEqual(out[14][:2], ["exc", "TypeError"])


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
