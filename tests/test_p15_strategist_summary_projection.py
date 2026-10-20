"""P1.5 BATCH04-A: Strategist LLM summary quality/readout + Markdown projection parity.

The frozen BASE ``strategist_llm_summary.py`` (``ead33ca7``) is exec'd as a separate module beside the current facade.
On identical synthetic temp artifacts: payload JSON bytes/order, Markdown bytes (Unicode/newlines), canonical and
strategist_input path resolution, clock substitution, external policy hooks, exceptions, late monkeypatch and the
effective (last-bound) renderer. No production files, live LLM or writes outside pytest temp directories.
"""
from __future__ import annotations

import ast
import copy
import json
import subprocess
import types
from pathlib import Path

import pytest

import libs.reporting.strategist_llm_summary as cur
import libs.reporting.strategist_llm_summary_markdown_projection as mdp
import libs.reporting.strategist_llm_summary_quality_projection as qp

ROOT = Path(__file__).resolve().parents[1]
BASE = "ead33ca78e7ee8eb17123fbd25bc129dbc042902"
PATH = "libs/reporting/strategist_llm_summary.py"
QUALITY = ("_headline_count_from_sample_map", "_directive", "_compact_operator_summary", "_memory_usage_from_canonical",
           "_news_usage_from_canonical", "_news_quality_audit", "_strategist_output_quality_audit",
           "_stage_decision_from_payload", "_first_text", "_operator_readout_clean", "_first_dict",
           "_strategy_detail_from_sources")
MARKDOWN = ("_json_inline", "_watch_scope_label_clean", "_strategy_patch_status_clean", "_playbook_flow_label",
            "_score_value", "_score_label", "_strategy_score_lines_clean", "_rejected_strategy_lines", "_bullet_lines",
            "_directive_line", "_memory_usage_lines_clean", "_news_usage_lines_clean", "_quality_audit_lines",
            "_render_stage_specific_summary_markdown_clean", "render_strategist_llm_summary_markdown")
NOW = "2026-10-20T00:00:00+00:00"


def _base_module():
    src = subprocess.check_output(["git", "show", f"{BASE}:{PATH}"], cwd=ROOT).decode("utf-8-sig")
    mod = types.ModuleType("strategist_llm_summary_base_ead33ca7")
    exec(compile(src, f"<base:{PATH}>", "exec"), mod.__dict__)
    return mod


@pytest.fixture()
def mods(monkeypatch):
    base = _base_module()
    for m in (base, cur):
        monkeypatch.setattr(m, "_utc_now_iso", lambda: NOW)
    return base, cur


def _w(path: Path, obj) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    return path


CANON_RICH = {
    "playbook": "breakout", "pre_llm_playbook": "defensive", "llm_requested_playbook": "breakout",
    "requested_playbook": "breakout", "requested_playbook_source": "llm", "final_playbook": "breakout",
    "tactical_strategy": "opening_range_breakout",
    "strategy_scores": {"opening_range_breakout": 0.82, "defensive_observe": 0.18, "bad": "x"},
    "rejected_strategy_reasons": {"defensive_observe": "risk_on tape supports active watch", "momentum": {"why": "중복"}},
    "candidate_watch_policy": {"behavior_effect": "visibility_only", "max_priority_rank": 7, "max_runner_ups": 4,
                               "cascade_enabled": True, "reason": "breakout tape supports rank expansion"},
    "memory_usage_trace": {"active_layers": ["daily", "weekly"], "priority_order": ["daily", "weekly", "monthly", "symbol"],
                           "human_summary": "Active memory layers: daily, weekly",
                           "applied_to_strategy": {"playbook_effect": "maintain_defensive", "risk_posture_effect": "defensive"},
                           "layer_decisions": {"daily": {"status": "ok", "active": True, "used": True,
                                                         "operator_summary": {"available": True, "trade_count": 3, "win_rate": 0.33}},
                                               "weekly": {"status": "missing", "active": False}}},
    "news_usage_trace": {"query_targets": ["휴대폰_RF부품", "코스피", ""], "human_summary": "News was used for context.",
                         "market_effect": "context only", "market_headlines_used": ["코스피 headline\n둘째 줄"],
                         "candidate_headlines_used": ["휴대폰 headline"],
                         "headline_sample_map": {"005930": ["a", "b"], "000660": "bad"}},
    "news_query_reasoning": "theme hints expanded queries",
    "market_regime": "risk_off", "market_regime_rail": {"rail": "risk_off", "score": -2},
    "news_event_intelligence": {"events": [{"title": "실적 발표", "impact": "high"}]},
}

RESP_MAIN = {"stage": "strategist", "provider": "OpenRouter", "model": "test-model", "status": "ok", "run_id": "run-1",
             "day": "2026-04-28", "saved_at": "2026-04-28T00:00:00+00:00", "repair_used": True,
             "response_text": json.dumps({
                 "playbook": "defensive", "selected_themes": [], "rationale": "defensive best 및 worst overlap",
                 "theme_strategy": {"selection_mode": "fallback", "fallback_reason": "available_themes empty"},
                 "strategy_adjustment_directives": {
                     "entry_policy_action": {"action": "tighten", "target_fields": ["volume_ratio_min"], "reason": "loss-heavy"},
                     "selected_symbol_bias_action": {"action": "none", "reason": "no memory"}},
                 "monitor_entry_policy": {"enabled": True, "volume_ratio_min": 0.75},
                 "risk_off_exception_conditions": ["반등 확인", ""],
                 "strategy_refresh_trace": {"summary": "refresh", "bullets": ["b1"], "stages": [{"s": 1}]},
                 "news_event_intelligence_usage": {"used": True}}, ensure_ascii=False)}


def _stage(kind, body):
    comp = {"selected_symbol_tactical_refresh": "strategist_stage2_selected_symbol",
            "stale_intraday_hold_review": "strategist_stage3_hold_review",
            "end_of_day_carry_review": "strategist_stage4_carry_review"}[kind]
    return {"status": "ok", "model": "m", "run_id": "c" * 32, "day": "2026-05-11", "stage_component": comp,
            "response_text": json.dumps(body, ensure_ascii=False)}


SCENARIOS = {
    "flat_fallback": ("flat", RESP_MAIN, None, None, None),
    "canonical_rich": ("llm", RESP_MAIN, CANON_RICH, None, None),
    "canonical_policy_given": ("llm", RESP_MAIN, {**CANON_RICH, "risk_off_exception_policy": {"allowed": False, "why": "주어짐"}}, None, None),
    "canonical_malformed": ("llm", RESP_MAIN, "{not json", None, None),
    "stage2_selected": ("category", _stage("selected_symbol_tactical_refresh", {
        "selected_symbol_decision": "keep", "target_symbol": "005930", "runner_up_order": ["000660"], "reason": "유지"}), CANON_RICH, None, None),
    "stage3_hold": ("category", _stage("stale_intraday_hold_review", {
        "hold_review_decision": "tighten_exit", "exit_pressure": "medium", "thesis_status": "weakened",
        "monitor_adjustment": {"tighten_stop": True, "next_check_minutes": 5},
        "priority_exit_triggers": ["vwap_breakdown", "time_decay"], "reason": "테제 약화"}),
        {"final_playbook": "pullback", "candidate_watch_policy": {"max_priority_rank": 5}}, None, None),
    "stage4_carry_meta_only": ("category", {**_stage("end_of_day_carry_review", {"carry_review_decision": "close"}),
                                            "stage_component": ""}, None, {"stage_component": "strategist_stage4_carry_review",
                                                                          "provider": "meta-provider", "llm_status": "fallback"}, None),
    "attempts_parsed": ("flat", {"status": "error", "attempts": [{"raw_response_text": "{bad"}, "junk",
                                                                  {"parsed_output": {"playbook": "trend", "selected_themes": ["2차전지"]}}]}, None, None, None),
    "response_text_invalid": ("flat", {"status": "ok", "response_text": "not json"}, None, None, None),
    "parsed_output_list_themes_none": ("flat", {"parsed_output": {"playbook": None, "selected_themes": None}}, None, "[1]", None),
    "trade_input_fallback": ("trade", RESP_MAIN, None, None, {"saved_at": "S", "run_id": "R", "source_input": CANON_RICH}),
    "trade_input_bad": ("trade", RESP_MAIN, None, None, "[]"),
}


def _layout(tmp: Path, name: str):
    kind, resp, canon, meta, trade_input = SCENARIOS[name]
    run = "c" * 32 if kind == "category" else "run-1"
    if kind == "flat":
        rp = tmp / name / "response.json"
    elif kind == "llm":
        rp = tmp / name / "reports" / "llm" / "2026-04-29" / run / "strategist" / "response.json"
    elif kind == "category":
        rp = tmp / name / "reports" / "llm" / "2026-05-11" / "trade_executed" / run / "stage" / "response.json"
    else:
        rp = tmp / name / "trade" / "reports" / "response.json"
    _w(rp, resp)
    if canon is not None:
        day = "2026-05-11" if kind == "category" else "2026-04-29"
        _w(tmp / name / "reports" / "canonical" / day / run / "strategist.json", canon)
    if meta is not None:
        _w(rp.with_name("meta.json"), meta)
    if trade_input is not None:
        _w(rp.parent.parent / "strategist_input.json", trade_input)
    return rp


def _both(mod, rp):
    try:
        payload = mod.build_strategist_llm_summary_payload(rp)
    except Exception as exc:  # noqa: BLE001
        return ("exc", type(exc).__name__, str(exc))
    return ("ok", json.dumps(payload, ensure_ascii=False, indent=2), mod.render_strategist_llm_summary_markdown(copy.deepcopy(payload)))


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_payload_and_markdown_bytes_match_base(name, mods, tmp_path):
    base, current = mods
    rp = _layout(tmp_path, name)
    assert _both(current, rp) == _both(base, rp)


def test_generate_writes_identical_files_to_temp_only(mods, tmp_path):
    base, current = mods
    rp = _layout(tmp_path, "canonical_rich")
    out = []
    for m in (base, current):
        md_path, js_path, payload = m.generate_strategist_llm_summary(rp)
        out.append((md_path.read_bytes(), js_path.read_bytes(), md_path, js_path, json.dumps(payload, ensure_ascii=False)))
    assert out[0] == out[1]
    assert {p.name for p in rp.parent.iterdir()} == {"response.json", "strategist_summary.md", "strategist_summary.json"}


def test_fixtures_reach_distinct_stages_and_readouts(mods, tmp_path):
    _base, current = mods
    heads, stages = set(), set()
    for name in SCENARIOS:
        r = _both(current, _layout(tmp_path, name))
        if r[0] == "ok":
            doc = json.loads(r[1])
            heads.add(doc["operator_readout"].get("headline"))
            stages.add(doc["llm_meta"]["call_kind"])
            assert r[2].endswith("\n") or r[2]
    assert {"selected_symbol_tactical_refresh", "stale_intraday_hold_review", "end_of_day_carry_review", ""} <= stages
    assert len(heads) >= 5


@pytest.mark.parametrize("bad", ["missing", "not-json", "list-root", "string-root"])
def test_read_failures_raise_identically(bad, mods, tmp_path):
    base, current = mods
    rp = tmp_path / "response.json"
    if bad != "missing":
        _w(rp, {"not-json": "{oops", "list-root": "[1, 2]", "string-root": '"text"'}[bad])
    assert _both(current, rp) == _both(base, rp)
    assert _both(current, rp)[0] == "exc"


def test_external_policy_clock_and_helper_call_order_match_base(mods, tmp_path, monkeypatch):
    base, current = mods
    rp = _layout(tmp_path, "canonical_rich")
    logs = []
    for m in (base, current):
        log = []
        for name in ("classify_market_regime_rail", "build_risk_off_exception_policy", "_utc_now_iso", "_first_text",
                     "_operator_readout_clean", "_directive", "_memory_usage_from_canonical", "_read_json",
                     "_stage_decision_from_payload", "_news_quality_audit", "_strategy_detail_from_sources"):
            real = getattr(m, name)
            monkeypatch.setattr(m, name, lambda *a, _n=name, _r=real, _l=log, **k: (_l.append(_n), _r(*a, **k))[1])
        _both(m, rp)
        logs.append(log)
    assert logs[0] == logs[1]
    assert "build_risk_off_exception_policy" in logs[1] and logs[1].index("_utc_now_iso") < logs[1].index("_operator_readout_clean")


def test_late_patch_of_facade_helpers_reaches_both_projections(mods, tmp_path, monkeypatch):
    base, current = mods
    rp = _layout(tmp_path, "canonical_rich")
    res = []
    for m in (base, current):
        monkeypatch.setattr(m, "_text", lambda v, d="-": ("«" + str(v) + "»") if v not in (None, "") else d)
        monkeypatch.setattr(m, "_score_label", lambda v: "PATCHED")
        monkeypatch.setattr(m, "build_risk_off_exception_policy", lambda **k: {"patched": sorted(k)})
        res.append(_both(m, rp))
    assert res[0] == res[1] and "PATCHED" in res[1][2] and '"patched"' in res[1][1]


def test_effective_renderer_binding_and_shadowed_definition_preserved():
    base_src = subprocess.check_output(["git", "show", f"{BASE}:{PATH}"], cwd=ROOT).decode("utf-8-sig")
    cur_src = (ROOT / PATH).read_text(encoding="utf-8-sig")
    bdefs = [n for n in ast.parse(base_src).body if isinstance(n, ast.FunctionDef)]
    cdefs = [n for n in ast.parse(cur_src).body if isinstance(n, ast.FunctionDef)]
    assert [n.name for n in bdefs] == [n.name for n in cdefs]  # same definition order incl. the duplicate renderer
    renders = [i for i, n in enumerate(cdefs) if n.name == "render_strategist_llm_summary_markdown"]
    assert len(renders) == 2
    assert ast.dump(cdefs[renders[0]]) == ast.dump(bdefs[renders[0]])  # shadowed legacy renderer untouched
    assert "_summary_markdown.render_strategist_llm_summary_markdown(" in ast.unparse(cdefs[renders[1]])
    assert cur.render_strategist_llm_summary_markdown.__code__.co_firstlineno == cdefs[renders[1]].lineno
    moved = set(QUALITY) | set(MARKDOWN)
    seen = set()
    for b, c in zip(bdefs, cdefs):
        assert ast.dump(c.args) == ast.dump(b.args) and ast.dump(c.returns) == ast.dump(b.returns), c.name
        if c.name in moved and not (c.name == "render_strategist_llm_summary_markdown" and c is cdefs[renders[0]]):
            assert len(c.body) == 1, c.name
            seen.add(c.name)
        elif c.name != "build_strategist_llm_summary_payload":
            assert ast.dump(c) == ast.dump(b), c.name
    assert seen == moved
    payload_src = ast.unparse(next(n for n in cdefs if n.name == "build_strategist_llm_summary_payload"))
    for kept in ("read_text(", "_read_json(", "_load_canonical_strategist(", "_market_rail_from_canonical(",
                 "build_risk_off_exception_policy(", "_utc_now_iso()"):
        assert kept in payload_src


def test_projections_are_effect_free_and_contain_exactly_the_moved_functions():
    for mod, names, allowed in ((qp, set(QUALITY) | {"assemble_summary_payload"}, {"__future__", "typing"}),
                                (mdp, set(MARKDOWN), {"__future__", "json", "typing"})):
        tree = ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))
        imports = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)} | \
            {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        assert imports == allowed
        assert {n.name for n in tree.body if isinstance(n, ast.FunctionDef)} == names
        attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        assert not attrs & {"read_text", "write_text", "open", "exists", "loads", "now", "_read_json",
                            "_load_canonical_strategist", "_utc_now_iso", "classify_market_regime_rail",
                            "build_risk_off_exception_policy", "_market_rail_from_canonical"}
        assert not [c for c in ast.walk(tree) if isinstance(c, ast.Constant) and isinstance(c.value, str) and "facade." in c.value]


def test_projection_callable_with_stub_facade():
    stub = types.SimpleNamespace(_as_dict=lambda v: dict(v) if isinstance(v, dict) else {},
                                 _as_list=lambda v: list(v) if isinstance(v, list) else [],
                                 _text=lambda v, d="-": str(v) if v not in (None, "") else d)
    base = _base_module()
    assert qp._first_text("x", None, "", "y", facade=stub) == base._first_text("x", None, "", "y")
    for items in ([], ["a", None, ""], [{"k": "v"}]):
        assert mdp._bullet_lines(items, facade=stub) == base._bullet_lines(items)


def _outcome(fn, *a, **k):
    try:
        return ("ok", json.dumps(fn(*a, **k), ensure_ascii=False, default=repr))
    except Exception as exc:  # noqa: BLE001
        return ("exc", type(exc).__name__, str(exc))


def test_news_quality_audit_boundary_grid_matches_base():
    base = _base_module()
    seen = set()
    for market in (0, 1, 2, "x"):
        for cand in (0, 1, None):
            for conf in ("", "low", "high", None):
                for effect in ("", "context only"):
                    usage = {"market_headline_count": market, "candidate_headline_count": cand, "confidence": conf,
                             "market_effect": effect, "query_targets": ["코스피"] if market else [], "human_summary": effect}
                    canon = {"news_evidence_ranked": {"candidate_news_ranked": ["c"] * (cand == 0), "market_news_ranked": []}}
                    got = _outcome(cur._news_quality_audit, canon, usage)
                    assert got == _outcome(base._news_quality_audit, canon, usage), usage
                    if got[0] == "ok":
                        seen.add(tuple(json.loads(got[1])["issues"]))
                    else:
                        seen.add(got[1])
    assert len(seen) >= 8


def test_output_quality_and_stage_decision_match_base_on_hostile_inputs(tmp_path):
    base = _base_module()
    for name in SCENARIOS:
        rp = _layout(tmp_path, name)
        try:
            raw = json.loads(rp.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if not isinstance(raw, dict):
            continue
        payload = base._parse_response_body(raw)
        _cp, canonical = base._load_canonical_strategist(rp)
        for p, r in ((payload, raw), ({}, {}), ({"hold_review_decision": None, "reason": 5}, {"stage_index": "x"})):
            for fn in ("_stage_decision_from_payload", "_strategy_detail_from_sources", "_operator_readout_clean"):
                args = {"_stage_decision_from_payload": (p, r, {}), "_strategy_detail_from_sources": (p, canonical),
                        "_operator_readout_clean": (p, base._stage_decision_from_payload(p, r, {}))}[fn]
                assert _outcome(getattr(cur, fn), *args) == _outcome(getattr(base, fn), *args), (name, fn)
            kw = dict(payload=p, canonical=canonical, stage_decision={}, strategy_detail={}, market_rail={"rail": "risk_off"},
                      news_quality={"status": "weak", "issues": ["news_headlines_missing"]})
            assert _outcome(cur._strategist_output_quality_audit, **kw) == _outcome(base._strategist_output_quality_audit, **kw)
