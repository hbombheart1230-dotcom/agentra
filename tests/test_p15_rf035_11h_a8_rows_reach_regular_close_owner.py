"""P15 RF-035 (11h): post_exit_shadow_recap._rows_reach_regular_close moved to post_exit_shadow_freshness_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import post_exit_shadow_freshness_projection as owner

FN = "_rows_reach_regular_close"
FACADE = True
GOLDEN = "7a82cdc1268c4cae6a6ae81e9f90d49adb7fa0aebb60f7e6351a6e9ca9781034"


def _scenarios(fn, root, mod):
    out = []
    for hh in ("152959", "153000", "160000", "", "090000", "235959"):
        out.append(_patched(mod, "_row_kst_hhmmss", lambda r, v=hh: v, lambda: _call(lambda: fn([{"x": 1}]))))
    out.append(_patched(mod, "_row_kst_hhmmss", lambda r: "160000", lambda: _call(lambda: fn(["bad", 5, None]))))
    out.append(_patched(mod, "_row_kst_hhmmss", lambda r: "160000", lambda: _call(lambda: fn([]))))
    out.append(_patched(mod, "_row_kst_hhmmss", lambda r: r["h"], lambda: _call(lambda: fn([{"h": "100000"}, {"h": ""}, {"h": "153500"}]))))
    out.append(_patched(mod, "_row_kst_hhmmss", lambda r: r["h"], lambda: _call(lambda: fn(iter([{"h": "100000"}])))))
    out.append(_patched(mod, "_row_kst_hhmmss", lambda r: (_ for _ in ()).throw(KeyError("k")), lambda: _call(lambda: fn([{"h": 1}]))))
    out.append(_call(lambda: fn(None)))
    return out


def _expected(tc, out, root):
    tc.assertEqual([o[1] for o in out[:6]], [False, True, True, False, False, True])
    tc.assertEqual(out[6], ["ok", False])
    tc.assertEqual(out[7], ["ok", False])
    tc.assertEqual(out[8], ["ok", True])
    tc.assertEqual(out[9], ["ok", False])
    tc.assertEqual(out[10][:2], ["exc", "KeyError"])
    tc.assertEqual(out[11][0], "exc")


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
