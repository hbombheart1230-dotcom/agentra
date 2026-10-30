"""P15 RF-035 (08h): intraday_trade_reports._payload_fingerprint moved to intraday_report_scalar_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import intraday_report_scalar_projection as owner

FN = "_payload_fingerprint"
FACADE = True
GOLDEN = "595d48d2c92ede2f281e232e920486336195a4427b5a74d9e5eabf9163f820ee"


def _scenarios(fn, root, mod):
    out = [_call(lambda v=v: fn(v)) for v in [{"a": 1}, {"b": 2, "a": 1}, {"a": 1, "b": 2}, [1, 2], "x", None, {"한": "글"}, {1, 2}]]
    out.append(_patched(mod, "_stable_json_text", lambda payload: "FIXED", lambda: _call(lambda: fn({"a": 1}))))
    sha_calls = []
    real = mod.hashlib.sha256
    out.append(_patched(mod.hashlib, "sha256", lambda b: (sha_calls.append(b), real(b))[1], lambda: _call(lambda: fn({"a": 1}))))
    out.append(sha_calls)
    return out


def _expected(tc, out, root):
    import hashlib
    tc.assertEqual(out[0], ["ok", hashlib.sha256(b'{"a":1}').hexdigest()])
    tc.assertEqual(out[1], out[2])
    tc.assertEqual(out[7][0], "exc")
    tc.assertEqual(out[8], ["ok", hashlib.sha256(b"FIXED").hexdigest()])
    tc.assertEqual(out[10], [b'{"a":1}'])


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
