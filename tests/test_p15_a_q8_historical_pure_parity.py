"""P1.5 DEV-A Q8: BASE (d7ab8294) vs current parity for the three Q8 post-hoc evaluation facades.

Each frozen BASE facade is exec'd from Git beside the live facade and both are driven over the same
synthetic reports tree (temp dirs only). Payloads, written JSON/Markdown bytes (BOM, newlines),
exceptions and the full ``pathlib.Path`` read/exists/glob/mkdir/write sequence are compared. Mutation
tests patch the new pure owners and prove the comparison is not vacuous.
"""
from __future__ import annotations

import json
import subprocess
import sys
import types
from pathlib import Path

import pytest

import libs.reporting.evaluation.q8_historical_aggregation_p15 as agg_owner
import libs.reporting.evaluation.q8_shadow_readout_p15 as readout_owner
import libs.reporting.q8_historical_review as hist_cur
import libs.reporting.q8_lane_decision_table as lane_cur
import libs.reporting.q8_shadow_blocker_review as shadow_cur

ROOT = Path(__file__).resolve().parents[1]
BASE = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
FACADES = {
    "hist": ("libs/reporting/q8_historical_review.py", hist_cur),
    "shadow": ("libs/reporting/q8_shadow_blocker_review.py", shadow_cur),
    "lane": ("libs/reporting/q8_lane_decision_table.py", lane_cur),
}
_BASE_CACHE: dict = {}


def base(key):
    if key not in _BASE_CACHE:
        path = FACADES[key][0]
        src = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT).decode("utf-8")
        name = f"_p15_q8_base_{key}_d7ab8294"
        mod = types.ModuleType(name)
        mod.__file__ = str(ROOT / path)
        sys.modules[name] = mod
        exec(compile(src, f"<base:{path}>", "exec"), mod.__dict__)
        _BASE_CACHE[key] = mod
    return _BASE_CACHE[key]


def _dump(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _shadow_section(day_index: int, *, v2: bool, allowed: bool) -> dict:
    lane_rows = [
        {"name": "vwap_reclaim:true_below_vwap_failure", "candidate_count": 40 + day_index, "observed_count": 35,
         "observed_count_5m": 33, "observed_count_15m": 30, "observed_day_count_5m": 1,
         "avg_return_5m_pct": "0.42", "avg_return_15m_pct": 0.31, "avg_mfe_5m_pct": "1,2", "avg_mae_5m_pct": -0.2},
        {"name": "vwap_reclaim:shallow", "candidate_count": 40 + day_index, "observed_count": 12,
         "avg_return_5m_pct": -0.3, "avg_return_60m_pct": 0.9},
        {"name": "breakout:other", "candidate_count": 99},
        "not-a-row",
    ]
    if day_index == 2:  # legacy day: horizon counts absent, odd number formats
        lane_rows[0] = {"name": "vwap_reclaim:true_below_vwap_failure", "candidate_count": "7", "observed_count": "x"}
    return {
        "candidate_count": 50 + day_index,
        "deduped_candidate_count": 45,
        "duplicate_candidate_count": 5,
        "evaluated_count": 44,
        "would_enter_count": day_index,
        "forward_outcome_coverage": "0.8",
        "evaluation_trust_gate": {"status": "pass" if allowed else "blocked", "promotion_allowed": allowed,
                                  "trusted_forward_count": 30, "trusted_forward_coverage": 0.71, "duplicate_rate": 0.1},
        # tie counts on purpose: most_common ordering depends on insertion order
        "by_reason": [{"name": "breakout_not_ready", "count": 3}, {"name": "volume_confirmation_missing", "count": 3},
                      {"name": "", "count": 9}, {"name": "none", "count": 2}, 7],
        "by_role": [{"name": "top_pick", "count": "2"}, {"name": "runner_up", "count": 2}],
        "by_tactic_id": [{"name": "vwap_reclaim_pullback", "count": 1}],
        "below_vwap_reclaim_observation": {
            "by_subtype": [{"name": "shallow", "count": 4}, {"name": "deep", "count": 4}],
            "by_subtype_v2": [{"name": "v2_a", "count": 1}] if v2 else [],
        },
        "entry_lane_forward_outcomes": {"by_lane_subtype": lane_rows},
    }


def _build_reports(tmp: Path, *, v2: bool = True, allowed_day: int | None = 1) -> Path:
    reports = tmp / "reports"
    days = ["2026-06-01", "2026-06-02", "2026-06-03", "2026-06-05"]
    for index, day in enumerate(days):
        if index == 3:
            continue  # missing day file inside the window
        payload = {
            "metrics": {"trade_count": "3", "closed_trade_count": 2, "return_sample_count": 2, "unavailable_return_count": 1,
                        "win_rate": "0.5", "avg_return_pct": "-0.25%", "truth_surface_count": 2},
            "quant_shadow_candidate_evaluation": _shadow_section(index, v2=v2, allowed=index == allowed_day),
            "market_regime_rail_review": {"rail_id": "risk_off" if index else ""},
            "q8_shadow_blocker_review": {"groups": [
                {"reason": "breakout_not_ready", "candidate_count": 10 + index, "observed_count": 8,
                 "avg_latest_return_pct": 0.5, "avg_max_favorable_pct": "1.5", "avg_max_adverse_pct": -0.7,
                 "positive_latest_count": 5, "missed_opportunity_count": 2, "adverse_count": 1, "decision": "adjust_and_retest"},
                {"name": "below_vwap_reclaim_not_ready", "count": 10 + index, "observed_review_candidate_count": 3,
                 "avg_latest_return_pct": -0.1},
                {"reason": "", "candidate_count": 4},
                "bad",
            ] if index != 1 else []},
            "pattern_performance": {
                "strategist": {"by_tactical_strategy": [
                    {"name": "defensive_observe", "count": 3, "win_count": 0, "loss_count": 3, "avg_return_pct": -0.8},
                    {"name": "momentum", "count": 3, "closed_or_realized_count": 3, "win_count": 2, "avg_return_pct": 0.8},
                    {"name": None, "count": 1, "avg_return_pct": "abc"},
                ]},
                "monitor_exit": {"by_exit_reason": [{"name": "stop", "count": 2, "loss_count": 2, "avg_return_pct": -1.1,
                                                     "cost_drag_loss_count": 1}]} if index else {},
            },
        }
        _dump(reports / "operator_summary" / "daily" / day / "daily_summary.json", payload)
    trades = [
        ("2026-06-01", "t1", {"pnl_pct": 0.012}, {"tactic_id": "momentum"}, {"entry_reason": "breakout", "exit_reason": "tp"}),
        ("2026-06-02", "t2", {"pnl_pct": "-0.02", "truth_source": "broker"}, {}, {"tactical_strategy": "defensive_observe"}),
        ("2026-06-02", "t3", {"pnl_pct": 3.5}, {"playbook": "pb"}, {"entry_trigger": "breakout", "exit_trigger": "stop"}),
        ("2026-06-03", "t4", {}, {}, {}),
        ("2026-07-01", "t5", {"pnl_pct": 0.5}, {}, {}),  # outside the window
    ]
    for day, trade_id, truth, quant, decision in trades:
        _dump(reports / "trades" / day / trade_id / "reports" / "ai_trade_summary.json",
              {"trade": {"trade_id": trade_id if trade_id != "t3" else "", "symbol": "005930", "status": "closed"},
               "truth_surface": truth, "quant_tactic": quant, "decision_flow": decision})
    (reports / "trades" / "2026-06-02" / "t6" / "reports").mkdir(parents=True)
    (reports / "trades" / "2026-06-02" / "t6" / "reports" / "ai_trade_summary.json").write_bytes(b"\xef\xbb\xbf{not json")
    logs = tmp / "data" / "logs" / "quant_shadow_candidates"
    for day, rows in (("2026-06-01", [{"reason": "below_vwap_reclaim_not_ready", "vwap_distance_pct": -1.4,
                                        "vwap_reclaim_progress": 0.2, "volume_ratio": 0.5},
                                       {"reason": "pullback_below_vwap_reclaim_not_ready", "vwap_distance_pct": -0.1,
                                        "factors": {"vwap_reclaim_ok": True, "volume_ok": True}},
                                       {"reason": "breakout_not_ready"}]),
                      ("2026-06-03", [{"primary_failure_axis": "vwap_relationship", "vwap_distance": "-3"}])):
        _dump(logs / day / "batch_01.json", {"candidates": rows + ["junk"]})
        _dump(logs / day / "latest.json", {"candidates": [{"reason": "below_vwap_reclaim_not_ready"}]})
    return reports


class _IoTrace:
    METHODS = ("read_text", "read_bytes", "write_text", "write_bytes", "exists", "mkdir", "glob")

    def __init__(self, monkeypatch, root: Path):
        self.calls = []
        self.root = root
        for name in self.METHODS:
            original = getattr(Path, name)
            monkeypatch.setattr(Path, name, self._wrap(name, original))

    def _wrap(self, name, original):
        trace = self

        def wrapper(path, *args, **kwargs):
            try:
                rel = str(Path(str(path)).relative_to(trace.root)).replace("\\", "/")
            except ValueError:
                rel = f"<outside>{path}"
            trace.calls.append((name, rel, args[:1] if name == "glob" else (), tuple(sorted(kwargs.items()))))
            return original(path, *args, **kwargs)

        return wrapper


def _run(tmp_path, monkeypatch, fn):
    trace = _IoTrace(monkeypatch, tmp_path)
    try:
        result = ("ok", fn())
    except Exception as exc:  # noqa: BLE001
        result = ("exc", type(exc).__name__, str(exc))
    monkeypatch.undo()
    written = {}
    for path in sorted(p for p in tmp_path.rglob("*") if p.is_file() and ("docs" in p.parts or "analysis" in p.parts)):
        written[str(path.relative_to(tmp_path)).replace("\\", "/")] = path.read_bytes()
    return result, trace.calls, written


def _relativize(result, tmp: Path):
    text = json.dumps(result, ensure_ascii=False, default=str)
    return json.loads(text.replace(json.dumps(str(tmp), ensure_ascii=False)[1:-1], "<TMP>"))


SCENARIOS = {
    "allowed_with_v2": dict(v2=True, allowed_day=1),
    "blocked_needs_candidate_fallback": dict(v2=False, allowed_day=None),
}


@pytest.mark.parametrize("scenario", sorted(SCENARIOS))
def test_historical_write_bytes_payload_and_io_sequence_match_base(tmp_path, monkeypatch, scenario):
    outcomes = []
    for label, mod in (("base", base("hist")), ("cur", hist_cur)):
        work = tmp_path / label
        reports = _build_reports(work, **SCENARIOS[scenario])
        docs = work / "docs" / "tactics"
        result, calls, written = _run(
            work, monkeypatch,
            lambda: mod.write_q8_historical_review(reports_root=reports, docs_root=docs, start="2026-06-01", end="2026-06-05"),
        )
        outcomes.append((_relativize(result, work), calls, written))
    (b_res, b_calls, b_files), (c_res, c_calls, c_files) = outcomes
    assert b_res[0] == "ok"
    assert c_res == b_res
    assert c_calls == b_calls
    assert c_files == b_files and len(c_files) == 2
    md = next(v for k, v in c_files.items() if k.endswith(".md"))
    assert md.startswith(b"\xef\xbb\xbf# Q8 Historical Review") and b"\r\n" not in md
    payload = b_res[1]["payload"]
    assert payload["below_vwap_reclaim_by_subtype_v2"]  # both branches of the v2 source are exercised
    assert payload["below_vwap_reclaim_subtype_forward"] and payload["q8_blocker_groups"]


@pytest.mark.parametrize(
    "start,end",
    [("2026-06-03", "2026-06-01"), ("2026-13-01", "2026-06-02"), ("bad", "2026-06-02"), ("2026-06-01", None)],
)
def test_historical_errors_and_empty_windows_match_base(tmp_path, monkeypatch, start, end):
    outcomes = []
    for label, mod in (("base", base("hist")), ("cur", hist_cur)):
        work = tmp_path / label
        reports = _build_reports(work)
        result, calls, _ = _run(work, monkeypatch,
                                lambda: mod.build_q8_historical_review_payload(reports_root=reports, start=start, end=end))
        outcomes.append((_relativize(result, work), calls))
    assert outcomes[0] == outcomes[1]


def test_historical_render_matches_base_on_sparse_and_hostile_payloads():
    payloads = [
        {},
        {"trade_summary": "x", "daily_rows": [{}], "q8_promotion_eligibility": [], "promotion_recommendations": [{"candidate": "c"}]},
        {"start": "a|b", "trade_by_tactic": [{"name": "한글", "win_rate": "0.5", "avg_return_pct": None}] * 12,
         "below_vwap_reclaim_subtype_forward": [{"name": "s", "avg_return_60m_pct": "1"}]},
    ]
    for payload in payloads:
        assert hist_cur.render_q8_historical_review_markdown(payload) == base("hist").render_q8_historical_review_markdown(payload)
    with pytest.raises(ValueError) as cur_exc:
        hist_cur.render_q8_historical_review_markdown({"trade_summary": {"win_rate": "nan%"}})
    with pytest.raises(ValueError) as base_exc:
        base("hist").render_q8_historical_review_markdown({"trade_summary": {"win_rate": "nan%"}})
    assert str(cur_exc.value) == str(base_exc.value)


def test_accumulators_and_folds_match_base_on_hostile_rows():
    rows = [{"candidate_count": "1,200", "observed_count": "3.9", "avg_latest_return_pct": "1.5%", "decision": "x"},
            {"count": 2, "observed_review_candidate_count": 0, "avg_max_adverse_pct": "-0.2"},
            {"candidate_count": None, "observed_count": "abc", "decision": "null"}, {}]
    b_group, c_group = base("hist").GroupAccumulator(), hist_cur.GroupAccumulator()
    b_fwd, c_fwd = base("hist").ForwardAccumulator(), hist_cur.ForwardAccumulator()
    for index, row in enumerate(rows):
        b_group.add(f"d{index % 2}", row)
        c_group.add(f"d{index % 2}", row)
        b_fwd.add({**row, "observed_count_5m": row.get("observed_count"), "avg_return_5m_pct": row.get("avg_latest_return_pct")})
        c_fwd.add({**row, "observed_count_5m": row.get("observed_count"), "avg_return_5m_pct": row.get("avg_latest_return_pct")})
    assert c_group.to_dict("r") == b_group.to_dict("r")
    assert list(c_fwd.to_dict("f")) == list(b_fwd.to_dict("f")) and c_fwd.to_dict("f") == b_fwd.to_dict("f")
    trade_rows = [{"tactic": "a", "pnl_pct": 1.0}, {"tactic": "b", "pnl_pct": -1.0}, {"tactic": None, "pnl_pct": 2},
                  {"tactic": "a", "pnl_pct": "3"}, {"tactic": "b", "pnl_pct": True}]
    assert hist_cur._aggregate_return_rows(trade_rows, "tactic", limit=2) == base("hist")._aggregate_return_rows(trade_rows, "tactic", limit=2)
    for value in (None, "", " 1,234.5% ", "-", "abc", 0.5, -2, "0.0049"):
        for name in ("_float", "_int", "_pct_from_ratio", "_text"):
            assert getattr(hist_cur, name)(value) == getattr(base("hist"), name)(value), (name, value)


def _shadow_payloads():
    candidate = {"symbol": "005930", "reason": "breakout_not_ready", "shadow_role": "top_pick", "rank": 1,
                 "quant_tactic_id": "vwap_reclaim_pullback",
                 "shadow_forward_base": {"available": True, "baseline_epoch": 1780358400, "baseline_price": 100.0}}
    return [{"generated_at": "2026-06-02T00:00:00+00:00", "candidates": [
        candidate, dict(candidate),
        {**candidate, "symbol": "000660", "reason": "volume_confirmation_missing", "rank": None,
         "shadow_forward_base": {"available": True, "baseline_epoch": 1780358400, "baseline_price": 200.0}},
        {**candidate, "symbol": "035420", "reason": "human_chart_sanity_guard_blocked"}, "junk"]}, "junk"]


_REAL_ATTACH = shadow_cur.attach_forward_outcomes
MINUTES = {
    "005930": [{"ts": 1780358400, "close": 100.0, "high": 100.0, "low": 100.0},
               {"ts": 1780358700, "close": 101.0, "high": 102.0, "low": 99.5},
               {"ts": 1780359300, "close": 103.0, "high": 104.0, "low": 99.0}],
    "000660": [{"ts": 1780358400, "close": 200.0, "high": 200.0, "low": 200.0},
               {"ts": 1780358700, "close": 198.0, "high": 199.0, "low": 197.0}],
}


@pytest.mark.parametrize("gate", [None, {"status": "pass", "promotion_allowed": True, "block_reasons": []},
                                  {"status": "blocked", "promotion_allowed": False, "reasons": ["low"]}])
def test_shadow_blocker_review_and_render_match_base(gate):
    kwargs = dict(minute_rows_by_symbol=MINUTES, market_regime_rail={"rail_id": "risk_off", "q8_review_focus": ["a", ""]})
    if gate is not None:
        kwargs["quant_shadow_evaluation"] = {"evaluation_trust_gate": gate}
    b_review = base("shadow").build_q8_shadow_blocker_review(_shadow_payloads(), **kwargs)
    c_review = shadow_cur.build_q8_shadow_blocker_review(_shadow_payloads(), **kwargs)
    assert json.dumps(c_review, ensure_ascii=False) == json.dumps(b_review, ensure_ascii=False)
    assert c_review["observed_review_candidate_count"] > 0
    assert shadow_cur.render_q8_shadow_blocker_review_markdown(c_review, day="2026-06-02") == \
        base("shadow").render_q8_shadow_blocker_review_markdown(b_review, day="2026-06-02")


def test_shadow_generate_writes_same_bytes_in_same_order(tmp_path, monkeypatch):
    outcomes = []
    for label, mod in (("base", base("shadow")), ("cur", shadow_cur)):
        work = tmp_path / label
        loads = []
        monkeypatch.setattr(mod, "load_quant_shadow_candidate_payloads", lambda **kw: loads.append(sorted(kw)) or _shadow_payloads()[:1])
        monkeypatch.setattr(mod, "load_latest_macro_snapshot", lambda day: {"day": day})
        monkeypatch.setattr(mod, "build_quant_shadow_candidate_evaluation", lambda payloads: {"evaluation_trust_gate": {"promotion_allowed": True}})
        # never fall back to a cwd-relative data/state.json; feed the same fixed minute bars to both
        monkeypatch.setattr(mod, "attach_forward_outcomes",
                            lambda rows, minute_rows_by_symbol=None: _REAL_ATTACH(rows, minute_rows_by_symbol=MINUTES))
        trace = _IoTrace(monkeypatch, work)
        result = mod.generate_q8_shadow_blocker_review(reports_root=work / "reports", day="2026-06-02")
        monkeypatch.undo()
        files = {p.name: p.read_bytes() for p in (work / "reports").rglob("*") if p.is_file()}
        outcomes.append((_relativize(result, work), trace.calls, files, loads))
    assert outcomes[0] == outcomes[1]
    writes = [c[1] for c in outcomes[1][1] if c[0] == "write_text"]
    assert writes == ["reports/operator_summary/daily/2026-06-02/q8_shadow_blocker_review.json",
                      "reports/operator_summary/daily/2026-06-02/q8_shadow_blocker_review.md"]
    assert {c[0] for c in outcomes[1][1]} == {"mkdir", "write_text"}  # no reads: loaders are the only input


def _lane_evaluation(allowed: bool):
    lanes = [
        {"name": "vwap_reclaim", "candidate_count": 30, "observed_count": 20, "coverage": 0.9, "avg_return_5m_pct": -0.1, "avg_return_15m_pct": -0.2},
        {"name": "breakout", "candidate_count": "30", "observed_count": 25, "coverage": "0.95", "avg_return_5m_pct": 0.6, "avg_mae_5m_pct": -2.0},
        {"name": "pullback", "candidate_count": 12, "observed_count": 12, "coverage": 0.99, "avg_return_5m_pct": -0.05, "avg_return_15m_pct": -0.3},
        {"name": "thin", "candidate_count": 9, "observed_count": 9, "coverage": 1.0},
        {"name": "low_cov", "candidate_count": 40, "observed_count": 30, "coverage": 0.1},
        {"name": "mixed", "candidate_count": 40, "observed_count": 30, "coverage": 0.99, "avg_return_5m_pct": -0.1, "avg_return_15m_pct": 0.2},
        {"name": "", "observed_count": "x"}, "junk",
    ]
    return {"payload_count": 2, "candidate_count": "41", "deduped_candidate_count": 40, "duplicate_candidate_count": None,
            "dedupe_key": ("symbol", "reason"), "evaluated_count": 40, "forward_outcome_available_count": 30,
            "forward_outcome_coverage": "0.73333", "would_enter_count": 1,
            "evaluation_trust_gate": {"status": "pass" if allowed else "blocked", "promotion_allowed": allowed},
            "entry_lane_observation": {"by_primary_lane": [{"name": "breakout", "count": 77}, {"name": "", "count": 1}]},
            "entry_lane_forward_outcomes": {"by_primary_lane": lanes},
            "by_reason": [{"name": "breakout_not_ready", "count": 9}, {"name": "", "count": 1}] + [{"name": f"r{i}"} for i in range(8)]}


@pytest.mark.parametrize("allowed", [True, False])
def test_lane_table_build_render_write_match_base(tmp_path, monkeypatch, allowed):
    outcomes = []
    for label, mod in (("base", base("lane")), ("cur", lane_cur)):
        work = tmp_path / label
        monkeypatch.setattr(mod, "load_quant_shadow_candidate_payloads", lambda **kw: [kw["days"]])
        monkeypatch.setattr(mod, "build_quant_shadow_candidate_evaluation", lambda payloads: _lane_evaluation(allowed))
        trace = _IoTrace(monkeypatch, work)
        result = mod.write_q8_lane_decision_table(reports_root=work / "reports", docs_root=work / "docs", day="2026-06-02T09:00")
        monkeypatch.undo()
        files = {str(p.relative_to(work)): p.read_bytes() for p in work.rglob("*") if p.is_file()}
        outcomes.append((_relativize(result, work), trace.calls, files))
    assert outcomes[0] == outcomes[1]
    verdicts = [row["verdict"] for row in outcomes[1][0]["payload"]["rows"]]
    assert set(verdicts) == ({"GOOD_BLOCK", "MISSED_OPPORTUNITY", "DATA_INCOMPLETE"} if allowed else {"TRUST_GATE_BLOCKED"})


# --- mutation checks: the parity harness must catch real grouping / return / verdict changes ---------


def _hist_payload(mod, tmp: Path, **scenario):
    reports = _build_reports(tmp, **scenario)
    return _relativize(mod.build_q8_historical_review_payload(reports_root=reports, start="2026-06-01", end="2026-06-05"), tmp)


@pytest.mark.parametrize(
    "target,name,mutant",
    [
        (agg_owner, "_weighted_avg", lambda total, weight: round(total, 4)),
        (agg_owner, "_counter_rows", lambda counter, limit: [{"name": n, "count": c} for n, c in sorted(counter.items()) if n][:limit]),
        (agg_owner, "_decision_for_reclaim_subtype", lambda row: "keep_blocked"),
        (agg_owner, "_PATTERN_INT_FIELDS", ("win_count", "loss_count", "flat_count")),
    ],
)
def test_historical_mutants_are_detected(tmp_path, monkeypatch, target, name, mutant):
    expected = _hist_payload(base("hist"), tmp_path / "base")
    assert _hist_payload(hist_cur, tmp_path / "green") == expected
    monkeypatch.setattr(target, name, mutant)
    assert _hist_payload(hist_cur, tmp_path / "mutant") != expected


@pytest.mark.parametrize(
    "name,mutant",
    [("TRUSTED_FORWARD_MIN_COVERAGE", 0.0), ("_VERDICT_ORDER", {}),
     ("_checkpoint_values", lambda outcome: {"available": False})],
)
def test_readout_mutants_are_detected(monkeypatch, name, mutant):
    for mod in (base("lane"), lane_cur):
        monkeypatch.setattr(mod, "load_quant_shadow_candidate_payloads", lambda **kw: [])
        monkeypatch.setattr(mod, "build_quant_shadow_candidate_evaluation", lambda payloads: _lane_evaluation(True))
    kwargs = dict(minute_rows_by_symbol=MINUTES, quant_shadow_evaluation={"evaluation_trust_gate": {"promotion_allowed": True}})

    def snapshot():
        return (lane_cur.build_q8_lane_decision_table(day="2026-06-02"),
                shadow_cur.build_q8_shadow_blocker_review(_shadow_payloads(), **kwargs))

    expected = (base("lane").build_q8_lane_decision_table(day="2026-06-02"),
                base("shadow").build_q8_shadow_blocker_review(_shadow_payloads(), **kwargs))
    assert snapshot() == expected
    monkeypatch.setattr(readout_owner, name, mutant)
    assert snapshot() != expected
