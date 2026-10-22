"""P1.5 DEV-A (large-first Reporter wave): BASE (d7ab8294) vs current parity for the Q9 full-chain component review.

The frozen BASE module is exec'd from Git inside the ``libs.reporting.evaluation`` package context (it uses relative
imports) beside the live one. Decision functions are compared on input grids, the whole ``build`` / ``render`` / ``write``
path is compared on hermetic datasets (loaders, cost profile, forward-outcome attachment and the three trade summaries are
replaced by identical fakes on both), facade seams are patched identically on both, and owner mutants must be detected.
Ownership / import / AST boundaries live in ``test_p15_a_full_chain_review_boundaries.py``.
"""
from __future__ import annotations

import copy
import enum
import itertools
import json
import subprocess
import sys
import types
from pathlib import Path

import pytest

import libs.reporting.evaluation.full_chain_component_review as cur
import libs.reporting.evaluation.full_chain_review_parts.attribution as attribution_owner
import libs.reporting.evaluation.full_chain_review_parts.component_decisions as decisions_owner
import libs.reporting.evaluation.full_chain_review_parts.render as render_owner
import libs.reporting.evaluation.full_chain_review_parts.root_cause as root_owner
import libs.reporting.evaluation.loss_decomposition as loss_mod
import libs.reporting.evaluation.scanner_quality as scanner_mod

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
PATH = "libs/reporting/evaluation/full_chain_component_review.py"
PACKAGE = "libs.reporting.evaluation"
_BASE: dict = {}


def base():
    if "mod" not in _BASE:
        src = subprocess.check_output(["git", "show", f"{BASE_SHA}:{PATH}"], cwd=ROOT).decode("utf-8-sig")
        mod = types.ModuleType(f"{PACKAGE}._p15_full_chain_base_d7ab8294")
        mod.__package__ = PACKAGE
        mod.__file__ = str(ROOT / PATH)
        sys.modules[mod.__name__] = mod
        exec(compile(src, f"<base:{PATH}>", "exec"), mod.__dict__)
        _BASE["mod"] = mod
    return _BASE["mod"]


def _outcome(fn):
    try:
        return ("ok", json.dumps(fn(), ensure_ascii=False, default=repr, sort_keys=False))
    except Exception as exc:  # noqa: BLE001
        return ("exc", type(exc).__name__, str(exc))


def _cp(value):
    return {"status": "observed", "return_pct": value}


HORIZONS = ("+5m", "+15m", "+30m", "+60m")


def _cand(window, role, base_value, *, day="20261001", pending=()):
    checkpoints = {h: _cp(base_value + i * 0.1) for i, h in enumerate(HORIZONS) if h not in pending}
    return {"_payload_generated_at": window, "shadow_role": role,
            "shadow_forward_base": {"baseline_raw_ts": day + "093000"}, "shadow_forward_outcome": {"checkpoints": checkpoints}}


def _q9_rows(index, *, day, b_minus_a, c_minus_b, no_trade=False, refresh=0.2):
    did = f"d{index}"
    a, b = 0.2, 0.2 + b_minus_a
    c = b + c_minus_b
    def row(role, value, **extra):
        return {"q9_decision_id": did, "q9_decision_role": role, "rank": 1, "shadow_forward_base": {"baseline_raw_ts": day + "093000"},
                "shadow_forward_outcome": {"checkpoints": {h: _cp(value) for h in HORIZONS}}, **extra}
    return [row("A_SCANNER_CONTROL", a), row("B_STRATEGIST_RANKED", b, q9_selected=True), row("B_STRATEGIST_RANKED", b - 5, rank=2),
            row("R1_PRE_REFRESH_SCANNER", a), row("R2_POST_REFRESH_SCANNER", a + refresh),
            row("C_COMMANDER_FINAL", c, q9_commander_no_trade=no_trade)]


def _payloads(n, *, b_minus_a, c_minus_b, days=("20261001", "20261002", "20261003"), refresh=0.2):
    payloads = []
    for i in range(n):
        day = days[i % len(days)]
        payloads.append({"generated_at": f"{day[:4]}-{day[4:6]}-{day[6:]}T00:{i:02d}:00+00:00",
                         "candidates": [_cand(f"{day}-w{i}", "top_pick", 1.0 + (i % 3) * 0.3, day=day), _cand(f"{day}-w{i}", "runner_up_evaluated", 0.2, day=day, pending=("+60m",))],
                         "q9_decision_candidates": _q9_rows(i, day=day, b_minus_a=b_minus_a, c_minus_b=c_minus_b, no_trade=(i % 5 == 0), refresh=refresh)})
    return payloads


def _topk(window_count, days, net, *, junk=False):
    rows = [{"top_k": 1, "horizon": "+30m", "window_count": window_count, "observed_day_count": days, "net": {"expectancy_pct": net}},
            {"top_k": 3, "horizon": "+30m", "window_count": window_count, "observed_day_count": days, "net": {"expectancy_pct": net}}]
    return {"topk_forward_performance": {"rows": rows + (["junk"] if junk else [])}}  # a non-dict row only for direct helper calls (render reads rows as dicts)


MODELS = [{"day": f"2026-10-0{1 + i % 3}", "integrity": {"defects": []} if i % 7 else {"defects": ["confirmed_runtime_defect"]}, "outcome": {"net_return_pct": -0.2 + i * 0.01},
           "selection": ({"raw_scanner_snapshot_source": "control_snapshot", "raw_scanner_top10": [{"symbol": "A"}], "strategist_run_id": "S1",
                          "post_strategist_top10": [{"symbol": "B"}], "commander_final_explicit": bool(i % 2)} if i % 4 else {})} for i in range(30)]
ENTRY = {"enough": {"matched_trade_count": 25, "matched_day_count": 3, "average_entry_price_delta_pct": 0.1, "median_entry_price_delta_pct": 0.05},
         "late": {"matched_trade_count": 25, "matched_day_count": 3, "average_entry_price_delta_pct": 0.6, "median_entry_price_delta_pct": 0.5}, "few": {"matched_trade_count": 2}}
EXIT = {"enough": {"observed_trade_count": 25, "observed_day_count": 3, "by_hold_offset": [{"offset": "+5m", "average_improvement_pct": 0.5}]},
        "flat": {"observed_trade_count": 25, "observed_day_count": 3, "by_hold_offset": [{"offset": "+5m", "average_improvement_pct": 0.0}, "junk"]}, "few": {}}
REALIZED = {"positive": {"performance": {"count": 25, "expectancy_pct": 0.2}}, "negative": {"performance": {"count": 25, "expectancy_pct": -0.2}}, "few": {"performance": {"count": 3}}}
DATASETS = {
    "strategist_helps": dict(payloads=_payloads(30, b_minus_a=0.5, c_minus_b=0.4), entry="enough", exit="flat", realized="positive", scanner=_topk(30, 3, 0.4)),
    "strategist_hurts_scanner_fails": dict(payloads=_payloads(30, b_minus_a=-0.6, c_minus_b=-0.5), entry="late", exit="enough", realized="negative", scanner=_topk(30, 3, -0.3)),
    "only_strategist_hurts": dict(payloads=_payloads(30, b_minus_a=-0.6, c_minus_b=0.0), entry="enough", exit="flat", realized="negative", scanner=_topk(30, 3, 0.4)),
    "thin_evidence": dict(payloads=_payloads(3, b_minus_a=0.1, c_minus_b=0.0), entry="few", exit="few", realized="few", scanner=_topk(2, 1, 0.1)),
    "empty": dict(payloads=[], entry="few", exit="few", realized="few", scanner={}),
}


def _install(monkeypatch, mod, dataset):
    monkeypatch.setattr(mod, "load_quant_shadow_candidate_payloads_for_range", lambda **kw: copy.deepcopy(dataset["payloads"]))
    monkeypatch.setattr(mod, "attach_forward_outcomes", lambda rows, **kw: rows)
    monkeypatch.setattr(loss_mod, "attach_forward_outcomes", lambda rows, **kw: rows)
    monkeypatch.setattr(scanner_mod, "attach_forward_outcomes", lambda rows, **kw: rows)
    monkeypatch.setattr(mod, "load_broker_cost_profile", lambda path=None: {"source": "fake", "sample_count": 3, "conservative_round_trip_cost_pct": 0.01})
    monkeypatch.setattr(mod, "_load_trade_models", lambda reports_root, start, end: copy.deepcopy(MODELS))
    monkeypatch.setattr(mod, "build_scanner_quality_review", lambda payloads, **kw: {"schema_version": "fake", **copy.deepcopy(dataset["scanner"])})
    monkeypatch.setattr(mod, "_entry_timing_summary", lambda models, candidates: dict(ENTRY[dataset["entry"]]))
    monkeypatch.setattr(mod, "_exit_hold_summary", lambda models: copy.deepcopy(EXIT[dataset["exit"]]))
    monkeypatch.setattr(mod, "_realized_trade_summary", lambda models: copy.deepcopy(REALIZED[dataset["realized"]]))


def _bundle(monkeypatch, mod, dataset, tmp_path):
    _install(monkeypatch, mod, dataset)
    monkeypatch.chdir(tmp_path)
    review = mod.build_full_chain_component_review(reports_root=tmp_path / "reports", start="2026-10-01", end="2026-10-03")
    written = mod.write_full_chain_component_review(reports_root=tmp_path / "reports", start="2026-10-01", end="2026-10-03", output_dir=tmp_path / "out")
    files = {name: (tmp_path / "out" / Path(path).name).read_bytes().decode("utf-8") for name, path in written.items()}
    return json.dumps([review, mod.render_full_chain_component_review(review), files], ensure_ascii=False, default=repr)


@pytest.mark.parametrize("name", sorted(DATASETS))
def test_build_render_and_written_files_match_base(monkeypatch, tmp_path, name):
    outputs = []
    for label, mod in (("base", base()), ("cur", cur)):
        work = tmp_path / label
        work.mkdir()
        outputs.append(_outcome(lambda m=mod, w=work: _bundle(monkeypatch, m, DATASETS[name], w).replace(str(w).replace("\\", "\\\\"), "<WORK>")))
        monkeypatch.undo()
    assert outputs[0] == outputs[1] and outputs[1][0] == "ok"


def test_datasets_reach_each_decision_branch(monkeypatch, tmp_path):
    seen = set()
    for name, dataset in DATASETS.items():
        work = tmp_path / name
        work.mkdir()
        review = json.loads(_bundle(monkeypatch, cur, dataset, work))[0]
        monkeypatch.undo()
        seen |= {c["decision"] for c in review["component_decisions"].values() if isinstance(c, dict) and "decision" in c}
        seen.add(review["problem_segment"]["primary_root_cause"])
    assert {"INSUFFICIENT_EVIDENCE", "RETAIN", "REJECT", "PROMOTION_CANDIDATE", "ADJUST_AND_RETEST"} <= seen
    assert {"strategist_degradation", "scanner_intrinsic_fail", "insufficient_sample"} <= seen


def test_root_cause_grid_matches_base():
    scanners = [{}, _topk(30, 3, 0.4), _topk(30, 3, -0.3, junk=True), _topk(5, 1, -0.3), {"topk_forward_performance": "x"}]
    attributions = [{}, {"by_horizon": [{"horizon": "+30m", "strategist_comparison_count": 30, "strategist_day_count": 3, "average_strategist_delta_pct": -0.5,
                                         "commander_comparison_count": 30, "commander_day_count": 3, "average_commander_delta_pct": -0.5}, "junk"]},
                    {"by_horizon": [{"horizon": "+30m", "strategist_comparison_count": 30, "strategist_day_count": 3, "average_strategist_delta_pct": "0.9",
                                     "commander_comparison_count": 1, "commander_day_count": 1, "average_commander_delta_pct": None}]}]
    cases = 0
    for scanner, attribution, entry, exit_hold in itertools.product(scanners, attributions, ENTRY.values(), EXIT.values()):
        kwargs = dict(scanner_quality=scanner, attribution=attribution, entry=entry, exit_hold=exit_hold)
        assert _outcome(lambda: cur._classify_root_cause(**copy.deepcopy(kwargs))) == _outcome(lambda: base()._classify_root_cause(**copy.deepcopy(kwargs)))
        cases += 1
    assert cases == 5 * 3 * 3 * 3
    for top_k, horizon in ((1, "+30m"), (3, "+5m"), (2, "+30m")):
        assert _outcome(lambda: cur._topk_metric(_topk(9, 2, 0.1), top_k=top_k, horizon=horizon)) == _outcome(lambda: base()._topk_metric(_topk(9, 2, 0.1), top_k=top_k, horizon=horizon))


def test_component_decision_grid_matches_base():
    attribution_rows = [{}, {"by_horizon": []}]
    for c, d, delta, rate in itertools.product((3, 25), (1, 3), (None, 0.1, 0.6), (0.2, 0.7)):
        attribution_rows.append({"by_horizon": [{"horizon": "+30m", "strategist_comparison_count": c, "strategist_day_count": d, "average_strategist_delta_pct": delta,
                                                 "strategist_positive_delta_rate": rate, "commander_comparison_count": c, "commander_day_count": d,
                                                 "average_commander_delta_pct": delta, "commander_positive_delta_rate": rate}]})
    assert len(attribution_rows) == 2 + 2 * 2 * 3 * 2
    for attribution in attribution_rows:
        for component in ("strategist", "commander"):
            kwargs = dict(attribution=attribution, component=component, question="q", missing_comparison="m", availability={"a": 1})
            assert _outcome(lambda: cur._attribution_component(**copy.deepcopy(kwargs))) == _outcome(lambda: base()._attribution_component(**copy.deepcopy(kwargs)))
    role_metrics = [[], [{"role": "top_pick", "horizon": "+30m", "expectancy_pct": -0.2}], [{"role": "top_pick", "horizon": "+30m", "expectancy_pct": 0.5}, "junk"]]
    paired = [[], [{"horizon": "+30m", "paired_window_count": 25, "observed_day_count": 3, "average_delta_pct": 0.6, "positive_delta_rate": 0.8}],
              [{"horizon": "+30m", "paired_window_count": 25, "observed_day_count": 3, "average_delta_pct": -0.6, "positive_delta_rate": 0.1}]]
    for rm, pr in itertools.product(role_metrics, paired):
        assert _outcome(lambda: cur._scanner_decision(role_metrics=copy.deepcopy(rm), paired=copy.deepcopy(pr))) == _outcome(lambda: base()._scanner_decision(role_metrics=copy.deepcopy(rm), paired=copy.deepcopy(pr)))
    kwargs = dict(question="q", missing_comparison="m", availability={"x": [1]})
    assert _outcome(lambda: cur._unavailable_component(**kwargs)) == _outcome(lambda: base()._unavailable_component(**kwargs))


def test_metric_helpers_match_base_on_adverse_rows(monkeypatch):
    for mod in (base(), cur):
        monkeypatch.setattr(mod, "attach_forward_outcomes", lambda rows, **kw: rows)
    rows = [_cand("w1", "top_pick", 1.0), _cand("w1", "runner_up_evaluated", 0.2), _cand("w2", "top_pick", -0.4, day="20261002"), {}, {"shadow_role": "top_pick"},
            {"shadow_role": "runner_up_evaluated", "_payload_generated_at": "w2", "shadow_forward_outcome": {"checkpoints": {"+30m": {"status": "pending", "return_pct": 9}}}}]
    for horizon in HORIZONS + ("+90m",):
        for role in ("top_pick", "runner_up_evaluated", "other"):
            assert _outcome(lambda: cur._role_metrics(copy.deepcopy(rows), role=role, horizon=horizon, cost_pct=0.5)) == _outcome(lambda: base()._role_metrics(copy.deepcopy(rows), role=role, horizon=horizon, cost_pct=0.5))
        assert _outcome(lambda: cur._paired_role_deltas(copy.deepcopy(rows), horizon=horizon)) == _outcome(lambda: base()._paired_role_deltas(copy.deepcopy(rows), horizon=horizon))
    assert _outcome(lambda: cur._selection_availability(copy.deepcopy(MODELS) + [{}, {"selection": "x"}])) == _outcome(lambda: base()._selection_availability(copy.deepcopy(MODELS) + [{}, {"selection": "x"}]))
    roles = {"B_STRATEGIST_RANKED": [{"rank": "3"}, {"rank": 1, "q9_selected": True}, {"rank": None}], "A_SCANNER_CONTROL": [{"rank": "x"}], "C": []}
    for role in ("B_STRATEGIST_RANKED", "A_SCANNER_CONTROL", "C", "missing"):
        assert _outcome(lambda: cur._q9_role_row(copy.deepcopy(roles), role)) == _outcome(lambda: base()._q9_role_row(copy.deepcopy(roles), role))
    for payloads in (DATASETS["strategist_helps"]["payloads"], [], [{"q9_decision_candidates": "x"}, {"q9_decision_candidates": [{"q9_decision_id": "", "q9_decision_role": "A_SCANNER_CONTROL"}, "junk"]}]):
        assert _outcome(lambda: cur._decision_window_attribution(copy.deepcopy(payloads), cost_pct=0.4)) == _outcome(lambda: base()._decision_window_attribution(copy.deepcopy(payloads), cost_pct=0.4))


@pytest.mark.parametrize("payload", [
    {}, {"component_decisions": "x"}, {"range": {"start": "a"}, "component_decisions": {"scanner": {"decision": "RETAIN", "metrics": {"k": [1, 2]}, "role_cost_adjusted_metrics": [{"role": "top_pick", "horizon": "+30m"}]}}},
    {"evidence": {"decision_window_attribution": {"by_horizon": ["junk", {"horizon": "+30m"}]}}, "problem_segment": {"primary_root_cause": "x", "statuses": {"a": True}}},
])
def test_render_matches_base_on_sparse_and_hostile_payloads(payload):
    assert _outcome(lambda: cur.render_full_chain_component_review(copy.deepcopy(payload))) == _outcome(lambda: base().render_full_chain_component_review(copy.deepcopy(payload)))


# --- facade monkeypatch seams: the same patch on BASE and current must give the same output, different from unpatched ---


class _Patched(enum.Enum):
    INSUFFICIENT_EVIDENCE = "x_insufficient"
    RETAIN = "x_retain"
    REJECT = "x_reject"
    ADJUST_AND_RETEST = "x_adjust"
    PROMOTION_CANDIDATE = "x_promotion"


SEAMS = [
    ("_number", lambda mod: (lambda value: None)),
    ("_checkpoint_return", lambda mod: (lambda row, label: 1.0)),
    ("candidate_day", lambda mod: (lambda row: "20990101")),
    ("performance_metrics", lambda mod: (lambda values: {"patched": len(values)})),
    ("HORIZONS", lambda mod: ("+5m", "+30m")),
    ("DIRECTIONAL_MIN_DAYS", lambda mod: 99),
    ("DIRECTIONAL_MIN_OBSERVATIONS", lambda mod: 999),
    ("MIN_MATERIAL_RANKING_DELTA_PCT", lambda mod: 100.0),
    ("MIN_POSITIVE_RANKING_DELTA_RATE", lambda mod: 0.99),
    ("DecisionClass", lambda mod: _Patched),
    ("_topk_metric", lambda mod: (lambda scanner_quality, *, top_k, horizon: {"window_count": 99, "observed_day_count": 9, "net": {"expectancy_pct": -1.0}})),
    ("_q9_role_row", lambda mod: (lambda roles, role: {})),
    ("_q9_decision_candidate_rows", lambda mod: (lambda payloads: [])),
    ("_role_metrics", lambda mod: (lambda candidates, *, role, horizon, cost_pct: {"role": role, "patched": True})),
    ("_paired_role_deltas", lambda mod: (lambda candidates, *, horizon: {"horizon": horizon, "patched": True})),
    ("_selection_availability", lambda mod: (lambda models: {"patched": len(models)})),
    ("_decision_window_attribution", lambda mod: (lambda payloads, *, cost_pct: {"by_horizon": [], "patched": True})),
    ("_classify_root_cause", lambda mod: (lambda **kw: {"primary_root_cause": "patched"})),
    ("_attribution_component", lambda mod: (lambda **kw: {"decision": "PATCHED", "component": kw["component"]})),
    ("_scanner_decision", lambda mod: (lambda **kw: {"decision": "PATCHED"})),
    ("_unavailable_component", lambda mod: (lambda **kw: {"decision": "PATCHED_UNAVAILABLE"})),
    ("render_full_chain_component_review", lambda mod: (lambda payload: "PATCHED-RENDER")),
]


@pytest.mark.parametrize("name,factory", SEAMS, ids=[n for n, _ in SEAMS])
def test_facade_monkeypatch_seams_match_base(monkeypatch, tmp_path, name, factory):
    dataset = DATASETS["strategist_helps"]
    runs = {}
    for label, mod, patched in (("unpatched", cur, False), ("base", base(), True), ("cur", cur, True)):
        work = tmp_path / label
        work.mkdir()
        if patched:
            monkeypatch.setattr(mod, name, factory(mod))
        runs[label] = _outcome(lambda m=mod, w=work: _bundle(monkeypatch, m, dataset, w).replace(str(w).replace("\\", "\\\\"), "<WORK>"))
        monkeypatch.undo()
    assert runs["cur"] == runs["base"] and runs["cur"] != runs["unpatched"]


# --- mutation checks: breaking an owner (as bound into the facade) must break parity ---------------------------------


@pytest.mark.parametrize(
    "name,mutant",
    [
        ("_topk_metric_impl", lambda scanner_quality, *, top_k, horizon, facade: {}),
        ("_classify_root_cause_impl", lambda *, scanner_quality, attribution, entry, exit_hold, facade: {"primary_root_cause": "mutant"}),
        ("_role_metrics_impl", lambda candidates, *, role, horizon, cost_pct, facade: {"role": role}),
        ("_paired_role_deltas_impl", lambda candidates, *, horizon, facade: {"horizon": horizon}),
        ("_selection_availability_impl", lambda models, *, facade: {}),
        ("_q9_role_row_impl", lambda roles, role, *, facade: {}),
        ("_decision_window_attribution_impl", lambda payloads, *, cost_pct, facade: {"by_horizon": []}),
        ("_attribution_component_impl", lambda *, attribution, component, question, missing_comparison, availability, facade: {"decision": "mutant"}),
        ("_scanner_decision_impl", lambda *, role_metrics, paired, facade: {"decision": "mutant"}),
        ("_unavailable_component_impl", lambda *, question, missing_comparison, availability, facade: {}),
        ("render_full_chain_component_review_impl", lambda payload, *, facade: "mutant"),
    ],
)
def test_owner_mutants_are_detected(monkeypatch, tmp_path, name, mutant):
    dataset = DATASETS["strategist_helps"]
    results = {}
    for label, mod, patched in (("base", base(), False), ("green", cur, False), ("mutant", cur, True)):
        work = tmp_path / label
        work.mkdir()
        if patched:
            monkeypatch.setattr(mod, name, mutant)
        results[label] = _outcome(lambda m=mod, w=work: _bundle(monkeypatch, m, dataset, w).replace(str(w).replace("\\", "\\\\"), "<WORK>"))
        monkeypatch.undo()
    assert results["green"] == results["base"]  # green baseline first
    assert results["mutant"] != results["base"]
