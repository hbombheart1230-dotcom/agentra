"""Markdown-clean canonical entry-monitor artifact resolution from report/provenance paths (read-only).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _safe_read_json_object_r3_impl(path_value, *, facade):
    text = str(path_value or "").strip()
    if not text:
        return {}
    try:
        path = facade.Path(text)
        if not path.exists() or not path.is_file():
            return {}
        payload = facade.json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _is_entry_monitor_artifact_r3_impl(payload, *, facade):
    if not payload:
        return False
    focus = facade._as_dict(payload.get("monitor_focus_context"))
    if bool(payload.get("entry_triggered")) or str(payload.get("entry_decision") or "").upper() == "BUY":
        return True
    if bool(focus.get("entry_triggered")) or str(focus.get("entry_decision") or "").upper() == "BUY":
        return True
    return False


def _canonical_monitor_from_trade_report_path_r3_impl(report, run_id, *, facade):
    paths = facade._as_dict(report.get("paths"))
    report_path_text = str(paths.get("ai_trade_report_json") or "").strip()
    if not report_path_text or not run_id:
        return {}
    try:
        report_path = facade.Path(report_path_text)
        parts = list(report_path.parts)
        idx = parts.index("trades")
        reports_root = facade.Path(*parts[:idx])
        day = parts[idx + 1]
    except Exception:
        return {}
    return facade._safe_read_json_object(reports_root / "canonical" / day / run_id / "monitor.json")


def _canonical_monitor_from_section_provenance_r3_impl(report, *, facade):
    provenance = facade._as_dict(report.get("section_provenance"))
    for key in ("entry_decision", "why_this_symbol_was_chosen", "market_context_at_entry"):
        row = facade._as_dict(provenance.get(key))
        artifact_path = str(row.get("artifact_path") or "").strip()
        if not artifact_path:
            continue
        monitor = facade._safe_read_json_object(facade.Path(artifact_path).with_name("monitor.json"))
        if facade._is_entry_monitor_artifact(monitor):
            return monitor
    return {}


def _resolve_entry_monitor_artifact_r3_impl(report, *, facade):
    fact_payload = facade._as_dict(report.get("fact_payload"))
    trade_payload = facade._as_dict(fact_payload.get("trade"))
    entry_summary = facade._as_dict(trade_payload.get("entry_summary"))
    entry_monitor = facade._as_dict(entry_summary.get("monitor_context"))
    if facade._is_entry_monitor_artifact(entry_monitor):
        return entry_monitor

    entry_run_id = str(entry_summary.get("run_id") or report.get("run_id") or "").strip()
    monitor = facade._canonical_monitor_from_trade_report_path(report, entry_run_id)
    if facade._is_entry_monitor_artifact(monitor):
        return monitor

    return facade._canonical_monitor_from_section_provenance(report)


def _candidate_cascade_matches_trade_r3_impl(cascade, traded_symbol, *, facade):
    symbol = facade._display_candidate_symbol(traded_symbol)
    if not symbol or not cascade:
        return True
    cascade_symbols = facade._candidate_cascade_symbols(cascade)
    if not cascade_symbols:
        return True
    return symbol in cascade_symbols
