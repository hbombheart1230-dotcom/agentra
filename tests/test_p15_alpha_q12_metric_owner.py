"""P15 A4: alpha board ``_q12_hypothesis_metric`` moved to builder_q12_hypothesis_metric; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting.alpha_research_board import builder as b
from libs.reporting.alpha_research_board import builder_q12_hypothesis_metric as owner

GOLDEN = ["55df25e78727fd47918059fb64134206e130eb7986e4e74414b118715605ca6e", "55df25e78727fd47918059fb64134206e130eb7986e4e74414b118715605ca6e", "55df25e78727fd47918059fb64134206e130eb7986e4e74414b118715605ca6e", "55df25e78727fd47918059fb64134206e130eb7986e4e74414b118715605ca6e", "55df25e78727fd47918059fb64134206e130eb7986e4e74414b118715605ca6e", "55df25e78727fd47918059fb64134206e130eb7986e4e74414b118715605ca6e", "55df25e78727fd47918059fb64134206e130eb7986e4e74414b118715605ca6e", "55df25e78727fd47918059fb64134206e130eb7986e4e74414b118715605ca6e", "04c0fa0b74c63eb929909e1eaa59657f949a3ee53db9cc63cb6cfb38d59026b3", "55df25e78727fd47918059fb64134206e130eb7986e4e74414b118715605ca6e", "1678ef861e15b097ac4aadb26f11b8f8398e2ebdc07e9e16b2031bf67a6bacc4", "55df25e78727fd47918059fb64134206e130eb7986e4e74414b118715605ca6e", "55df25e78727fd47918059fb64134206e130eb7986e4e74414b118715605ca6e", "55df25e78727fd47918059fb64134206e130eb7986e4e74414b118715605ca6e", "55df25e78727fd47918059fb64134206e130eb7986e4e74414b118715605ca6e", "55df25e78727fd47918059fb64134206e130eb7986e4e74414b118715605ca6e"]   # row-major: payload x kwargs

Q12 = [
    {},
    {"rows": []},
    {"rows": [
        {"evidence_phase": "P", "axis": "hypothesis_path", "value": "FAST_BUY_ALL_PASS", "entry_method": "09:05", "horizon": "+30m", "metrics": {"count": 4, "win_rate": 0.5, "expectancy_pct": 0.1}},
        {"evidence_phase": "P", "axis": "hypothesis_path", "value": "FAST_BUY_ALL_PASS", "entry_method": "09:05", "horizon": "+30m", "metrics": {"count": 9}},
        {"evidence_phase": "Q", "axis": "hypothesis_path", "value": "OTHER", "entry_method": "09:10", "horizon": "+60m", "metrics": {"count": 7, "win_rate": 0.9}},
        "junk", None]},
    {"rows": "junk"},
]
Q12_KW = [dict(phase="P"), dict(phase="Q"), dict(phase="Q", path_value="OTHER", entry_method="09:10", horizon="+60m"), dict(phase="P", horizon="+5m")]
FEATURE = [
    ({}, {}, {}),
    ({"prospective_shadow_candidates": [{"feature": "scanner.risk_band", "category": "HIGH", "decision": "HIST_OK", "train": {"count": 30, "win_rate": 0.6}, "validation": {"count": 10}},
                                        {"feature": "chart.daily_ma5_20_cross_state", "category": "POST_CROSS_EXTENDED", "train": {"count": 5}}, "junk"]},
     {"candidate_summaries": [
         {"candidate_id": "R1_SCANNER_RISK_HIGH_30M_V1", "candidate": {"expected_value": "HIGH", "feature_path": "scanner.risk_band"}, "decision": {"status": "SINGLE_BEHAVIOR_PATCH_REVIEW_ELIGIBLE"}, "branch": {"count": 12, "win_rate": 0.7}},
         {"candidate_id": "R1_ENTRY_DAILY_MA5_20_EXTENDED_15M_V1", "candidate": {"expected_value": "POST_CROSS_EXTENDED", "feature_path": "chart.daily_ma5_20_cross_state"}, "decision": {"status": "REJECTED"}, "branch": {"count": 3}}]},
     {"R1_SCANNER_RISK_HIGH_30M_V1": {"largest_day_share": 0.4, "largest_symbol_share": 0.5}}),
    ({"prospective_shadow_candidates": "junk"}, {"candidate_summaries": "junk"}, {"x": 1}),
    ({"prospective_shadow_candidates": [{"feature": "scanner.risk_band", "category": "HIGH", "decision": "FALLBACK"}]}, {"candidate_summaries": [{"candidate_id": "R1_SCANNER_RISK_HIGH_30M_V1", "candidate": {"expected_value": "HIGH", "feature_path": "scanner.risk_band"}}]}, {}),
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


CASES = [(p, kw) for p in Q12 for kw in Q12_KW]


@pytest.mark.parametrize("i", range(len(CASES)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    payload, kw = CASES[i]
    snap = copy.deepcopy(payload)
    assert _safe(lambda: b._q12_hypothesis_metric(payload, **kw)) == GOLDEN[i]
    assert _safe(lambda: owner._q12_hypothesis_metric(payload, facade=b, **kw)) == GOLDEN[i]
    assert payload == snap


def test_first_matching_row_wins_and_mismatches_fall_back_to_empty_snapshot():
    first = b._q12_hypothesis_metric(Q12[2], phase="P")
    assert first == b.metric_snapshot({"count": 4, "win_rate": 0.5, "expectancy_pct": 0.1}) and first != b.metric_snapshot({"count": 9})
    assert b._q12_hypothesis_metric(Q12[2], phase="Q", path_value="OTHER", entry_method="09:10", horizon="+60m") == b.metric_snapshot({"count": 7, "win_rate": 0.9})
    empty = b.metric_snapshot({})
    for kw in (dict(phase="X"), dict(phase="P", path_value="N"), dict(phase="P", entry_method="09:10"), dict(phase="P", horizon="+60m")):
        assert b._q12_hypothesis_metric(Q12[2], **kw) == empty
    assert b._q12_hypothesis_metric({}, phase="P") == empty and b._q12_hypothesis_metric({"rows": "junk"}, phase="P") == empty


def test_facade_use_time_patches_reach_the_owner(monkeypatch):
    seen = []
    monkeypatch.setattr(b, "metric_snapshot", lambda v: (seen.append(v), "SNAP")[1])
    assert b._q12_hypothesis_metric(Q12[2], phase="P") == "SNAP" and seen == [{"count": 4, "win_rate": 0.5, "expectancy_pct": 0.1}]
    real_mapping = b.mapping
    rows = []
    monkeypatch.setattr(b, "mapping", lambda v: (rows.append(v), real_mapping(v))[1])
    b._q12_hypothesis_metric(Q12[2], phase="P")
    assert rows and rows[0] is Q12[2]["rows"][0]


def test_owner_does_not_import_the_builder_and_wrapper_is_thin():
    assert "from .builder import" not in inspect.getsource(owner) and "import builder\n" not in inspect.getsource(owner)
    assert len(inspect.getsource(b._q12_hypothesis_metric).splitlines()) <= 10
