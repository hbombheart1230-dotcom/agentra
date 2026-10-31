"""P15 RF-035 (11h): q8_historical_review._read_json moved to q8_historical_read_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import q8_historical_read_projection as owner

FN = "_read_json"
FACADE = True
GOLDEN = "72f45ad818b9baa7f6bbf91b74a3787cb20705c83283a041602479af09940641"


def _scenarios(fn, root, mod):
    out = [_call(lambda: fn(root / "missing.json"))]
    out.append(_call(lambda: fn(_write(root, "ok.json", {"x": 1, "한": "글"}))))
    bom = root / "bom.json"
    bom.write_bytes(b"\xef\xbb\xbf" + json.dumps({"bom": True}).encode("utf-8"))
    out.append(_call(lambda: fn(bom)))
    out.append(_call(lambda: fn(_write(root, "list.json", [1]))))
    out.append(_call(lambda: fn(_write(root, "bad.json", "{oops"))))
    bad_bytes = root / "bytes.json"
    bad_bytes.write_bytes(b"\xff\xfe\x00bad")
    out.append(_call(lambda: fn(bad_bytes)))
    out.append(_call(lambda: fn(root)))
    out.append(_patched(mod.json, "loads", lambda s: {"patched": True}, lambda: _call(lambda: fn(root / "ok.json"))))
    out.append(_patched(mod.json, "loads", lambda s: (_ for _ in ()).throw(ValueError("x")), lambda: _call(lambda: fn(root / "ok.json"))))
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", {}])
    tc.assertEqual(out[1], ["ok", {"x": 1, "한": "글"}])
    tc.assertEqual(out[2], ["ok", {"bom": True}])
    tc.assertEqual(out[3:7], [["ok", {}]] * 4)
    tc.assertEqual(out[7], ["ok", {"patched": True}])
    tc.assertEqual(out[8], ["ok", {}])


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
