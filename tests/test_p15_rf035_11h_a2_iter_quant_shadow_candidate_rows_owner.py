"""P15 RF-035 (11h): q8_historical_review._iter_quant_shadow_candidate_rows moved to q8_historical_read_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import q8_historical_read_projection as owner

FN = "_iter_quant_shadow_candidate_rows"
FACADE = True
GOLDEN = "a9fd7963acb9885c70ad0ebabbe2c285d2d10504cc9ce97b1b09e2b2485e0ef4"


def _scenarios(fn, root, mod):
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    cand = root / "data" / "logs" / "quant_shadow_candidates"
    _write(cand, "2026-10-29/a.json", {"candidates": [{"symbol": "A", "n": 1}, "bad", {"symbol": "B"}]})
    _write(cand, "2026-10-29/latest.json", {"candidates": [{"symbol": "LATEST"}]})
    _write(cand, "2026-10-30/b.json", {"candidates": [{"symbol": "C"}]})
    _write(cand, "2026-10-30/a.json", {"candidates": [{"symbol": "D"}]})
    _write(cand, "2026-10-30/bad.json", "{oops")
    _write(cand, "2026-10-30/none.json", {"candidates": None})
    (cand / "2026-10-31").mkdir(parents=True, exist_ok=True)
    out = [_call(lambda: list(fn(reports, start="2026-10-29", end="2026-10-31")))]
    out.append(_call(lambda: list(fn(reports, start="2026-10-31", end="2026-10-29"))))
    out.append(_call(lambda: list(fn(reports, start="2026-10-30", end="2026-10-30"))))
    out.append(_call(lambda: list(fn(root / "none" / "reports", start="2026-10-29", end="2026-10-30"))))
    gen = fn(reports, start="bad", end="2026-10-30")
    out.append(["created", type(gen).__name__])
    out.append(_call(lambda: list(gen)))
    row = next(iter(fn(reports, start="2026-10-29", end="2026-10-29")))
    row["symbol"] = "MUTATED"
    out.append(_call(lambda: [r["symbol"] for r in fn(reports, start="2026-10-29", end="2026-10-29")]))
    out.append(_patched(mod, "_read_json", lambda p: {"candidates": [{"symbol": "SEAM"}]}, lambda: _call(lambda: list(fn(reports, start="2026-10-30", end="2026-10-30")))))
    out.append(_patched(mod, "_iter_days", lambda s, e: iter(["2026-10-30"]), lambda: _call(lambda: [r["symbol"] for r in fn(reports, start="x", end="y")])))
    out.append(_patched(mod, "_quant_shadow_candidate_root", lambda r: root / "elsewhere", lambda: _call(lambda: list(fn(reports, start="2026-10-29", end="2026-10-30")))))
    return out


def _expected(tc, out, root):
    tc.assertEqual([r["symbol"] for r in out[0][1]], ["A", "B", "D", "C"])
    tc.assertEqual(out[1], ["ok", []])
    tc.assertEqual([r["symbol"] for r in out[2][1]], ["D", "C"])
    tc.assertEqual(out[3], ["ok", []])
    tc.assertEqual(out[4], ["created", "generator"])
    tc.assertEqual(out[5][:2], ["exc", "ValueError"])
    tc.assertEqual(out[6], ["ok", ["A", "B"]])
    tc.assertEqual(out[7], ["ok", [{"symbol": "SEAM"}] * 4])
    tc.assertEqual(out[8], ["ok", ["D", "C"]])
    tc.assertEqual(out[9], ["ok", []])


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
        self.assertTrue(len(stmts) == 1 and isinstance(stmts[0], ast.Expr) and isinstance(stmts[0].value, ast.YieldFrom))
        self.assertNotIn("import " + m.__name__.split(".")[-1], inspect.getsource(owner))

    def test_expected_values(self):
        with tempfile.TemporaryDirectory() as t:
            _expected(self, _scenarios(getattr(m, FN), Path(t), m), Path(t))


if __name__ == "__main__":
    unittest.main()
