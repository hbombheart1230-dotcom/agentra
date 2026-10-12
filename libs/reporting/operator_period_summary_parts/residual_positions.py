"""Operator summary residual-position payload and overnight context (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _build_residual_positions_payload_r3_impl(*, reports_root, day, facade):
    state, state_path = facade._load_state_snapshot(reports_root)
    if not state:
        return {
            "available": False,
            "source": "state_snapshot",
            "source_path": "",
            "position_count": 0,
            "positions": [],
        }

    raw_positions = state.get("mock_positions") if isinstance(state.get("mock_positions"), list) else []
    overnight = (
        state.get("overnight_decision_by_symbol")
        if isinstance(state.get("overnight_decision_by_symbol"), dict)
        else {}
    )
    closeout = state.get("closeout_backup_liquidation") if isinstance(state.get("closeout_backup_liquidation"), dict) else {}
    monitor_states = (
        state.get("monitor_last_state_by_symbol")
        if isinstance(state.get("monitor_last_state_by_symbol"), dict)
        else {}
    )
    account_snapshot_reconciliation = facade._account_snapshot_closeout_reconciliation(reports_root, day)
    account_snapshot_positions = {
        str(item or "").strip().upper()
        for item in list(account_snapshot_reconciliation.get("position_symbols") or [])
        if str(item or "").strip()
    }
    account_snapshot_fresh = bool(account_snapshot_reconciliation.get("fresh_after_closeout_window"))
    positions: List[Dict[str, Any]] = []
    reconciled_closed: List[Dict[str, Any]] = []
    for raw_row in raw_positions:
        if not isinstance(raw_row, dict):
            continue
        symbol = str(raw_row.get("symbol") or "").strip().upper()
        qty = facade._safe_int(raw_row.get("qty"))
        if not symbol or qty <= 0:
            continue
        if account_snapshot_fresh and symbol not in account_snapshot_positions:
            reconciled_closed.append(
                {
                    "symbol": symbol,
                    "trade_id": "",
                    "lifecycle_bundle_path": "",
                    "reason": "fresh_account_snapshot_position_absent_after_closeout",
                    "exit_reason": "latest Kiwoom account snapshot has no remaining position after 15:20 closeout window",
                    "exit_ts": str(account_snapshot_reconciliation.get("generated_at_kst") or ""),
                    "exit_qty": qty,
                    "source_path": str(account_snapshot_reconciliation.get("snapshot_path") or ""),
                }
            )
            continue
        sell_guard_reconciliation = facade._same_day_sell_guard_reconciliation(
            reports_root=reports_root,
            state_path=state_path,
            day=day,
            symbol=symbol,
            qty=qty,
        )
        if sell_guard_reconciliation:
            reconciled_closed.append(sell_guard_reconciliation)
            continue
        decision = overnight.get(symbol) if isinstance(overnight.get(symbol), dict) else {}
        action = str(decision.get("action") or "").strip()
        if action in facade._FLATTEN_BEFORE_CLOSE_ACTIONS:
            reconciliation = facade._same_day_flatten_reconciliation(
                reports_root=reports_root,
                day=day,
                symbol=symbol,
                qty=qty,
                avg_price=raw_row.get("avg_price"),
            )
            if reconciliation:
                reconciled_closed.append(reconciliation)
                continue
        weekend_carry = facade._decision_is_weekend_carry(decision)
        reason = str(decision.get("reason") or "").strip()
        if not reason and not decision:
            reason = "오버나이트 판단 기록 없음"
        row = {
            "symbol": symbol,
            "qty": qty,
            "avg_price": facade._safe_float(raw_row.get("avg_price")),
            "current_price": facade._safe_float(raw_row.get("current_price")),
            "unrealized_pnl": facade._safe_float(raw_row.get("unrealized_pnl")),
            "account_pnl_ratio": facade._safe_float(raw_row.get("account_pnl_ratio")),
            "status": facade._residual_position_status(raw_row, decision, closeout),
            "overnight_action": action,
            "overnight_reason": reason,
            "overnight_decision_missing": not bool(decision),
            "weekend_carry": bool(weekend_carry),
            "allow_weekend_carry": bool(decision.get("allow_weekend_carry")),
            "holding_gap_days": facade._safe_int(decision.get("holding_gap_days"), default=3 if weekend_carry else 1),
            "overnight_minutes_to_close": facade._safe_float(decision.get("minutes_to_close")),
            "overnight_positive_signals": [
                str(item)
                for item in list(decision.get("positive_signals") or [])
                if str(item or "").strip()
            ],
            "overnight_blockers": [
                str(item)
                for item in list(decision.get("blockers") or [])
                if str(item or "").strip()
            ],
        }
        if not decision:
            monitor_state = monitor_states.get(symbol) if isinstance(monitor_states.get(symbol), dict) else {}
            row.update(facade._overnight_missing_context(raw_row, monitor_state))
        else:
            row.update(facade._overnight_recorded_context(decision))
        positions.append(row)

    reconciled_symbols = {str(row.get("symbol") or "").strip().upper() for row in reconciled_closed}
    carry_forward_symbols = [
        item
        for item in list(closeout.get("carry_forward_symbols") or [])
        if str(item or "").strip().upper() not in reconciled_symbols
    ]
    closeout_meta = facade._closeout_state_metadata(closeout, day)
    unresolved_symbols = [
        row["symbol"]
        for row in positions
        if isinstance(row, dict) and str(row.get("symbol") or "").strip()
    ]
    closeout_operational_risk = {
        "severity": "critical" if unresolved_symbols else "ok",
        "reason": (
            "broker_truth_unclosed_positions_after_closeout"
            if unresolved_symbols and account_snapshot_fresh
            else "state_unclosed_positions_after_closeout"
            if unresolved_symbols
            else ""
        ),
        "unresolved_symbols": list(unresolved_symbols),
        "requires_next_open_flatten": bool(unresolved_symbols),
        "operator_action": (
            "next_open_market_flatten_required"
            if unresolved_symbols
            else ""
        ),
    }

    return {
        "available": True,
        "source": "state_snapshot",
        "source_path": state_path,
        "position_count": len(positions),
        "positions": positions,
        "reconciled_closed_positions": reconciled_closed,
        "account_snapshot_reconciliation": account_snapshot_reconciliation,
        "closeout_operational_risk": closeout_operational_risk,
        "closeout_state": {
            "mode": str(closeout.get("mode") or ""),
            "reason": str(closeout.get("reason") or ""),
            "applied_at": str(closeout.get("applied_at") or ""),
            **closeout_meta,
            "carry_forward_symbols": carry_forward_symbols,
            "flattened_symbols": list(closeout.get("flattened_symbols") or []),
            "unresolved_flatten_symbols": list(closeout.get("unresolved_flatten_symbols") or []),
        },
    }


def _residual_position_status_r3_impl(row, decision, closeout, *, facade):
    symbol = str(row.get("symbol") or "").strip().upper()
    action = str(decision.get("action") or "").strip()
    if bool(decision.get("approved")) and action == "carry_overnight":
        if facade._decision_is_weekend_carry(decision):
            return "주말 오버나이트 승인(주의)"
        return "오버나이트 승인"
    if action == "flatten_before_close":
        return "장마감 정리 지시"
    unresolved = {str(x or "").strip().upper() for x in list(closeout.get("unresolved_flatten_symbols") or [])}
    flattened = {str(x or "").strip().upper() for x in list(closeout.get("flattened_symbols") or [])}
    if symbol in unresolved:
        return "정리 필요"
    if symbol in flattened:
        return "정리 불일치"
    return "잔여 보유"


def _snapshot_position_symbols_r3_impl(snapshot, *, facade):
    symbols: set[str] = set()
    for call in list(snapshot.get("calls") or []):
        if not isinstance(call, dict):
            continue
        api_id = str(call.get("api_id") or "").strip()
        payload = call.get("payload") if isinstance(call.get("payload"), dict) else {}
        rows: List[Any] = []
        if api_id == "kt00018":
            rows = list(payload.get("acnt_evlt_remn_indv_tot") or [])
        elif api_id == "kt00004":
            rows = list(payload.get("stk_acnt_evlt_prst") or [])
        else:
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            symbol = facade._normalize_symbol_code(row.get("stk_cd"))
            qty = facade._safe_int(row.get("rmnd_qty"))
            if symbol and qty > 0:
                symbols.add(symbol)
    return symbols


def _overnight_missing_context_r3_impl(raw_row, monitor_state, *, facade):
    position_entry_text = facade._epoch_to_kst_text(raw_row.get("position_entry_epoch"))
    if not isinstance(monitor_state, dict) or not monitor_state:
        out: Dict[str, Any] = {
            "overnight_missing_reason_code": "no_monitor_state_for_residual_position",
            "overnight_missing_detail": "모니터 상태 기록 없음; EOD 전체 보유 종목 재점검 필요",
            "overnight_decision_status": "missing",
            "overnight_decision_label": "미수행(모니터 상태 기록 없음)",
        }
        if position_entry_text:
            out["position_entry_at_kst"] = position_entry_text
        return out

    updated_epoch = facade._safe_int(monitor_state.get("updated_at_epoch"))
    updated_text = facade._epoch_to_kst_text(updated_epoch)
    posture = str(monitor_state.get("posture") or "").strip()
    monitor_reason = str(monitor_state.get("reason") or "").strip()
    entry_state = monitor_state.get("entry_state") if isinstance(monitor_state.get("entry_state"), dict) else {}
    blocking_axis = str(entry_state.get("current_blocking_axis") or "").strip()
    detail_parts: List[str] = []
    if updated_text:
        detail_parts.append(f"마지막 모니터 {updated_text}")
    if posture or monitor_reason:
        detail_parts.append(f"마지막 판단 {posture or '-'}({monitor_reason or '-'})")
    if blocking_axis:
        detail_parts.append(f"차단축 {blocking_axis}")

    reason_code = "no_persisted_overnight_decision"
    decision_label = "미확인(오버나이트 판단 저장 기록 없음)"
    if updated_epoch > 0:
        try:
            kst = facade.timezone(facade.timedelta(hours=9))
            updated_dt = facade.datetime.fromtimestamp(updated_epoch, tz=facade.timezone.utc).astimezone(kst)
            eod_window_start = updated_dt.replace(hour=15, minute=20, second=0, microsecond=0)
            market_close = updated_dt.replace(hour=15, minute=30, second=0, microsecond=0)
            if updated_dt < eod_window_start:
                reason_code = "last_monitor_before_eod_window_no_later_review"
                decision_label = "미수행(15:20 이후 재점검 없음)"
                detail_parts.append("EOD 판단창(15:20 이후) 재점검 없음")
            elif updated_dt <= market_close:
                reason_code = "last_monitor_inside_eod_window_without_persisted_decision"
                decision_label = "기록 누락 가능(EOD 판단창 내 저장 없음)"
                detail_parts.append("EOD 판단창 내 평가 기록 저장 누락 가능")
            else:
                reason_code = "last_monitor_after_market_close_without_persisted_decision"
                decision_label = "기록 누락 가능(장마감 후 저장 없음)"
                detail_parts.append("장마감 후 평가 기록 저장 누락 가능")
        except Exception:
            pass

    out = {
        "overnight_missing_reason_code": reason_code,
        "overnight_missing_detail": " / ".join(detail_parts) if detail_parts else "오버나이트 판단 저장 기록 없음",
        "overnight_decision_status": "missing",
        "overnight_decision_label": decision_label,
        "last_monitor_updated_at_epoch": updated_epoch if updated_epoch > 0 else None,
        "last_monitor_updated_at_kst": updated_text,
        "last_monitor_posture": posture,
        "last_monitor_reason": monitor_reason,
        "last_monitor_blocking_axis": blocking_axis,
    }
    if position_entry_text:
        out["position_entry_at_kst"] = position_entry_text
    return out


def _overnight_recorded_context_r3_impl(decision, *, facade):
    action = str(decision.get("action") or "").strip()
    approved = bool(decision.get("approved"))
    if approved and action == "carry_overnight":
        status = "approved"
        label = "수행됨(오버나이트 승인)"
    elif action in facade._FLATTEN_BEFORE_CLOSE_ACTIONS:
        status = "flatten_requested"
        label = "수행됨(장마감 전 정리 지시)"
    elif action:
        status = "recorded"
        label = f"수행됨({action})"
    else:
        status = "recorded"
        label = "수행됨(결정 기록 있음)"
    return {
        "overnight_decision_status": status,
        "overnight_decision_label": label,
    }
