"""P15 RF-035 (15h): post_exit_shadow_recap.opening_rank1_eod_fallback_row moved to post_exit_shadow_eod_fallback_projection; parity with the pre-move body (stdlib unittest)."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from libs.reporting import post_exit_shadow_recap as m
from libs.reporting import post_exit_shadow_eod_fallback_projection as owner

FN = "opening_rank1_eod_fallback_row"
FACADE = True
GOLDEN = "aaf40aa6a1e1b47304e69d1872da9ec6caabc1a8deca1f5b0358b67fb0e43481"


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


def _put(root, day, episodes):
    p = Path(root) / "evaluation" / "opening_rank1_shadow" / day / "opening_rank1_shadow_daily.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"episodes": episodes}), encoding="utf-8")


def _scenarios(fn, root, mod):
    root = Path(root)
    eod = lambda **k: {"checkpoints": {"EOD": k}}
    _put(root, "2026-10-31", [
        dict(symbol="000660", **eod(status="observed", price=5)),
        dict(symbol="005930", **eod(status="observed", price=100, observed_epoch=1700000000, volume=7)),
    ])
    _put(root, "2026-10-29", [dict(symbol="005930", **eod(status="observed", observed_price="12.5"))])
    _put(root, "2026-10-30", [
        dict(symbol="005930", **eod(status="pending", price=1)),
        dict(symbol="005930", **eod(status="observed", price="bad")),
        dict(symbol="005930", **eod(status="OBSERVED", price=0, observed_ts=1700000100)),
    ])
    _put(root, "bad-day", [dict(symbol="005930", **eod(status="observed", price=3))])
    out = [
        _call(lambda: fn(reports_root=root, day="2026-10-31", symbol="005930")),
        _call(lambda: fn(reports_root=root, day="2026-10-31", symbol="999999")),
        _call(lambda: fn(reports_root=root, day="2026-10-29", symbol="005930")),
        _call(lambda: fn(reports_root=root, day="2026-10-30", symbol="005930")),
        _call(lambda: fn(reports_root=root, day="bad-day", symbol="005930")),
        _call(lambda: fn(reports_root=root, day="nofile", symbol="005930")),
        _call(lambda: fn(reports_root=str(root), day="2026-10-31", symbol="")),
    ]
    out.append(_patched(mod, "_read_json", lambda path: {"episodes": [{"symbol": "005930", "checkpoints": {"EOD": {"status": "observed", "price": 9, "observed_epoch": 1700000000}}}]}, lambda: _call(lambda: fn(reports_root=root, day="x", symbol="005930"))))
    return out


def _expected(tc, out, root):
    row, meta = out[0][1]
    tc.assertEqual((row["close"], row["source"], row["ts"], row["volume"], row["eod_fallback"]), (100.0, "opening_rank1_shadow.EOD", 1700000000, 7, True))
    tc.assertTrue(meta["applied"])
    tc.assertEqual(meta["source"], "opening_rank1_shadow.EOD")
    tc.assertFalse(out[1][1][1]["applied"])
    tc.assertIsNone(out[1][1][0])
    tc.assertEqual(out[1][1][1]["reason"], "matching_observed_opening_rank1_eod_not_found")
    tc.assertEqual(out[2][1][0]["close"], 12.5)
    tc.assertEqual(out[2][1][0]["ts"], 1793255400)
    tc.assertEqual(out[4][1][0], None)
    tc.assertEqual(out[3][1][0]["close"], 0.0)
    tc.assertEqual(out[5][1][1]["applied"], False)
    tc.assertEqual(out[7][1][0]["close"], 9.0)


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
        self.assertNotIn("import post_exit_shadow_recap", inspect.getsource(owner))

    def test_expected_values(self):
        with tempfile.TemporaryDirectory() as t:
            _expected(self, _scenarios(getattr(m, FN), Path(t), m), Path(t))


if __name__ == "__main__":
    unittest.main()
