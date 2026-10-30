"""P15 RF-035 (07h): trade_bundle_assembly.apply_strategy_anchor_metadata moved to trade_bundle_strategy_anchor_projection; parity with the pre-move body (stdlib unittest)."""
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

from libs.reporting import trade_bundle_assembly as m
from libs.reporting import trade_bundle_strategy_anchor_projection as owner

FN = "apply_strategy_anchor_metadata"
FACADE = True
GOLDEN = "b3612b3a5e61a930fe68e7107a62bc88d13254d2d764ff129ea61da3aa5e59f8"


def _scenarios(fn, root, mod):
    kw = dict(strategist_input_path=root / "si.json", strategist_compact_input_path=root / "sci.json", strategist_llm_response_path=root / "sl.json")
    out = []
    lc, lb = {}, {}
    res = fn(lifecycle=lc, lifecycle_bundle=lb, strategy_anchor_run_id="r", **kw)
    out.append([res["lifecycle"] is lc, res["lifecycle_bundle"] is lb, res["strategy_anchor_run_id"], lc, lb])
    lc2, lb2 = {}, {"market_context_human": {"keep": 1}, "scanner_reason_human": "bad", "monitor_reason_human": None}
    out.append(_call(lambda: fn(lifecycle=lc2, lifecycle_bundle=lb2, strategy_anchor_run_id="", **kw)))
    out.append([lc2, lb2])
    calls = []
    real = mod.attach_strategy_anchor
    out.append(_patched(mod, "attach_strategy_anchor", lambda payload, **k: (calls.append((payload, k["strategy_anchor_run_id"])), {"SEAM": len(calls)})[1], lambda: _call(lambda: fn(lifecycle={}, lifecycle_bundle={}, strategy_anchor_run_id="z", **kw))))
    out.append(calls)
    out.append(_call(lambda: fn(lifecycle=None, lifecycle_bundle={}, strategy_anchor_run_id="r", **kw)))
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0][:3], [True, True, "r"])
    tc.assertEqual(out[0][3]["strategy_anchor"]["source"], "strategist_input_artifact")
    for key in ("market_context_human", "scanner_reason_human", "monitor_reason_human"):
        tc.assertEqual(out[0][4][key]["strategy_anchor"]["run_id"], "r")
    tc.assertEqual(out[2][0]["strategy_anchor"]["source"], "missing")
    tc.assertEqual(out[2][1]["market_context_human"]["keep"], 1)
    tc.assertEqual(out[4], [({}, "z")] * 3)
    tc.assertEqual(out[3][1]["lifecycle_bundle"]["scanner_reason_human"], {"SEAM": 2})
    tc.assertEqual(out[5][0], "exc")


def _run(fn, root, mod):
    return _norm(_scenarios(fn, root, mod), root)


class Test(unittest.TestCase):
    def test_wrapper_owner_and_pre_move_golden(self):
        with tempfile.TemporaryDirectory() as ta, tempfile.TemporaryDirectory() as tb:
            a = _run(getattr(m, FN), Path(ta), m)
            b = _run(lambda *x, **k: getattr(owner, FN)(*x, facade=m, **k) if FACADE else getattr(owner, FN)(*x, **k), Path(tb), m)
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
