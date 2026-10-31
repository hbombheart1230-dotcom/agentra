"""P15 RF-035 (13h): q8_shadow_blocker_review._checkpoint_values moved to q8_shadow_blocker_checkpoint_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import q8_shadow_blocker_checkpoint_projection as owner

FN = "_checkpoint_values"
FACADE = True
GOLDEN = "90bf7cf074205c5cd28455233b3ade706ddf49b85a35016f65e6043cf6b4b4e9"


def _scenarios(fn, root, mod):
    cases = [
        {"checkpoints": {"5m": {"status": "observed", "return_pct": "1.2", "mfe_pct": "2.0", "mae_pct": "-0.5"}}},
        {"checkpoints": {"5m": {"status": "pending"}}},
        {},
        {"checkpoints": {"5m": {"status": "observed", "return_pct": 1.0, "mfe_pct": 3.0, "mae_pct": -1.0}, "15m": {"status": "observed", "return_pct": 2.0, "mfe_pct": 2.5, "mae_pct": -0.2}, "60m": {"status": "observed"}}},
        {"checkpoints": {"5m": {"status": "observed", "return_pct": "bad"}}},
        {"checkpoints": "bad"},
        {"checkpoints": {"5m": "bad"}},
        {"checkpoints": [1]},
    ]
    out = [_call(lambda c=c: fn(c)) for c in cases]
    out.append(_call(lambda: fn(None)))
    out.append(_patched(mod, "_to_float", lambda v: 9.0, lambda: _call(lambda: fn(cases[0]))))
    out.append(_patched(mod, "Mapping", type("Never", (), {}), lambda: _call(lambda: fn(cases[0]))))
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", {"available": True, "latest_return_pct": 1.2, "max_favorable_pct": 2.0, "max_adverse_pct": -0.5}])
    tc.assertEqual(out[1], ["ok", {"available": False}])
    tc.assertEqual(out[2], ["ok", {"available": False}])
    tc.assertEqual(out[3][1], {"available": True, "latest_return_pct": 2.0, "max_favorable_pct": 3.0, "max_adverse_pct": -1.0})
    tc.assertEqual(out[4][1]["latest_return_pct"], None)
    tc.assertEqual(out[8][0], "exc")
    tc.assertEqual(out[9][1], {"available": True, "latest_return_pct": 9.0, "max_favorable_pct": 9.0, "max_adverse_pct": 9.0})
    tc.assertEqual(out[10], ["ok", {"available": False}])


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
