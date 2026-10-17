"""Monitor observation views; policy/effects remain at the facade."""
from __future__ import annotations

from typing import Any, Dict


def _empty_entry_transition_trace(*, facade) -> Dict[str, Any]:
    return {
        "reclaim_distance_to_ready": None,
        "vwap_reclaim_progress": None,
        "rebound_progress": None,
        "volume_distance_to_ready": None,
        "breakout_distance_to_ready": None,
        "transition_readiness_score": None,
        "last_blocking_axis": "",
        "became_ready_this_cycle": False,
        "extended_from_vwap_improvement": None,
        "volume_ratio_improvement": None,
        "breakout_gap_improvement": None,
        "transition_happening_now": False,
        "volume_recovery_slope": None,
        "volume_recovery_recent": False,
    }


def _empty_monitor_signal_evidence(*, score_threshold: float = 3.0, facade) -> Dict[str, Any]:
    return facade._build_monitor_signal_evidence(
        reclaim_score=0.0,
        volume_score=0.0,
        pullback_score=0.0,
        breakout_score=0.0,
        confidence_score=0.0,
        confidence_threshold=0.55,
        entry_quality_score=0.0,
        breakout_quality_score=0.0,
        pullback_quality_score=0.0,
        entry_quality_path="",
        reclaim_ok=False,
        volume_ok=False,
        pullback_ok=False,
        breakout_ok=False,
        rebound_ok=False,
        reclaim_gate_ok=False,
        breakout_path_ok=False,
        pullback_volume_path_ok=False,
        extension_ok=False,
        too_extended=False,
        reclaim_strength=0.0,
        rebound_strength=0.0,
        transition_readiness_score=0.0,
        reclaim_distance_to_ready=None,
        volume_distance_to_ready=None,
        breakout_distance_to_ready=None,
        score_breakdown={},
        score_threshold=score_threshold,
    )


def _empty_monitor_policy_interpretation(*, facade) -> Dict[str, Any]:
    return {
        "policy_available": False,
        "entry_style": None,
        "contract_source": None,
        "policy_schema_available": False,
        "policy_schema_version": None,
        "policy_schema_raw_keys": [],
        "interpretation_basis": "none",
        "explicit_fields_used": [],
        "required_checks": [],
        "preferred_checks": [],
        "relaxable_checks": [],
        "blockers": [],
        "priority_hints": {
            "volume_priority": None,
            "reclaim_priority": None,
            "breakout_priority": None,
            "pullback_priority": None,
        },
        "evidence_focus": {
            "primary": [],
            "secondary": [],
        },
        "policy_source": None,
        "policy_adjustments": [],
        "spec_validation_notes": [],
        "notes": [],
    }


def _empty_monitor_policy_interpreter_trace(*, facade) -> Dict[str, Any]:
    return {
        "available": False,
        "policy_available": False,
        "entry_style": None,
        "focus_alignment": {
            "primary_focus": [],
            "secondary_focus": [],
        },
        "check_status": {
            "required": [],
            "preferred": [],
            "relaxable": [],
            "blockers": [],
        },
        "alignment_summary": {
            "policy_alignment_state": None,
            "primary_blocker": None,
            "secondary_blockers": [],
        },
        "notes": [],
    }


def _empty_monitor_policy_alignment_summary(*, facade) -> Dict[str, Any]:
    return {
        "available": False,
        "policy_available": False,
        "entry_style": None,
        "alignment_state": None,
        "primary_blocker": None,
        "secondary_blockers": [],
        "focus_mismatch": [],
        "top_failed_required_checks": [],
        "top_failed_preferred_checks": [],
        "top_relaxable_gaps": [],
        "summary_notes": [],
    }


def _empty_monitor_policy_aware_gating(*, facade) -> Dict[str, Any]:
    return {
        "available": False,
        "applied": False,
        "applied_hints": [],
        "required_failures": [],
        "relaxations_considered": [],
        "relaxations_applied": [],
        "blocked_by_required": [],
        "notes": [],
        "entry_tuning_flags": [],
        "reclaim_readiness_tuned": False,
        "reclaim_tuning_version": facade._RECLAIM_TUNING_VERSION,
        "reclaim_tuning_scope": facade._RECLAIM_TUNING_SCOPE,
        "reclaim_near_ready_distance_min": facade._RECLAIM_NEAR_READY_DISTANCE_MIN_BASE,
        "reclaim_tuning_band_used": "standard",
        "reclaim_evidence_explanation": "",
    }


def _empty_chart_structure_decision_hint(*, facade) -> Dict[str, Any]:
    return {
        "available": False,
        "applied": False,
        "mode": "none",
        "entry_style": None,
        "considered_features": [],
        "matched_features": [],
        "blocking_features": [],
        "notes": [],
    }


def _empty_human_chart_detail_context(*, facade) -> Dict[str, Any]:
    return {
        "schema_version": "human_chart_detail_context.v1",
        "available": False,
        "candle_quality_score": 0.5,
        "vwap_reference_quality_score": 0.5,
        "reward_room_score": 0.5,
        "multi_window_structure_score": 0.5,
        "observed": {},
        "notes": [],
    }
