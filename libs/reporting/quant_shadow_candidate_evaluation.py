from __future__ import annotations

import json
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from libs.reporting.json_array_stream import iter_json_array
from libs.reporting.q8_evaluation_contract import (
    CANONICAL_DEDUPE_KEY_FIELDS,
    PROMOTION_CANDIDATE_MIN_DAYS,
    PROMOTION_CANDIDATE_MIN_OBSERVED,
    TRUSTED_FORWARD_MIN_COUNT,
    TRUSTED_FORWARD_MIN_COVERAGE,
    build_q8_trust_gate,
    candidate_day as q8_candidate_day,
    dedupe_q8_candidates,
    entry_lane_subtype as q8_entry_lane_subtype,
)
from libs.reporting.quant_shadow_forward_outcomes import attach_forward_outcomes
from libs.runtime.quant.enforcement import build_entry_quant_enforcement
from libs.runtime.quant.entry_lane_observation import build_entry_lane_observation
from libs.runtime.quant.vwap_reclaim_observation import classify_below_vwap_reclaim_observation
from libs.reporting import quant_shadow_scalar_projection as _scalar_owner
from libs.reporting import quant_shadow_day_projection as _day_owner
from libs.reporting import quant_shadow_counter_projection as _counter_owner
from libs.reporting import quant_shadow_blocker_projection as _blocker_owner
from libs.reporting import quant_shadow_reason_projection as _reason_owner
from libs.reporting import quant_shadow_runnerup_projection as _runnerup_owner
from libs.reporting import quant_shadow_mean_projection as _mean_owner
from libs.reporting import quant_shadow_scorecard_signal_projection as _scorecard_signal_owner
from libs.reporting import quant_shadow_cost_floor_projection as _cost_floor_owner
from libs.reporting import quant_shadow_entry_decision_projection as _entry_decision_owner
from libs.reporting import quant_shadow_tactic_projection as _tactic_owner
from libs.reporting import quant_shadow_tactic_tier_projection as _tactic_tier_owner
from libs.reporting import quant_shadow_forward_base_projection as _forward_base_owner
from libs.reporting import quant_shadow_forward_outcome_projection as _forward_outcome_owner
from libs.reporting import quant_shadow_entry_shape_projection as _entry_shape_owner
from libs.reporting import quant_shadow_checkpoint_projection as _checkpoint_owner
from libs.reporting import quant_shadow_opening_probe_projection as _opening_probe_owner
from libs.reporting import quant_shadow_opening_probe_enter_projection as _opening_enter_owner
from libs.reporting import quant_shadow_largecap_probe_projection as _largecap_probe_owner
from libs.reporting import quant_shadow_largecap_enter_projection as _largecap_enter_owner
from libs.reporting import quant_shadow_entry_shape_payload_projection as _shape_payload_owner
from libs.reporting import quant_shadow_vwap_observation_payload_projection as _vwap_payload_owner
from libs.reporting import quant_shadow_forward_summary_projection as _forward_summary_owner
from libs.reporting import quant_shadow_top_forward_groups_projection as _top_groups_owner
from libs.reporting import quant_shadow_vwap_observation_projection as _vwap_obs_owner
from libs.reporting import quant_shadow_entry_lane_observation_projection as _lane_obs_owner
from libs.reporting import quant_shadow_entry_lane_payload_projection as _lane_payload_owner
from libs.reporting import quant_shadow_entry_lane_forward_projection as _lane_forward_owner
from libs.reporting import quant_shadow_scorecard_rows_projection as _scorecard_rows_owner
from libs.reporting import quant_shadow_named_forward_rows_projection as _named_rows_owner
from libs.reporting import quant_shadow_format_rows_projection as _format_rows_owner
from libs.reporting import quant_shadow_format_forward_projection as _format_forward_owner
from libs.reporting import quant_shadow_text_projection as _text_owner
from libs.reporting import quant_shadow_json_projection as _json_owner
from libs.reporting import quant_shadow_day_paths_projection as _day_paths_owner
from libs.reporting import quant_shadow_drop_q9_projection as _drop_q9_owner
from libs.reporting import quant_shadow_format_scorecard_projection as _format_scorecard_owner
from libs.reporting import quant_shadow_readiness_projection as _readiness_owner
from libs.reporting import quant_shadow_root_projection as _root_owner
from libs.reporting import quant_shadow_no_trade_scorecard_projection as _no_trade_owner
from libs.reporting import quant_shadow_q9_windows_projection as _q9_windows_owner
from libs.reporting import quant_shadow_q9_augment_projection as _q9_augment_owner
from libs.reporting import quant_shadow_trust_gate_projection as _trust_gate_owner
from libs.reporting import quant_shadow_render_lines_projection as _render_lines_owner
from libs.reporting import quant_shadow_guard_observation_projection as _guard_obs_owner
from libs.reporting import quant_shadow_payload_iterator_projection as _payload_iter_owner
from libs.reporting import quant_shadow_promotion_projection as _promotion_owner
from libs.reporting import quant_shadow_evaluation_builder_projection as _eval_builder_owner


def _text(value: Any) -> str:
    return _text_owner._text(value)


def _bool(value: Any) -> bool:
    return _scalar_owner._bool(value)


def _read_json(path: Path) -> Any:
    return _json_owner._read_json(path, facade=sys.modules[__name__])


def shadow_candidate_root_for_reports(reports_root: Path) -> Path:
    return _root_owner.shadow_candidate_root_for_reports(reports_root, facade=sys.modules[__name__])


def _iter_days(start: str, end: str) -> Iterable[str]:
    yield from _day_owner._iter_days(start, end, facade=sys.modules[__name__])


def _json_paths_for_day(root: Path, day: str) -> List[Path]:
    return _day_paths_owner._json_paths_for_day(root, day)


def _q9_windows_by_id(reports_root: Path, day: str) -> Dict[str, Dict[str, Any]]:
    return _q9_windows_owner._q9_windows_by_id(reports_root, day, facade=sys.modules[__name__])


def _augment_missing_q9_commander_candidate(
    payload: Dict[str, Any],
    *,
    windows_by_id: Mapping[str, Mapping[str, Any]],
) -> Dict[str, Any]:
    return _q9_augment_owner._augment_missing_q9_commander_candidate(payload, windows_by_id=windows_by_id, facade=sys.modules[__name__])


# The only top-level payload keys the closeout-path consumers read (candidate
# evaluation, Q8 blocker review, strategist LLM evaluation). Everything else in
# a shadow payload -- chiefly `q9_decision_candidates`, ~65% of the bytes -- is
# dead weight for them. Closeout passes this to `keys=` so a full trading day
# is not held in memory (the 10-06 closeout was OOM-killed at the 1 GiB cap).
CANDIDATE_EVALUATION_PAYLOAD_KEYS: Tuple[str, ...] = ("candidates", "generated_at")

# Keys of each `q9_decision_candidates` row that are ~83% of its bytes and that the full-chain
# component review, the scanner-quality review and the cost-basis comparison never read
# (verified statically and with access-trapping values on real days -- see
# tests/test_closeout_memory_bounds.py). Those consumers pass `drop_q9_row_keys=` so a day of
# q9 rows is not held in full. Consumers that DO read them (stage-2 authority, episode scanner
# review, evaluation lens ...) must not use it.
Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN: Tuple[str, ...] = (
    "entry_lane_observation",
    "score_breakdown",
    "compact_feature_snapshot",
    "below_vwap_reclaim_observation",
)


def _drop_q9_row_keys(payload: Dict[str, Any], drop: Optional[Sequence[str]]) -> Dict[str, Any]:
    """Remove `drop` keys from every q9 decision-candidate row of `payload` (no-op when `drop` is empty)."""
    return _drop_q9_owner._drop_q9_row_keys(payload, drop)


def load_quant_shadow_candidate_payloads(
    *,
    reports_root: Path,
    days: Sequence[str],
    keys: Optional[Sequence[str]] = None,
    drop_q9_row_keys: Optional[Sequence[str]] = None,
) -> List[Dict[str, Any]]:
    return list(
        iter_quant_shadow_candidate_payloads(
            reports_root=reports_root,
            days=days,
            keys=keys,
            drop_q9_row_keys=drop_q9_row_keys,
        )
    )


def iter_quant_shadow_candidate_payloads(
    *,
    reports_root: Path,
    days: Sequence[str],
    keys: Optional[Sequence[str]] = None,
    drop_q9_row_keys: Optional[Sequence[str]] = None,
) -> Iterable[Dict[str, Any]]:
    """Yield one payload dict per shadow file.

    `keys=None` (default) yields the complete payload, unchanged. With `keys`,
    each payload is projected onto those top-level keys as soon as it is parsed
    (the full parse is released immediately) and the q9 commander augmentation
    -- which only ever rewrites `q9_decision_candidates` -- is skipped together
    with its multi-hundred-MiB `q9_decision_windows.json` load, unless the
    caller asked for that key.
    """
    yield from _payload_iter_owner.iter_quant_shadow_candidate_payloads(reports_root=reports_root, days=days, keys=keys, drop_q9_row_keys=drop_q9_row_keys, facade=sys.modules[__name__])


def iter_quant_shadow_candidate_payloads_for_range(
    *,
    reports_root: Path,
    start: str,
    end: str,
    drop_q9_row_keys: Optional[Sequence[str]] = None,
) -> Iterable[Dict[str, Any]]:
    return iter_quant_shadow_candidate_payloads(
        reports_root=reports_root,
        days=list(_iter_days(start, end)),
        drop_q9_row_keys=drop_q9_row_keys,
    )


def load_quant_shadow_candidate_payloads_for_range(
    *,
    reports_root: Path,
    start: str,
    end: str,
    drop_q9_row_keys: Optional[Sequence[str]] = None,
    keys: Optional[Sequence[str]] = None,
) -> List[Dict[str, Any]]:
    return load_quant_shadow_candidate_payloads(
        reports_root=reports_root,
        days=list(_iter_days(start, end)),
        keys=keys,
        drop_q9_row_keys=drop_q9_row_keys,
    )


def _top_counter(counter: Counter[str], *, limit: int = 8) -> List[Dict[str, Any]]:
    return _counter_owner._top_counter(counter, limit=limit)


def _row_blockers(row: Mapping[str, Any]) -> List[str]:
    return _blocker_owner._row_blockers(row, facade=sys.modules[__name__])


def _cost_floor_state(row: Mapping[str, Any]) -> str:
    return _cost_floor_owner._cost_floor_state(row, facade=sys.modules[__name__])


def _entry_quant_decision(row: Mapping[str, Any]) -> str:
    return _entry_decision_owner._entry_quant_decision(row, facade=sys.modules[__name__])


def _tactic_id(row: Mapping[str, Any]) -> str:
    return _tactic_owner._tactic_id(row, facade=sys.modules[__name__])


def _tactic_suitability_tier(row: Mapping[str, Any]) -> str:
    return _tactic_tier_owner._tactic_suitability_tier(row, facade=sys.modules[__name__])


def _forward_base(row: Mapping[str, Any]) -> Dict[str, Any]:
    return _forward_base_owner._forward_base(row, facade=sys.modules[__name__])


def _forward_outcome(row: Mapping[str, Any]) -> Dict[str, Any]:
    return _forward_outcome_owner._forward_outcome(row, facade=sys.modules[__name__])


def _candidate_day(row: Mapping[str, Any]) -> str:
    return q8_candidate_day(row)


def _entry_lane_subtype(row: Mapping[str, Any]) -> str:
    return q8_entry_lane_subtype(row)


def _dedupe_candidates(rows: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    return dedupe_q8_candidates(rows)


def _opening_probe(row: Mapping[str, Any]) -> Dict[str, Any]:
    return _opening_probe_owner._opening_probe(row, facade=sys.modules[__name__])


def _opening_probe_would_enter(row: Mapping[str, Any]) -> bool:
    return _opening_enter_owner._opening_probe_would_enter(row, facade=sys.modules[__name__])


def _largecap_surge_probe(row: Mapping[str, Any]) -> Dict[str, Any]:
    return _largecap_probe_owner._largecap_surge_probe(row, facade=sys.modules[__name__])


def _largecap_surge_would_enter(row: Mapping[str, Any]) -> bool:
    return _largecap_enter_owner._largecap_surge_would_enter(row, facade=sys.modules[__name__])


def _actionable_entry_guard_block(row: Mapping[str, Any]) -> bool:
    return _guard_obs_owner._actionable_entry_guard_block(row, facade=sys.modules[__name__])


def _count_reason(candidates: Sequence[Mapping[str, Any]], names: set[str]) -> int:
    return _reason_owner._count_reason(candidates, names, facade=sys.modules[__name__])


def _runner_up_risk_count(candidates: Sequence[Mapping[str, Any]]) -> int:
    return _runnerup_owner._runner_up_risk_count(candidates, facade=sys.modules[__name__])


def _entry_shape(row: Mapping[str, Any]) -> str:
    return _entry_shape_owner._entry_shape(row, facade=sys.modules[__name__])


def _entry_shape_payload(candidates: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    return _shape_payload_owner._entry_shape_payload(candidates, facade=sys.modules[__name__])


def _below_vwap_reclaim_observation(row: Mapping[str, Any]) -> Dict[str, Any]:
    return _vwap_obs_owner._below_vwap_reclaim_observation(row, facade=sys.modules[__name__])


def _below_vwap_reclaim_observation_payload(candidates: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    return _vwap_payload_owner._below_vwap_reclaim_observation_payload(candidates, facade=sys.modules[__name__])


def _entry_lane_observation(row: Mapping[str, Any]) -> Dict[str, Any]:
    return _lane_obs_owner._entry_lane_observation(row, facade=sys.modules[__name__])


def _entry_lane_observation_payload(candidates: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    return _lane_payload_owner._entry_lane_observation_payload(candidates, facade=sys.modules[__name__])


def _mean(values: Sequence[float]) -> float | None:
    return _mean_owner._mean(values)


def _checkpoint_value(row: Mapping[str, Any], checkpoint: str, metric: str) -> float | None:
    return _checkpoint_owner._checkpoint_value(row, checkpoint, metric, facade=sys.modules[__name__])


def _forward_outcome_summary(rows: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    return _forward_summary_owner._forward_outcome_summary(rows, facade=sys.modules[__name__])


def _top_forward_groups(groups: Mapping[str, List[Mapping[str, Any]]], *, limit: int = 10) -> List[Dict[str, Any]]:
    return _top_groups_owner._top_forward_groups(groups, limit=limit, facade=sys.modules[__name__])


def _entry_lane_forward_outcomes(candidates: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    return _lane_forward_owner._entry_lane_forward_outcomes(candidates, facade=sys.modules[__name__])


def _scorecard_return_signal(row: Mapping[str, Any]) -> float | None:
    return _scorecard_signal_owner._scorecard_return_signal(row)


def _scorecard_rows(rows: Sequence[Mapping[str, Any]], *, mode: str, limit: int = 5) -> List[Dict[str, Any]]:
    return _scorecard_rows_owner._scorecard_rows(rows, mode=mode, limit=limit, facade=sys.modules[__name__])


def _named_forward_rows(rows: Sequence[Mapping[str, Any]], names: set[str]) -> List[Dict[str, Any]]:
    return _named_rows_owner._named_forward_rows(rows, names, facade=sys.modules[__name__])


def _no_trade_scorecard(
    *,
    candidates: Sequence[Mapping[str, Any]],
    entry_lane_forward_outcomes: Mapping[str, Any],
    would_enter_count: int,
    opening_probe_would_enter: int,
    largecap_probe_would_enter: int,
) -> Dict[str, Any]:
    return _no_trade_owner._no_trade_scorecard(candidates=candidates, entry_lane_forward_outcomes=entry_lane_forward_outcomes, would_enter_count=would_enter_count, opening_probe_would_enter=opening_probe_would_enter, largecap_probe_would_enter=largecap_probe_would_enter, facade=sys.modules[__name__])


def _evaluation_trust_gate(
    *,
    raw_candidate_count: int,
    deduped_candidate_count: int,
    trusted_forward_count: int,
    trusted_forward_coverage: float,
    no_trade_scorecard: Mapping[str, Any],
) -> Dict[str, Any]:
    return _trust_gate_owner._evaluation_trust_gate(raw_candidate_count=raw_candidate_count, deduped_candidate_count=deduped_candidate_count, trusted_forward_count=trusted_forward_count, trusted_forward_coverage=trusted_forward_coverage, no_trade_scorecard=no_trade_scorecard, facade=sys.modules[__name__])


def _promotion_candidate(candidates: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    return _promotion_owner._promotion_candidate(candidates, facade=sys.modules[__name__])


def _shadow_readiness(candidates: Sequence[Mapping[str, Any]], promotion: Mapping[str, Any]) -> Dict[str, Any]:
    return _readiness_owner._shadow_readiness(candidates, promotion, facade=sys.modules[__name__])


def build_quant_shadow_candidate_evaluation(
    payloads: Iterable[Mapping[str, Any]],
    *,
    symbol: str = "",
) -> Dict[str, Any]:
    return _eval_builder_owner.build_quant_shadow_candidate_evaluation(payloads, symbol=symbol, facade=sys.modules[__name__])


def _format_rows(rows: Sequence[Mapping[str, Any]], *, limit: int = 4) -> str:
    return _format_rows_owner._format_rows(rows, limit=limit, facade=sys.modules[__name__])


def _format_forward_rows(rows: Sequence[Mapping[str, Any]], *, limit: int = 4) -> str:
    return _format_forward_owner._format_forward_rows(rows, limit=limit, facade=sys.modules[__name__])


def _format_scorecard_rows(rows: Sequence[Mapping[str, Any]], *, limit: int = 4) -> str:
    return _format_scorecard_owner._format_scorecard_rows(rows, limit=limit, facade=sys.modules[__name__])


def render_quant_shadow_candidate_evaluation_lines(payload: Mapping[str, Any] | None) -> List[str]:
    return _render_lines_owner.render_quant_shadow_candidate_evaluation_lines(payload, facade=sys.modules[__name__])
