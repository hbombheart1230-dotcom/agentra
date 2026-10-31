from __future__ import annotations

import sys
from typing import Any, Dict, List, Mapping

from libs.runtime.quant.decision import build_entry_quant_decision
from libs.runtime.quant.suitability import score_candidate_tactic_suitability
from libs.reporting import quant_tactic_items_projection as _items_owner
from libs.reporting import quant_tactic_fmt_projection as _fmt_owner
from libs.reporting import quant_tactic_mapping_projection as _mapping_owner
from libs.reporting import quant_tactic_pct_projection as _pct_owner
from libs.reporting import quant_tactic_decision_label_projection as _decision_label_owner
from libs.reporting import quant_tactic_reason_text_projection as _reason_text_owner
from libs.reporting import quant_tactic_monitor_projection as _monitor_owner
from libs.reporting import quant_tactic_nested_dicts_projection as _nested_dicts_owner
from libs.reporting import quant_tactic_first_nested_mapping_projection as _first_nested_owner
from libs.reporting import quant_tactic_symbol_projection as _symbol_owner
from libs.reporting import quant_tactic_playbook_projection as _playbook_owner
from libs.reporting import quant_tactic_entry_visibility_projection as _entry_vis_owner
from libs.reporting import quant_tactic_entry_info_projection as _entry_info_owner
from libs.reporting import quant_tactic_candidate_symbol_projection as _cand_symbol_owner
from libs.reporting import quant_tactic_scanner_chart_fit_projection as _chart_fit_owner
from libs.reporting import quant_tactic_value_projection as _tactic_value_owner
from libs.reporting import quant_tactic_mismatches_projection as _mismatches_owner
from libs.reporting import quant_tactic_exit_drifts_projection as _exit_drifts_owner


def _mapping(value: Any) -> Dict[str, Any]:
    return _mapping_owner._mapping(value, facade=sys.modules[__name__])


def _items(value: Any) -> List[str]:
    return _items_owner._items(value)


def _fmt(value: Any) -> str:
    return _fmt_owner._fmt(value)


def _pct(value: Any) -> str:
    return _pct_owner._pct(value)


def _decision_label(value: Any) -> str:
    return _decision_label_owner._decision_label(value)


def _reason_text(values: Any) -> str:
    return _reason_text_owner._reason_text(values, facade=sys.modules[__name__])


def _monitor(report: Mapping[str, Any]) -> Dict[str, Any]:
    return _monitor_owner._monitor(report, facade=sys.modules[__name__])


def _nested_dicts(value: Any, *, max_depth: int = 9) -> List[Dict[str, Any]]:
    return _nested_dicts_owner._nested_dicts(value, max_depth=max_depth, facade=sys.modules[__name__])


def _first_nested_mapping(root: Mapping[str, Any], key: str) -> Dict[str, Any]:
    return _first_nested_owner._first_nested_mapping(root, key, facade=sys.modules[__name__])


def _symbol(report: Mapping[str, Any]) -> str:
    return _symbol_owner._symbol(report, facade=sys.modules[__name__])


def _playbook(report: Mapping[str, Any], *, fallback: str = "") -> str:
    return _playbook_owner._playbook(report, fallback=fallback, facade=sys.modules[__name__])


def _entry_visibility(report: Mapping[str, Any]) -> Dict[str, Any]:
    return _entry_vis_owner._entry_visibility(report, facade=sys.modules[__name__])


def _entry_info_from_visibility(visibility: Mapping[str, Any], monitor: Mapping[str, Any]) -> Dict[str, Any]:
    return _entry_info_owner._entry_info_from_visibility(visibility, monitor, facade=sys.modules[__name__])


def _candidate_symbol(row: Mapping[str, Any]) -> str:
    return _cand_symbol_owner._candidate_symbol(row)


def _selected_candidate_row(report: Mapping[str, Any], symbol: str) -> Dict[str, Any]:
    target = str(symbol or "").strip()
    if not target:
        return {}
    candidates: List[Dict[str, Any]] = []
    for item in _nested_dicts(report):
        if _candidate_symbol(item) != target:
            continue
        if any(
            key in item
            for key in (
                "quant_factor_snapshot",
                "tactic_suitability",
                "scanner_chart_fit_score",
                "scanner_chart_fit_components",
                "score_total",
                "confidence",
            )
        ):
            candidates.append(dict(item))
    if not candidates:
        return {}

    def score(row: Mapping[str, Any]) -> tuple[int, int]:
        has_quant = 1 if _mapping(row.get("quant_factor_snapshot")) else 0
        has_suitability = 1 if _mapping(row.get("tactic_suitability")) else 0
        has_chart = 1 if row.get("scanner_chart_fit_score") not in (None, "") else 0
        # Prefer final/fallback candidates over top-pick snapshots when labels exist.
        final_hint = 1 if str(row.get("final_selected_symbol") or row.get("selected_symbol") or row.get("entry_final_symbol") or "") == target else 0
        return (has_quant + has_suitability + has_chart + final_hint, len(row))

    candidates.sort(key=score, reverse=True)
    return candidates[0]


def _scanner_chart_fit_from_row(row: Mapping[str, Any]) -> Dict[str, Any]:
    return _chart_fit_owner._scanner_chart_fit_from_row(row, facade=sys.modules[__name__])


def _tactic_value(value: Any) -> str:
    return _tactic_value_owner._tactic_value(value)


def _tactic_sources(
    *,
    entry_decision: Mapping[str, Any],
    factor_snapshot: Mapping[str, Any],
    selected_row: Mapping[str, Any],
    tactic_suitability: Mapping[str, Any],
    exit_decision: Mapping[str, Any],
) -> List[tuple[str, str]]:
    selected_factor = _mapping(selected_row.get("quant_factor_snapshot"))
    rows = (
        ("entry_quant_decision", entry_decision.get("tactic_id")),
        ("factor_snapshot", factor_snapshot.get("tactic_id")),
        ("selected_quant_factor_snapshot", selected_factor.get("tactic_id")),
        ("selected_candidate", selected_row.get("tactical_strategy")),
        ("tactic_suitability", tactic_suitability.get("tactic_id")),
        ("exit_quant_decision", exit_decision.get("tactic_id")),
    )
    return [(source, tactic_id) for source, value in rows if (tactic_id := _tactic_value(value))]


def _tactic_mismatches(sources: List[tuple[str, str]], tactic_id: str) -> List[Dict[str, str]]:
    return _mismatches_owner._tactic_mismatches(sources, tactic_id)


def _exit_tactic_drifts(sources: List[tuple[str, str]], tactic_id: str) -> List[Dict[str, str]]:
    return _exit_drifts_owner._exit_tactic_drifts(sources, tactic_id)


def quant_tactic_surface(report: Mapping[str, Any] | None) -> Dict[str, Any]:
    root = _mapping(report)
    monitor = _monitor(root)
    visibility = _entry_visibility(root)
    symbol = _symbol(root)
    selection = _mapping(root.get("why_this_symbol_was_chosen"))
    scanner_trace = _mapping(selection.get("scanner_selection_trace"))
    selected_row = _selected_candidate_row(root, symbol)
    entry_decision = _mapping(
        monitor.get("entry_quant_decision")
        or root.get("entry_quant_decision")
        or _first_nested_mapping(root, "entry_quant_decision")
    )
    exit_decision = _mapping(monitor.get("exit_quant_decision") or root.get("exit_quant_decision"))
    factor_snapshot = _mapping(
        monitor.get("quant_factor_snapshot")
        or root.get("quant_factor_snapshot")
        or selected_row.get("quant_factor_snapshot")
    )
    factors = _mapping(factor_snapshot.get("factors"))
    tactic_suitability = _mapping(
        selection.get("tactic_suitability")
        or scanner_trace.get("tactic_suitability")
        or selected_row.get("tactic_suitability")
        or entry_decision.get("tactic_suitability")
    )
    tactic_sources = _tactic_sources(
        entry_decision=entry_decision,
        factor_snapshot=factor_snapshot,
        selected_row=selected_row,
        tactic_suitability=tactic_suitability,
        exit_decision=exit_decision,
    )
    tactic_id_source, tactic_id = tactic_sources[0] if tactic_sources else ("", "")
    playbook = str(entry_decision.get("playbook") or exit_decision.get("playbook") or factor_snapshot.get("playbook") or _playbook(root)).strip()
    if not tactic_suitability and selected_row:
        tactic_suitability = score_candidate_tactic_suitability(selected_row, tactic_id=tactic_id, playbook=playbook)
    if not entry_decision:
        entry_info = _entry_info_from_visibility(visibility, monitor)
        if entry_info or selected_row or factor_snapshot:
            entry_decision = build_entry_quant_decision(
                entry_info,
                selected=selected_row,
                factor_snapshot=factor_snapshot,
                state=root,
                tactic_id=tactic_id,
                playbook=playbook,
            )
    scanner_chart_fit = _mapping(selection.get("scanner_chart_fit")) or _mapping(scanner_trace.get("scanner_chart_fit")) or _scanner_chart_fit_from_row(selected_row)
    if not any((entry_decision, exit_decision, factor_snapshot, tactic_suitability, tactic_id, scanner_chart_fit)):
        return {}
    return {
        "schema_version": "quant_tactic_report_surface.v1",
        "tactic_id": tactic_id,
        "tactic_id_source": tactic_id_source,
        "tactic_id_mismatches": _tactic_mismatches(tactic_sources, tactic_id),
        "exit_tactic_drifts": _exit_tactic_drifts(tactic_sources, tactic_id),
        "playbook": playbook,
        "entry_quant_decision": entry_decision,
        "exit_quant_decision": exit_decision,
        "factor_snapshot": factor_snapshot,
        "factors": factors,
        "tactic_suitability": tactic_suitability,
        "scanner_chart_fit": scanner_chart_fit,
    }


def render_quant_tactic_report_lines(report: Mapping[str, Any] | None, *, compact: bool = False) -> List[str]:
    surface = quant_tactic_surface(report)
    if not surface:
        return []
    entry = _mapping(surface.get("entry_quant_decision"))
    exit_decision = _mapping(surface.get("exit_quant_decision"))
    factors = _mapping(surface.get("factors"))
    suitability = _mapping(surface.get("tactic_suitability"))
    lines: List[str] = []
    tactic = surface.get("tactic_id") or "-"
    playbook = surface.get("playbook") or "-"
    if compact:
        lines.append(f"* 전술 진단: `{tactic}` / 플레이북 `{playbook}`")
    else:
        lines.append(f"- 전술 ID: `{tactic}`")
        lines.append(f"- 플레이북: `{playbook}`")
    if suitability:
        lines.append(
            f"- 스캐너 전술 적합도: {suitability.get('tier') or '-'} "
            f"({_fmt(suitability.get('score'))})"
        )
    if entry:
        lines.append(
            f"- 진입 quant 판단: {_decision_label(entry.get('decision'))} "
            f"/ blocker={_reason_text(entry.get('blockers'))} "
            f"/ warning={_reason_text(entry.get('warnings'))}"
        )
        cost = _mapping(entry.get("cost_edge"))
        if cost:
            lines.append(
                f"- 비용 엣지: {'통과' if cost.get('ok') else '미통과'} "
                f"/ edge={_pct(cost.get('cost_adjusted_edge_pct'))} "
                f"/ drag={_pct(cost.get('cost_drag_pct'))}"
            )
        if bool(entry.get("commander_override_required")):
            lines.append(f"- commander override 필요 항목: {_reason_text(entry.get('override_reason_required_for'))}")
    if exit_decision:
        lines.append(
            f"- 청산 quant 판단: {_decision_label(exit_decision.get('decision'))} "
            f"/ hard_exit={'예' if exit_decision.get('hard_exit') else '아니오'} "
            f"/ confirmation_pending={'예' if exit_decision.get('confirmation_pending') else '아니오'}"
        )
        if exit_decision.get("early_exit_flag") or exit_decision.get("actual_hold_sec") not in (None, ""):
            window = _mapping(exit_decision.get("expected_hold_window"))
            lines.append(
                f"- 보유시간 비교: 실제 {_fmt(exit_decision.get('actual_hold_sec'))}초 "
                f"/ 기대 최소 {_fmt(window.get('min_sec'))}초 "
                f"/ mismatch={'예' if exit_decision.get('hold_window_mismatch') else '아니오'}"
            )
        if exit_decision.get("blockers") or exit_decision.get("warnings"):
            lines.append(
                f"- 청산 진단 사유: blocker={_reason_text(exit_decision.get('blockers'))} "
                f"/ warning={_reason_text(exit_decision.get('warnings'))}"
            )
    if not compact and factors:
        factor_bits = []
        for key in ("vwap_distance_pct", "volume_ratio", "cost_floor_state", "confidence_score", "human_chart_entry_score"):
            if factors.get(key) not in (None, ""):
                factor_bits.append(f"{key}={_fmt(factors.get(key))}")
        if factor_bits:
            lines.append("- 핵심 factor snapshot: " + ", ".join(factor_bits[:6]))
    return lines
