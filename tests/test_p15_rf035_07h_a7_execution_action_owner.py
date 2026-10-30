"""P15 RF-035 (07h): intraday_trade_reports._execution_action moved to intraday_report_execution_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import intraday_report_execution_projection as owner

FN = "_execution_action"
FACADE = False
GOLDEN = "dbc076ce79e61b20dd567f89e1f8f8269ec373249d242373e6304ef72b7b0d1d"


def _scenarios(fn, root, mod):
    cases = [{"execution": {"order": {"action": " buy "}}}, {"execution": {"action": "sell"}}, {}, {"execution": {"order": {"action": ""}, "action": "Hold"}}, {"execution": "bad"}, {"execution": {"order": "bad", "action": "x"}},
             {"execution": {"order": {"action": None}, "action": None}}, None, {"execution": {"order": {"action": 5}}}]
    return [_call(lambda c=c: fn(c)) for c in cases]


def _expected(tc, out, root):
    tc.assertEqual([o[1] for o in out[:7]], ["BUY", "SELL", "", "HOLD", "", "X", ""])
    tc.assertEqual(out[7][0], "exc")
    tc.assertEqual(out[8], ["ok", "5"])


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
