"""P15 RF-035 (11h): q8_historical_review._daily_summary_rows moved to q8_historical_daily_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import q8_historical_daily_projection as owner

FN = "_daily_summary_rows"
FACADE = True
GOLDEN = "955f522f7aa1947e5415672a1389169dcca9593993145cef9541d8fa2955e8ab"


def _scenarios(fn, root, mod):
    reports = root / "reports"
    base = reports / "operator_summary" / "daily"
    _write(base, "2026-10-29/daily_summary.json", {
        "metrics": {"trade_count": "5", "closed_trade_count": 3, "return_sample_count": "2", "unavailable_return_count": 1, "win_rate": "0.5", "avg_return_pct": "1.5%", "truth_surface_count": 4},
        "quant_shadow_candidate_evaluation": {"candidate_count": 10, "deduped_candidate_count": 8, "duplicate_candidate_count": 2, "evaluated_count": 7, "would_enter_count": 3, "forward_outcome_coverage": "0.7",
            "evaluation_trust_gate": {"status": "ok", "promotion_allowed": True, "trusted_forward_count": 5, "trusted_forward_coverage": 0.6, "duplicate_rate": 0.1}},
        "market_regime_rail_review": {"rail_id": "rail_x"}})
    _write(base, "2026-10-30/daily_summary.json", {"metrics": "bad", "quant_shadow_candidate_evaluation": [], "market_regime_rail_review": {"market_regime_rail": "alt"}})
    _write(base, "2026-10-31/daily_summary.json", "{oops")
    out = [_call(lambda: fn(reports, start="2026-10-29", end="2026-11-01"))]
    out.append(_call(lambda: fn(reports, start="2026-11-01", end="2026-10-29")))
    out.append(_call(lambda: fn(root / "none", start="2026-10-29", end="2026-10-30")))
    out.append(_patched(mod, "_float", lambda v: 7.0, lambda: _call(lambda: fn(reports, start="2026-10-29", end="2026-10-29"))))
    out.append(_patched(mod, "_int", lambda v: 9, lambda: _call(lambda: fn(reports, start="2026-10-29", end="2026-10-29"))))
    out.append(_patched(mod, "_text", lambda v: "T", lambda: _call(lambda: fn(reports, start="2026-10-29", end="2026-10-29"))))
    out.append(_patched(mod, "_read_json", lambda p: {"metrics": {"trade_count": 1}}, lambda: _call(lambda: fn(reports, start="2026-10-29", end="2026-10-29"))))
    return out


def _expected(tc, out, root):
    rows = out[0][1]
    tc.assertEqual([r["day"] for r in rows], ["2026-10-29", "2026-10-30", "2026-10-31"])
    a = rows[0]
    tc.assertEqual((a["trade_count"], a["win_rate"], a["avg_return_pct"], a["shadow_candidate_count"], a["q8_trust_gate_status"], a["q8_promotion_allowed"], a["market_regime_rail"]), (5, 0.5, 1.5, 10, "ok", True, "rail_x"))
    tc.assertEqual(rows[1]["market_regime_rail"], "alt")
    tc.assertEqual(rows[1]["trade_count"], 0)
    tc.assertEqual(rows[2]["trade_count"], 0)
    tc.assertEqual(out[1], ["ok", []])
    tc.assertEqual(out[2], ["ok", []])
    tc.assertEqual(out[3][1][0]["win_rate"], 7.0)
    tc.assertEqual(out[4][1][0]["trade_count"], 9)
    tc.assertEqual(out[5][1][0]["q8_trust_gate_status"], "T")
    tc.assertEqual(out[6][1][0]["trade_count"], 1)


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
