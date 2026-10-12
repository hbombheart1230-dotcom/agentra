"""Operator summary closeout, sell-guard and broker day-trade diary reconciliation (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _account_snapshot_closeout_reconciliation_r3_impl(reports_root, day, *, facade):
    normalized_day = str(day or "").strip()[:10]
    path = facade._latest_account_snapshot_path(reports_root, normalized_day)
    snapshot = facade._read_json(path)
    if not isinstance(snapshot, dict):
        return {"available": False, "reason": "account_snapshot_missing", "path": str(path)}
    generated_at = str(snapshot.get("generated_at") or "").strip()
    generated_dt = facade._iso_to_kst_dt(generated_at)
    generated_day = generated_dt.strftime("%Y-%m-%d") if generated_dt is not None else ""
    after_closeout_window = False
    if generated_dt is not None:
        closeout_start = generated_dt.replace(hour=15, minute=20, second=0, microsecond=0)
        after_closeout_window = bool(generated_dt >= closeout_start)
    summary = snapshot.get("summary") if isinstance(snapshot.get("summary"), dict) else {}
    ok_count = facade._safe_int(summary.get("ok_count"))
    error_count = facade._safe_int(summary.get("error_count"))
    api_call_count = facade._safe_int(summary.get("api_call_count"))
    positions = facade._snapshot_position_symbols(snapshot)
    fresh = bool(
        normalized_day
        and generated_day == normalized_day
        and after_closeout_window
        and api_call_count > 0
        and ok_count > 0
    )
    return {
        "available": True,
        "fresh_after_closeout_window": fresh,
        "path": str(path),
        "snapshot_path": str(snapshot.get("path") or path),
        "generated_at": generated_at,
        "generated_at_kst": generated_dt.strftime("%Y-%m-%d %H:%M:%S KST") if generated_dt is not None else "",
        "generated_day_kst": generated_day,
        "after_closeout_window": after_closeout_window,
        "api_call_count": api_call_count,
        "ok_count": ok_count,
        "error_count": error_count,
        "position_symbols": sorted(positions),
        "position_count": len(positions),
    }


def _same_day_sell_guard_reconciliation_r3_impl(*, reports_root, state_path, day, symbol, qty, facade):
    normalized_day = str(day or "").strip()
    normalized_symbol = str(symbol or "").strip().upper()
    if not normalized_day or not normalized_symbol or qty <= 0:
        return {}
    for path in facade._sell_guard_candidate_paths(reports_root=reports_root, state_path=state_path):
        payload = facade._read_json(path)
        if not isinstance(payload, dict):
            continue
        orders = payload.get("orders") if isinstance(payload.get("orders"), dict) else {}
        row = orders.get(normalized_symbol) if isinstance(orders.get(normalized_symbol), dict) else {}
        if not row:
            continue
        if facade._epoch_day_kst(row.get("last_sell_epoch")) != normalized_day:
            continue
        remaining_hint = facade._safe_int(row.get("remaining_qty_hint"), default=-1)
        last_sell_qty = facade._safe_int(row.get("last_sell_qty"))
        position_qty_hint = facade._safe_int(row.get("position_qty_hint"))
        if remaining_hint == 0 and max(last_sell_qty, position_qty_hint) >= qty:
            return {
                "symbol": normalized_symbol,
                "trade_id": str(row.get("run_id") or ""),
                "lifecycle_bundle_path": "",
                "reason": "same_day_sell_guard_remaining_zero",
                "exit_reason": "recent sell guard reports remaining_qty_hint=0",
                "exit_ts": facade._epoch_to_kst_text(row.get("last_sell_epoch")),
                "exit_qty": last_sell_qty,
                "source_path": str(path),
            }
    return {}


def _closeout_state_metadata_r3_impl(closeout, day, *, facade):
    applied_at = str(closeout.get("applied_at") or "").strip()
    applied_raw = closeout.get("applied")
    applied_known = isinstance(applied_raw, bool)
    applied = bool(applied_raw) if applied_known else False
    applied_at_kst = facade._iso_to_kst_text(applied_at)
    applied_day = ""
    dt = facade._iso_to_kst_dt(applied_at)
    if dt is not None:
        applied_day = dt.strftime("%Y-%m-%d")
    normalized_day = str(day or "").strip()
    stale = bool(normalized_day and applied_day and applied_day != normalized_day)

    note_parts: List[str] = []
    if applied_at_kst:
        if applied_known:
            note_parts.append("적용" if applied else "미적용")
        note_parts.append(f"기록시각 {applied_at_kst}")
    if stale:
        note_parts.append(f"당일({normalized_day}) 오버나이트 판단 근거 아님")
    return {
        "applied": applied,
        "applied_at_kst": applied_at_kst,
        "applied_day_kst": applied_day,
        "stale_for_day": stale,
        "report_note": "; ".join(note_parts),
    }


def _snapshot_day_trade_diary_rows_r3_impl(snapshot, *, facade):
    payload = facade._first_snapshot_call_payload(snapshot, "ka10170")
    rows = payload.get("tdy_trde_diary") if isinstance(payload.get("tdy_trde_diary"), list) else []
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        symbol = facade._normalize_symbol_code(row.get("stk_cd") or row.get("stk_cd_1"))
        if not symbol:
            continue
        out.append(
            {
                "symbol": symbol,
                "symbol_name": str(row.get("stk_nm") or "").strip(),
                "buy_qty": facade._safe_int(row.get("buy_qty")),
                "sell_qty": facade._safe_int(row.get("sell_qty")),
                "buy_avg_price": facade._safe_float(row.get("buy_avg_pric") or row.get("buy_avg_price")),
                "sell_avg_price": facade._safe_float(row.get("sel_avg_pric") or row.get("sell_avg_price")),
                "realized_pnl": facade._safe_float(row.get("pl_amt") or row.get("realized_pnl")),
                "pnl_ratio": facade._safe_float(row.get("prft_rt") or row.get("pnl_ratio")),
                "fee_tax": facade._safe_int(row.get("cmsn_alm_tax") or row.get("fee_tax")),
                "source": "kiwoom.ka10170",
            }
        )
    return out


def _broker_day_trade_diary_truth_metrics_r3_impl(row, reports_root, *, facade):
    day = str(row.get("date") or row.get("day") or "").strip()[:10]
    symbol = facade._normalize_symbol_code(row.get("symbol"))
    if not day or not symbol:
        return {}
    snapshot = facade._latest_account_snapshot(reports_root, day)
    if not snapshot:
        return {}
    rows = facade._snapshot_day_trade_diary_rows(snapshot)
    if not rows:
        return {}
    hints = facade._entry_truth_hints(row, reports_root)
    match = facade.match_trade_diary_row(
        rows,
        symbol=symbol,
        filled_qty=hints.get("qty"),
        buy_price=hints.get("buy_price"),
    )
    if not match or not bool(match.get("authoritative")):
        return {}
    if facade._safe_int(match.get("filled_qty")) <= 0:
        return {}
    pnl_pct = facade._safe_float(match.get("pnl_ratio"))
    return {
        "truth_surface_available": True,
        "truth_surface_path": str(facade._latest_account_snapshot_path(reports_root, day)),
        "truth_result_label": "profit" if (facade._safe_float(match.get("realized_pnl")) or 0.0) > 0 else "loss" if (facade._safe_float(match.get("realized_pnl")) or 0.0) < 0 else "flat",
        "truth_source": str(match.get("source") or "kiwoom.ka10170"),
        "truth_net_pnl": facade._safe_float(match.get("realized_pnl")),
        "truth_net_return_pct": pnl_pct,
        "truth_observed_return_pct": None,
        "truth_price_move_pct": None,
        "truth_cost_drag_pct": None,
        "truth_breakeven_move_pct": None,
        "broker_day_match_mode": str(match.get("match_mode") or ""),
        "broker_day_authoritative": True,
        "broker_day_reconciled_status": "closed",
    }
