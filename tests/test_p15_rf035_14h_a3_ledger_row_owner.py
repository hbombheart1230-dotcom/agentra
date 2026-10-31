"""P15 RF-035 (14h): controlled_mock_lane_report._ledger_row moved to controlled_lane_ledger_projection; parity with the pre-move body (stdlib unittest)."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from libs.reporting import controlled_mock_lane_report as m
from libs.reporting import controlled_lane_ledger_projection as owner

FN = "_ledger_row"
GOLDEN = "ea3ba511de21f5cae669875199948e7f6697df184f048cbc238978860c2f2a73"


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
    _ledger(root, "d1", [{"symbol": "A", "order_id": "0007", "n": 1}, {"symbol": "A", "order_id": "7", "n": 2}, {"symbol": "A", "run_id": "r9", "n": 3}, {"symbol": "B", "order_id": "7", "n": 4}, "junk"])
    _ledger(root, "bad", "{not json")
    _ledger(root, "nomap", "[1, 2]")
    out = [
        _call(lambda: fn(root=root, day="d1", symbol="A", order_id="007")),
        _call(lambda: fn(root=root, day="d1", symbol="A", run_id="r9")),
        _call(lambda: fn(root=root, day="d1", symbol="A", order_id="999", run_id="r9")),
        _call(lambda: fn(root=root, day="d1", symbol="A")),
        _call(lambda: fn(root=root, day="d1", symbol="Z", order_id="7")),
        _call(lambda: fn(root=root, day="bad", symbol="A", order_id="7")),
        _call(lambda: fn(root=root, day="nomap", symbol="A", order_id="7")),
        _call(lambda: fn(root=root, day="missing", symbol="A")),
        _call(lambda: fn(root=Path(root) / "x", day="d1", symbol="A")),
    ]
    out.append(_patched(mod, "_text", lambda v: "A" if v == "B" else str(v or "").strip(), lambda: _call(lambda: fn(root=root, day="d1", symbol="A", order_id="7"))))
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", {"symbol": "A", "order_id": "7", "n": 2}])
    tc.assertEqual(out[1], ["ok", {"symbol": "A", "run_id": "r9", "n": 3}])
    tc.assertEqual(out[2], ["ok", {"symbol": "A", "run_id": "r9", "n": 3}])
    tc.assertEqual(out[3], ["ok", {}])
    tc.assertEqual(out[4], ["ok", {}])
    tc.assertEqual(out[5:9], [["ok", {}]] * 4)
    tc.assertEqual(out[9], ["ok", {"symbol": "B", "order_id": "7", "n": 4}])


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
