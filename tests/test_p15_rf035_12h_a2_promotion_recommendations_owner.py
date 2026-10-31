"""P15 RF-035 (12h): q8_historical_review._promotion_recommendations moved to q8_historical_recommendation_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import q8_historical_recommendation_projection as owner

FN = "_promotion_recommendations"
FACADE = False
GOLDEN = "2d5a79137bfc7d7b4137669e5ecf58425d56cde9f26713932bd718e3bce9e140"


def _scenarios(fn, root, mod):
    payloads = [
        {"q8_blocker_groups": [], "trade_by_tactic": []},
        {"trade_by_tactic": [{"name": "defensive_observe", "count": 5, "avg_return_pct": -0.5}]},
        {"trade_by_tactic": [{"name": "defensive_observe", "count": 4, "avg_return_pct": -0.5}]},
        {"trade_by_tactic": [{"name": "defensive_observe", "count": 9, "avg_return_pct": 0.5}]},
        {"q8_blocker_groups": [{"reason": "below_vwap_reclaim_not_ready", "candidate_count": 3, "observed_count": 2, "avg_latest_return_pct": 0.1, "missed_opportunity_rate": 0.2, "adverse_rate": 0.3},
                               {"reason": "volume_confirmation_missing", "candidate_count": 1}, {"reason": "unknown"}, "bad"]},
        {"below_vwap_reclaim_subtype_forward": [{"name": "a", "avg_return_15m_pct": 0.1, "avg_return_5m_pct": 0.9, "observed_count": 3}, {"name": "b", "avg_return_15m_pct": 0.5, "avg_return_5m_pct": 0.1, "observed_count": 1}]},
        {}, None, {"q8_blocker_groups": "bad"}, {"trade_by_tactic": ["bad"]},
    ]
    return [_call(lambda p=p: fn(p)) for p in payloads]


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", []])
    tc.assertEqual([r["candidate"] for r in out[1][1]], ["risk_off_defensive_observe_no_entry_policy"])
    tc.assertEqual(out[2], ["ok", []])
    tc.assertEqual(out[3], ["ok", []])
    tc.assertEqual([r["candidate"] for r in out[4][1]], ["below_vwap_reclaim_not_ready", "volume_confirmation_missing"])
    tc.assertIn("strongest=b", out[5][1][0]["reason"])
    tc.assertEqual(out[6], ["ok", []])
    tc.assertEqual(out[7][0], "exc")
    tc.assertEqual(out[9][0], "exc")


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
