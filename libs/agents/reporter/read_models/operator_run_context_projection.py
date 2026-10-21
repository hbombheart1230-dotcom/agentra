"""Operator daily per-run story fold.

The streaming fold of ``build_operator_daily_summary_payload``'s day rows into per-run contexts, kept in file order
exactly as before (the OOM RCA comment inside the function still applies). Reads, clocks and the day-row iterators
stay in ``operator_visibility``; its helpers resolve on the injected facade module at call time.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List


def build_run_contexts(day_rows: Iterable[Dict[str, Any]], *, facade: Any) -> List[Dict[str, Any]]:
    # OOM RCA follow-up (2026-09-23): day_rows used to be pre-sorted here
    # (sorted(day_rows, key=epoch)), which required the caller to already
    # hold the whole day as a materialized list -- fine for the small
    # fixtures this was validated against, but a real busy trading day's
    # own JSON can be tens of MB, and retaining every row as a live Python
    # dict for the whole function scales linearly toward the 1GiB container
    # limit on its own, independent of the (already-fixed) unbounded
    # total-history bug. events.jsonl has exactly one active writer at a
    # time (SQLiteRuntimeOwnershipStore's single-owner lease), so file
    # order already IS chronological order for all practical purposes; the
    # final `stories.sort(key=first_epoch)` below independently
    # re-establishes correct STORY ordering regardless of fold order, and
    # within a single run_id the fold's per-stage fields only get
    # overwritten by a same-stage-same-event repeat, which does not happen
    # in this system's normal one-decision-per-run flow. So this now folds
    # directly off the iterator in file/stream order, discarding each row
    # right after folding it, instead of pre-sorting a fully materialized list.
    by_run: Dict[str, Dict[str, Any]] = {}
    for row in day_rows:
        run_id = str(row.get("run_id") or "").strip()
        if not run_id:
            continue
        ctx = by_run.setdefault(run_id, facade._run_context_default(run_id))
        epoch = int(row.get("_epoch") or 0)
        if ctx["first_epoch"] <= 0 or epoch < int(ctx["first_epoch"]):
            ctx["first_epoch"] = epoch
        if epoch > int(ctx["last_epoch"]):
            ctx["last_epoch"] = epoch

        stage = str(row.get("stage") or "").strip()
        event = str(row.get("event") or "").strip()
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}

        if stage == "strategist_llm" and event == "result":
            ctx["llm"] = dict(payload)
            continue

        if stage == "strategist" and event == "policy_resolution":
            ctx["strategist_policy_resolution"] = dict(payload)
            continue

        if stage == "decision" and event == "trace":
            packet = payload.get("decision_packet") if isinstance(payload.get("decision_packet"), dict) else {}
            trace = payload.get("trace") if isinstance(payload.get("trace"), dict) else {}
            intent = packet.get("intent") if isinstance(packet.get("intent"), dict) else {}
            why = packet.get("why") if isinstance(packet.get("why"), dict) else {}
            llm_ctx = trace.get("llm_context") if isinstance(trace.get("llm_context"), dict) else {}
            technical = why.get("technical") if isinstance(why.get("technical"), dict) else {}
            news = why.get("news") if isinstance(why.get("news"), dict) else {}
            policy = why.get("policy") if isinstance(why.get("policy"), dict) else {}
            if not technical:
                technical = llm_ctx.get("technical") if isinstance(llm_ctx.get("technical"), dict) else {}
            if not news:
                news = llm_ctx.get("news") if isinstance(llm_ctx.get("news"), dict) else {}
            if not policy:
                policy = llm_ctx.get("decision_policy") if isinstance(llm_ctx.get("decision_policy"), dict) else {}
            symbol_status = str(news.get("symbol_sentiment_status") or "").strip().lower()
            global_status = str(news.get("global_sentiment_status") or "").strip().lower()

            action = str(intent.get("action") or "").strip().upper()
            symbol = str(intent.get("symbol") or "").strip().upper()
            qty = facade._safe_int(intent.get("qty"), 0)

            if action:
                ctx["action"] = action
            if symbol:
                ctx["symbol"] = symbol
            if qty > 0:
                ctx["qty"] = qty

            reason_raw = facade._reason_text(intent, trace, ctx.get("llm") if isinstance(ctx.get("llm"), dict) else {})
            ctx["key_reason_raw"] = reason_raw
            ctx["key_reason"] = facade._humanize_reason(reason_raw)
            ctx["technical_evidence"] = facade._compact_kv_text(technical, topn=6)
            ctx["sentiment_evidence"] = facade._compact_kv_text(news, topn=6)
            ctx["policy_evidence"] = facade._compact_kv_text(policy, topn=6)
            ctx["invalidation"] = packet.get("invalidation") if isinstance(packet.get("invalidation"), dict) else {}
            ctx["news_status"] = {
                "symbol_sentiment_status": symbol_status,
                "global_sentiment_status": global_status,
            }
            if symbol_status and symbol_status != "ok":
                ctx["risk_flags"].append(f"symbol_sentiment_{symbol_status}")
            if global_status and global_status != "ok":
                ctx["risk_flags"].append(f"global_sentiment_{global_status}")
            ctx["decision"] = dict(payload)
            continue

        if stage == "decision_trace":
            inner = facade._decision_trace_inner(payload)

            if event == "strategic_frame":
                ctx["strategy_frame"] = dict(inner)
                if not str(ctx.get("key_reason_raw") or "").strip():
                    key_events = inner.get("key_events") if isinstance(inner.get("key_events"), list) else []
                    if key_events:
                        ctx["key_reason_raw"] = str(key_events[0])
                        ctx["key_reason"] = facade._humanize_reason(ctx["key_reason_raw"])
                continue

            if event == "candidate_selection":
                symbol = str(inner.get("selected_symbol") or "").strip().upper()
                if symbol:
                    ctx["symbol"] = symbol
                selected = inner.get("selected_candidate") if isinstance(inner.get("selected_candidate"), dict) else {}
                score_summary = inner.get("score_breakdown_summary") if isinstance(inner.get("score_breakdown_summary"), dict) else {}
                reason_raw = str(
                    selected.get("why")
                    or inner.get("candidate_source")
                    or ctx.get("key_reason_raw")
                    or ""
                ).strip()
                if reason_raw:
                    ctx["key_reason_raw"] = reason_raw
                    ctx["key_reason"] = facade._humanize_reason(reason_raw)
                if not str(ctx.get("technical_evidence") or "").strip():
                    technical_bits = {
                        "playbook": inner.get("playbook"),
                        "candidate_pool_size": inner.get("candidate_pool_size"),
                        "score_total": selected.get("score_total") or inner.get("top_score"),
                        "risk_score": selected.get("risk_score"),
                    }
                    if score_summary:
                        technical_bits["score_breakdown"] = facade._compact_kv_text(score_summary, topn=5)
                    ctx["technical_evidence"] = facade._compact_kv_text(technical_bits, topn=6)
                continue

            if event == "entry_exit_decision":
                symbol = str(inner.get("selected_symbol") or "").strip().upper()
                if symbol:
                    ctx["symbol"] = symbol
                exit_reason = str(inner.get("exit_reason") or "").strip()
                entry_reason = str(inner.get("entry_reason") or "").strip()
                reason_raw = exit_reason or entry_reason
                if reason_raw:
                    ctx["key_reason_raw"] = reason_raw
                    ctx["key_reason"] = facade._humanize_reason(reason_raw)
                thresholds = inner.get("thresholds") if isinstance(inner.get("thresholds"), dict) else {}
                if thresholds:
                    ctx["technical_evidence"] = facade._compact_kv_text(thresholds, topn=6)
                if bool(inner.get("min_hold_blocked")):
                    ctx["risk_flags"].append("min_hold_blocked")
                if bool(inner.get("sell_cooldown_blocked")):
                    ctx["risk_flags"].append("sell_cooldown_blocked")
                continue

        if stage == "scanner" and event == "candidate_selection_reason":
            ctx["scanner_selection"] = dict(payload)
            continue

        if stage == "scanner" and event == "selection_output":
            existing = ctx.get("scanner_selection") if isinstance(ctx.get("scanner_selection"), dict) else {}
            ctx["scanner_selection"] = {**dict(existing), **dict(payload)}
            continue

        if stage == "monitor" and event == "entry_decision_detail":
            ctx["monitor_entry"] = dict(payload)
            continue

        if stage == "commander_router" and event in {"route", "route_selected", "end"}:
            existing = ctx.get("commander_route") if isinstance(ctx.get("commander_route"), dict) else {}
            merged = {**dict(existing), **dict(payload)}
            route_obs = payload.get("route_observability") if isinstance(payload.get("route_observability"), dict) else {}
            if route_obs:
                merged.update(dict(route_obs))
            ctx["commander_route"] = merged
            continue

        if stage == "execute_from_packet" and event == "verdict":
            ctx["verdict"] = dict(payload)
            allowed = payload.get("allowed")
            if allowed is False:
                ctx["execution_status"] = "BLOCKED"
                ctx["guard_status"] = "intervened"
                ctx["guard_reason"] = str(payload.get("reason") or "blocked_by_guard")
                ctx["guard_reason_human"] = facade._humanize_reason(ctx.get("guard_reason"))
            continue

        if stage == "execute_from_packet" and event == "execution":
            order = payload.get("order") if isinstance(payload.get("order"), dict) else {}
            ex_payload = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
            action = str(order.get("action") or "").strip().upper()
            symbol = str(order.get("symbol") or "").strip().upper()
            qty = facade._safe_int(order.get("qty"), 0)
            if action:
                ctx["action"] = action
            if symbol:
                ctx["symbol"] = symbol
            if qty > 0:
                ctx["qty"] = qty

            broker_ok = facade._broker_code_success(ex_payload.get("broker_code"))
            if broker_ok is True:
                ctx["execution_status"] = "EXECUTED_OK"
            elif broker_ok is False:
                ctx["execution_status"] = "EXECUTED_FAIL"
            else:
                ctx["execution_status"] = "EXECUTED"
            ctx["execution"] = dict(payload)
            continue

        if stage == "commander_router" and event == "intervention":
            p_type = str(payload.get("type") or "operator_intervention").strip()
            if p_type:
                ctx["operator_intervention"].append(p_type)
            continue

        if event == "error":
            st = str(row.get("stage") or "unknown").strip() or "unknown"
            ctx["risk_flags"].append(f"error:{st}")
            continue

        if stage == "commander_router" and event == "transition":
            transition = str(payload.get("transition") or "").strip().lower()
            if transition == "cooldown":
                ctx["risk_flags"].append("cooldown_transition")

    stories: List[Dict[str, Any]] = []
    for ctx in by_run.values():
        action = str(ctx.get("action") or "").strip().upper()
        if not action:
            llm = ctx.get("llm") if isinstance(ctx.get("llm"), dict) else {}
            action = str(llm.get("intent_action") or "").strip().upper()
            if action:
                ctx["action"] = action

        if not str(ctx.get("execution_status") or "").strip() or str(ctx.get("execution_status")) == "UNKNOWN":
            if str(ctx.get("guard_status")) == "intervened":
                ctx["execution_status"] = "BLOCKED"
            elif action == "NOOP":
                ctx["execution_status"] = "NOOP"
            elif action in ("BUY", "SELL"):
                ctx["execution_status"] = "INTENT_ONLY"
            else:
                ctx["execution_status"] = "UNKNOWN"

        if not str(ctx.get("guard_reason") or "").strip():
            ctx["guard_reason"] = "none"
        ctx["guard_reason_human"] = facade._humanize_reason(ctx.get("guard_reason") or "none")
        if not str(ctx.get("key_reason") or "").strip():
            llm = ctx.get("llm") if isinstance(ctx.get("llm"), dict) else {}
            raw_reason = str(llm.get("intent_reason") or llm.get("intent_rationale") or "unspecified")
            ctx["key_reason_raw"] = raw_reason

        normalized_reason = facade._normalize_reason_code(
            ctx.get("key_reason_raw"),
            action=str(ctx.get("action") or "").strip().upper(),
            execution_status=str(ctx.get("execution_status") or "").strip().upper(),
            guard_status=str(ctx.get("guard_status") or "").strip().lower(),
        )
        ctx["key_reason_raw"] = normalized_reason
        ctx["key_reason"] = facade._humanize_reason(normalized_reason)

        monitor_entry = ctx.get("monitor_entry") if isinstance(ctx.get("monitor_entry"), dict) else {}
        no_trade_surface = monitor_entry.get("no_trade_surface") if isinstance(monitor_entry.get("no_trade_surface"), dict) else {}
        scanner_handoff = monitor_entry.get("scanner_monitor_handoff") if isinstance(monitor_entry.get("scanner_monitor_handoff"), dict) else {}
        scanner_selection = ctx.get("scanner_selection") if isinstance(ctx.get("scanner_selection"), dict) else {}
        strategist_resolution = (
            ctx.get("strategist_policy_resolution") if isinstance(ctx.get("strategist_policy_resolution"), dict) else {}
        )
        commander_route = ctx.get("commander_route") if isinstance(ctx.get("commander_route"), dict) else {}
        if no_trade_surface:
            ctx["no_trade_surface"] = dict(no_trade_surface)
            dominant_blocker = str(no_trade_surface.get("dominant_blocker") or no_trade_surface.get("no_trade_reason_code") or "").strip()
            if dominant_blocker and normalized_reason in {"NO_CANDIDATE", "GUARD_BLOCK", "unspecified"}:
                ctx["key_reason_raw"] = dominant_blocker
                ctx["key_reason"] = facade._humanize_reason(dominant_blocker)
            ctx["decision_outcome"] = str(no_trade_surface.get("decision_outcome") or "")
            ctx["dominant_blocker"] = dominant_blocker
            ctx["near_ready_flag"] = bool(no_trade_surface.get("near_ready_flag"))
            ctx["distance_to_ready_text"] = facade._compact_distance_to_ready_text(no_trade_surface.get("distance_to_ready"))
            ctx["no_trade_summary"] = str(no_trade_surface.get("no_trade_reason_summary") or "")
        merged_handoff = facade._merge_scanner_handoff_with_selection(scanner_handoff, scanner_selection)
        if merged_handoff:
            ctx["scanner_monitor_handoff"] = merged_handoff
            if not str(ctx.get("symbol") or "").strip():
                ctx["symbol"] = str(
                    merged_handoff.get("scanner_selected_symbol")
                    or merged_handoff.get("selected_symbol")
                    or ""
                ).strip().upper()
        if strategist_resolution:
            ctx["strategist_policy_resolution"] = dict(strategist_resolution)
        if commander_route:
            ctx["commander_route"] = dict(commander_route)

        if not str(ctx.get("final_outcome") or "").strip():
            if str(ctx.get("execution_status")) == "EXECUTED_OK":
                ctx["final_outcome"] = "order accepted"
            elif str(ctx.get("execution_status")) == "EXECUTED_FAIL":
                ctx["final_outcome"] = "order rejected"
            elif str(ctx.get("execution_status")) == "BLOCKED":
                ctx["final_outcome"] = f"blocked:{ctx.get('guard_reason')}"
            elif no_trade_surface:
                ctx["final_outcome"] = str(no_trade_surface.get("no_trade_reason_summary") or "no trade")
            elif str(ctx.get("execution_status")) == "NOOP":
                ctx["final_outcome"] = "no trade"
            else:
                ctx["final_outcome"] = str(ctx.get("execution_status")).lower()

        if ctx.get("operator_intervention"):
            dedup = []
            seen = set()
            for item in ctx.get("operator_intervention") or []:
                s = str(item)
                if s and s not in seen:
                    seen.add(s)
                    dedup.append(s)
            ctx["operator_intervention"] = dedup

        risk_flags = [str(x) for x in (ctx.get("risk_flags") or []) if str(x).strip()]
        if str(ctx.get("execution_status")) == "EXECUTED_FAIL":
            risk_flags.append("broker_reject")
        if str(ctx.get("guard_status")) == "intervened":
            risk_flags.append("guard_block")
        ctx["risk_flags"] = sorted(set(risk_flags))

        stories.append(ctx)

    stories.sort(key=lambda x: int(x.get("first_epoch") or 0))
    return stories
