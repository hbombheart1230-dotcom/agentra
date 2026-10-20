"""P1.5 DEV-A: strategist feedback projection parity.

The frozen BASE ``reporter_feedback.py`` (``41ca719a``) is exec'd as a separate module and compared with the current
facade on identical temp report trees: full packet JSON (key order), ``feedback_id``, read order of report files,
exception type/message, malformed/missing inputs and late monkeypatch. Only temp directories are read or written.
"""
from __future__ import annotations

import ast
import json
import subprocess
import types
from pathlib import Path

import pytest

import libs.reporting.reporter_feedback as cur
import libs.reporting.reporter_feedback_projection as proj

ROOT = Path(__file__).resolve().parents[1]
BASE = "41ca719a7a0717b185ed77674541fd6671f45b2b"
PATH = "libs/reporting/reporter_feedback.py"
MOVED = ("_extract_reporter_analysis_blocker_totals", "_extract_reporter_analysis_recommendations", "_build_dominant_patterns",
         "_build_blocker_analysis", "_build_route_analysis", "_build_recommendations", "_build_insight_summary",
         "_build_confidence")
DAY = "2026-04-23"


def _base_module():
    src = subprocess.check_output(["git", "show", f"{BASE}:{PATH}"], cwd=ROOT).decode("utf-8-sig")
    mod = types.ModuleType("reporter_feedback_base_41ca719a")
    exec(compile(src, f"<base:{PATH}>", "exec"), mod.__dict__)
    return mod


def _w(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False), encoding="utf-8")


METRICS = {"route_selected_total": {"monitor_only": 30, "cached_strategist": 15, "full_cycle": 9},
           "strategist_fallback_total": 4, "route_source": "events",
           "blocker_totals": {"vwap_reclaim_not_ready": 12, "cost_edge_fail": 9, "min_hold": 3, "사용자 정의 차단": 2},
           "latest_run_id": "run-77", "freshness_status": "fresh", "source_window_summary": "09:00-15:30"}
ANALYSIS = {"monitor_evaluation": {"monitor_reason_top": {"hold": 5, "": 3, "reclaim_wait": "4"}},
            "supervisor_activity": {"blocked_reason_top": {"risk_limit": 7}},
            "intent_flow_analysis": {"reason_top": {"monitor:hold": 9, "spread": 2}},
            "improvement_suggestions": ["", "모니터 청산 품질 점검", "Check spread"],
            "operator_facing_summary": {"recommended_actions": ["fallback action"]}}


def _trade(root: Path, n: int, pnl, pct, *, broker=True):
    d = root / "trades" / DAY / f"TRD_20260423_{5930 + n:06d}_01" / "reports"
    _w(d / "ai_trade_report.json", {"trade_id": d.parent.name, "symbol": f"{5930 + n:06d}", "truth_surface": {
        "status": {"status": "closed", "exit_reason": "peak_drawdown"},
        "price": {"broker_buy_price": 1000.0, "broker_fill_price": 1000.0 if n % 2 else 1010.0},
        "pnl": {"value": pnl, "pct": pct, "broker_fee": 15, "broker_tax": 4},
        "availability": {"broker_fill_present": broker, "broker_pnl_present": broker}}})


def _tree(tmp: Path, kind: str) -> Path:
    root = tmp / kind / "reports"
    root.mkdir(parents=True)
    if kind in ("metrics", "all"):
        _w(root / "metrics" / f"metrics_{DAY}.json", METRICS)
    if kind in ("analysis", "all"):
        _w(root / "dev" / "analysis" / "reporter_analysis" / f"reporter_analysis_{DAY}.json", ANALYSIS)
    if kind in ("trades", "all"):
        for n, (pnl, pct) in enumerate(((-522.0, -0.0023), (310.0, 0.0011), (None, None), (0.0, 0.0))):
            _trade(root, n, pnl, pct, broker=n != 2)
    if kind == "malformed":
        _w(root / "metrics" / f"metrics_{DAY}.json", "{not json")
        _w(root / "dev" / "analysis" / "reporter_analysis" / f"reporter_analysis_{DAY}.json", "[1, 2]")
    return root


CASES = {
    "metrics_report_payload": ("empty", "metrics_report", METRICS, DAY),
    "metrics_file": ("metrics", "daily_report", {"day": DAY}, None),
    "analysis_fallback": ("analysis", "daily_report", {"day": DAY}, DAY),
    "analysis_payload_mode": ("empty", "reporter_analysis", {**ANALYSIS, "day": DAY}, None),
    "trade_explain_payload": ("empty", "trade_explain", {"route_selected_total": {"full_cycle": 3}, "blocker_totals": {"x": 1}}, DAY),
    "trade_reports_only": ("trades", "daily_report", {"day": DAY}, DAY),
    "everything": ("all", "daily_report", {"day": DAY, "latest_run_id": "payload-run"}, DAY),
    "malformed_files": ("malformed", "daily_report", {"day": DAY}, DAY),
    "no_day_no_payload": ("empty", "", None, None),
    "unicode_mode_and_bad_counts": ("all", "모드", {"route_selected_total": {"monitor_only": "x", "full_cycle": "7"}}, DAY),
}


def _packet(mod, root, mode, payload, day):
    try:
        return ("ok", json.dumps(mod.build_strategist_feedback_packet(mode=mode, payload=payload, reports_root=root, day=day),
                                 ensure_ascii=False))
    except Exception as exc:  # noqa: BLE001
        return ("exc", type(exc).__name__, str(exc))


@pytest.mark.parametrize("case", sorted(CASES))
def test_packet_bytes_and_feedback_id_match_base(case, tmp_path):
    base = _base_module()
    kind, mode, payload, day = CASES[case]
    root = _tree(tmp_path, kind)
    got, want = _packet(cur, root, mode, payload, day), _packet(base, root, mode, payload, day)
    assert got == want
    if got[0] == "ok" and kind == "all":
        doc = json.loads(got[1])
        assert doc["feedback_id"] and doc["confidence"] in ("medium", "high") and doc["dominant_patterns"]


def test_fixtures_reach_distinct_recommendation_and_confidence_branches(tmp_path):
    seen = set()
    for case, (kind, mode, payload, day) in CASES.items():
        status, *rest = _packet(cur, _tree(tmp_path / case, kind), mode, payload, day)
        if status == "ok":
            doc = json.loads(rest[0])
            seen.add((doc["confidence"], doc["recommendation"][0][:20]))
    assert len({c for c, _ in seen}) == 3 and len(seen) >= 5


def test_report_read_order_and_counts_match_base(tmp_path, monkeypatch):
    base = _base_module()
    root = _tree(tmp_path, "all")
    logs = []
    for mod in (base, cur):
        log = []
        real = mod._read_json
        monkeypatch.setattr(mod, "_read_json", lambda p, _l=log, _r=real: (_l.append(Path(p).relative_to(root).as_posix()), _r(p))[1])
        _packet(mod, root, "daily_report", {"day": DAY}, DAY)
        logs.append(log)
    assert logs[0] == logs[1] and logs[1]


@pytest.mark.parametrize("name", MOVED)
def test_each_moved_function_matches_base_including_hostile_inputs(name):
    base = _base_module()
    ra = {"route_selected_total": {"monitor_only": 6, "cached_strategist": 3, "full_cycle": 1}}
    ba = [{"blocker": "vwap_reclaim", "count": 9}, {"blocker": "spread", "count": "3"}]
    trade = {"closed_trade_count": 4, "win_count": 1, "loss_count": 2, "flat_count": 1, "unknown_pnl_count": 1,
             "avg_pnl_pct": -0.1, "pnl_pct_sample_count": 3, "same_price_cost_loss_count": 1, "broker_truth_count": 3}
    cases = {
        "_extract_reporter_analysis_blocker_totals": [((ANALYSIS,), {}), ((None,), {}), (({"monitor_evaluation": []},), {})],
        "_extract_reporter_analysis_recommendations": [((ANALYSIS,), {}), (({"operator_facing_summary": {"recommended_actions": ["a", "", "b"]}},), {}), ((None,), {})],
        "_build_dominant_patterns": [((), dict(route_summary=METRICS, blocker_totals=METRICS["blocker_totals"], freshness=METRICS, trade_report_summary=trade)),
                                     ((), dict(route_summary={}, blocker_totals={}, freshness={}))],
        "_build_blocker_analysis": [(({"b": 2, "a": 2, "c": "x", 3: 1, "d": 5, "e": 1, "f": 9},), {}), (({},), {})],
        "_build_route_analysis": [((METRICS,), {}), (({},), {})],
        "_build_recommendations": [((), dict(route_analysis={"monitor_only_ratio": 0.6, "cached_strategist_ratio": 0.3}, blocker_analysis=ba, trade_report_summary=trade)),
                                   ((), dict(route_analysis={}, blocker_analysis=[])),
                                   ((), dict(route_analysis={"monitor_only_ratio": "bad"}, blocker_analysis=[]))],
        "_build_insight_summary": [((), dict(route_analysis=ra, blocker_analysis=ba, trade_report_summary=trade)),
                                   ((), dict(route_analysis={"route_selected_total": {"a": 0}}, blocker_analysis=[])),
                                   ((), dict(route_analysis={}, blocker_analysis=[]))],
        "_build_confidence": [((), dict(route_analysis=ra, blocker_analysis=ba * 2, trade_report_summary=trade)),
                              ((), dict(route_analysis={}, blocker_analysis=ba)), ((), dict(route_analysis={}, blocker_analysis=[]))],
    }
    for args, kw in cases[name]:
        got = _outcome(getattr(cur, name), *args, **kw)
        assert got == _outcome(getattr(base, name), *args, **kw), (name, args, kw)


def _outcome(fn, *a, **k):
    try:
        return ("ok", json.dumps(fn(*a, **k), ensure_ascii=False, default=repr))
    except Exception as exc:  # noqa: BLE001
        return ("exc", type(exc).__name__, str(exc))


def test_late_monkeypatch_of_helpers_reaches_projection_like_base(tmp_path, monkeypatch):
    base = _base_module()
    root = _tree(tmp_path, "all")
    out = []
    for mod in (base, cur):
        monkeypatch.setattr(mod, "_ratio", lambda c, t: 0.5)
        monkeypatch.setattr(mod, "_build_confidence", lambda **_k: "patched")
        monkeypatch.setattr(mod, "stable_evidence_id", lambda kind, body: f"{kind}:{sorted(body)}")
        out.append(_packet(mod, root, "daily_report", {"day": DAY}, DAY))
        monkeypatch.undo()
    assert out[0] == out[1]
    doc = json.loads(out[1][1])
    assert doc["confidence"] == "patched" and doc["route_analysis"]["monitor_only_ratio"] == 0.5
    assert doc["feedback_id"].startswith("feedback:")


def test_facade_keeps_io_identity_and_signatures():
    base_src = subprocess.check_output(["git", "show", f"{BASE}:{PATH}"], cwd=ROOT).decode("utf-8-sig")
    cur_src = (ROOT / PATH).read_text(encoding="utf-8-sig")
    bf = {n.name: n for n in ast.parse(base_src).body if isinstance(n, ast.FunctionDef)}
    cf = {n.name: n for n in ast.parse(cur_src).body if isinstance(n, ast.FunctionDef)}
    assert list(bf) == list(cf)
    for name, node in cf.items():
        assert ast.dump(node.args) == ast.dump(bf[name].args) and ast.dump(node.returns) == ast.dump(bf[name].returns)
        if name in MOVED:
            assert len(node.body) == 1 and f"_feedback_projection.{name}(" in ast.unparse(node.body[0])
        elif name != "build_strategist_feedback_packet":
            assert ast.dump(node) == ast.dump(bf[name]), name
    seg = ast.unparse(cf["build_strategist_feedback_packet"])
    for kept in ("_load_or_generate_metrics_payload(", "_read_json(", "_build_trade_report_feedback_summary(", "stable_evidence_id("):
        assert kept in seg


def test_projection_is_read_only_and_independently_callable():
    tree = ast.parse((ROOT / "libs/reporting/reporter_feedback_projection.py").read_text(encoding="utf-8"))
    mods = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)} | \
        {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert mods == {"__future__", "typing"}
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)} | {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert not names & {"open", "read_text", "write_text", "_read_json", "_load_or_generate_metrics_payload",
                        "_build_trade_report_feedback_summary", "stable_evidence_id", "Path", "environ", "getenv"}
    assert not [n for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and "facade." in n.value]
    stub = types.SimpleNamespace(_safe_int=lambda v, d=0: int(v) if str(v).lstrip("-").isdigit() else d,
                                 _safe_total=lambda c: sum(int(v) for v in (c or {}).values()),
                                 _ratio=lambda c, t: round(c / t, 4) if t else 0.0)
    assert proj._build_route_analysis({"route_selected_total": {"monitor_only": 1, "full_cycle": 3}}, facade=stub)["full_cycle_ratio"] == 0.75
