"""Commander decision-event meta, portfolio guard/preflight summaries and pending-order cancel intent projection (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _commander_decision_event_meta_r3_impl(state, *, facade):
    commander_decision = state.get("commander_decision") if isinstance(state.get("commander_decision"), dict) else {}
    route_observability = facade.build_commander_route_observability_surface(
        selected_route=facade._derive_commander_selected_route(state),
        route_reason=str(
            commander_decision.get("decision_summary")
            or state.get("runtime_transition")
            or state.get("runtime_status")
            or ""
        ),
        commander_decision=commander_decision,
        runtime_fast_path=state.get("runtime_fast_path") if isinstance(state.get("runtime_fast_path"), dict) else {},
        resilience=state.get("runtime_resilience_state") if isinstance(state.get("runtime_resilience_state"), dict) else state.get("resilience"),
        runtime_status=state.get("runtime_status"),
        runtime_transition=state.get("runtime_transition"),
    )
    state["commander_route_observability"] = dict(route_observability)
    return {
        "shadow_used": bool(commander_decision.get("shadow_used")),
        "source_priority": list(commander_decision.get("source_priority") or []),
        "strategist_fallback_used": bool(commander_decision.get("strategist_fallback_used")),
        "applied_policy": dict(commander_decision.get("applied_policy") or {}),
        "policy_source": str(commander_decision.get("policy_source") or ""),
        "policy_validation_status": str(commander_decision.get("policy_validation_status") or ""),
        "policy_fallback_used": bool(commander_decision.get("policy_fallback_used")),
        "policy_fallback_reason": str(commander_decision.get("policy_fallback_reason") or ""),
        "override_reason": str(commander_decision.get("override_reason") or ""),
        "applied_policy_source_chain": list(commander_decision.get("applied_policy_source_chain") or []),
        "route_observability": dict(route_observability),
        "strategist_invocation_mode": str(commander_decision.get("strategist_invocation_mode") or ""),
        "strategy_selection_mode": str(commander_decision.get("strategy_selection_mode") or ""),
        "strategy_state": str(commander_decision.get("strategy_state") or ""),
        "route_selected": str(route_observability.get("route_selected") or ""),
        "route_reason": str(route_observability.get("route_reason") or ""),
        "strategist_call_decision": str(route_observability.get("strategist_call_decision") or ""),
        "strategist_call_reason": str(route_observability.get("strategist_call_reason") or ""),
        "strategist_skip_reason": str(route_observability.get("strategist_skip_reason") or ""),
        "policy_refresh_reason": str(route_observability.get("policy_refresh_reason") or ""),
        "cache_hit": bool(route_observability.get("cache_hit")),
        "cache_age_sec": route_observability.get("cache_age_sec"),
        "applied_policy_source": str(route_observability.get("applied_policy_source") or ""),
        "applied_policy_id": str(route_observability.get("applied_policy_id") or ""),
        "monitor_only_reason": str(route_observability.get("monitor_only_reason") or ""),
        "full_cycle_reason": str(route_observability.get("full_cycle_reason") or ""),
        "resilience_state": dict(route_observability.get("resilience_state") or {}),
        "intervention_reason": str(route_observability.get("intervention_reason") or ""),
        "strategy_generation_mode": str(route_observability.get("strategy_generation_mode") or ""),
        "commander_applied_policy_summary": dict(state.get("commander_applied_policy_summary") or {}),
        "policy_sources": dict(
            (
                (state.get("applied_policy") or {}).get("policy_sources")
                if isinstance((state.get("applied_policy") or {}).get("policy_sources"), dict)
                else {}
            )
        ),
        "llm_execution_profile_source": "commander_applied_policy",
    }


def _portfolio_guard_event_summary_r3_impl(state, *, facade):
    pg = state.get("portfolio_guard")
    if not isinstance(pg, dict):
        return {}
    return {
        "portfolio_guard": {
            "applied": bool(pg.get("applied")),
            "approved_total": facade._coerce_int(pg.get("approved_total"), 0),
            "blocked_total": facade._coerce_int(pg.get("blocked_total"), 0),
            "blocked_reason_counts": pg.get("blocked_reason_counts")
            if isinstance(pg.get("blocked_reason_counts"), dict)
            else {},
        }
    }


def _portfolio_preflight_event_summary_r3_impl(state, *, facade):
    pf = state.get("portfolio_preflight")
    if not isinstance(pf, dict):
        return {}
    return {
        "portfolio_preflight": {
            "applied": bool(pf.get("applied")),
            "blocked": bool(pf.get("blocked")),
            "degraded": bool(pf.get("degraded")),
            "reason": str(pf.get("reason") or ""),
            "phase": str(pf.get("phase") or ""),
            "closeout_fallback": pf.get("closeout_fallback") if isinstance(pf.get("closeout_fallback"), dict) else {},
        }
    }


def _portfolio_preflight_block_payload_r3_impl(state, *, facade):
    health = facade._extract_portfolio_snapshot_health(state)
    if not health:
        return {}

    reader_ok = bool(health.get("reader_ok"))
    mismatch = bool(health.get("positions_mismatch_detected"))
    reconciled = bool(health.get("reconciliation_applied"))

    reason = ""
    reason_human = ""
    if not reader_ok:
        reason = "portfolio_snapshot_reader_error"
        reason_human = "계좌 조회가 실패해서 전략 판단 전에 실행을 중단했습니다."
    elif mismatch and not reconciled:
        reason = "portfolio_snapshot_positions_mismatch_unresolved"
        reason_human = "계좌 보유 종목과 로컬 상태 불일치가 남아 있어서 전략 판단 전에 실행을 중단했습니다."
    if not reason:
        return {}

    return {
        "blocked": True,
        "reason": reason,
        "reason_human": reason_human,
        "reader_ok": reader_ok,
        "positions_source": str(health.get("positions_source") or ""),
        "reconciliation_status": str(health.get("reconciliation_status") or ""),
        "reader_positions_authoritative": bool(health.get("reader_positions_authoritative")),
        "positions_mismatch_detected": mismatch,
        "reconciliation_applied": reconciled,
        "reader_positions_count": facade._coerce_int(health.get("reader_positions_count"), 0),
        "persisted_positions_count": facade._coerce_int(health.get("persisted_positions_count"), 0),
    }


def _extract_portfolio_snapshot_health_r3_impl(state, *, facade):
    health = state.get("portfolio_snapshot_health")
    if isinstance(health, dict):
        return dict(health)
    snap = state.get("portfolio_snapshot")
    if isinstance(snap, dict) and isinstance(snap.get("_health"), dict):
        return dict(snap.get("_health") or {})
    return {}


def _order_row_side_r3_impl(row, *, facade):
    raw = str(row.get("side") or row.get("io_tp_nm") or row.get("trde_tp") or "").strip().upper()
    if raw in {"BUY", "B", "2"} or "BUY" in raw or "매수" in raw or "留ㅼ닔" in raw:
        return "BUY"
    if raw in {"SELL", "S", "1"} or "SELL" in raw or "매도" in raw or "留ㅻ룄" in raw:
        return "SELL"
    return raw


def _pending_buy_cancel_intents_from_account_orders_r3_impl(state, *, facade):
    try:
        from graphs.nodes.skill_contracts import (
            account_order_is_pending,
            account_order_quantity_snapshot,
            account_order_side,
            extract_account_orders_rows,
        )
    except Exception:
        return []

    rows, meta = extract_account_orders_rows(state)
    out: list[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if account_order_side(row) != "BUY" or not account_order_is_pending(row):
            continue
        symbol = facade._normalize_order_symbol(row.get("symbol") or row.get("stk_cd") or row.get("pdno") or row.get("code"))
        ord_no = str(row.get("ord_no") or row.get("odno") or row.get("ODNO") or "").strip()
        if not symbol or not ord_no:
            continue
        qty_snapshot = account_order_quantity_snapshot(row)
        order_qty = int(qty_snapshot.get("order_qty") or 0)
        filled_qty = int(qty_snapshot.get("filled_qty") or 0)
        remaining_qty_raw = qty_snapshot.get("remaining_qty")
        remaining_qty = facade._coerce_int(remaining_qty_raw, -1) if remaining_qty_raw is not None else -1
        status = str(row.get("status") or row.get("acpt_tp") or row.get("ord_st") or "").strip()
        terminal_cancel = any(token in status for token in ("취소", "거부", "거절", "CANCEL", "REJECT"))
        pending = True
        if terminal_cancel or not pending:
            continue
        out.append(
            {
                "action": "CANCEL",
                "symbol": symbol,
                "qty": 0,
                "order_type": "market",
                "order_api_id": "kt10003",
                "api_id": "kt10003",
                "stk_cd": symbol,
                "orig_ord_no": ord_no,
                "cncl_qty": "0",
                "dmst_stex_tp": str(row.get("dmst_stex_tp") or "KRX"),
                "rationale": "session_closeout_pending_buy_cancel",
                "meta": {
                    "source": "commander_session_closeout_guard",
                    "order_qty": int(order_qty),
                    "filled_qty": int(filled_qty),
                    "remaining_qty": int(remaining_qty) if remaining_qty >= 0 else None,
                    "status": status,
                    "account_orders_present": bool(meta.get("present")),
                },
            }
        )
    return out


def _strategist_shadow_fingerprint_r3_impl(output, *, facade):
    row = dict(output or {}) if isinstance(output, dict) else {}
    return {
        "market_regime": str(row.get("market_regime") or "").strip().lower(),
        "market_sentiment": str(row.get("market_sentiment") or "").strip().lower(),
        "playbook": str(row.get("playbook") or "").strip().lower(),
        "monitor_guidance": str(row.get("monitor_guidance") or "").strip().lower(),
        "risk_tone": str(row.get("risk_tone") or "").strip().lower(),
        "trade_aggressiveness": str(row.get("trade_aggressiveness") or "").strip().lower(),
        "themes": tuple(sorted(str(x or "").strip().lower() for x in list(row.get("themes") or []) if str(x or "").strip())),
        "avoid_themes": tuple(sorted(str(x or "").strip().lower() for x in list(row.get("avoid_themes") or []) if str(x or "").strip())),
        "global_sentiment_score": round(float(row.get("global_sentiment_score") or 0.0), 4) if row.get("global_sentiment_score") not in (None, "") else None,
    }


def _shadow_float_r3_impl(value, *, facade):
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None


def _shadow_selected_score_r3_impl(state, *, facade):
    selected = state.get("selected") if isinstance(state.get("selected"), dict) else {}
    for key in ("score_total", "score", "confidence"):
        value = facade._shadow_float(selected.get(key))
        if value is not None:
            return value
    return None


def _seed_commander_shadow_prior_context_r3_impl(state, *, prior_cached_output, facade):
    shadow_runtime = facade._ensure_commander_shadow_runtime(state)
    strategist_llm = state.get("strategist_llm") if isinstance(state.get("strategist_llm"), dict) else {}
    baseline_output = (
        dict(prior_cached_output)
        if isinstance(prior_cached_output, dict) and prior_cached_output
        else dict(state.get("strategist_output") or {}) if isinstance(state.get("strategist_output"), dict) else {}
    )
    baseline_global_signal = baseline_output.get("global_signal") if isinstance(baseline_output.get("global_signal"), dict) else {}
    baseline_fear_index = baseline_global_signal.get("fear_index") if isinstance(baseline_global_signal.get("fear_index"), dict) else {}
    baseline_overlay = baseline_output.get("macro_stress_overlay") if isinstance(baseline_output.get("macro_stress_overlay"), dict) else {}
    shadow_runtime["prior_context"] = {
        "selected_symbol": facade._shadow_selected_symbol(state),
        "selected_score_total": facade._shadow_selected_score(state),
        "playbook": facade._shadow_text(baseline_output.get("playbook"), max_len=40),
        "market_regime": facade._shadow_text(baseline_output.get("market_regime"), max_len=40),
        "market_sentiment": facade._shadow_text(baseline_output.get("market_sentiment"), max_len=40),
        "global_sentiment_score": baseline_output.get("global_sentiment_score"),
        "vix_level": baseline_fear_index.get("level") if baseline_fear_index.get("level") not in (None, "") else baseline_overlay.get("vix_level"),
        "stress_flags": [str(x or "").strip() for x in list(baseline_overlay.get("stress_flags") or []) if str(x or "").strip()][:8],
        "llm_status": facade._shadow_text(strategist_llm.get("status") or strategist_llm.get("llm_status"), max_len=40),
        "monitor_entry_policy_summary": facade._summarize_monitor_entry_policy_from_strategist_output(baseline_output),
    }
    state["commander_shadow_runtime"] = shadow_runtime
