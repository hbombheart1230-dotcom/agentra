from __future__ import annotations

from datetime import timedelta
from typing import Any, Callable, Dict, Iterable, List, Mapping
import sys as _r3_sys
from libs.agents.reporter.narrative.strategy_memory_md_bodies_01 import (  # R-4 owner bodies (facade-injected)
    strategy_horizon_label_r4_impl,
    strategy_horizon_reason_label_r4_impl,
    strategy_horizon_alignment_label_r4_impl,
    duration_label_compact_r4_impl,
    hold_window_label_r4_impl,
    strategy_horizon_report_surface_r4_impl,
    build_strategy_horizon_lines_r4_impl,
    carryover_context_r4_impl,
    build_prompt_proven_memory_r4_impl,
)
from libs.agents.reporter.narrative.strategy_memory_md_bodies_02 import (  # R-4 owner bodies (facade-injected)
    build_memory_application_r4_impl,
)


def strategy_horizon_label(value: Any, *, metadata_value: Callable[[Any], str]) -> str:
    return strategy_horizon_label_r4_impl(value, metadata_value=metadata_value, facade=_r3_sys.modules[__name__])


def strategy_horizon_reason_label(value: Any, *, metadata_value: Callable[[Any], str]) -> str:
    return strategy_horizon_reason_label_r4_impl(value, metadata_value=metadata_value, facade=_r3_sys.modules[__name__])


def strategy_horizon_alignment_label(value: Any, *, metadata_value: Callable[[Any], str]) -> str:
    return strategy_horizon_alignment_label_r4_impl(value, metadata_value=metadata_value, facade=_r3_sys.modules[__name__])


def duration_label_compact(value: Any, *, num_opt: Callable[[Any], float | None]) -> str:
    return duration_label_compact_r4_impl(value, num_opt=num_opt, facade=_r3_sys.modules[__name__])


def hold_window_label(
    window: Dict[str, Any],
    *,
    as_dict: Callable[[Any], Dict[str, Any]],
    duration_label_compact_fn: Callable[[Any], str],
) -> str:
    return hold_window_label_r4_impl(window, as_dict=as_dict, duration_label_compact_fn=duration_label_compact_fn, facade=_r3_sys.modules[__name__])


def strategy_horizon_report_surface(
    report: Dict[str, Any],
    *,
    as_dict: Callable[[Any], Dict[str, Any]],
    first_report_path: Callable[[Dict[str, Any], Iterable[str]], Any],
    compact_post_exit_shadow: Callable[[Dict[str, Any]], Dict[str, Any]],
    post_exit_shadow_surface: Callable[[Dict[str, Any]], Dict[str, Any]],
    carryover_context: Callable[[Dict[str, Any]], Dict[str, Any]],
    num_opt: Callable[[Any], float | None],
    duration_label_compact_fn: Callable[[Any], str],
) -> Dict[str, Any]:
    return strategy_horizon_report_surface_r4_impl(report, as_dict=as_dict, first_report_path=first_report_path, compact_post_exit_shadow=compact_post_exit_shadow, post_exit_shadow_surface=post_exit_shadow_surface, carryover_context=carryover_context, num_opt=num_opt, duration_label_compact_fn=duration_label_compact_fn, facade=_r3_sys.modules[__name__])


def build_strategy_horizon_lines(
    report: Dict[str, Any],
    *,
    compact: bool = False,
    strategy_horizon_report_surface_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    strategy_horizon_label_fn: Callable[[Any], str],
    strategy_horizon_alignment_label_fn: Callable[[Any], str],
    strategy_horizon_reason_label_fn: Callable[[Any], str],
    as_dict: Callable[[Any], Dict[str, Any]],
    axis_label: Callable[[Any], str],
    hold_window_label_fn: Callable[[Dict[str, Any]], str],
    duration_label_compact_fn: Callable[[Any], str],
) -> List[str]:
    return build_strategy_horizon_lines_r4_impl(report, compact=compact, strategy_horizon_report_surface_fn=strategy_horizon_report_surface_fn, strategy_horizon_label_fn=strategy_horizon_label_fn, strategy_horizon_alignment_label_fn=strategy_horizon_alignment_label_fn, strategy_horizon_reason_label_fn=strategy_horizon_reason_label_fn, as_dict=as_dict, axis_label=axis_label, hold_window_label_fn=hold_window_label_fn, duration_label_compact_fn=duration_label_compact_fn, facade=_r3_sys.modules[__name__])

# P1.5.2 R2-B: carryover / prompt-proven memory / memory-application owners.


def carryover_context(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    return carryover_context_r4_impl(report, deps=deps, facade=_r3_sys.modules[__name__])



def build_prompt_proven_memory(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> List[str]:
    return build_prompt_proven_memory_r4_impl(report, deps=deps, facade=_r3_sys.modules[__name__])


def build_memory_application(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> List[str]:
    return build_memory_application_r4_impl(report, deps=deps, facade=_r3_sys.modules[__name__])

