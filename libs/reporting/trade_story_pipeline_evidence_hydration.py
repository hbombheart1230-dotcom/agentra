from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from libs.reporting.trade_report_common import clip_text as clip, safe_float, safe_int


def safe_read_json_file(path_value: Any) -> Dict[str, Any]:
    path_text = str(path_value or "").strip()
    if not path_text:
        return {}
    try:
        path = Path(path_text)
        if not path.exists() or not path.is_file():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def hydrate_canonical_agent_artifacts(
    bundle_out: Dict[str, Any],
    canonical_agent_artifacts: Dict[str, Any] | None,
    *,
    read_json_file=safe_read_json_file,
) -> Dict[str, Any]:
    hydrated = dict(canonical_agent_artifacts or {})
    artifacts = bundle_out.get("artifacts") if isinstance(bundle_out.get("artifacts"), dict) else {}
    for agent in ("commander", "strategist", "scanner", "monitor", "supervisor", "executor"):
        if isinstance(hydrated.get(agent), dict) and hydrated.get(agent):
            continue
        path_key = f"canonical_{agent}_json"
        payload = read_json_file(artifacts.get(path_key))
        if payload:
            hydrated[agent] = payload
            hydrated[path_key] = str(artifacts.get(path_key) or "")
    return hydrated


def resolve_selection_monitor_artifact(
    bundle_out: Dict[str, Any],
    canonical_agent_artifacts: Dict[str, Any] | None,
    *,
    read_json_file=safe_read_json_file,
) -> Dict[str, Any]:
    hydrated = dict(canonical_agent_artifacts or {})
    monitor_payload = (
        hydrated.get("monitor")
        if isinstance(hydrated.get("monitor"), dict)
        else bundle_out.get("monitor")
        if isinstance(bundle_out.get("monitor"), dict)
        else {}
    )
    scanner_path = str(
        hydrated.get("canonical_scanner_json")
        or ((bundle_out.get("artifacts") or {}).get("canonical_scanner_json"))
        or ""
    ).strip()
    if scanner_path:
        sibling_monitor = read_json_file(Path(scanner_path).with_name("monitor.json"))
        sibling_handoff = sibling_monitor.get("scanner_monitor_handoff") if isinstance(sibling_monitor.get("scanner_monitor_handoff"), dict) else {}
        sibling_cascade = sibling_handoff.get("entry_candidate_cascade") if isinstance(sibling_handoff.get("entry_candidate_cascade"), dict) else {}
        if (
            sibling_handoff.get("scanner_selected_symbol")
            or sibling_handoff.get("monitor_selected_symbol")
            or sibling_cascade.get("attempted")
            or sibling_cascade.get("fallback_used")
        ):
            return sibling_monitor

    handoff = monitor_payload.get("scanner_monitor_handoff") if isinstance(monitor_payload.get("scanner_monitor_handoff"), dict) else {}
    cascade = handoff.get("entry_candidate_cascade") if isinstance(handoff.get("entry_candidate_cascade"), dict) else {}
    if (
        handoff.get("scanner_selected_symbol")
        or handoff.get("monitor_selected_symbol")
        or cascade.get("attempted")
        or cascade.get("fallback_used")
    ):
        return dict(monitor_payload)

    return dict(monitor_payload)

# P1.5.2 R2-C: scanner/filter evidence enrichment owners.


def enrich_scanner_reason_from_evidence(
    scanner_reason_human: Dict[str, Any],
    scanner_evidence: Dict[str, Any],
    *,
    deps: Mapping[str, Any],
) -> Dict[str, Any]:
    _normalized_feature_coverage_from_scanner_evidence = deps["normalized_feature_coverage_from_scanner_evidence"]
    _scanner_candidate_row_from_evidence = deps["scanner_candidate_row_from_evidence"]
    _scanner_chart_fit_from_scanner_evidence = deps["scanner_chart_fit_from_scanner_evidence"]
    _scanner_macro_chart_fit_from_scanner_evidence = deps["scanner_macro_chart_fit_from_scanner_evidence"]
    _selection_basis_from_scores = deps["selection_basis_from_scores"]
    _top_numeric_drivers = deps["top_numeric_drivers"]
    out = dict(scanner_reason_human or {})
    evidence = scanner_evidence if isinstance(scanner_evidence, dict) else {}
    reason_rows = [dict(row) for row in list(evidence.get("candidate_selection_reasons") or []) if isinstance(row, dict)]
    payload = (
        reason_rows[0].get("payload")
        if reason_rows and isinstance(reason_rows[0].get("payload"), dict)
        else {}
    )
    if not isinstance(payload, dict):
        payload = {}

    why_selected = [str(x or "") for x in list(payload.get("why_selected") or []) if str(x or "").strip()][:4]
    selection_basis = clip(payload.get("final_decision_basis"), max_len=260)
    tie_break_rule = clip(payload.get("tie_break_rule"), max_len=180)
    runner_ups_lost: List[Dict[str, Any]] = []
    for row in list(payload.get("runner_ups_lost") or payload.get("runner_up_reasons") or []):
        if not isinstance(row, dict):
            continue
        symbol = clip(row.get("symbol"), max_len=24)
        why_lost = [
            clip(x, max_len=140)
            for x in list(row.get("why_lost") or row.get("lost_because") or [])
            if clip(x, max_len=140)
        ][:4]
        summary = clip(row.get("summary") or "; ".join(why_lost), max_len=240)
        if not symbol and not summary:
            continue
        runner_ups_lost.append(
            {
                "symbol": symbol,
                "why_lost": why_lost,
                "summary": summary,
            }
        )
        if len(runner_ups_lost) >= 3:
            break

    selected_symbol = str(out.get("selected_symbol") or "").strip()
    selected_evidence_row = _scanner_candidate_row_from_evidence(
        scanner_evidence,
        selected_symbol=selected_symbol,
    )
    selected_evidence_score_breakdown = (
        selected_evidence_row.get("score_breakdown")
        if isinstance(selected_evidence_row.get("score_breakdown"), dict)
        else {}
    )
    selected_evidence_sources = [
        str(x or "")
        for x in list(selected_evidence_row.get("sources") or [])
        if str(x or "").strip()
    ]
    selected_evidence_has_selection_metrics = bool(
        selected_evidence_score_breakdown
        or selected_evidence_sources
        or selected_evidence_row.get("score_total") not in (None, "")
        or selected_evidence_row.get("rank") not in (None, "")
    )
    selected_evidence_basis = _selection_basis_from_scores(
        selected_evidence_score_breakdown,
        selected_evidence_sources,
    )
    if selected_evidence_row and selected_evidence_has_selection_metrics:
        selected_score = selected_evidence_row.get("score_total")
        out["selected_candidate"] = dict(selected_evidence_row)
        out["selected_score"] = selected_score
        out["selected_rank"] = safe_int(selected_evidence_row.get("rank"), safe_int(out.get("selected_rank"), 0))
        out["selected_sources"] = selected_evidence_sources
        out["score_breakdown"] = dict(selected_evidence_score_breakdown)
        out["ranking_basis"] = list(selected_evidence_basis)
        out["selected_symbol_score_drivers"] = _top_numeric_drivers(selected_evidence_score_breakdown)
        out["selection_reason"] = (
            f"final selected symbol {selected_symbol} ranked #{safe_int(out.get('selected_rank'), 0) or '?'} "
            f"with score {safe_float(selected_score, 0.0):.3f}; led on {', '.join(selected_evidence_basis[:3])}"
        )
        out["summary"] = (
            f"Scanner selected {selected_symbol or '-'} as rank #{safe_int(out.get('selected_rank'), 0) or 1} "
            f"with score {safe_float(selected_score, 0.0):.3f} because it led on {', '.join(selected_evidence_basis[:3])}."
        )
        news_scanner_contribution = (
            out.get("news_scanner_contribution")
            if isinstance(out.get("news_scanner_contribution"), dict)
            else {}
        )
        if news_scanner_contribution:
            core_rows = news_scanner_contribution.get("core_score_contributions")
            if isinstance(core_rows, dict):
                positive_total = sum(
                    max(safe_float(value, 0.0), 0.0)
                    for value in dict(selected_evidence_score_breakdown or {}).values()
                )
                for key in ("trading_value", "momentum", "trend", "theme_boost", "sentiment"):
                    value = safe_float(selected_evidence_score_breakdown.get(key), 0.0)
                    core_rows[key] = {
                        "value": value,
                        "positive_share_pct": (100.0 * value / positive_total) if positive_total > 0 else 0.0,
                    }
            theme_trace = news_scanner_contribution.get("theme_alignment_trace")
            if isinstance(theme_trace, dict):
                theme_score = safe_float(selected_evidence_score_breakdown.get("theme_boost"), 0.0)
                theme_trace["theme_boost_score_contribution"] = theme_score
                theme_trace["theme_source_matched"] = "sector_theme" in selected_evidence_sources or theme_score > 0.0
            out["news_scanner_contribution"] = news_scanner_contribution
    coverage = _normalized_feature_coverage_from_scanner_evidence(scanner_evidence, selected_symbol=selected_symbol)
    if coverage:
        out["feature_coverage"] = dict(coverage)
        present = safe_int(coverage.get("present"), 0)
        total = safe_int(coverage.get("total"), 0)
        if present > 0 and total > 0:
            top_reasons = [str(x or "") for x in list(out.get("top_reasons") or []) if str(x or "").strip()]
            replaced_top_reason = False
            for idx, reason in enumerate(top_reasons):
                if reason.lower().startswith("chart feature coverage "):
                    top_reasons[idx] = f"chart feature coverage {present}/{total}"
                    replaced_top_reason = True
                    break
            if not replaced_top_reason:
                top_reasons.append(f"chart feature coverage {present}/{total}")
            out["top_reasons"] = top_reasons[:6]
            selection_reason = clip(out.get("selection_reason"), max_len=260)
            if selection_reason:
                if "chart feature coverage " in selection_reason.lower():
                    selection_reason = re.sub(
                        r"chart feature coverage\s+\d+/\d+",
                        f"chart feature coverage {present}/{total}",
                        selection_reason,
                        flags=re.IGNORECASE,
                    )
                else:
                    selection_reason = clip(f"{selection_reason}; chart feature coverage {present}/{total}", max_len=260)
            else:
                selection_reason = f"chart feature coverage {present}/{total}"
            out["selection_reason"] = selection_reason

    chart_fit = (
        out.get("scanner_chart_fit")
        if isinstance(out.get("scanner_chart_fit"), dict)
        else {}
    )
    if not chart_fit:
        chart_fit = _scanner_chart_fit_from_scanner_evidence(scanner_evidence, selected_symbol=selected_symbol)
        if chart_fit:
            out["scanner_chart_fit"] = dict(chart_fit)
    macro_chart_fit = (
        out.get("scanner_macro_chart_fit")
        if isinstance(out.get("scanner_macro_chart_fit"), dict)
        else {}
    )
    if not macro_chart_fit:
        macro_chart_fit = _scanner_macro_chart_fit_from_scanner_evidence(
            scanner_evidence,
            selected_symbol=selected_symbol,
        )
        if macro_chart_fit:
            out["scanner_macro_chart_fit"] = dict(macro_chart_fit)

    if why_selected:
        out["why_selected"] = why_selected
    if selection_basis:
        out["selection_basis"] = selection_basis
    if tie_break_rule:
        out["tie_break_rule"] = tie_break_rule
    if runner_ups_lost:
        out["runner_ups_lost"] = runner_ups_lost

    bullets = [str(x or "") for x in list(out.get("bullets") or []) if str(x or "").strip()]
    if selected_evidence_row and selected_evidence_has_selection_metrics:
        stale_prefixes = (
            "Selected because:",
            "Selection sources:",
            "Core score contributions:",
            "Theme linkage:",
        )
        bullets = [
            bullet
            for bullet in bullets
            if not any(bullet.startswith(prefix) for prefix in stale_prefixes)
        ]
        bullets.insert(
            0,
            (
                "Selected because: "
                f"{selected_symbol} rank #{safe_int(out.get('selected_rank'), 0) or '?'} "
                f"score {safe_float(out.get('selected_score'), 0.0):.3f}"
            ),
        )
        bullets.insert(
            1,
            "Selection sources: " + (", ".join(selected_evidence_sources) if selected_evidence_sources else "score_breakdown_only"),
        )
        bullets.insert(
            2,
            "Core score contributions: "
            f"trading_value {safe_float(selected_evidence_score_breakdown.get('trading_value'), 0.0):+.3f}, "
            f"momentum {safe_float(selected_evidence_score_breakdown.get('momentum'), 0.0):+.3f}, "
            f"trend {safe_float(selected_evidence_score_breakdown.get('trend'), 0.0):+.3f}, "
            f"theme_boost {safe_float(selected_evidence_score_breakdown.get('theme_boost'), 0.0):+.3f}, "
            f"sentiment {safe_float(selected_evidence_score_breakdown.get('sentiment'), 0.0):+.3f}",
        )
        theme_score = safe_float(selected_evidence_score_breakdown.get("theme_boost"), 0.0)
        bullets.insert(
            3,
            "Theme linkage: "
            f"matched={bool('sector_theme' in selected_evidence_sources or theme_score > 0.0)}, "
            f"theme_boost={theme_score:+.3f}",
        )
    if coverage:
        present = safe_int(coverage.get("present"), 0)
        total = safe_int(coverage.get("total"), 0)
        updated_bullets: List[str] = []
        replaced_chart_bullet = False
        coverage_detail_inserted = False
        present_keys = [str(x or "") for x in list(coverage.get("present_keys") or []) if str(x or "").strip()]
        missing_keys = [str(x or "") for x in list(coverage.get("missing_keys") or []) if str(x or "").strip()]
        coverage_source = clip(coverage.get("source"), max_len=80)

        def _append_coverage_details(target: List[str]) -> None:
            nonlocal coverage_detail_inserted
            if coverage_detail_inserted:
                return
            if present_keys:
                target.append(
                    "Chart features present: " + ", ".join(present_keys[:8]) + (", ..." if len(present_keys) > 8 else "")
                )
            if missing_keys:
                target.append(
                    "Chart features missing: " + ", ".join(missing_keys[:8]) + (", ..." if len(missing_keys) > 8 else "")
                )
            if coverage_source:
                target.append(f"Chart feature coverage source: {coverage_source}")
            coverage_detail_inserted = True

        for bullet in bullets:
            if bullet.lower().startswith("chart / feature coverage:"):
                updated_bullets.append(f"Chart / feature coverage: {present}/{total}")
                replaced_chart_bullet = True
                _append_coverage_details(updated_bullets)
            else:
                updated_bullets.append(bullet)
        if not replaced_chart_bullet and present > 0 and total > 0:
            updated_bullets.append(f"Chart / feature coverage: {present}/{total}")
            _append_coverage_details(updated_bullets)
        bullets = updated_bullets
    if chart_fit:
        fit_line = (
            "Scanner chart-fit: "
            f"{safe_float(chart_fit.get('score'), 0.0):.3f} "
            f"({chart_fit.get('authority') or 'not_captured'})"
        )
        if fit_line not in bullets:
            bullets.append(fit_line)
    if macro_chart_fit:
        macro_fit_line = (
            "Scanner macro chart-fit: "
            f"{safe_float(macro_chart_fit.get('score'), 0.0):.3f} "
            f"(bias {safe_float(macro_chart_fit.get('bias'), 0.0):+.3f})"
        )
        if macro_fit_line not in bullets:
            bullets.append(macro_fit_line)
    if why_selected:
        bullets.append("Selection decision: " + "; ".join(why_selected))
    if selection_basis:
        bullets.append(f"Final decision basis: {selection_basis}")
    if tie_break_rule:
        bullets.append(f"Tie-break rule: {tie_break_rule}")
    if runner_ups_lost:
        bullets.append(
            "Runner-ups lost because: "
            + "; ".join(
                f"{row.get('symbol')}: {row.get('summary')}" for row in runner_ups_lost if row.get("symbol")
            )
        )
    if bullets:
        deduped: List[str] = []
        seen: set[str] = set()
        for bullet in bullets:
            if bullet not in seen:
                deduped.append(bullet)
                seen.add(bullet)
        out["bullets"] = deduped[:12]
    trace = out.get("scanner_selection_trace") if isinstance(out.get("scanner_selection_trace"), dict) else {}
    if trace and coverage:
        trace["chart_feature_coverage"] = dict(coverage)
        out["scanner_selection_trace"] = trace
    if trace and chart_fit:
        trace["scanner_chart_fit"] = dict(chart_fit)
        out["scanner_selection_trace"] = trace
    if trace and macro_chart_fit:
        trace["scanner_macro_chart_fit"] = dict(macro_chart_fit)
        out["scanner_selection_trace"] = trace
    if selected_evidence_row and selected_evidence_has_selection_metrics:
        trace = dict(out.get("scanner_selection_trace") or {})
        trace["selected_symbol"] = selected_symbol
        trace["selected_rank"] = safe_int(out.get("selected_rank"), 0)
        trace["selected_symbol_score_drivers"] = dict(out.get("selected_symbol_score_drivers") or {})
        trace["selection_reason"] = str(out.get("selection_reason") or "")
        out["scanner_selection_trace"] = trace
    return out



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


