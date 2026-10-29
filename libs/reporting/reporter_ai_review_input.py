"""Reporter AI review: compact input and prompt message builders (pure; moved verbatim from reporter_ai_review).

Helpers (``_clip_str``/``_list_str``/``json``) are resolved on the ``facade`` module at call time so patches applied to
``libs.reporting.reporter_ai_review`` keep working. This module never imports the facade.
"""
from __future__ import annotations

from typing import Any, Dict, List


def build_compact_input(day: str, out: Dict[str, Any], *, facade: Any) -> Dict[str, Any]:
    trade_summary = out.get("trade_summary") if isinstance(out.get("trade_summary"), dict) else {}
    strategist_eval = out.get("strategist_evaluation") if isinstance(out.get("strategist_evaluation"), dict) else {}
    scanner_eval = out.get("scanner_evaluation") if isinstance(out.get("scanner_evaluation"), dict) else {}
    monitor_eval = out.get("monitor_evaluation") if isinstance(out.get("monitor_evaluation"), dict) else {}
    supervisor_activity = out.get("supervisor_activity") if isinstance(out.get("supervisor_activity"), dict) else {}
    intent_flow = out.get("intent_flow_analysis") if isinstance(out.get("intent_flow_analysis"), dict) else {}
    incidents = out.get("incident_postmortem") if isinstance(out.get("incident_postmortem"), dict) else {}
    market_context = out.get("market_context") if isinstance(out.get("market_context"), dict) else {}
    overtrading = out.get("overtrading_diagnostics") if isinstance(out.get("overtrading_diagnostics"), dict) else {}
    trace = out.get("decision_trace_chain_summary") if isinstance(out.get("decision_trace_chain_summary"), dict) else {}
    evidence_catalog = out.get("ai_evidence_catalog") if isinstance(out.get("ai_evidence_catalog"), dict) else {}

    chain_samples: List[Dict[str, Any]] = []
    for chain in (trace.get("chains") or [])[:12]:
        if not isinstance(chain, dict):
            continue
        strategist = chain.get("strategist") if isinstance(chain.get("strategist"), dict) else {}
        scanner = chain.get("scanner") if isinstance(chain.get("scanner"), dict) else {}
        monitor = chain.get("monitor") if isinstance(chain.get("monitor"), dict) else {}
        supervisor = chain.get("supervisor") if isinstance(chain.get("supervisor"), dict) else {}
        executor = chain.get("executor") if isinstance(chain.get("executor"), dict) else {}
        chain_samples.append(
            {
                "run_id": facade._clip_str(chain.get("run_id"), max_len=80),
                "strategist": {
                    "market_regime": facade._clip_str(strategist.get("market_regime"), max_len=40),
                    "themes": facade._list_str(strategist.get("themes"), max_items=4, max_len=40),
                    "playbook": facade._clip_str(strategist.get("playbook"), max_len=40),
                    "risk_tone": facade._clip_str(strategist.get("risk_tone"), max_len=40),
                    "monitor_guidance": facade._clip_str(strategist.get("monitor_guidance"), max_len=60),
                },
                "scanner": {
                    "candidate_pool_size": int(scanner.get("candidate_pool_size") or 0),
                    "selected_symbol": facade._clip_str(scanner.get("selected_symbol"), max_len=20),
                    "top_candidates": facade._list_str(scanner.get("top_candidates"), max_items=3, max_len=20),
                },
                "monitor": {
                    "monitor_reason": facade._clip_str(monitor.get("monitor_reason"), max_len=60),
                    "exit_reason": facade._clip_str(monitor.get("exit_reason"), max_len=60),
                    "min_hold_blocked": bool(monitor.get("min_hold_blocked")),
                    "sell_cooldown_blocked": bool(monitor.get("sell_cooldown_blocked")),
                },
                "supervisor": {
                    "verdict": facade._clip_str(supervisor.get("verdict"), max_len=32),
                    "guard_reason": facade._clip_str(supervisor.get("guard_reason"), max_len=80),
                },
                "executor": {
                    "fill_status_summary": facade._clip_str(executor.get("fill_status_summary"), max_len=40),
                },
                "complete_chain": bool(chain.get("complete_chain")),
            }
        )

    return {
        "day": str(day),
        "evidence_catalog_summary": {
            str(key): facade._clip_str((item or {}).get("summary"), max_len=180)
            for key, item in list(evidence_catalog.items())[:10]
            if isinstance(item, dict)
        },
        "market_context": {
            "global_sentiment_avg": market_context.get("global_sentiment_avg"),
            "symbol_sentiment_avg": market_context.get("symbol_sentiment_avg"),
            "llm_provider_top": market_context.get("llm_provider_top"),
            "llm_model_top": market_context.get("llm_model_top"),
        },
        "trade_summary": {
            "trade_count": int(trade_summary.get("trade_count") or 0),
            "symbols_traded": list(trade_summary.get("symbols_traded") or [])[:8],
        },
        "strategist_evaluation": {
            "theme_alignment_status": strategist_eval.get("theme_alignment_status"),
            "themes_proposed": list(strategist_eval.get("themes_proposed") or [])[:8],
            "assessment": facade._clip_str(strategist_eval.get("assessment"), max_len=220),
        },
        "scanner_evaluation": {
            "selection_status": scanner_eval.get("selection_status"),
            "no_candidate_total": int(scanner_eval.get("no_candidate_total") or 0),
            "selected_symbol_top": scanner_eval.get("selected_symbol_top") or {},
            "assessment": facade._clip_str(scanner_eval.get("assessment"), max_len=220),
        },
        "monitor_evaluation": {
            "monitor_status": monitor_eval.get("monitor_status"),
            "rapid_buy_sell_cycles": int(monitor_eval.get("rapid_buy_sell_cycles") or 0),
            "monitor_reason_top": monitor_eval.get("monitor_reason_top") or {},
            "assessment": facade._clip_str(monitor_eval.get("assessment"), max_len=220),
        },
        "supervisor_activity": {
            "blocked_rate": supervisor_activity.get("blocked_rate"),
            "blocked_total": int(supervisor_activity.get("blocked_total") or 0),
            "blocked_reason_top": supervisor_activity.get("blocked_reason_top") or {},
            "assessment": facade._clip_str(supervisor_activity.get("assessment"), max_len=220),
        },
        "intent_flow_analysis": {
            "intents_created": int(intent_flow.get("intents_created") or 0),
            "intents_blocked": int(intent_flow.get("intents_blocked") or 0),
            "intents_approved": int(intent_flow.get("intents_approved") or 0),
            "intents_executed": int(intent_flow.get("intents_executed") or 0),
            "reason_top": intent_flow.get("reason_top") or {},
        },
        "overtrading_diagnostics": {
            "rapid_buy_sell_cycles": int(overtrading.get("rapid_buy_sell_cycles") or 0),
            "guard_block_rate": overtrading.get("guard_block_rate"),
            "noise_exit_related_count": int(overtrading.get("noise_exit_related_count") or 0),
        },
        "incidents": incidents.get("incidents") or [],
        "improvement_suggestions": list(out.get("improvement_suggestions") or [])[:8],
        "decision_trace_chain_samples": chain_samples,
    }


def build_messages(day: str, compact_input: Dict[str, Any], *, facade: Any) -> List[Dict[str, str]]:
    system_prompt = (
        "You are an AI post-run reviewer for a trading agent system. "
        "You must remain passive and never suggest direct live execution actions. "
        "Given deterministic summaries, return concise JSON only. "
        "Prefer 2-3 short findings, 1-3 root causes, and 1-3 concrete improvement suggestions. "
        "Do not return empty arrays when evidence_catalog_summary contains meaningful evidence."
    )
    json_contract = {
        "ai_summary": "string",
        "ai_findings": ["string"],
        "ai_root_causes": ["string"],
        "ai_improvement_suggestions": ["string"],
        "ai_run_grade": "A+|A|B+|B|C|D|F",
        "ai_agent_evaluations": {
            "strategist": "good|mixed|needs_improvement",
            "scanner": "good|mixed|needs_improvement",
            "monitor": "good|mixed|needs_improvement",
            "supervisor": "good|mixed|needs_improvement",
            "executor": "good|mixed|needs_improvement",
        },
        "ai_evidence_links": {
            "findings": [{"text": "same as ai_findings[i]", "evidence_keys": ["evidence_catalog_key"]}],
            "root_causes": [{"text": "same as ai_root_causes[i]", "evidence_keys": ["evidence_catalog_key"]}],
            "improvements": [{"text": "same as ai_improvement_suggestions[i]", "evidence_keys": ["evidence_catalog_key"]}],
        },
    }
    user_prompt = (
        f"Day: {day}\n"
        "Analyze the run quality and answer these aspects: strategist reasonableness, scanner fit, "
        "monitor exit quality, overtrading risk, supervisor guard appropriateness, anomalies, and next-run improvements.\n"
        "Use only evidence keys already present in evidence_catalog_summary. "
        "ai_evidence_links rows must align by index with ai_findings / ai_root_causes / ai_improvement_suggestions.\n"
        "If the run has any meaningful deterministic evidence, each of ai_findings / ai_root_causes / "
        "ai_improvement_suggestions must contain at least one item.\n"
        "Return strict JSON matching this contract keys only:\n"
        f"{facade.json.dumps(json_contract, ensure_ascii=False)}\n\n"
        "Input summary:\n"
        f"{facade.json.dumps(compact_input, ensure_ascii=False)}"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
