"""P15 RF-035 (15h): controlled_mock_lane_report.apply_controlled_lane_story_surface moved to controlled_lane_story_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import controlled_lane_story_projection as owner

FN = "apply_controlled_lane_story_surface"
FACADE = True
GOLDEN = "4f3b5be5544cc760f15fe32b6d313d6e5769deb07734e5a2ef85773f337fbaa8"


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
    si = {"entry_summary": {"x": 1}}
    r = fn(si, {"lane_id": "L", "symbol": "A"})
    out.append(["basic", [r is not si, si, r]])
    out.append(_call(lambda: fn({"a": 1}, {})))
    full = {
        "entry_summary": {"x": 1}, "lifecycle_summary": {"y": 2}, "scanner_evidence": {"z": 3},
        "trade_lifecycle": {"entry": {"e": 1}}, "lifecycle": {"q": 1},
        "lifecycle_bundle": {"lifecycle": {"entry": {"b": 1}}},
    }
    out.append(_call(lambda: fn(full, {"lane_id": "Q10_INDEX", "lane_label": "LBL", "symbol": "005930", "signal_id": "s9"})))
    out.append(_call(lambda: fn({"b": 1}, MappingProxyType({"lane_id": "P", "symbol": "S"}))))
    out.append(_call(lambda: fn(None, {"lane_id": "L"})))
    out.append(_patched(mod, "_mapping", lambda v: {"lane_id": "PM", "symbol": "PS"} if v and "lane_id" in v else {}, lambda: _call(lambda: fn({}, {"lane_id": "L"}))))
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0][1][0], True)
    tc.assertEqual(out[0][1][1], {"entry_summary": {"x": 1}})
    res = out[0][1][2]
    tc.assertEqual(res["scanner_selection_trace"]["selection_authority"], "deterministic_independent_lane")
    tc.assertIsNone(res["scanner_selection_trace"]["selected_rank"])
    tc.assertEqual(res["entry_summary"]["controlled_mock_lane"]["lane_id"], "L")
    tc.assertEqual(out[1], ["ok", {"a": 1}])
    full = out[2][1]
    tc.assertEqual(full["lifecycle_bundle"]["lifecycle"]["entry"]["controlled_mock_lane"]["lane_id"], "Q10_INDEX")
    tc.assertEqual(full["scanner_evidence"]["independent_lane"]["symbol"], "005930")
    tc.assertEqual(out[4][0], "exc")
    tc.assertEqual(out[5][1]["controlled_mock_lane"]["lane_id"], "PM")


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
