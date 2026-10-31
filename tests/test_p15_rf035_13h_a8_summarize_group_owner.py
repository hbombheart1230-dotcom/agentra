"""P15 RF-035 (13h): q8_shadow_blocker_review._summarize_group moved to q8_shadow_blocker_group_projection; parity with the pre-move body (stdlib unittest)."""
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

from libs.reporting import q8_shadow_blocker_review as m
from libs.reporting import q8_shadow_blocker_group_projection as owner

FN = "_summarize_group"
FACADE = True
GOLDEN = "d38b16d94933c1494548ae7fffe10bee1c18960424ab4f38faf193c15a1e1a4e"


def _row(symbol, **o):
    r = {"symbol": symbol, "shadow_role": "leader", "rank": 1, "quant_tactic_id": "t1", "reason": "breakout_not_ready",
         "shadow_forward_outcome": {"checkpoints": {"5m": {"status": "observed", "return_pct": 1.0, "mfe_pct": 2.0, "mae_pct": -0.6}}}}
    r.update(o)
    return r


def _scenarios(fn, root, mod):
    rows = [_row("A"), _row("B", shadow_forward_outcome={"checkpoints": {"5m": {"status": "observed", "return_pct": -1.0, "mfe_pct": 0.4, "mae_pct": -0.1}}}), _row("C", shadow_forward_outcome={}), _row("D", shadow_forward_outcome="bad")]
    snap = copy.deepcopy(rows)
    out = [_call(lambda: fn("breakout_not_ready", rows, promotion_allowed=True)), rows == snap]
    out.append(_call(lambda: fn("breakout_not_ready", rows, promotion_allowed=False)))
    out.append(_call(lambda: fn("r", [], promotion_allowed=True)))
    out.append(_call(lambda: fn("r", [rows[2]], promotion_allowed=True)))
    out.append(_call(lambda: fn("r", [_row(f"S{i}", shadow_forward_outcome={"checkpoints": {"5m": {"status": "observed", "return_pct": 1, "mfe_pct": i, "mae_pct": -i}}}) for i in range(8)], promotion_allowed=True)))
    out.append(_call(lambda: fn("r", rows)))
    out.append(_patched(mod, "_decision_for_row", lambda r: "SEAM", lambda: _call(lambda: fn("breakout_not_ready", rows, promotion_allowed=True))))
    out.append(_patched(mod, "_avg", lambda v: 42.0, lambda: _call(lambda: fn("breakout_not_ready", rows, promotion_allowed=True))))
    out.append(_patched(mod, "_checkpoint_values", lambda o: {"available": False}, lambda: _call(lambda: fn("breakout_not_ready", rows, promotion_allowed=True))))
    out.append(_patched(mod, "_text", lambda v: "T", lambda: _call(lambda: fn("breakout_not_ready", rows, promotion_allowed=True))))
    return out


def _expected(tc, out, root):
    r = out[0][1]
    tc.assertTrue(out[1])
    tc.assertEqual((r["candidate_count"], r["observed_count"], r["coverage"], r["decision"], r["raw_decision"]), (4, 2, 0.5, "adjust_and_retest", "adjust_and_retest"))
    tc.assertEqual(out[2][1]["decision"], "retain_under_observation")
    tc.assertTrue(out[2][1]["decision_blocked_by_trust_gate"])
    tc.assertEqual(out[3][1]["candidate_count"], 0)
    tc.assertEqual(out[3][1]["coverage"], 0.0)
    tc.assertEqual(out[4][1]["observed_count"], 0)
    tc.assertEqual(len(out[5][1]["examples"]), 5)
    tc.assertEqual(out[6][0], "exc")
    tc.assertEqual(out[7][1]["raw_decision"], "SEAM")
    tc.assertEqual(out[8][1]["avg_latest_return_pct"], 42.0)
    tc.assertEqual(out[9][1]["observed_count"], 0)


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
