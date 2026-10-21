"""Pure loss / no-trade / evaluation-lens aggregation (P1.5 FAST07 A7.2).

Forward-window bucketing, realized and post-exit summaries, Q9 decision-surface
counters, baseline readouts and the streaming lens accumulators. Shadow payload
and trade-model loading, forward-outcome attachment, dedupe, the broker cost
profile, the entry-delay cutoffs, every no-trade/shadow classification and the
loss diagnosis/next-action decisions stay in the original modules.
"""

from __future__ import annotations

from array import array
from collections import Counter, defaultdict
from typing import Any, Callable, Iterable, Mapping

from .metrics import performance_metrics


FORWARD_LABELS = ("+5m", "+15m", "+30m", "+60m")


# --- A7.2a: loss decomposition -------------------------------------------------


def to_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def checkpoint_return(row: Mapping[str, Any], label: str) -> float | None:
    outcome = row.get("shadow_forward_outcome")
    outcome = outcome if isinstance(outcome, Mapping) else {}
    checkpoints = outcome.get("checkpoints")
    checkpoints = checkpoints if isinstance(checkpoints, Mapping) else {}
    checkpoint = checkpoints.get(label)
    if not isinstance(checkpoint, Mapping) or checkpoint.get("status") != "observed":
        return None
    return to_float(checkpoint.get("return_pct"))


def rank_bucket(value: Any) -> str:
    try:
        rank = int(float(value))
    except (TypeError, ValueError):
        return "unknown"
    if rank == 1:
        return "rank1"
    if rank <= 3:
        return "rank2-3"
    if rank <= 5:
        return "rank4-5"
    if rank <= 10:
        return "rank6-10"
    return "rank11+"


def raw_candidate_rows(payloads: Iterable[Mapping[str, Any]], *, key: str = "candidates") -> list[dict[str, Any]]:
    """Flatten payload candidate rows, stamping each with its payload ``generated_at``."""
    rows: list[dict[str, Any]] = []
    for payload in payloads:
        generated_at = payload.get("generated_at")
        for raw in payload.get(key) or []:
            if not isinstance(raw, Mapping):
                continue
            row = dict(raw)
            row.setdefault("_payload_generated_at", generated_at)
            rows.append(row)
    return rows


def group_forward(rows: list[dict[str, Any]], key_fn: Callable[[Mapping[str, Any]], Any]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(key_fn(row) or "unknown")].append(row)
    out: list[dict[str, Any]] = []
    for name, members in groups.items():
        result: dict[str, Any] = {"name": name, "candidate_count": len(members)}
        observed_any: set[int] = set()
        for label in FORWARD_LABELS:
            values: list[float] = []
            for index, row in enumerate(members):
                value = checkpoint_return(row, label)
                if value is None:
                    continue
                observed_any.add(index)
                values.append(value)
            result[f"observed_{label[1:-1]}m"] = len(values)
            result[f"avg_return_{label[1:-1]}m_pct"] = round(sum(values) / len(values), 4) if values else None
        result["observed_count"] = len(observed_any)
        result["coverage"] = round(len(observed_any) / len(members), 4) if members else 0.0
        out.append(result)
    return sorted(out, key=lambda row: (-int(row["observed_count"]), row["name"]))


def realized_trade_summary(models: list[dict[str, Any]]) -> dict[str, Any]:
    returns: list[float] = []
    by_rank: dict[str, list[float]] = defaultdict(list)
    selection_mismatch = 0
    for model in models:
        value = to_float((model.get("outcome") or {}).get("net_return_pct"))
        if value is None:
            continue
        returns.append(value)
        selection = model.get("selection") or {}
        by_rank[rank_bucket(selection.get("selected_rank"))].append(value)
        scanner_top1 = selection.get("scanner_top1")
        scanner_top1 = scanner_top1 if isinstance(scanner_top1, Mapping) else {}
        if scanner_top1.get("symbol") and selection.get("selected_symbol") != scanner_top1.get("symbol"):
            selection_mismatch += 1
    return {
        "performance": performance_metrics(returns),
        "by_executed_rank": [{"rank_bucket": name, **performance_metrics(values)} for name, values in sorted(by_rank.items())],
        "scanner_top1_execution_mismatch_count": selection_mismatch,
        "comparable_trade_count": len(returns),
    }


def exit_hold_summary(models: list[dict[str, Any]]) -> dict[str, Any]:
    improvements: dict[str, list[float]] = defaultdict(list)
    examples: list[dict[str, Any]] = []
    observed_trade_count = 0
    observed_days: set[str] = set()
    for model in models:
        realized = to_float((model.get("outcome") or {}).get("net_return_pct"))
        post_exit = (model.get("monitor") or {}).get("post_exit")
        post_exit = post_exit if isinstance(post_exit, Mapping) else {}
        checkpoints = post_exit.get("checkpoints")
        checkpoints = checkpoints if isinstance(checkpoints, Mapping) else {}
        trade_values: dict[str, float] = {}
        for label in FORWARD_LABELS:
            row = checkpoints.get(label)
            if not isinstance(row, Mapping) or row.get("status") != "observed":
                continue
            ratio = to_float(row.get("return_pct"))
            if ratio is None:
                continue
            delta_pct = ratio * 100.0
            improvements[label].append(delta_pct)
            trade_values[label] = round(delta_pct, 4)
        if trade_values:
            observed_trade_count += 1
            observed_days.add(str(model.get("day") or "")[:10])
            examples.append(
                {
                    "trade_id": model.get("trade_id"),
                    "symbol": model.get("symbol"),
                    "realized_net_return_pct": realized,
                    "hold_improvement_pct": trade_values,
                }
            )
    return {
        "observed_trade_count": observed_trade_count,
        "observed_day_count": len({day for day in observed_days if day}),
        "by_hold_offset": [
            {
                "offset": label,
                "count": len(values),
                "average_improvement_pct": round(sum(values) / len(values), 4),
                "improved_count": sum(1 for value in values if value > 0),
                "worsened_count": sum(1 for value in values if value < 0),
            }
            for label, values in improvements.items()
        ],
        "examples": examples[:20],
        "limitation": "price delta after actual exit; realized fees remain fixed and re-entry is not assumed",
    }


def shadow_lane_rows(shadow: Mapping[str, Any], key: str) -> list[Any]:
    return (shadow.get("entry_lane_forward_outcomes") or {}).get(key) or []


def assemble_loss_decomposition(
    *,
    start: str,
    end: str,
    payload_count: int,
    shadow: Mapping[str, Any],
    model_count: int,
    rank_rows: list[dict[str, Any]],
    role_rows: list[dict[str, Any]],
    tactic_rows: list[dict[str, Any]],
    entry: dict[str, Any],
    exit_hold: dict[str, Any],
    realized: dict[str, Any],
    diagnosis: list[dict[str, Any]],
    next_action: dict[str, Any],
) -> dict[str, Any]:
    observed_days = sorted(
        {
            str(day)
            for row in shadow_lane_rows(shadow, "by_time_bucket")
            if isinstance(row, Mapping)
            for day in row.get("observed_days") or []
        }
    )
    return {
        "schema_version": "full_chain_loss_decomposition.v1",
        "behavior_effect": "evaluation_only",
        "range": {"start": start[:10], "end": end[:10]},
        "evidence": {
            "shadow_payload_count": payload_count,
            "raw_shadow_candidate_count": shadow.get("candidate_count"),
            "deduped_shadow_candidate_count": shadow.get("deduped_candidate_count"),
            "trusted_forward_count": shadow.get("forward_outcome_available_count"),
            "trusted_forward_coverage": shadow.get("forward_outcome_coverage"),
            "trusted_forward_observed_days": observed_days,
            "trade_model_count": model_count,
        },
        "raw_candidate_edge": {
            "by_time_bucket": shadow_lane_rows(shadow, "by_time_bucket"),
            "by_lane": shadow_lane_rows(shadow, "by_primary_lane"),
            "by_tactic": tactic_rows,
        },
        "scanner_ranking": {
            "by_rank_bucket": rank_rows,
            "by_selection_role": role_rows,
            "control_status": "RECONSTRUCTED_ONLY",
        },
        "strategist_commander": {
            "status": "UNAVAILABLE",
            "reason": "true pre-Strategist Scanner control and explicit Commander alternative outcomes were not historically persisted",
        },
        "monitor_entry": entry,
        "monitor_exit": exit_hold,
        "realized_system": realized,
        "diagnosis": diagnosis,
        "next_action": next_action,
    }


# --- A7.2b: no-trade attribution -----------------------------------------------


def mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def num(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def top(counter: Counter[str], limit: int = 10) -> list[dict[str, Any]]:
    return [{"name": key, "count": int(value)} for key, value in counter.most_common(limit) if key]


def q9_window_view(row: Mapping[str, Any]) -> dict[str, Any]:
    """The only parts of a q9 window the no-trade report reads (non-mappings read as {})."""
    view: dict[str, Any] = {}
    scanner = row.get("scanner_control")
    if isinstance(scanner, Mapping):
        view["scanner_control"] = {"top1_symbol": scanner.get("top1_symbol")}
    strategist = row.get("strategist_selection")
    if isinstance(strategist, Mapping):
        view["strategist_selection"] = {"selected_symbol": strategist.get("selected_symbol")}
    commander = row.get("commander_final")
    if isinstance(commander, Mapping):
        observation = commander.get("monitor_observation")
        view["commander_final"] = {
            key: commander.get(key)
            for key in ("selected_symbol", "decision", "monitor_intent", "reason", "detail", "monitor_reason")
        }
        if isinstance(observation, Mapping):
            view["commander_final"]["monitor_observation"] = {"reason": observation.get("reason")}
    return view


def q9_decision_surface(windows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Counters over the Q9 decision windows; the facade classifies the day from them."""
    counters = {
        name: Counter()
        for name in (
            "commander_decisions",
            "commander_reasons",
            "commander_details",
            "monitor_intents",
            "monitor_noop_reasons",
            "scanner_top1",
            "strategist_selected",
            "commander_selected",
        )
    }
    approve_noop = 0
    approve_buy = 0
    for window in windows:
        scanner = mapping(window.get("scanner_control"))
        strategist = mapping(window.get("strategist_selection"))
        commander = mapping(window.get("commander_final"))
        if scanner.get("top1_symbol"):
            counters["scanner_top1"][str(scanner.get("top1_symbol"))] += 1
        if strategist.get("selected_symbol"):
            counters["strategist_selected"][str(strategist.get("selected_symbol"))] += 1
        if commander.get("selected_symbol"):
            counters["commander_selected"][str(commander.get("selected_symbol"))] += 1
        decision = str(commander.get("decision") or "")
        intent = str(commander.get("monitor_intent") or "")
        counters["commander_decisions"][decision] += 1
        counters["commander_reasons"][str(commander.get("reason") or "")] += 1
        detail = str(commander.get("detail") or "")
        if detail:
            counters["commander_details"][detail[:160]] += 1
        counters["monitor_intents"][intent] += 1
        monitor_reason = str(commander.get("monitor_reason") or mapping(commander.get("monitor_observation")).get("reason") or "")
        if intent == "NOOP" and monitor_reason:
            counters["monitor_noop_reasons"][monitor_reason] += 1
        if decision == "approve" and intent == "NOOP":
            approve_noop += 1
        if decision == "approve" and intent == "BUY":
            approve_buy += 1
    return {"counters": counters, "approve_noop": approve_noop, "approve_buy": approve_buy}


def samsung_baseline(payload: Mapping[str, Any]) -> dict[str, Any]:
    summary = mapping(payload.get("summary"))
    rows = summary.get("horizons") if isinstance(summary.get("horizons"), list) else []
    return {
        "available": bool(payload),
        "horizons": [
            {
                "horizon": str(row.get("horizon") or ""),
                "trade_count": int(row.get("top1_observation_count") or row.get("trade_count") or 0),
                "win_rate": num(mapping(row.get("top1_net")).get("win_rate") or row.get("top1_win_rate") or row.get("win_rate")),
                "avg_net_return_pct": num(
                    mapping(row.get("top1_net")).get("average_return_pct")
                    or row.get("top1_avg_net_return_pct")
                    or row.get("avg_net_return_pct")
                ),
                "profit_factor": num(mapping(row.get("top1_net")).get("profit_factor") or row.get("top1_profit_factor") or row.get("profit_factor")),
            }
            for row in rows
            if isinstance(row, Mapping)
        ],
    }


def q11_opening(payload: Mapping[str, Any], signals: Mapping[str, Any], virtual: Mapping[str, Any]) -> dict[str, Any]:
    summary = mapping(virtual.get("summary") or payload.get("summary"))
    data_quality = mapping(signals.get("data_quality"))
    return {
        "available": bool(payload or signals or virtual),
        "signal_rows": int(signals.get("signal_count") or summary.get("signal_rows") or payload.get("signal_rows") or 0),
        "probe_candidates": sum(
            1
            for row in signals.get("signals") or []
            if isinstance(row, Mapping) and bool(mapping(row.get("opportunity")).get("probe_candidate"))
        ),
        "probe_near_misses": int(data_quality.get("probe_near_miss_count") or 0),
        "virtual_trades": int(virtual.get("trade_count") or summary.get("trade_count") or summary.get("virtual_trades") or 0),
        "win_rate": num(summary.get("win_rate") or payload.get("win_rate")),
        "avg_net_return_pct": num(summary.get("average_net_return_pct") or summary.get("avg_net_return") or summary.get("avg_net_return_pct") or payload.get("avg_net_return_pct")),
        "avg_mfe_pct": num(summary.get("average_mfe_pct") or summary.get("avg_mfe") or summary.get("avg_mfe_pct") or payload.get("avg_mfe_pct")),
        "avg_mae_pct": num(summary.get("average_mae_pct") or summary.get("avg_mae") or summary.get("avg_mae_pct") or payload.get("avg_mae_pct")),
        "profit_factor": num(summary.get("profit_factor") or payload.get("profit_factor")),
    }


def btc_woori_baseline(payload: Mapping[str, Any]) -> dict[str, Any]:
    summary = mapping(payload.get("summary"))
    horizons = summary.get("horizons") if isinstance(summary.get("horizons"), list) else []
    return {
        "available": bool(payload),
        "horizons": [
            {
                "horizon": str(row.get("horizon") or ""),
                "trade_count": int(row.get("trade_count") or 0),
                "win_rate": num(mapping(row.get("eligible_entries_net")).get("win_rate") or mapping(row.get("top1_net")).get("win_rate") or row.get("win_rate")),
                "avg_net_return_pct": num(
                    mapping(row.get("eligible_entries_net")).get("average_return_pct")
                    or mapping(row.get("top1_net")).get("average_return_pct")
                    or row.get("avg_net_return_pct")
                ),
                "profit_factor": num(mapping(row.get("eligible_entries_net")).get("profit_factor") or mapping(row.get("top1_net")).get("profit_factor") or row.get("profit_factor")),
            }
            for row in horizons
            if isinstance(row, Mapping)
        ],
    }


# --- A7.2c: evaluation lens -----------------------------------------------------


LENS_HORIZONS = ("+5m", "+15m", "+30m", "EOD")
BLOCKERS_OF_INTEREST = (
    "below_vwap_reclaim_not_ready",
    "pullback_not_mature",
    "breakout_not_ready",
    "volume_confirmation_missing",
    "human_chart_sanity_guard_blocked",
    "quant_entry_block:vwap_pullback_promoted_quality_gate",
)
ROLES_FOR_BEST_ROLE = ("P_SCANNER_PRE_STRATEGIST_UNIVERSE", "A_SCANNER_CONTROL", "B_STRATEGIST_RANKED", "C_COMMANDER_FINAL")
EXIT_COUNTERFACTUAL_HORIZONS = ("+5m", "+15m", "+30m", "+60m", "EOD")


def text(value: Any) -> str:
    return str(value or "").strip()


def lens_num(value: Any, default: float | None = None) -> float | None:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except Exception:
        return default


def as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _observed(row: Mapping[str, Any], horizon: str, field: str) -> float | None:
    checkpoint = as_dict(as_dict(as_dict(row.get("shadow_forward_outcome")).get("checkpoints")).get(horizon))
    if checkpoint.get("status") != "observed":
        return None
    return lens_num(checkpoint.get(field))


def lens_checkpoint(row: Mapping[str, Any], horizon: str) -> dict[str, Any]:
    return as_dict(as_dict(as_dict(row.get("shadow_forward_outcome")).get("checkpoints")).get(horizon))


def lens_checkpoint_return(row: Mapping[str, Any], horizon: str) -> float | None:
    return _observed(row, horizon, "return_pct")


def lens_checkpoint_mfe(row: Mapping[str, Any], horizon: str) -> float | None:
    return _observed(row, horizon, "mfe_pct")


def lens_checkpoint_mae(row: Mapping[str, Any], horizon: str) -> float | None:
    return _observed(row, horizon, "mae_pct")


def market_rail(row: Mapping[str, Any]) -> str:
    lane = as_dict(row.get("entry_lane_observation"))
    if lane.get("market_regime_rail"):
        return text(lane.get("market_regime_rail"))
    return text(as_dict(lane.get("market_regime_rail_shadow")).get("market_regime_rail")) or "unknown"


def blocker_label(row: Mapping[str, Any]) -> str:
    for key in ("guard_reason", "reason", "primary_failure_axis"):
        value = text(row.get(key))
        if value:
            return value
    blockers = as_dict(row.get("entry_quant_decision")).get("blockers")
    if isinstance(blockers, list) and blockers:
        return text(blockers[0])
    return "unknown"


def _horizon_record(returns: list[float], mfes: list[float], maes: list[float], reach: int) -> dict[str, Any]:
    return {
        "observed_count": len(returns),
        "return": performance_metrics(returns),
        "avg_mfe_pct": round(sum(mfes) / len(mfes), 4) if mfes else None,
        "avg_mae_pct": round(sum(maes) / len(maes), 4) if maes else None,
        "cost_floor_reachable_count": reach,
        "cost_floor_reachable_rate": round(reach / len(mfes), 4) if mfes else 0.0,
    }


def _forward_sort_key(row: Mapping[str, Any]) -> tuple[int, str]:
    return (-max(int(as_dict(row.get(h)).get("observed_count") or 0) for h in LENS_HORIZONS), row["name"])


def lens_forward_group(
    rows: list[dict[str, Any]],
    group_key: str,
    *,
    cost_floor_pct: float,
    day_of: Callable[[Mapping[str, Any]], str],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[text(row.get(group_key)) or "unknown"].append(row)
    out: list[dict[str, Any]] = []
    for name, members in grouped.items():
        record: dict[str, Any] = {"name": name, "candidate_count": len(members)}
        record["observed_days"] = sorted({day_of(row) for row in members if day_of(row)})
        for horizon in LENS_HORIZONS:
            returns: list[float] = []
            mfes: list[float] = []
            maes: list[float] = []
            reach = 0
            for row in members:
                ret = lens_checkpoint_return(row, horizon)
                mfe = lens_checkpoint_mfe(row, horizon)
                mae = lens_checkpoint_mae(row, horizon)
                if ret is not None:
                    returns.append(ret)
                if mfe is not None:
                    mfes.append(mfe)
                    if cost_floor_pct > 0 and mfe >= cost_floor_pct:
                        reach += 1
                if mae is not None:
                    maes.append(mae)
            record[horizon] = _horizon_record(returns, mfes, maes, reach)
        out.append(record)
    return sorted(out, key=_forward_sort_key)


def blocker_forward_review(
    rows: list[dict[str, Any]],
    *,
    cost_floor_pct: float,
    day_of: Callable[[Mapping[str, Any]], str],
) -> dict[str, Any]:
    prepared: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["blocker"] = blocker_label(row)
        item["market_rail"] = market_rail(row)
        prepared.append(item)
    interested = [row for row in prepared if any(token in text(row.get("blocker")) for token in BLOCKERS_OF_INTEREST)]
    return {
        "schema_version": "blocker_forward_review.v1",
        "behavior_effect": "evaluation_only",
        "cost_floor_pct": round(cost_floor_pct, 4),
        "candidate_count": len(prepared),
        "focused_candidate_count": len(interested),
        "by_blocker": lens_forward_group(interested, "blocker", cost_floor_pct=cost_floor_pct, day_of=day_of),
        "by_market_rail": lens_forward_group(prepared, "market_rail", cost_floor_pct=cost_floor_pct, day_of=day_of),
    }


def _ranked_roles(by_role: Mapping[str, Any], horizon: str) -> dict[str, Any]:
    ranked = [{"role": role, **performance_metrics(list(values))} for role, values in by_role.items() if len(values)]
    ranked.sort(key=lambda row: float(row.get("expectancy_pct") or 0.0), reverse=True)
    return {"horizon": horizon, "roles": ranked, "best_role": ranked[0]["role"] if ranked else ""}


def best_role_by_horizon(rows: list[dict[str, Any]], horizon: str) -> dict[str, Any]:
    by_role: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        role = text(row.get("q9_decision_role"))
        if role not in set(ROLES_FOR_BEST_ROLE):
            continue
        value = lens_checkpoint_return(row, horizon)
        if value is not None:
            by_role[role].append(value)
    return _ranked_roles(by_role, horizon)


def _delta_rows(pairs_by_horizon: Iterable[tuple[str, list[float], list[float]]]) -> list[dict[str, Any]]:
    return [
        {
            "horizon": horizon,
            "strategist_minus_scanner_control": performance_metrics(strategist_delta),
            "commander_minus_strategist": performance_metrics(commander_delta),
        }
        for horizon, strategist_delta, commander_delta in pairs_by_horizon
    ]


def strategist_delta_review(q9_rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in q9_rows:
        decision_id = text(row.get("q9_decision_id"))
        role = text(row.get("q9_decision_role"))
        if decision_id and role:
            grouped[decision_id][role].append(row)
    pairs: list[tuple[str, list[float], list[float]]] = []
    for horizon in LENS_HORIZONS:
        strategist_delta: list[float] = []
        commander_delta: list[float] = []
        for roles in grouped.values():
            a = min(roles.get("A_SCANNER_CONTROL") or [], key=lambda r: int(float(r.get("rank") or 999)), default={})
            b = next((r for r in roles.get("B_STRATEGIST_RANKED") or [] if r.get("q9_selected")), None)
            if not b:
                b = min(roles.get("B_STRATEGIST_RANKED") or [], key=lambda r: int(float(r.get("rank") or 999)), default={})
            c = min(roles.get("C_COMMANDER_FINAL") or [], key=lambda r: int(float(r.get("rank") or 999)), default={})
            av = lens_checkpoint_return(a, horizon) if a else None
            bv = lens_checkpoint_return(b, horizon) if b else None
            cv = lens_checkpoint_return(c, horizon) if c else None
            if av is not None and bv is not None:
                strategist_delta.append(bv - av)
            if bv is not None and cv is not None:
                commander_delta.append(cv - bv)
        pairs.append((horizon, strategist_delta, commander_delta))
    return {
        "schema_version": "strategist_delta_review.v1",
        "behavior_effect": "evaluation_only",
        "decision_window_count": len(grouped),
        "best_role_by_horizon": [best_role_by_horizon(q9_rows, horizon) for horizon in LENS_HORIZONS],
        "deltas_by_horizon": _delta_rows(pairs),
    }


def exit_counterfactual_review(models: list[dict[str, Any]]) -> dict[str, Any]:
    by_reason: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for model in models:
        exit_reason = text(as_dict(model.get("exit")).get("reason")) or text(as_dict(model.get("outcome")).get("exit_reason")) or "unknown"
        monitor = as_dict(model.get("monitor"))
        shadow = as_dict(model.get("post_exit_shadow")) or as_dict(monitor.get("post_exit"))
        checkpoints = as_dict(shadow.get("checkpoints"))
        outcome = as_dict(model.get("outcome"))
        actual = lens_num(outcome.get("net_return_pct") or outcome.get("return_pct"))
        row: dict[str, Any] = {"trade_id": model.get("trade_id"), "symbol": model.get("symbol"), "actual_return_pct": actual}
        for horizon in EXIT_COUNTERFACTUAL_HORIZONS:
            ret = lens_num(as_dict(checkpoints.get(horizon)).get("return_pct"))
            row[horizon] = ret
            if ret is not None and actual is not None:
                row[f"{horizon}_improvement_pct"] = round(ret - actual, 4)
        by_reason[exit_reason].append(row)
    groups: list[dict[str, Any]] = []
    for reason, rows in by_reason.items():
        group: dict[str, Any] = {"exit_reason": reason, "trade_count": len(rows)}
        for horizon in EXIT_COUNTERFACTUAL_HORIZONS:
            values = [float(r[f"{horizon}_improvement_pct"]) for r in rows if r.get(f"{horizon}_improvement_pct") is not None]
            group[horizon] = performance_metrics(values)
        groups.append(group)
    return {
        "schema_version": "exit_hold_counterfactual_review.v1",
        "behavior_effect": "evaluation_only",
        "trade_count": len(models),
        "by_exit_reason": sorted(groups, key=lambda row: (-int(row["trade_count"]), row["exit_reason"])),
    }


class ForwardGroupAccumulator:
    """Streaming equivalent of ``lens_forward_group``: rows are folded in one at a time, in order.

    Per group only the member count, observed days and the per-horizon return/MFE/MAE values in
    member order are needed, so those are accumulated directly (floats in ``array('d')``) instead of
    keeping every forward-outcome row of the whole freeze range alive.
    """

    def __init__(self, cost_floor_pct: float) -> None:
        self._cost_floor_pct = cost_floor_pct
        self._groups: dict[str, dict[str, Any]] = {}

    def add(self, name: str, day: str, per_horizon: dict[str, tuple[float | None, float | None, float | None]]) -> None:
        group = self._groups.get(name)
        if group is None:
            group = {
                "count": 0,
                "days": set(),
                "h": {h: {"ret": array("d"), "mfe": array("d"), "mae": array("d"), "reach": 0} for h in LENS_HORIZONS},
            }
            self._groups[name] = group
        group["count"] += 1
        if day:
            group["days"].add(day)
        for horizon in LENS_HORIZONS:
            ret, mfe, mae = per_horizon[horizon]
            slot = group["h"][horizon]
            if ret is not None:
                slot["ret"].append(ret)
            if mfe is not None:
                slot["mfe"].append(mfe)
                if self._cost_floor_pct > 0 and mfe >= self._cost_floor_pct:
                    slot["reach"] += 1
            if mae is not None:
                slot["mae"].append(mae)

    def result(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for name, group in self._groups.items():
            record: dict[str, Any] = {"name": name, "candidate_count": group["count"]}
            record["observed_days"] = sorted(group["days"])
            for horizon in LENS_HORIZONS:
                slot = group["h"][horizon]
                record[horizon] = _horizon_record(list(slot["ret"]), list(slot["mfe"]), list(slot["mae"]), slot["reach"])
            out.append(record)
        return sorted(out, key=_forward_sort_key)


class BlockerReviewAccumulator:
    """Streaming equivalent of ``blocker_forward_review`` (same output, rows folded in order)."""

    def __init__(self, cost_floor_pct: float, *, day_of: Callable[[Mapping[str, Any]], str]) -> None:
        self._cost_floor_pct = cost_floor_pct
        self._day_of = day_of
        self._prepared = 0
        self._interested = 0
        self._by_blocker = ForwardGroupAccumulator(cost_floor_pct)
        self._by_rail = ForwardGroupAccumulator(cost_floor_pct)

    def add_rows(self, rows: list[dict[str, Any]]) -> None:
        for row in rows:
            blocker, rail = blocker_label(row), market_rail(row)
            day = self._day_of(row)  # group keys never contain it; it is read off the original row
            per_horizon = {
                horizon: (lens_checkpoint_return(row, horizon), lens_checkpoint_mfe(row, horizon), lens_checkpoint_mae(row, horizon))
                for horizon in LENS_HORIZONS
            }
            self._prepared += 1
            if any(token in text(blocker) for token in BLOCKERS_OF_INTEREST):
                self._interested += 1
                self._by_blocker.add(text(blocker) or "unknown", day, per_horizon)
            self._by_rail.add(text(rail) or "unknown", day, per_horizon)

    def result(self) -> dict[str, Any]:
        return {
            "schema_version": "blocker_forward_review.v1",
            "behavior_effect": "evaluation_only",
            "cost_floor_pct": round(self._cost_floor_pct, 4),
            "candidate_count": self._prepared,
            "focused_candidate_count": self._interested,
            "by_blocker": self._by_blocker.result(),
            "by_market_rail": self._by_rail.result(),
        }


class StrategistDeltaAccumulator:
    """Streaming equivalent of ``strategist_delta_review``.

    Per decision only the three rows the review picks (control A = first lowest-rank; strategist
    B = first ``q9_selected``, else first lowest-rank; commander C = first lowest-rank) matter, and
    of those only their per-horizon returns; per-role return lists feed ``best_role_by_horizon``.
    """

    def __init__(self) -> None:
        self._decisions: dict[str, dict[str, Any]] = {}
        self._role_returns: dict[str, dict[str, Any]] = {h: {} for h in LENS_HORIZONS}

    def add_rows(self, rows: list[dict[str, Any]]) -> None:
        for row in rows:
            role = text(row.get("q9_decision_role"))
            returns = tuple(lens_checkpoint_return(row, horizon) for horizon in LENS_HORIZONS)
            if role in ROLES_FOR_BEST_ROLE:
                for horizon, value in zip(LENS_HORIZONS, returns):
                    if value is not None:
                        self._role_returns[horizon].setdefault(role, array("d")).append(value)
            decision_id = text(row.get("q9_decision_id"))
            if not (decision_id and role):
                continue
            entry = self._decisions.setdefault(decision_id, {})
            if role not in ("A_SCANNER_CONTROL", "B_STRATEGIST_RANKED", "C_COMMANDER_FINAL"):
                continue
            rank = int(float(row.get("rank") or 999))
            best = entry.get(role)
            if best is None or rank < best[0]:
                entry[role] = (rank, returns)
            if role == "B_STRATEGIST_RANKED" and row.get("q9_selected") and "B_selected" not in entry:
                entry["B_selected"] = returns

    def result(self) -> dict[str, Any]:
        pairs: list[tuple[str, list[float], list[float]]] = []
        for index, horizon in enumerate(LENS_HORIZONS):
            strategist_delta: list[float] = []
            commander_delta: list[float] = []
            for entry in self._decisions.values():
                a = entry.get("A_SCANNER_CONTROL")
                b = entry.get("B_selected") or (entry.get("B_STRATEGIST_RANKED") or (None, None))[1]
                c = entry.get("C_COMMANDER_FINAL")
                av = a[1][index] if a else None
                bv = b[index] if b else None
                cv = c[1][index] if c else None
                if av is not None and bv is not None:
                    strategist_delta.append(bv - av)
                if bv is not None and cv is not None:
                    commander_delta.append(cv - bv)
            pairs.append((horizon, strategist_delta, commander_delta))
        return {
            "schema_version": "strategist_delta_review.v1",
            "behavior_effect": "evaluation_only",
            "decision_window_count": len(self._decisions),
            "best_role_by_horizon": [_ranked_roles(self._role_returns[h], h) for h in LENS_HORIZONS],
            "deltas_by_horizon": _delta_rows(pairs),
        }


# --- A7.3: full-chain role attribution measurements ---------------------------


CHAIN_HORIZONS = ("+5m", "+15m", "+30m", "+60m")
BEHAVIOR_METRIC_EXCLUSION_DEFECTS = {
    "broker_day_partial_exit_duplicate",
    "confirmed_runtime_defect",
}


def behavior_metric_eligible(model: Mapping[str, Any]) -> bool:
    integrity = model.get("integrity") if isinstance(model.get("integrity"), Mapping) else {}
    defects = {str(value) for value in (integrity.get("defects") or [])}
    return not bool(defects & BEHAVIOR_METRIC_EXCLUSION_DEFECTS)


def role_metrics(
    candidates: list[dict[str, Any]],
    *,
    role: str,
    horizon: str,
    cost_pct: float,
    day_of: Callable[[Mapping[str, Any]], str],
) -> dict[str, Any]:
    values: list[float] = []
    days: set[str] = set()
    for row in candidates:
        if str(row.get("shadow_role") or "") != role:
            continue
        value = checkpoint_return(row, horizon)
        if value is None:
            continue
        values.append(value - cost_pct)
        day = day_of(row)
        if day:
            days.add(day)
    return {
        "role": role,
        "horizon": horizon,
        "evidence_class": "TRUSTED_SHADOW",
        "observed_count": len(values),
        "observed_day_count": len(days),
        "cost_adjusted": True,
        **performance_metrics(values),
    }


def _rate(values: list[float]) -> float | None:
    return round(sum(value > 0 for value in values) / len(values), 4) if values else None


def _mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 4) if values else None


def paired_role_deltas(
    candidates: list[dict[str, Any]],
    *,
    horizon: str,
    day_of: Callable[[Mapping[str, Any]], str],
) -> dict[str, Any]:
    windows: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    window_days: dict[str, str] = {}
    for row in candidates:
        role = str(row.get("shadow_role") or "")
        if role not in {"top_pick", "runner_up_evaluated"}:
            continue
        value = checkpoint_return(row, horizon)
        if value is None:
            continue
        window = str(row.get("_payload_generated_at") or "")
        if not window:
            continue
        windows[window][role].append(value)
        window_days[window] = day_of(row) or ""
    deltas: list[float] = []
    days: set[str] = set()
    for window, roles in windows.items():
        top_values = roles.get("top_pick") or []
        runner = roles.get("runner_up_evaluated") or []
        if not top_values or not runner:
            continue
        deltas.append((sum(top_values) / len(top_values)) - (sum(runner) / len(runner)))
        if window_days.get(window):
            days.add(window_days[window])
    return {
        "horizon": horizon,
        "comparison": "top_pick_minus_runner_up_evaluated",
        "evidence_class": "TRUSTED_SHADOW",
        "paired_window_count": len(deltas),
        "observed_day_count": len(days),
        "average_delta_pct": _mean(deltas),
        "positive_delta_rate": _rate(deltas),
        "delta_distribution": performance_metrics(deltas),
    }


def selection_availability(models: list[dict[str, Any]]) -> dict[str, Any]:
    raw_controls = strategist_snapshots = commander_snapshots = 0
    comparable_strategist = comparable_commander = 0
    missing: dict[str, int] = defaultdict(int)
    for model in models:
        selection = model.get("selection") if isinstance(model.get("selection"), Mapping) else {}
        raw_rows = selection.get("raw_scanner_top10")
        raw_control = bool(
            selection.get("raw_scanner_snapshot_source") in {"control_snapshot", "scanner_intrinsic_control_snapshot"}
            and isinstance(raw_rows, list)
            and raw_rows
        )
        strategist = bool(
            selection.get("strategist_run_id")
            and isinstance(selection.get("post_strategist_top10"), list)
            and selection.get("post_strategist_top10")
        )
        commander = bool(selection.get("commander_final_explicit"))
        raw_controls += int(raw_control)
        strategist_snapshots += int(strategist)
        commander_snapshots += int(commander)
        comparable_strategist += int(raw_control and strategist)
        comparable_commander += int(strategist and commander)
        if not raw_control:
            missing["trusted_raw_scanner_top10"] += 1
        if not strategist:
            missing["strategist_run_and_post_ranking"] += 1
        if not commander:
            missing["explicit_commander_selection_or_veto"] += 1
    return {
        "trade_model_count": len(models),
        "raw_scanner_control_count": raw_controls,
        "strategist_snapshot_count": strategist_snapshots,
        "commander_snapshot_count": commander_snapshots,
        "scanner_vs_strategist_comparable_count": comparable_strategist,
        "strategist_vs_commander_comparable_count": comparable_commander,
        "missing_fields": dict(sorted(missing.items())),
    }


def q9_role_row(roles: Mapping[str, list[dict[str, Any]]], role: str) -> dict[str, Any]:
    rows = roles.get(role) or []
    if role == "B_STRATEGIST_RANKED":
        selected = next((row for row in rows if row.get("q9_selected")), None)
        if selected:
            return selected
    return min(rows, key=lambda row: int(float(row.get("rank") or 999)), default={})


def decision_window_attribution(
    rows: Iterable[Mapping[str, Any]],
    *,
    cost_pct: float,
    day_of: Callable[[Mapping[str, Any]], str],
) -> dict[str, Any]:
    """A/B/R1/R2/C paired deltas per decision window; ``rows`` already carry forward outcomes."""
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        decision_id = str(row.get("q9_decision_id") or "")
        role = str(row.get("q9_decision_role") or "")
        if decision_id and role:
            grouped[decision_id][role].append(row)
    by_horizon: list[dict[str, Any]] = []
    for horizon in CHAIN_HORIZONS:
        strategist_deltas: list[float] = []
        refresh_deltas: list[float] = []
        commander_deltas: list[float] = []
        strategist_days: set[str] = set()
        refresh_days: set[str] = set()
        commander_days: set[str] = set()
        for roles in grouped.values():
            a_row = q9_role_row(roles, "A_SCANNER_CONTROL")
            b_row = q9_role_row(roles, "B_STRATEGIST_RANKED")
            r1_row = q9_role_row(roles, "R1_PRE_REFRESH_SCANNER")
            r2_row = q9_role_row(roles, "R2_POST_REFRESH_SCANNER")
            c_row = q9_role_row(roles, "C_COMMANDER_FINAL")
            a_value = checkpoint_return(a_row, horizon) if a_row else None
            b_value = checkpoint_return(b_row, horizon) if b_row else None
            if a_value is not None and b_value is not None:
                strategist_deltas.append(b_value - a_value)
                day = day_of(b_row)
                if day:
                    strategist_days.add(day)
            r1_value = checkpoint_return(r1_row, horizon) if r1_row else None
            r2_value = checkpoint_return(r2_row, horizon) if r2_row else None
            if r1_value is not None and r2_value is not None:
                refresh_deltas.append(r2_value - r1_value)
                day = day_of(r2_row)
                if day:
                    refresh_days.add(day)
            if b_value is None or not c_row:
                continue
            if c_row.get("q9_commander_no_trade"):
                c_net = 0.0
            else:
                c_value = checkpoint_return(c_row, horizon)
                if c_value is None:
                    continue
                c_net = c_value - cost_pct
            b_net = b_value - cost_pct
            commander_deltas.append(c_net - b_net)
            day = day_of(c_row)
            if day:
                commander_days.add(day)
        by_horizon.append(
            {
                "horizon": horizon,
                "strategist_comparison_count": len(strategist_deltas),
                "strategist_day_count": len(strategist_days),
                "average_strategist_delta_pct": _mean(strategist_deltas),
                "strategist_positive_delta_rate": _rate(strategist_deltas),
                "strategy_ranking_overlay_comparison_count": len(strategist_deltas),
                "strategy_ranking_overlay_day_count": len(strategist_days),
                "average_strategy_ranking_overlay_delta_pct": _mean(strategist_deltas),
                "strategy_ranking_overlay_positive_delta_rate": _rate(strategist_deltas),
                "post_scanner_refresh_comparison_count": len(refresh_deltas),
                "post_scanner_refresh_day_count": len(refresh_days),
                "average_post_scanner_refresh_delta_pct": _mean(refresh_deltas),
                "post_scanner_refresh_positive_delta_rate": _rate(refresh_deltas),
                "commander_comparison_count": len(commander_deltas),
                "commander_day_count": len(commander_days),
                "average_commander_delta_pct": _mean(commander_deltas),
                "commander_positive_delta_rate": _rate(commander_deltas),
            }
        )
    return {
        "schema_version": "q9_decision_window_attribution.v1",
        "role_semantics": {
            "A_SCANNER_CONTROL": "same-universe intrinsic Scanner ranking; not a full pre-Strategist control",
            "B_STRATEGIST_RANKED": "strategy-weighted Scanner ranking",
            "R1_PRE_REFRESH_SCANNER": "first Scanner result before optional tactical refresh",
            "R2_POST_REFRESH_SCANNER": "Scanner result after optional tactical refresh",
            "C_COMMANDER_FINAL": "Commander final approval or veto",
        },
        "full_strategist_contribution_status": "NOT_MEASURABLE",
        "full_strategist_missing_control": "strategy-neutral candidate sourcing and ranking shadow",
        "decision_window_count": len(grouped),
        "candidate_row_count": sum(len(r) for roles in grouped.values() for r in roles.values()),
        "by_horizon": by_horizon,
    }
