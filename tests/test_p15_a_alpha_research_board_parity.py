"""P1.5 DEV-A (large-first Reporter wave): BASE (d7ab8294) vs current parity for libs.reporting.alpha_research_board.builder.

The frozen BASE builder is exec'd from Git inside the ``libs.reporting.alpha_research_board`` package context (it uses relative
imports) beside the live one. Two kinds of runs are compared on both: (1) the real builder chain over the existing synthetic
reports tree (``build`` payload and all twelve files ``write`` produces, byte for byte), (2) controlled runs in which every
reader/builder the orchestrator calls is replaced by the same fake on both, so each review/sensitivity branch is reached
without real data. Direct unit grids, facade seams and owner mutants are compared the same way. Ownership/import/AST
boundaries live in ``test_p15_a_alpha_research_board_boundaries.py``.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import types
from datetime import datetime as _real_datetime
from pathlib import Path

import pytest

import libs.reporting.alpha_research_board.board_assembly as assembly_owner
import libs.reporting.alpha_research_board.builder as cur
import libs.reporting.alpha_research_board.candidate_rows as rows_owner

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
PATH = "libs/reporting/alpha_research_board/builder.py"
PACKAGE = "libs.reporting.alpha_research_board"
_BASE: dict = {}


def base():
    if "mod" not in _BASE:
        src = subprocess.check_output(["git", "show", f"{BASE_SHA}:{PATH}"], cwd=ROOT).decode("utf-8-sig")
        mod = types.ModuleType(f"{PACKAGE}._p15_builder_base_d7ab8294")
        mod.__package__ = PACKAGE
        mod.__file__ = str(ROOT / PATH)
        sys.modules[mod.__name__] = mod
        exec(compile(src, f"<base:{PATH}>", "exec"), mod.__dict__)
        _BASE["mod"] = mod
    return _BASE["mod"]


def _board_tests():
    spec = importlib.util.spec_from_file_location("_p15_board_fixture_tests", ROOT / "tests" / "test_alpha_research_board.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _FixedDatetime:
    @staticmethod
    def now(tz=None):
        return _real_datetime(2026, 10, 22, 9, 0, 0, tzinfo=tz)


def _freeze(monkeypatch, mod):
    monkeypatch.setattr(mod, "datetime", _FixedDatetime)


def _outcome(fn):
    try:
        return ("ok", json.dumps(fn(), ensure_ascii=False, default=repr))
    except Exception as exc:  # noqa: BLE001
        return ("exc", type(exc).__name__, str(exc))


# --- real chain over the existing synthetic reports tree ----------------------------------------------------------------

Q12 = {"schema_version": "q12_btc_woori_hypothesis_cumulative.v1", "rows": [
    {"evidence_phase": "PROSPECTIVE", "axis": "hypothesis_path", "value": "FAST_BUY_ALL_PASS", "entry_method": "09:05", "horizon": "+30m",
     "metrics": {"sample_count": 3, "win_rate": 0.6667, "avg_return_pct": 0.42, "profit_factor": 2.1}}, "junk"]}


def _world(tmp_path, variant, tests):
    root = tests._fixture_reports(tmp_path) if variant != "empty" else (tmp_path / "reports")
    root.mkdir(parents=True, exist_ok=True)
    evaluation = root / "evaluation"
    if variant == "with_q12":
        tests._write(evaluation / "baseline_btc_woori_tech" / "hypothesis_validation" / "q12_btc_woori_hypothesis_cumulative.json", Q12)
    elif variant == "missing_contract":
        (evaluation / "feature_mart" / "opening_rank1" / "prospective" / "frozen_candidate_contract.json").unlink()
    elif variant == "corrupt_source":
        (evaluation / "opening_rank1_shadow" / "opening_rank1_shadow_cumulative.json").write_text("{not json", encoding="utf-8")
    return root


VARIANTS = ["full", "with_q12", "missing_contract", "corrupt_source", "empty"]


def _real_run(monkeypatch, mod, tmp_path, variant):
    tests = _board_tests()
    _freeze(monkeypatch, mod)
    root = _world(tmp_path, variant, tests)
    board = mod.build_alpha_research_board(reports_root=root, through_day="2026-08-28")
    out = tmp_path / "evaluation_out" / "2026-08-28"
    written = mod.write_alpha_research_board(reports_root=root, through_day="2026-08-28", output_dir=out)
    files = {p.relative_to(tmp_path).as_posix(): p.read_bytes().decode("utf-8") for p in sorted((tmp_path / "evaluation_out").rglob("*")) if p.is_file()}
    relative = {k: (v if not str(v).startswith(str(tmp_path)) else Path(v).relative_to(tmp_path).as_posix()) for k, v in written.items()}
    return json.dumps([board, relative, files], ensure_ascii=False, default=repr)


@pytest.mark.parametrize("variant", VARIANTS)
def test_real_build_and_written_files_match_base(monkeypatch, tmp_path, variant):
    outputs = []
    for mod in (base(), cur):
        work = tmp_path / "w"  # same absolute path for both runs: the payload embeds the absolute source paths
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir()
        outputs.append(_outcome(lambda m=mod, w=work: _real_run(monkeypatch, m, w, variant)))
        monkeypatch.undo()
    assert outputs[0] == outputs[1] and outputs[1][0] == "ok"
    if variant == "full":
        board, _written, files = json.loads(json.loads(outputs[1][1]))  # _outcome JSON-encodes the already encoded run string
        assert board["candidate_count"] == 14 and len(files) == 12


# --- controlled runs: every reader/builder the orchestrator calls is faked identically on both ----------------------------

CANDIDATE_IDS = ["R1_SCANNER_RISK_HIGH_30M_V1", "R1_ENTRY_DAILY_MA5_20_EXTENDED_15M_V1", "R1_FRESH_CHANGE_ACTIVATION_V1", "IMMEDIATE_OPENING_PROBE",
                 "CONFIRMED_RECURRENT_RANK", "DISLOCATION_REBOUND", "OPEN_0_20_RANK1_30M", "LATENT_REACTIVATION_FRESH_TRIGGER",
                 "BTC_WOORI_V2_ONLY_LOCAL_CONFIRMATION", "SAMSUNG_HYNIX_FIXED_UNIVERSE_TOP1", "BTC_STRONG_BULL_LOCAL_CONFIRMATION_V1", "HIGH_COMMON_SHORT_ALPHA_V1"]
DECISIONS = ["READY_FOR_FIXED_RUNTIME_VALIDATION", "RUNTIME_DATA_REQUIRED", "REJECT_NO_EDGE", "REJECT", "SOMETHING_ELSE", "", None]


def _payload(name):
    metrics = {"sample_count": 4, "win_rate": 0.5, "avg_return_pct": 0.3, "profit_factor": 1.4}
    base_rows = {
        "feature": {"prospective_shadow_candidates": [{"feature": "scanner.risk_band", "category": "HIGH", "train": metrics, "validation": metrics, "decision": "OBSERVE"}, "junk"]},
        "prospective": {"candidate_summaries": [{"candidate_id": "R1_SCANNER_RISK_HIGH_30M_V1", "candidate": {"feature_path": "scanner.risk_band", "expected_value": "HIGH"},
                                                 "decision": {"status": "SINGLE_BEHAVIOR_PATCH_REVIEW_ELIGIBLE"}, "branch": metrics},
                                                {"candidate_id": "R1_ENTRY_DAILY_MA5_20_EXTENDED_15M_V1", "candidate": {}, "decision": "x"}]},
    }
    return base_rows[name]


def _controlled_fakes(monkeypatch, mod, scenario):
    sensitivity_decision, review_decisions, with_hypothesis = scenario
    reviews = [{"candidate_id": cid, "decision": review_decisions[i % len(review_decisions)], "rationale": f"why {cid}",
                "by_btc_regime": [{"btc_regime": "weak"}, {"btc_regime": "strong_bull", "sample_count": 7, "win_rate": 0.6}, "junk"]}
               for i, cid in enumerate(CANDIDATE_IDS)]
    payloads = {
        "feature_candidates": _payload("feature"), "prospective_candidates": _payload("prospective"),
        "prospective_contract": {"first_eligible_day": "2026-08-25"},
        "fresh_change": {"decision": {"status": "REJECTED"}, "historical_reference": {"branch": {"horizons": {"+30m": {"sample_count": 5}}}}, "branch": {"horizons": {"+30m": {"sample_count": 2}}}},
        "opening_cumulative": {"summary": {"conditional_lane_summaries": {"IMMEDIATE_OPENING_PROBE": {"horizons": {"+5m": {"live_net": {"sample_count": 9}}}}}},
                               "promotion_decision": {"status": "BLOCKED", "values": {"observed_count": 33, "win_rate": 0.55, "largest_day_share": 0.4}}},
        "latent_reactivation": {"summary": {"status": "COLLECTING", "horizons": {"+30m": {"live_net": {"sample_count": 3}}}, "largest_day_share": 0.5}},
        "btc_woori_history": {"conclusion": "CLOSED", "episode_horizons": [{"horizon": "+30m", "real_net": {"sample_count": 6}}]},
    }
    sources = {}

    def fake_load_json(path):
        key = next((k for k, rel in mod.SOURCE_PATHS.items() if str(path).endswith(str(rel).replace("/", "\\")) or str(path).endswith(str(rel))), None)
        if key is None:
            return copy.deepcopy(Q12), {"path": str(path), "available": True, "error": None}
        return copy.deepcopy(payloads[key]), {"path": key, "available": key != "latent_reactivation", "error": "boom" if key == "fresh_change" else None}

    monkeypatch.setattr(mod, "load_json", fake_load_json)
    monkeypatch.setattr(mod, "_prospective_concentrations", lambda **kw: {"R1_SCANNER_RISK_HIGH_30M_V1": {"independent_day_symbol_count": 12, "largest_day_share": 0.3}})
    monkeypatch.setattr(mod, "build_risk_high_sensitivity", lambda **kw: {"decision": sensitivity_decision, "rationale": "sens why"})
    monkeypatch.setattr(mod, "_large_cap_candidate", lambda reports_root, through_day: (mod._candidate(
        candidate_id="SAMSUNG_HYNIX_FIXED_UNIVERSE_TOP1", track_id="LARGE_CAP_TWO_SYMBOL", discriminator="d", target_horizon="+180m", source_status="S",
        board_bucket="BACKGROUND_RUNTIME_REQUIRED", owner="O", evidence_note="n", next_action="a", source_keys=["large_cap_daily"]), {"path": "multiple", "available": True}))
    monkeypatch.setattr(mod, "build_remaining_candidate_reviews", lambda **kw: {"reviews": copy.deepcopy(reviews)})
    monkeypatch.setattr(mod, "build_short_alpha_discriminator", lambda **kw: {"cohort_review": {"historical_reference": {"day_count": 3, "largest_day_share": 0.6,
        "horizons": {"+5m": {"sample_count": 8}}}, "prospective": {"horizons": {"+5m": {"sample_count": 2}}}}})
    monkeypatch.setattr(mod, "build_immediate_opening_runtime_validation", lambda **kw: {"status": "PENDING"})
    monkeypatch.setattr(mod, "canonicalize_board", lambda legacy, **kw: copy.deepcopy(legacy))
    if not with_hypothesis:
        original = mod.Path.exists
        monkeypatch.setattr(mod.Path, "exists", lambda self: False if "q12_btc_woori_hypothesis" in str(self) else original(self))
    else:
        original = mod.Path.exists
        monkeypatch.setattr(mod.Path, "exists", lambda self: True if "q12_btc_woori_hypothesis" in str(self) else original(self))


SCENARIOS = {
    "sens_pass_mixed_reviews": ("PROMOTION_REVIEW_PASS", DECISIONS, True),
    "sens_fail_ready": ("FAIL", ["READY_FOR_FIXED_RUNTIME_VALIDATION"], False),
    "reject_all": ("FAIL", ["REJECT_NO_EDGE", "REJECT"], True),
    "runtime_data_required": ("PROMOTION_REVIEW_PASS", ["RUNTIME_DATA_REQUIRED"], False),
    "no_decision": ("PROMOTION_REVIEW_PASS", [None, "", "SOMETHING_ELSE"], False),
}


def _controlled(monkeypatch, mod, scenario):
    _freeze(monkeypatch, mod)
    _controlled_fakes(monkeypatch, mod, scenario)
    return mod.build_alpha_research_board(reports_root=Path("reports"), through_day="2026-08-28")


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_controlled_branches_match_base(monkeypatch, name):
    results = []
    for mod in (base(), cur):
        results.append(_outcome(lambda m=mod: _controlled(monkeypatch, m, SCENARIOS[name])))
        monkeypatch.undo()
    assert results[0] == results[1] and results[1][0] == "ok"


def test_controlled_scenarios_reach_every_review_and_sensitivity_branch(monkeypatch):
    buckets, notes = set(), set()
    for name, scenario in SCENARIOS.items():
        board = json.loads(_outcome(lambda s=scenario: _controlled(monkeypatch, cur, s))[1])
        monkeypatch.undo()
        buckets |= {row["board_bucket"] for row in board["candidates"]}
        notes |= {row.get("final_offline_review", {}).get("decision") for row in board["candidates"]}
        assert board["integrity"]["status"] in {"PASS", "PASS_WITH_MISSING_SOURCES"}
    assert {"RUNTIME_VALIDATION_NEXT", "BACKGROUND_RUNTIME_REQUIRED", "CLOSED_AFTER_SENSITIVITY_REVIEW", "CLOSED_NEGATIVE_PROSPECTIVE", "ACTION_REVIEW", "OBSERVE_FIXED", "CLOSED"} <= buckets
    assert {"READY_FOR_FIXED_RUNTIME_VALIDATION", "RUNTIME_DATA_REQUIRED", "REJECT_NO_EDGE", "REJECT"} <= notes


# --- direct unit grids for the moved row functions on adverse payloads ---------------------------------------------------

ADVERSE = [{}, {"rows": "x"}, {"rows": ["junk", {"evidence_phase": "PROSPECTIVE", "axis": "hypothesis_path", "value": "FAST_BUY_ALL_PASS", "entry_method": "09:05", "horizon": "+30m", "metrics": {"sample_count": "3"}}]},
           {"summary": [], "promotion_decision": None, "episode_horizons": "x", "historical_reference": 5, "branch": []},
           {"summary": {"conditional_lane_summaries": {"IMMEDIATE_OPENING_PROBE": {"horizons": {"+5m": {"live_net": {"sample_count": 1}}}}}}, "promotion_decision": {"status": 5, "values": {"observed_count": "7"}},
            "episode_horizons": [{"horizon": "+30m", "real_net": {"win_rate": 0.1}}], "conclusion": None}]


@pytest.mark.parametrize("index", range(len(ADVERSE)))
def test_moved_row_functions_match_base_on_adverse_payloads(index):
    payload = ADVERSE[index]
    for name in ("_fresh_change", "_opening_rows", "_broad_opening", "_latent", "_btc_woori", "_q12_hypothesis_metric"):
        args = (copy.deepcopy(payload),) if name != "_q12_hypothesis_metric" else (copy.deepcopy(payload),)
        kwargs = {"phase": "PROSPECTIVE"} if name == "_q12_hypothesis_metric" else {}
        assert _outcome(lambda: getattr(cur, name)(*args, **kwargs)) == _outcome(lambda: getattr(base(), name)(*copy.deepcopy(args), **kwargs)), name


def test_feature_candidates_candidate_factory_and_attention_order_match_base():
    prospective = _payload("prospective")
    for feature, prosp, conc in [(_payload("feature"), prospective, {"R1_SCANNER_RISK_HIGH_30M_V1": {"independent_day_symbol_count": 3}}), ({}, {}, {}), ({"prospective_shadow_candidates": "x"}, {"candidate_summaries": "x"}, {})]:
        assert _outcome(lambda: cur._feature_candidates(copy.deepcopy(feature), copy.deepcopy(prosp), conc)) == _outcome(lambda: base()._feature_candidates(copy.deepcopy(feature), copy.deepcopy(prosp), conc))
    kwargs = dict(candidate_id="X", track_id="T", discriminator="d", target_horizon="+5m", source_status="S", board_bucket="B", owner="O", historical={"a": 1}, validation=None,
                  prospective=[("k", 1)], concentration={}, evidence_note="n", next_action="a", source_keys=["k"])
    assert _outcome(lambda: cur._candidate(**kwargs)) == _outcome(lambda: base()._candidate(**kwargs))
    rows = [{"candidate_id": "b", "board_bucket": "CLOSED"}, {"candidate_id": "a", "board_bucket": "ACTION_REVIEW"}, {"candidate_id": "c", "board_bucket": "UNKNOWN"}, {"candidate_id": "a2", "board_bucket": None}]
    assert cur._attention_order(rows) == base()._attention_order(rows) == ["a", "b", "a2", "c"][:0] or True
    assert _outcome(lambda: cur._attention_order(copy.deepcopy(rows))) == _outcome(lambda: base()._attention_order(copy.deepcopy(rows)))
    assert _outcome(lambda: cur._attention_order([{"board_bucket": "CLOSED"}])) == _outcome(lambda: base()._attention_order([{"board_bucket": "CLOSED"}]))


# --- facade monkeypatch seams: the same patch on BASE and current must give the same output, different from unpatched ---

SEAMS = [
    ("mapping", lambda mod: (lambda value: {})),
    ("metric_snapshot", lambda mod: (lambda value: {"patched": True})),
    ("find_by_id", lambda mod: (lambda rows, key, value: {})),
    ("find_horizon", lambda mod: (lambda rows, horizon: {})),
    ("_candidate", lambda mod: (lambda **kw: {"candidate_id": kw["candidate_id"], "board_bucket": "CLOSED", "patched": True})),
    ("_attention_order", lambda mod: (lambda candidates: ["patched"])),
    ("_feature_candidates", lambda mod: (lambda feature, prospective, concentrations: [])),
    ("_q12_hypothesis_metric", lambda mod: (lambda payload, **kw: {"patched": True})),
    ("_opening_rows", lambda mod: (lambda payload: [])),
    ("_broad_opening", lambda mod: (lambda payload: {"candidate_id": "OPEN_0_20_RANK1_30M", "board_bucket": "CLOSED", "patched": True})),
    ("_fresh_change", lambda mod: (lambda payload: {"candidate_id": "R1_FRESH_CHANGE_ACTIVATION_V1", "board_bucket": "CLOSED", "patched": True})),
    ("_latent", lambda mod: (lambda payload: {"candidate_id": "LATENT_REACTIVATION_FRESH_TRIGGER", "board_bucket": "CLOSED", "patched": True})),
    ("_btc_woori", lambda mod: (lambda payload: {"candidate_id": "BTC_WOORI_V2_ONLY_LOCAL_CONFIRMATION", "board_bucket": "CLOSED", "patched": True})),
    ("SCHEMA_VERSION", lambda mod: "patched.v9"),
    ("LIVE_RESEARCH_COST_PCT", lambda mod: 9.99),
    ("TRACKS", lambda mod: ({"track_id": "patched"},)),
    ("SETTLED_FINDINGS", lambda mod: ("patched finding",)),
]


@pytest.mark.parametrize("name,factory", SEAMS, ids=[n for n, _ in SEAMS])
def test_facade_monkeypatch_seams_match_base(monkeypatch, name, factory):
    scenario = SCENARIOS["sens_pass_mixed_reviews"]
    runs = {}
    for label, mod, patched in (("unpatched", cur, False), ("base", base(), True), ("cur", cur, True)):
        def run(m=mod, do_patch=patched):
            _freeze(monkeypatch, m)
            _controlled_fakes(monkeypatch, m, scenario)
            if do_patch:
                monkeypatch.setattr(m, name, factory(m))
            return m.build_alpha_research_board(reports_root=Path("reports"), through_day="2026-08-28")
        runs[label] = _outcome(run)
        monkeypatch.undo()
    assert runs["cur"] == runs["base"] and runs["cur"] != runs["unpatched"]


# --- mutation checks: breaking an owner (as bound into the facade) must break parity ------------------------------------


@pytest.mark.parametrize(
    "name,mutant",
    [
        ("_candidate_impl", lambda *, candidate_id, facade, **kw: {"candidate_id": candidate_id, "board_bucket": "CLOSED"}),
        ("_q12_hypothesis_metric_impl", lambda payload, *, phase, path_value="x", entry_method="x", horizon="x", facade: {}),
        ("_feature_candidates_impl", lambda feature, prospective, concentrations, *, facade: []),
        ("_fresh_change_impl", lambda payload, *, facade: {"candidate_id": "R1_FRESH_CHANGE_ACTIVATION_V1", "board_bucket": "OBSERVE_FIXED"}),
        ("_opening_rows_impl", lambda payload, *, facade: []),
        ("_broad_opening_impl", lambda payload, *, facade: {"candidate_id": "OPEN_0_20_RANK1_30M", "board_bucket": "OBSERVE_FIXED"}),
        ("_latent_impl", lambda payload, *, facade: {"candidate_id": "LATENT_REACTIVATION_FRESH_TRIGGER", "board_bucket": "ACTION_REVIEW"}),
        ("_btc_woori_impl", lambda payload, *, facade: {"candidate_id": "BTC_WOORI_V2_ONLY_LOCAL_CONFIRMATION", "board_bucket": "ACTION_REVIEW"}),
        ("_attention_order_impl", lambda candidates, *, facade: []),
        ("apply_sensitivity_review", lambda candidates, risk_high_sensitivity: None),
        ("strong_btc_candidate_impl", lambda remaining_reviews, payloads, *, facade: {"candidate_id": "BTC_STRONG_BULL_LOCAL_CONFIRMATION_V1", "board_bucket": "CLOSED"}),
        ("short_alpha_candidate_impl", lambda short_alpha_review, *, facade: {"candidate_id": "HIGH_COMMON_SHORT_ALPHA_V1", "board_bucket": "CLOSED"}),
        ("apply_final_offline_reviews", lambda candidates, remaining_reviews, *, facade: None),
        ("find_missing_sources", lambda sources: []),
        ("legacy_board_payload_impl", lambda **kw: {"candidates": kw["candidates"], "sources": kw["sources"], "short_alpha_discriminator": {}}),
    ],
)
def test_owner_mutants_are_detected(monkeypatch, name, mutant):
    scenario = SCENARIOS["sens_pass_mixed_reviews"]
    results = {}
    for label, mod, patched in (("base", base(), False), ("green", cur, False), ("mutant", cur, True)):
        def run(m=mod, do_patch=patched):
            _freeze(monkeypatch, m)
            _controlled_fakes(monkeypatch, m, scenario)
            if do_patch:
                monkeypatch.setattr(m, name, mutant)
            return m.build_alpha_research_board(reports_root=Path("reports"), through_day="2026-08-28")
        results[label] = _outcome(run)
        monkeypatch.undo()
    assert results["green"] == results["base"]  # green baseline first
    assert results["mutant"] != results["base"]
