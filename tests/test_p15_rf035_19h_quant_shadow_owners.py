"""P15 RF-035 (19h): eight quant_shadow_candidate_evaluation bodies moved to projection Owners; parity with the pre-move bodies (stdlib unittest)."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import types
import unittest
from collections import Counter
from unittest import mock

from libs.reporting import quant_shadow_blocker_projection as blocker_owner
from libs.reporting import quant_shadow_candidate_evaluation as qs
from libs.reporting import quant_shadow_counter_projection as counter_owner
from libs.reporting import quant_shadow_day_projection as day_owner
from libs.reporting import quant_shadow_mean_projection as mean_owner
from libs.reporting import quant_shadow_reason_projection as reason_owner
from libs.reporting import quant_shadow_runnerup_projection as runnerup_owner
from libs.reporting import quant_shadow_scalar_projection as scalar_owner
from libs.reporting import quant_shadow_scorecard_signal_projection as signal_owner

GOLDENS = {
    "a1": "b2e5d4b414ef543be10197e3d9e5c4555ce1a5ca43b707ffe73a31f9e2c2b789",
    "a2": "6e2510ae00861781b19267abb7e59f36c5b1f490831c2767a43f4decab72051c",
    "a3": "0ba97749c6ebdd6dc1dac37edc7f9329ecab5a64d493c255c11f57d0b27ea27b",
    "a4": "51682802bf5af922b0198c54117f5097ebd9f326ca167202033b624954b5be3e",
    "a5": "28584c1fd2ceb968304b9427f8f72846167882bc05cd204f7a960516663a8622",
    "a6": "069037b8b0a07c6994d671e93bbfa1725c9677e0f270e37aaa093c25ead35262",
    "a7": "2537a91f573d682703679e581875fd79761a548f16e8d86887e257b93ff09108",
    "a8": "6cf1d6b2c1538a391af67b8b66a615a2d2db85ea7b7e4d10d818880272a9348a",
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
        return "Y"


def _a1(fn, mod):
    values = [True, False, 0, 1, 2.5, 0.0, "YES", " y ", "on", "1", "true", "off", "no", "", None, [], [1], {}, "False", _Odd()]
    return [_call(lambda v=v: fn(v)) for v in values] + [_call(lambda: fn())]


def _a2(fn, mod):
    gen = fn("bad", "bad")
    out = [
        ["lazy", [isinstance(gen, types.GeneratorType)]],
        _call(lambda: list(fn("2026-10-30", "2026-10-31"))),
        _call(lambda: list(fn("2026-10-31", "2026-10-30"))),
        _call(lambda: list(fn("2026-02-27T10:00:00", "2026-03-02"))),
        _call(lambda: list(fn("bad", "2026-10-30"))),
        _call(lambda: list(fn("2026-10-30", "x"))),
        _call(lambda: list(fn(20261030, "2026-10-31"))),
        _call(lambda: list(fn("2026-10-30"))),
    ]
    it = fn("2026-10-30", "2026-11-02")
    out.append(["partial", [next(it), next(it)]])
    with mock.patch.object(mod, "timedelta", lambda days: __import__("datetime").timedelta(days=2 * days)):
        out.append(_call(lambda: list(fn("2026-10-30", "2026-11-03"))))
    return out


def _a3(fn, mod):
    return [
        _call(lambda: fn(Counter({"a": 2, "b": 1}), limit=1)),
        _call(lambda: fn(Counter())),
        _call(lambda: fn(Counter({"": 5, "x": 1}))),
        _call(lambda: fn(Counter({"a": 1, "b": 1, "c": 1}), limit=2)),
        _call(lambda: fn(Counter("aab" * 3), limit=0)),
        _call(lambda: fn(Counter({str(i): i for i in range(1, 12)}))),
        _call(lambda: fn(Counter({"a": 1}), limit=-1)),
        _call(lambda: fn(None)),
        _call(lambda: fn([("a", 1)])),
        _call(lambda: fn()),
    ]


def _a4(fn, mod):
    out = [
        _call(lambda: fn({"blockers": ["a", ""]})),
        _call(lambda: fn({"entry_quant_decision": {"blockers": ["b", "b"]}})),
        _call(lambda: fn({"blockers": ["x", None, " y ", "none", "Unknown"], "entry_quant_decision": {"blockers": ["z", "-"]}})),
        _call(lambda: fn({"blockers": "a", "entry_quant_decision": {"blockers": ("t",)}})),
        _call(lambda: fn({"entry_quant_decision": [1]})),
        _call(lambda: fn({})),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    with mock.patch.object(mod, "_text", lambda v: "T" if v else ""):
        out.append(_call(lambda: fn({"blockers": ["a", "", "b"], "entry_quant_decision": {"blockers": ["c"]}})))
    with mock.patch.object(mod, "Mapping", dict):
        out.append(_call(lambda: fn({"entry_quant_decision": {"blockers": ["m"]}})))
    with mock.patch.object(mod, "Mapping", tuple):
        out.append(_call(lambda: fn({"entry_quant_decision": {"blockers": ["m"]}})))
    return out


def _a5(fn, mod):
    out = [
        _call(lambda: fn([{"reason": "bad"}], {"bad"})),
        _call(lambda: fn([], {"bad"})),
        _call(lambda: fn([{"primary_failure_axis": "ax"}, {"reason": "zz"}], {"ax"})),
        _call(lambda: fn([{"blockers": ["bad", "bad"]}, {"entry_quant_decision": {"blockers": ["bad"]}}], {"bad"})),
        _call(lambda: fn([{"reason": "bad", "blockers": ["bad"]}], {"bad"})),
        _call(lambda: fn([{"entry_quant_cost_floor_state": "floor_x"}], {"floor_x"})),
        _call(lambda: fn([{"reason": "n"}], set())),
        _call(lambda: fn([None], {"bad"})),
        _call(lambda: fn(None, {"bad"})),
        _call(lambda: fn([{"reason": "bad"}])),
    ]
    rows = [{"reason": "a"}, {"reason": "b"}]
    with mock.patch.object(mod, "_cost_floor_state", lambda row: "cf" if row["reason"] == "a" else ""):
        out.append(_call(lambda: fn(rows, {"cf"})))
    with mock.patch.object(mod, "_row_blockers", lambda row: ["hit"]):
        out.append(_call(lambda: fn(rows, {"hit"})))
    with mock.patch.object(mod, "_text", lambda v: "bad"):
        out.append(_call(lambda: fn(rows, {"bad"})))
    return out


def _a6(fn, mod):
    role = {"shadow_role": "runner_up_evaluated"}
    out = [
        _call(lambda: fn([dict(role, would_enter=True)])),
        _call(lambda: fn([{"shadow_role": "other", "would_enter": True}])),
        _call(lambda: fn([dict(role, runner_up_quality_blocked="yes"), dict(role, weak_fallback_blocked=1)])),
        _call(lambda: fn([dict(role, reason="runner_up_quality_gate_failed"), dict(role, reason="weak_fallback_pullback"), dict(role, reason="other")])),
        _call(lambda: fn([dict(role, would_enter=True, runner_up_quality_blocked=True, reason="weak_fallback_pullback")])),
        _call(lambda: fn([])),
        _call(lambda: fn([None])),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    with mock.patch.object(mod, "_bool", lambda v: True):
        out.append(_call(lambda: fn([dict(role), {"shadow_role": "x"}])))
    with mock.patch.object(mod, "_text", lambda v: "runner_up_evaluated"):
        out.append(_call(lambda: fn([{"reason": "weak_fallback_pullback"}, {}])))
    return out


def _a7(fn, mod):
    return [
        _call(lambda: fn([])),
        _call(lambda: fn([1.0, None, 3.0])),
        _call(lambda: fn(["bad"])),
        _call(lambda: fn([None, None])),
        _call(lambda: fn(["1.5", 2])),
        _call(lambda: fn([1, 2, 2])),
        _call(lambda: fn([0.00005, 0.00004])),
        _call(lambda: fn((x for x in [1.0, 2.0]))),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
        _call(lambda: fn([float("inf"), 1.0])),
    ]


def _a8(fn, mod):
    return [
        _call(lambda: fn({"avg_return_15m_pct": "0.2"})),
        _call(lambda: fn({"avg_return_15m_pct": "bad", "avg_return_5m_pct": "0.4"})),
        _call(lambda: fn({})),
        _call(lambda: fn({"avg_return_15m_pct": "", "avg_return_30m_pct": 3, "avg_return_3m_pct": 9})),
        _call(lambda: fn({"avg_return_3m_pct": "1e-2"})),
        _call(lambda: fn({"avg_return_15m_pct": 0, "avg_return_5m_pct": 1})),
        _call(lambda: fn({"avg_return_15m_pct": [1], "avg_return_5m_pct": None})),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]


CASES = {
    "a1": (_a1, "_bool", lambda: scalar_owner._bool, False, scalar_owner),
    "a2": (_a2, "_iter_days", lambda: day_owner._iter_days, True, day_owner),
    "a3": (_a3, "_top_counter", lambda: counter_owner._top_counter, False, counter_owner),
    "a4": (_a4, "_row_blockers", lambda: blocker_owner._row_blockers, True, blocker_owner),
    "a5": (_a5, "_count_reason", lambda: reason_owner._count_reason, True, reason_owner),
    "a6": (_a6, "_runner_up_risk_count", lambda: runnerup_owner._runner_up_risk_count, True, runnerup_owner),
    "a7": (_a7, "_mean", lambda: mean_owner._mean, False, mean_owner),
    "a8": (_a8, "_scorecard_return_signal", lambda: signal_owner._scorecard_return_signal, False, signal_owner),
}


def _run(key, which):
    scenario, name, owner_factory, facade, _ = CASES[key]
    if which == "wrapper":
        fn = getattr(qs, name)
    else:
        raw = owner_factory()
        fn = (lambda *a, **k: raw(*a, facade=qs, **k)) if facade else raw
    return json.loads(json.dumps(scenario(fn, qs), default=repr))


class Test(unittest.TestCase):
    def _parity(self, key):
        a = _run(key, "wrapper")
        b = _run(key, "owner")
        self.assertEqual(a, b)
        self.assertEqual(_h(a), GOLDENS[key])
        name, owner_mod = CASES[key][1], CASES[key][4]
        fn = ast.parse(inspect.getsource(getattr(qs, name))).body[0]
        stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
        self.assertEqual(len(stmts), 1)
        if key == "a2":
            self.assertTrue(isinstance(stmts[0], ast.Expr) and isinstance(stmts[0].value, ast.YieldFrom))
        else:
            self.assertIsInstance(stmts[0], ast.Return)
        self.assertNotIn("import quant_shadow_candidate_evaluation", inspect.getsource(owner_mod))
        return a

    def test_a1_bool(self):
        self._parity("a1")
        self.assertIs(qs._bool(True), True)
        self.assertIs(qs._bool("YES"), True)
        self.assertIs(qs._bool("off"), False)
        self.assertIs(qs._bool(0), False)

    def test_a2_iter_days(self):
        out = self._parity("a2")
        self.assertEqual(out[0], ["lazy", [True]])
        self.assertEqual(list(qs._iter_days("2026-10-30", "2026-10-31")), ["2026-10-30", "2026-10-31"])
        self.assertEqual(list(qs._iter_days("2026-10-31", "2026-10-30")), [])
        with self.assertRaises(ValueError):
            list(qs._iter_days("bad", "2026-10-30"))
        self.assertEqual(out[-1], ["ok", ["2026-10-30", "2026-11-01", "2026-11-03"]])

    def test_a3_top_counter(self):
        self._parity("a3")
        self.assertEqual(qs._top_counter(Counter({"a": 2, "b": 1}), limit=1), [{"name": "a", "count": 2}])
        self.assertEqual(qs._top_counter(Counter()), [])

    def test_a4_row_blockers(self):
        out = self._parity("a4")
        self.assertEqual(qs._row_blockers({"blockers": ["a", ""]}), ["a"])
        self.assertEqual(qs._row_blockers({"entry_quant_decision": {"blockers": ["b", "b"]}}), ["b", "b"])
        self.assertEqual(out[-2], ["ok", ["m"]])
        self.assertEqual(out[-1], ["ok", []])

    def test_a5_count_reason(self):
        out = self._parity("a5")
        self.assertEqual(qs._count_reason([{"reason": "bad"}], {"bad"}), 1)
        self.assertEqual(qs._count_reason([], {"bad"}), 0)
        self.assertEqual(out[3], ["ok", 2])
        self.assertEqual(out[4], ["ok", 1])

    def test_a6_runner_up_risk_count(self):
        out = self._parity("a6")
        self.assertEqual(qs._runner_up_risk_count([{"shadow_role": "runner_up_evaluated", "would_enter": True}]), 1)
        self.assertEqual(qs._runner_up_risk_count([{"shadow_role": "other", "would_enter": True}]), 0)
        self.assertEqual(out[4], ["ok", 1])

    def test_a7_mean(self):
        out = self._parity("a7")
        self.assertIsNone(qs._mean([]))
        self.assertEqual(qs._mean([1.0, None, 3.0]), 2.0)
        with self.assertRaises(ValueError):
            qs._mean(["bad"])
        self.assertEqual(out[2][1], "ValueError")

    def test_a8_scorecard_return_signal(self):
        self._parity("a8")
        self.assertEqual(qs._scorecard_return_signal({"avg_return_15m_pct": "0.2"}), 0.2)
        self.assertEqual(qs._scorecard_return_signal({"avg_return_15m_pct": "bad", "avg_return_5m_pct": "0.4"}), 0.4)
        self.assertIsNone(qs._scorecard_return_signal({}))


if __name__ == "__main__":
    unittest.main()
