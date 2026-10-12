"""Strategist LLM commander-refresh context and read-model compaction (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _build_llm_commander_refresh_context_r3_impl(
    commander_context,
    read_model_facts,
    reports_root,
    *,
    facade,
):
    context = dict(commander_context or {}) if isinstance(commander_context, dict) else {}
    open_position_refresh_context = (
        dict(context.get("open_position_refresh_context") or {})
        if isinstance(context.get("open_position_refresh_context"), dict)
        else {}
    )
    strategist_refresh_context = (
        dict(context.get("strategist_refresh_context") or {})
        if isinstance(context.get("strategist_refresh_context"), dict)
        else {}
    )
    refresh_context = (
        dict(open_position_refresh_context)
        if open_position_refresh_context
        else dict(strategist_refresh_context)
    )
    commander_horizon_policy = (
        dict(context.get("commander_horizon_policy") or {})
        if isinstance(context.get("commander_horizon_policy"), dict)
        else dict(strategist_refresh_context.get("commander_horizon_policy") or {})
        if isinstance(strategist_refresh_context.get("commander_horizon_policy"), dict)
        else dict(open_position_refresh_context.get("commander_horizon_policy") or {})
        if isinstance(open_position_refresh_context.get("commander_horizon_policy"), dict)
        else {}
    )
    selected_symbol = str(refresh_context.get("selected_symbol") or "")
    selected_symbol_was_rank1_raw = refresh_context.get("selected_symbol_was_rank1")
    selected_symbol_was_rank1 = (
        bool(selected_symbol_was_rank1_raw)
        if selected_symbol_was_rank1_raw is not None
        else int(refresh_context.get("selected_rank") or 0) == 1
    )
    return {
        "requested": bool(context.get("strategist_refresh_requested")),
        "reason": str(context.get("strategist_refresh_reason") or ""),
        "refresh_scope": str(refresh_context.get("refresh_scope") or ""),
        "selected_symbol": selected_symbol,
        "hold_repeat_count_max": int(refresh_context.get("hold_repeat_count_max") or 0),
        "selected_hold_repeat_count": int(refresh_context.get("selected_hold_repeat_count") or 0),
        "monitor_reason": str(refresh_context.get("monitor_reason") or ""),
        "active_exit_axis": str(refresh_context.get("active_exit_axis") or ""),
        "refresh_summary": str(refresh_context.get("refresh_summary") or ""),
        "selected_rank": int(refresh_context.get("selected_rank") or 0),
        "selected_score": facade._round_optional(refresh_context.get("selected_score"), 4),
        "scanner_primary_candidate": dict(refresh_context.get("scanner_primary_candidate") or {}),
        "actual_selected_candidate": dict(
            refresh_context.get("actual_selected_candidate")
            or refresh_context.get("scanner_primary_candidate")
            or {}
        ),
        "scanner_rank1_candidate": dict(refresh_context.get("scanner_rank1_candidate") or {}),
        "scanner_runner_ups": [
            dict(row)
            for row in list(refresh_context.get("scanner_runner_ups") or [])[:4]
            if isinstance(row, dict)
        ],
        "scanner_top_candidates": [
            dict(row)
            for row in list(refresh_context.get("scanner_top_candidates") or [])[:5]
            if isinstance(row, dict)
        ],
        "selected_symbol_was_rank1": bool(selected_symbol_was_rank1),
        "stage2_context_quality": str(refresh_context.get("stage2_context_quality") or ""),
        "stage2_context_quality_reasons": [
            str(reason or "")
            for reason in list(refresh_context.get("stage2_context_quality_reasons") or [])[:6]
            if str(reason or "").strip()
        ],
        "entry_state": dict(refresh_context.get("entry_state") or {}),
        "carry_state": str(refresh_context.get("carry_state") or context.get("carry_state") or ""),
        "carry_risk_bias": str(
            refresh_context.get("carry_risk_bias") or context.get("carry_risk_bias") or ""
        ),
        "carry_risk_reason": str(
            refresh_context.get("carry_risk_reason") or context.get("carry_risk_reason") or ""
        ),
        "session_open_recovery_assessment": dict(
            refresh_context.get("session_open_recovery_assessment")
            or context.get("session_open_recovery_assessment")
            or {}
        ),
        "prior_monitor_entry_policy_summary": dict(
            refresh_context.get("prior_monitor_entry_policy_summary")
            or strategist_refresh_context.get("prior_monitor_entry_policy_summary")
            or {}
        )
        if isinstance(
            refresh_context.get("prior_monitor_entry_policy_summary")
            or strategist_refresh_context.get("prior_monitor_entry_policy_summary"),
            dict,
        )
        else {},
        "current_monitor_entry_policy_summary": dict(
            refresh_context.get("current_monitor_entry_policy_summary")
            or strategist_refresh_context.get("current_monitor_entry_policy_summary")
            or {}
        )
        if isinstance(
            refresh_context.get("current_monitor_entry_policy_summary")
            or strategist_refresh_context.get("current_monitor_entry_policy_summary"),
            dict,
        )
        else {},
        "commander_horizon_policy": dict(commander_horizon_policy),
        "horizon_context": {
            "owner": str(commander_horizon_policy.get("owner") or "commander") if commander_horizon_policy else "",
            "strategy_horizon": str(commander_horizon_policy.get("strategy_horizon") or ""),
            "source_strategy_horizon": str(commander_horizon_policy.get("source_strategy_horizon") or ""),
            "observability_only": bool(commander_horizon_policy.get("observability_only", True))
            if commander_horizon_policy
            else True,
            "do_not_force_hold": bool(commander_horizon_policy.get("do_not_force_hold", True))
            if commander_horizon_policy
            else True,
        },
        "requires_policy_delta": bool(context.get("strategist_refresh_requested")),
        "selected_symbol_memory": facade._build_symbol_refresh_memory_excerpt(
            selected_symbol,
            read_model_facts,
            reports_root,
        ),
    }


def _compact_top_metric_map_r3_impl(raw, *, max_items, facade):
    if not isinstance(raw, dict):
        return {}
    rows: List[tuple[str, float]] = []
    for key, value in raw.items():
        name = str(key or "").strip()
        if not name:
            continue
        try:
            metric = float(value)
        except Exception:
            metric = 0.0
        rows.append((name, metric))
    rows.sort(key=lambda item: (-item[1], item[0]))
    out: Dict[str, Any] = {}
    for name, metric in rows[: max(0, int(max_items))]:
        out[name] = facade._round_optional(metric, 4)
    return out


def _compact_performance_summary_map_r3_impl(raw, *, max_items, facade):
    if not isinstance(raw, dict):
        return {}
    rows: List[tuple[str, float, Dict[str, Any]]] = []
    for key, value in raw.items():
        name = str(key or "").strip()
        item = value if isinstance(value, dict) else {}
        if not name:
            continue
        priority = 0.0
        if isinstance(item, dict):
            priority = float(item.get("appearance_count") or item.get("trade_count_total") or 0.0)
        rows.append((name, priority, item))
    rows.sort(key=lambda item: (-item[1], item[0]))
    out: Dict[str, Any] = {}
    for name, _priority, item in rows[: max(0, int(max_items))]:
        compact_item = {
            "appearance_count": int(item.get("appearance_count") or 0),
            "metric_basis": str(item.get("metric_basis") or ""),
            "performance_metric_usable": bool(
                item.get("performance_metric_usable")
            ),
        }
        if bool(item.get("performance_metric_usable")):
            compact_item["win_rate"] = facade._round_optional(item.get("win_rate"), 4)
            compact_item["avg_return_pct"] = facade._round_optional(
                item.get("avg_return_pct"),
                4,
            )
        out[name] = compact_item
    return out


def _compact_pattern_performance_for_llm_r3_impl(snapshot, *, facade):
    src = snapshot if isinstance(snapshot, dict) else {}
    out: Dict[str, Any] = {}
    for section, limit in (
        ("entry_pattern_types", 4),
        ("exit_pattern_types", 4),
        ("entry_exit_combos", 5),
    ):
        section_rows = src.get(section) if isinstance(src.get(section), dict) else {}
        compact_rows: Dict[str, Any] = {}
        for key, value in list(section_rows.items())[:limit]:
            item = value if isinstance(value, dict) else {}
            compact_rows[str(key)] = {
                "trade_count": int(item.get("trade_count") or 0),
                "win_rate": facade._round_optional(item.get("win_rate"), 4),
                "avg_return": facade._round_optional(item.get("avg_return"), 4),
                "symbols": [str(x or "") for x in list(item.get("symbols") or [])[:4] if str(x or "").strip()],
            }
        out[section] = compact_rows
    out["problem_patterns"] = [
        str(x or "") for x in list(src.get("problem_patterns") or [])[:6] if str(x or "").strip()
    ]
    out["working_patterns"] = [
        str(x or "") for x in list(src.get("working_patterns") or [])[:4] if str(x or "").strip()
    ]
    return out


def _compact_scalar_mapping_for_llm_r3_impl(src, *, allowed_keys, max_text_len, facade):
    obj = src if isinstance(src, dict) else {}
    out: Dict[str, Any] = {}
    for key in allowed_keys:
        if key not in obj:
            continue
        value = obj.get(key)
        if isinstance(value, str):
            out[key] = facade._clip_text_for_llm(value, max_len=max_text_len)
        elif isinstance(value, (int, float, bool)) or value is None:
            out[key] = value
        elif isinstance(value, list):
            out[key] = [
                facade._clip_text_for_llm(x, max_len=max_text_len) if not isinstance(x, dict) else x
                for x in list(value)[:4]
            ]
    return out


def _compact_pattern_rows_for_llm_r3_impl(rows, *, limit, facade):
    out: List[Dict[str, Any]] = []
    for row in list(rows or [])[:limit]:
        if not isinstance(row, dict):
            continue
        compact = facade._compact_scalar_mapping_for_llm(
            row,
            allowed_keys=[
                "type",
                "value",
                "count",
                "playbook",
                "entry_reason",
                "exit_reason",
                "monitor_reason",
                "blocker",
                "pattern",
                "win_rate",
                "avg_return",
                "avg_pnl_pct",
            ],
            max_text_len=100,
        )
        if compact:
            out.append(compact)
    return out


def _compact_trade_read_model_for_llm_r3_impl(row, *, facade):
    src = row if isinstance(row, dict) else {}
    return facade._compact_scalar_mapping_for_llm(
        src,
        allowed_keys=[
            "trade_id",
            "symbol",
            "entry_ts",
            "exit_ts",
            "entry_price",
            "exit_price",
            "qty",
            "hold_duration_sec",
            "pnl",
            "pnl_pct",
            "return_pct",
            "net_return_pct",
            "realized_pnl",
            "realized_pnl_pct",
            "kiwoom_pnl_pct",
            "entry_reason",
            "exit_reason",
            "entry_pattern",
            "exit_pattern",
            "playbook",
            "monitor_reason",
        ],
        max_text_len=120,
    )
