"""P15 RF-035 (12h): post_exit_shadow_recap._post_exit_shadow_needs_fresh_minutes moved to post_exit_shadow_freshness_decision_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import post_exit_shadow_freshness_decision_projection as owner

FN = "_post_exit_shadow_needs_fresh_minutes"
FACADE = True
GOLDEN = "7429d0160a0091e8c49a6d710d6d0ac8d7fbd6f2d3ccd18fe0882b0ff03275e4"


from datetime import datetime as real_datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))


def _clock(hour, minute=0):
    fixed = real_datetime(2026, 10, 31, hour, minute, tzinfo=KST).astimezone(timezone.utc)

    class FakeDT(real_datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed.astimezone(tz) if tz else fixed.replace(tzinfo=None)

    return FakeDT


def _with(mod, hour, minute, required, reach_epoch, reach_close, fn, shadow, rows=()):
    with mock.patch.object(mod, "datetime", _clock(hour, minute)), mock.patch.object(mod, "_shadow_latest_required_epoch", lambda s: required), \
            mock.patch.object(mod, "_rows_reach_epoch", lambda r, e: reach_epoch), mock.patch.object(mod, "_rows_reach_regular_close", lambda r: reach_close):
        return _call(lambda: fn(shadow, list(rows)))


def _scenarios(fn, root, mod):
    eod = lambda status: {"checkpoints": {"EOD": {"status": status}}}
    t = real_datetime(2026, 10, 31, 16, 0, tzinfo=KST).timestamp()
    out = [
        _with(mod, 16, 0, None, False, False, fn, eod("observed")),
        _with(mod, 16, 0, None, False, False, fn, eod("pending")),
        _with(mod, 16, 0, None, False, True, fn, eod("pending")),
        _with(mod, 15, 0, None, False, False, fn, eod("pending")),
        _with(mod, 16, 0, t + 3600, False, False, fn, eod("pending")),
        _with(mod, 16, 0, t - 3600, False, False, fn, eod("observed")),
        _with(mod, 16, 0, t - 3600, True, False, fn, eod("pending")),
        _with(mod, 16, 0, None, False, False, fn, {}),
        _with(mod, 16, 0, None, False, False, fn, None),
    ]
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", False])
    tc.assertEqual(out[1], ["ok", True])
    tc.assertEqual(out[2], ["ok", False])
    tc.assertEqual(out[3], ["ok", False])
    tc.assertEqual(out[4], ["ok", False])
    tc.assertEqual(out[5], ["ok", True])
    tc.assertEqual(out[6], ["ok", True])
    tc.assertEqual(out[8][0], "exc")


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
