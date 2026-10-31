"""P15 RF-035 (20261101-02h): six live_execution_bundle_runner and two quant_tactic_report helpers moved to projection Owners; parity with the pre-move bodies (stdlib unittest)."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from libs.reporting import live_bundle_json_read_projection as json_read_owner
from libs.reporting import live_bundle_jsonl_iter_projection as jsonl_owner
from libs.reporting import live_bundle_lock_path_projection as lock_path_owner
from libs.reporting import live_bundle_queue_path_projection as queue_path_owner
from libs.reporting import live_bundle_stale_timeout_projection as stale_owner
from libs.reporting import live_bundle_trade_id_projection as trade_id_owner
from libs.reporting import live_execution_bundle_runner as lb
from libs.reporting import quant_tactic_fmt_projection as fmt_owner
from libs.reporting import quant_tactic_items_projection as items_owner
from libs.reporting import quant_tactic_report as qt

GOLDENS = {
    "a1": "6f2075e27e6c3b092b06c1d72e0534915d96d60bbb6f1e99282cc35d78dd761e",
    "a2": "68bd40f6c145354262dbf0ad8898eb3383778cdfcdc9965d4f7cd4347589dddf",
    "a3": "6d060f6f8769f72a29b0a0f3c9c355151e057b4e24846d2463137276ae71de90",
    "a4": "7efccd9115f9d3765a6521b3ea9dfb68681169ad87dbf7dc5bc7f124ed46e906",
    "a5": "69731bb587a13747da40ad88eeea6edd06523eed0a78866bc1159a850130368f",
    "a6": "9a0281a2cd7ae0763d7d2737d96b6a11b02781683549f618458c49df7fda8b86",
    "a7": "60db550816ed796cba77c8dfb86930c133b14280b32279d7d9de487d9fb0e4ba",
    "a8": "6afcc1d391e5a5ab9e32985c5247adacc1a4851f0e6437b24bee001951f89b94",
}


def _call(fn):
    try:
        return ["ok", fn()]
    except BaseException as exc:  # noqa: BLE001 - parity of exception type/message is the point
        return ["exc", type(exc).__name__, str(exc)]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, default=repr).encode()).hexdigest()


class _Odd:
    def __bool__(self):
        raise RuntimeError("odd-bool")

    def __str__(self):
        return " Odd "


class _FakeOS:
    def __init__(self, value):
        self.value = value
        self.calls = []

    def getenv(self, name, default=None):
        self.calls.append([name, default])
        return self.value


def _a1(fn, mod, root):
    out = []
    for value in ("12", "45", "bad", "", None, "30", "29.9", "1e3", "-5", "nan", "inf", " 60 ", "0"):
        fake = _FakeOS(value)
        with mock.patch.object(lb, "os", fake):
            out.append([_call(lambda: fn()), fake.calls])
    broken = mock.Mock(getenv=mock.Mock(side_effect=RuntimeError("env boom")))
    with mock.patch.object(lb, "os", broken):
        out.append(_call(lambda: fn()))
    return out


def _a2(fn, mod, root):
    root_fake = Path("/tmp/fake")
    out = []
    for value in ("", None, "/tmp/custom.lock", " /tmp/x.lock ", "   ", "rel/lock", 0):
        fake = _FakeOS(value)
        with mock.patch.object(lb, "os", fake), mock.patch.object(lb, "ROOT", root_fake):
            out.append([_call(lambda: fn()), fake.calls])
    with mock.patch.object(lb, "os", _FakeOS("")), mock.patch.object(lb, "ROOT", "/str/root"):
        out.append(_call(lambda: fn()))
    with mock.patch.object(lb, "os", _FakeOS("/a")), mock.patch.object(lb, "Path", lambda raw: ("PATCHED", raw)):
        out.append(_call(lambda: fn()))
    return out


def _a3(fn, mod, root):
    out = []
    for base in (Path("/tmp/fake"), Path("rel"), Path("/"), "/str/root"):
        with mock.patch.object(lb, "ROOT", base):
            out.append(_call(lambda: fn()))
    return out


def _a4(fn, mod, root):
    root = Path(root)
    (root / "ok.json").write_text('{"a": 1}', encoding="utf-8")
    (root / "list.json").write_text("[1]", encoding="utf-8")
    (root / "bad.json").write_text("{nope", encoding="utf-8")
    (root / "bin.json").write_bytes(b"\xff\xfe\x00")
    (root / "dir.json").mkdir()
    out = [_call(lambda n=n: fn(root / n)) for n in ("ok.json", "missing.json", "list.json", "bad.json", "bin.json", "dir.json")]
    out += [_call(lambda: fn(None)), _call(lambda: fn())]

    class _P:
        def exists(self):
            return True

        def read_text(self, encoding=None):
            return '{"fake": true}'

    out.append(_call(lambda: fn(_P())))
    with mock.patch.object(lb, "json", mock.Mock(loads=lambda text: {"patched": text})):
        out.append(_call(lambda: fn(root / "ok.json")))
    with mock.patch.object(lb, "json", mock.Mock(loads=lambda text: [text])):
        out.append(_call(lambda: fn(root / "ok.json")))
    return out


def _a5(fn, mod, root):
    root = Path(root)
    (root / "ok.jsonl").write_text('{"a":1}\nBAD\n[]\n\n  \n{"b": 2}\n"str"\n', encoding="utf-8")
    (root / "empty.jsonl").write_text("", encoding="utf-8")
    (root / "bin.jsonl").write_bytes(b"\xff\xfe\n")
    (root / "dir.jsonl").mkdir()
    out = [_call(lambda n=n: fn(root / n)) for n in ("ok.jsonl", "missing.jsonl", "empty.jsonl", "bin.jsonl", "dir.jsonl")]
    out += [_call(lambda: fn(None)), _call(lambda: fn())]
    res = fn(root / "ok.jsonl")
    out.append(["is-list", [isinstance(res, list), len(res)]])
    with mock.patch.object(lb, "json", mock.Mock(loads=lambda text: {"p": text})):
        out.append(_call(lambda: fn(root / "ok.jsonl")))
    return out


def _a6(fn, mod, root):
    out = [
        _call(lambda: fn("2026-11-01", "005930", 2)),
        _call(lambda: fn("", "", 0)),
        _call(lambda: fn(None, None, 7)),
        _call(lambda: fn("2026-11-01", "abc", "5")),
        _call(lambda: fn("2026-11-01", "005930", 123)),
        _call(lambda: fn("2026-11-01", "005930", "x")),
        _call(lambda: fn("2026-11-01", "005930", None)),
        _call(lambda: fn("2026-11-01", "005930", -3)),
        _call(lambda: fn("2026-11-01", "005930", 2.9)),
        _call(lambda: fn("2026-11-01", 5, 1)),
        _call(lambda: fn("2026-11-01")),
        _call(lambda: fn()),
    ]
    with mock.patch.object(lb, "normalize_symbol", lambda s, allow_test_symbols=False: "005930"):
        out.append(_call(lambda: fn("2026-11-01", "005930", 2)))
    with mock.patch.object(lb, "normalize_symbol", lambda s, allow_test_symbols=False: ""):
        out.append(_call(lambda: fn("20261101", "zzz", 1)))
    with mock.patch.object(lb, "normalize_symbol", lambda s, allow_test_symbols=False: (_ for _ in ()).throw(ValueError("boom"))):
        out.append(_call(lambda: fn("20261101", "zzz", 1)))
    return out


def _a7(fn, mod, root):
    values = [[" A ", None, "B", ""], {"x": 1}, (" t ", 3, 0, "   "), [], (), None, "text", 5, {"a"}, [1.5, False, True], [_Odd()], iter([1])]
    out = [_call(lambda v=v: fn(v)) for v in values]
    out.append(_call(lambda: fn()))
    res = fn([" a "])
    out.append(["new-list", [res == ["a"], isinstance(res, list)]])
    return out


def _a8(fn, mod, root):
    values = [None, "", 1.25, 1.2500, "abc", 0.0, 0, 1.0, 100.0, 0.00001, 0.12345678, -0.5, float("inf"), float("nan"), True, False, 5, [], [1], {}, "", " "]
    out = [_call(lambda v=v: fn(v)) for v in values]
    out.append(_call(lambda: fn()))
    out.append(_call(lambda: fn(_Odd())))
    return out


CASES = {
    "a1": (_a1, lb, "_stale_process_after_sec", lambda: stale_owner._stale_process_after_sec, True, stale_owner),
    "a2": (_a2, lb, "_background_job_lock_path", lambda: lock_path_owner._background_job_lock_path, True, lock_path_owner),
    "a3": (_a3, lb, "_background_job_queue_path", lambda: queue_path_owner._background_job_queue_path, True, queue_path_owner),
    "a4": (_a4, lb, "_read_json", lambda: json_read_owner._read_json, True, json_read_owner),
    "a5": (_a5, lb, "_iter_jsonl", lambda: jsonl_owner._iter_jsonl, True, jsonl_owner),
    "a6": (_a6, lb, "_build_trade_id", lambda: trade_id_owner._build_trade_id, True, trade_id_owner),
    "a7": (_a7, qt, "_items", lambda: items_owner._items, False, items_owner),
    "a8": (_a8, qt, "_fmt", lambda: fmt_owner._fmt, False, fmt_owner),
}


def _run(key, which):
    scenario, mod, name, owner_factory, facade, _ = CASES[key]
    if which == "wrapper":
        fn = getattr(mod, name)
    else:
        raw = owner_factory()
        fn = (lambda *a, **k: raw(*a, facade=mod, **k)) if facade else raw
    with tempfile.TemporaryDirectory() as t:
        out = scenario(fn, mod, t)
        return json.loads(json.dumps(out, default=repr).replace(t, "<T>").replace(str(Path(t).resolve()), "<T>"))


class Test(unittest.TestCase):
    def _parity(self, key):
        a = _run(key, "wrapper")
        b = _run(key, "owner")
        self.assertEqual(a, b)
        self.assertEqual(_h(a), GOLDENS[key])
        _, mod, name, _, _, owner_mod = CASES[key]
        fn = ast.parse(inspect.getsource(getattr(mod, name))).body[0]
        stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
        self.assertTrue(len(stmts) == 1 and isinstance(stmts[0], ast.Return))
        self.assertNotIn("import " + mod.__name__.split(".")[-1], inspect.getsource(owner_mod))
        return a

    def test_a1_stale_process_after_sec(self):
        out = self._parity("a1")
        self.assertEqual([o[0][1] for o in out[:3]], [30.0, 45.0, 180.0])
        self.assertEqual(out[0][1], [["INTRADAY_TRADE_REPORT_STALE_PROCESS_SEC", "180"]])

    def test_a2_background_job_lock_path(self):
        out = self._parity("a2")
        with mock.patch.object(lb, "os", _FakeOS("")), mock.patch.object(lb, "ROOT", Path("/tmp/fake")):
            self.assertEqual(lb._background_job_lock_path(), Path("/tmp/fake/reports/runtime/intraday_trade_report_bundle.lock"))
        with mock.patch.object(lb, "os", _FakeOS("/tmp/custom.lock")):
            self.assertEqual(lb._background_job_lock_path(), Path("/tmp/custom.lock"))

    def test_a3_background_job_queue_path(self):
        out = self._parity("a3")
        with mock.patch.object(lb, "ROOT", Path("/tmp/fake")):
            self.assertEqual(lb._background_job_queue_path(), Path("/tmp/fake/reports/runtime/intraday_trade_report_bundle.queue.json"))

    def test_a4_read_json(self):
        out = self._parity("a4")
        self.assertEqual(out[0], ["ok", {"a": 1}])
        self.assertEqual(out[1], ["ok", {}])
        self.assertEqual(out[3], ["ok", {}])
        self.assertEqual(out[-2], ["ok", {"patched": '{"a": 1}'}])
        self.assertEqual(out[-1], ["ok", {}])

    def test_a5_iter_jsonl(self):
        out = self._parity("a5")
        self.assertEqual(out[0], ["ok", [{"a": 1}, {"b": 2}]])
        self.assertEqual(out[1], ["ok", []])
        self.assertEqual(out[-2], ["is-list", [True, 2]])

    def test_a6_build_trade_id(self):
        out = self._parity("a6")
        with mock.patch.object(lb, "normalize_symbol", lambda s, allow_test_symbols=False: "005930"):
            self.assertEqual(lb._build_trade_id("2026-11-01", "005930", 2), "TRD_20261101_005930_02")
        self.assertEqual(out[-3], ["ok", "TRD_20261101_005930_02"])
        self.assertEqual(out[-2], ["ok", "TRD_20261101_UNKNOWN_01"])

    def test_a7_items(self):
        out = self._parity("a7")
        self.assertEqual(qt._items([" A ", None, "B", ""]), ["A", "B"])
        self.assertEqual(qt._items({"x": 1}), [])
        self.assertEqual(out[-1], ["new-list", [True, True]])

    def test_a8_fmt(self):
        out = self._parity("a8")
        self.assertEqual(qt._fmt(None), "-")
        self.assertEqual(qt._fmt(1.2500), "1.25")
        self.assertEqual(qt._fmt("abc"), "abc")
        self.assertEqual(out[-2][0], "exc")


if __name__ == "__main__":
    unittest.main()
