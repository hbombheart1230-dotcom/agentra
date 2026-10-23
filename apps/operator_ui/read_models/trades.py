"""Operator UI trade-day/symbol summaries, overtrading warning, top candidates, health and report detail projections.

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def load_recent_trades_for_day_r3_impl(config, day, *, limit, facade):
    rows = list(facade._iter_jsonl(config.event_log_path))
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        rid = str(row.get("run_id") or "").strip()
        if rid:
            grouped.setdefault(rid, []).append(row)
    out: List[Dict[str, Any]] = []
    for row in rows:
        if str(row.get("stage") or "") != "execute_from_packet":
            continue
        if str(row.get("event") or "") != "execution":
            continue
        if day and facade._event_day(row.get("ts_kst") or row.get("ts")) != day:
            continue
        execution = facade._normalize_execution_payload(row.get("payload") if isinstance(row.get("payload"), dict) else {})
        action = str(execution.get("action") or "").upper()
        symbol = facade.normalize_symbol(execution.get("symbol"), allow_test_symbols=True)
        if action not in {"BUY", "SELL"}:
            continue
        if not symbol:
            continue
        run_id = str(row.get("run_id") or "").strip()
        run_rows = grouped.get(run_id) or []
        monitor_summary = next(
            (r.get("payload") for r in reversed(run_rows) if str(r.get("stage") or "") == "monitor" and str(r.get("event") or "") == "summary" and isinstance(r.get("payload"), dict)),
            {},
        )
        monitor_trace = next(
            (
                (r.get("payload") or {}).get("payload")
                for r in reversed(run_rows)
                if str(r.get("stage") or "") == "decision_trace"
                and str(r.get("event") or "") == "entry_exit_decision"
                and isinstance(r.get("payload"), dict)
                and str((r.get("payload") or {}).get("agent") or "") == "monitor"
            ),
            {},
        )
        monitor_row = facade._monitor_row_summary(
            monitor_summary if isinstance(monitor_summary, dict) else {},
            monitor_trace if isinstance(monitor_trace, dict) else {},
        )
        out.append(
            {
                "ts": facade._iso_to_display(row.get("ts_kst") or row.get("ts")),
                "run_id": run_id,
                "action": action,
                "symbol": symbol,
                "qty": facade._safe_int(execution.get("qty"), 0),
                "status": str(execution.get("status") or ""),
                "ord_no": str(execution.get("ord_no") or ""),
                "active_exit_axis": str(monitor_row.get("active_exit_axis") or "-"),
                "effective_stop": str(monitor_row.get("effective_stop") or "-"),
                "peak_drawdown": str(monitor_row.get("peak_drawdown") or "-"),
            }
        )
    out = sorted(out, key=lambda row: facade._to_epoch(row.get("ts")) or 0, reverse=True)
    return out[: max(1, int(limit))]


def summarize_trades_by_symbol_r3_impl(trades, *, facade):
    grouped: Dict[str, Dict[str, Any]] = {}
    for trade in trades:
        symbol = facade.normalize_symbol(trade.get("symbol"), allow_test_symbols=True)
        if not symbol:
            continue
        row = grouped.setdefault(
            symbol,
            {
                "symbol": symbol,
                "buy_count": 0,
                "sell_count": 0,
                "net_qty": 0,
                "latest_action": "",
                "latest_ts": "",
                "latest_status": "",
            },
        )
        action = str(trade.get("action") or "").upper()
        qty = facade._safe_int(trade.get("qty"), 0)
        if action == "BUY":
            row["buy_count"] += 1
            row["net_qty"] += qty
        elif action == "SELL":
            row["sell_count"] += 1
            row["net_qty"] -= qty
        if (facade._to_epoch(trade.get("ts")) or 0) >= (facade._to_epoch(row.get("latest_ts")) or 0):
            row["latest_action"] = action
            row["latest_ts"] = str(trade.get("ts") or "")
            row["latest_status"] = str(trade.get("status") or "")
    out = list(grouped.values())
    out.sort(key=lambda row: (facade._to_epoch(row.get("latest_ts")) or 0, row.get("symbol") or ""), reverse=True)
    return out


def build_overtrading_warning_r3_impl(trades, traded_symbols, reporter_report, *, facade):
    total_executions = len(trades)
    round_trip_symbols = [
        {
            "symbol": row.get("symbol"),
            "buy_count": facade._safe_int(row.get("buy_count"), 0),
            "sell_count": facade._safe_int(row.get("sell_count"), 0),
            "round_trips": min(facade._safe_int(row.get("buy_count"), 0), facade._safe_int(row.get("sell_count"), 0)),
        }
        for row in traded_symbols
        if facade._safe_int(row.get("buy_count"), 0) > 0 and facade._safe_int(row.get("sell_count"), 0) > 0
    ]
    round_trip_symbols.sort(key=lambda row: (row.get("round_trips") or 0, row.get("symbol") or ""), reverse=True)
    ai_findings = list(reporter_report.get("ai_findings") or [])[:4] if isinstance(reporter_report, dict) else []
    reasons: List[str] = []
    level = "normal"
    if total_executions >= 10:
        level = "high"
        reasons.append(f"execution count elevated ({total_executions})")
    elif total_executions >= 5:
        level = "elevated"
        reasons.append(f"execution count moderately elevated ({total_executions})")
    if round_trip_symbols:
        if level == "normal":
            level = "elevated"
        top = round_trip_symbols[0]
        reasons.append(
            f"same-symbol round trips detected on {top.get('symbol')} ({top.get('round_trips')} cycles)"
        )
    if any("overtrading" in str(item).lower() for item in ai_findings):
        if level == "normal":
            level = "elevated"
        reasons.append("reporter flagged overtrading risk")
    if not reasons:
        reasons.append("no immediate overtrading signal in latest execution window")
    return {
        "level": level,
        "total_executions": total_executions,
        "round_trip_symbols": round_trip_symbols[:5],
        "reasons": reasons[:4],
    }


def _build_top_candidates_r3_impl(scanner_summary, scanner_trace, selected_symbol, *, facade):
    out: List[Dict[str, Any]] = []
    raw_ranked = scanner_summary.get("top_ranked_symbols") if isinstance(scanner_summary, dict) else []
    if isinstance(raw_ranked, list):
        for idx, item in enumerate(raw_ranked[:5], start=1):
            if isinstance(item, dict):
                symbol = facade.normalize_symbol(
                    item.get("symbol")
                    or item.get("code")
                    or item.get("ticker")
                    or item.get("stock")
                    or "",
                    allow_test_symbols=True,
                )
                reason = str(item.get("reason") or item.get("why") or "").strip()
                score = item.get("score_total") if item.get("score_total") is not None else item.get("score")
            else:
                symbol = facade.normalize_symbol(item, allow_test_symbols=True)
                reason = ""
                score = None
            if not symbol:
                continue
            out.append(
                {
                    "rank": idx,
                    "symbol": symbol,
                    "reason": reason,
                    "score": score,
                }
            )
    ranked_candidates = scanner_trace.get("ranked_candidates") if isinstance(scanner_trace, dict) else []
    if isinstance(ranked_candidates, list):
        seen = {str(row.get("symbol") or "") for row in out}
        for item in ranked_candidates[:5]:
            if not isinstance(item, dict):
                continue
            symbol = facade.normalize_symbol(
                item.get("symbol")
                or item.get("code")
                or item.get("ticker")
                or "",
                allow_test_symbols=True,
            )
            if not symbol or symbol in seen:
                continue
            seen.add(symbol)
            out.append(
                {
                    "rank": len(out) + 1,
                    "symbol": symbol,
                    "reason": str(item.get("reason") or item.get("why") or "").strip(),
                    "score": item.get("score_total") if item.get("score_total") is not None else item.get("score"),
                }
            )
    if selected_symbol and not any(str(row.get("symbol") or "") == selected_symbol for row in out):
        out.insert(
            0,
            {
                "rank": 1,
                "symbol": selected_symbol,
                "reason": "",
                "score": None,
            },
        )
    for idx, row in enumerate(out, start=1):
        row["rank"] = idx
    return out[:5]


def load_latest_strategist_prompt_summary_r3_impl(config, day, *, facade):
    target = {}
    for row in facade._iter_jsonl_reverse(config.evidence_log_path):
        if str(row.get("agent") or "") != "strategist":
            continue
        if str(row.get("stage") or "") != "theme_selection":
            continue
        if day and facade._event_day(row.get("timestamp")) != day:
            continue
        target = row
        break
    if not target:
        return {}
    raw_input = target.get("raw_input") if isinstance(target.get("raw_input"), dict) else {}
    parsed_output = target.get("parsed_output") if isinstance(target.get("parsed_output"), dict) else {}
    prompt = str(target.get("llm_prompt") or "")
    compact_prompt = prompt if len(prompt) <= 400 else prompt[:397] + "..."
    return {
        "run_id": str(target.get("run_id") or ""),
        "timestamp": str(target.get("timestamp") or ""),
        "news_query_targets": list(raw_input.get("news_query_targets") or [])[:8],
        "themes": list(parsed_output.get("themes") or [])[:6],
        "playbook": str(parsed_output.get("playbook") or ""),
        "market_regime": str(parsed_output.get("market_regime") or ""),
        "prompt_excerpt": compact_prompt,
    }


def load_health_r3_impl(config, *, facade):
    latest_day = facade._latest_event_day(config.event_log_path)
    operator_summary = facade._read_daily_artifact_day(config.reports_root, latest_day, "operator_summary")
    reporter = facade._read_exact_day(config.reports_root / "dev" / "analysis" / "reporter_analysis", "reporter_analysis", latest_day)
    misplaced_trade_day_roots = facade.list_misplaced_trade_day_roots(config.reports_root)
    if operator_summary:
        executive = operator_summary.get("executive_summary") if isinstance(operator_summary.get("executive_summary"), dict) else {}
        system_status = str(executive.get("system_status") or "UNKNOWN")
    else:
        system_status = "LIVE" if latest_day else "UNKNOWN"
    if reporter:
        ai_review = reporter.get("ai_review") if isinstance(reporter.get("ai_review"), dict) else {}
        ai_review_status = str(ai_review.get("status") or "disabled")
    else:
        ai_review_status = "not_generated_yet" if latest_day else "disabled"
    return {
        "status": "ok",
        "latest_day": latest_day,
        "system_status": system_status,
        "ai_review_status": ai_review_status,
        "misplaced_trade_day_root_count": len(misplaced_trade_day_roots),
        "misplaced_trade_day_roots": [str(path) for path in misplaced_trade_day_roots[:5]],
        "event_log_path": str(config.event_log_path),
        "reports_root": str(config.reports_root),
    }


def load_trade_report_detail_r3_impl(config, story_id, *, facade):
    meta = facade._trade_report_meta_for_story(config, story_id)
    if not meta:
        return {"found": False, "story_id": str(story_id or "")}

    payloads = facade.load_trade_report_detail_payloads(meta, read_json=facade._read_json)
    detail = facade._read_model_build_trade_report_detail_view(
        meta,
        payloads,
        trim_text=facade._trim_text,
        clean_str_list=facade._clean_str_list,
        normalize_symbol=facade.normalize_symbol,
        story_type_label=facade._story_type_label,
        story_type_badge_class=facade._story_type_badge_class,
        normalize_ai_report_diagnostics=facade._normalize_ai_report_diagnostics,
    )
    detail["trade_id"] = str(detail.get("trade_id") or meta.get("trade_id") or meta.get("story_id") or story_id)
    detail["story_id"] = str(detail.get("story_id") or meta.get("story_id") or story_id)
    return detail
