"""P15 RF-035 (21h): eight more quant_shadow_candidate_evaluation bodies moved to projection Owners; parity with the pre-move bodies (stdlib unittest)."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import unittest
from collections import Counter
from types import MappingProxyType
from unittest import mock

from libs.reporting import quant_shadow_candidate_evaluation as qs
from libs.reporting import quant_shadow_entry_shape_payload_projection as shape_payload_owner
from libs.reporting import quant_shadow_forward_summary_projection as summary_owner
from libs.reporting import quant_shadow_largecap_enter_projection as largecap_enter_owner
from libs.reporting import quant_shadow_largecap_probe_projection as largecap_probe_owner
from libs.reporting import quant_shadow_opening_probe_enter_projection as opening_enter_owner
from libs.reporting import quant_shadow_opening_probe_projection as opening_probe_owner
from libs.reporting import quant_shadow_top_forward_groups_projection as top_groups_owner
from libs.reporting import quant_shadow_vwap_observation_payload_projection as vwap_payload_owner

GOLDENS = {
    "a1": "83490795e966b05a4e3fe6918221cfde4e5289afb4aa8ecdada3bdedbe94dfd7",
    "a2": "0aa9df1c13aa1e65adf1673e828fd8b5da0a27699b210b22afa7f69138540433",
    "a3": "6386e7a413f7cb95133d19adeb7e3487cd3625a461536641a5a5ea25b4cca7ca",
    "a4": "744250d7ef42348c442451c2e5a75809efe2121520e7d2748f9290195b1a2478",
    "a5": "3bf632ff7ed2e3c3605b2693dcfdc16bfe533118458deedf06ac493c1dca0bbe",
    "a6": "6ed6d8823775e0b951c10139ba388111ea1088f351f0e21055f45ee9e44428dd",
    "a7": "047694637b72dd980225ab490026d49c534ba541efb19ed8a85a6884d1c3e3cd",
    "a8": "c242b7d68bd05e5d5ee47bde216e2f440838911ee3fcb71871435c0b397b1b4f",
}


def _call(fn):
    try:
        return ["ok", fn()]
    except BaseException as exc:  # noqa: BLE001 - parity of exception type/message is the point
        return ["exc", type(exc).__name__, str(exc)]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, default=repr).encode()).hexdigest()


def _copy_cases(key):
    def scenario(fn, mod):
        inner = {"would_probe": 1}
        res = fn({key: inner})
        out = [
            ["copy", [res == inner, res is not inner]],
            _call(lambda: fn({})),
            _call(lambda: fn({key: [("a", 1)]})),
            _call(lambda: fn({key: None})),
            _call(lambda: fn({key: MappingProxyType({"m": 2})})),
            _call(lambda: fn({key: {}})),
            _call(lambda: fn(None)),
            _call(lambda: fn()),
        ]
        with mock.patch.object(qs, "Mapping", tuple):
            out.append(_call(lambda: fn({key: {"a": 1}})))
        with mock.patch.object(qs, "Mapping", dict):
            out.append(_call(lambda: fn({key: MappingProxyType({"a": 1})})))
        return out

    return scenario


def _would_enter_cases(direct_key, shadow_key, probe_name):
    def scenario(fn, mod):
        out = [
            _call(lambda: fn({direct_key: "yes"})),
            _call(lambda: fn({shadow_key: {"would_probe": 1}})),
            _call(lambda: fn({})),
            _call(lambda: fn({direct_key: "off", shadow_key: {"would_probe": 1}})),
            _call(lambda: fn({direct_key: 0, shadow_key: {"would_probe": 1}})),
            _call(lambda: fn({direct_key: "", shadow_key: {"would_probe": "true"}})),
            _call(lambda: fn({direct_key: None, shadow_key: [1]})),
            _call(lambda: fn({direct_key: False})),
            _call(lambda: fn(None)),
            _call(lambda: fn()),
        ]
        with mock.patch.object(qs, probe_name, lambda row: {"would_probe": "on"}):
            out.append(_call(lambda: fn({})))
        with mock.patch.object(qs, "_bool", lambda v: not v):
            out.append(_call(lambda: fn({direct_key: "x"})))
            out.append(_call(lambda: fn({})))
        return out

    return scenario


def _shape_rows():
    return [
        {"reason": "breakout_not_ready", "would_enter": False},
        {"reason": "breakout_above_recent_high_with_vwap_hold_and_volume_confirmation", "would_enter": False},
        {"reason": "breakout_not_ready", "would_enter": True},
        {"reason": "pullback_not_mature"},
        {"primary_failure_axis": "vwap_relationship", "would_enter": "yes"},
        {"reason": "volume_confirmation_missing"},
        {"reason": "zzz"},
        {},
    ]


def _a5(fn, mod):
    rows = _shape_rows()
    out = [
        _call(lambda: fn([])),
        _call(lambda: fn([{"reason": "breakout_not_ready", "would_enter": False}])),
        _call(lambda: fn(rows)),
        _call(lambda: fn(iter(rows[:2]))),
        _call(lambda: fn([None])),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    with mock.patch.object(qs, "_entry_shape", lambda row: "breakout"):
        out.append(_call(lambda: fn(rows)))
    with mock.patch.object(qs, "_top_counter", lambda c, **k: [{"patched": sorted(c.items())}]):
        out.append(_call(lambda: fn(rows)))
    with mock.patch.object(qs, "_bool", lambda v: True):
        out.append(_call(lambda: fn(rows)))
    with mock.patch.object(qs, "_text", lambda v: "breakout_above_recent_high_with_vwap_structure_confirmation"):
        out.append(_call(lambda: fn(rows)))
    with mock.patch.object(qs, "Counter", lambda it: Counter(["x", "x"])):
        out.append(_call(lambda: fn(rows)))
    return out


def _a6(fn, mod):
    obs = {"a": {"applies": True, "subtype": "s1", "subtype_v2": "v1"}, "b": {"applies": "yes", "subtype": "s1", "subtype_v2": "v2"}, "c": {"applies": False, "subtype": "s9"}}
    rows = [{"id": "a"}, {"id": "b"}, {"id": "c"}, {"id": "a"}]
    out = [_call(lambda: fn([]))]
    with mock.patch.object(qs, "_below_vwap_reclaim_observation", lambda row: obs[row["id"]]):
        out.append(_call(lambda: fn(rows)))
    with mock.patch.object(qs, "_below_vwap_reclaim_observation", lambda row: {"applies": True, "subtype": "x"}):
        out.append(_call(lambda: fn([{}])))
    with mock.patch.object(qs, "_below_vwap_reclaim_observation", lambda row: {}):
        out.append(_call(lambda: fn([{}])))
    out.append(_call(lambda: fn([{"reason": "pullback_below_vwap_reclaim_not_ready"}])))
    out.append(_call(lambda: fn(None)))
    out.append(_call(lambda: fn()))
    with mock.patch.object(qs, "_below_vwap_reclaim_observation", lambda row: {"applies": True, "subtype": "q", "subtype_v2": "r"}):
        with mock.patch.object(qs, "_top_counter", lambda c, limit=0: [{"limit": limit, "n": sum(c.values())}]):
            out.append(_call(lambda: fn([{}, {}])))
        with mock.patch.object(qs, "_text", lambda v: "T"):
            out.append(_call(lambda: fn([{}])))
        with mock.patch.object(qs, "_bool", lambda v: False):
            out.append(_call(lambda: fn([{}])))
    return out


def _fw_rows():
    def mk(day, ret3, ret5, mfe=None, avail=True):
        cps = {"+3m": {"status": "observed", "return_pct": ret3, "mfe_pct": mfe}, "+5m": {"status": "observed", "return_pct": ret5, "mfe_pct": mfe, "mae_pct": -1}}
        return {"shadow_forward_base": {"baseline_raw_ts": day + "090000"}, "shadow_forward_outcome": {"available": avail, "checkpoints": cps}}

    return [mk("20261030", "1.0", "2.0", 3.0), mk("20261030", "3.0", "4.0"), mk("20261031", None, "6.0"), {"generated_at": "2026-10-31T00:00:00"}, mk("20261029", "x", "y", avail=False)]


def _a7(fn, mod):
    rows = _fw_rows()
    out = [
        _call(lambda: fn([])),
        _call(lambda: fn(rows[:3])),
        _call(lambda: fn([rows[3]])),
        _call(lambda: fn([rows[0]])),
        _call(lambda: fn(rows[:2] + [rows[3]])),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
        _call(lambda: fn([None])),
    ]
    with mock.patch.object(qs, "_mean", lambda vals: len(vals)):
        out.append(_call(lambda: fn(rows[:2])))
    with mock.patch.object(qs, "_checkpoint_value", lambda row, h, m: 1.0 if h == "EOD" else None):
        out.append(_call(lambda: fn(rows[:2])))
    with mock.patch.object(qs, "_bool", lambda v: False):
        out.append(_call(lambda: fn(rows[:2])))
    with mock.patch.object(qs, "_candidate_day", lambda row: "D"):
        out.append(_call(lambda: fn(rows[:2])))
    with mock.patch.object(qs, "_forward_outcome", lambda row: {"available": True}):
        out.append(_call(lambda: fn(rows[:2])))
    with mock.patch.object(qs, "Counter", lambda it: Counter(["z"])):
        out.append(_call(lambda: fn(rows[:2])))
    return out


def _a8(fn, mod):
    rows = _fw_rows()
    fake = {"a": 0, "b": 2, "c": 1, "d": 2, "e": 3}
    ret = {"a": 9.0, "b": 1.0, "c": None, "d": 1.0, "e": 5.0}

    def summ(rs):
        key = rs[0]
        return {"observed_count": fake[key], "avg_return_5m_pct": ret[key], "avg_return_3m_pct": 0.5}

    out = [
        _call(lambda: fn({})),
        _call(lambda: fn({"a": []})),
        _call(lambda: fn({"x": rows[:2], "y": rows[2:3], "z": [rows[3]]})),
        _call(lambda: fn({"x": rows[:2], "y": rows[2:3]}, limit=1)),
        _call(lambda: fn({"x": rows[:2]}, limit=0)),
        _call(lambda: fn({"x": rows[:2]}, limit=-1)),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
        _call(lambda: fn({"x": None})),
    ]
    with mock.patch.object(qs, "_forward_outcome_summary", summ):
        out.append(_call(lambda: fn({k: [k] for k in "abcde"})))
        out.append(_call(lambda: fn({k: [k] for k in "abcde"}, limit=2)))
        out.append(_call(lambda: fn({"a": ["a"]})))
    return out


CASES = {
    "a1": (_copy_cases("opening_momentum_probe_shadow"), "_opening_probe", lambda: opening_probe_owner._opening_probe, opening_probe_owner),
    "a2": (_would_enter_cases("opening_momentum_probe_would_enter", "opening_momentum_probe_shadow", "_opening_probe"), "_opening_probe_would_enter", lambda: opening_enter_owner._opening_probe_would_enter, opening_enter_owner),
    "a3": (_copy_cases("opening_largecap_surge_shadow"), "_largecap_surge_probe", lambda: largecap_probe_owner._largecap_surge_probe, largecap_probe_owner),
    "a4": (_would_enter_cases("opening_largecap_surge_would_enter", "opening_largecap_surge_shadow", "_largecap_surge_probe"), "_largecap_surge_would_enter", lambda: largecap_enter_owner._largecap_surge_would_enter, largecap_enter_owner),
    "a5": (_a5, "_entry_shape_payload", lambda: shape_payload_owner._entry_shape_payload, shape_payload_owner),
    "a6": (_a6, "_below_vwap_reclaim_observation_payload", lambda: vwap_payload_owner._below_vwap_reclaim_observation_payload, vwap_payload_owner),
    "a7": (_a7, "_forward_outcome_summary", lambda: summary_owner._forward_outcome_summary, summary_owner),
    "a8": (_a8, "_top_forward_groups", lambda: top_groups_owner._top_forward_groups, top_groups_owner),
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

    def test_a1_opening_probe(self):
        out = self._parity("a1")
        inner = {"would_probe": 1}
        res = qs._opening_probe({"opening_momentum_probe_shadow": inner})
        self.assertEqual(res, {"would_probe": 1})
        self.assertIsNot(res, inner)
        self.assertEqual(qs._opening_probe({}), {})
        self.assertEqual(out[-2], ["ok", {}])

    def test_a2_opening_probe_would_enter(self):
        out = self._parity("a2")
        self.assertIs(qs._opening_probe_would_enter({"opening_momentum_probe_would_enter": "yes"}), True)
        self.assertIs(qs._opening_probe_would_enter({"opening_momentum_probe_shadow": {"would_probe": 1}}), True)
        self.assertIs(qs._opening_probe_would_enter({}), False)
        self.assertEqual(out[3], ["ok", False])
        self.assertEqual(out[10], ["ok", True])

    def test_a3_largecap_surge_probe(self):
        out = self._parity("a3")
        inner = {"would_probe": 1}
        res = qs._largecap_surge_probe({"opening_largecap_surge_shadow": inner})
        self.assertEqual(res, {"would_probe": 1})
        self.assertIsNot(res, inner)
        self.assertEqual(qs._largecap_surge_probe({}), {})
        self.assertEqual(out[-2], ["ok", {}])

    def test_a4_largecap_surge_would_enter(self):
        out = self._parity("a4")
        self.assertIs(qs._largecap_surge_would_enter({"opening_largecap_surge_would_enter": "yes"}), True)
        self.assertIs(qs._largecap_surge_would_enter({"opening_largecap_surge_shadow": {"would_probe": 1}}), True)
        self.assertIs(qs._largecap_surge_would_enter({}), False)
        self.assertEqual(out[3], ["ok", False])

    def test_a5_entry_shape_payload(self):
        out = self._parity("a5")
        empty = qs._entry_shape_payload([])
        self.assertEqual((empty["by_shape"], empty["pullback_or_vwap_blocked_count"], empty["breakout_ready_like_count"], empty["breakout_not_ready_count"]), ([], 0, 0, 0))
        self.assertEqual(empty["behavior_effect"], "diagnostic_only")
        one = qs._entry_shape_payload([{"reason": "breakout_not_ready", "would_enter": False}])
        self.assertEqual(one["breakout_not_ready_count"], 1)
        self.assertEqual(out[7][1]["by_shape"], [{"name": "breakout", "count": 8}])

    def test_a6_below_vwap_reclaim_observation_payload(self):
        out = self._parity("a6")
        empty = qs._below_vwap_reclaim_observation_payload([])
        self.assertEqual((empty["candidate_count"], empty["by_subtype"], empty["by_subtype_v2"]), (0, [], []))
        self.assertEqual(empty["behavior_effect"], "observation_only")
        self.assertEqual(out[1][1]["candidate_count"], 3)
        self.assertEqual(out[2][1]["candidate_count"], 1)

    def test_a7_forward_outcome_summary(self):
        out = self._parity("a7")
        empty = qs._forward_outcome_summary([])
        self.assertEqual((empty["candidate_count"], empty["observed_count"], empty["coverage"]), (0, 0, 0.0))
        self.assertEqual(empty["measurement_contract_version"], "forward_horizon_coverage.v2")
        got = out[1][1]
        self.assertEqual(list(got["observed_count_by_horizon"]), ["+3m", "+5m", "+15m", "+30m", "+60m", "EOD"])
        self.assertEqual(got["observed_count_3m"], 2)
        self.assertEqual(got["observed_days"][0], "20261030")
        self.assertEqual(got["avg_return_5m_pct"], 4.0)

    def test_a8_top_forward_groups(self):
        out = self._parity("a8")
        self.assertEqual(qs._top_forward_groups({}), [])
        self.assertEqual(out[0], ["ok", []])
        self.assertEqual(out[1], ["ok", []])
        names = [g["name"] for g in out[9][1]]
        self.assertEqual(names, ["e", "b", "d", "c"])
        self.assertEqual([g["name"] for g in out[10][1]], ["e", "b"])


if __name__ == "__main__":
    unittest.main()
