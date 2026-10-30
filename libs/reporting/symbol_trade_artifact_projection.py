"""symbol_trade_report _extract_trade_artifact_snapshot (moved verbatim from symbol_trade_report).

Module globals and helpers are resolved on ``facade`` (the symbol_trade_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def _extract_trade_artifact_snapshot(
    *,
    report_path: Path,
    operator_brief_path: Path,
    lifecycle_bundle_path: Path,
    facade: Any,
) -> Dict[str, Any]:
    report = facade._read_json(report_path)
    brief = facade._read_json(operator_brief_path)
    bundle = facade._read_json(lifecycle_bundle_path)
    report_executive = report.get("executive_summary") if isinstance(report.get("executive_summary"), dict) else {}
    report_market = report.get("market_context_at_entry") if isinstance(report.get("market_context_at_entry"), dict) else {}
    report_entry = report.get("entry_decision") if isinstance(report.get("entry_decision"), dict) else {}
    report_final = report.get("final_operator_conclusion") if isinstance(report.get("final_operator_conclusion"), dict) else {}
    feedback = (
        bundle.get("strategist_feedback_input")
        if isinstance(bundle.get("strategist_feedback_input"), dict)
        else report.get("strategist_feedback_input")
        if isinstance(report.get("strategist_feedback_input"), dict)
        else {}
    )
    shared_facts = (
        bundle.get("shared_facts")
        if isinstance(bundle.get("shared_facts"), dict)
        else report.get("shared_facts")
        if isinstance(report.get("shared_facts"), dict)
        else {}
    )
    trade_outcome = bundle.get("trade_outcome") if isinstance(bundle.get("trade_outcome"), dict) else {}
    report_shared_facts = report.get("shared_facts") if isinstance(report.get("shared_facts"), dict) else {}
    artifact_result_pct = facade._pick_result_pct(
        trade_outcome.get("return_pct"),
        shared_facts.get("return_pct"),
        shared_facts.get("pnl_pct"),
        report_shared_facts.get("return_pct"),
        report_shared_facts.get("pnl_pct"),
    )
    entry_reason_text = str(report_entry.get("summary") or "").strip()
    actual_entry_reason_text = facade._actual_entry_reason_from_artifacts(
        report_path=facade.Path(report_path),
        report_entry_summary=entry_reason_text,
        bundle=bundle,
        feedback=feedback,
    )
    exit_reason_text = str(shared_facts.get("exit_reason") or "").strip()
    if not exit_reason_text:
        exit_reason_text = str(report_final.get("summary") or "").strip()
    entry_pattern_type = str(feedback.get("entry_pattern_type") or "").strip() or facade._classify_entry_pattern(actual_entry_reason_text or entry_reason_text)
    exit_pattern_type = str(feedback.get("exit_pattern_type") or "").strip() or facade._classify_exit_pattern(exit_reason_text)
    clean_entry_reason = facade._clean_symbol_reason(actual_entry_reason_text or entry_reason_text, axis="entry")
    clean_exit_reason = facade._clean_symbol_reason(exit_reason_text, axis="exit")
    return {
        "report_headline": facade._clean_symbol_free_text(report_executive.get("headline") or report.get("headline"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "report_executive_summary": facade._clean_symbol_free_text(report_executive.get("summary"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "report_market_summary": str(report_market.get("summary") or "").strip(),
        "report_entry_summary": clean_entry_reason,
        "actual_entry_reason": clean_entry_reason,
        "report_final_conclusion": facade._clean_symbol_free_text(report_final.get("summary"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "brief_headline": facade._clean_symbol_free_text(brief.get("headline"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "brief_executive_summary": facade._clean_symbol_free_text(brief.get("executive_summary"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "brief_risk_summary": facade._clean_symbol_free_text(brief.get("risk_summary"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "brief_next_checkpoints": facade._list_text(brief.get("next_checkpoints"), limit=3),
        "entry_pattern_type": facade._clean_symbol_pattern(entry_pattern_type, axis="entry", fallback_reason=clean_entry_reason),
        "exit_pattern_type": facade._clean_symbol_pattern(exit_pattern_type, axis="exit", fallback_reason=clean_exit_reason),
        "thesis_invalidation_code": facade._clean_symbol_code(feedback.get("thesis_invalidation_code")),
        "improvement_tags": facade._list_text(feedback.get("improvement_tags"), limit=6),
        "review_flags": facade._list_text(feedback.get("review_flags"), limit=6),
        "artifact_result_pct": artifact_result_pct,
    }
