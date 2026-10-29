"""RF-033 C3: samsung q9_comparison role/representative/commander rules with candle recovery and outcome attach stubbed (tmp root only)."""
from __future__ import annotations

import json
import socket

import pytest

from libs.reporting.baseline_samsung_hynix import q9_comparison as qc

ROLES = qc.ROLES


@pytest.fixture(autouse=True)
def _deny(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network attempt")

    monkeypatch.setattr(socket.socket, "connect", boom)
    monkeypatch.setattr(socket, "create_connection", boom)


@pytest.fixture
def stubs(monkeypatch):
    st = {"candle_calls": [], "attached": None}

    def candles(rows, *, state_path, allow_fresh_fetch, run_id_prefix):
        st["candle_calls"].append({"n": len(rows), "state_path": state_path, "fresh": allow_fresh_fetch, "prefix": run_id_prefix})
        return {"CANDLES": []}

    def attach(rows, *, minute_rows_by_symbol):
        st["attached"] = minute_rows_by_symbol
        return rows

    monkeypatch.setattr(qc, "load_q9_forward_candles", candles)
    monkeypatch.setattr(qc, "attach_forward_outcomes", attach)
    return st


def cand(did, role, *, rank=1, ret=None, horizon="+30m", selected=False, decision=None, no_trade=False, status="observed"):
    c = {"q9_decision_id": did, "q9_decision_role": role, "rank": rank, "q9_selected": selected}
    if ret is not None:
        c["shadow_forward_outcome"] = {"checkpoints": {horizon: {"status": status, "return_pct": ret}}}
    if decision is not None:
        c["q9_commander_decision"] = decision
    if no_trade:
        c["q9_commander_no_trade"] = True
    return c


def write(root, day, name, rows, generated_at="2026-09-07T00:00:00Z"):
    p = root / day / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"generated_at": generated_at, "q9_decision_candidates": rows}), encoding="utf-8")


def window(did, **over):
    rows = [cand(did, "P_SCANNER_PRE_STRATEGIST_UNIVERSE", ret=1.0), cand(did, "A_SCANNER_CONTROL", ret=2.0),
            cand(did, "B_STRATEGIST_RANKED", ret=3.0, selected=True), cand(did, "C_COMMANDER_FINAL", ret=4.0, decision="approve")]
    return rows


def run(tmp_path, rows_by_file, baseline=None, cost=0.1, slip=0.05):
    for name, rows in rows_by_file.items():
        write(tmp_path, "2026-09-07", name, rows)
    return qc.build_q9_role_comparison(day="2026-09-07", baseline_summary=baseline or {}, cost_pct=cost, slippage_pct=slip, q9_root=tmp_path, state_path=tmp_path / "s.json")


def role(out, name, horizon="+30m"):
    return next(r for r in out["roles"] if r["role"] == name and r["horizon"] == horizon)


def test_load_rows_filters_files_roles_and_recovers_candles_with_fresh_fetch(tmp_path, stubs):
    write(tmp_path, "2026-09-07", "a.json", [cand("D1", "A_SCANNER_CONTROL"), cand("D1", "OTHER_ROLE"), "junk"])
    write(tmp_path, "2026-09-07", "latest.json", [cand("D9", "A_SCANNER_CONTROL")])
    (tmp_path / "2026-09-07" / "bad.json").write_text("{bad", encoding="utf-8")
    rows = qc._load_q9_rows(day="2026-09-07", root=tmp_path, state_path=tmp_path / "s.json")
    assert [r["q9_decision_id"] for r in rows] == ["D1"] and rows[0]["_payload_generated_at"] == "2026-09-07T00:00:00Z"
    assert stubs["candle_calls"] == [{"n": 1, "state_path": tmp_path / "s.json", "fresh": True, "prefix": "q9_comparison_forward_recovery"}]     # fresh fetch is hard-wired ON
    assert stubs["attached"] == {"CANDLES": []}
    assert qc._load_q9_rows(day="2026-01-01", root=tmp_path) == [] and len(stubs["candle_calls"]) == 1                                         # missing day: no recovery call


def test_only_complete_pabc_windows_are_comparable(tmp_path, stubs):
    rows = window("D1") + [cand("D2", "A_SCANNER_CONTROL", ret=9.0), cand("D2", "B_STRATEGIST_RANKED", ret=9.0)]
    out = run(tmp_path, {"a.json": rows})
    assert out["decision_window_count"] == 2 and out["comparable_complete_window_count"] == 1 and out["cohort_scope"] == "complete_pabc_decision_windows_only"
    assert role(out, "A_SCANNER_CONTROL")["q9_net"]["count"] == 1 and len(out["roles"]) == 4 * len(qc.HORIZONS)
    assert out["behavior_effect"] == "evaluation_only" and out["schema_version"] == "baseline_samsung_hynix_q9_comparison.v1"


def test_net_return_subtracts_cost_and_slippage_and_skips_unobserved(tmp_path, stubs):
    rows = window("D1")
    rows[1]["shadow_forward_outcome"]["checkpoints"]["+30m"]["return_pct"] = "bad"
    rows.append(cand("D2", "A_SCANNER_CONTROL", ret=5.0, status="pending"))
    out = run(tmp_path, {"a.json": rows})
    assert role(out, "P_SCANNER_PRE_STRATEGIST_UNIVERSE")["q9_net"]["average_return_pct"] == pytest.approx(0.85)
    assert role(out, "A_SCANNER_CONTROL")["q9_net"]["count"] == 0                      # non-numeric return skipped
    assert role(out, "P_SCANNER_PRE_STRATEGIST_UNIVERSE")["active_candidate_count"] == 1


def test_representative_is_selected_for_b_else_lowest_rank(tmp_path, stubs):
    d = "D1"
    rows = [cand(d, "P_SCANNER_PRE_STRATEGIST_UNIVERSE", rank=3, ret=30.0), cand(d, "P_SCANNER_PRE_STRATEGIST_UNIVERSE", rank=1, ret=10.0), cand(d, "P_SCANNER_PRE_STRATEGIST_UNIVERSE", rank=2, ret=20.0),
            cand(d, "A_SCANNER_CONTROL", rank=5, ret=1.0),
            cand(d, "B_STRATEGIST_RANKED", rank=1, ret=1.0), cand(d, "B_STRATEGIST_RANKED", rank=7, ret=77.0, selected=True),
            cand(d, "C_COMMANDER_FINAL", ret=2.0, decision="buy")]
    out = run(tmp_path, {"a.json": rows}, cost=0.0, slip=0.0)
    assert role(out, "P_SCANNER_PRE_STRATEGIST_UNIVERSE")["q9_net"]["average_return_pct"] == 10.0                # rank 1 wins
    assert role(out, "B_STRATEGIST_RANKED")["q9_net"]["average_return_pct"] == 77.0                          # selected beats rank
    no_sel = [dict(r, q9_selected=False) for r in rows]
    assert role(run(tmp_path / "n", {"a.json": no_sel}, cost=0.0, slip=0.0), "B_STRATEGIST_RANKED")["q9_net"]["average_return_pct"] == 1.0


def test_unparsable_rank_raises_valueerror_current_behavior(tmp_path, stubs):
    rows = window("D1") + [cand("D1", "A_SCANNER_CONTROL", rank="x", ret=1.0)]
    with pytest.raises(ValueError):
        run(tmp_path, {"a.json": rows})


@pytest.mark.parametrize("decision,no_trade,expected_value,cash,active", [
    ("approve", False, 3.85, 0, 1), ("approved", False, 3.85, 0, 1), ("allow", False, 3.85, 0, 1), ("BUY", False, 3.85, 0, 1),
    ("reject", False, 0.0, 1, 0), ("noop", False, 0.0, 1, 0), ("no_trade", False, 0.0, 1, 0), ("blocked", False, 0.0, 1, 0),
    ("approve", True, 0.0, 1, 0),                                  # explicit no_trade flag wins over an approve decision
])
def test_commander_policy_return_or_cash(tmp_path, stubs, decision, no_trade, expected_value, cash, active):
    rows = window("D1")[:3] + [cand("D1", "C_COMMANDER_FINAL", ret=4.0, decision=decision, no_trade=no_trade)]
    c = role(run(tmp_path, {"a.json": rows}), "C_COMMANDER_FINAL")
    assert c["q9_net"]["average_return_pct"] == pytest.approx(expected_value) and c["cash_no_trade_count"] == cash and c["active_candidate_count"] == active
    assert c["metric_semantics"] == "commander_policy_return_approved_candidate_else_cash_zero"
    assert sum(c["commander_decision_counts"].values()) == 1 and role(run(tmp_path / "x", {"a.json": rows}), "A_SCANNER_CONTROL")["metric_semantics"] == "representative_candidate_forward_return"


def test_unknown_commander_decision_is_excluded_from_values_but_counted(tmp_path, stubs):
    rows = window("D1")[:3] + [cand("D1", "C_COMMANDER_FINAL", ret=4.0, decision="maybe")]
    c = role(run(tmp_path, {"a.json": rows}), "C_COMMANDER_FINAL")
    assert c["q9_net"]["count"] == 0 and c["commander_decision_counts"] == {"maybe": 1} and c["active_candidate_count"] == 0
    rows = window("D1")[:3] + [cand("D1", "C_COMMANDER_FINAL", ret=4.0)]
    assert role(run(tmp_path / "e", {"a.json": rows}), "C_COMMANDER_FINAL")["commander_decision_counts"] == {"unknown": 1}


def test_baseline_gap_only_when_both_sides_have_samples(tmp_path, stubs):
    base = {"horizons": [{"horizon": "+30m", "top1_net": {"expectancy_pct": 1.0, "count": 5}}]}
    out = run(tmp_path, {"a.json": window("D1")}, baseline=base)
    a = role(out, "A_SCANNER_CONTROL")
    assert a["baseline_top1_count"] == 5 and a["baseline_top1_net_expectancy_pct"] == 1.0 and a["baseline_minus_q9_expectancy_pct"] == round(1.0 - a["q9_net"]["expectancy_pct"], 4)
    other = role(out, "A_SCANNER_CONTROL", "+5m")
    assert other["baseline_minus_q9_expectancy_pct"] is None and other["baseline_top1_count"] == 0                 # no baseline row for that horizon
    zero = role(run(tmp_path / "z", {"a.json": window("D1")}, baseline={"horizons": [{"horizon": "+30m", "top1_net": {"expectancy_pct": 1.0, "count": 0}}]}), "A_SCANNER_CONTROL")
    assert zero["baseline_minus_q9_expectancy_pct"] is None


def test_pending_checkpoint_inside_a_complete_window_is_not_counted(tmp_path, stubs):
    rows = window("D1")
    rows[1]["shadow_forward_outcome"]["checkpoints"]["+30m"]["status"] = "pending"
    out = run(tmp_path, {"a.json": rows})
    assert role(out, "A_SCANNER_CONTROL")["q9_net"]["count"] == 0 and role(out, "A_SCANNER_CONTROL")["active_candidate_count"] == 0
    assert role(out, "P_SCANNER_PRE_STRATEGIST_UNIVERSE")["q9_net"]["count"] == 1


def test_baseline_gap_is_none_when_q9_side_has_no_samples(tmp_path, stubs):
    rows = window("D1")
    rows[1]["shadow_forward_outcome"]["checkpoints"]["+30m"]["status"] = "pending"
    base = {"horizons": [{"horizon": "+30m", "top1_net": {"expectancy_pct": 1.0, "count": 5}}]}
    a = role(run(tmp_path, {"a.json": rows}, baseline=base), "A_SCANNER_CONTROL")
    assert a["baseline_top1_count"] == 5 and a["q9_net"]["count"] == 0 and a["baseline_minus_q9_expectancy_pct"] is None
