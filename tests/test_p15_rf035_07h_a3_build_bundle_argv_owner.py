"""P15 RF-035 (07h): intraday_trade_reports._build_bundle_argv moved to intraday_report_command_projection; parity with the pre-move body (stdlib unittest)."""
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

from libs.reporting import intraday_trade_reports as m
from libs.reporting import intraday_report_command_projection as owner

FN = "_build_bundle_argv"
FACADE = True
GOLDEN = "d3e7a091bbce47b83987ef2b778c81a0d1bbee76da7be483f398103cfac0bbe5"
ENV_KEYS = ("ENV_PATH", "EVENT_LOG_PATH", "EVIDENCE_LOG_PATH", "INTENTS_PATH")


def _scenarios(fn, root, mod):
    base = {k: v for k, v in os.environ.items() if k not in ENV_KEYS}
    out = []
    with mock.patch.dict(os.environ, base, clear=True):
        with mock.patch.object(mod, "_bundle_role", lambda: "reporter"), mock.patch.object(mod, "_runtime_trade_day", lambda s: "fake"):
            out.append(_call(lambda: fn(root)))
            out.append(_call(lambda: fn(root, {"run_id": "r", "execution": {"order": {"symbol": " 005930 "}}})))
            out.append(_call(lambda: fn(root, {"execution": {"symbol": "000660"}, "symbol": "x"})))
            out.append(_call(lambda: fn(root, "bad")))
            out.append(_call(lambda: fn(root, {"run_id": "  "})))
            with mock.patch.dict(os.environ, {"ENV_PATH": str(root / "custom.env"), "INTENTS_PATH": str(root / "i.jsonl")}):
                out.append(_call(lambda: fn(root, {"run_id": "r"})))
            with mock.patch.object(mod, "_runtime_trade_day", lambda s: ""):
                out.append(_call(lambda: fn(root, {"run_id": "r"})))
            with mock.patch.object(mod, "_normalize_symbol", lambda v: "SEAM"):
                out.append(_call(lambda: fn(root, {"run_id": "r", "symbol": "q"})))
            with mock.patch.object(mod, "_bundle_role", lambda: "SEAMROLE"):
                out.append(_call(lambda: fn(root)))
    return out


def _expected(tc, out, root):
    argv = out[1][1]
    tc.assertIn("--target-run-id", argv)
    tc.assertEqual(argv[argv.index("--target-run-id") + 1], "r")
    tc.assertEqual(argv[argv.index("--target-symbol") + 1], "005930")
    tc.assertEqual(argv[argv.index("--day") + 1], "fake")
    tc.assertEqual(argv[argv.index("--role") + 1], "reporter")
    tc.assertNotIn("--target-run-id", out[0][1])
    tc.assertEqual(out[2][1][out[2][1].index("--target-symbol") + 1], "000660")
    tc.assertNotIn("--day", out[6][1])
    tc.assertEqual(out[7][1][out[7][1].index("--target-symbol") + 1], "SEAM")
    tc.assertEqual(out[8][1][out[8][1].index("--role") + 1], "SEAMROLE")


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
