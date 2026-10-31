"""P15 RF-035 (14h): controlled_mock_lane_report._first_mapping moved to controlled_lane_scalar_projection; parity with the pre-move body (stdlib unittest)."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from libs.reporting import controlled_mock_lane_report as m
from libs.reporting import controlled_lane_scalar_projection as owner

FN = "_first_mapping"
GOLDEN = "aa73b1de45f4a2b2813c57383d1ccabef844cd86991c4ddc6eb29d119baa53a6"


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


def _ledger(root, day, rows):
    p = Path(root) / "data" / "logs" / "controlled_mock_lanes" / day / "lane_submissions.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(rows if isinstance(rows, str) else json.dumps({"submissions": rows}), encoding="utf-8")


LANE = {"lane_id": "BTC_WOORI", "symbol": "005930", "signal_id": "s1", "signal_epoch": 5, "run_id": "r1", "order_id": "0007", "score": 3, "evidence": {"a": 1}, "daily_limit": 2, "reservation": {"k": "v"}}
STRAT = {"controlled_mock_lane": True, "strategy_horizon": "intraday", "expected_hold_window": {"min_sec": 1}, "llm_used": False, "horizon_revision_allowed": False}
REPORT = {"controlled_mock_lane": {"lane_id": "Q10_INDEX", "lane_label": "L", "signal_id": "sx", "evidence": {"x": 1, "y": ""}, "expected_hold_window": {"min_sec": 1, "target_sec": 2}, "score": 0.5, "scanner_rank_applicable": False}}

def _scenarios(fn, root, mod):
    out = [
        _call(lambda: fn({}, {"a": 1}, {"b": 2})),
        _call(lambda: fn(None, "x", [1], MappingProxyType({"c": 3}))),
        _call(lambda: fn()),
        _call(lambda: fn({}, None)),
    ]
    d = {"k": 1}
    r = fn(d)
    r["k"] = 2
    out.append(["copy", [d["k"], r is not d]])
    out.append(_patched(mod, "_mapping", lambda v: {"p": v} if v == 2 else {}, lambda: _call(lambda: fn(1, 2, 3))))
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", {"a": 1}])
    tc.assertEqual(out[1], ["ok", {"c": 3}])
    tc.assertEqual(out[2], ["ok", {}])
    tc.assertEqual(out[3], ["ok", {}])
    tc.assertEqual(out[4], ["copy", [1, True]])
    tc.assertEqual(out[5], ["ok", {"p": 2}])


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
        self.assertNotIn("import controlled_mock_lane_report", inspect.getsource(owner))

    def test_expected_values(self):
        with tempfile.TemporaryDirectory() as t:
            _expected(self, _scenarios(getattr(m, FN), Path(t), m), Path(t))


if __name__ == "__main__":
    unittest.main()
