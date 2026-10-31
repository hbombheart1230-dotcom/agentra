"""P15 RF-035 (13h): q8_shadow_blocker_review._candidate_rows moved to q8_shadow_blocker_candidate_projection; parity with the pre-move body (stdlib unittest)."""
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

from libs.reporting import q8_shadow_blocker_review as m
from libs.reporting import q8_shadow_blocker_candidate_projection as owner

FN = "_candidate_rows"
FACADE = True
GOLDEN = "bbd72329261ccdf2851aa59e2e7327e3089f82ee400888bbd0bf8695a7ea3c73"


def _scenarios(fn, root, mod):
    payloads = [{"generated_at": "t", "candidates": [{"symbol": "A"}, "bad", {"symbol": "B", "_payload_generated_at": "keep"}]}, "skip", None, {"candidates": None}, {"generated_at": "t2", "candidates": [{"symbol": "C"}]}, {}]
    snap = copy.deepcopy(payloads)
    out = [_call(lambda: fn(payloads)), payloads == snap, _call(lambda: fn([])), _call(lambda: fn(iter(payloads[:1]))), _call(lambda: fn(None))]
    out.append(_call(lambda: fn([{"candidates": [{"symbol": "X"}]}])))

    class Never:
        pass

    out.append(_patched(mod, "Mapping", Never, lambda: _call(lambda: fn(payloads))))
    out.append(_patched(mod, "Mapping", dict, lambda: _call(lambda: fn(payloads))))
    return out


def _expected(tc, out, root):
    rows = out[0][1]
    tc.assertEqual([r["symbol"] for r in rows], ["A", "B", "C"])
    tc.assertEqual(rows[0]["_payload_generated_at"], "t")
    tc.assertEqual(rows[1]["_payload_generated_at"], "keep")
    tc.assertTrue(out[1])
    tc.assertEqual(out[2], ["ok", []])
    tc.assertEqual(out[4][0], "exc")
    tc.assertEqual(out[5][1][0]["_payload_generated_at"], None)
    tc.assertEqual(out[6], ["ok", []])
    tc.assertEqual([r["symbol"] for r in out[7][1]], ["A", "B", "C"])


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
