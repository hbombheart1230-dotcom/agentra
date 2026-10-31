"""P15 RF-035 (09h): q8_historical_review._aggregate_return_rows moved to q8_historical_aggregate_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import q8_historical_aggregate_projection as owner

FN = "_aggregate_return_rows"
FACADE = True
GOLDEN = "277410c89e0531559bedd4150336c28c79f93849c8e3fcd8d37934ca8b2c7045"


ROWS = [
    {"axis": "alpha", "pnl_pct": 2.0}, {"axis": "alpha", "pnl_pct": -1.0}, {"axis": "beta", "pnl_pct": 5}, {"axis": "beta", "pnl_pct": 5}, {"axis": "beta", "pnl_pct": 0},
    {"axis": "", "pnl_pct": 1.0}, {"axis": "unknown", "pnl_pct": -3.0}, {"axis": "gamma", "pnl_pct": "x"}, {"pnl_pct": 4.0}, {"axis": "delta", "pnl_pct": True},
]


def _scenarios(fn, root, mod):
    snap = copy.deepcopy(ROWS)
    out = [_call(lambda: fn(ROWS, "axis")), ROWS == snap]
    out.append(_call(lambda: fn([], "axis")))
    out.append(_call(lambda: fn(ROWS, "axis", limit=2)))
    out.append(_call(lambda: fn(ROWS, "axis", limit=0)))
    out.append(_call(lambda: fn([{"axis": "a", "pnl_pct": 1}, {"axis": "b", "pnl_pct": -1}], "axis")))
    out.append(_call(lambda: fn(["bad"], "axis")))
    out.append(_call(lambda: fn(ROWS, "missing")))
    out.append(_patched(mod, "_text", lambda v: "SEAM", lambda: _call(lambda: fn(ROWS, "axis", limit=3))))
    out.append(_patched(mod, "_avg", lambda v: 42.0, lambda: _call(lambda: fn(ROWS, "axis", limit=3))))
    out.append(_patched(mod, "defaultdict", lambda f: {}, lambda: _call(lambda: fn(ROWS, "axis"))))
    return out


def _expected(tc, out, root):
    r = out[0][1]
    tc.assertTrue(out[1])
    tc.assertEqual(r[0]["name"], "beta")
    tc.assertEqual([x["name"] for x in r][:3], ["beta", "missing", "alpha"])
    alpha = [x for x in r if x["name"] == "alpha"][0]
    tc.assertEqual((alpha["count"], alpha["win_count"], alpha["loss_count"], alpha["win_rate"], alpha["avg_return_pct"]), (2, 1, 1, 0.5, 0.5))
    tc.assertEqual(out[2], ["ok", []])
    tc.assertEqual(len(out[3][1]), 2)
    tc.assertEqual(out[4], ["ok", []])
    tc.assertEqual([x["name"] for x in out[5][1]], ["a", "b"])
    tc.assertEqual(out[6][0], "exc")
    tc.assertEqual([x["name"] for x in out[8][1]], ["SEAM"])
    tc.assertTrue(all(x["avg_return_pct"] == 42.0 for x in out[9][1]))
    tc.assertEqual(out[10][0], "exc")


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
