"""P15 RF-035 (12h): post_exit_shadow_recap._utc_now_iso moved to post_exit_shadow_clock_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import post_exit_shadow_clock_projection as owner

FN = "_utc_now_iso"
FACADE = True
GOLDEN = "c5411d4aee42ab19e92a675fd907b456945f88d1223f28504cc50f3c76bd2cd7"


from datetime import datetime as real_datetime, timezone


class _FakeDT(real_datetime):
    @classmethod
    def now(cls, tz=None):
        return real_datetime(2026, 10, 31, 0, 0, 0, 123456, tzinfo=tz)


def _scenarios(fn, root, mod):
    out = [_patched(mod, "datetime", _FakeDT, lambda: _call(fn))]
    seen = []

    class FakeDT(real_datetime):
        @classmethod
        def now(cls, tz=None):
            seen.append(tz)
            return real_datetime(2026, 1, 2, 3, 4, 5, tzinfo=tz)

    class FakeTZ:
        utc = timezone.utc

    out.append(_patched(mod, "datetime", FakeDT, lambda: _patched(mod, "timezone", FakeTZ, lambda: _call(fn))))
    out.append(seen)
    real = _call(fn)
    out.append(real[0] == "ok" and real[1].endswith("+00:00"))
    return out


def _expected(tc, out, root):
    tc.assertIn(out[0][0], ("ok",))
    tc.assertTrue(out[0][1].startswith("2026-10-31T00:00:00"))
    tc.assertEqual(out[1][1], "2026-01-02T03:04:05+00:00")
    tc.assertEqual(out[2], [timezone.utc])
    tc.assertTrue(out[3])


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
