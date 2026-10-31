"""P15 RF-035 (12h): q8_historical_review.render_q8_historical_review_markdown moved to q8_historical_markdown_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import q8_historical_markdown_projection as owner

FN = "render_q8_historical_review_markdown"
FACADE = True
GOLDEN = "7e57dc4d4089776f3b96d562804a7e80e5f1f2146c82d3c495ba81a355fa255e"



def _daily(base, day, q=None, q8=None, metrics=None, pattern=None, rail=None):
    payload = {"metrics": metrics or {"trade_count": 2, "closed_trade_count": 2, "return_sample_count": 2, "win_rate": 0.5, "avg_return_pct": 1.0}}
    if q is not None:
        payload["quant_shadow_candidate_evaluation"] = q
    if q8 is not None:
        payload["q8_shadow_blocker_review"] = q8
    if pattern is not None:
        payload["pattern_performance"] = pattern
    if rail is not None:
        payload["market_regime_rail_review"] = rail
    _write(base / "operator_summary" / "daily", f"{day}/daily_summary.json", payload)


def _build_tree(root):
    reports = root / "reports"
    gate = {"status": "ok", "promotion_allowed": True, "trusted_forward_count": 5, "trusted_forward_coverage": 0.6, "duplicate_rate": 0.1}
    q = {"candidate_count": 10, "deduped_candidate_count": 8, "duplicate_candidate_count": 2, "evaluated_count": 7, "would_enter_count": 3, "forward_outcome_coverage": 0.7, "evaluation_trust_gate": gate,
         "by_reason": [{"name": "breakout_not_ready", "count": 4}, {"name": "pullback_not_mature", "count": 2}, "bad"],
         "by_role": [{"name": "leader", "count": 3}], "by_tactic_id": [{"name": "t1", "count": 5}],
         "below_vwap_reclaim_observation": {"by_subtype": [{"name": "st1", "count": 2}], "by_subtype_v2": [{"name": "v2a", "count": 1}]},
         "entry_lane_forward_outcomes": {"by_lane_subtype": [{"name": "vwap_reclaim:true_below_vwap_failure", "candidate_count": 40, "observed_count": 35, "avg_return_5m_pct": 0.2, "avg_return_15m_pct": 0.3, "avg_mae_5m_pct": -0.1},
                                                              {"name": "other:x", "candidate_count": 1}, "bad"]}}
    q8 = {"groups": [{"reason": "below_vwap_reclaim_not_ready", "candidate_count": 12, "observed_count": 9, "avg_latest_return_pct": 0.5, "missed_opportunity_rate": 0.1, "adverse_rate": 0.2},
                     {"name": "breakout_not_ready", "candidate_count": 7, "observed_count": 4}, {"reason": ""}, "bad"]}
    pattern = {"strategist": {"by_tactical_strategy": [{"name": "p1", "count": 4, "closed_or_realized_count": 4, "avg_return_pct": 1.0, "win_count": 3, "loss_count": 1}]},
               "monitor_exit": {"by_exit_reason": [{"name": "stop", "count": 2, "closed_or_realized_count": 2, "avg_return_pct": -1.5, "win_count": 0, "loss_count": 2}]}}
    _daily(reports, "2026-10-29", q=q, q8=q8, pattern=pattern, rail={"rail_id": "rail_x"})
    _daily(reports, "2026-10-30", q={"candidate_count": 3, "by_reason": [{"name": "breakout_not_ready", "count": 1}]}, q8={"groups": []})
    summary = {"trade": {"trade_id": "T1", "symbol": "005930", "status": "closed", "tactical_strategy": "defensive_observe"}, "truth_surface": {"pnl_pct": -0.02, "truth_source": "broker"},
               "decision_flow": {"entry_reason": "er", "exit_reason": "et"}, "quant_tactic": {}}
    for i in range(6):
        _write(reports, f"trades/2026-10-29/T{i}/reports/ai_trade_summary.json", dict(summary, trade={"trade_id": f"T{i}", "symbol": "005930", "status": "closed", "tactical_strategy": "defensive_observe"}))
    cand = root / "data" / "logs" / "quant_shadow_candidates"
    _write(cand, "2026-10-29/a.json", {"candidates": [{"symbol": "A", "price": 1000}, {"symbol": "B"}]})
    return reports


def _scenarios(fn, root, mod):
    reports = _build_tree(root)
    built = mod.build_q8_historical_review_payload(reports_root=reports, start="2026-10-29", end="2026-10-30")
    empty = mod.build_q8_historical_review_payload(reports_root=root / "empty", start="2026-10-30", end="2026-10-30")
    snap = copy.deepcopy(built)
    out = [_call(lambda: fn(built)), built == snap, _call(lambda: fn(empty)), _call(lambda: fn({})), _call(lambda: fn(None))]
    out.append(_call(lambda: fn(dict(built, daily_rows=[], trade_by_tactic=[], q8_blocker_groups=[], below_vwap_reclaim_subtype_forward=[]))))
    out.append(_patched(mod, "_md_table", lambda headers, rows: ["TABLE:" + ",".join(map(str, headers))], lambda: _call(lambda: fn(built))))
    out.append(_patched(mod, "_text", lambda v: "T", lambda: _call(lambda: fn(built))))
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0][0], "ok")
    tc.assertIsInstance(out[0][1], str)
    tc.assertTrue(out[1])
    tc.assertTrue(out[0][1].endswith("\n") or out[0][1] != "")
    tc.assertEqual(out[2][0], "ok")
    tc.assertEqual(out[4][0], "exc")
    tc.assertIn("TABLE:", out[6][1])


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
