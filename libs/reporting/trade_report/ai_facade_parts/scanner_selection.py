"""AI report scanner-selection text and filter-bullet composition (deterministic, read-only).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _scanner_basis_text_r3_impl(scanner_reason, *, facade):
    def _basis_label(value: Any) -> str:
        raw = facade._clip(value, max_len=120).strip()
        mapping = {
            "trading value": "거래대금",
            "theme and sector alignment": "섹터·테마 정렬",
            "sentiment support": "감성 지원",
            "top value": "거래대금 상위",
            "top volume": "거래량 상위",
            "momentum": "모멘텀",
            "trend": "추세",
            "confidence": "신뢰도",
        }
        return mapping.get(raw.lower(), raw)

    basis = scanner_reason.get("ranking_basis")
    if isinstance(basis, list):
        return ", ".join(_basis_label(item) for item in facade._listify(basis, max_items=4, max_len=80) if _basis_label(item))
    return _basis_label(facade._clip(basis, max_len=220))


def _scanner_ranked_candidates_r3_impl(scanner_reason, *, facade):
    for key in ("top_candidates", "ranked_candidates"):
        rows = [row for row in list(scanner_reason.get(key) or []) if isinstance(row, dict)]
        if rows:
            return rows[:5]
    trace = scanner_reason.get("scanner_selection_trace") if isinstance(scanner_reason.get("scanner_selection_trace"), dict) else {}
    return [row for row in list(trace.get("ranked_candidates") or []) if isinstance(row, dict)][:5]


def _scanner_monitor_fallback_context_r3_impl(scanner_reason, *, facade):
    trace = scanner_reason.get("scanner_selection_trace") if isinstance(scanner_reason.get("scanner_selection_trace"), dict) else {}
    return {
        "used": bool(scanner_reason.get("monitor_fallback_used") or trace.get("monitor_fallback_used")),
        "scanner_top_pick_symbol": facade._clip(
            scanner_reason.get("scanner_top_pick_symbol") or trace.get("scanner_top_pick_symbol"),
            max_len=24,
        ),
        "reason": facade._operatorize_report_text(
            scanner_reason.get("monitor_fallback_reason") or trace.get("monitor_fallback_reason")
        ),
        "trigger_reason": facade._operatorize_report_text(
            scanner_reason.get("monitor_trigger_reason") or trace.get("monitor_trigger_reason")
        ),
    }


def _scanner_chart_feature_coverage_r3_impl(scanner_reason, *, facade):
    trace = scanner_reason.get("scanner_selection_trace") if isinstance(scanner_reason.get("scanner_selection_trace"), dict) else {}
    row = trace.get("chart_feature_coverage") if isinstance(trace.get("chart_feature_coverage"), dict) else {}
    out = dict(row)
    present = int(float(out.get("present") or 0)) if facade._num_opt(out.get("present")) is not None else 0
    total = int(float(out.get("total") or 0)) if facade._num_opt(out.get("total")) is not None else 0
    present_keys = [str(x or "") for x in list(out.get("present_keys") or []) if str(x or "").strip()]
    missing_keys = [str(x or "") for x in list(out.get("missing_keys") or []) if str(x or "").strip()]
    if (present_keys or missing_keys) and not (
        present_keys
        and len(present_keys) == present
        and len(present_keys) + len(missing_keys) == total
    ):
        out["present_keys"] = []
        out["missing_keys"] = []
    return out


def _build_scanner_filters_bullets_r3_impl(filters_human, *, facade):
    checks = [row for row in list(filters_human.get("checks") or []) if isinstance(row, dict)]
    if not checks:
        return facade._listify(filters_human.get("bullets"), max_items=10, max_len=260)
    bullets: List[str] = []
    for row in checks[:8]:
        label = facade._scanner_check_name_label(row.get("name"))
        status = facade._scanner_check_status_label(row.get("status"))
        detail = facade._operatorize_report_text(row.get("detail"))
        if detail:
            bullets.append(f"{label}은 {status}였습니다. 근거: {detail}")
        else:
            bullets.append(f"{label}은 {status}였습니다.")
    return facade._dedupe_list(bullets, max_items=10, max_len=260)
