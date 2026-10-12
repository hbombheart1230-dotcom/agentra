"""Behavior-preserving R3 implementation bodies moved from the public facade.

Each function keeps its original body except that every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module, no getattr fallback,
no entry-time capture), so late/use-time lookup and monkeypatching match the original
module-level resolution. Owner never imports the facade.
"""
from __future__ import annotations


def _has_noisy_trade_report_text_r3_impl(value, *, facade):
    raw = str(value or "").strip().lower()
    if not raw:
        return False
    noisy_tokens = (
        "cached_strategist",
        "policy_validation_status",
        "fallback_invalid",
        "strategist invocation",
        "headlines were considered",
        "market regime",
        "scanner selected ",
        "source mix:",
        "chart feature coverage",
        "trading value",
        "theme and sector alignment",
        "confidence:",
        "risk_score",
        "timeframe ",
        "breakout lookback",
        "volume lookback",
        "volume_ratio_min",
        "min_extended_from_vwap_pct",
        "max_extended_from_vwap_pct",
    )
    return any(token in raw for token in noisy_tokens)


def _build_scanner_filters_summary_r3_impl(filters_human, *, facade):
    checks = [row for row in list(filters_human.get("checks") or []) if isinstance(row, dict)]
    feature_coverage = filters_human.get("feature_coverage") if isinstance(filters_human.get("feature_coverage"), dict) else {}
    if not checks:
        return facade._clip(filters_human.get("summary"), max_len=600) or "스캐너 후보 비교 근거는 저장된 범위 안에서 제한적으로 확인됩니다."
    pass_count = sum(1 for row in checks if str(row.get("status") or "").strip().upper() == "PASS")
    fail_count = sum(1 for row in checks if str(row.get("status") or "").strip().upper() == "FAIL")
    na_count = sum(1 for row in checks if str(row.get("status") or "").strip().upper() == "NOT_AVAILABLE")
    present = int(float(feature_coverage.get("present") or 0)) if facade._num_opt(feature_coverage.get("present")) is not None else 0
    total = int(float(feature_coverage.get("total") or 0)) if facade._num_opt(feature_coverage.get("total")) is not None else 0
    quality_raw = facade._clip(feature_coverage.get("quality"), max_len=40).strip().lower()
    quality = {
        "strong": "양호",
        "good": "양호",
        "moderate": "보통",
        "weak": "취약",
    }.get(quality_raw, facade._clip(feature_coverage.get("quality"), max_len=40) or "not_captured")

    summary = f"스캐너 후보 비교에서는 {len(checks)}개 체크 중 통과 {pass_count}개, 미통과 {fail_count}개, 확인 불가 {na_count}개였습니다."
    if present and total:
        summary += f" 차트 피처 커버리지는 {present}/{total}로 {quality} 수준이었습니다."
    return summary


def _looks_like_post_entry_monitor_snapshot_r3_impl(story_input, monitor_reason, *, facade):
    grouped_trace = facade._as_dict(monitor_reason.get("entry_grouped_logic_trace"))
    entry_scores = facade._as_dict(monitor_reason.get("entry_condition_scores"))
    has_entry_gate_snapshot = bool(
        grouped_trace
        or entry_scores
        or monitor_reason.get("entry_condition_path") not in (None, "")
    )
    if not has_entry_gate_snapshot:
        return False

    status_text = facade._clip(
        story_input.get("status")
        or story_input.get("lifecycle_status")
        or facade._as_dict(story_input.get("shared_facts")).get("status"),
        max_len=40,
    ).lower()
    action_text = facade._clip(
        story_input.get("action")
        or facade._as_dict(story_input.get("shared_facts")).get("action"),
        max_len=40,
    ).upper()
    posture = facade._clip(monitor_reason.get("posture"), max_len=40).upper()
    has_exit_axis = any(
        monitor_reason.get(key) not in (None, "", [], {})
        for key in (
            "active_exit_axis",
            "exit_triggered",
            "position_age_seconds",
            "trigger_type",
            "peak_drawdown",
            "current_drawdown",
            "effective_stop_loss_pct",
            "watch_axes",
        )
    )
    return bool(has_exit_axis and (status_text == "closed" or action_text == "SELL" or posture in {"SELL", "HOLD"}))


def _build_exit_decision_summary_r3_impl(exit_summary, monitor_context, *, status_text, facade):
    reason = facade._clip(exit_summary.get("reason_human"), max_len=600)
    reason_label = facade._exit_reason_label(reason)
    if status_text.lower() == "open":
        return reason_label or "현재 포지션은 아직 열려 있어 확정된 청산 체결은 기록되지 않았습니다."
    if reason or reason_label:
        price = facade._fmt_price(monitor_context.get("current_price"))
        avg_price = facade._fmt_price(monitor_context.get("average_price"))
        drawdown = facade._fmt_pct(monitor_context.get("current_drawdown"))
        axis = facade._operator_axis_label(facade._clip(monitor_context.get("active_exit_axis"), max_len=64))
        confirm_required = monitor_context.get("confirm_required")
        confirm_count = monitor_context.get("confirm_count")
        details: List[str] = []
        if axis:
            details.append(f"핵심 청산 축은 {axis}")
        if confirm_required is not None:
            details.append(f"확인 조건은 {int(confirm_count or 0)}/{int(confirm_required or 0)}")
        if price != "-" and avg_price != "-":
            details.append(f"현재가는 {price}, 평균가는 {avg_price}")
        if drawdown != "-":
            details.append(f"현재 손익 변동은 {drawdown}")
        if details:
            return f"{reason_label or reason}. 청산 당시 상황은 " + ", ".join(details) + "입니다."
        return reason_label or reason
    return "청산 판단 근거는 저장된 데이터 범위 안에서 충분히 확인되지 않았습니다."


def _compact_entry_or_exit_summary_r3_impl(summary, *, facade):
    data = summary if isinstance(summary, dict) else {}
    strategist_ctx = data.get("strategist_context") if isinstance(data.get("strategist_context"), dict) else {}
    scanner_ctx = data.get("scanner_context") if isinstance(data.get("scanner_context"), dict) else {}
    monitor_ctx = data.get("monitor_context") if isinstance(data.get("monitor_context"), dict) else {}
    guard_ctx = data.get("guard_context") if isinstance(data.get("guard_context"), dict) else {}
    execution_ctx = data.get("execution_context") if isinstance(data.get("execution_context"), dict) else {}
    return {
        "run_id": facade._clip(data.get("run_id"), max_len=40),
        "ts": facade._clip(data.get("ts"), max_len=40),
        "action": facade._clip(data.get("action"), max_len=24),
        "reason_human": facade._clip(data.get("reason_human"), max_len=280),
        "strategist_context": {
            "market_regime": facade._clip(strategist_ctx.get("market_regime"), max_len=32),
            "market_sentiment": facade._clip(strategist_ctx.get("market_sentiment"), max_len=32),
            "playbook": facade._clip(strategist_ctx.get("playbook"), max_len=40),
            "themes": facade._listify(strategist_ctx.get("themes"), max_items=4, max_len=80),
            "global_sentiment_score": strategist_ctx.get("global_sentiment_score"),
            "vix_level": strategist_ctx.get("vix_level"),
            "headline_count": strategist_ctx.get("headline_count"),
            "news_query_targets": facade._listify(strategist_ctx.get("news_query_targets"), max_items=5, max_len=80),
            "stress_flags": facade._listify(strategist_ctx.get("stress_flags"), max_items=4, max_len=80),
        },
        "scanner_context": {
            "selected_symbol": facade._clip(scanner_ctx.get("selected_symbol"), max_len=24),
            "selected_rank": scanner_ctx.get("selected_rank"),
            "universe_size": scanner_ctx.get("universe_size"),
            "score_total": scanner_ctx.get("score_total"),
            "confidence": scanner_ctx.get("confidence"),
            "top_candidates": facade._compact_named_rows(scanner_ctx.get("top_candidates"), max_items=3),
            "selection_reason": facade._clip(scanner_ctx.get("selection_reason"), max_len=220),
        },
        "monitor_context": facade._compact_monitor_snapshot(monitor_ctx),
        "guard_context": {
            "status": facade._clip(guard_ctx.get("status") or guard_ctx.get("verdict"), max_len=32),
            "summary": facade._clip(guard_ctx.get("summary") or guard_ctx.get("reason"), max_len=220),
        },
        "execution_context": {
            "status": facade._clip(execution_ctx.get("status"), max_len=32),
            "summary": facade._clip(execution_ctx.get("summary") or execution_ctx.get("message"), max_len=220),
            "qty": execution_ctx.get("qty"),
            "price": execution_ctx.get("price"),
        },
    }


def _extract_policy_ref_context_r3_impl(story_input, monitor_reason, *, facade):
    candidates: List[Dict[str, Any]] = []
    if isinstance(monitor_reason.get("policy_ref"), dict):
        candidates.append(monitor_reason.get("policy_ref"))
    for key in ("entry_summary", "exit_summary"):
        block = story_input.get(key) if isinstance(story_input.get(key), dict) else {}
        monitor_ctx = block.get("monitor_context") if isinstance(block.get("monitor_context"), dict) else {}
        policy_ref = monitor_ctx.get("policy_ref") if isinstance(monitor_ctx.get("policy_ref"), dict) else {}
        if policy_ref:
            candidates.append(policy_ref)
    holding = story_input.get("holding_summary") if isinstance(story_input.get("holding_summary"), dict) else {}
    for row in list(holding.get("holding_events") or [])[:8]:
        if not isinstance(row, dict):
            continue
        monitor_ctx = row.get("monitor_context") if isinstance(row.get("monitor_context"), dict) else {}
        policy_ref = monitor_ctx.get("policy_ref") if isinstance(monitor_ctx.get("policy_ref"), dict) else {}
        if policy_ref:
            candidates.append(policy_ref)
    for policy_ref in candidates:
        symbol_constraints = policy_ref.get("symbol_constraints") if isinstance(policy_ref.get("symbol_constraints"), dict) else {}
        risk_mode = facade._clip(policy_ref.get("risk_mode"), max_len=40)
        selected_playbook = facade._clip(policy_ref.get("selected_playbook"), max_len=40)
        preferred_themes = facade._listify(symbol_constraints.get("preferred_themes"), max_items=6, max_len=80)
        avoid_themes = facade._listify(symbol_constraints.get("avoid_themes"), max_items=6, max_len=80)
        if risk_mode or selected_playbook or preferred_themes or avoid_themes:
            return {
                "risk_mode": risk_mode,
                "selected_playbook": selected_playbook,
                "preferred_themes": preferred_themes,
                "avoid_themes": avoid_themes,
            }
    return {}


def _extract_scanner_bias_summary_r3_impl(story_input, scanner_reason, *, facade):
    candidates: List[Dict[str, Any]] = []
    if isinstance(scanner_reason.get("scanner_bias_summary"), dict) and scanner_reason.get("scanner_bias_summary"):
        candidates.append(scanner_reason.get("scanner_bias_summary"))
    scanner_trace_summary = story_input.get("scanner_trace_summary") if isinstance(story_input.get("scanner_trace_summary"), dict) else {}
    if isinstance(scanner_trace_summary.get("scanner_bias_summary"), dict) and scanner_trace_summary.get("scanner_bias_summary"):
        candidates.append(scanner_trace_summary.get("scanner_bias_summary"))
    canonical_artifacts = story_input.get("canonical_agent_artifacts") if isinstance(story_input.get("canonical_agent_artifacts"), dict) else {}
    canonical_scanner = canonical_artifacts.get("scanner") if isinstance(canonical_artifacts.get("scanner"), dict) else {}
    if isinstance(canonical_scanner.get("scanner_bias_summary"), dict) and canonical_scanner.get("scanner_bias_summary"):
        candidates.append(canonical_scanner.get("scanner_bias_summary"))
    scanner_evidence = story_input.get("scanner_evidence") if isinstance(story_input.get("scanner_evidence"), dict) else {}
    for row in list(scanner_evidence.get("candidate_selection_reasons") or [])[:3]:
        if not isinstance(row, dict):
            continue
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        if isinstance(payload.get("scanner_bias_summary"), dict) and payload.get("scanner_bias_summary"):
            candidates.append(payload.get("scanner_bias_summary"))
    for item in candidates:
        if item:
            return {
                "enabled": item.get("enabled"),
                "active_biases": facade._listify(item.get("active_biases"), max_items=6, max_len=80),
                "bias_strength": facade._clip(item.get("bias_strength"), max_len=24),
                "bias_source": facade._clip(item.get("bias_source"), max_len=80),
                "summary": facade._clip(item.get("summary"), max_len=220),
            }
    return {}
