"""P15 RF-035 (09h): q8_historical_review._md_table moved to q8_historical_markdown_table_projection; parity with the pre-move body (stdlib unittest)."""
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
from libs.reporting import q8_historical_markdown_table_projection as owner

FN = "_md_table"
FACADE = False
GOLDEN = "4f8e0af5cb175ab6d60b21c72f35ab8ba583f957349d46e079c4e95cb84ab79a"


def _scenarios(fn, root, mod):
    out = [_call(lambda: fn(["a", "b"], [["x", 2]]))]
    out.append(_call(lambda: fn(["a"], [])))
    out.append(_call(lambda: fn([], [])))
    out.append(_call(lambda: fn(["a", "b"], [["x"], ["y", "z", "extra"], [None, 1.5], ("t", True)])))
    out.append(_call(lambda: fn(["한", "글"], [["값", "|"]])))
    out.append(_call(lambda: fn([1, 2], [])))
    out.append(_call(lambda: fn(None, [])))
    out.append(_call(lambda: fn(["a"], [5])))
    out.append(_call(lambda: fn(("a", "b"), iter([["i", "j"]]))))
    return out


def _expected(tc, out, root):
    tc.assertEqual(out[0], ["ok", ["| a | b |", "| --- | --- |", "| x | 2 |"]])
    tc.assertEqual(out[1], ["ok", ["| a |", "| --- |"]])
    tc.assertEqual(out[2], ["ok", ["|  |", "|  |"]])
    tc.assertEqual(out[3][1][2:], ["| x |", "| y | z | extra |", "| None | 1.5 |", "| t | True |"])
    tc.assertEqual(out[5][0], "exc")
    tc.assertEqual(out[6][0], "exc")
    tc.assertEqual(out[7][0], "exc")
    tc.assertEqual(out[8][1][2:], ["| i | j |"])


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
        self.assertTrue(len(stmts) == 1 and isinstance(stmts[0], ast.Return))
        self.assertNotIn("import " + m.__name__.split(".")[-1], inspect.getsource(owner))

    def test_expected_values(self):
        with tempfile.TemporaryDirectory() as t:
            _expected(self, _scenarios(getattr(m, FN), Path(t), m), Path(t))


if __name__ == "__main__":
    unittest.main()
