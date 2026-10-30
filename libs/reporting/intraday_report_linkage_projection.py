"""intraday_trade_reports projections (moved verbatim from intraday_trade_reports).

Module globals and helpers are resolved on ``facade`` (the intraday_trade_reports module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def build_same_day_reporter_linkage(
    *,
    reporter_obj: Dict[str, Any],
    reporter_js: Path,
    reporter_md: Path,
    entry_run_id: str,
    exit_run_id: str,
    entry_bundle: Dict[str, Any],
    exit_bundle: Dict[str, Any],
    facade: Any,
) -> Dict[str, Any]:
    reporter_obj = reporter_obj if isinstance(reporter_obj, dict) else {}
    entry_reporter = entry_bundle.get("reporter") if isinstance(entry_bundle.get("reporter"), dict) else {}
    exit_reporter = exit_bundle.get("reporter") if isinstance(exit_bundle.get("reporter"), dict) else {}
    reporter_day_file_found = bool(
        reporter_js.exists()
        or reporter_md.exists()
        or entry_reporter.get("reporter_analysis_day_file_found")
        or exit_reporter.get("reporter_analysis_day_file_found")
    )
    linked_run_ids: List[str] = []
    if bool(entry_reporter.get("reporter_analysis_found")) and entry_run_id:
        linked_run_ids.append(str(entry_run_id))
    if bool(exit_reporter.get("reporter_analysis_found")) and exit_run_id and exit_run_id not in linked_run_ids:
        linked_run_ids.append(str(exit_run_id))
    run_link_found = bool(linked_run_ids)
    if run_link_found:
        status = "linked_run"
        linkage_source = "run_specific"
        linkage_reason = "A same-day reporter analysis linked directly to this lifecycle run."
    elif reporter_day_file_found:
        status = "linked_day_fallback"
        linkage_source = "day_fallback"
        linkage_reason = "A same-day reporter analysis file was attached as fallback context for this lifecycle."
    else:
        status = "missing"
        linkage_source = "missing"
        linkage_reason = "Same-day reporter analysis is not available for this lifecycle yet."
    return {
        "schema_version": "same_day_reporter_linkage.v1",
        "status": status,
        "linkage_source": linkage_source,
        "linkage_reason": linkage_reason,
        "reporter_analysis_day_file_found": reporter_day_file_found,
        "run_link_found": run_link_found,
        "linked_run_ids": linked_run_ids,
        "reporter_analysis_json_path": str(reporter_js) if reporter_js.exists() else "",
        "reporter_analysis_md_path": str(reporter_md) if reporter_md.exists() else "",
        "reporter_analysis_expected_json_path": str(reporter_js),
        "reporter_analysis_expected_md_path": str(reporter_md),
        "reporter_analysis_json_found": bool(reporter_js.exists()),
        "reporter_analysis_md_found": bool(reporter_md.exists()),
        "reporter_analysis_summary": str(reporter_obj.get("ai_summary") or ""),
        "reporter_analysis_grade": str(reporter_obj.get("ai_run_grade") or "N/A"),
    }
