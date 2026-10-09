from __future__ import annotations

import html
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

from .summary_parts.findings import collect_deterministic_summary_findings
from .summary_parts.render_diagnostics import collect_render_diagnostics
from .summary_render_parts.main_renderer import render_trade_summary_markdown_impl
from .summary_render_parts.render_helpers import (
    pick_impl,
    money_impl,
    compact_number_impl,
    compact_decimal_impl,
    first_matching_line_impl,
    section_texts_impl,
    same_day_summary_impl,
    selected_score_impl,
    selected_rank_impl,
    extract_run_id_impl,
    policy_delta_lines_impl,
)
from .summary_input_parts.main_builder import build_trade_summary_input_impl
from .summary_input_parts.broker_alignment import build_broker_alignment
from .summary_input_parts.market_and_strategy import build_market_and_strategy
from .summary_input_parts.decision_flow import build_decision_flow


from .summary_render_parts.overview import append_summary_overview
from .summary_render_parts.market_news import append_summary_market_news
from .summary_render_parts.decision_lifecycle import append_summary_decision_lifecycle
from .summary_render_parts.closing import append_summary_closing



def render_trade_summary_markdown(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> str:
    """Preserve the public renderer API and call-time patchable helper bindings."""
    return render_trade_summary_markdown_impl(
        report, deps=deps,
        append_summary_overview=append_summary_overview, append_summary_market_news=append_summary_market_news, append_summary_decision_lifecycle=append_summary_decision_lifecycle,
        append_summary_closing=append_summary_closing, collect_render_diagnostics=collect_render_diagnostics, pick_impl=pick_impl,
        money_impl=money_impl, compact_number_impl=compact_number_impl, compact_decimal_impl=compact_decimal_impl,
        first_matching_line_impl=first_matching_line_impl, section_texts_impl=section_texts_impl, same_day_summary_impl=same_day_summary_impl,
        selected_score_impl=selected_score_impl, selected_rank_impl=selected_rank_impl, extract_run_id_impl=extract_run_id_impl,
        policy_delta_lines_impl=policy_delta_lines_impl,
    )


def build_trade_summary_input(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    """Keep public identity and call-time monkeypatchable dependency boundaries."""
    return build_trade_summary_input_impl(
        report, deps=deps,
        collect_deterministic_summary_findings=collect_deterministic_summary_findings,
        build_broker_alignment=build_broker_alignment,
        build_market_and_strategy=build_market_and_strategy,
        build_decision_flow=build_decision_flow,
    )
