"""P15 RF-035 (07h): trade_bundle_assembly.attach_strategy_anchor moved to trade_bundle_strategy_anchor_projection; parity with the pre-move body (stdlib unittest)."""
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

FN = "attach_strategy_anchor"
FACADE = False


GOLDEN = "ce455b9da69de39522bb2d41149548d5e572c2690a3a1339b133096c5c8289f2"


def _scenarios(fn, root, mod):
    kw = dict(strategist_input_path=root / "si.json", strategist_compact_input_path=root / "sci.json", strategist_llm_response_path=root / "sl.json")
    src = {"x": 1, "nested": {"k": 1}}
    snap = copy.deepcopy(src)
    out = [_call(lambda: fn(src, strategy_anchor_run_id="r", **kw)), src == snap]
    out.append(_call(lambda: fn(None, strategy_anchor_run_id=None, **kw)))
    out.append(_call(lambda: fn({}, strategy_anchor_run_id=0, **kw)))
    out.append(_call(lambda: fn(None, strategy_anchor_run_id="r", **{k: "str" for k in kw})))
    out.append(_call(lambda: fn([("a", 1)], strategy_anchor_run_id="r", **kw)))
    out.append(_call(lambda: fn("bad", strategy_anchor_run_id="r", **kw)))
    return out


def _expected(tc, out, root):
    r = out[0][1]
    tc.assertEqual(r["x"], 1)
    tc.assertEqual(r["strategy_anchor"]["run_id"], "r")
    tc.assertEqual(r["strategy_anchor"]["artifacts"]["strategist_input_json"], str(root / "si.json"))
    tc.assertTrue(out[1])
    tc.assertEqual(out[2][1]["strategy_anchor_run_id"], "")
    tc.assertEqual(out[5], ["ok", {"a": 1, "entry_strategist_run_id": "r", "strategy_anchor_run_id": "r", "strategy_anchor": r["strategy_anchor"] | {"artifacts": out[5][1]["strategy_anchor"]["artifacts"]}}])
    tc.assertEqual(out[6][0], "exc")


def _run(fn, root, mod):
    return _norm(_scenarios(fn, root, mod), root)


class Test(unittest.TestCase):
    def test_wrapper_owner_and_pre_move_golden(self):
        with tempfile.TemporaryDirectory() as ta, tempfile.TemporaryDirectory() as tb:
            a = _run(getattr(m, FN), Path(ta), m)
            b = _run(lambda *x, **k: getattr(owner, FN)(*x, **k), Path(tb), m)
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
