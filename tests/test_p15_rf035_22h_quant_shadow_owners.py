"""P15 RF-035 (22h): eight more quant_shadow_candidate_evaluation bodies moved to projection Owners; parity with the pre-move bodies (stdlib unittest)."""
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
from libs.reporting import quant_shadow_entry_lane_forward_projection as lane_forward_owner
from libs.reporting import quant_shadow_entry_lane_observation_projection as lane_obs_owner
from libs.reporting import quant_shadow_entry_lane_payload_projection as lane_payload_owner
from libs.reporting import quant_shadow_format_forward_projection as format_forward_owner
from libs.reporting import quant_shadow_format_rows_projection as format_rows_owner
from libs.reporting import quant_shadow_named_forward_rows_projection as named_rows_owner
from libs.reporting import quant_shadow_scorecard_rows_projection as scorecard_owner
from libs.reporting import quant_shadow_vwap_observation_projection as vwap_owner

GOLDENS = {
    "a1": "daa95d222801a2a10d52e32c1f2fa4df6b1819d3d65920589835f17816812091",
    "a2": "d520f3d3639995dedcf8ced0edcd0fae9127fb0cbce733bafbe91046ff733a22",
    "a3": "42cc9a97a35a34ca69caead1675a7cd669023b839edcad8266a9e77a35839ae2",
    "a4": "8fa0010140f5dc1b0106db5d9c00ce3f83b5b003ef68470729e6f0b2f2c1d6a6",
    "a5": "4f178838e92d1d3c6e755e6985e2aabc720ff90fba0e86752a542a85deb3a59f",
    "a6": "91e4c9faf4cef99576b8a4a99db7db7eba6cb111595477c596f1e3803bfdd26a",
    "a7": "b512142918e09de1a9f207f4a065eaf373bb868a80ac33f27d9231ca3131f1be",
    "a8": "86ddee41c27e2fcc475e6575bf32571a61712132abe2311bd51e0acabdadbdad",
}


def _call(fn):
    try:
        return ["ok", fn()]
    except BaseException as exc:  # noqa: BLE001 - parity of exception type/message is the point
        return ["exc", type(exc).__name__, str(exc)]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, default=repr).encode()).hexdigest()


def _observation_cases(payload_key, classifier_name):
    def scenario(fn, mod):
        inner = {"flag": 1}
        res = fn({payload_key: inner})
        out = [
            ["copy", [res == inner, res is not inner]],
            _call(lambda: fn({payload_key: MappingProxyType({"m": 1})})),
            _call(lambda: fn({payload_key: {}})),
        ]
        with mock.patch.object(qs, classifier_name, lambda row: {"fallback": True, "keys": sorted(row)}):
            out.append(_call(lambda: fn({})))
            out.append(_call(lambda: fn({payload_key: [1]})))
            out.append(_call(lambda: fn({payload_key: None, "x": 1})))
            out.append(_call(lambda: fn(None)))
            out.append(_call(lambda: fn()))
        with mock.patch.object(qs, classifier_name, lambda row: (_ for _ in ()).throw(RuntimeError("boom"))):
            out.append(_call(lambda: fn({})))
        with mock.patch.object(qs, "Mapping", tuple):
            with mock.patch.object(qs, classifier_name, lambda row: {"fb": 1}):
                out.append(_call(lambda: fn({payload_key: {"a": 1}})))
        return out

    return scenario


def _lane_obs(row):
    return {
        "primary_lane": row.get("lane"), "subtype": row.get("sub"), "subtype_v2": row.get("sub2"),
        "time_bucket": row.get("tb"), "market_regime": row.get("mr"), "market_regime_rail": row.get("rail"),
    }


_LANE_ROWS = [
    {"lane": "trend", "sub": "A", "sub2": "A2", "tb": "open", "mr": "bull", "rail": "g"},
    {"lane": "trend", "sub": "A", "tb": "open"},
    {"lane": "range", "sub": "B", "sub2": "B2", "mr": "bear", "rail": "r"},
    {},
    {"lane": "none", "sub": "Unknown"},
]


def _a3(fn, mod):
    out = [_call(lambda: fn([]))]
    with mock.patch.object(qs, "_entry_lane_observation", _lane_obs):
        out.append(_call(lambda: fn([{"lane": "trend", "sub": "A"}])))
        out.append(_call(lambda: fn(_LANE_ROWS)))
        out.append(_call(lambda: fn(iter(_LANE_ROWS[:2]))))
    out.append(_call(lambda: fn([{"entry_lane_observation": {"primary_lane": "real", "subtype": "S"}}])))
    out.append(_call(lambda: fn(None)))
    out.append(_call(lambda: fn()))
    with mock.patch.object(qs, "_entry_lane_observation", _lane_obs):
        with mock.patch.object(qs, "_top_counter", lambda c, limit=0: [{"limit": limit, "n": sum(c.values())}]):
            out.append(_call(lambda: fn(_LANE_ROWS)))
        with mock.patch.object(qs, "_text", lambda v: "T" if v else ""):
            out.append(_call(lambda: fn(_LANE_ROWS)))
        with mock.patch.object(qs, "Counter", lambda: Counter({"zz": 1})):
            out.append(_call(lambda: fn(_LANE_ROWS[:1])))
    return out


def _a4(fn, mod):
    out = [_call(lambda: fn([]))]
    with mock.patch.object(qs, "_entry_lane_observation", _lane_obs):
        out.append(_call(lambda: fn([{"lane": "trend"}])))
        with mock.patch.object(qs, "_top_forward_groups", lambda groups, limit=0: [{"limit": limit, "groups": {k: len(v) for k, v in groups.items()}}]):
            out.append(_call(lambda: fn(_LANE_ROWS)))
        with mock.patch.object(qs, "_text", lambda v: "T" if v else ""):
            with mock.patch.object(qs, "_top_forward_groups", lambda groups, limit=0: [sorted(groups)]):
                out.append(_call(lambda: fn(_LANE_ROWS)))
    out.append(_call(lambda: fn(None)))
    out.append(_call(lambda: fn()))
    out.append(_call(lambda: fn([None])))
    return out


def _sc(name, observed=10, **kw):
    return dict({"name": name, "observed_count": observed, "candidate_count": 12, "observed_day_count": 3, "sample_concentration": 0.5,
                 "avg_return_5m_pct": 0.3, "avg_return_15m_pct": 0.2}, **kw)


def _a5(fn, mod):
    rows = [_sc("a", avg_mfe_5m_pct=0.5, avg_mae_5m_pct=-0.1), _sc("b", avg_return_5m_pct=-0.2, avg_mae_5m_pct="-0.9"), _sc("c", observed=9),
            _sc("d", avg_return_5m_pct=0.0, avg_mfe_5m_pct="bad", avg_mae_5m_pct="bad"), _sc("e", avg_mae_5m_pct=-2.0), _sc("f", avg_return_5m_pct=-0.5)]
    out = [_call(lambda: fn([], mode="missed"))]
    for mode in ("missed", "blocked", "unknown"):
        out.append(_call(lambda m=mode: fn(rows, mode=m)))
        out.append(_call(lambda m=mode: fn(rows, mode=m, limit=1)))
    out.append(_call(lambda: fn(rows)))
    out.append(_call(lambda: fn(None, mode="missed")))
    out.append(_call(lambda: fn([None], mode="missed")))
    with mock.patch.object(qs, "_scorecard_return_signal", lambda row: 0.5):
        out.append(_call(lambda: fn([_sc("x", observed=10)], mode="missed")))
    with mock.patch.object(qs, "_scorecard_return_signal", lambda row: None):
        out.append(_call(lambda: fn(rows, mode="missed")))
    with mock.patch.object(qs, "_text", lambda v: "T"):
        out.append(_call(lambda: fn(rows[:1], mode="missed")))
    return out


def _a6(fn, mod):
    r = lambda name, **kw: dict({"name": name, "observed_count": 25, "observed_day_count": 3, "candidate_count": 30, "avg_return_5m_pct": 0.1, "avg_return_15m_pct": 0.1}, **kw)  # noqa: E731
    rows = [r("a"), r("b", observed_count=0), r("c", observed_day_count=1), r("d", avg_return_15m_pct=-0.1), r("e", avg_return_5m_pct=-1), r("f", observed_count=21),
            r("g", avg_return_5m_pct="bad", avg_return_15m_pct=""), r("h", observed_count="x")]
    out = [
        _call(lambda: fn([], set())),
        _call(lambda: fn(rows, {"a", "b", "c", "d", "e", "f", "g", "zz"})),
        _call(lambda: fn(rows, {"x"})),
        _call(lambda: fn(rows, {"h"})),
        _call(lambda: fn([{"observed_count": 0, "name": "x"}], {"x"})),
        _call(lambda: fn(rows, set())),
        _call(lambda: fn(None, {"a"})),
        _call(lambda: fn(rows)),
        _call(lambda: fn([None], {"a"})),
    ]
    with mock.patch.object(qs, "PROMOTION_CANDIDATE_MIN_OBSERVED", 30):
        out.append(_call(lambda: fn(rows, {"a", "f"})))
    with mock.patch.object(qs, "Mapping", tuple):
        out.append(_call(lambda: fn(rows, {"a"})))
    return out


def _a7(fn, mod):
    out = [
        _call(lambda: fn([{"name": "x", "count": 2}])),
        _call(lambda: fn([])),
        _call(lambda: fn([{"name": "x", "count": 2}], limit=0)),
        _call(lambda: fn([{"name": ""}, {"name": "none"}, {"name": "y"}])),
        _call(lambda: fn([{"name": "a", "count": 1}, {"name": "b"}, {"name": "c", "count": 3}], limit=2)),
        _call(lambda: fn([{"name": "a", "count": 1}] * 6)),
        _call(lambda: fn([{"name": "a"}], limit=-1)),
        _call(lambda: fn(None)),
        _call(lambda: fn([None])),
        _call(lambda: fn()),
        _call(lambda: fn(iter([{"name": "z", "count": 9}]))),
    ]
    with mock.patch.object(qs, "_text", lambda v: "T" if v else ""):
        out.append(_call(lambda: fn([{"name": "x", "count": 2}])))
    return out


def _a8(fn, mod):
    out = [
        _call(lambda: fn([{"name": "x", "observed_count": 2, "candidate_count": 3, "avg_return_5m_pct": 1.25}])),
        _call(lambda: fn([])),
        _call(lambda: fn([{"name": "x", "observed_count": 2, "candidate_count": 3}])),
        _call(lambda: fn([{"name": "x", "avg_return_5m_pct": 1, "avg_return_15m_pct": 2, "avg_mfe_5m_pct": 3, "avg_mae_5m_pct": -4}])),
        _call(lambda: fn([{"name": "x", "avg_return_5m_pct": "bad"}])),
        _call(lambda: fn([{"name": "x", "avg_return_15m_pct": "bad", "avg_return_5m_pct": 1}])),
        _call(lambda: fn([{"name": "x", "observed_count": "bad"}])),
        _call(lambda: fn([{"name": ""}, {"name": "y", "avg_return_5m_pct": 0.5}, {"name": "z"}], limit=2)),
        _call(lambda: fn([{"name": "y", "avg_return_5m_pct": 0.5}], limit=0)),
        _call(lambda: fn(None)),
        _call(lambda: fn([None])),
        _call(lambda: fn()),
        _call(lambda: fn([{"name": "x", "avg_return_5m_pct": 1, "avg_mfe_5m_pct": None, "avg_mae_5m_pct": 0}])),
    ]
    with mock.patch.object(qs, "_text", lambda v: "T" if v else ""):
        out.append(_call(lambda: fn([{"name": "x", "avg_return_5m_pct": 1}])))
    return out


CASES = {
    "a1": (_observation_cases("below_vwap_reclaim_observation", "classify_below_vwap_reclaim_observation"), "_below_vwap_reclaim_observation", lambda: vwap_owner._below_vwap_reclaim_observation, vwap_owner),
    "a2": (_observation_cases("entry_lane_observation", "build_entry_lane_observation"), "_entry_lane_observation", lambda: lane_obs_owner._entry_lane_observation, lane_obs_owner),
    "a3": (_a3, "_entry_lane_observation_payload", lambda: lane_payload_owner._entry_lane_observation_payload, lane_payload_owner),
    "a4": (_a4, "_entry_lane_forward_outcomes", lambda: lane_forward_owner._entry_lane_forward_outcomes, lane_forward_owner),
    "a5": (_a5, "_scorecard_rows", lambda: scorecard_owner._scorecard_rows, scorecard_owner),
    "a6": (_a6, "_named_forward_rows", lambda: named_rows_owner._named_forward_rows, named_rows_owner),
    "a7": (_a7, "_format_rows", lambda: format_rows_owner._format_rows, format_rows_owner),
    "a8": (_a8, "_format_forward_rows", lambda: format_forward_owner._format_forward_rows, format_forward_owner),
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

    def test_a1_below_vwap_reclaim_observation(self):
        out = self._parity("a1")
        inner = {"flag": 1}
        res = qs._below_vwap_reclaim_observation({"below_vwap_reclaim_observation": inner})
        self.assertEqual(res, {"flag": 1})
        self.assertIsNot(res, inner)
        with mock.patch.object(qs, "classify_below_vwap_reclaim_observation", lambda row: {"fallback": True}):
            self.assertEqual(qs._below_vwap_reclaim_observation({}), {"fallback": True})
        self.assertEqual(out[3], ["ok", {"fallback": True, "keys": []}])

    def test_a2_entry_lane_observation(self):
        out = self._parity("a2")
        inner = {"primary_lane": "trend"}
        res = qs._entry_lane_observation({"entry_lane_observation": inner})
        self.assertEqual(res, {"primary_lane": "trend"})
        self.assertIsNot(res, inner)
        with mock.patch.object(qs, "build_entry_lane_observation", lambda row: {"primary_lane": "fallback"}):
            self.assertEqual(qs._entry_lane_observation({}), {"primary_lane": "fallback"})
        self.assertEqual(out[-2][0], "exc")

    def test_a3_entry_lane_observation_payload(self):
        out = self._parity("a3")
        empty = out[0][1]
        self.assertEqual(empty["behavior_effect"], "observation_only")
        self.assertEqual(empty["candidate_count"], 0)
        self.assertTrue(all(v == [] for k, v in empty.items() if k.startswith("by_")))
        self.assertEqual(len([k for k in empty if k.startswith("by_")]), 8)
        self.assertEqual(out[1][1]["candidate_count"], 1)
        self.assertEqual(out[1][1]["by_primary_lane"], [{"name": "trend", "count": 1}])

    def test_a4_entry_lane_forward_outcomes(self):
        out = self._parity("a4")
        empty = out[0][1]
        self.assertEqual(empty["behavior_effect"], "evaluation_only")
        self.assertEqual(list(empty), ["behavior_effect", "by_primary_lane", "by_subtype", "by_subtype_v2", "by_lane_subtype", "by_lane_subtype_v2", "by_time_bucket", "by_market_regime_rail"])
        self.assertTrue(all(v == [] for k, v in empty.items() if k != "behavior_effect"))

    def test_a5_scorecard_rows(self):
        out = self._parity("a5")
        self.assertEqual(qs._scorecard_rows([], mode="missed"), [])
        self.assertEqual(qs._scorecard_rows([_sc("x", observed=9)], mode="missed"), [])
        self.assertEqual(qs._scorecard_rows([_sc("x")], mode="unknown"), [])
        self.assertEqual(out[-3][1][0]["scorecard_signal_pct"], 0.5)
        self.assertEqual(out[-2], ["ok", []])

    def test_a6_named_forward_rows(self):
        out = self._parity("a6")
        self.assertEqual(qs._named_forward_rows([], set()), [])
        got = qs._named_forward_rows([{"name": "x", "observed_count": 0}], {"x"})
        self.assertEqual([g["review_state"] for g in got], ["sample_insufficient"])
        got = qs._named_forward_rows([{"name": "b", "observed_count": 25, "observed_day_count": 3}, {"name": "a", "observed_count": 25, "observed_day_count": 3}], {"b", "a", "zz"})
        self.assertEqual([g["name"] for g in got], ["a", "b"])
        self.assertEqual([g["name"] for g in out[1][1]], sorted(g["name"] for g in out[1][1]))

    def test_a7_format_rows(self):
        out = self._parity("a7")
        self.assertEqual(qs._format_rows([{"name": "x", "count": 2}]), "x (2)")
        self.assertEqual(qs._format_rows([]), "none")
        self.assertEqual(qs._format_rows([{"name": "x", "count": 2}], limit=0), "none")
        self.assertEqual(out[-1], ["ok", "T (2)"])

    def test_a8_format_forward_rows(self):
        out = self._parity("a8")
        self.assertEqual(qs._format_forward_rows([{"name": "x", "observed_count": 2, "candidate_count": 3, "avg_return_5m_pct": 1.25}]), "x (2/3, +5m 1.2500%)")
        self.assertEqual(qs._format_forward_rows([]), "none")
        self.assertEqual(out[4][0], "exc")
        self.assertEqual(out[6][0], "exc")


if __name__ == "__main__":
    unittest.main()
