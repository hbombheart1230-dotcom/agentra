"""P15 RF-035 (11h): q8_historical_review._pattern_rows_from_daily_summaries moved to q8_historical_pattern_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import q8_historical_pattern_projection as owner

FN = "_pattern_rows_from_daily_summaries"
FACADE = True
GOLDEN = "26e690cbba04efe67f02f1ccd1776bc717a871d469a76d867a8f023c2d73a8b7"


def _day(rows):
    return {"pattern_performance": {"entry": {"by_pattern": rows}}}


def _scenarios(fn, root, mod):
    reports = root / "reports"
    base = reports / "operator_summary" / "daily"
    _write(base, "2026-10-29/daily_summary.json", _day([
        {"name": "p1", "count": 4, "closed_or_realized_count": 4, "avg_return_pct": 1.0, "win_count": 3, "loss_count": 1, "flat_count": 0, "cost_drag_loss_count": 1},
        {"name": "p2", "count": 2, "avg_return_pct": -2.0, "win_count": 0, "loss_count": 2},
        "bad", {"count": 1, "closed_or_realized_count": 1, "avg_return_pct": "5"}]))
    _write(base, "2026-10-30/daily_summary.json", _day([{"name": "p1", "count": 2, "closed_or_realized_count": 2, "avg_return_pct": 4.0, "win_count": 2}, {"name": "p3", "count": 0, "avg_return_pct": 9}]))
    _write(base, "2026-10-31/daily_summary.json", {"pattern_performance": []})
    _write(base, "2026-11-01/daily_summary.json", "{oops")
    kw = dict(start="2026-10-29", end="2026-11-01", section="entry", group_key="by_pattern")
    out = [_call(lambda: fn(reports, **kw))]
    out.append(_call(lambda: fn(reports, **dict(kw, section="exit"))))
    out.append(_call(lambda: fn(reports, **dict(kw, group_key="nope"))))
    out.append(_call(lambda: fn(root / "none", **kw)))
    out.append(_call(lambda: fn(reports, **dict(kw, start="2026-11-05", end="2026-11-01"))))
    out.append(_patched(mod, "_weighted_avg", lambda total, weight: -1.0, lambda: _call(lambda: fn(reports, **kw))))
    out.append(_patched(mod, "_text", lambda v: "ONE", lambda: _call(lambda: fn(reports, **kw))))
    out.append(_patched(mod, "defaultdict", lambda f: {}, lambda: _call(lambda: fn(reports, **kw))))
    return out


def _expected(tc, out, root):
    rows = out[0][1]
    by = {r["name"]: r for r in rows}
    tc.assertEqual(set(by), {"p1", "p2", "p3", "missing"})
    tc.assertEqual((by["p1"]["count"], by["p1"]["closed_or_realized_count"], by["p1"]["win_count"], by["p1"]["win_rate"], by["p1"]["avg_return_pct"]), (6, 6, 5, 0.8333, 2.0))
    tc.assertEqual(by["p2"]["avg_return_pct"], -2.0)
    tc.assertEqual(by["missing"]["avg_return_pct"], 5.0)
    tc.assertEqual(rows[0]["name"], "p1")
    tc.assertEqual(out[1], ["ok", []])
    tc.assertEqual(out[2], ["ok", []])
    tc.assertEqual(out[3], ["ok", []])
    tc.assertTrue(all(r["avg_return_pct"] == -1.0 for r in out[5][1]))
    tc.assertEqual([r["name"] for r in out[6][1]], ["ONE"])
    tc.assertEqual(out[7][0], "exc")


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
