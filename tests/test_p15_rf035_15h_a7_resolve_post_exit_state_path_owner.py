"""P15 RF-035 (15h): post_exit_shadow_recap.resolve_post_exit_state_path moved to post_exit_shadow_state_path_projection; parity with the pre-move body (stdlib unittest)."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from libs.reporting import post_exit_shadow_recap as m
from libs.reporting import post_exit_shadow_state_path_projection as owner

FN = "resolve_post_exit_state_path"
FACADE = True
GOLDEN = "936799c955acd928eceb4bb0b699394d67afcb477d758b8f39b7154c09b10b9b"


def _norm(obj, root):
    return json.dumps(obj, ensure_ascii=False, default=repr).replace(str(root), "<T>")


def _h(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _call(fn):
    try:
        return ["ok", fn()]
    except BaseException as exc:  # noqa: BLE001 - parity of exception type/message is the point
        return ["exc", type(exc).__name__, str(exc)]


def _patched(mod, name, value, fn):
    with mock.patch.object(mod, name, value):
        return fn()


def _scenarios(fn, root, mod):
    root = Path(root)
    (root / "reports").mkdir(parents=True, exist_ok=True)
    (root / "data").mkdir(parents=True, exist_ok=True)
    (root / "data" / "state.json").write_text("{}", encoding="utf-8")
    (root / "explicit.json").write_text("{}", encoding="utf-8")
    (root / "env.json").write_text("{}", encoding="utf-8")
    cwd = os.getcwd()
    out = []
    env_clear = {"STATE_STORE_PATH": "", "MOCK_EXAM_STATE_PATH": ""}
    try:
        os.chdir(root)
        with mock.patch.dict(os.environ, env_clear):
            out.append(_call(lambda: fn(root / "reports")))
            out.append(_call(lambda: fn(root / "reports", root / "explicit.json")))
            out.append(_call(lambda: fn(root / "reports", Path("missing.json"))))
            out.append(_call(lambda: fn(str(root / "reports"), None)))
            out.append(_call(lambda: fn(root / "reports", Path(" "))))
        with mock.patch.dict(os.environ, {"STATE_STORE_PATH": str(root / "env.json"), "MOCK_EXAM_STATE_PATH": ""}):
            out.append(_call(lambda: fn(root / "reports")))
        with mock.patch.dict(os.environ, {"STATE_STORE_PATH": "", "MOCK_EXAM_STATE_PATH": "env.json"}):
            out.append(_call(lambda: fn(root / "reports")))
        (root / "data" / "state.json").unlink()
        with mock.patch.dict(os.environ, env_clear):
            out.append(_call(lambda: fn(root / "reports")))
            out.append(_call(lambda: fn(root / "nodir" / "reports")))
            out.append(_call(lambda: fn(None)))
    finally:
        os.chdir(cwd)
    out.append(_patched(mod, "Path", lambda *a: root / "explicit.json", lambda: _call(lambda: fn(root / "reports", root / "x"))))
    return out


def _expected(tc, out, root):
    r = Path(root)
    def p(name):
        return ["ok", (r / name).resolve()]
    tc.assertEqual(out[0], p("data/state.json"))
    tc.assertEqual(out[1], p("explicit.json"))
    tc.assertEqual(out[2], p("data/state.json"))
    tc.assertEqual(out[3], p("data/state.json"))
    tc.assertEqual(out[5], p("env.json"))
    tc.assertEqual(out[6], p("env.json"))
    tc.assertEqual(out[7], ["ok", None])
    tc.assertEqual(out[8], ["ok", None])
    tc.assertEqual(out[9][0], "exc")


def _run(fn, root, mod):
    return _norm(_scenarios(fn, root, mod), root)


def _owner_fn():
    f = getattr(owner, FN)
    return (lambda *x, **k: f(*x, facade=m, **k)) if FACADE else f


class Test(unittest.TestCase):
    def test_wrapper_owner_and_pre_move_golden(self):
        with tempfile.TemporaryDirectory() as ta, tempfile.TemporaryDirectory() as tb:
            a = _run(getattr(m, FN), Path(ta), m)
            b = _run(_owner_fn(), Path(tb), m)
        self.assertEqual(a, b)
        self.assertEqual(_h(a), GOLDEN)

    def test_wrapper_is_thin_and_owner_does_not_import_source(self):
        import ast
        import inspect
        fn = ast.parse(inspect.getsource(getattr(m, FN))).body[0]
        stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
        self.assertTrue(len(stmts) == 1 and isinstance(stmts[0], ast.Return))
        self.assertNotIn("import post_exit_shadow_recap", inspect.getsource(owner))

    def test_expected_values(self):
        with tempfile.TemporaryDirectory() as t:
            _expected(self, _scenarios(getattr(m, FN), Path(t), m), Path(t))


if __name__ == "__main__":
    unittest.main()
