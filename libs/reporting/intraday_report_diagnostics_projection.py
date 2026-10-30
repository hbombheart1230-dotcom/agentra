"""intraday_trade_reports projections (moved verbatim from intraday_trade_reports).

Module globals and helpers are resolved on ``facade`` (the intraday_trade_reports module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict


def _report_diagnostics_from_report(report: Dict[str, Any], llm_artifact: Dict[str, Any], *, facade: Any) -> Dict[str, Any]:
    generation = report.get("generation") if isinstance(report.get("generation"), dict) else {}
    generation_status = str(generation.get("status") or llm_artifact.get("status") or "").strip().lower()
    generation_mode = str(generation.get("mode") or "").strip().lower()
    declared_ai_status = str(
        report.get("ai_trade_report_status")
        or generation.get("ai_trade_report_status")
        or ""
    ).strip().lower()
    model = str(generation.get("model") or llm_artifact.get("model") or ((llm_artifact.get("model_info") or {}).get("model")) or "")
    deterministic_only = generation_mode in {"deterministic", "local_debug"} or (
        declared_ai_status == "skipped" and generation_status in {"ok", "skipped", ""}
    )
    if deterministic_only:
        ai_trade_report_status = "skipped"
    elif generation_status in {"ok", "repaired"}:
        ai_trade_report_status = "ok"
    elif generation_status in {"partial", "salvaged"}:
        ai_trade_report_status = "partial"
    elif generation_status in {"skipped", "disabled"}:
        ai_trade_report_status = "skipped"
    else:
        ai_trade_report_status = "error"
    diagnostics = {
        "report_status": "failed",
        "report_reason_code": "llm_generation_failed",
        "report_reason_human": "AI trade report generation failed.",
        "report_generation_reason": "AI trade report generation failed.",
        "generation_attempted": True,
        "generation_ts": facade._utc_now_iso(),
        "story_input_available": True,
        "report_output_available": True,
        "report_artifact_available": True,
        "llm_model_used": model,
        "last_error_message": str(llm_artifact.get("error") or ""),
        "next_expected_step": "Inspect the LLM response artifact and retry generation.",
        "deterministic_report_status": str(
            report.get("deterministic_report_status")
            or generation.get("deterministic_report_status")
            or "ok"
        ),
        "llm_brief_status": str(report.get("llm_brief_status") or generation.get("llm_brief_status") or "skipped"),
        "ai_trade_report_status": ai_trade_report_status,
        "llm_response_status": str(llm_artifact.get("status") or ""),
        "llm_parse_mode": str(llm_artifact.get("parse_mode") or ""),
        "llm_completeness_score": float(llm_artifact.get("completeness_score") or 0.0),
        "llm_required_keys_missing": [
            str(x or "")
            for x in list(llm_artifact.get("required_keys_missing") or [])
            if str(x or "").strip()
        ],
    }
    if deterministic_only:
        diagnostics.update(
            {
                "report_status": "available",
                "report_reason_code": "deterministic_only",
                "report_reason_human": "Deterministic report was generated without AI expansion.",
                "report_generation_reason": "Deterministic report was generated without AI expansion.",
                "generation_attempted": False,
                "next_expected_step": "Review deterministic report sections and evidence linkage.",
                "last_error_message": "",
            }
        )
    elif generation_status in {"ok", "repaired"}:
        diagnostics.update(
            {
                "report_status": "available",
                "report_reason_code": "",
                "report_reason_human": "AI trade report was generated successfully.",
                "report_generation_reason": "AI trade report was generated successfully.",
                "next_expected_step": "Open the full report for detailed lifecycle analysis.",
                "last_error_message": "",
            }
        )
    elif generation_status in {"partial", "salvaged"}:
        diagnostics.update(
            {
                "report_status": "available",
                "report_reason_code": "llm_generation_salvaged",
                "report_reason_human": "AI trade report was generated with partial recovery.",
                "report_generation_reason": "AI trade report was generated with partial recovery.",
                "next_expected_step": "Open the report and review completeness metadata before relying on every section.",
            }
        )
    return diagnostics
