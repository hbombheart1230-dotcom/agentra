"""LLM artifacts trade artifact path projection (moved verbatim from llm_artifacts).

Helpers are resolved on ``facade`` (the llm_artifacts module) at call time; this module never imports it.
Pure path construction except trade lookup, which only reads the filesystem through the facade.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def trade_artifact_paths(
    reports_root: Path,
    day: str,
    trade_id: str,
    *,
    prefer_existing_day_root: bool = False,
    time_bucket: str | None = None,
    facade: Any,
) -> Dict[str, Path]:
    normalized_day = str(day or "").strip()
    normalized_trade_id = str(trade_id or "").strip()
    trade_day_root = (
        facade.resolve_trade_day_root(reports_root, normalized_day)
        if prefer_existing_day_root
        else facade.canonical_trade_day_root(reports_root, normalized_day)
    )
    existing_trade_root = facade.find_trade_dir(trade_day_root, normalized_trade_id)
    if existing_trade_root is not None:
        trade_root = existing_trade_root
    else:
        bucket = str(time_bucket or "").strip()
        if bucket:
            trade_root = trade_day_root / bucket / normalized_trade_id
        else:
            trade_root = trade_day_root / normalized_trade_id
    legacy_root = reports_root / "trades" / normalized_day[:4] / normalized_day[5:7] / normalized_trade_id
    # Phase 3 primary structure (operator-facing):
    # reports/trades/<day>/<trade_id>/
    #   lifecycle_bundle.json, entry.json, hold.json, exit.json
    #   evidence/*.json
    #   reports/*.json|md
    reports_dir = trade_root / "reports"
    evidence_dir = trade_root / "evidence"
    lifecycle_bundle_json = trade_root / "lifecycle_bundle.json"
    entry_json = trade_root / "entry.json"
    hold_json = trade_root / "hold.json"
    exit_json = trade_root / "exit.json"
    commander_evidence_json = evidence_dir / "commander_evidence.json"
    monitor_evidence_json = evidence_dir / "monitor_evidence.json"

    # Legacy normalized layout (read fallback only).
    legacy_normalized_strategist_dir = trade_root / "strategist"
    legacy_normalized_ai_report_dir = trade_root / "ai_trade_report"
    legacy_normalized_lifecycle_dir = trade_root / "lifecycle"
    return {
        "trade_root": trade_root,
        "legacy_trade_root": legacy_root,
        "reports_dir": reports_dir,
        "evidence_dir": evidence_dir,
        "strategist_dir": reports_dir,
        "ai_trade_report_dir": reports_dir,
        "brief_dir": reports_dir,
        "lifecycle_dir": trade_root,
        "lifecycle_bundle_json": lifecycle_bundle_json,
        "entry_json": entry_json,
        "hold_json": hold_json,
        "exit_json": exit_json,
        # Compact trade-scoped LLM status artifacts (no raw body content).
        "strategist_llm_response_json": reports_dir / "strategist_llm_response.json",
        "strategist_summary_md": reports_dir / "strategist_summary.md",
        "strategist_summary_json": reports_dir / "strategist_summary.json",
        "ai_trade_report_llm_response_json": reports_dir / "ai_trade_report_llm_response.json",
        "brief_llm_response_json": reports_dir / "brief_llm_response.json",
        # Deprecated intermediate artifacts (no forward writes in Phase 3).
        "strategist_input_json": trade_root / "strategist_input.json",
        "strategist_compact_input_json": trade_root / "strategist_compact_input.json",
        "ai_trade_report_input_json": trade_root / "ai_trade_report_input.json",
        "ai_trade_report_compact_input_json": trade_root / "ai_trade_report_compact_input.json",
        "brief_input_json": trade_root / "brief_input.json",
        "brief_compact_input_json": trade_root / "brief_compact_input.json",
        # Operator-facing summary reports.
        "ai_trade_report_json": reports_dir / "ai_trade_report.json",
        "ai_trade_report_md": reports_dir / "ai_trade_report.md",
        "ai_trade_summary_input_json": reports_dir / "ai_trade_summary_input.json",
        "ai_trade_summary_json": reports_dir / "ai_trade_summary.json",
        "ai_trade_summary_md": reports_dir / "ai_trade_summary.md",
        "ai_trade_summary_llm_response_json": reports_dir / "ai_trade_summary_llm_response.json",
        "brief_json": reports_dir / "operator_brief.json",
        "brief_md": reports_dir / "operator_brief.md",
        # Deprecated compatibility files (read fallback only).
        "trade_lifecycle_json": trade_root / "trade_lifecycle.json",
        "aggregated_execution_bundle_json": trade_root / "aggregated_execution_bundle.json",
        # Evidence set.
        "strategist_evidence_json": evidence_dir / "strategist_evidence.json",
        "scanner_evidence_json": evidence_dir / "scanner_evidence.json",
        "monitor_evidence_json": monitor_evidence_json,
        "monitor_timeline_json": monitor_evidence_json,
        "commander_evidence_json": commander_evidence_json,
        "trade_provenance_json": trade_root / "_provenance.json",
        "trade_health_json": trade_root / "_health.json",
        "trade_artifact_links_json": trade_root / "_artifact_links.json",
        # Legacy normalized read fallbacks.
        "legacy_normalized_strategist_llm_response_json": legacy_normalized_strategist_dir / "strategist_llm_response.json",
        "legacy_normalized_ai_trade_report_input_json": legacy_normalized_ai_report_dir / "ai_trade_report_input.json",
        "legacy_normalized_ai_trade_report_compact_input_json": legacy_normalized_ai_report_dir / "ai_trade_report_compact_input.json",
        "legacy_normalized_ai_trade_report_json": legacy_normalized_ai_report_dir / "ai_trade_report.json",
        "legacy_normalized_ai_trade_report_md": legacy_normalized_ai_report_dir / "ai_trade_report.md",
        "legacy_normalized_ai_trade_report_llm_response_json": legacy_normalized_ai_report_dir / "ai_trade_report_llm_response.json",
        "legacy_normalized_trade_lifecycle_json": legacy_normalized_lifecycle_dir / "trade_lifecycle.json",
        "legacy_normalized_aggregated_execution_bundle_json": legacy_normalized_lifecycle_dir / "aggregated_execution_bundle.json",
        "legacy_normalized_strategist_evidence_json": evidence_dir / "strategist_evidence.json",
        "legacy_normalized_scanner_evidence_json": evidence_dir / "scanner_evidence.json",
        "legacy_normalized_monitor_timeline_json": evidence_dir / "monitor_timeline.json",
        "legacy_trade_story_input_json": legacy_root / "trade_story_input.json",
        "legacy_trade_report_json": legacy_root / "trade_report.json",
        "legacy_trade_report_md": legacy_root / "trade_report.md",
        "legacy_trade_lifecycle_json": legacy_root / "trade_lifecycle.json",
        "legacy_aggregated_execution_bundle_json": legacy_root / "aggregated_execution_bundle.json",
    }
