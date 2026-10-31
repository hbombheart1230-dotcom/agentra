"""P15 RF-035 (15h): controlled_mock_lane_report._fixed_lane_strategy moved to controlled_lane_strategy_projection; parity with the pre-move body (stdlib unittest)."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from libs.reporting import controlled_mock_lane_report as m
from libs.reporting import controlled_lane_strategy_projection as owner

FN = "_fixed_lane_strategy"
FACADE = False
GOLDEN = "9dea7e044537fb9ac6f500c50cb06454662f80393cfe956f743440c2c79b7090"


def _norm(obj, root):
    return json.dumps(obj, ensure_ascii=False, default=repr).replace(str(root), "<T>")


def _h(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _call(fn):
    try:
        return ["ok", fn()]
    except BaseException as exc:  # noqa: BLE001 - parity of exception type/message is the point
        return ["exc", type(exc).__name__, str(exc)]


def _patched(mod, name, value, fn):
    with mock.patch.object(mod, name, value):
        return fn()


def _scenarios(fn, root, mod):
    a = fn()
    b = fn()
    a["expected_hold_window"]["min_sec"] = 1
    return [_call(lambda: fn()), ["distinct", [a is not b, a["expected_hold_window"] is not b["expected_hold_window"], b["expected_hold_window"]["min_sec"]]], _call(lambda: fn(1))]


def _expected(tc, out, root):
    tc.assertEqual(out[0][1], {"controlled_mock_lane": True, "strategy_horizon": "intraday", "expected_hold_window": {"min_sec": 300, "target_sec": 1800, "max_sec": 14400}, "llm_used": False, "horizon_revision_allowed": False})
    tc.assertEqual(out[1], ["distinct", [True, True, 300]])
    tc.assertEqual(out[2][0], "exc")


def _run(fn, root, mod):
    return _norm(_scenarios(fn, root, mod), root)


def _owner_fn():
    f = getattr(owner, FN)
    return (lambda *x, **k: f(*x, facade=m, **k)) if FACADE else f


class Test(unittest.TestCase):
    def test_wrapper_owner_and_pre_move_golden(self):
        with tempfile.TemporaryDirectory() as ta, tempfile.TemporaryDirectory() as tb:
            a = _run(getattr(m, FN), Path(ta), m)
            b = _run(_owner_fn(), Path(tb), m)
        self.assertEqual(a, b)
        self.assertEqual(_h(a), GOLDEN)

    def test_wrapper_is_thin_and_owner_does_not_import_source(self):
        import ast
        import inspect
        fn = ast.parse(inspect.getsource(getattr(m, FN))).body[0]
        stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
        self.assertTrue(len(stmts) == 1 and isinstance(stmts[0], ast.Return))
        self.assertNotIn("import controlled_mock_lane_report", inspect.getsource(owner))

    def test_expected_values(self):
        with tempfile.TemporaryDirectory() as t:
            _expected(self, _scenarios(getattr(m, FN), Path(t), m), Path(t))


if __name__ == "__main__":
    unittest.main()
