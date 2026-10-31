"""P15 RF-035 (20261101-00h): eight larger quant_shadow_candidate_evaluation bodies moved to projection Owners; parity with the pre-move bodies (stdlib unittest)."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import tempfile
import types
import unittest
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from libs.reporting import quant_shadow_candidate_evaluation as qs
from libs.reporting import quant_shadow_evaluation_builder_projection as builder_owner
from libs.reporting import quant_shadow_guard_observation_projection as guard_owner
from libs.reporting import quant_shadow_payload_iterator_projection as iterator_owner
from libs.reporting import quant_shadow_promotion_projection as promotion_owner
from libs.reporting import quant_shadow_q9_augment_projection as augment_owner
from libs.reporting import quant_shadow_q9_windows_projection as windows_owner
from libs.reporting import quant_shadow_render_lines_projection as render_owner
from libs.reporting import quant_shadow_trust_gate_projection as trust_owner

GOLDENS = {
    "a1": "672794f0c3474b5720667c5335f33625c1e4dafc2b1c30ad2a477287eecd527a",
    "a2": "c72a51e77547b9c1d5a081f90ba96f6d8eb07bf08357e5b6bbf83878012440a6",
    "a3": "627abe34e74e78fdb60b16964bef2e2491a736fbf090625ad32e16786e168917",
    "a4": "daf1781a1d805b6e2cbb4266fce936b3af52cd8cc81094cb8e7c4e49d1562c80",
    "a5": "6c5c69d99acdf9d5c8c73c66e52316d7d85c9467b64fcd280c069ee829382ec8",
    "a6": "f27e9bc3ed599b34685464aad49a06ce021a47534b38813e8d7ecc1a0f34ac56",
    "a7": "b043ed0d4b57b4cbbc72051f95593ed3a881aca93889fac4c714eb34ac5f8c85",
    "a8": "1e72fe8eb8c6641e4fc9b361aa7e1a2dd7dc5e047b2255c0d841ae667b4ca51e",
}


def _call(fn):
    try:
        return ["ok", fn()]
    except BaseException as exc:  # noqa: BLE001 - parity of exception type/message is the point
        return ["exc", type(exc).__name__, str(exc)]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, default=repr).encode()).hexdigest()


def _w(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def _lane_fake(row):
    return {"primary_lane": row.get("lane") or "trend", "subtype": row.get("sub") or "A", "subtype_v2": row.get("sub") or "A2", "time_bucket": "open", "market_regime": "bull", "market_regime_rail": "g"}


def _vwap_fake(row):
    return {"applies": bool(row.get("vwap")), "subtype": "s1", "subtype_v2": "v1"}


def _live_fakes():
    """Pure fakes for runtime observation classifiers/enforcement and forward attachment (no live calls)."""
    return (
        mock.patch.object(qs, "build_entry_lane_observation", _lane_fake),
        mock.patch.object(qs, "classify_below_vwap_reclaim_observation", _vwap_fake),
        mock.patch.object(qs, "build_entry_quant_enforcement", lambda payload: {"blocked": False}),
        mock.patch.object(qs, "attach_forward_outcomes", lambda rows, **k: list(rows)),
    )


class _Fakes:
    def __enter__(self):
        self.ms = _live_fakes()
        for m in self.ms:
            m.start()
        return self

    def __exit__(self, *exc):
        for m in reversed(self.ms):
            m.stop()


def _cp(ret5, mfe=0.5, mae=-0.1):
    return {"+3m": {"status": "observed", "return_pct": ret5, "mfe_pct": mfe}, "+5m": {"status": "observed", "return_pct": ret5, "mfe_pct": mfe, "mae_pct": mae}, "+15m": {"status": "observed", "return_pct": ret5}}


def _cands(n=12):
    rows = []
    for i in range(n):
        rows.append({
            "symbol": "AB"[i % 2] + str(i % 3), "reason": "cost_edge_fail" if i % 3 == 0 else "breakout_not_ready", "shadow_role": "runner_up_evaluated" if i % 4 == 0 else "selected",
            "would_enter": i % 5 == 0, "evaluated": True, "guard_blocked": i % 2 == 0, "primary_failure_axis": "confirmed_entry" if i % 4 == 0 else "pullback_structure",
            "lane": "trend" if i % 2 else "range", "sub": "A" if i % 3 else "B", "vwap": i % 2 == 0,
            "opening_momentum_probe_shadow": {"would_probe": i % 3 == 0, "reason": "r1"} if i % 2 else {},
            "opening_largecap_surge_shadow": {"would_probe": 1, "reason": "r2"} if i % 5 == 0 else {},
            "shadow_forward_base": {"available": True, "baseline_raw_ts": "20261031090000"},
            "shadow_forward_outcome": {"available": True, "checkpoints": _cp(0.3 + i / 100.0)},
            "candidate_id": f"c{i}", "entry_quant_decision": {"decision": "entry_ready", "tactic_id": "T", "blockers": ["b"] if i % 3 else []},
        })
    return rows


def _a1(fn, mod, root):
    root = Path(root)
    out = []
    with mock.patch.object(qs, "iter_json_array", lambda path, key, strict=False: iter([{"decision_id": "d1", "commander_final": {"decision": "hold"}}, {"decision_id": ""}, "junk", {"decision_id": 5, "commander_final": None}, {"nodid": 1}])):
        out.append(_call(lambda: fn(root, "2026-10-31")))
        out.append(_call(lambda: fn(str(root), "2026-10-31T10:00")))
    def raise_os(path, key, strict=False):
        raise OSError("nope")
    def raise_val(path, key, strict=False):
        raise ValueError("bad")
    def raise_rt(path, key, strict=False):
        raise RuntimeError("other")
    for exc in (raise_os, raise_val, raise_rt):
        with mock.patch.object(qs, "iter_json_array", exc):
            out.append(_call(lambda: fn(root, "2026-10-31")))
    seen = []
    with mock.patch.object(qs, "iter_json_array", lambda path, key, strict=False: seen.append([str(path).replace(str(root), "<R>"), key, strict]) or iter([])):
        out.append(_call(lambda: fn(root, "2026-10-31T10:00")))
    out.append(["path-args", seen])
    _w(root / "operator_summary" / "daily" / "2026-10-31" / "q9_decision_windows.json", {"windows": [{"decision_id": "z", "commander_final": {"selected_symbol": "A"}}]})
    out.append(_call(lambda: fn(root, "2026-10-31")))
    out.append(_call(lambda: fn(root, "2026-10-30")))
    out.append(_call(lambda: fn(None, "2026-10-31")))
    out.append(_call(lambda: fn()))
    with mock.patch.object(qs, "Mapping", tuple), mock.patch.object(qs, "iter_json_array", lambda path, key, strict=False: iter([{"decision_id": "d1"}])):
        out.append(_call(lambda: fn(root, "d")))
    return out


def _q9_rows():
    return [
        {"symbol": "A", "q9_decision_role": "B_STRATEGIST_RANKED", "rank": 3},
        {"symbol": "B", "q9_decision_role": "A_SCANNER_CONTROL"},
        "junk",
        {"symbol": "C", "q9_decision_role": "OTHER"},
    ]


def _a2(fn, mod, root):
    def payload(**kw):
        return dict({"q9_decision_id": "d1", "q9_decision_candidates": _q9_rows()}, **kw)

    win = {"d1": {"commander_final": {"selected_symbol": "A", "decision": "enter", "no_trade": 1}}}
    out = []
    p = payload()
    res = fn(p, windows_by_id=win)
    out.append(["added", [res is p, res["q9_decision_candidates"]]])
    p2 = payload(q9_decision_candidates=_q9_rows() + [{"q9_decision_role": "C_COMMANDER_FINAL"}])
    out.append(["existing", [fn(p2, windows_by_id=win) is p2, p2]])
    for label, windows in (
        ("no-window", {}),
        ("window-not-mapping", {"d1": [1]}),
        ("empty-commander", {"d1": {"commander_final": {}}}),
        ("bad-commander", {"d1": {"commander_final": "x"}}),
        ("candidate-symbol", {"d1": {"commander_final": {"candidate_symbol": "B"}}}),
        ("no-source", {"d1": {"commander_final": {"selected_symbol": "C"}}}),
        ("unknown-symbol", {"d1": {"commander_final": {"selected_symbol": "Z"}}}),
        ("mapping-proxy", MappingProxyType({"d1": MappingProxyType({"commander_final": MappingProxyType({"selected_symbol": "A"})})})),
    ):
        pp = payload()
        out.append([label, _call(lambda: fn(pp, windows_by_id=windows)), pp["q9_decision_candidates"] if isinstance(pp.get("q9_decision_candidates"), list) else None])
    out.append(_call(lambda: fn({}, windows_by_id=win)))
    out.append(_call(lambda: fn({"q9_decision_id": " d1 ", "q9_decision_candidates": None}, windows_by_id=win)))
    out.append(_call(lambda: fn(payload(), windows_by_id=None)))
    out.append(_call(lambda: fn(None, windows_by_id=win)))
    out.append(_call(lambda: fn(payload())))
    with mock.patch.object(qs, "Mapping", tuple):
        out.append(_call(lambda: fn(payload(), windows_by_id=win)))
    return out


def _a3(fn, mod, root):
    ready = {"promotion_watchlist": [{"review_state": "promotion_watch", "name": "x"}, {"review_state": "other"}, "junk"]}
    kw = dict(raw_candidate_count=10, deduped_candidate_count=8, trusted_forward_count=5, trusted_forward_coverage=0.5)
    out = [
        _call(lambda: fn(no_trade_scorecard={}, **kw)),
        _call(lambda: fn(no_trade_scorecard=ready, **kw)),
        _call(lambda: fn(no_trade_scorecard={"promotion_watchlist": None}, **kw)),
        _call(lambda: fn(raw_candidate_count=1000, deduped_candidate_count=900, trusted_forward_count=800, trusted_forward_coverage=0.9, no_trade_scorecard=ready)),
        _call(lambda: fn(no_trade_scorecard=None, **kw)),
        _call(lambda: fn(no_trade_scorecard={}, raw_candidate_count="x", deduped_candidate_count=1, trusted_forward_count=1, trusted_forward_coverage=1)),
        _call(lambda: fn()),
    ]
    with mock.patch.object(qs, "build_q8_trust_gate", lambda **k: {"block_reasons": ["low_coverage"], "minimums": {}, "seen": sorted(k)}):
        out.append(_call(lambda: fn(no_trade_scorecard={}, **kw)))
        out.append(_call(lambda: fn(no_trade_scorecard=ready, **kw)))
    with mock.patch.object(qs, "build_q8_trust_gate", lambda **k: {"minimums": {"m": 1}, "promotion_allowed": True}):
        out.append(_call(lambda: fn(no_trade_scorecard={}, **kw)))
    with mock.patch.object(qs, "_text", lambda v: "promotion_watch"):
        out.append(_call(lambda: fn(no_trade_scorecard=ready, **kw)))
    with mock.patch.object(qs, "Mapping", tuple):
        out.append(_call(lambda: fn(no_trade_scorecard=ready, **kw)))
    return out


def _a4(fn, mod, root):
    out = [_call(lambda: fn({})), _call(lambda: fn(None)), _call(lambda: fn({"candidate_count": 0})), _call(lambda: fn({"candidate_count": 1, "evaluation": {}})), _call(lambda: fn({"candidate_count": "x"})), _call(lambda: fn())]
    with _Fakes():
        evaluation = qs.build_quant_shadow_candidate_evaluation([{"generated_at": "2026-10-31T00:00:00", "candidates": _cands()}])
        empty_eval = qs.build_quant_shadow_candidate_evaluation([{"candidates": [{"symbol": "Z"}]}])
    out.append(_call(lambda: fn(evaluation)))
    out.append(_call(lambda: fn(empty_eval)))
    out.append(_call(lambda: fn(MappingProxyType(evaluation))))
    broken = json.loads(json.dumps(evaluation, default=repr))
    broken["no_trade_scorecard"]["forward_outcome_coverage"] = "bad"
    out.append(_call(lambda: fn(broken)))
    with mock.patch.object(qs, "_format_rows", lambda rows, limit=4: "FR"), mock.patch.object(qs, "_format_forward_rows", lambda rows, limit=4: "FF"), mock.patch.object(qs, "_format_scorecard_rows", lambda rows, limit=4: "FS"):
        out.append(_call(lambda: fn(evaluation)))
    with mock.patch.object(qs, "_text", lambda v: "T"):
        out.append(_call(lambda: fn(evaluation)))
    with mock.patch.object(qs, "Mapping", tuple):
        out.append(_call(lambda: fn(evaluation)))
    return out


def _a5(fn, mod, root):
    out = [
        _call(lambda: fn({"guard_blocked": False})),
        _call(lambda: fn({"guard_blocked": True, "primary_failure_axis": "other"})),
        _call(lambda: fn({"guard_blocked": "yes", "primary_failure_axis": "confirmed_entry", "entry_quant_decision": {"decision": "entry_ready"}})),
        _call(lambda: fn({"guard_blocked": 1, "primary_failure_axis": "confirmed_entry", "entry_quant_decision": {"decision": "entry_ready", "blockers": ["b"]}})),
        _call(lambda: fn({"guard_blocked": 1, "primary_failure_axis": "confirmed_entry", "entry_quant_decision": {"decision": "entry_ready"}, "guard_reason": "r"})),
        _call(lambda: fn({"guard_blocked": 1, "primary_failure_axis": "confirmed_entry", "entry_quant_decision": {"decision": "block"}})),
        _call(lambda: fn({"guard_blocked": 1, "primary_failure_axis": "confirmed_entry", "blockers": ["x"], "entry_quant_decision": {"decision": "entry_ready"}})),
        _call(lambda: fn({})),
        _call(lambda: fn(None)),
        _call(lambda: fn()),
    ]
    with mock.patch.object(qs, "_bool", lambda v: True):
        out.append(_call(lambda: fn({"primary_failure_axis": "other"})))
    with mock.patch.object(qs, "_entry_quant_decision", lambda row: "entry_ready"), mock.patch.object(qs, "_row_blockers", lambda row: []):
        out.append(_call(lambda: fn({"guard_blocked": 1, "primary_failure_axis": "confirmed_entry"})))
    with mock.patch.object(qs, "_text", lambda v: ""):
        out.append(_call(lambda: fn({"guard_blocked": 1, "primary_failure_axis": "confirmed_entry"})))
    return out


def _a6(fn, mod, root):
    root = Path(root)
    reports = root / "reports"
    reports.mkdir()
    shadow = root / "data" / "logs" / "quant_shadow_candidates"
    payload = {"candidates": [{"symbol": "A"}], "extra": 1, "q9_decision_id": "d1", "q9_decision_candidates": _q9_rows()}
    _w(shadow / "2026-10-31" / "a.json", payload)
    _w(shadow / "2026-10-31" / "b.json", {"candidates": [{"symbol": "B"}], "q9_decision_candidates": [{"x": 1, "y": 2}]})
    _w(shadow / "2026-10-31" / "latest.json", {"candidates": []})
    _w(shadow / "2026-10-31" / "bad.json", "{nope")
    _w(shadow / "2026-10-31" / "list.json", "[1]")
    _w(reports / "operator_summary" / "daily" / "2026-10-31" / "q9_decision_windows.json", {"windows": [{"decision_id": "d1", "commander_final": {"selected_symbol": "A", "decision": "enter"}}]})
    out = []
    gen = fn(reports_root=reports, days=["2026-10-31"])
    out.append(["lazy", [isinstance(gen, types.GeneratorType)]])
    out.append(_call(lambda: list(fn(reports_root=reports, days=["2026-10-31"]))))
    out.append(_call(lambda: list(fn(reports_root=reports, days=["2026-10-31", "2026-10-31T09:00"]))))
    out.append(_call(lambda: list(fn(reports_root=reports, days=["2026-10-31"], keys=["candidates"]))))
    out.append(_call(lambda: list(fn(reports_root=reports, days=["2026-10-31"], keys=["q9_decision_candidates"], drop_q9_row_keys=["x"]))))
    out.append(_call(lambda: list(fn(reports_root=reports, days=["2026-10-31"], keys=["candidates"], drop_q9_row_keys=["x"]))))
    out.append(_call(lambda: list(fn(reports_root=reports, days=["2026-10-30"]))))
    out.append(_call(lambda: list(fn(reports_root=reports, days=[]))))
    out.append(_call(lambda: list(fn(reports_root=reports, days=None))))
    out.append(_call(lambda: list(fn(days=["d"]))))
    it = fn(reports_root=reports, days=["2026-10-31"], keys=[])
    out.append(["first", _call(lambda: next(it))])
    calls = []
    with mock.patch.object(qs, "_q9_windows_by_id", lambda r, d: calls.append(d) or {}):
        out.append(_call(lambda: list(fn(reports_root=reports, days=["2026-10-31"], keys=["candidates"]))))
        out.append(_call(lambda: list(fn(reports_root=reports, days=["2026-10-31"], keys=["q9_decision_candidates"]))))
    out.append(["windows-calls", calls])
    with mock.patch.object(qs, "_read_json", lambda p: {"candidates": [str(p.name)]}):
        out.append(_call(lambda: list(fn(reports_root=reports, days=["2026-10-31"], keys=["candidates"]))))
    with mock.patch.object(qs, "_json_paths_for_day", lambda r, d: [Path("/x/1.json"), Path("/x/1.json"), Path("/x/2.json")]), mock.patch.object(qs, "_read_json", lambda p: {"candidates": [p.name]}):
        out.append(_call(lambda: list(fn(reports_root=reports, days=["d1", "d2"], keys=["candidates"]))))
    with mock.patch.object(qs, "shadow_candidate_root_for_reports", lambda r: root / "elsewhere"):
        out.append(_call(lambda: list(fn(reports_root=reports, days=["2026-10-31"]))))
    with mock.patch.object(qs, "_augment_missing_q9_commander_candidate", lambda p, windows_by_id: dict(p, augmented=True)), mock.patch.object(qs, "_drop_q9_row_keys", lambda p, d: dict(p, dropped=d)):
        out.append(_call(lambda: list(fn(reports_root=reports, days=["2026-10-31"]))))
    return out


def _a7(fn, mod, root):
    def rows(n, **kw):
        return [dict({"reason": "cost_edge_fail"}, **kw) for _ in range(n)]

    out = [
        _call(lambda: fn([])),
        _call(lambda: fn(rows(3))),
        _call(lambda: fn(rows(6))),
        _call(lambda: fn(rows(2))),
        _call(lambda: fn([{"reason": "other"}] * 3)),
        _call(lambda: fn([{"shadow_role": "runner_up_evaluated", "would_enter": True}] * 4)),
        _call(lambda: fn([{"guard_blocked": True, "primary_failure_axis": "other"}] * 6 + [{}] * 4)),
        _call(lambda: fn(rows(3) + [{"guard_blocked": True, "primary_failure_axis": "x"}] * 3)),
        _call(lambda: fn(None)),
        _call(lambda: fn([None])),
        _call(lambda: fn()),
    ]
    with mock.patch.object(qs, "build_entry_quant_enforcement", lambda payload: {"blocked": False}):
        out.append(_call(lambda: fn(rows(3))))
    with mock.patch.object(qs, "build_entry_quant_enforcement", lambda payload: {"blocked": True, "behavior_effect": "hard_gate"}):
        out.append(_call(lambda: fn(rows(6))))
    with mock.patch.object(qs, "build_entry_quant_enforcement", lambda payload: {"blocked": True}):
        out.append(_call(lambda: fn(rows(3))))
    with mock.patch.object(qs, "build_entry_quant_enforcement", lambda payload: (_ for _ in ()).throw(RuntimeError("boom"))):
        out.append(_call(lambda: fn(rows(3))))
        out.append(_call(lambda: fn([{"reason": "other"}] * 3 + [{"shadow_role": "runner_up_evaluated", "would_enter": True}] * 5)))
    with mock.patch.object(qs, "_count_reason", lambda c, n: 0), mock.patch.object(qs, "_actionable_entry_guard_block", lambda r: True), mock.patch.object(qs, "_runner_up_risk_count", lambda c: 1):
        out.append(_call(lambda: fn(rows(4))))
    with mock.patch.object(qs, "_count_reason", lambda c, n: 0), mock.patch.object(qs, "_actionable_entry_guard_block", lambda r: False), mock.patch.object(qs, "_runner_up_risk_count", lambda c: 0):
        out.append(_call(lambda: fn(rows(4))))
    return out


def _a8(fn, mod, root):
    payloads = [{"generated_at": "2026-10-31T00:00:00", "candidates": _cands()}, {"candidates": [{"symbol": "AB"}, "junk"]}, "bad", {"candidates": None}]
    out = []
    with _Fakes():
        out += [
            _call(lambda: fn([])),
            _call(lambda: fn(payloads)),
            _call(lambda: fn(payloads, symbol=" a0 ")),
            _call(lambda: fn(payloads, symbol="zzz")),
            _call(lambda: fn(iter(payloads[:1]))),
            _call(lambda: fn([{"candidates": [{"symbol": "A", "shadow_forward_outcome": {"available": False}}]}])),
            _call(lambda: fn(None)),
            _call(lambda: fn([{"candidates": [{"symbol": "A"}]}], symbol=None)),
            _call(lambda: fn()),
        ]
        with mock.patch.object(qs, "attach_forward_outcomes", lambda rows: [dict(r, attached=True) for r in rows]):
            out.append(_call(lambda: fn([{"candidates": [{"symbol": "A"}]}])))
        with mock.patch.object(qs, "_dedupe_candidates", lambda rows: list(rows)[:1]):
            out.append(_call(lambda: fn(payloads)))
        with mock.patch.object(qs, "_top_counter", lambda c, limit=0: [{"limit": limit, "n": sum(c.values())}]):
            out.append(_call(lambda: fn(payloads)))
        with mock.patch.object(qs, "_evaluation_trust_gate", lambda **k: {"patched_gate": sorted(k)}):
            out.append(_call(lambda: fn(payloads)))
        with mock.patch.object(qs, "_promotion_candidate", lambda c: {"candidate": "PATCHED"}):
            out.append(_call(lambda: fn(payloads)))
        with mock.patch.object(qs, "_bool", lambda v: False):
            out.append(_call(lambda: fn(payloads)))
        with mock.patch.object(qs, "Mapping", tuple):
            out.append(_call(lambda: fn(payloads)))
        with mock.patch.object(qs, "Counter", lambda it: __import__("collections").Counter(["q"])):
            out.append(_call(lambda: fn(payloads)))
    return out


CASES = {
    "a1": (_a1, "_q9_windows_by_id", lambda: windows_owner._q9_windows_by_id, windows_owner),
    "a2": (_a2, "_augment_missing_q9_commander_candidate", lambda: augment_owner._augment_missing_q9_commander_candidate, augment_owner),
    "a3": (_a3, "_evaluation_trust_gate", lambda: trust_owner._evaluation_trust_gate, trust_owner),
    "a4": (_a4, "render_quant_shadow_candidate_evaluation_lines", lambda: render_owner.render_quant_shadow_candidate_evaluation_lines, render_owner),
    "a5": (_a5, "_actionable_entry_guard_block", lambda: guard_owner._actionable_entry_guard_block, guard_owner),
    "a6": (_a6, "iter_quant_shadow_candidate_payloads", lambda: iterator_owner.iter_quant_shadow_candidate_payloads, iterator_owner),
    "a7": (_a7, "_promotion_candidate", lambda: promotion_owner._promotion_candidate, promotion_owner),
    "a8": (_a8, "build_quant_shadow_candidate_evaluation", lambda: builder_owner.build_quant_shadow_candidate_evaluation, builder_owner),
}


def _run(key, which):
    scenario, name, owner_factory, _ = CASES[key]
    if which == "wrapper":
        fn = getattr(qs, name)
    else:
        raw = owner_factory()
        fn = lambda *a, **k: raw(*a, facade=qs, **k)  # noqa: E731
    with tempfile.TemporaryDirectory() as t:
        out = scenario(fn, qs, t)
        return json.loads(json.dumps(out, default=repr).replace(t, "<T>").replace(str(Path(t).resolve()), "<T>"))


class Test(unittest.TestCase):
    def _parity(self, key):
        a = _run(key, "wrapper")
        b = _run(key, "owner")
        self.assertEqual(a, b)
        self.assertEqual(_h(a), GOLDENS[key])
        name, owner_mod = CASES[key][1], CASES[key][3]
        fn = ast.parse(inspect.getsource(getattr(qs, name))).body[0]
        stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
        self.assertEqual(len(stmts), 1)
        if key == "a6":
            self.assertTrue(isinstance(stmts[0], ast.Expr) and isinstance(stmts[0].value, ast.YieldFrom))
        else:
            self.assertIsInstance(stmts[0], ast.Return)
        self.assertNotIn("import quant_shadow_candidate_evaluation", inspect.getsource(owner_mod))
        self.assertIn("facade", inspect.getsource(getattr(owner_mod, name)))
        return a

    def test_a1_q9_windows(self):
        out = self._parity("a1")
        self.assertEqual(out[0], ["ok", {"d1": {"commander_final": {"decision": "hold"}}, "5": {"commander_final": None}}])
        self.assertEqual(out[2], ["ok", {}])
        self.assertEqual(out[3], ["ok", {}])
        self.assertEqual(out[4][0], "exc")

    def test_a2_q9_augment(self):
        out = self._parity("a2")
        added = out[0][1]
        self.assertTrue(added[0])
        self.assertEqual([r.get("q9_decision_role") for r in added[1] if isinstance(r, dict)][-1], "C_COMMANDER_FINAL")
        self.assertEqual(out[1][1][0], True)

    def test_a3_trust_gate(self):
        out = self._parity("a3")
        self.assertEqual(out[0][1]["behavior_effect"], "evaluation_only")
        self.assertEqual(out[7][1]["reasons"], ["low_coverage"])
        self.assertEqual(out[8][1]["promotion_ready_candidates"], [{"review_state": "promotion_watch", "name": "x"}])
        self.assertIn("candidate_avg_return_5m_pct", out[0][1]["minimum_requirements"])

    def test_a4_render_lines(self):
        out = self._parity("a4")
        self.assertEqual(out[0], ["ok", []])
        self.assertEqual(out[1], ["ok", []])
        self.assertEqual(out[2], ["ok", []])
        self.assertIn("## Quant Shadow Candidates", out[3][1])
        self.assertEqual(out[4][0], "exc")
        self.assertIn("## Quant Shadow Candidates", out[6][1])

    def test_a5_guard_observation(self):
        out = self._parity("a5")
        self.assertEqual(out[0], ["ok", False])
        self.assertEqual(out[1], ["ok", True])
        self.assertEqual(out[2], ["ok", False])
        self.assertEqual(out[3], ["ok", True])
        self.assertEqual(out[10], ["ok", True])

    def test_a6_payload_iterator(self):
        out = self._parity("a6")
        self.assertEqual(out[0], ["lazy", [True]])
        self.assertEqual(out[1][0], "ok")
        dup = out[2][1]
        self.assertEqual(len(dup), len(out[1][1]))
        self.assertEqual(out[-4][1][0], {"candidates": ["a.json"]})
        self.assertEqual(out[-3], ["ok", [{"candidates": ["1.json"]}, {"candidates": ["2.json"]}]])
        self.assertEqual(out[-6][1][0]["q9_decision_candidates"][0]["symbol"], "A")

    def test_a7_promotion(self):
        out = self._parity("a7")
        self.assertEqual((out[0][1]["candidate"], out[0][1]["reason"]), ("hold", "no_shadow_candidates"))
        self.assertEqual(out[1][1]["counts"], {"cost_edge": 3, "runner_up": 0, "entry_guard": 0})
        self.assertEqual(out[1][1]["confidence"], "medium")
        self.assertEqual(out[11][1]["recommended_action"], "promote_shadow_validated_guard")
        self.assertEqual(out[12][1]["recommended_action"], "already_promoted_monitor_hard_gate")

    def test_a8_evaluation_builder(self):
        out = self._parity("a8")
        empty = out[0][1]
        self.assertEqual(empty["schema_version"], "quant_shadow_candidate_evaluation.v1")
        self.assertEqual((empty["candidate_count"], empty["behavior_effect"]), (0, "observation_only"))
        self.assertEqual(out[3][1]["candidate_count"], 0)
        self.assertEqual(out[1][1]["candidate_count"], 13)
        self.assertEqual(out[6][0], "exc")


if __name__ == "__main__":
    unittest.main()
