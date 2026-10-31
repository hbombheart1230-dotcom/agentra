"""P15 RF-035 (11h): q8_historical_review._extract_trade_rows moved to q8_historical_trade_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import q8_historical_trade_projection as owner

FN = "_extract_trade_rows"
FACADE = True
GOLDEN = "3ad9fa91a1ee187fa5e5a9cc7b0248b0a27d1859c5a402aca328ef01cc4b0a9a"


def _summary(trade_id, **o):
    d = {"trade": {"trade_id": trade_id, "symbol": " 005930 ", "status": "closed", "tactical_strategy": "t1", "playbook": "pb"},
         "truth_surface": {"pnl_pct": 0.25, "truth_source": "broker"}, "decision_flow": {"entry_reason": "er", "exit_trigger": "et", "playbook": "dpb"},
         "quant_tactic": {"tactic_id": "qt"}}
    d.update(o)
    return d


def _scenarios(fn, root, mod):
    reports = root / "reports"
    _write(reports, "trades/2026-10-29/T1/reports/ai_trade_summary.json", _summary("T1"))
    _write(reports, "trades/2026-10-30/SYM/T2/reports/ai_trade_summary.json", _summary("", truth_surface={"pnl_pct": 15}))
    _write(reports, "trades/2026-10-30/T3/reports/ai_trade_summary.json", {"trade": "bad", "truth_surface": [], "decision_flow": None, "quant_tactic": 5})
    _write(reports, "trades/2026-10-31/T4/reports/ai_trade_summary.json", _summary("T4"))
    _write(reports, "trades/2026-11-05/T5/reports/ai_trade_summary.json", _summary("T5"))
    _write(reports, "trades/2026-10-30/T6/reports/ai_trade_summary.json", "{oops")
    out = [_call(lambda: fn(reports, start="2026-10-29", end="2026-10-31"))]
    out.append(_call(lambda: fn(reports, start="2026-10-30", end="2026-10-30")))
    out.append(_call(lambda: fn(reports, start="2026-12-01", end="2026-12-02")))
    out.append(_call(lambda: fn(root / "none", start="a", end="z")))
    out.append(_patched(mod, "_pct_from_ratio", lambda v: 99.0, lambda: _call(lambda: fn(reports, start="2026-10-29", end="2026-10-29"))))
    out.append(_patched(mod, "_read_json", lambda p: {}, lambda: _call(lambda: fn(reports, start="2026-10-29", end="2026-10-29"))))
    out.append(_patched(mod, "_trade_id_from_path", lambda p: "FROMPATH", lambda: _call(lambda: fn(reports, start="2026-10-30", end="2026-10-30"))))
    return out


def _expected(tc, out, root):
    rows = out[0][1]
    tc.assertEqual([r["trade_id"] for r in rows if r["day"] == "2026-10-29"], ["T1"])
    first = rows[0]
    tc.assertEqual((first["symbol"], first["pnl_pct"], first["tactic"], first["playbook"], first["entry_reason"], first["exit_reason"]), ("005930", 25.0, "qt", "pb", "er", "et"))
    tc.assertEqual(list(first), ["day", "trade_id", "symbol", "status", "pnl_pct", "truth_source", "tactic", "playbook", "entry_reason", "exit_reason"])
    tc.assertEqual(out[2], ["ok", []])
    tc.assertEqual(out[3], ["ok", []])
    tc.assertEqual(out[4][1][0]["pnl_pct"], 99.0)
    tc.assertEqual(out[6][1][0]["trade_id"] in ("FROMPATH", "T3", "T2"), True)


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
