"""P1.5 DEV-A Q8: BASE (d7ab8294) vs current parity for the quant-shadow forward readout and Markdown render.

The frozen BASE facade is exec'd from Git beside the live one. Moved functions are compared directly and through
``build_quant_shadow_candidate_evaluation`` + ``render_quant_shadow_candidate_evaluation_lines`` (the forward-outcome
attachment is replaced by the same identity function on both so nothing reads ``data/state.json``). Seam tests patch one
facade attribute identically on both modules; mutation tests break the new owners and must be detected.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import types
from pathlib import Path

import pytest

import libs.reporting.evaluation.quant_shadow_forward_readout_p15 as fwd_owner
import libs.reporting.evaluation.quant_shadow_render_p15 as render_owner
import libs.reporting.quant_shadow_candidate_evaluation as cur

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
PATH = "libs/reporting/quant_shadow_candidate_evaluation.py"
_BASE: dict = {}


def base():
    if "mod" not in _BASE:
        src = subprocess.check_output(["git", "show", f"{BASE_SHA}:{PATH}"], cwd=ROOT).decode("utf-8")
        mod = types.ModuleType("_p15_qsce_base_d7ab8294")
        mod.__file__ = str(ROOT / PATH)
        sys.modules[mod.__name__] = mod
        exec(compile(src, f"<base:{PATH}>", "exec"), mod.__dict__)
        _BASE["mod"] = mod
    return _BASE["mod"]


def _cp(ret=None, mfe=None, mae=None, status="observed"):
    return {"status": status, "return_pct": ret, "mfe_pct": mfe, "mae_pct": mae}


def _row(day, lane, *, ret5=None, ret15=None, ret3=None, ret60=None, mfe5=None, mae5=None, avail=True, symbol="005930",
         subtype="s1", rail="risk_on", bucket="open", reason="breakout_not_ready", role="top_pick"):
    checkpoints = {}
    for key, value in (("+3m", ret3), ("+5m", ret5), ("+15m", ret15), ("+60m", ret60)):
        if value is not None:
            checkpoints[key] = _cp(value, mfe5 if key == "+5m" else None, mae5 if key == "+5m" else None)
    return {
        "symbol": symbol, "reason": reason, "shadow_role": role, "generated_at": f"{day[:4]}-{day[4:6]}-{day[6:]}T09:00:00",
        "entry_lane_observation": {"primary_lane": lane, "subtype": subtype, "subtype_v2": subtype + "_v2",
                                   "time_bucket": bucket, "market_regime_rail": rail},
        "shadow_forward_base": {"available": True, "baseline_epoch": 1780358400 + len(symbol) * 60, "baseline_price": 100.0},
        "shadow_forward_outcome": {"available": avail, "checkpoints": checkpoints},
    }


TYPICAL = [
    _row("20260601", "vwap_reclaim", ret5=0.5, ret15=0.8, ret3=0.2, mfe5=1.2, mae5=-0.4, symbol="A1"),
    _row("20260601", "vwap_reclaim", ret5=0.3, ret15=-0.1, mfe5=0.9, mae5=-0.9, symbol="A2"),
    _row("20260602", "vwap_reclaim", ret5=-0.4, ret15=-0.2, ret60=0.7, symbol="A3", subtype="s2"),
    _row("20260602", "squeeze", ret5=1.5, ret15=2.0, mfe5=3.0, mae5=-0.1, symbol="B1", rail="risk_off"),
    _row("20260602", "squeeze", avail=False, symbol="B2"),
    _row("20260603", "pullback", ret5=0.5, ret15=0.8, symbol="C1", bucket="close"),
    _row("20260603", "pullback", ret5=0.5, ret15=0.8, symbol="C2", bucket="close"),  # exact tie with C1
]
MALFORMED = [
    {"shadow_forward_outcome": "x"},
    {},
    {"shadow_forward_outcome": {"available": "yes", "checkpoints": {
        "+5m": {"status": " Observed ", "return_pct": "abc"}, "+15m": "junk", "+3m": _cp("1.5%"), "EOD": _cp(0.1)}}},
    {"generated_at": "2026-06-01", "shadow_forward_outcome": {"available": True, "checkpoints": {
        "+5m": _cp(None, ""), "+60m": _cp(True), "+30m": _cp(0.25, status="pending")}}},
    {"generated_at": "bad", "entry_lane_observation": {"primary_lane": None, "subtype": "", "time_bucket": "한글"},
     "shadow_forward_outcome": {"available": 1, "checkpoints": {"+5m": _cp(2)}}},
]
ROW_CASES = {"empty": [], "typical": TYPICAL, "malformed": MALFORMED, "single": TYPICAL[:1]}


def _outcome(fn):
    try:
        return ("ok", json.dumps(fn(), ensure_ascii=False, default=repr))
    except Exception as exc:  # noqa: BLE001
        return ("exc", type(exc).__name__, str(exc))


def _groups(rows):
    groups = {}
    for row in rows:
        lane = (row.get("entry_lane_observation") or {}).get("primary_lane") if isinstance(row.get("entry_lane_observation"), dict) else None
        groups.setdefault(str(lane), []).append(row)
    return groups


@pytest.mark.parametrize("case", sorted(ROW_CASES))
def test_forward_readout_functions_match_base(case):
    rows = ROW_CASES[case]
    for fn_name, args, kwargs in [
        ("_forward_outcome_summary", (rows,), {}),
        ("_entry_lane_forward_outcomes", (rows,), {}),
        ("_top_forward_groups", (_groups(rows),), {}),
        ("_top_forward_groups", (_groups(rows),), {"limit": 1}),
        ("_top_forward_groups", (_groups(rows),), {"limit": 0}),
        ("_top_forward_groups", (_groups(rows),), {"limit": -1}),
        ("_checkpoint_value", (rows[0] if rows else {}, "+5m", "return_pct"), {}),
        ("_checkpoint_value", (rows[-1] if rows else {}, "+5m", "mfe_pct"), {}),
        ("_checkpoint_value", (rows[-1] if rows else {}, "EOD", "return_pct"), {}),
        ("_mean", ([1, None, "2", 0.5],), {}),
        ("_mean", ([None],), {}),
    ]:
        expected = _outcome(lambda: getattr(base(), fn_name)(*copy.deepcopy(args), **kwargs))
        assert _outcome(lambda: getattr(cur, fn_name)(*copy.deepcopy(args), **kwargs)) == expected, (fn_name, kwargs)


def test_typical_case_exercises_ranking_ties_and_horizon_coverage():
    summary = cur._forward_outcome_summary(TYPICAL)
    assert summary["observed_count"] == 6 and summary["observed_count_5m"] == 6 and summary["observed_count_eod"] == 0
    top = cur._top_forward_groups(_groups(TYPICAL))
    assert [row["name"] for row in top] == ["squeeze", "pullback", "vwap_reclaim"]
    lanes = cur._entry_lane_forward_outcomes(TYPICAL)
    assert set(lanes) >= {"by_primary_lane", "by_lane_subtype_v2", "by_market_regime_rail"} and lanes["behavior_effect"] == "evaluation_only"


def _payload(rows):
    return {"generated_at": "2026-06-03T00:00:00", "candidates": copy.deepcopy(rows)}


def _install_identity_attach(monkeypatch, mod):
    monkeypatch.setattr(mod, "attach_forward_outcomes", lambda rows: [dict(row) for row in rows])


def _evaluation(mod, monkeypatch, rows):
    _install_identity_attach(monkeypatch, mod)
    return mod.build_quant_shadow_candidate_evaluation([_payload(rows)])


@pytest.mark.parametrize("case", ["typical", "malformed", "single"])
def test_full_evaluation_and_render_lines_match_base(monkeypatch, case):
    rows = [dict(r) for r in ROW_CASES[case] if isinstance(r, dict)]
    results = []
    for mod in (base(), cur):
        results.append(_outcome(lambda m=mod: (lambda ev: [ev, m.render_quant_shadow_candidate_evaluation_lines(ev)])(_evaluation(m, monkeypatch, rows))))
        monkeypatch.undo()
    assert results[0] == results[1]
    if case == "typical":
        lines = json.loads(results[1][1])[1]
        assert lines[1] == "## Quant Shadow Candidates" and any("Entry lane forward outcomes:" in line for line in lines)


RENDER_PAYLOADS = {
    "none": None,
    "empty": {},
    "zero_candidates": {"candidate_count": 0, "by_role": [{"name": "x", "count": 1}]},
    "minimal": {"candidate_count": 2},
    "sections": {
        "candidate_count": 5, "deduped_candidate_count": 4, "duplicate_candidate_count": 1, "payload_count": 2,
        "evaluated_count": 3, "forward_base_coverage": "0.5", "forward_outcome_coverage": 0.256,
        "by_role": [{"name": "한글", "count": 3}, {"name": "-", "count": 9}, {"name": "b"}],
        "evaluation_trust_gate": {"status": "blocked", "promotion_allowed": 0, "reasons": ["a", 2],
                                  "promotion_ready_candidates": [{"name": "c", "observed_count": 3, "candidate_count": 9,
                                                                  "avg_return_5m_pct": 0.5, "review_state": "promotion_watch"}]},
        "shadow_readiness": {"status": "ready", "evaluated_count": 3}, "promotion_candidate": {"candidate": "cost_edge",
                             "promotion_state": "candidate_review", "counts": {"cost_edge": 3}},
        "no_trade_scorecard": {"status": "ok", "correctly_blocked_signals": [{"name": "g", "avg_return_5m_pct": -0.2, "avg_mae_5m_pct": -1}],
                                "missed_opportunity_candidates": [{"name": "m", "avg_return_5m_pct": None}], "promotion_watchlist": []},
        "opening_momentum_probe": {"would_enter_count": 1, "zero_would_enter_explanation": "none today"},
        "opening_largecap_surge": {"candidate_count": 2, "zero_would_enter_explanation": "x"},
        "entry_shape_diagnostics": {"by_shape": [{"name": "s", "count": 1}]},
        "entry_lane_observation": {"candidate_count": 2, "by_primary_lane": [{"name": "l", "count": 2}]},
        "entry_lane_forward_outcomes": {"by_primary_lane": [{"name": "l", "observed_count": 2, "candidate_count": 3, "avg_return_5m_pct": "0.1",
                                                              "avg_return_15m_pct": 0.2, "avg_mfe_5m_pct": 0.3, "avg_mae_5m_pct": -0.4}]},
        "below_vwap_reclaim_observation": {"candidate_count": 1, "by_subtype": [{"name": "d", "count": 1}]},
    },
    "bad_number": {"candidate_count": 1, "forward_base_coverage": "abc"},
    "bad_forward_row": {"candidate_count": 1, "entry_lane_forward_outcomes": {"by_primary_lane": [{"name": "l", "avg_return_5m_pct": "x"}]}},
    "non_mapping_sections": {"candidate_count": 1, "evaluation_trust_gate": "x", "no_trade_scorecard": [], "entry_lane_observation": 3},
}


@pytest.mark.parametrize("name", sorted(RENDER_PAYLOADS))
def test_render_lines_match_base_including_exceptions(name):
    payload = RENDER_PAYLOADS[name]
    args = (copy.deepcopy(payload),)
    assert _outcome(lambda: cur.render_quant_shadow_candidate_evaluation_lines(*args)) == _outcome(
        lambda: base().render_quant_shadow_candidate_evaluation_lines(*args))


@pytest.mark.parametrize("fn_name", ["_format_rows", "_format_forward_rows", "_format_scorecard_rows"])
def test_row_formatters_match_base(fn_name):
    rows = [{"name": "a", "count": 2, "observed_count": "3", "candidate_count": None, "avg_return_5m_pct": 0.123456, "review_state": "w",
             "avg_mfe_5m_pct": 1, "avg_mae_5m_pct": -1}, {"name": ""}, {"name": "b", "avg_return_5m_pct": "bad"}, {}, {"name": "c"}]
    for limit in (None, 0, 1, 2, 10):
        kwargs = {} if limit is None else {"limit": limit}
        assert _outcome(lambda: getattr(cur, fn_name)(rows, **kwargs)) == _outcome(lambda: getattr(base(), fn_name)(rows, **kwargs))
    assert _outcome(lambda: getattr(cur, fn_name)([])) == ("ok", json.dumps("none"))


# --- facade monkeypatch seams: the same patch on BASE and current must give the same output, different from unpatched ---

SEAMS = [
    ("_text", lambda mod: (lambda value, o=mod._text: o(value).upper())),
    ("_bool", lambda mod: (lambda value: False)),
    ("_forward_outcome", lambda mod: (lambda row: {})),
    ("_candidate_day", lambda mod: (lambda row: "20990101")),
    ("_entry_lane_observation", lambda mod: (lambda row: {"primary_lane": "patched", "subtype": "p"})),
    ("_mean", lambda mod: (lambda values: 42.0)),
    ("_checkpoint_value", lambda mod: (lambda row, checkpoint, metric: 1.0)),
    ("_forward_outcome_summary", lambda mod: (lambda rows: {"observed_count": len(rows), "patched": True})),
    ("_top_forward_groups", lambda mod: (lambda groups, *, limit=10: [{"name": "patched", "limit": limit}])),
    ("_entry_lane_forward_outcomes", lambda mod: (lambda candidates: {"patched": len(candidates)})),
    ("_format_rows", lambda mod: (lambda rows, *, limit=4: "ROWS")),
    ("_format_forward_rows", lambda mod: (lambda rows, *, limit=4: "FWD")),
    ("_format_scorecard_rows", lambda mod: (lambda rows, *, limit=4: "SCORE")),
]


def _run_all(mod, monkeypatch):
    evaluation = _evaluation(mod, monkeypatch, [dict(r) for r in TYPICAL])
    return json.dumps([evaluation, mod.render_quant_shadow_candidate_evaluation_lines(evaluation),
                       mod.render_quant_shadow_candidate_evaluation_lines(RENDER_PAYLOADS["sections"])], ensure_ascii=False, default=repr)


@pytest.mark.parametrize("name,factory", SEAMS, ids=[n for n, _ in SEAMS])
def test_facade_monkeypatch_seams_match_base(monkeypatch, name, factory):
    unpatched = _run_all(cur, monkeypatch)
    monkeypatch.undo()
    outputs = []
    for mod in (base(), cur):
        monkeypatch.setattr(mod, name, factory(mod))
        outputs.append(_run_all(mod, monkeypatch))
        monkeypatch.undo()
    assert outputs[1] == outputs[0] and outputs[1] != unpatched


# --- mutation checks: breaking an owner must break parity (the comparison is not vacuous) ---------------------------


@pytest.mark.parametrize(
    "owner,name,mutant",
    [
        (fwd_owner, "_top_forward_groups_impl", lambda groups, *, limit=10, facade: sorted(
            ({**facade._forward_outcome_summary(rows), "name": name} for name, rows in groups.items()), key=lambda s: s["name"])[:limit]),
        (fwd_owner, "_checkpoint_value_impl", lambda row, checkpoint, metric, *, facade: 0.0),
        (fwd_owner, "_entry_lane_forward_outcomes_impl", lambda candidates, *, facade: {"behavior_effect": "trading"}),
        (fwd_owner, "_forward_outcome_summary_impl", lambda rows, *, facade: {"candidate_count": 0}),
        (render_owner, "_format_forward_rows_impl", lambda rows, *, limit=4, facade: "x"),
        (render_owner, "_format_scorecard_rows_impl", lambda rows, *, limit=4, facade: "x"),
        (render_owner, "_format_rows_impl", lambda rows, *, limit=4, facade: "x"),
        (render_owner, "render_quant_shadow_candidate_evaluation_lines_impl", lambda payload, *, facade: []),
    ],
)
def test_owner_mutants_are_detected(monkeypatch, owner, name, mutant):
    expected = _run_all(base(), monkeypatch)
    monkeypatch.undo()
    assert _run_all(cur, monkeypatch) == expected  # green baseline first
    monkeypatch.undo()
    monkeypatch.setattr(owner, name, mutant)
    assert _run_all(cur, monkeypatch) != expected
