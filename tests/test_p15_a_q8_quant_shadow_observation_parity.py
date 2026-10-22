"""P1.5 DEV-A Q8 (wave A-W1): BASE (d7ab8294) vs current parity for the entry-shape / below-VWAP / entry-lane projections.

The frozen BASE facade is exec'd from Git beside the live one; both receive the same rows. Direct calls, the full
``build_quant_shadow_candidate_evaluation`` sections (forward-outcome attachment replaced identically so nothing reads
``data/state.json``), facade monkeypatch seams and owner mutants are compared. Ownership/import/AST boundaries for the new
owner live in ``test_p15_a_q8_quant_shadow_readout_boundaries.py``.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import types
from pathlib import Path

import pytest

import libs.reporting.evaluation.quant_shadow_observation_projection_p15 as owner
import libs.reporting.quant_shadow_candidate_evaluation as cur

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
PATH = "libs/reporting/quant_shadow_candidate_evaluation.py"
_BASE: dict = {}


def base():
    if "mod" not in _BASE:
        src = subprocess.check_output(["git", "show", f"{BASE_SHA}:{PATH}"], cwd=ROOT).decode("utf-8")
        mod = types.ModuleType("_p15_qsce_obs_base_d7ab8294")
        mod.__file__ = str(ROOT / PATH)
        sys.modules[mod.__name__] = mod
        exec(compile(src, f"<base:{PATH}>", "exec"), mod.__dict__)
        _BASE["mod"] = mod
    return _BASE["mod"]


def _row(reason="", axis="", *, would=False, symbol="005930", **extra):
    row = {"symbol": symbol, "reason": reason, "primary_failure_axis": axis, "would_enter": would, "shadow_role": "top_pick",
           "generated_at": "2026-06-02T09:00:00", "shadow_forward_base": {"available": True, "baseline_epoch": 1780358400 + len(symbol), "baseline_price": 100.0}}
    row.update(extra)
    return row


TYPICAL = [
    _row("pullback_not_mature", symbol="A1"),
    _row("pullback_below_vwap_reclaim_not_ready", symbol="A2"),
    _row("below_vwap_reclaim_not_ready", symbol="A3", vwap_distance_pct=-1.2, vwap_reclaim_progress=0.3),
    _row("", "vwap_relationship", symbol="A4", factors={"vwap_reclaim_ok": True}),
    _row("breakout_not_ready", symbol="B1"),
    _row("breakout_above_recent_high_with_vwap_hold_and_volume_confirmation", symbol="B2"),
    _row("breakout_above_recent_high_with_vwap_structure_confirmation", would=True, symbol="B3"),
    _row("", "breakout_readiness", would=True, symbol="B4"),
    _row("volume_confirmation_missing", symbol="C1"),
    _row("volume_insufficient", symbol="C2"),
    _row("human_chart_sanity_guard_blocked", symbol="C3"),
    _row("", "human_chart_sanity", symbol="C4"),
    _row("something_else", symbol="D1"),
    _row("none", "unknown", symbol="D2"),
    # precomputed observation mappings take priority over the runtime classifiers
    _row("below_vwap_reclaim_not_ready", symbol="E1", below_vwap_reclaim_observation={"applies": True, "subtype": "pre", "subtype_v2": "pre_v2"}),
    _row("breakout_not_ready", symbol="E2", below_vwap_reclaim_observation={"applies": False},
         entry_lane_observation={"primary_lane": "vwap_reclaim", "subtype": "s", "subtype_v2": "", "time_bucket": "open",
                                 "market_regime": "bull", "market_regime_rail": "risk_on"}),
    _row("breakout_not_ready", symbol="E3", entry_lane_observation={"primary_lane": None, "time_bucket": "한글|pipe"}),
]
MALFORMED = [_row("pullback_not_mature", below_vwap_reclaim_observation="x", entry_lane_observation=["y"]), {}, {"reason": None},
             {"reason": "breakout_not_ready", "would_enter": "yes"}, {"reason": 5, "primary_failure_axis": 7, "would_enter": "off"}]
CASES = {"empty": [], "typical": TYPICAL, "malformed": MALFORMED, "mixed": TYPICAL + MALFORMED}
FUNCS = ["_entry_shape_payload", "_below_vwap_reclaim_observation_payload", "_entry_lane_observation_payload"]


def _outcome(fn):
    try:
        return ("ok", json.dumps(fn(), ensure_ascii=False, default=repr))
    except Exception as exc:  # noqa: BLE001
        return ("exc", type(exc).__name__, str(exc))


@pytest.mark.parametrize("case", sorted(CASES))
def test_payload_projections_match_base(case):
    rows = CASES[case]
    for name in FUNCS:
        expected = _outcome(lambda: getattr(base(), name)(copy.deepcopy(rows)))
        assert _outcome(lambda: getattr(cur, name)(copy.deepcopy(rows))) == expected, name


def test_row_helpers_match_base_for_every_row():
    for row in TYPICAL + MALFORMED:
        for name in ("_entry_shape", "_below_vwap_reclaim_observation", "_entry_lane_observation"):
            assert _outcome(lambda: getattr(cur, name)(copy.deepcopy(row))) == _outcome(lambda: getattr(base(), name)(copy.deepcopy(row))), name


def test_typical_case_exercises_every_shape_branch_and_tie_order():
    shapes = {cur._entry_shape(row) for row in TYPICAL}
    assert shapes == {"pullback", "vwap_reclaim", "breakout", "volume_confirmation", "human_chart_sanity", "other"}
    payload = cur._entry_shape_payload(TYPICAL)
    # literals taken from the BASE (d7ab8294) facade output for these rows, not from the code under test
    assert payload["behavior_effect"] == "diagnostic_only" and payload["breakout_ready_like_count"] == 3
    assert payload["pullback_or_vwap_blocked_count"] == 5 and payload["breakout_not_ready_count"] == 4
    assert [(r["name"], r["count"]) for r in payload["by_shape"]] == [
        ("breakout", 6), ("vwap_reclaim", 3), ("pullback", 2), ("volume_confirmation", 2), ("human_chart_sanity", 2), ("other", 2)]
    lane = cur._entry_lane_observation_payload(TYPICAL)
    assert lane["behavior_effect"] == "observation_only" and lane["candidate_count"] == len(TYPICAL) == 17
    assert cur._below_vwap_reclaim_observation_payload(TYPICAL)["candidate_count"] == 4


def _install_identity_attach(monkeypatch, mod):
    monkeypatch.setattr(mod, "attach_forward_outcomes", lambda rows: [dict(row) for row in rows])


def _sections(mod, monkeypatch, rows):
    _install_identity_attach(monkeypatch, mod)
    evaluation = mod.build_quant_shadow_candidate_evaluation([{"generated_at": "2026-06-02T00:00:00", "candidates": copy.deepcopy(rows)}])
    return json.dumps({k: evaluation.get(k) for k in ("entry_shape_diagnostics", "below_vwap_reclaim_observation",
                                                       "entry_lane_observation", "entry_lane_forward_outcomes", "candidate_count")},
                      ensure_ascii=False, default=repr)


@pytest.mark.parametrize("case", ["typical", "mixed"])
def test_build_sections_match_base(monkeypatch, case):
    outputs = []
    for mod in (base(), cur):
        outputs.append(_outcome(lambda m=mod: _sections(m, monkeypatch, CASES[case])))
        monkeypatch.undo()
    assert outputs[0] == outputs[1] and outputs[1][0] == "ok"


# --- facade monkeypatch seams: the same patch on BASE and current must give the same output, different from unpatched ---

SEAMS = [
    ("_text", lambda mod: (lambda value, o=mod._text: o(value).upper())),
    ("_bool", lambda mod: (lambda value: False)),
    ("_top_counter", lambda mod: (lambda counter, *, limit=8: [{"name": "patched", "count": limit}])),
    ("_entry_shape", lambda mod: (lambda row: "other")),
    ("_below_vwap_reclaim_observation", lambda mod: (lambda row: {"applies": True, "subtype": "p", "subtype_v2": "q"})),
    ("classify_below_vwap_reclaim_observation", lambda mod: (lambda row: {"applies": True, "subtype": "cls", "subtype_v2": "cls2"})),
    ("_entry_lane_observation", lambda mod: (lambda row: {"primary_lane": "patched", "subtype": "p"})),
    ("build_entry_lane_observation", lambda mod: (lambda row: {"primary_lane": "built", "subtype": "b", "time_bucket": "t"})),
    ("_entry_shape_payload", lambda mod: (lambda candidates: {"patched": len(candidates)})),
    ("_below_vwap_reclaim_observation_payload", lambda mod: (lambda candidates: {"patched": len(candidates)})),
    ("_entry_lane_observation_payload", lambda mod: (lambda candidates: {"patched": len(candidates)})),
]


@pytest.mark.parametrize("name,factory", SEAMS, ids=[n for n, _ in SEAMS])
def test_facade_monkeypatch_seams_match_base(monkeypatch, name, factory):
    rows = TYPICAL
    unpatched = _sections(cur, monkeypatch, rows)
    monkeypatch.undo()
    outputs = []
    for mod in (base(), cur):
        monkeypatch.setattr(mod, name, factory(mod))
        outputs.append(_sections(mod, monkeypatch, rows))
        monkeypatch.undo()
    assert outputs[1] == outputs[0] and outputs[1] != unpatched


# --- mutation checks: breaking an owner must break parity (the comparison is not vacuous) ---------------------------


@pytest.mark.parametrize(
    "name,mutant",
    [
        ("_entry_shape_impl", lambda row, *, facade: "other"),
        ("_entry_shape_payload_impl", lambda candidates, *, facade: {"behavior_effect": "diagnostic_only"}),
        ("_below_vwap_reclaim_observation_impl", lambda row, *, facade: {"applies": False}),
        ("_below_vwap_reclaim_observation_payload_impl", lambda candidates, *, facade: {"behavior_effect": "trading"}),
        ("_entry_lane_observation_impl", lambda row, *, facade: {}),
        ("_entry_lane_observation_payload_impl", lambda candidates, *, facade: {"candidate_count": 0}),
    ],
)
def test_owner_mutants_are_detected(monkeypatch, name, mutant):
    expected = _sections(base(), monkeypatch, TYPICAL)
    monkeypatch.undo()
    assert _sections(cur, monkeypatch, TYPICAL) == expected  # green baseline first
    monkeypatch.undo()
    monkeypatch.setattr(owner, name, mutant)
    assert _sections(cur, monkeypatch, TYPICAL) != expected
