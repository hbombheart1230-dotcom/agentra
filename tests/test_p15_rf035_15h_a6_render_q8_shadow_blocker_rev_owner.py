"""P15 RF-035 (15h): q8_shadow_blocker_review.render_q8_shadow_blocker_review_markdown moved to q8_shadow_blocker_markdown_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import q8_shadow_blocker_markdown_projection as owner

FN = "render_q8_shadow_blocker_review_markdown"
FACADE = True
GOLDEN = "c560b0ed09daf318be08748a74105bfe473832d2c9311febddec558a5b628e0b"


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


def _scenarios(fn, root, mod):
    base = {"candidate_count": 0, "groups": [], "evaluation_trust_gate": {"status": "blocked", "promotion_allowed": False}}
    rich = {
        "candidate_count": 3, "raw_candidate_count": 4, "duplicate_count": 1, "promotion_allowed": False,
        "evaluation_trust_gate": {"status": "blocked", "promotion_allowed": False},
        "market_regime_rail": {"rationale": "why", "q8_review_focus": ["a", "", "b"]},
        "groups": [
            {"reason": "breakout_not_ready", "candidate_count": 2, "observed_count": 1, "avg_latest_return_pct": 1.23456, "decision": "adjust_and_retest",
             "examples": [{"symbol": "A", "role": "r", "rank": 0, "latest_return_pct": 0.5}, "junk", {"symbol": "B"}]},
            "junk", {"reason": "empty"},
        ],
    }
    return [
        _call(lambda: fn(base, day="2026-10-31")),
        _call(lambda: fn(rich, day="d")),
        _call(lambda: fn({}, day="")),
        _call(lambda: fn(MappingProxyType(base), day="x")),
        _call(lambda: fn(None, day="x")),
        _call(lambda: fn(base)),
        _patched(mod, "Mapping", tuple, lambda: _call(lambda: fn(rich, day="d"))),
    ]


def _expected(tc, out, root):
    text = out[0][1]
    tc.assertTrue(text.startswith("# Q8 Shadow Blocker Review (2026-10-31)"))
    tc.assertIn("candidate_count: **0**", text)
    tc.assertTrue(text.endswith("\n") and not text.endswith("\n\n"))
    tc.assertIn("## Examples: breakout_not_ready", out[1][1])
    tc.assertIn("rank `0`", out[1][1])
    tc.assertEqual(out[4][0], "exc")
    tc.assertEqual(out[5][0], "exc")
    tc.assertNotEqual(out[6][1], out[1][1])


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
