"""P15 RF-035 (07h): intraday_trade_reports._load_bundle_queue moved to intraday_report_queue_read_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import intraday_report_queue_read_projection as owner

FN = "_load_bundle_queue"
FACADE = True
GOLDEN = "07b4f4b7021c24f0bb95798ad2a7373cc9cb02c9e1d5d77459170dcc6064281e"


def _scenarios(fn, root, mod):
    out = [_call(lambda: fn(root / "missing.json"))]
    src = [{"id": 1}, 3, {"id": 2}, None, "x"]
    p = _write(root, "q.json", src)
    out.append(_call(lambda: fn(p)))
    out.append(_call(lambda: _copy_check(fn, p)))
    out.append(_call(lambda: fn(_write(root, "dict.json", {"a": 1}))))
    out.append(_call(lambda: fn(_write(root, "bad.json", "[oops"))))
    out.append(_call(lambda: fn(_write(root, "empty.json", []))))
    out.append(_patched(mod.json, "loads", lambda s: [{"patched": 1}], lambda: _call(lambda: fn(p))))
    out.append(_patched(mod.json, "loads", lambda s: (_ for _ in ()).throw(ValueError("x")), lambda: _call(lambda: fn(p))))
    return out


def _copy_check(fn, p):
    a = fn(p)
    b = fn(p)
    a[0]["id"] = 99
    return [a[0] is not b[0], b[0]["id"]]


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", []])
    tc.assertEqual(out[1], ["ok", [{"id": 1}, {"id": 2}]])
    tc.assertEqual(out[2], ["ok", [True, 1]])
    tc.assertEqual(out[3:6], [["ok", []]] * 3)
    tc.assertEqual(out[6], ["ok", [{"patched": 1}]])
    tc.assertEqual(out[7], ["ok", []])


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
