from __future__ import annotations
from typing import Any, Dict, List

def _build_markdown(summary: Dict[str, Any], *, facade: Any) -> str:
    exe = summary.get("execution") if isinstance(summary.get("execution"), dict) else {}
    noop = summary.get("noop") if isinstance(summary.get("noop"), dict) else {}
    llm = summary.get("strategist_llm") if isinstance(summary.get("strategist_llm"), dict) else {}

    lines: List[str] = [
        f"# Ops Diagnostic Report ({summary.get('day')})",
        "",
        f"- schema_version: **{summary.get('schema_version')}**",
        f"- events: **{int(summary.get('events') or 0)}**",
        f"- runs: **{int(summary.get('runs') or 0)}**",
        "",
        "## Execution",
        "",
        f"- execution_total: **{int(exe.get('execution_total') or 0)}**",
        f"- verdict_block_total: **{int(exe.get('verdict_block_total') or 0)}**",
        f"- broker_success_total: **{int(exe.get('broker_success_total') or 0)}**",
        f"- broker_fail_total: **{int(exe.get('broker_fail_total') or 0)}**",
        f"- broker_unknown_total: **{int(exe.get('broker_unknown_total') or 0)}**",
        f"- broker_success_rate: **{float(exe.get('broker_success_rate') or 0.0):.2%}**",
        "",
        "### verdict_reason_topN",
        "",
    ]

    top_verdict = exe.get("verdict_reason_topN") if isinstance(exe.get("verdict_reason_topN"), list) else []
    if top_verdict:
        for row in top_verdict:
            if not isinstance(row, dict):
                continue
            lines.append(f"- {row.get('reason')}: {int(row.get('count') or 0)}")
    else:
        lines.append("- (none)")

    lines += ["", "### broker_failure_topN", ""]
    top_fail = exe.get("broker_failure_topN") if isinstance(exe.get("broker_failure_topN"), list) else []
    if top_fail:
        for row in top_fail:
            if not isinstance(row, dict):
                continue
            lines.append(f"- {row.get('broker_code')}: {int(row.get('count') or 0)}")
    else:
        lines.append("- (none)")

    lines += ["", "## NOOP", "", f"- total: **{int(noop.get('total') or 0)}**", "", "### focus_reason_ratio", ""]
    focus = noop.get("focus_reason_ratio") if isinstance(noop.get("focus_reason_ratio"), dict) else {}
    for key in ("model_no_signal", "missing_rationale", "post_exit_cooldown"):
        lines.append(f"- {key}: {float(focus.get(key) or 0.0):.2%}")

    latency = llm.get("latency_ms") if isinstance(llm.get("latency_ms"), dict) else {}
    lines += [
        "",
        "## Strategist LLM",
        "",
        f"- total: **{int(llm.get('total') or 0)}**",
        f"- ok_total: **{int(llm.get('ok_total') or 0)}**",
        f"- error_total: **{int(llm.get('error_total') or 0)}**",
        f"- latency_ms_p50: **{float(latency.get('p50') or 0.0):.1f}**",
        f"- latency_ms_p95: **{float(latency.get('p95') or 0.0):.1f}**",
        "",
    ]
    return "\n".join(lines)


