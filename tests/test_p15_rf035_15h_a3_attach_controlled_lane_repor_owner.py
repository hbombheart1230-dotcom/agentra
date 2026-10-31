"""P15 RF-035 (15h): controlled_mock_lane_report.attach_controlled_lane_report_surface moved to controlled_lane_attach_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import controlled_lane_attach_projection as owner

FN = "attach_controlled_lane_report_surface"
FACADE = True
GOLDEN = "42bbe0ae3cf1048507630db3914e10a2c6bf64e0b998ca298ffe534ad425a192"


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
    out = []
    rep = {"fact_payload": {"trade": {"symbol": "A"}}}
    r = fn(rep, {"controlled_mock_lane": {"lane_id": "L"}})
    out.append(["same", [r is rep, rep["controlled_mock_lane"]["lane_id"], rep["fact_payload"]["trade"]["controlled_mock_lane"]["lane_id"]]])
    rep2 = {"fact_payload": {"trade": {"symbol": "A"}}}
    out.append(["empty", [fn(rep2, {}) is rep2, rep2]])
    rep3 = {}
    out.append(_call(lambda: fn(rep3, {"trade_lifecycle": {"controlled_mock_lane": {"lane_id": "TL"}}})) + [rep3])
    rep4 = {"fact_payload": {"trade": {"controlled_mock_lane": {"lane_id": "OLD"}}}}
    out.append(_call(lambda: fn(rep4, {"lifecycle_bundle": {"controlled_mock_lane": {"lane_id": "LB"}}})) + [rep4])
    rep5 = {}
    out.append(_call(lambda: fn(rep5, {"trade_lifecycle": {"entry": {"controlled_mock_lane": {"lane_id": "EN"}}}})) + [rep5])
    out.append(_call(lambda: fn({}, None)))
    rep6 = {}
    out.append(_patched(mod, "_first_mapping", lambda *v: {"patched": len(v)}, lambda: _call(lambda: fn(rep6, {}))) + [rep6])
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["same", [True, "L", "L"]])
    tc.assertEqual(out[1], ["empty", [True, {"fact_payload": {"trade": {"symbol": "A"}}}]])
    tc.assertEqual(out[2][2], {"controlled_mock_lane": {"lane_id": "TL"}})
    tc.assertEqual(out[3][2]["fact_payload"]["trade"]["controlled_mock_lane"]["lane_id"], "OLD")
    tc.assertEqual(out[4][2]["controlled_mock_lane"]["lane_id"], "EN")
    tc.assertEqual(out[5][0], "exc")
    tc.assertEqual(out[6][2], {"controlled_mock_lane": {"patched": 4}})


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
