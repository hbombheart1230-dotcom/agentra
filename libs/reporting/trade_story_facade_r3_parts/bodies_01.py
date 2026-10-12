"""Behavior-preserving R3 implementation bodies moved from the public facade.

Each function keeps its original body except that every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module, no getattr fallback,
no entry-time capture), so late/use-time lookup and monkeypatching match the original
module-level resolution. Owner never imports the facade.
"""
from __future__ import annotations


def build_trade_story_input_from_bundle_r3_impl(bundle_out, *, trade_lifecycle, existing_story_input, facade):
    normalized_lifecycle = facade._normalize_trade_lifecycle_for_story_input(
        bundle_out,
        trade_lifecycle=trade_lifecycle,
        existing_story_input=existing_story_input,
    )
    story_input = facade.build_trade_story_input(
        bundle_out,
        trade_lifecycle=normalized_lifecycle if normalized_lifecycle else trade_lifecycle,
    )
    existing = existing_story_input if isinstance(existing_story_input, dict) else {}
    for key in (
        "report_runtime_mode",
        "skip_separated_report_llm",
        "entry_strategist_run_id",
        "strategy_anchor_run_id",
    ):
        if key not in story_input and key in existing:
            story_input[key] = existing.get(key)
    for key in ("trade_id", "day", "run_id"):
        if story_input.get(key) in (None, "", [], {}) and existing.get(key) not in (None, "", [], {}):
            story_input[key] = existing.get(key)
    return story_input


def render_bundle_markdown_r3_impl(out, *, facade):
    story_contract = out.get("story_contract") if isinstance(out.get("story_contract"), dict) else {}
    lines: List[str] = []
    lines.append(f"# Aggregated Execution Bundle ({out.get('run_id')})")
    lines.append("")
    lines.append(f"- day: **{out.get('day')}**")
    lines.append(f"- story_anchor: **{story_contract.get('story_anchor') or '-'}**")
    lines.append(f"- story_type: **{story_contract.get('story_type') or '-'}**")
    lines.append(f"- execution_mode: **{story_contract.get('execution_mode_label') or '-'}**")
    lines.append("")
    sections = [
        ("Market Context", out.get("market_context_human")),
        ("Why This Symbol", out.get("scanner_reason_human")),
        ("Filters / Gates", out.get("filters_human")),
        ("Monitor / Trigger Reasoning", out.get("monitor_reason_human")),
        ("Guard / Approval", out.get("guard_reason_human")),
        ("Execution Outcome", out.get("execution_outcome_human")),
        ("Reporter Status", out.get("reporter_status_human")),
        ("Operator Conclusion", out.get("operator_conclusion_human")),
    ]
    for title, section in sections:
        data = section if isinstance(section, dict) else {}
        lines.append(f"## {title}")
        lines.append("")
        if data.get("summary"):
            lines.append(str(data.get("summary")))
            lines.append("")
        for bullet in list(data.get("bullets") or [])[:8]:
            lines.append(f"- {bullet}")
        lines.append("")
    lines.append("## Timeline")
    lines.append("")
    for row in list(out.get("timeline") or [])[:10]:
        if not isinstance(row, dict):
            continue
        lines.append(f"- {row.get('step')}: {row.get('summary') or '-'}")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    for key, value in dict(out.get("artifacts") or {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    return "\n".join(lines)


def render_summary_markdown_r3_impl(out, *, facade):
    bundles = out.get("bundles") if isinstance(out.get("bundles"), list) else []
    lines: List[str] = []
    lines.append(f"# Live Execution Bundles ({out.get('day')})")
    lines.append("")
    lines.append(f"- bundle_count: **{out.get('bundle_count')}**")
    lines.append(f"- canonical_trades_root: `{out.get('canonical_trades_root')}`")
    lines.append("")
    if not bundles:
        lines.append("No executed BUY/SELL runs were found for the selected day.")
        lines.append("")
        return "\n".join(lines)
    lines.append("## Bundles")
    lines.append("")
    for row in bundles:
        lines.append(
            f"- `{row.get('run_id')}` {row.get('action')} {row.get('symbol')} x{row.get('qty')} "
            f"story=`{row.get('story_type')}` report=`{row.get('trade_report_json_path')}`"
        )
    lines.append("")
    return "\n".join(lines)
