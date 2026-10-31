"""P15 RF-035 (23h): eight more quant_shadow_candidate_evaluation bodies moved to projection Owners; parity with the pre-move bodies (stdlib unittest)."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import tempfile
import unittest
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from libs.reporting import quant_shadow_candidate_evaluation as qs
from libs.reporting import quant_shadow_day_paths_projection as day_paths_owner
from libs.reporting import quant_shadow_drop_q9_projection as drop_owner
from libs.reporting import quant_shadow_format_scorecard_projection as format_owner
from libs.reporting import quant_shadow_json_projection as json_owner
from libs.reporting import quant_shadow_no_trade_scorecard_projection as no_trade_owner
from libs.reporting import quant_shadow_readiness_projection as readiness_owner
from libs.reporting import quant_shadow_root_projection as root_owner
from libs.reporting import quant_shadow_text_projection as text_owner

GOLDENS = {
    "a1": "9f9c2b357362502e44a2a05c000048cefc38dd57dd520beac14a415af0f7e8b5",
    "a2": "f4c906a039b823f7c691e647179e2665efcafd604131dca87e9172184536de6e",
    "a3": "40e713ec9ce85b2a1d895f858e87e6aa5a1e3e7637d480a5ba6f6c18fdb668cd",
    "a4": "be5f3dbee6ff70f9e85a210aca21fdc2746fe31e7e7f4ed39d3cff7502a8cade",
    "a5": "7911422102c18efbab2051d4f668548868dc4fdaafcc6014e75f620f777f3b07",
    "a6": "f07fdc77ab8573ff0ea796ddcb6fb8487f3bbf70de77a4a4fe10dbc144ad2667",
    "a7": "30a562f415e9f15652f057784864bb5fc1fa0023314590b761d8d28234e0ff93",
    "a8": "f3d6bc88ec62992fd48ffc7965b3f6f577c13e87836d3af4459ff37a6f03b269",
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
        return " Weird "


def _a1(fn, mod, root):
    values = [" unknown ", " x ", None, "", 0, "-", "NONE", " Null ", "not_captured", "UNKNOWN", "None ", 1, 1.5, True, False, [], [1], {}, _Odd(), "a b"]
    return [_call(lambda v=v: fn(v)) for v in values] + [_call(lambda: fn())]


def _a2(fn, mod, root):
    root = Path(root)
    (root / "ok.json").write_text('{"x": 1}', encoding="utf-8")
    (root / "list.json").write_text("[1, 2]", encoding="utf-8")
    (root / "bad.json").write_text("{nope", encoding="utf-8")
    (root / "bin.json").write_bytes(b"\xff\xfe\x00")
    (root / "dir.json").mkdir()

    class _P:
        def read_text(self, encoding=None):
            return '{"fake": true}'

    out = [_call(lambda n=n: fn(root / n)) for n in ("ok.json", "missing.json", "list.json", "bad.json", "bin.json", "dir.json")]
    out += [_call(lambda: fn(None)), _call(lambda: fn(_P())), _call(lambda: fn())]
    with mock.patch.object(qs, "json", mock.Mock(loads=lambda text: ["patched", text])):
        out.append(_call(lambda: fn(root / "ok.json")))
    return out


def _a3(fn, mod, root):
    root = Path(root)
    day = root / "2026-10-31"
    day.mkdir()
    for name in ("b.json", "a.json", "latest.json", "c.txt"):
        (day / name).write_text("{}", encoding="utf-8")
    (day / "sub.json").mkdir()
    return [
        _call(lambda: fn(root, "2026-10-31")),
        _call(lambda: fn(root, "2026-10-31T09:00:00")),
        _call(lambda: fn(root, "2026-10-30")),
        _call(lambda: fn(root, 20261031)),
        _call(lambda: fn(root, "")),
        _call(lambda: fn(root / "nope", "2026-10-31")),
        _call(lambda: fn(str(root), "2026-10-31")),
        _call(lambda: fn(None, "d")),
        _call(lambda: fn()),
    ]


def _a4(fn, mod, root):
    payload = {"q9_decision_candidates": [{"x": 1, "y": 2}, {"x": 3}, "junk", None, {"y": 4}]}
    res = fn(payload, ["x"])
    out = [["identity", [res is payload, payload]]]
    p2 = {"q9_decision_candidates": [{"x": 1}]}
    out.append(["unchanged", [fn(p2, None) is p2, p2]])
    p3 = {"q9_decision_candidates": [{"x": 1}]}
    out.append(["empty-drop", [fn(p3, []) is p3, p3]])
    p4 = {"q9_decision_candidates": [{"x": 1, "y": 2}]}
    out.append(["multi", [fn(p4, ("x", "y", "z")) is p4, p4]])
    out.append(_call(lambda: fn({}, ["x"])))
    out.append(_call(lambda: fn({"q9_decision_candidates": None}, ["x"])))
    out.append(_call(lambda: fn({"q9_decision_candidates": "abc"}, ["x"])))
    out.append(_call(lambda: fn(None, ["x"])))
    out.append(_call(lambda: fn(None, None)))
    out.append(_call(lambda: fn({})))
    out.append(_call(lambda: fn({"q9_decision_candidates": [{"x": 1}]}, "x")))
    return out


def _a5(fn, mod, root):
    full = {"name": "x", "observed_count": 2, "candidate_count": 3, "avg_return_5m_pct": 1.0, "avg_return_15m_pct": 2, "avg_mfe_5m_pct": 3, "avg_mae_5m_pct": -4, "review_state": "promotion_watch"}
    out = [
        _call(lambda: fn([])),
        _call(lambda: fn([{"name": "x", "observed_count": 2, "candidate_count": 3, "avg_return_5m_pct": 1.0}])),
        _call(lambda: fn([full])),
        _call(lambda: fn([{"name": "x"}])),
        _call(lambda: fn([{"name": "x", "avg_return_5m_pct": "bad"}])),
        _call(lambda: fn([{"name": "x", "avg_return_5m_pct": 1, "avg_mfe_5m_pct": "bad"}])),
        _call(lambda: fn([{"name": "x", "observed_count": "bad"}])),
        _call(lambda: fn([{"name": ""}, {"name": "none"}, dict(full, name="y"), dict(full, name="z")], limit=2)),
        _call(lambda: fn([full], limit=0)),
        _call(lambda: fn(None)),
        _call(lambda: fn([None])),
        _call(lambda: fn()),
    ]
    with mock.patch.object(qs, "_text", lambda v: "T" if v else ""):
        out.append(_call(lambda: fn([full])))
    return out


def _a6(fn, mod, root):
    ok = {"candidate": "probe", "confidence": "high", "recommended_action": "promote", "promotion_scope": "scope"}
    many = [{"evaluated": True}] * 40 + [{"evaluated": False}] * 10
    out = [
        _call(lambda: fn([], {})),
        _call(lambda: fn(many, ok)),
        _call(lambda: fn(many, dict(ok, candidate="hold"))),
        _call(lambda: fn(many, dict(ok, confidence="low"))),
        _call(lambda: fn(many[:5], ok)),
        _call(lambda: fn([{"evaluated": True}], ok)),
        _call(lambda: fn([{"evaluated": False}] * 40, ok)),
        _call(lambda: fn(many, {})),
        _call(lambda: fn(many, MappingProxyType(ok))),
        _call(lambda: fn(iter(many), ok)),
        _call(lambda: fn(None, ok)),
        _call(lambda: fn(many, None)),
        _call(lambda: fn([])),
    ]
    with mock.patch.object(qs, "TRUSTED_FORWARD_MIN_COUNT", 1), mock.patch.object(qs, "PROMOTION_CANDIDATE_MIN_OBSERVED", 1), mock.patch.object(qs, "TRUSTED_FORWARD_MIN_COVERAGE", 0.0):
        out.append(_call(lambda: fn([{"evaluated": 1}], ok)))
    with mock.patch.object(qs, "_bool", lambda v: True):
        out.append(_call(lambda: fn(many, ok)))
    with mock.patch.object(qs, "_text", lambda v: "high" if v else ""):
        out.append(_call(lambda: fn(many, ok)))
    real_ready = [{"evaluated": True}] * 80 + [{"evaluated": False}] * 20
    real_coverage = [{"evaluated": True}] * 55 + [{"evaluated": False}] * 45
    real_weak = [{"evaluated": True}] * 90 + [{"evaluated": False}] * 30
    out.append(_call(lambda: fn(real_ready, ok)))
    out.append(_call(lambda: fn(real_coverage, ok)))
    out.append(_call(lambda: fn(real_weak, dict(ok, candidate="hold"))))
    return out


def _a7(fn, mod, root):
    out = [
        _call(lambda: fn(Path("/tmp/fake/reports"))),
        _call(lambda: fn("/tmp/fake/reports")),
        _call(lambda: fn("relative/reports")),
        _call(lambda: fn(Path("/"))),
        _call(lambda: fn("")),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    with mock.patch.object(qs, "Path", lambda *a: Path("/patched") / "x"):
        out.append(_call(lambda: fn("/tmp/fake/reports")))
    return out


def _nt_rows(name, observed=10, **kw):
    return dict({"name": name, "observed_count": observed, "candidate_count": 20, "observed_day_count": 3, "avg_return_5m_pct": 0.3, "avg_return_15m_pct": 0.2}, **kw)


def _a8(fn, mod, root):
    def run(**kw):
        base = dict(candidates=[], entry_lane_forward_outcomes={}, would_enter_count=0, opening_probe_would_enter=0, largecap_probe_would_enter=0)
        base.update(kw)
        return _call(lambda: fn(**base))

    cands = [{"shadow_forward_outcome": {"available": True}}] * 3 + [{}]
    lanes = {"by_primary_lane": [_nt_rows("trend", avg_return_5m_pct=0.5)], "by_lane_subtype": [_nt_rows("pullback_quality:failed_pullback", observed=25, observed_day_count=3, avg_return_5m_pct=0.4, avg_return_15m_pct=0.3), _nt_rows("weak", avg_return_5m_pct=-0.5)]}
    blocked_only = {"by_primary_lane": [_nt_rows("weak", avg_return_5m_pct=-0.5)]}
    missed_only = {"by_primary_lane": [_nt_rows("trend", avg_return_5m_pct=0.5)]}
    out = [
        run(),
        run(candidates=cands),
        run(candidates=cands, would_enter_count=1),
        run(candidates=cands, opening_probe_would_enter=2),
        run(candidates=cands, largecap_probe_would_enter=3),
        run(candidates=cands, entry_lane_forward_outcomes=lanes),
        run(candidates=cands, entry_lane_forward_outcomes=missed_only),
        run(candidates=cands, entry_lane_forward_outcomes=blocked_only),
        run(candidates=cands, entry_lane_forward_outcomes=MappingProxyType(lanes)),
        run(candidates=cands, entry_lane_forward_outcomes=[1]),
        run(candidates=[{"shadow_forward_outcome": {"available": True}}] * 40, entry_lane_forward_outcomes=lanes),
        run(candidates=None),
        run(would_enter_count="x"),
        _call(lambda: fn()),
    ]
    with mock.patch.object(qs, "_scorecard_rows", lambda rows, mode, limit: [{"mode": mode, "limit": limit}] if mode == "missed" else []):
        out.append(run(candidates=cands, entry_lane_forward_outcomes=lanes))
    with mock.patch.object(qs, "_named_forward_rows", lambda rows, names: [{"review_state": "promotion_watch", "names": sorted(names)}]):
        out.append(run(candidates=cands, entry_lane_forward_outcomes=lanes))
    with mock.patch.object(qs, "_bool", lambda v: False):
        out.append(run(candidates=cands))
    with mock.patch.object(qs, "TRUSTED_FORWARD_MIN_COUNT", 1), mock.patch.object(qs, "TRUSTED_FORWARD_MIN_COVERAGE", 0.1):
        out.append(run(candidates=cands))
    with mock.patch.object(qs, "_forward_outcome", lambda row: {"available": False}):
        out.append(run(candidates=cands))
    with mock.patch.object(qs, "Mapping", tuple):
        out.append(run(candidates=cands, entry_lane_forward_outcomes=lanes))
    return out


CASES = {
    "a1": (_a1, "_text", lambda: text_owner._text, False, text_owner),
    "a2": (_a2, "_read_json", lambda: json_owner._read_json, True, json_owner),
    "a3": (_a3, "_json_paths_for_day", lambda: day_paths_owner._json_paths_for_day, False, day_paths_owner),
    "a4": (_a4, "_drop_q9_row_keys", lambda: drop_owner._drop_q9_row_keys, False, drop_owner),
    "a5": (_a5, "_format_scorecard_rows", lambda: format_owner._format_scorecard_rows, True, format_owner),
    "a6": (_a6, "_shadow_readiness", lambda: readiness_owner._shadow_readiness, True, readiness_owner),
    "a7": (_a7, "shadow_candidate_root_for_reports", lambda: root_owner.shadow_candidate_root_for_reports, True, root_owner),
    "a8": (_a8, "_no_trade_scorecard", lambda: no_trade_owner._no_trade_scorecard, True, no_trade_owner),
}


def _run(key, which):
    scenario, name, owner_factory, facade, _ = CASES[key]
    if which == "wrapper":
        fn = getattr(qs, name)
    else:
        raw = owner_factory()
        fn = (lambda *a, **k: raw(*a, facade=qs, **k)) if facade else raw
    with tempfile.TemporaryDirectory() as t:
        out = scenario(fn, qs, t)
        return json.loads(json.dumps(out, default=repr).replace(t, "<T>").replace(str(Path(t).resolve()), "<T>"))


class Test(unittest.TestCase):
    def _parity(self, key):
        a = _run(key, "wrapper")
        b = _run(key, "owner")
        self.assertEqual(a, b)
        self.assertEqual(_h(a), GOLDENS[key])
        name, owner_mod = CASES[key][1], CASES[key][4]
        fn = ast.parse(inspect.getsource(getattr(qs, name))).body[0]
        stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
        self.assertTrue(len(stmts) == 1 and isinstance(stmts[0], ast.Return))
        self.assertNotIn("import quant_shadow_candidate_evaluation", inspect.getsource(owner_mod))
        return a

    def test_a1_text(self):
        out = self._parity("a1")
        self.assertEqual(qs._text(" unknown "), "")
        self.assertEqual(qs._text(" x "), "x")
        self.assertEqual(out[-1][0], "exc")

    def test_a2_read_json(self):
        out = self._parity("a2")
        self.assertEqual(out[0], ["ok", {"x": 1}])
        self.assertEqual(out[1], ["ok", None])
        self.assertEqual(out[-1], ["ok", ["patched", '{"x": 1}']])

    def test_a3_json_paths_for_day(self):
        out = self._parity("a3")
        self.assertEqual([p.rsplit("/", 1)[-1] for p in [x.split("'")[1] for x in out[0][1]]], ["a.json", "b.json", "sub.json"])
        self.assertEqual(out[2], ["ok", []])

    def test_a4_drop_q9_row_keys(self):
        out = self._parity("a4")
        self.assertEqual(out[0], ["identity", [True, {"q9_decision_candidates": [{"y": 2}, {}, "junk", None, {"y": 4}]}]])
        self.assertEqual(out[1], ["unchanged", [True, {"q9_decision_candidates": [{"x": 1}]}]])

    def test_a5_format_scorecard_rows(self):
        out = self._parity("a5")
        self.assertEqual(qs._format_scorecard_rows([]), "none")
        self.assertEqual(out[1], ["ok", "x (2/3, +5m 1.0000%)"])
        self.assertEqual(out[4][0], "exc")

    def test_a6_shadow_readiness(self):
        out = self._parity("a6")
        empty = qs._shadow_readiness([], {})
        self.assertEqual((empty["status"], empty["action"], empty["evaluated_ratio"]), ("hold_no_shadow_candidates", "hold", 0.0))
        self.assertEqual(out[1][1]["status"], "hold_shadow_sample_insufficient")
        self.assertEqual(out[-3][1]["status"], "ready")
        self.assertEqual(out[-3][1]["action"], "promote")
        self.assertEqual(out[-2][1]["status"], "hold_shadow_coverage_insufficient")
        self.assertEqual(out[-1][1]["status"], "review_shadow_signal_weak")

    def test_a7_shadow_candidate_root_for_reports(self):
        out = self._parity("a7")
        self.assertEqual(qs.shadow_candidate_root_for_reports(Path("/tmp/fake/reports")), Path("/tmp/fake/data/logs/quant_shadow_candidates"))
        self.assertEqual(out[0], ["ok", "PosixPath('/tmp/fake/data/logs/quant_shadow_candidates')"])
        self.assertEqual(out[-1], ["ok", "PosixPath('/patched/data/logs/quant_shadow_candidates')"])

    def test_a8_no_trade_scorecard(self):
        out = self._parity("a8")
        got = qs._no_trade_scorecard(candidates=[], entry_lane_forward_outcomes={}, would_enter_count=0, opening_probe_would_enter=0, largecap_probe_would_enter=0)
        self.assertEqual((got["status"], got["candidate_count"], got["behavior_effect"], got["forward_outcome_coverage"]), ("no_shadow_data", 0, "evaluation_only", 0.0))
        self.assertEqual(out[2][1]["status"], "trade_candidates_available")
        self.assertEqual(out[13][0], "exc")


if __name__ == "__main__":
    unittest.main()
