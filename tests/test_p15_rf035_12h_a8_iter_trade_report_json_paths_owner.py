"""P15 RF-035 (12h): post_exit_shadow_recap.iter_trade_report_json_paths moved to post_exit_shadow_path_projection; parity with the pre-move body (stdlib unittest)."""
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

from libs.reporting import post_exit_shadow_recap as m
from libs.reporting import post_exit_shadow_path_projection as owner

FN = "iter_trade_report_json_paths"
FACADE = False
GOLDEN = "d9869f4f8653100d1ec45a6688a88429ec92bdc1eb39f23a1e4f4925acb18586"


def _scenarios(fn, root, mod):
    for name in ("x", "y"):
        _write(root, f"trades/2026-10-31/{name}/reports/ai_trade_report.json", {"n": name})
    _write(root, "trades/2026-10-31/z/reports/other.json", {})
    _write(root, "trades/2026-10-31/deep/er/reports/ai_trade_report.json", {})
    before = sorted(str(p) for p in root.rglob("*"))
    out = [_call(lambda: fn(root, "2026-10-31")), _call(lambda: fn(root, "2026-10-30")), _call(lambda: fn(root / "none", "2026-10-31")), _call(lambda: fn(root, "")), _call(lambda: fn(str(root), "2026-10-31"))]
    out.append(sorted(str(p) for p in root.rglob("*")) == before)
    return out


def _expected(tc, out, root):
    day = root / "trades" / "2026-10-31"
    tc.assertEqual(out[0], ["ok", sorted([day / "deep" / "er" / "reports" / "ai_trade_report.json", day / "x" / "reports" / "ai_trade_report.json", day / "y" / "reports" / "ai_trade_report.json"])])
    tc.assertEqual(out[1], ["ok", []])
    tc.assertEqual(out[2], ["ok", []])
    tc.assertEqual(out[4][0], "exc")
    tc.assertTrue(out[5])


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
