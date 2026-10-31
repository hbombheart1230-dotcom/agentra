"""P15 RF-035 (20261101-01h): eight pure live_execution_bundle_runner helpers moved to projection Owners; parity with the pre-move bodies (stdlib unittest)."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import time as _time
import unittest
from pathlib import Path
from unittest import mock

from libs.reporting import live_bundle_artifact_paths_projection as artifact_owner
from libs.reporting import live_bundle_bundle_role_projection as role_owner
from libs.reporting import live_bundle_duration_human_projection as duration_owner
from libs.reporting import live_bundle_env_bool_projection as env_owner
from libs.reporting import live_bundle_lock_epoch_projection as lock_owner
from libs.reporting import live_bundle_trade_sequence_projection as sequence_owner
from libs.reporting import live_bundle_trueish_projection as trueish_owner
from libs.reporting import live_bundle_wmi_epoch_projection as wmi_owner
from libs.reporting import live_execution_bundle_runner as lb

GOLDENS = {
    "a1": "fc807c59a0dfbb6b358b066f220cf890b1caaa0ff17ed078d62be389e23680cc",
    "a2": "a17d55714ef3bc14dea76f4c3dbc5a76cac4e9f2e7bf66b5cbfd76c8729d134d",
    "a3": "4d77874bc3081a17c27ce3ee306f6cca87abe44d954d5a76d263c03686abe48c",
    "a4": "e205d0cabab89384b1379d7c7b371cede8446d58ac2009266ec10c94521c17d8",
    "a5": "5a2b29ec4a39f9edbe1866647a4a43cd0b1b955dd06703c505b1b72d45beb7ff",
    "a6": "8817d2b602809c4e0db4294fe3101f08eeff6862da542947a3128ac2ad399471",
    "a7": "37d868534eb7060477970d4b81b7d525c7122a584147de1f6ff6b493546305c2",
    "a8": "118ddbb0e26361e19f835f7f38ff271e81e307db1722b04112504bc285893792",
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
        return " YES "


_TOKENS = ["YES", "y", "on", "false", None, "", " 1 ", "True", "TRUE", "no", "off", "0", 0, 1, 2.5, False, True, [], "On ", "yes!", _Odd()]


class _FakeOS:
    def __init__(self, value):
        self.value = value
        self.calls = []

    def getenv(self, name, default=None):
        self.calls.append([name, default])
        return self.value


def _a1(fn, mod):
    out = []
    for value in ("YES", "off", "1", "true", " On ", "", None, "maybe", 0):
        fake = _FakeOS(value)
        with mock.patch.object(lb, "os", fake):
            out.append([_call(lambda: fn("FLAG")), fake.calls])
            out.append([_call(lambda: fn("FLAG", False)), fake.calls[-1:]])
            out.append([_call(lambda: fn("FLAG", default=True)), fake.calls[-1:]])
    with mock.patch.dict(lb.os.environ, {"LB_TEST_FLAG": "on"}):
        out.append(_call(lambda: fn("LB_TEST_FLAG")))
    with mock.patch.dict(lb.os.environ, {}, clear=False):
        lb.os.environ.pop("LB_TEST_MISSING", None)
        out.append(_call(lambda: fn("LB_TEST_MISSING", default=False)))
        out.append(_call(lambda: fn("LB_TEST_MISSING")))
    out.append(_call(lambda: fn()))
    return out


def _a2(fn, mod):
    values = [" audit ", " ", None, "", 0, "x", [], 5, False, _Odd()]
    return [_call(lambda v=v: fn(v)) for v in values] + [_call(lambda: fn()), _call(lambda: fn(value="named"))]


def _a3(fn, mod):
    return [_call(lambda v=v: fn(v)) for v in _TOKENS] + [_call(lambda: fn())]


def _a4(fn, mod):
    patcher = mock.patch.object(lb, "time", mock.Mock(time=lambda: 2000.0))
    patcher.start()
    try:
        return _a4_cases(fn, mod)
    finally:
        patcher.stop()


def _a4_cases(fn, mod):
    out = [
        _call(lambda: fn({"touched_at_epoch": 123.5}, stale_after_sec=30)),
        _call(lambda: fn({"heartbeat_epoch": "7.5", "touched_at_epoch": 0}, stale_after_sec=30)),
        _call(lambda: fn({"started_at_epoch": 9}, stale_after_sec=30)),
        _call(lambda: fn({"touched_at_epoch": "bad"}, stale_after_sec=30)),
        _call(lambda: fn({"touched_at_epoch": -5}, stale_after_sec=30)),
        _call(lambda: fn({"touched_at_epoch": 0, "started_at": "2026-11-01T00:00:00+00:00"}, stale_after_sec=30)),
        _call(lambda: fn({}, stale_after_sec=0)),
        _call(lambda: fn(None, stale_after_sec=1)),
        _call(lambda: fn({})),
        _call(lambda: fn({"touched_at_epoch": 5})),
    ]
    with mock.patch.object(lb, "_to_epoch", lambda text: 500 if text else None):
        out.append(_call(lambda: fn({"started_at": "fake"}, stale_after_sec=30)))
        out.append(_call(lambda: fn({}, stale_after_sec=30)))
    fake_time = mock.Mock(time=lambda: 1000.0)
    with mock.patch.object(lb, "_to_epoch", lambda text: None), mock.patch.object(lb, "time", fake_time):
        out.append(_call(lambda: fn({}, stale_after_sec=30)))
        out.append(_call(lambda: fn({"started_at": " x "}, stale_after_sec=2.5)))
    with mock.patch.object(lb, "_to_epoch", lambda text: 0):
        with mock.patch.object(lb, "time", fake_time):
            out.append(_call(lambda: fn({"started_at": "z"}, stale_after_sec=10)))
    return out


def _a5(fn, mod):
    values = [0, -1, 1, 59, 60, 90, 3599, 3600, 7200, 5400, 10**6, 59.9, 3599.9, "5", None, True, [], 1.5]
    return [_call(lambda v=v: fn(v)) for v in values] + [_call(lambda: fn())]


def _a6(fn, mod):
    values = ["TRD_20261101_005930_12", "", "broken", None, "a_b_c", "TRD_1_x", "12", " 7 ", "t_-3", "t_1.5", "t_٣", 0, 5, "TRD__9", "_", "A_B_ 4 ", _Odd()]
    return [_call(lambda v=v: fn(v)) for v in values] + [_call(lambda: fn())]


def _a7(fn, mod):
    return [
        _call(lambda: fn(Path("/tmp/fake"), "daily", "2026-11-01")),
        _call(lambda: fn(Path("rel"), "p", "d")),
        _call(lambda: fn(Path("/tmp/fake"), "", "")),
        _call(lambda: fn(Path("/tmp/fake"), "a_b", 20261101)),
        _call(lambda: fn("/tmp/fake", "daily", "d")),
        _call(lambda: fn(None, "daily", "d")),
        _call(lambda: fn(Path("/tmp/fake"), None, None)),
        _call(lambda: fn(Path("/tmp/fake"), "daily")),
        _call(lambda: fn()),
    ]


def _a8(fn, mod):
    values = ["/Date(123000)/", "", "nonsense", None, "/Date(0)/", "x/Date(5000)y", "/Date(abc)/", "/Date(1700000000000+0900)/", " /Date(99)/ ", 0, [], "/Date(", _Odd()]
    out = [_call(lambda v=v: fn(v)) for v in values] + [_call(lambda: fn())]
    fake_re = mock.Mock(search=lambda pattern, raw: mock.Mock(group=lambda i: "2000"))
    with mock.patch.object(lb, "re", fake_re):
        out.append(_call(lambda: fn("anything")))
        out.append(_call(lambda: fn("")))
    bad_re = mock.Mock(search=lambda pattern, raw: mock.Mock(group=lambda i: "nan-text"))
    with mock.patch.object(lb, "re", bad_re):
        out.append(_call(lambda: fn("anything")))
    return out


CASES = {
    "a1": (_a1, "_env_bool", lambda: env_owner._env_bool, True, env_owner),
    "a2": (_a2, "_bundle_role", lambda: role_owner._bundle_role, False, role_owner),
    "a3": (_a3, "_is_trueish", lambda: trueish_owner._is_trueish, False, trueish_owner),
    "a4": (_a4, "_lock_timestamp_epoch", lambda: lock_owner._lock_timestamp_epoch, True, lock_owner),
    "a5": (_a5, "_format_duration_human", lambda: duration_owner._format_duration_human, False, duration_owner),
    "a6": (_a6, "_trade_id_sequence", lambda: sequence_owner._trade_id_sequence, False, sequence_owner),
    "a7": (_a7, "_resolve_existing_day_artifact", lambda: artifact_owner._resolve_existing_day_artifact, False, artifact_owner),
    "a8": (_a8, "_creation_epoch_from_wmi", lambda: wmi_owner._creation_epoch_from_wmi, True, wmi_owner),
}


def _run(key, which):
    scenario, name, owner_factory, facade, _ = CASES[key]
    if which == "wrapper":
        fn = getattr(lb, name)
    else:
        raw = owner_factory()
        fn = (lambda *a, **k: raw(*a, facade=lb, **k)) if facade else raw
    return json.loads(json.dumps(scenario(fn, lb), default=repr))


class Test(unittest.TestCase):
    def _parity(self, key):
        a = _run(key, "wrapper")
        b = _run(key, "owner")
        self.assertEqual(a, b)
        self.assertEqual(_h(a), GOLDENS[key])
        name, owner_mod = CASES[key][1], CASES[key][4]
        fn = ast.parse(inspect.getsource(getattr(lb, name))).body[0]
        stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
        self.assertTrue(len(stmts) == 1 and isinstance(stmts[0], ast.Return))
        self.assertNotIn("import live_execution_bundle_runner", inspect.getsource(owner_mod))
        return a

    def test_a1_env_bool(self):
        out = self._parity("a1")
        with mock.patch.object(lb, "os", _FakeOS("YES")):
            self.assertIs(lb._env_bool("X"), True)
        with mock.patch.object(lb, "os", _FakeOS("off")):
            self.assertIs(lb._env_bool("X"), False)
        with mock.patch.object(lb, "os", _FakeOS(None)):
            self.assertIs(lb._env_bool("X", default=False), False)
        self.assertEqual(out[-1][0], "exc")

    def test_a2_bundle_role(self):
        self._parity("a2")
        self.assertEqual(lb._bundle_role(" audit "), "audit")
        self.assertEqual(lb._bundle_role(" "), "intraday_trade_report_bundle")
        self.assertEqual(lb._bundle_role(None), "intraday_trade_report_bundle")
        self.assertEqual(lb._bundle_role(), "intraday_trade_report_bundle")

    def test_a3_trueish(self):
        out = self._parity("a3")
        for token, expected in (("YES", True), ("y", True), ("on", True), ("false", False), (None, False)):
            self.assertIs(lb._is_trueish(token), expected)
        self.assertEqual(out[-1][0], "exc")

    def test_a4_lock_epoch(self):
        self._parity("a4")
        self.assertEqual(lb._lock_timestamp_epoch({"touched_at_epoch": 123.5}, stale_after_sec=30), 123.5)
        with mock.patch.object(lb, "_to_epoch", lambda text: 500):
            self.assertEqual(lb._lock_timestamp_epoch({"started_at": "fake"}, stale_after_sec=30), 500)
        with mock.patch.object(lb, "_to_epoch", lambda text: None), mock.patch.object(lb, "time", mock.Mock(time=lambda: 1000.0)):
            self.assertEqual(lb._lock_timestamp_epoch({}, stale_after_sec=30), 969.0)

    def test_a5_duration_human(self):
        self._parity("a5")
        for seconds, expected in ((0, "0m"), (59, "59s"), (90, "1.5m"), (7200, "2.0h")):
            self.assertEqual(lb._format_duration_human(seconds), expected)

    def test_a6_trade_sequence(self):
        self._parity("a6")
        self.assertEqual(lb._trade_id_sequence("TRD_20261101_005930_12"), 12)
        self.assertEqual(lb._trade_id_sequence(""), 10**9)
        self.assertEqual(lb._trade_id_sequence("broken"), 10**9)

    def test_a7_artifact_paths(self):
        self._parity("a7")
        self.assertEqual(
            lb._resolve_existing_day_artifact(Path("/tmp/fake"), "daily", "2026-11-01"),
            (Path("/tmp/fake/daily_2026-11-01.md"), Path("/tmp/fake/daily_2026-11-01.json")),
        )

    def test_a8_wmi_epoch(self):
        out = self._parity("a8")
        self.assertEqual(lb._creation_epoch_from_wmi("/Date(123000)/"), 123.0)
        self.assertEqual(lb._creation_epoch_from_wmi(""), 0.0)
        self.assertEqual(lb._creation_epoch_from_wmi("nonsense"), 0.0)
        self.assertEqual(out[-3], ["ok", 2.0])
        self.assertEqual(out[-1], ["ok", 0.0])


if __name__ == "__main__":
    unittest.main()
