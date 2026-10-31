"""P15 RF-035 (09h): q8_historical_review._iter_days moved to q8_historical_day_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import q8_historical_day_projection as owner

FN = "_iter_days"
FACADE = False
GOLDEN = "cd2a9c6472b8e34cbe475045f247b626e45920d2f8134ad656827855bf515712"


def _scenarios(fn, root, mod):
    out = [_call(lambda: list(fn("2026-10-29", "2026-10-31")))]
    out.append(_call(lambda: list(fn("2026-10-31", "2026-10-29"))))
    out.append(_call(lambda: list(fn("2026-10-30T12:00:00", "2026-10-30 23:59"))))
    out.append(_call(lambda: list(fn("2024-02-28", "2024-03-01"))))
    gen = fn("not-a-date", "2026-10-31")
    out.append(["generator-created", type(gen).__name__])
    out.append(_call(lambda: list(gen)))
    out.append(_call(lambda: list(fn("2026-10-30", "bad"))))
    out.append(_call(lambda: list(fn(None, "2026-10-31"))))
    it = fn("2026-10-30", "2026-11-01")
    out.append([next(it), next(it), next(it), _call(lambda: next(it))[0]])
    out.append(_call(lambda: list(fn(20261030, 20261031))))
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", ["2026-10-29", "2026-10-30", "2026-10-31"]])
    tc.assertEqual(out[1], ["ok", []])
    tc.assertEqual(out[2], ["ok", ["2026-10-30"]])
    tc.assertEqual(out[3], ["ok", ["2024-02-28", "2024-02-29", "2024-03-01"]])
    tc.assertEqual(out[4], ["generator-created", "generator"])
    tc.assertEqual(out[5][:2], ["exc", "ValueError"])
    tc.assertEqual(out[8], ["2026-10-30", "2026-10-31", "2026-11-01", "exc"])


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
        self.assertTrue(len(stmts) == 1 and isinstance(stmts[0], ast.Expr) and isinstance(stmts[0].value, ast.YieldFrom))
        self.assertNotIn("import " + m.__name__.split(".")[-1], inspect.getsource(owner))

    def test_expected_values(self):
        with tempfile.TemporaryDirectory() as t:
            _expected(self, _scenarios(getattr(m, FN), Path(t), m), Path(t))


if __name__ == "__main__":
    unittest.main()
