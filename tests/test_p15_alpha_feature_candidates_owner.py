"""P15 A5: alpha board ``_feature_candidates`` moved to builder_feature_candidates; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting.alpha_research_board import builder as b
from libs.reporting.alpha_research_board import builder_feature_candidates as owner

GOLDEN = ["e760af640cfaf9ed7b8d9b7ba28c8860426ee835340bedf065720c8923c0d551", "e38dc11aa7b5658ee1c07c56ba245ae7999de56f5f9d826b423af15274522ab7", "e760af640cfaf9ed7b8d9b7ba28c8860426ee835340bedf065720c8923c0d551", "3858ace3f0546396ad2903ec995e10550160416db4ebd9b6b482bc192c2c37bb"]

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


@pytest.mark.parametrize("i", range(len(FEATURE)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    args = FEATURE[i]
    snap = copy.deepcopy(args)
    assert _safe(lambda: b._feature_candidates(*args)) == GOLDEN[i]
    assert _safe(lambda: owner._feature_candidates(*args, facade=b)) == GOLDEN[i]
    assert args == snap


def test_two_fixed_candidates_in_order_with_default_status():
    rows = b._feature_candidates({}, {}, {})
    assert [r["candidate_id"] for r in rows] == ["R1_SCANNER_RISK_HIGH_30M_V1", "R1_ENTRY_DAILY_MA5_20_EXTENDED_15M_V1"]
    assert [r["target_horizon"] for r in rows] == ["+30m", "+15m"] and all(r["source_status"] == "INSUFFICIENT_EVIDENCE" and r["board_bucket"] == "OBSERVE_FIXED" for r in rows)


def test_eligible_vs_rejected_buckets_notes_and_concentration():
    first, second = b._feature_candidates(*FEATURE[1])
    assert first["board_bucket"] == "ACTION_REVIEW" and first["source_status"] == "SINGLE_BEHAVIOR_PATCH_REVIEW_ELIGIBLE" and first["responsibility_if_proven"] == "SCANNER"
    assert first["evidence_note"] == "Prospective에서도 비교군을 이겼지만 날짜·종목 집중도 민감도 검토가 필요함."
    assert first["next_action"].startswith("집중 종목·최대 일자를 제외한")
    assert first["concentration"]["largest_day_share"] == 0.4 and first["historical"] == b.metric_snapshot({"count": 30, "win_rate": 0.6}) and first["validation"] == b.metric_snapshot({"count": 10})
    assert second["board_bucket"] == "OBSERVE_FIXED" and second["source_status"] == "REJECTED" and second["responsibility_if_proven"] == "MONITOR_ENTRY"
    assert second["evidence_note"] == "과거 방향성이 prospective에서 유지되지 못함." and second["next_action"] == "관측만 유지하고 과거 성과만으로 승격하지 않음."
    fallback = b._feature_candidates(*FEATURE[3])[0]
    assert fallback["source_status"] == "FALLBACK"                                       # historical decision used when prospective has no decision


def test_facade_candidate_spy_sees_both_candidates_in_order(monkeypatch):
    calls = []
    real = b._candidate
    monkeypatch.setattr(b, "_candidate", lambda **kw: (calls.append(kw), real(**kw))[1])
    out = b._feature_candidates(*FEATURE[1])
    assert [c["candidate_id"] for c in calls] == [r["candidate_id"] for r in out] and calls[0]["source_keys"] == ["feature_candidates", "prospective_candidates"]
    monkeypatch.setattr(b, "find_by_id", lambda rows, key, value: {"decision": {"status": "PATCHED"}})
    assert [r["source_status"] for r in b._feature_candidates(*FEATURE[1])] == ["PATCHED", "PATCHED"]


def test_owner_does_not_import_the_builder_and_wrapper_is_thin():
    assert "from .builder import" not in inspect.getsource(owner) and "import builder\n" not in inspect.getsource(owner)
    assert len(inspect.getsource(b._feature_candidates).splitlines()) <= 10
