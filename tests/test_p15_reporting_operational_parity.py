"""P1.5 BATCH05-A: BASE (4dbbfa34) vs current parity for the four Reporter operational projections.

Each frozen BASE facade is exec'd as its own module (registered in ``sys.modules`` so pinned R3 wrappers resolve
it) beside the live facade. Entry points are driven by (1) the existing upstream tests, whose real entry-point
calls are recorded and then replayed against BASE and current with a fixed clock, and (2) synthetic branch
fixtures. Full JSON/Markdown bytes, exceptions and call order are compared. Temp directories only.
"""
from __future__ import annotations

import copy
import importlib.util
import inspect
import json
import subprocess
import sys
import types
from pathlib import Path

import pytest

import libs.reporting.metrics_report_generator as metrics_cur
import libs.reporting.operator_period_summary as period_cur
import libs.reporting.operator_visibility as visibility_cur
import libs.reporting.phase_runtime_health as health_cur

ROOT = Path(__file__).resolve().parents[1]
BASE = "4dbbfa34c2f89a407bcc3b79b11d88b945ba7f42"
NOW = "2026-10-20T00:00:00+00:00"
FACADES = {
    "visibility": ("libs/reporting/operator_visibility.py", visibility_cur),
    "health": ("libs/reporting/phase_runtime_health.py", health_cur),
    "period": ("libs/reporting/operator_period_summary.py", period_cur),
    "metrics": ("libs/reporting/metrics_report_generator.py", metrics_cur),
}
_BASE_CACHE: dict = {}


def base(key):
    if key not in _BASE_CACHE:
        path = FACADES[key][0]
        src = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT).decode("utf-8-sig")
        name = f"_p15_base_{key}_4dbbfa34"
        mod = types.ModuleType(name)
        mod.__file__ = str(ROOT / path)
        sys.modules[name] = mod
        exec(compile(src, f"<base:{path}>", "exec"), mod.__dict__)
        _BASE_CACHE[key] = mod
    return _BASE_CACHE[key]


def _fix_clock(monkeypatch, *mods):
    for m in mods:
        if hasattr(m, "_utc_now_iso"):
            monkeypatch.setattr(m, "_utc_now_iso", lambda: NOW)


def _outcome(fn, *a, **k):
    try:
        res = fn(*a, **k)
    except Exception as exc:  # noqa: BLE001
        return ("exc", type(exc).__name__, str(exc))
    return ("ok", _norm(res))


def _norm(res):
    if isinstance(res, tuple) and res and all(isinstance(x, Path) for x in res):
        return [(str(p), p.read_bytes() if p.exists() else None) for p in res]
    return json.dumps(res, ensure_ascii=False, sort_keys=False, default=repr)


def _load_test_module(name):
    spec = importlib.util.spec_from_file_location(f"_p15_upstream_{name}", ROOT / "tests" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ENTRYPOINTS = {
    "visibility": ["build_operator_daily_summary_payload", "generate_operator_daily_summary"],
    "health": ["build_phase_5_2_5_3_runtime_health", "render_phase_5_2_5_3_runtime_health_text",
               "_build_policy_aware_gating_deadness", "_build_policy_source_summary", "_compact_run_view",
               "_build_suspicious_flags"],
    "period": ["_runtime_activity_payload", "build_operator_daily_summary_artifact_payload"],
    "metrics": ["generate_metrics_report"],
}
UPSTREAM = {
    "visibility": ("test_operator_visibility_reports", ["test_operator_daily_summary_script_generates_red_status",
                                                        "test_operator_daily_summary_treats_unmeasurable_slo_artifact_as_stale_diagnostic",
                                                        "test_operator_daily_summary_supports_new_decision_trace_events"]),
    "health": ("test_check_phase_5_2_5_3_runtime_health", None),
    "metrics": ("test_generate_metrics_report", None),
}


def _record_upstream(key, tmp_path, monkeypatch, capsys):
    """Run upstream tests against the CURRENT facade while recording entry-point calls (deep-copied args)."""
    mod_name, only = UPSTREAM[key]
    cur = FACADES[key][1]
    calls = []
    for name in ENTRYPOINTS[key]:
        real = getattr(cur, name)

        def spy(*a, _n=name, _r=real, **k):
            calls.append((_n, copy.deepcopy(a), copy.deepcopy(k)))
            return _r(*a, **k)
        monkeypatch.setattr(cur, name, spy)
        # re-exports bound earlier, possibly aliased (scripts.generate_metrics_report: `as _generate_metrics_report`)
        for mod_name_, other in list(sys.modules.items()):
            if other is cur or not mod_name_.startswith(("scripts.", "libs.", "graphs.", "apps.")):
                continue
            for attr, value in list(vars(other).items()):
                if value is real:
                    monkeypatch.setattr(other, attr, spy)
    tests = _load_test_module(mod_name)  # after spies: upstream modules may bind entry points at import time
    names = only or [n for n in dir(tests) if n.startswith("test_")]
    for i, tname in enumerate(names):
        fn = getattr(tests, tname)
        params = inspect.signature(fn).parameters
        avail = {"tmp_path": tmp_path / f"u{i}", "monkeypatch": monkeypatch, "capsys": capsys}
        avail["tmp_path"].mkdir()
        fn(**{p: avail[p] for p in params})
        capsys.readouterr()
    monkeypatch.undo()
    return calls


@pytest.mark.parametrize("key", sorted(UPSTREAM))
def test_upstream_entrypoint_calls_replay_identically_on_base(key, tmp_path, monkeypatch, capsys):
    calls = _record_upstream(key, tmp_path, monkeypatch, capsys)
    assert calls, key
    b, cur = base(key), FACADES[key][1]
    _fix_clock(monkeypatch, b, cur)
    for name, a, k in calls:
        want = _outcome(getattr(b, name), *copy.deepcopy(a), **copy.deepcopy(k))
        got = _outcome(getattr(cur, name), *copy.deepcopy(a), **copy.deepcopy(k))
        assert got == want, (key, name)


# ---------- A4 metrics: synthetic events covering every aggregation branch ----------

def _metrics_events(path: Path, day="2026-03-10"):
    t = 1773100800  # 2026-03-10T00:00:00Z
    rows = []
    def add(stage, event, payload, run="r1", dt=0):
        rows.append({"ts": t + dt, "run_id": run, "stage": stage, "event": event, "payload": payload})
    add("decision", "trace", {"decision_packet": {"intent": {"action": "BUY"}}})
    add("decision", "trace", {"decision_packet": {"intent": {"action": "HOLD"}}}, run="r2", dt=5)
    add("execute_from_packet", "verdict", {"allowed": True})
    add("execute_from_packet", "verdict", {"allowed": False, "reason": "max_notional"}, run="r2", dt=6)
    for j, why in enumerate(["sector_cap", "max_notional", "cooldown", "spread", "halt", "단일종목"]):
        for _ in range(6 - j):
            add("execute_from_packet", "verdict", {"allowed": False, "reason": why}, run=f"b{j}", dt=30 + j)
    add("execute_from_packet", "execution", {"broker_code": "0"})
    add("broker", "error", {"api_id": "ka10080", "response": {"status_code": 429}}, dt=7)
    add("broker", "error", {"api_id": "kt00001", "message": "boom"}, dt=8)
    for i, payload in enumerate([
        {"ok": True, "latency_ms": 812, "attempts": 1, "prompt_tokens": 100, "completion_tokens": "40", "total_tokens": 140,
         "estimated_cost_usd": 0.0012, "circuit_state": "closed", "prompt_version": "p3", "schema_version": "s2"},
        {"ok": False, "error_type": "CircuitOpen", "latency_ms": "bad", "attempts": -1, "prompt_tokens": None, "circuit_state": "OPEN"},
        {"ok": False, "latency_ms": -5, "estimated_cost_usd": "x"}]):
        add("strategist_llm", "result", payload, dt=10 + i)
    add("strategist", "policy_resolution", {"strategy_generation_mode": "llm", "fallback_used": True}, dt=20)
    add("monitor", "entry_decision_detail", {"no_trade_surface": {"no_trade_reason_code": "vwap_wait", "dominant_blocker": "reclaim",
        "near_ready_flag": True, "no_trade_stage": "pre_intent_wait"}, "scanner_monitor_handoff": {"scanner_vs_monitor_alignment": "aligned"}}, dt=21)
    add("monitor", "entry_decision_detail", {"no_trade_surface": {"no_trade_stage": "guard_block"}}, dt=22)
    add("monitor", "entry_decision_detail", {"no_trade_surface": {"no_trade_stage": "pre_intent_noop"}}, dt=23)
    add("skill_hydration", "summary", {"used_runner": True, "runner_source": "local", "errors_total": 2, "attempted": {"news": 2, "chart": "x"},
                                        "ready": {"news": 1}, "errors": [{"skill": "news", "error": "timeout"}, "raw-error"]}, dt=24)
    add("skill_hydration", "summary", {"fallback_hint": True}, dt=25)
    for ev, payload in [("route_selected", {"route_selected": "full_cycle", "status": "ok"}),
                        ("end", {"route_observability": {"route_selected": "monitor_only"}}),
                        ("transition", {"transition": "COOLDOWN"}), ("transition", {"reason": "cooldown_active"}),
                        ("intervention", {}), ("error", {}), ("resilience", {"reason": ""}),
                        ("route_selected", {"portfolio_guard": {"applied": True, "approved_total": 3, "blocked_total": "2",
                                                                 "blocked_reason_counts": {"sector_cap": 2, "bad": "x"}}})]:
        add("commander_router", ev, payload, run="r3", dt=30)
    add("monitor", "summary", {"exit_policy_enabled": True, "exit_evaluated": True, "exit_triggered": True, "exit_reason": "익절",
                               "position_sizing_enabled": True, "position_sizing_evaluated": True, "position_sizing_qty": 0,
                               "position_sizing_reason": "cash_floor"}, dt=40)
    add("monitor", "summary", {"position_sizing_qty": "7"}, run="", dt=41)
    rows.append({"ts": t - 86400, "run_id": "old", "stage": "decision", "event": "trace", "payload": {}})  # previous day
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return path


@pytest.mark.parametrize("day", ["2026-03-10", None, "2026-01-01"])
def test_metrics_report_bytes_match_base_on_branch_fixture(day, tmp_path, monkeypatch):
    events = _metrics_events(tmp_path / "events.jsonl")
    b = base("metrics")
    _fix_clock(monkeypatch, b, metrics_cur)
    out_dir = tmp_path / "reports" / "metrics"
    want = _outcome(b.generate_metrics_report, events, out_dir, day=day)
    got = _outcome(metrics_cur.generate_metrics_report, events, out_dir, day=day)
    assert got == want
    if got[0] == "ok" and day == "2026-03-10":
        doc = json.loads(got[1][1][1])
        assert doc["strategist_llm"]["total"] == 3 and doc["portfolio_guard"]["total"] == 1 and doc["broker_api"]["api_429_total"] == 1


def test_metrics_write_path_resolution_clock_and_route_order_match_base(tmp_path, monkeypatch):
    events = _metrics_events(tmp_path / "events.jsonl")
    logs = []
    for m in (base("metrics"), metrics_cur):
        log = []
        for name in ("resolve_runtime_write_path", "iter_jsonl_events", "_build_event_rows", "_latency_summary",
                     "build_commander_route_summary", "_utc_now_iso", "_epoch_to_iso", "build_data_freshness",
                     "build_route_provenance", "_render_metrics_markdown", "_extract_guard_reason", "_numeric_summary"):
            real = getattr(m, name)
            monkeypatch.setattr(m, name, lambda *a, _n=name, _r=real, _l=log, **k: (_l.append(_n), _r(*a, **k))[1])
        monkeypatch.setattr(m, "_utc_now_iso", (lambda _l=log: (_l.append("_utc_now_iso"), NOW)[1]))
        m.generate_metrics_report(events, tmp_path / "reports" / "metrics", day="2026-03-10")
        logs.append(log)
        monkeypatch.undo()
    assert logs[0] == logs[1]
    assert logs[1][0] == "resolve_runtime_write_path"
    assert logs[1].index("build_commander_route_summary") < logs[1].index("_utc_now_iso") < logs[1].index("_epoch_to_iso")


# ---------- A3 period: runtime activity shapes and CRITICAL closeout overlay ----------

def _q9(root: Path, day: str, windows):
    p = root / "operator_summary" / "daily" / day / "q9_decision_windows.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(windows if isinstance(windows, str) else json.dumps({"windows": windows}, ensure_ascii=False), encoding="utf-8")


@pytest.mark.parametrize("case", ["q9", "q9_all_synthetic", "q9_unreadable", "daily_payload", "live", "none"])
def test_runtime_activity_shapes_match_base(case, tmp_path, monkeypatch):
    day = "2026-05-11"
    root = tmp_path / "reports"
    src = {}
    if case == "q9":
        _q9(root, day, [{"decision_id": "d1", "commander_final": {"decision": "Approve", "monitor_intent": "buy"}},
                        {"decision_id": "d2", "commander_final": {"decision": "veto"}}, {"decision_id": "d3"},
                        {"decision_id": "d4", "commander_final": {"decision": "no_trade", "monitor_intent": "NOOP"}}, "junk"])
    elif case == "q9_all_synthetic":
        _q9(root, day, [{"decision_id": "test-1"}, {"run_id": "fixture"}])
        src = {"events": "12", "approvals": 2, "symbols_observed": ["005930", "000660"]}
    elif case == "q9_unreadable":
        _q9(root, day, "{not json")
    elif case == "daily_payload":
        src = {"blocks": "x", "generated_symbol_report_count": 3}
    b = base("period")
    if case == "live":
        live = ({"lookback_min": "15", "events": {"window_total": 9, "scanned_total": "x"},
                 "execution": {"allowed_total": 2, "blocked_total": 1, "executed_total": 1, "executed_broker_fail_total": 0}}, "live.json")
        for m in (b, period_cur):
            monkeypatch.setattr(m, "_latest_live_summary_payload", lambda r, d, _v=live: _v)
    got = _outcome(period_cur._runtime_activity_payload, reports_root=root, day=day, source_payload=src)
    assert got == _outcome(b._runtime_activity_payload, reports_root=root, day=day, source_payload=src)


@pytest.mark.parametrize("severity", ["critical", "CRITICAL", "high", None])
def test_daily_artifact_payload_and_critical_overlay_match_base(severity, tmp_path, monkeypatch):
    b = base("period")
    root = tmp_path / "reports"
    residual = {"closeout_operational_risk": {"severity": severity, "unresolved_symbols": ["005930", "", "000660"]}} if severity else []
    outs = []
    for m in (b, period_cur):
        _fix_clock(monkeypatch, m)
        monkeypatch.setattr(m, "_build_residual_positions_payload", lambda **k: copy.deepcopy(residual))
        monkeypatch.setattr(m, "build_controlled_validation_daily", lambda **k: {"status": "stub"})
        monkeypatch.setattr(m, "load_latest_macro_snapshot", lambda *a, **k: {})
        outs.append(_outcome(m.build_operator_daily_summary_artifact_payload, reports_root=root, day="2026-05-11",
                             daily_report_payload={"events": 3, "trade_index": []}))
    assert outs[0] == outs[1]
    if severity in ("critical", "CRITICAL"):
        assert "CRITICAL closeout issue" in outs[1][1] and "005930, 000660" in outs[1][1]


# ---------- A1 visibility: health escalation branches on synthetic artifacts ----------

def _vis_tree(tmp: Path, *, m30, m31, rows, metrics):
    root = tmp / "reports"
    ev = tmp / "events.jsonl"
    ev.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    day = "2026-03-10"
    (root / "metrics").mkdir(parents=True, exist_ok=True)
    (root / "metrics" / f"metrics_{day}.json").write_text(json.dumps(metrics), encoding="utf-8")
    if m30 is not None:
        p = root / "m30_post" / f"m30_post_golive_policy_{day}.json"
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps(m30), encoding="utf-8")
    if m31 is not None:
        p = root / "m31" / f"m31_slo_incident_{day}.json"
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps(m31), encoding="utf-8")
    return ev, root, day


VIS_ROWS = [
    {"ts": "2026-03-10T00:00:01Z", "run_id": "r1", "stage": "decision", "event": "trace",
     "payload": {"decision_packet": {"intent": {"action": "BUY", "symbol": "005930"}}, "trace": {"strategy": "돌파"}}},
    {"ts": "2026-03-10T00:00:02Z", "run_id": "r1", "stage": "execute_from_packet", "event": "verdict", "payload": {"allowed": False, "reason": "max_notional"}},
    {"ts": "2026-03-10T00:00:03Z", "run_id": "r2", "stage": "execute_from_packet", "event": "execution", "payload": {"payload": {"broker_code": "1"}}},
    {"ts": "2026-03-10T00:00:04Z", "run_id": "r2", "stage": "commander_router", "event": "transition", "payload": {"transition": "cooldown", "x": "duplicate_execution"}},
    {"ts": "2026-03-10T00:00:05Z", "run_id": "r3", "stage": "decision_trace", "event": "strategic_frame", "payload": {"payload": {"playbook": "pullback"}}},
    {"ts": "2026-03-10T00:00:06Z", "run_id": "r3", "stage": "monitor", "event": "error", "payload": {"note": "guard_precedence_violation"}},
]
VIS_CASES = {
    "red_everything": dict(m30={"escalation_level": "incident"}, m31={"ok": False, "failure_total": 4, "slo": {"event_total": 3}}, rows=VIS_ROWS,
                           metrics={"execution": {"intents_created": 9, "intents_blocked": 8}, "broker_api": {"api_429_rate": 0.5},
                                    "strategist_llm": {"total": 4, "success_rate": 0.75}}),
    "watch_unmeasurable": dict(m30={"escalation_level": "WATCH"}, m31={"ok": False, "slo": {"event_total": 0, "run_total": 0}}, rows=VIS_ROWS[:3],
                               metrics={"execution": {"intents_created": 4, "intents_blocked": 4}}),
    "yellow_api_429_boundary": dict(m30=None, m31=None, rows=VIS_ROWS[4:5], metrics={"broker_api": {"api_429_rate": 0.22}}),
    "green_empty_metrics": dict(m30=None, m31=None, rows=VIS_ROWS[4:5], metrics={}),
    "no_rows_m31_failed": dict(m30={"escalation_level": "watch"}, m31={"ok": False, "slo": {"event_total": 0, "run_total": 0}}, rows=[],
                               metrics={"execution": "bad", "strategist_llm": {"total": "x"}}),
}


@pytest.mark.parametrize("case", sorted(VIS_CASES))
def test_operator_daily_summary_payload_and_markdown_match_base(case, tmp_path, monkeypatch):
    ev, root, day = _vis_tree(tmp_path, **VIS_CASES[case])
    b = base("visibility")
    kw = dict(day=day, metrics_report_dir=root / "metrics", m30_post_golive_dir=root / "m30_post",
              m30_golive_dir=root / "m30_go", m31_slo_incident_dir=root / "m31")
    _fix_clock(monkeypatch, b, visibility_cur)
    want = _outcome(b.build_operator_daily_summary_payload, ev, root / "operator_summary", **kw)
    got = _outcome(visibility_cur.build_operator_daily_summary_payload, ev, root / "operator_summary", **kw)
    assert got == want
    if case == "red_everything":
        doc = json.loads(got[1])
        assert doc["system_health_status"]["system_health_level"] == "RED" and len(doc["top_issues"]) >= 5
    md_want = _outcome(b.generate_operator_daily_summary, ev, root / "md", **kw)
    md_got = _outcome(visibility_cur.generate_operator_daily_summary, ev, root / "md", **kw)
    assert md_got == md_want


def test_visibility_helper_late_patch_reaches_readout_like_base(tmp_path, monkeypatch):
    ev, root, day = _vis_tree(tmp_path, **VIS_CASES["red_everything"])
    outs = []
    for m in (base("visibility"), visibility_cur):
        _fix_clock(monkeypatch, m)
        monkeypatch.setattr(m, "_health_badge", lambda h: f"<<{h}>>")
        monkeypatch.setattr(m, "narrative_axis_policy", lambda: {"patched": True})
        outs.append(_outcome(m.build_operator_daily_summary_payload, ev, root / "s", day=day, metrics_report_dir=root / "metrics",
                             m30_post_golive_dir=root / "m30_post", m31_slo_incident_dir=root / "m31"))
    assert outs[0] == outs[1] and "<<RED>>" in outs[1][1] and '"patched": true' in outs[1][1]


# ---------- A2 runtime health: direct pure aggregate/render parity on hostile inputs ----------

def test_runtime_health_pure_functions_match_base_on_hostile_inputs():
    b = base("health")
    rows = [
        {"run_id": "r1", "selected_source": "canonical", "interpretation_basis": "explicit", "alignment_state": "aligned",
         "primary_blocker": "reclaim_wait", "final_decision": "NOOP", "reason": "줄1\n" + "x" * 120,
         "policy_aware_gating": {"applied": True, "candidate": True, "rejection_reasons": ["min_hold", "", 3]},
         "chart_structure_decision_hint": {"available": True, "hint": "pullback"}, "policy_source": "explicit"},
        {"run_id": "r2", "policy_aware_gating": "bad", "final_decision": "BUY", "selected_source": None, "reason": "y" * 93},
        {"run_id": "r2b", "reason": "z" * 90},
        {},
    ]
    sources = [dict(r, policy_source_inspection={"selected_source": "canonical", "fields_present": ["min_hold"],
                                                 "explicit_fields_used": ["min_hold", 5]}) for r in rows]
    cases = {
        "_build_policy_aware_gating_deadness": [((rows,), {}), (([],), {})],
        "_build_policy_source_summary": [((sources,), {}), (([],), {})],
        "_compact_run_view": [((r,), {}) for r in rows],
        "_build_suspicious_flags": [((), dict(final_decision=d, alignment_summary=a, trace=t, gating=g))
                                    for d, a, t, g in [("NOOP", {"primary_blocker": "reclaim_wait", "alignment_state": "MISALIGNED"}, {"x": 1}, {"applied": True}),
                                                       ("buy", {}, {}, {}), ("", {"alignment_state": "aligned"}, {"grouped": []}, {"candidate": True})]],
        "_render_text_table": [((rows,), {}), (([],), {})],
        "_render_compact_run_table": [(([b._compact_run_view(r) for r in rows],), {}), (([],), {})],
        "_render_reclaim_table": [((rows,), {}), (([],), {})],
        "render_policy_surface_quality_summary_text": [(("2026-05-11", {"schema_available_rate": "0.5", "issues": ["i"]}), {}),
                                                       (("2026-05-11", None), {})],
        "render_chart_structure_decision_hint_summary_text": [(("2026-05-11", {"available_run_count": 3, "top": [1]}), {}),
                                                               (("2026-05-11", "bad"), {})],
    }
    ok = 0
    for name, arglist in cases.items():
        for args, kw in arglist:
            got = _outcome(getattr(health_cur, name), *copy.deepcopy(args), **copy.deepcopy(kw))
            assert got == _outcome(getattr(b, name), *copy.deepcopy(args), **copy.deepcopy(kw)), (name, args, kw)
            ok += got[0] == "ok"
    assert ok >= 18  # non-vacuous: almost every case must produce real output, not a shared exception
