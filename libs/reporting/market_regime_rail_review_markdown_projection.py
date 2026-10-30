"""Market regime rail review markdown rendering (moved verbatim from market_regime_rail_review).

``Mapping`` is resolved on ``facade`` (the market_regime_rail_review module) at call time; this module never imports it.
Pure formatting; no IO.
"""
from __future__ import annotations

from typing import Any, Mapping


def render_market_regime_rail_markdown(rail: Mapping[str, Any], *, day: str, facade: Any) -> str:
    inputs = rail.get("market_inputs") if isinstance(rail.get("market_inputs"), facade.Mapping) else {}
    lines = [
        f"# Market Regime Rail Review ({day})",
        "",
        "This report is read-only evaluation output. It does not change trading behavior.",
        "",
        "## Rail",
        "",
        f"- rail_id: `{rail.get('rail_id') or 'not_available'}`",
        f"- confidence: `{rail.get('rail_confidence') or 'none'}`",
        f"- behavior_effect: `{rail.get('behavior_effect') or 'evaluation_only'}`",
        f"- source: `{rail.get('source') or '-'}`",
        f"- rationale: {rail.get('rationale') or '-'}",
        "",
        "## Market Inputs",
        "",
    ]
    for key in (
        "kospi_pct",
        "kosdaq_pct",
        "kospi200_pct",
        "krx_night_futures_pct",
        "breadth",
        "nasdaq_pct",
        "sp500_pct",
        "usdkrw_pct",
        "dxy_pct",
        "vix_level",
        "vix_pct",
        "global_sentiment_score",
    ):
        lines.append(f"- {key}: **{float(inputs.get(key) or 0.0):.4f}**")
    if inputs.get("krx_night_futures_status") or inputs.get("krx_night_futures_pressure"):
        lines.append(f"- krx_night_futures_status: `{inputs.get('krx_night_futures_status') or '-'}`")
        lines.append(f"- krx_night_futures_pressure: `{inputs.get('krx_night_futures_pressure') or '-'}`")
    sanity = rail.get("market_input_sanity") if isinstance(rail.get("market_input_sanity"), facade.Mapping) else {}
    warnings = sanity.get("warnings") if isinstance(sanity.get("warnings"), list) else []
    if warnings:
        lines += ["", "## Market Input Sanity", ""]
        lines.append(f"- status: `{sanity.get('status') or 'warning'}`")
        lines.append(f"- extreme_move_requires_confirmation: `{bool(sanity.get('extreme_move_requires_confirmation'))}`")
        for row in warnings[:8]:
            if not isinstance(row, facade.Mapping):
                continue
            lines.append(
                "- warning: "
                f"`{row.get('code')}` {row.get('index') or '-'} "
                f"change_pct={float(row.get('change_pct') or 0.0):.4f} "
                f"severity=`{row.get('severity') or '-'}`"
            )
    lines += ["", "## Expected Tactical Behavior", ""]
    for item in list(rail.get("expected_tactical_behavior") or []):
        lines.append(f"- {item}")
    lines += ["", "## Q8 Review Focus", ""]
    for item in list(rail.get("q8_review_focus") or []):
        lines.append(f"- `{item}`")
    return "\n".join(lines).rstrip() + "\n"
