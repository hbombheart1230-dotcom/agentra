"""Scanner open-order counts, feature-engine map and policy-trace evidence (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _extract_account_open_order_counts_r3_impl(state, *, facade):
    rows, meta = facade.extract_account_orders_rows(state)

    out: Dict[str, int] = {}
    for r in rows:
        if not isinstance(r, dict):
            continue
        if not facade.account_order_is_pending(r):
            continue
        symbol = facade._norm_symbol(r.get("symbol") or r.get("stk_cd") or r.get("code"))
        if not symbol:
            continue
        out[symbol] = int(out.get(symbol, 0)) + 1
    return out, len(rows), meta


def _should_auto_hydrate_scanner_skills_r3_impl(state, candidates, *, facade):
    policy = state.get("policy") if isinstance(state.get("policy"), dict) else {}
    explicit = policy.get("enable_scanner_skill_hydration")
    if explicit is not None:
        enabled = facade._is_trueish(explicit)
    else:
        env_value = facade.os.getenv("SCANNER_AUTO_SKILL_HYDRATION", "")
        if env_value:
            enabled = facade._is_trueish(env_value)
        else:
            enabled = not bool(facade.os.getenv("PYTEST_CURRENT_TEST"))
    if not enabled:
        return False

    if state.get("skill_runner") is not None or callable(state.get("skill_runner_factory")):
        return True
    if facade._is_trueish(state.get("auto_skill_runner")) or facade._is_trueish(facade.os.getenv("M22_AUTO_SKILL_RUNNER", "")):
        return True

    candidate_symbols: List[str] = []
    for item in candidates:
        if isinstance(item, dict):
            sym = facade._norm_symbol(item.get("symbol"))
        else:
            sym = facade._norm_symbol(item)
        if sym:
            candidate_symbols.append(sym)
    return any(facade._is_live_equity_symbol(sym) for sym in candidate_symbols)


def _extract_feature_engine_map_r3_impl(state, *, facade):
    errors: List[str] = []

    # Priority 1: explicit features map injection.
    direct = state.get("scanner_features")
    if isinstance(direct, dict):
        out: Dict[str, Dict[str, Any]] = {}
        for k, v in direct.items():
            if not isinstance(v, dict):
                continue
            sym = facade._norm_symbol(k)
            if sym:
                out[sym] = dict(v)
        return out, "state.scanner_features", errors

    # Priority 2: precomputed feature engine output.
    fe = state.get("feature_engine")
    if isinstance(fe, dict) and isinstance(fe.get("by_symbol"), dict):
        out2: Dict[str, Dict[str, Any]] = {}
        by_symbol = fe.get("by_symbol") or {}
        for k, v in by_symbol.items():
            if not isinstance(v, dict):
                continue
            sym = facade._norm_symbol(k)
            if sym:
                out2[sym] = dict(v)
        return out2, "state.feature_engine.by_symbol", errors

    # Priority 3: compute from OHLCV data if available.
    ohlcv = state.get("ohlcv_by_symbol")
    if isinstance(ohlcv, dict):
        try:
            policy = state.get("policy") if isinstance(state.get("policy"), dict) else {}
            trend_gap_threshold = float(policy.get("feature_trend_gap_threshold", 0.01))
            high_vol_threshold = float(policy.get("feature_high_vol_threshold", 0.03))
            ctx: Dict[str, Any] = {
                "global_sentiment": facade._get_global_sentiment_score(state),
            }
            # Optional context hooks (already normalized in state when available).
            if isinstance(state.get("market_context"), dict):
                mc = state.get("market_context") or {}
                if mc.get("market_breadth") is not None:
                    ctx["market_breadth"] = mc.get("market_breadth")
                if mc.get("index_trend") is not None:
                    ctx["index_trend"] = mc.get("index_trend")
                if mc.get("realized_vol") is not None:
                    ctx["realized_vol"] = mc.get("realized_vol")
            built = facade.build_feature_map(
                ohlcv,
                trend_gap_threshold=trend_gap_threshold,
                high_vol_threshold=high_vol_threshold,
                context=ctx,
            )
            return {facade._norm_symbol(k): v for k, v in built.items() if facade._norm_symbol(k)}, "state.ohlcv_by_symbol", errors
        except Exception as e:
            errors.append(f"feature_engine:error:{type(e).__name__}")

    return {}, "none", errors


def _build_scanner_policy_trace_r3_impl(
    *,
    commander_context,
    strategist_plan,
    policy_provenance,
    playbook,
    scanner_priority,
    scanner_bias,
    scanner_bias_context,
    scanner_memory_bias,
    facade,
):
    consumed_fields: List[str] = []
    for key in (
        "scanner_mission",
        "allowed_playbooks",
        "banned_playbooks",
        "risk_mode",
        "command_intent",
        "strategist_invocation",
        "no_trade_reason_code",
        "source_priority",
    ):
        value = commander_context.get(key)
        if value not in (None, "", [], {}):
            consumed_fields.append(key)
    commander_context_consumed = bool(consumed_fields)

    strategist_consumed_fields: List[str] = []
    for key in ("selected_playbook", "candidate_hypotheses", "symbol_constraints", "strategy_summary"):
        value = strategist_plan.get(key)
        if value not in (None, "", [], {}):
            strategist_consumed_fields.append(key)

    commander_priority_ref = {
        "scanner_mission": str(commander_context.get("scanner_mission") or ""),
        "allowed_playbooks": list(commander_context.get("allowed_playbooks") or []),
        "banned_playbooks": list(commander_context.get("banned_playbooks") or []),
        "risk_mode": str(commander_context.get("risk_mode") or ""),
        "command_intent": str(commander_context.get("command_intent") or ""),
        "strategist_invocation": str(commander_context.get("strategist_invocation") or ""),
        "no_trade_reason_code": str(commander_context.get("no_trade_reason_code") or ""),
        "source_priority": list(commander_context.get("source_priority") or []),
    }
    strategist_constraints_ref = {
        "selected_playbook": str(strategist_plan.get("selected_playbook") or ""),
        "candidate_hypotheses": list(strategist_plan.get("candidate_hypotheses") or []),
        "symbol_constraints": dict(strategist_plan.get("symbol_constraints") or {}),
        "strategy_summary": str(strategist_plan.get("strategy_summary") or ""),
    }
    applied_policy = (
        dict(commander_context.get("applied_policy") or {})
        if isinstance(commander_context.get("applied_policy"), dict)
        else {}
    )
    normalized_scanner_bias_context, _scanner_bias_meta = facade.normalize_scanner_bias_context(
        scanner_bias_context or None,
        bias_source=str(commander_context.get("policy_source") or "strategist"),
    )
    scanner_bias_summary = facade.summarize_scanner_bias_context(normalized_scanner_bias_context)
    scanner_memory_bias_summary = facade.summarize_scanner_memory_bias(scanner_memory_bias)
    policy_source = str(
        commander_context.get("policy_source")
        or policy_provenance.get("applied_policy_source")
        or policy_provenance.get("monitor_entry_policy_source")
        or ""
    )
    monitor_entry_policy_summary = {
        key: applied_policy.get(key)
        for key in (
            "timeframe_minutes",
            "breakout_lookback",
            "volume_lookback",
            "volume_ratio_min",
            "pullback_min_pct",
            "pullback_max_pct",
            "max_extended_from_vwap_pct",
        )
        if key in applied_policy
    }
    ranking_factors = list(dict.fromkeys([str(x).strip() for x in list(scanner_priority or []) if str(x).strip()]))[:8]
    if scanner_bias:
        ranking_factors.append(f"bias:{scanner_bias}")
    if bool(scanner_bias_summary.get("enabled")):
        ranking_factors.append(f"scanner_bias:{scanner_bias_summary.get('summary')}")
    if bool(scanner_memory_bias_summary.get("enabled")):
        ranking_factors.append("memory_bias")
    if playbook:
        ranking_factors.append(f"playbook:{playbook}")
    if str(commander_context.get("scanner_mission") or "").strip():
        ranking_factors.append("commander_mission")
    if str(commander_context.get("risk_mode") or "").strip():
        ranking_factors.append(f"risk_mode:{str(commander_context.get('risk_mode') or '').strip()}")
    ranking_factors = list(dict.fromkeys(ranking_factors))[:10]

    summary_parts: List[str] = []
    if str(commander_context.get("scanner_mission") or "").strip():
        summary_parts.append(f"commander_mission={str(commander_context.get('scanner_mission') or '').strip()}")
    if str(strategist_plan.get("selected_playbook") or playbook).strip():
        summary_parts.append(f"playbook={str(strategist_plan.get('selected_playbook') or playbook).strip()}")
    if str(commander_context.get("risk_mode") or "").strip():
        summary_parts.append(f"risk_mode={str(commander_context.get('risk_mode') or '').strip()}")
    if str(commander_context.get("no_trade_reason_code") or "").strip():
        summary_parts.append(f"no_trade_reason={str(commander_context.get('no_trade_reason_code') or '').strip()}")
    if policy_source:
        summary_parts.append(f"policy_source={policy_source}")
    if bool(scanner_bias_summary.get("enabled")):
        summary_parts.append(f"scanner_bias={str(scanner_bias_summary.get('summary') or '')}")
    if bool(scanner_memory_bias_summary.get("enabled")):
        summary_parts.append("memory_bias=commander")

    return {
        "commander_context_consumed": commander_context_consumed,
        "consumed_fields": consumed_fields,
        "commander_priority_ref": commander_priority_ref,
        "strategist_constraints_ref": strategist_constraints_ref,
        "selection_basis": {
            "commander_context_consumed": commander_context_consumed,
            "strategist_plan_consumed": bool(strategist_consumed_fields),
            "consumed_fields": consumed_fields + strategist_consumed_fields,
            "scanner_bias_context": normalized_scanner_bias_context.to_dict(),
            "scanner_bias_summary": dict(scanner_bias_summary),
            "scanner_memory_bias_summary": dict(scanner_memory_bias_summary),
            "summary": " | ".join(summary_parts) if summary_parts else "base_quantitative_ranking",
        },
        "ranking_factors": ranking_factors,
        "playbook": str(strategist_plan.get("selected_playbook") or playbook or ""),
        "policy_source": policy_source,
        "applied_policy_present": bool(applied_policy),
        "monitor_entry_policy_summary": monitor_entry_policy_summary,
        "scanner_bias_context": normalized_scanner_bias_context.to_dict(),
        "scanner_bias_summary": dict(scanner_bias_summary),
        "scanner_memory_bias": dict(scanner_memory_bias or {}),
        "scanner_memory_bias_summary": dict(scanner_memory_bias_summary),
        "shadow_used": bool(
            commander_context.get("shadow_used")
            if commander_context.get("shadow_used") is not None
            else policy_provenance.get("shadow_used")
        ),
        "strategist_fallback_used": bool(
            commander_context.get("strategist_fallback_used")
            if commander_context.get("strategist_fallback_used") is not None
            else policy_provenance.get("strategist_fallback_used")
        ),
        "policy_provenance_ref": {
            "policy_source": policy_source,
            "applied_policy_present": bool(applied_policy),
            "monitor_entry_policy_summary": monitor_entry_policy_summary,
            "scanner_bias_summary": dict(scanner_bias_summary),
        },
    }
