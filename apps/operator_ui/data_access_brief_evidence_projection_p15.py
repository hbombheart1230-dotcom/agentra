"""Brief evidence normalization over already-read input; no IO, LLM or policy evaluation."""
from __future__ import annotations
from typing import List


def chart_evidence(canonical_trade, feature_coverage, chart_status, chart_note, *, facade):
    canonical_filter_bullets = list(canonical_trade.get("filter_bullets") or [])[:8]
    canonical_selection_bullets = list(canonical_trade.get("selection_bullets") or [])[:6]
    if facade._safe_int(feature_coverage.get("total"), 0) > 0:
        updated_bullets: List[str] = []
        replaced_chart_bullet = False
        for bullet in canonical_filter_bullets:
            text = str(bullet or "").strip()
            if text.lower().startswith("chart completeness filter:"):
                updated_bullets.append(f"chart completeness filter: {chart_status} - {chart_note}")
                replaced_chart_bullet = True
            else:
                updated_bullets.append(text)
        if not replaced_chart_bullet:
            updated_bullets.append(f"chart completeness filter: {chart_status} - {chart_note}")
        canonical_filter_bullets = updated_bullets[:8]
        canonical_filters_summary = (
            f"Scanner and guard checks used normalized chart coverage with {feature_coverage.get('present')}/{feature_coverage.get('total')} captured features."
        )
        updated_selection_bullets: List[str] = []
        replaced_selection_chart_bullet = False
        for bullet in canonical_selection_bullets:
            text = str(bullet or "").strip()
            if text.lower().startswith("chart / feature coverage:"):
                updated_selection_bullets.append(
                    f"Chart / feature coverage: {feature_coverage.get('present')}/{feature_coverage.get('total')}"
                )
                replaced_selection_chart_bullet = True
            else:
                updated_selection_bullets.append(text)
        if not replaced_selection_chart_bullet:
            updated_selection_bullets.append(
                f"Chart / feature coverage: {feature_coverage.get('present')}/{feature_coverage.get('total')}"
            )
        canonical_selection_bullets = updated_selection_bullets[:6]
    else:
        canonical_filters_summary = canonical_trade.get("filters_summary")
    return canonical_filter_bullets, canonical_filters_summary, canonical_selection_bullets


def merge_stop_evidence(monitor_stop_policy_trace, canonical_monitor_stop_policy_trace, canonical_monitor_snapshot_stop_policy_trace):
    if not any(value not in (None, "", []) for value in monitor_stop_policy_trace.values()):
        monitor_stop_policy_trace = dict(canonical_monitor_stop_policy_trace or {})
    elif canonical_monitor_stop_policy_trace:
        for key, value in canonical_monitor_stop_policy_trace.items():
            if monitor_stop_policy_trace.get(key) in (None, "", []):
                monitor_stop_policy_trace[key] = value
    if canonical_monitor_snapshot_stop_policy_trace:
        for key, value in canonical_monitor_snapshot_stop_policy_trace.items():
            if monitor_stop_policy_trace.get(key) in (None, "", []):
                monitor_stop_policy_trace[key] = value
    return monitor_stop_policy_trace
