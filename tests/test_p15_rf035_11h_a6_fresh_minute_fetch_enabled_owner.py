"""P15 RF-035 (11h): post_exit_shadow_recap._fresh_minute_fetch_enabled moved to post_exit_shadow_env_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import post_exit_shadow_env_projection as owner

FN = "_fresh_minute_fetch_enabled"
FACADE = True
GOLDEN = "3289143bd13e62749b7c5938ddd1e9e4ce8187ce2262eaf5a16c913976fb49db"


KEY = "POST_EXIT_SHADOW_RECAP_FETCH_FRESH_MINUTES"


def _scenarios(fn, root, mod):
    out = []
    for val in ("1", "0", "false", "FALSE", " No ", "off", "on", "true", "", "garbage", " 0 "):
        out.append(_patched(mod.os, "getenv", lambda k, d=None, v=val: v, lambda: _call(fn)))
    out.append(_patched(mod.os, "getenv", lambda k, d=None: d, lambda: _call(fn)))
    seen = []
    out.append(_patched(mod.os, "getenv", lambda k, d=None: (seen.append((k, d)), "1")[1], lambda: _call(fn)))
    out.append(seen)
    base = {k: v for k, v in os.environ.items() if k != KEY}
    with mock.patch.dict(os.environ, base, clear=True):
        out.append(_call(fn))
    return out


def _expected(tc, out, root):
    tc.assertEqual([o[1] for o in out[:11]], [True, False, False, False, False, False, True, True, True, True, False])
    tc.assertEqual(out[11], ["ok", True])
    tc.assertEqual(out[13], [("POST_EXIT_SHADOW_RECAP_FETCH_FRESH_MINUTES", "1")])
    tc.assertEqual(out[14], ["ok", True])


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
