"""Behavior-preserving R3 implementation bodies moved from the public facade.

Each function keeps its original body except that every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module, no getattr fallback,
no entry-time capture), so late/use-time lookup and monkeypatching match the original
module-level resolution. Owner never imports the facade.
"""
from __future__ import annotations


def _attach_report_status_matrix_r3_impl(
    report,
    story_input,
    *,
    ai_trade_report_status,
    deterministic_report_status,
    facade,
):
    out = dict(report or {})
    diagnostics = story_input.get("ai_report_diagnostics") if isinstance(story_input.get("ai_report_diagnostics"), dict) else {}
    llm_brief_status = facade._canonical_ai_report_status(diagnostics.get("llm_brief_status") or "skipped")
    out["deterministic_report_status"] = facade._canonical_ai_report_status(deterministic_report_status)
    out["llm_brief_status"] = llm_brief_status
    out["ai_trade_report_status"] = facade._canonical_ai_report_status(ai_trade_report_status)
    generation = out.get("generation") if isinstance(out.get("generation"), dict) else {}
    generation["deterministic_report_status"] = out["deterministic_report_status"]
    generation["llm_brief_status"] = out["llm_brief_status"]
    generation["ai_trade_report_status"] = out["ai_trade_report_status"]
    out["generation"] = generation
    if "fact_payload" not in out or "narrative" not in out:
        separated_trade_model = facade._resolve_separated_trade_model(story_input)
        runtime_mode = str(story_input.get("report_runtime_mode") or "").strip().lower()
        enable_separated_narrative = bool(story_input.get("enable_separated_narrative"))
        skip_separated_report_llm = bool(story_input.get("skip_separated_report_llm"))
        try:
            if enable_separated_narrative and not skip_separated_report_llm:
                from libs.reporting.fact_narrative_report import build_separated_report

                separated = build_separated_report(
                    trade_model=dict(separated_trade_model or {}),
                    model=str(generation.get("model") or "").strip() or None,
                    execution_profile=facade._resolve_intraday_report_execution_profile(
                        dict(separated_trade_model or {})
                    ),
                )
            else:
                skip_reason = (
                    f"{runtime_mode or 'runtime'}_skip_separated_report_llm"
                    if skip_separated_report_llm
                    else f"{runtime_mode or 'runtime'}_separated_narrative_disabled"
                )
                separated = facade._build_skipped_separated_report(
                    dict(separated_trade_model or {}),
                    reason=skip_reason,
                )
        except Exception:
            separated = {
                "fact_payload": {"trade": dict(separated_trade_model or {}), "daily": {}, "symbol": {}},
                "narrative": {
                    "summary": "",
                    "insight": "",
                    "recommendation": "",
                    "source": "llm",
                    "based_on": "fact_payload",
                    "status": "error",
                },
            }
        if isinstance(separated.get("fact_payload"), dict):
            out["fact_payload"] = dict(separated.get("fact_payload") or {})
        if isinstance(separated.get("narrative"), dict):
            out["narrative"] = dict(separated.get("narrative") or {})
    post_exit_shadow = facade._story_post_exit_shadow(story_input)
    if post_exit_shadow:
        out.setdefault("post_exit_shadow", dict(post_exit_shadow))
        fact_payload = out.get("fact_payload") if isinstance(out.get("fact_payload"), dict) else {}
        if fact_payload:
            fact_payload = dict(fact_payload)
            fact_payload.setdefault("post_exit_shadow", dict(post_exit_shadow))
            out["fact_payload"] = fact_payload
    return out
