"""Pure prompt assembly for the passive reporter AI review (P1.5 DEV-A).

System/user message construction only: no LLM call, ledger write, environment read or clock. ``*_impl`` bodies take the
injected ``facade`` (``libs.reporting.reporter_ai_review``) like the other ``*_parts`` owners.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List


def _build_messages_impl(day: str, compact_input: Dict[str, Any], *, facade: Any) -> List[Dict[str, str]]:
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
        f"{json.dumps(json_contract, ensure_ascii=False)}\n\n"
        "Input summary:\n"
        f"{json.dumps(compact_input, ensure_ascii=False)}"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
