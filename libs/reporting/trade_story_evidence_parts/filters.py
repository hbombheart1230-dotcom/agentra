from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from libs.reporting.trade_report_common import clip_text as clip, safe_float, safe_int


def enrich_filters_from_evidence(
    filters_human: Dict[str, Any],
    scanner_evidence: Dict[str, Any],
    *,
    selected_symbol: str,
    monitor_evidence: Optional[Dict[str, Any]] = None,
    entry_execution_details: Optional[Dict[str, Any]] = None,
    exit_execution_details: Optional[Dict[str, Any]] = None,
    deps: Mapping[str, Any],
) -> Dict[str, Any]:
    _normalized_feature_coverage_from_scanner_evidence = deps["normalized_feature_coverage_from_scanner_evidence"]
    _scanner_candidate_row_from_evidence = deps["scanner_candidate_row_from_evidence"]
    out = dict(filters_human or {})
    coverage = _normalized_feature_coverage_from_scanner_evidence(scanner_evidence, selected_symbol=selected_symbol)
    selected_evidence_row = _scanner_candidate_row_from_evidence(
        scanner_evidence,
        selected_symbol=selected_symbol,
    )
    theme_check_override: Optional[Dict[str, str]] = None
    if selected_evidence_row:
        score_breakdown = (
            selected_evidence_row.get("score_breakdown")
            if isinstance(selected_evidence_row.get("score_breakdown"), dict)
            else {}
        )
        sources = [
            str(x or "")
            for x in list(selected_evidence_row.get("sources") or [])
            if str(x or "").strip()
        ]
        if score_breakdown or sources:
            theme_score = safe_float(score_breakdown.get("theme_boost"), 0.0)
            theme_pass = "sector_theme" in sources or theme_score > 0.0
            theme_check_override = {
                "name": "sector/theme alignment",
                "status": "PASS" if theme_pass else "FAIL",
                "detail": (
                    f"final selected candidate theme boost was {theme_score:+.3f} or sector_theme source matched"
                    if theme_pass
                    else f"final selected candidate had no sector_theme source and theme boost was {theme_score:+.3f}"
                ),
            }
    price_anomaly_check: Optional[Dict[str, str]] = None
    execution_spread_check: Optional[Dict[str, str]] = None

    def _existing_chart_feature_total() -> int:
        texts: List[str] = [str(out.get("summary") or "")]
        texts.extend([str(x or "") for x in list(out.get("bullets") or []) if str(x or "").strip()])
        for check in list(out.get("checks") or []):
            if isinstance(check, dict):
                texts.append(str(check.get("detail") or ""))
        for text in texts:
            match = re.search(r"\b\d+\s*/\s*(\d+)\s+captured(?:\s+chart)?\s+features\b", text, flags=re.IGNORECASE)
            if match:
                total_value = safe_int(match.group(1), 0)
                if total_value > 0:
                    return int(total_value)
        return 0

    if coverage and str(coverage.get("source") or "") == "snapshot_derived":
        existing_total = _existing_chart_feature_total()
        if existing_total > 0 and existing_total != safe_int(coverage.get("total"), 0):
            coverage = dict(coverage)
            present_count = safe_int(coverage.get("present"), 0)
            coverage["total"] = int(existing_total)
            coverage["coverage_ratio"] = float(present_count) / float(existing_total) if existing_total else 0.0
            if coverage["coverage_ratio"] >= 0.75:
                coverage["quality"] = "strong"
            elif coverage["coverage_ratio"] >= 0.5:
                coverage["quality"] = "partial"
            else:
                coverage["quality"] = "weak"
            coverage["source"] = "snapshot_derived_existing_filter_total"

    def _visit_monitor_payload(node: Any) -> None:
        nonlocal price_anomaly_check
        if price_anomaly_check is not None:
            return
        if isinstance(node, dict):
            if "price_anomaly_flag" in node:
                flagged = bool(node.get("price_anomaly_flag"))
                reason = str(node.get("price_anomaly_reason") or "").strip()
                price_anomaly_check = {
                    "name": "price anomaly filter",
                    "status": "FAIL" if flagged else "PASS",
                    "detail": reason if flagged and reason else ("monitor price cross-check flagged an anomaly" if flagged else "monitor price cross-check found no anomaly"),
                }
                return
            for value in node.values():
                _visit_monitor_payload(value)
                if price_anomaly_check is not None:
                    return
        elif isinstance(node, list):
            for value in node:
                _visit_monitor_payload(value)
                if price_anomaly_check is not None:
                    return

    _visit_monitor_payload(monitor_evidence)

    def _resolve_execution_spread_check() -> Optional[Dict[str, str]]:
        spread_threshold_bps = 50.0
        for details in (entry_execution_details, exit_execution_details):
            if not isinstance(details, dict):
                continue
            quote_snapshot = details.get("quote_snapshot") if isinstance(details.get("quote_snapshot"), dict) else {}
            spread_bps = details.get("spread_bps")
            if spread_bps in (None, ""):
                spread_bps = quote_snapshot.get("spread_bps")
            if spread_bps in (None, ""):
                continue
            spread_value = safe_float(spread_bps, None)
            if spread_value is None:
                continue
            return {
                "name": "spread/slippage filter",
                "status": "PASS" if spread_value <= spread_threshold_bps else "FAIL",
                "detail": f"execution quote snapshot spread was {spread_value:.1f} bps",
            }
        return None

    execution_spread_check = _resolve_execution_spread_check()
    coverage_quality = "missing"
    present = 0
    total = 0
    chart_status = "NOT_AVAILABLE"
    chart_note = "feature snapshot not available"
    chart_available = bool(coverage)
    if coverage:
        present = safe_int(coverage.get("present"), 0)
        total = safe_int(coverage.get("total"), 0)
        coverage_quality = str(coverage.get("quality") or "").strip().lower() or "missing"
        if total <= 0:
            chart_status = "NOT_AVAILABLE"
            chart_note = "feature snapshot not available"
        elif present >= 8:
            chart_status = "PASS"
            chart_note = f"{present}/{total} captured chart features"
        elif present >= 4:
            chart_status = "PARTIAL"
            chart_note = f"{present}/{total} captured chart features"
        else:
            chart_status = "FAIL"
            chart_note = f"{present}/{total} captured chart features"

    summary = str(out.get("summary") or "").strip()
    if chart_available:
        if summary:
            summary = re.sub(
                r"Chart completeness was [^.]*(?:\.)?",
                f"Chart completeness was {coverage_quality} with {present}/{total} captured features.",
                summary,
                flags=re.IGNORECASE,
            )
        else:
            summary = (
                "Scanner and guard checks were captured. "
                f"Chart completeness was {coverage_quality} with {present}/{total} captured features."
            )
        out["summary"] = summary

    checks = [dict(x) for x in list(out.get("checks") or []) if isinstance(x, dict)]
    updated_checks: List[Dict[str, Any]] = []
    replaced_check = False
    replaced_theme_check = False
    replaced_price_anomaly = False
    replaced_spread_check = False
    for check in checks:
        name = str(check.get("name") or "").strip().lower()
        if name == "chart completeness filter" and chart_available:
            check["status"] = chart_status
            check["detail"] = chart_note
            replaced_check = True
        elif name == "sector/theme alignment" and theme_check_override is not None:
            check["status"] = str(theme_check_override.get("status") or "")
            check["detail"] = str(theme_check_override.get("detail") or "")
            replaced_theme_check = True
        elif name == "price anomaly filter" and price_anomaly_check is not None:
            check["status"] = str(price_anomaly_check.get("status") or check.get("status") or "")
            check["detail"] = str(price_anomaly_check.get("detail") or check.get("detail") or "")
            replaced_price_anomaly = True
        elif name == "spread/slippage filter" and execution_spread_check is not None:
            current_status = str(check.get("status") or "").strip().upper()
            if current_status in {"", "NOT_AVAILABLE", "UNKNOWN"}:
                check["status"] = str(execution_spread_check.get("status") or check.get("status") or "")
                check["detail"] = str(execution_spread_check.get("detail") or check.get("detail") or "")
                replaced_spread_check = True
        updated_checks.append(check)
    if chart_available and not replaced_check:
        updated_checks.append(
            {
                "name": "chart completeness filter",
                "status": chart_status,
                "detail": chart_note,
            }
        )
    if theme_check_override is not None and not replaced_theme_check:
        updated_checks.append(dict(theme_check_override))
    if price_anomaly_check is not None and not replaced_price_anomaly:
        updated_checks.append(dict(price_anomaly_check))
    if execution_spread_check is not None and not replaced_spread_check:
        updated_checks.append(dict(execution_spread_check))
    if updated_checks:
        out["checks"] = updated_checks

    bullets = [str(x or "") for x in list(out.get("bullets") or []) if str(x or "").strip()]
    updated_bullets: List[str] = []
    replaced = False
    replaced_theme_bullet = False
    replaced_price_bullet = False
    replaced_spread_bullet = False
    for bullet in bullets:
        if bullet.lower().startswith("chart completeness filter:") and chart_available:
            updated_bullets.append(f"chart completeness filter: {chart_status} - {chart_note}")
            replaced = True
        elif bullet.lower().startswith("sector/theme alignment:") and theme_check_override is not None:
            updated_bullets.append(
                f"sector/theme alignment: {theme_check_override['status']} - {theme_check_override['detail']}"
            )
            replaced_theme_bullet = True
        elif bullet.lower().startswith("price anomaly filter:") and price_anomaly_check is not None:
            updated_bullets.append(
                f"price anomaly filter: {price_anomaly_check['status']} - {price_anomaly_check['detail']}"
            )
            replaced_price_bullet = True
        elif bullet.lower().startswith("spread/slippage filter:") and execution_spread_check is not None:
            current_status = ""
            match = re.match(r"spread/slippage filter:\s*([A-Z_]+)\s*-", bullet, flags=re.IGNORECASE)
            if match:
                current_status = str(match.group(1) or "").strip().upper()
            if current_status in {"", "NOT_AVAILABLE", "UNKNOWN"}:
                updated_bullets.append(
                    f"spread/slippage filter: {execution_spread_check['status']} - {execution_spread_check['detail']}"
                )
                replaced_spread_bullet = True
            else:
                updated_bullets.append(bullet)
        else:
            updated_bullets.append(bullet)
    if chart_available and not replaced:
        updated_bullets.append(f"chart completeness filter: {chart_status} - {chart_note}")
    if theme_check_override is not None and not replaced_theme_bullet:
        updated_bullets.append(
            f"sector/theme alignment: {theme_check_override['status']} - {theme_check_override['detail']}"
        )
    if price_anomaly_check is not None and not replaced_price_bullet:
        updated_bullets.append(
            f"price anomaly filter: {price_anomaly_check['status']} - {price_anomaly_check['detail']}"
        )
    if execution_spread_check is not None and not replaced_spread_bullet:
        updated_bullets.append(
            f"spread/slippage filter: {execution_spread_check['status']} - {execution_spread_check['detail']}"
        )
    out["bullets"] = updated_bullets[:8]
    if coverage:
        out["feature_coverage"] = dict(coverage)
    return out


