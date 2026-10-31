"""P15 RF-035 (10h): q8_historical_review._decision_for_reclaim_subtype moved to q8_historical_decision_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import q8_historical_decision_projection as owner

FN = "_decision_for_reclaim_subtype"
FACADE = True
GOLDEN = "b07eaf8f340bff715b2ca592fa697ae8c1e592864f02319292081953b334b228"


CASES = [
    {"name": "x", "observed_count": 1},
    {"name": "x_true_below_vwap_failure", "observed_count": 30, "avg_return_5m_pct": 0.2, "avg_return_15m_pct": 0.3},
    {"name": "x", "observed_count": 40, "avg_return_5m_pct": 0.2, "avg_return_15m_pct": 0.3, "avg_mae_5m_pct": -0.1},
    {"name": "x", "observed_count": 40, "avg_return_5m_pct": 0.2, "avg_return_15m_pct": 0.3, "avg_mae_5m_pct": -0.9},
    {"name": "x", "observed_count": 40, "avg_return_5m_pct": -0.2, "avg_return_15m_pct": -0.3},
    {"name": "x", "observed_count": 40, "avg_return_5m_pct": -0.2, "avg_return_15m_pct": 0.1, "avg_return_60m_pct": 1.0},
    {"name": "x", "observed_count": 40, "avg_return_5m_pct": 0.0, "avg_return_15m_pct": 0.0, "avg_return_60m_pct": 0.5},
    {"name": "unknown", "observed_count": "bad"},
    {"name": "x", "observed_count": "1,200", "avg_return_5m_pct": "1.5%", "avg_return_15m_pct": "2%"},
    {},
    {"name": None, "observed_count": 29.9},
]


def _scenarios(fn, root, mod):
    out = [_call(lambda c=c: fn(c)) for c in CASES]
    out.append(_call(lambda: fn(None)))
    out.append(_patched(mod, "_int", lambda v: 5, lambda: _call(lambda: fn({"name": "x", "observed_count": 99}))))
    out.append(_patched(mod, "_text", lambda v: "SEAM_true_below_vwap_failure", lambda: _call(lambda: fn({"name": "x", "observed_count": 40, "avg_return_5m_pct": 1, "avg_return_15m_pct": 1}))))
    out.append(_patched(mod, "_float", lambda v: 1.0, lambda: _call(lambda: fn({"name": "x", "observed_count": 40, "avg_mae_5m_pct": -9}))))
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", "retain_observation_sample_small"])
    tc.assertEqual(out[1], ["ok", "review_classifier_or_label"])
    tc.assertEqual(out[2], ["ok", "adjust_and_retest_candidate"])
    tc.assertEqual(out[3], ["ok", "retain_under_observation"])
    tc.assertEqual(out[4], ["ok", "keep_blocked"])
    tc.assertEqual(out[5], ["ok", "hold_observation_longer_horizon_only"])
    tc.assertEqual(out[6], ["ok", "hold_observation_longer_horizon_only"])
    tc.assertEqual(out[7], ["ok", "retain_observation_sample_small"])
    tc.assertEqual(out[12], ["ok", "retain_observation_sample_small"])
    tc.assertEqual(out[13], ["ok", "review_classifier_or_label"])
    tc.assertEqual(out[14], ["ok", "adjust_and_retest_candidate"])


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
