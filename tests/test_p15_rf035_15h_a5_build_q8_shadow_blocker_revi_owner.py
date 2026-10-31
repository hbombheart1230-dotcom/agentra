"""P15 RF-035 (15h): q8_shadow_blocker_review.build_q8_shadow_blocker_review moved to q8_shadow_blocker_review_build_projection; parity with the pre-move body (stdlib unittest)."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from libs.reporting import q8_shadow_blocker_review as m
from libs.reporting import q8_shadow_blocker_review_build_projection as owner

FN = "build_q8_shadow_blocker_review"
FACADE = True
GOLDEN = "f316b500f6604f3f70f22307ffcb943e1803ecb27351c89d69ac3ccfc934bd6e"


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


def _payloads():
    return [{"generated_at": "t1", "candidates": [
        {"reason": "breakout_not_ready", "symbol": "A", "role": "r", "rank": 1},
        {"reason": "breakout_not_ready", "symbol": "A", "role": "r", "rank": 1},
        {"reason": "other_reason", "symbol": "B"},
        "junk",
    ]}, "bad"]


def _scenarios(fn, root, mod):
    gate = {"evaluation_trust_gate": {"status": "blocked", "promotion_allowed": False}}
    ok_gate = {"evaluation_trust_gate": {"status": "ok", "promotion_allowed": True}}
    out = [
        _call(lambda: fn([], review_reasons=("breakout_not_ready",), quant_shadow_evaluation=gate)),
        _call(lambda: fn(_payloads(), review_reasons=("breakout_not_ready", "pullback_not_mature"), market_regime_rail={"k": "v"})),
        _call(lambda: fn(_payloads(), review_reasons=("breakout_not_ready",), quant_shadow_evaluation=ok_gate)),
        _call(lambda: fn([], review_reasons=())),
        _call(lambda: fn(None, review_reasons=("a",))),
        _call(lambda: fn(_payloads(), review_reasons=m.DEFAULT_REVIEW_REASONS)),
    ]
    out.append(_patched(mod, "_candidate_rows", lambda p: [{"reason": "x", "symbol": "S"}], lambda: _call(lambda: fn([], review_reasons=("x",)))))
    out.append(_patched(mod, "_summarize_group", lambda reason, rows, *, promotion_allowed: {"reason": reason, "n": len(rows), "p": promotion_allowed, "observed_count": 2}, lambda: _call(lambda: fn(_payloads(), review_reasons=("breakout_not_ready", "z")))))
    return out


def _expected(tc, out, root):
    r = out[0][1]
    tc.assertEqual((r["candidate_count"], r["review_reason_count"], r["behavior_effect"], r["promotion_allowed"]), (0, 1, "evaluation_only", False))
    tc.assertEqual(r["schema_version"], "q8_shadow_blocker_review.v1")
    tc.assertEqual(out[1][1]["market_regime_rail"], {"k": "v"})
    tc.assertEqual(out[1][1]["raw_candidate_count"], 3)
    tc.assertEqual(out[2][1]["promotion_allowed"], True)
    tc.assertEqual(out[3][1]["groups"], [])
    tc.assertEqual(out[4][0], "exc")
    tc.assertEqual(out[5][1]["review_reason_count"], len(m.DEFAULT_REVIEW_REASONS))
    tc.assertEqual(out[6][1]["candidate_count"], 1)
    tc.assertEqual(out[7][1]["observed_review_candidate_count"], 4)
    tc.assertEqual(out[7][1]["groups"][1], {"reason": "z", "n": 0, "p": False, "observed_count": 2})


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
        self.assertNotIn("import q8_shadow_blocker_review", inspect.getsource(owner))

    def test_expected_values(self):
        with tempfile.TemporaryDirectory() as t:
            _expected(self, _scenarios(getattr(m, FN), Path(t), m), Path(t))


if __name__ == "__main__":
    unittest.main()
