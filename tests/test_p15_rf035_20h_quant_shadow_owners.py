"""P15 RF-035 (20h): eight more quant_shadow_candidate_evaluation bodies moved to projection Owners; parity with the pre-move bodies (stdlib unittest)."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import unittest
from types import MappingProxyType
from unittest import mock

from libs.reporting import quant_shadow_candidate_evaluation as qs
from libs.reporting import quant_shadow_checkpoint_projection as checkpoint_owner
from libs.reporting import quant_shadow_cost_floor_projection as cost_owner
from libs.reporting import quant_shadow_entry_decision_projection as decision_owner
from libs.reporting import quant_shadow_entry_shape_projection as shape_owner
from libs.reporting import quant_shadow_forward_base_projection as base_owner
from libs.reporting import quant_shadow_forward_outcome_projection as outcome_owner
from libs.reporting import quant_shadow_tactic_projection as tactic_owner
from libs.reporting import quant_shadow_tactic_tier_projection as tier_owner

GOLDENS = {
    "a1": "297361c3720ba046c93eb6f0edf3b1b2df06c1ebfa69fb592f7f747785f1eec5",
    "a2": "c2d57d8b6ab1f4a5bd6e290fc3846d4a6cdce5cd206e6d00e6531755a2c22749",
    "a3": "5c0028602ee8f50334fc676be58651b4ae36e3fde4120153bc8716823e3a73f3",
    "a4": "447a367ddabffd814d5592e5d614c7a2751becd24deb4867837a9d253f326f6f",
    "a5": "1dcaba9f7ec67f3341cb2348636c95da4f9b7ff6a86d2650e86ebebb76a39dd4",
    "a6": "c6a5a1e0059a0572427f5e4fc3b309bd0eb4896f47d109e234297f5ea38efe8b",
    "a7": "5a9fb8332d7e332546a2c77485f66db10f7387abefdd17f8e62b6f44f3b958f1",
    "a8": "cc4cf51071a8ef3ca3c01e8a7853d37bad95841397f98d88f73a972e5c22ef7f",
}


def _call(fn):
    try:
        return ["ok", fn()]
    except BaseException as exc:  # noqa: BLE001 - parity of exception type/message is the point
        return ["exc", type(exc).__name__, str(exc)]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, default=repr).encode()).hexdigest()


def _text_patch():
    return mock.patch.object(qs, "_text", lambda v: "T" if v else "")


def _a1(fn, mod):
    out = [
        _call(lambda: fn({"entry_quant_cost_floor_state": "safe"})),
        _call(lambda: fn({"entry_quant_decision": {"cost_edge": {"cost_floor_state": "hold"}}})),
        _call(lambda: fn({})),
        _call(lambda: fn({"entry_quant_cost_floor_state": "safe", "entry_quant_decision": {"cost_edge": {"cost_floor_state": "hold"}}})),
        _call(lambda: fn({"entry_quant_decision": {"cost_edge": {"cost_floor_state": "none"}}, "quant_factor_snapshot": {"factors": {"cost_floor_state": "snap"}}})),
        _call(lambda: fn({"quant_factor_snapshot": {"factors": {"cost_floor_state": " fac "}}})),
        _call(lambda: fn({"quant_factor_snapshot": {"factors": [1]}})),
        _call(lambda: fn({"quant_factor_snapshot": [1], "entry_quant_decision": "x"})),
        _call(lambda: fn({"entry_quant_decision": {"cost_edge": [1]}})),
        _call(lambda: fn({"entry_quant_cost_floor_state": "-", "quant_factor_snapshot": {"factors": {"cost_floor_state": "Unknown"}}})),
        _call(lambda: fn(MappingProxyType({"entry_quant_decision": MappingProxyType({"cost_edge": {"cost_floor_state": "p"}})}))),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    with _text_patch():
        out.append(_call(lambda: fn({"quant_factor_snapshot": {"factors": {"cost_floor_state": "z"}}})))
    with mock.patch.object(qs, "Mapping", tuple):
        out.append(_call(lambda: fn({"entry_quant_decision": {"cost_edge": {"cost_floor_state": "hold"}}})))
    return out


def _a2(fn, mod):
    out = [
        _call(lambda: fn({"entry_quant_decision": {"decision": "entry_ready"}})),
        _call(lambda: fn({})),
        _call(lambda: fn({"entry_quant_decision": {"decision": " NONE "}})),
        _call(lambda: fn({"entry_quant_decision": {"decision": "-"}})),
        _call(lambda: fn({"entry_quant_decision": "entry_ready"})),
        _call(lambda: fn({"entry_quant_decision": MappingProxyType({"decision": "mp"})})),
        _call(lambda: fn({"entry_quant_decision": {}})),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    with _text_patch():
        out.append(_call(lambda: fn({"entry_quant_decision": {"decision": "d"}})))
    with mock.patch.object(qs, "Mapping", tuple):
        out.append(_call(lambda: fn({"entry_quant_decision": {"decision": "d"}})))
    return out


def _a3(fn, mod):
    out = [
        _call(lambda: fn({"quant_tactic_id": "T1"})),
        _call(lambda: fn({"entry_quant_decision": {"tactic_id": "T2"}})),
        _call(lambda: fn({})),
        _call(lambda: fn({"tactic_id": "T3", "entry_quant_decision": {"tactic_id": "T2"}})),
        _call(lambda: fn({"quant_tactic_id": "", "tactic_id": " T4 "})),
        _call(lambda: fn({"quant_factor_snapshot": {"tactic_id": "T5"}})),
        _call(lambda: fn({"entry_quant_decision": {"tactic_id": "none"}, "quant_factor_snapshot": {"tactic_id": "T6"}})),
        _call(lambda: fn({"entry_quant_decision": [1], "quant_factor_snapshot": [1]})),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    with _text_patch():
        out.append(_call(lambda: fn({"quant_tactic_id": "x"})))
    with mock.patch.object(qs, "Mapping", tuple):
        out.append(_call(lambda: fn({"quant_factor_snapshot": {"tactic_id": "T5"}})))
    return out


def _a4(fn, mod):
    out = [
        _call(lambda: fn({"tactic_suitability_tier": "high"})),
        _call(lambda: fn({"entry_quant_decision": {"tactic_suitability": {"tier": "low"}}})),
        _call(lambda: fn({})),
        _call(lambda: fn({"tactic_suitability_tier": "high", "entry_quant_decision": {"tactic_suitability": {"tier": "low"}}})),
        _call(lambda: fn({"tactic_suitability_tier": "null", "entry_quant_decision": {"tactic_suitability": {"tier": "mid"}}})),
        _call(lambda: fn({"entry_quant_decision": {"tactic_suitability": "x"}})),
        _call(lambda: fn({"entry_quant_decision": "x"})),
        _call(lambda: fn({"entry_quant_decision": {"tactic_suitability": {"tier": ""}}})),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    with _text_patch():
        out.append(_call(lambda: fn({"tactic_suitability_tier": "q"})))
    with mock.patch.object(qs, "Mapping", tuple):
        out.append(_call(lambda: fn({"entry_quant_decision": {"tactic_suitability": {"tier": "low"}}})))
    return out


def _copy_cases(key):
    def scenario(fn, mod):
        inner = {"a": 1}
        row = {key: inner}
        res = fn(row)
        out = [
            ["copy", [res == inner, res is not inner]],
            _call(lambda: fn({})),
            _call(lambda: fn({key: [("a", 1)]})),
            _call(lambda: fn({key: None})),
            _call(lambda: fn({key: MappingProxyType({"m": 2})})),
            _call(lambda: fn({key: {}})),
            _call(lambda: fn({key: {"checkpoints": {}}})),
            _call(lambda: fn(None)),
            _call(lambda: fn()),
        ]
        with mock.patch.object(qs, "Mapping", tuple):
            out.append(_call(lambda: fn({key: {"a": 1}})))
        with mock.patch.object(qs, "Mapping", dict):
            out.append(_call(lambda: fn({key: MappingProxyType({"a": 1})})))
        return out

    return scenario


def _a7(fn, mod):
    reasons = [
        "pullback_not_mature", "pullback_below_vwap_reclaim_not_ready", "pullback_structure_above_vwap_with_volume_confirmation",
        "below_vwap_reclaim_not_ready", "breakout_above_recent_high_with_vwap_hold_and_volume_confirmation",
        "breakout_above_recent_high_with_vwap_structure_confirmation", "breakout_not_ready", "volume_confirmation_missing",
        "volume_insufficient", "human_chart_sanity_guard_blocked", "something_else", "", None, " breakout_not_ready ",
    ]
    axes = ["pullback_structure", "vwap_relationship", "breakout_readiness", "volume_confirmation", "human_chart_sanity", "other", "", None]
    out = [_call(lambda r=r: fn({"reason": r})) for r in reasons]
    out += [_call(lambda a=a: fn({"primary_failure_axis": a})) for a in axes]
    out += [
        _call(lambda: fn({"reason": "breakout_not_ready", "primary_failure_axis": "pullback_structure"})),
        _call(lambda: fn({"reason": "volume_confirmation_missing", "primary_failure_axis": "vwap_relationship"})),
        _call(lambda: fn({"reason": "pullback_below_vwap_reclaim_not_ready", "primary_failure_axis": "vwap_relationship"})),
        _call(lambda: fn({})),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    with mock.patch.object(qs, "_text", lambda v: "breakout_not_ready"):
        out.append(_call(lambda: fn({"reason": "zzz"})))
    with mock.patch.object(qs, "_text", lambda v: "human_chart_sanity"):
        out.append(_call(lambda: fn({"reason": "zzz"})))
    return out


def _a8(fn, mod):
    obs = {"shadow_forward_outcome": {"checkpoints": {"5m": {"status": "observed", "ret": "1.25", "z": 0, "e": "", "n": None, "b": "bad", "l": [1]}}}}
    out = [
        _call(lambda: fn(obs, "5m", "ret")),
        _call(lambda: fn({"shadow_forward_outcome": {"checkpoints": {"5m": {"status": "pending", "ret": 3}}}}, "5m", "ret")),
        _call(lambda: fn(obs, "5m", "z")),
        _call(lambda: fn(obs, "5m", "e")),
        _call(lambda: fn(obs, "5m", "n")),
        _call(lambda: fn(obs, "5m", "missing")),
        _call(lambda: fn(obs, "5m", "b")),
        _call(lambda: fn(obs, "5m", "l")),
        _call(lambda: fn(obs, "15m", "ret")),
        _call(lambda: fn({}, "5m", "ret")),
        _call(lambda: fn({"shadow_forward_outcome": {"checkpoints": [1]}}, "5m", "ret")),
        _call(lambda: fn({"shadow_forward_outcome": {"checkpoints": {"5m": "x"}}}, "5m", "ret")),
        _call(lambda: fn({"shadow_forward_outcome": {"checkpoints": {"5m": {"status": " OBSERVED ", "ret": 2}}}}, "5m", "ret")),
        _call(lambda: fn(None, "5m", "ret")),
        _call(lambda: fn(obs, "5m")),
    ]
    with mock.patch.object(qs, "_forward_outcome", lambda row: {"checkpoints": {"1m": {"status": "observed", "m": "4"}}}):
        out.append(_call(lambda: fn({}, "1m", "m")))
    with _text_patch():
        out.append(_call(lambda: fn(obs, "5m", "ret")))
    with mock.patch.object(qs, "Mapping", tuple):
        out.append(_call(lambda: fn(obs, "5m", "ret")))
    return out


CASES = {
    "a1": (_a1, "_cost_floor_state", lambda: cost_owner._cost_floor_state, cost_owner),
    "a2": (_a2, "_entry_quant_decision", lambda: decision_owner._entry_quant_decision, decision_owner),
    "a3": (_a3, "_tactic_id", lambda: tactic_owner._tactic_id, tactic_owner),
    "a4": (_a4, "_tactic_suitability_tier", lambda: tier_owner._tactic_suitability_tier, tier_owner),
    "a5": (_copy_cases("shadow_forward_base"), "_forward_base", lambda: base_owner._forward_base, base_owner),
    "a6": (_copy_cases("shadow_forward_outcome"), "_forward_outcome", lambda: outcome_owner._forward_outcome, outcome_owner),
    "a7": (_a7, "_entry_shape", lambda: shape_owner._entry_shape, shape_owner),
    "a8": (_a8, "_checkpoint_value", lambda: checkpoint_owner._checkpoint_value, checkpoint_owner),
}


def _run(key, which):
    scenario, name, owner_factory, _ = CASES[key]
    if which == "wrapper":
        fn = getattr(qs, name)
    else:
        raw = owner_factory()
        fn = lambda *a, **k: raw(*a, facade=qs, **k)  # noqa: E731
    return json.loads(json.dumps(scenario(fn, qs), default=repr))


class Test(unittest.TestCase):
    def _parity(self, key):
        a = _run(key, "wrapper")
        b = _run(key, "owner")
        self.assertEqual(a, b)
        self.assertEqual(_h(a), GOLDENS[key])
        name, owner_mod = CASES[key][1], CASES[key][3]
        fn = ast.parse(inspect.getsource(getattr(qs, name))).body[0]
        stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
        self.assertTrue(len(stmts) == 1 and isinstance(stmts[0], ast.Return))
        self.assertNotIn("import quant_shadow_candidate_evaluation", inspect.getsource(owner_mod))
        self.assertIn("facade", inspect.getsource(getattr(owner_mod, name)))
        return a

    def test_a1_cost_floor_state(self):
        out = self._parity("a1")
        self.assertEqual(qs._cost_floor_state({"entry_quant_cost_floor_state": "safe"}), "safe")
        self.assertEqual(qs._cost_floor_state({"entry_quant_decision": {"cost_edge": {"cost_floor_state": "hold"}}}), "hold")
        self.assertEqual(qs._cost_floor_state({}), "")
        self.assertEqual(out[3], ["ok", "safe"])
        self.assertEqual(out[-1], ["ok", ""])

    def test_a2_entry_quant_decision(self):
        out = self._parity("a2")
        self.assertEqual(qs._entry_quant_decision({"entry_quant_decision": {"decision": "entry_ready"}}), "entry_ready")
        self.assertEqual(qs._entry_quant_decision({}), "")
        self.assertEqual(out[-2], ["ok", "T"])
        self.assertEqual(out[-1], ["ok", ""])

    def test_a3_tactic_id(self):
        self._parity("a3")
        self.assertEqual(qs._tactic_id({"quant_tactic_id": "T1"}), "T1")
        self.assertEqual(qs._tactic_id({"entry_quant_decision": {"tactic_id": "T2"}}), "T2")
        self.assertEqual(qs._tactic_id({}), "")

    def test_a4_tactic_suitability_tier(self):
        self._parity("a4")
        self.assertEqual(qs._tactic_suitability_tier({"tactic_suitability_tier": "high"}), "high")
        self.assertEqual(qs._tactic_suitability_tier({"entry_quant_decision": {"tactic_suitability": {"tier": "low"}}}), "low")
        self.assertEqual(qs._tactic_suitability_tier({}), "")

    def test_a5_forward_base(self):
        out = self._parity("a5")
        inner = {"a": 1}
        res = qs._forward_base({"shadow_forward_base": inner})
        self.assertEqual(res, {"a": 1})
        self.assertIsNot(res, inner)
        self.assertEqual(qs._forward_base({}), {})
        self.assertEqual(out[-2], ["ok", {}])

    def test_a6_forward_outcome(self):
        out = self._parity("a6")
        inner = {"checkpoints": {}}
        res = qs._forward_outcome({"shadow_forward_outcome": inner})
        self.assertEqual(res, {"checkpoints": {}})
        self.assertIsNot(res, inner)
        self.assertEqual(qs._forward_outcome({}), {})
        self.assertEqual(out[-2], ["ok", {}])

    def test_a7_entry_shape(self):
        out = self._parity("a7")
        self.assertEqual(qs._entry_shape({"reason": "breakout_not_ready"}), "breakout")
        self.assertEqual(qs._entry_shape({"primary_failure_axis": "volume_confirmation"}), "volume_confirmation")
        self.assertEqual(qs._entry_shape({}), "other")
        self.assertEqual(out[-2], ["ok", "breakout"])

    def test_a8_checkpoint_value(self):
        out = self._parity("a8")
        obs = {"shadow_forward_outcome": {"checkpoints": {"5m": {"status": "observed", "ret": "1.25"}}}}
        self.assertEqual(qs._checkpoint_value(obs, "5m", "ret"), 1.25)
        self.assertIsNone(qs._checkpoint_value({"shadow_forward_outcome": {"checkpoints": {"5m": {"status": "pending", "ret": 3}}}}, "5m", "ret"))
        self.assertEqual(out[-3], ["ok", 4.0])
        self.assertEqual(out[-1], ["ok", None])


if __name__ == "__main__":
    unittest.main()
