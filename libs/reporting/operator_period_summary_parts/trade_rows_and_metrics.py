"""Operator summary daily trade index rows, symbol rows, trade metrics and truth-surface enrichment (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _daily_trade_index_rows_r3_impl(*, reports_root, trade_index, facade):
    rows: List[Dict[str, Any]] = []
    for item in trade_index:
        if not isinstance(item, dict):
            continue
        row = dict(item)
        trade_dir = facade._trade_dir_for_row(row, reports_root)
        if trade_dir is not None:
            summary_input = facade._read_json(trade_dir / "reports" / "ai_trade_summary_input.json")
            summary_report = facade._read_json(trade_dir / "reports" / "ai_trade_summary.json")
            full_report = facade._read_json(trade_dir / "reports" / "ai_trade_report.json")
            lifecycle_bundle = facade._read_json(trade_dir / "lifecycle_bundle.json")
            summary_input = summary_input if isinstance(summary_input, dict) else {}
            summary_report = summary_report if isinstance(summary_report, dict) else {}
            full_report = full_report if isinstance(full_report, dict) else {}
            lifecycle_bundle = lifecycle_bundle if isinstance(lifecycle_bundle, dict) else {}
            decision_flow = summary_input.get("decision_flow") if isinstance(summary_input.get("decision_flow"), dict) else {}
            if not decision_flow:
                decision_flow = summary_report.get("decision_flow") if isinstance(summary_report.get("decision_flow"), dict) else {}
            shared_facts = full_report.get("shared_facts") if isinstance(full_report.get("shared_facts"), dict) else {}
            if not shared_facts and isinstance(summary_input, dict):
                shared_facts = summary_input.get("shared_facts") if isinstance(summary_input.get("shared_facts"), dict) else {}
            for field in ("lifecycle_completeness", "trade_origin", "evidence_recovery_used"):
                if lifecycle_bundle.get(field) not in (None, ""):
                    row[field] = lifecycle_bundle.get(field)

            entry_reason = facade._entry_reason_from_decision_flow(decision_flow, fallback=row.get("entry_reason"))
            exit_reason = str(
                decision_flow.get("exit_trigger")
                or decision_flow.get("exit_reason")
                or shared_facts.get("exit_reason")
                or row.get("exit_reason")
                or ""
            ).strip()
            if entry_reason:
                row["entry_reason"] = entry_reason
            if exit_reason:
                row["exit_reason"] = exit_reason
            if shared_facts:
                row["last_action"] = str(shared_facts.get("action") or row.get("last_action") or "")
                row["last_status"] = str(shared_facts.get("status") or row.get("last_status") or row.get("status") or "")
            row["trade_root_path"] = str(trade_dir)
            row["report_path"] = str(trade_dir / "reports" / "ai_trade_report.json")
        rows.append(row)
    return rows


def _trade_metrics_r3_impl(rows, *, facade):
    closed_rows = [row for row in rows if facade._is_closed_trade(row)]
    realized_rows = [row for row in rows if facade._is_realized_nonclosed_exit(row)]
    carryover_rows = [row for row in closed_rows if facade._is_carryover_exit_marker(row)]
    same_day_rows = facade._same_day_new_trade_rows(rows)
    same_day_closed_rows = [row for row in same_day_rows if facade._is_closed_trade(row)]
    closed_stats = facade._return_count_payload(closed_rows)
    same_day_closed_stats = facade._return_count_payload(same_day_closed_rows)
    realized_stats = facade._return_count_payload(realized_rows)
    return {
        "trade_count": len(rows),
        "closed_trade_count": len(closed_rows),
        **closed_stats,
        "same_day_new_trade_count": len(same_day_rows),
        "same_day_new_closed_trade_count": len(same_day_closed_rows),
        "same_day_new_return_sample_count": same_day_closed_stats["return_sample_count"],
        "same_day_new_win_count": same_day_closed_stats["win_count"],
        "same_day_new_loss_count": same_day_closed_stats["loss_count"],
        "same_day_new_flat_count": same_day_closed_stats["flat_count"],
        "same_day_new_win_rate": same_day_closed_stats["win_rate"],
        "same_day_new_avg_return_pct": same_day_closed_stats["avg_return_pct"],
        "carryover_closed_trade_count": len(carryover_rows),
        "return_basis": "truth_surface_net" if closed_stats["truth_surface_count"] else "operator_symbol_result_pct",
        "realized_exit_count": len(realized_rows),
        "recovered_partial_exit_count": sum(1 for row in realized_rows if facade._is_recovered_partial_marker(row)),
        "carryover_exit_count": len(carryover_rows),
        "realized_exit_return_sample_count": realized_stats["return_sample_count"],
        "realized_exit_unavailable_return_count": realized_stats["unavailable_return_count"],
        "realized_exit_observed_return_sample_count": realized_stats["observed_return_sample_count"],
        "realized_exit_truth_surface_count": realized_stats["truth_surface_count"],
        "realized_exit_win_count": realized_stats["win_count"],
        "realized_exit_loss_count": realized_stats["loss_count"],
        "realized_exit_flat_count": realized_stats["flat_count"],
        "realized_exit_observed_win_count": realized_stats["observed_win_count"],
        "realized_exit_observed_loss_count": realized_stats["observed_loss_count"],
        "realized_exit_observed_flat_count": realized_stats["observed_flat_count"],
        "realized_exit_observed_avg_return_pct": realized_stats["observed_avg_return_pct"],
        "realized_exit_win_rate": realized_stats["win_rate"],
        "realized_exit_avg_return_pct": realized_stats["avg_return_pct"],
        "realized_exit_cost_drag_loss_count": realized_stats["cost_drag_loss_count"],
        "closed_or_realized_exit_count": len(closed_rows) + len(realized_rows),
    }


def _symbol_rows_r3_impl(rows, limit, *, facade):
    grouped: Dict[str, List[Dict[str, Any]]] = facade.defaultdict(list)
    for row in rows:
        grouped[str(row.get("symbol") or "").strip().upper()].append(row)

    out: List[Dict[str, Any]] = []
    for symbol, items in grouped.items():
        closed = [row for row in items if facade._is_closed_trade(row)]
        realized = [row for row in items if facade._is_realized_nonclosed_exit(row)]
        closed_stats = facade._return_count_payload(closed)
        realized_stats = facade._return_count_payload(realized)
        out.append(
            {
                "symbol": symbol,
                "trade_count": len(items),
                "closed_trade_count": len(closed),
                **closed_stats,
                "realized_exit_count": len(realized),
                "recovered_partial_exit_count": sum(1 for row in realized if facade._is_recovered_partial_marker(row)),
                "carryover_exit_count": sum(1 for row in realized if facade._is_recovered_partial_marker(row)),
                "realized_exit_return_sample_count": realized_stats["return_sample_count"],
                "realized_exit_unavailable_return_count": realized_stats["unavailable_return_count"],
                "realized_exit_observed_return_sample_count": realized_stats["observed_return_sample_count"],
                "realized_exit_win_count": realized_stats["win_count"],
                "realized_exit_loss_count": realized_stats["loss_count"],
                "realized_exit_flat_count": realized_stats["flat_count"],
                "realized_exit_win_rate": realized_stats["win_rate"],
                "realized_exit_avg_return_pct": realized_stats["avg_return_pct"],
                "realized_exit_cost_drag_loss_count": realized_stats["cost_drag_loss_count"],
            }
        )
    out.sort(key=lambda row: (int(row.get("trade_count") or 0), abs(float(row.get("avg_return_pct") or 0.0))), reverse=True)
    return out[:limit]


def _extract_truth_surface_metrics_r3_impl(row, reports_root, *, facade):
    for path in facade._truth_surface_candidate_paths(row, reports_root):
        payload = facade._read_json(path)
        if not isinstance(payload, dict):
            continue
        truth = payload.get("truth_surface") if isinstance(payload.get("truth_surface"), dict) else {}
        if not truth:
            continue
        pnl_raw = truth.get("pnl")
        pnl = None if facade._is_unavailable_pnl(pnl_raw) else facade._safe_float(pnl_raw)
        pnl_pct = facade._ratio_to_pct(truth.get("pnl_pct"))
        cost = truth.get("cost_analysis") if isinstance(truth.get("cost_analysis"), dict) else {}
        price_move_pct = facade._ratio_to_pct(cost.get("price_move_pct"))
        observed_pct = pnl_pct if pnl is None else None
        return {
            "truth_surface_available": True,
            "truth_surface_path": str(path),
            "truth_result_label": str(truth.get("result_label") or ""),
            "truth_source": str(truth.get("truth_source") or ""),
            "truth_net_pnl": pnl,
            "truth_net_return_pct": pnl_pct if pnl is not None else None,
            "truth_observed_return_pct": observed_pct,
            "truth_price_move_pct": price_move_pct,
            "truth_cost_drag_pct": facade._ratio_to_pct(cost.get("cost_drag_pct")),
            "truth_breakeven_move_pct": facade._ratio_to_pct(cost.get("breakeven_move_pct")),
        }
    return {"truth_surface_available": False}


def _merge_daily_trade_index_with_symbol_history_r3_impl(trade_rows, history_rows, *, facade):
    history_by_trade_id = {
        str(row.get("trade_id") or "").strip(): dict(row)
        for row in history_rows
        if str(row.get("trade_id") or "").strip()
    }
    merged_rows: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for row in trade_rows:
        trade_id = str(row.get("trade_id") or "").strip()
        base = dict(history_by_trade_id.get(trade_id) or {})
        for key, value in row.items():
            if value not in (None, ""):
                base[key] = value
        merged_rows.append(base if base else dict(row))
        if trade_id:
            seen.add(trade_id)
    for trade_id, row in history_by_trade_id.items():
        if trade_id not in seen:
            merged_rows.append(dict(row))
    return merged_rows


def _enrich_rows_with_truth_surface_r3_impl(rows, reports_root, *, facade):
    out: List[Dict[str, Any]] = []
    for row in rows:
        row_obj = dict(row or {})
        row_obj.update(facade._extract_trade_decision_fields(row_obj, reports_root))
        truth_metrics = facade._extract_truth_surface_metrics(row_obj, reports_root)
        broker_skip = facade._closeout_broker_skip_for_row(row_obj, reports_root)
        broker_skip_unresolved = bool(broker_skip and not bool(truth_metrics.get("truth_surface_available")))
        if broker_skip_unresolved:
            row_obj.update(broker_skip)
        broker_truth_metrics = facade._broker_day_trade_diary_truth_metrics(row_obj, reports_root)
        if not broker_skip_unresolved and broker_truth_metrics and (
            not bool(truth_metrics.get("truth_surface_available"))
            or str(row_obj.get("last_status") or row_obj.get("status") or "").strip().lower() != "closed"
        ):
            truth_metrics = broker_truth_metrics
            row_obj["status"] = "closed"
            row_obj["last_status"] = "closed"
            row_obj["last_action"] = "SELL"
            row_obj.setdefault("exit_reason", "broker day trade diary closed")
        row_obj.update(truth_metrics)
        out.append(row_obj)
    return out


def _entry_reason_from_decision_flow_r3_impl(decision_flow, *, fallback, facade):
    for value in (
        decision_flow.get("monitor_fallback_reason"),
        decision_flow.get("actual_entry_reason"),
        decision_flow.get("entry_trigger"),
    ):
        text = str(value or "").strip()
        if text:
            return text
    fallback_text = str(fallback or "").strip()
    fallback_lower = fallback_text.lower()
    if fallback_text and not fallback_lower.startswith("scanner selected ") and not fallback_lower.startswith("entry evidence was not captured"):
        return fallback_text
    for source in (decision_flow.get("entry_confidence"), decision_flow.get("entry_reason")):
        text = str(source or "").strip()
        for pattern in (
            r"실제 트리거는\s+(.+?)(?:였|이었|입니다|였습니다)",
            r"실제 엔트리 경로는\s+(.+?)(?:였|이었|입니다|였습니다)",
            r"실제 엔트리는\s+(.+?)(?:에서\s+확정|로\s+확정|으로\s+확정)",
        ):
            match = facade.re.search(pattern, text)
            if match:
                return match.group(1).strip(" .")
    return fallback_text


def _is_closed_trade_r3_impl(row, *, facade):
    if str(row.get("broker_reconciliation_status") or "") == "skipped_unresolved":
        return False
    if facade._has_partial_lifecycle_marker(row):
        return False
    status = facade._trade_status(row)
    lifecycle_status = str(row.get("trade_lifecycle_status") or "").strip().lower()
    if status in {"open", "holding"} or lifecycle_status in {"open", "holding"}:
        return False
    if status == "closed":
        return True
    truth_source = str(row.get("truth_source") or row.get("pnl_truth_source") or "").strip().lower()
    if bool(row.get("truth_surface_available")) and truth_source in {
        "kiwoom.ka10170",
        "kiwoom.ka10077",
        "kiwoom.order_pair_snapshot",
    }:
        return True
    return False


def _entry_truth_hints_r3_impl(row, reports_root, *, facade):
    trade_dir = facade._trade_dir_for_row(row, reports_root)
    if trade_dir is None:
        return {}
    lifecycle_bundle = facade._read_json(trade_dir / "lifecycle_bundle.json")
    if not isinstance(lifecycle_bundle, dict):
        return {}
    entry = lifecycle_bundle.get("entry") if isinstance(lifecycle_bundle.get("entry"), dict) else {}
    return {
        "qty": entry.get("qty"),
        "buy_price": entry.get("price") or entry.get("avg_price") or entry.get("filled_price"),
    }
