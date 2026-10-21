"""Pure Q9 evidence normalization and trade projections (P1.5 FAST07 A7.1).

Timestamp/value normalization, lifecycle-section shaping, integrity
classification and payload assembly for the Q9 trade read model, the Q13
entry-timing report and the horizon-alignment statistics. Every artifact
read, the streamed Q9 window scan, forward-outcome attachment, cost-profile
load and all labelling/eligibility thresholds stay in the original
``libs.reporting.evaluation`` modules, which pass the results in.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Sequence

from .contracts import CONTRACT_VERSION, EvidenceClass, IntegrityStatus
from .metrics import performance_metrics


# --- shared normalization ----------------------------------------------------


def mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def num(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_ts(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text or text == "unknown":
        return None
    try:
        return datetime.fromtimestamp(float(text), tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        pass
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def epoch(value: Any) -> int:
    if value in (None, ""):
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value or "").strip()
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        pass
    try:
        return int(datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp())
    except ValueError:
        return 0


def iso(value: int) -> str:
    if value <= 0:
        return ""
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()


def stage_epoch(payload: Mapping[str, Any], *keys: str) -> int:
    for key in keys:
        value = epoch(payload.get(key))
        if value > 0:
            return value
    return 0


def meaningful(*values: Any) -> Any:
    for value in values:
        text = str(value or "").strip()
        if text and text.lower() not in {"unknown", "none", "null", "unavailable", "nan"}:
            return value
    return None


def deep_value(obj: Any, *keys: str) -> Any:
    if isinstance(obj, dict):
        for key in keys:
            if key in obj and obj[key] not in (None, ""):
                return obj[key]
        for value in obj.values():
            found = deep_value(value, *keys)
            if found not in (None, ""):
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = deep_value(value, *keys)
            if found not in (None, ""):
                return found
    return None


# --- A7.1a: Q9 trade read model ---------------------------------------------


def lifecycle_sections(bundle: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    lifecycle = bundle.get("lifecycle") if isinstance(bundle.get("lifecycle"), dict) else bundle
    entry = lifecycle.get("entry") if isinstance(lifecycle.get("entry"), dict) else bundle.get("entry")
    exit_row = lifecycle.get("exit") if isinstance(lifecycle.get("exit"), dict) else bundle.get("exit")
    return lifecycle, entry if isinstance(entry, dict) else {}, exit_row if isinstance(exit_row, dict) else {}


def is_realized_exit(exit_row: dict[str, Any], bundle: dict[str, Any]) -> bool:
    if not exit_row:
        return False
    details = dict_or_empty(exit_row.get("execution_details"))
    action = str(exit_row.get("action") or details.get("action") or "").upper()
    timestamp = exit_row.get("timestamp") or exit_row.get("ts")
    filled_quantity = details.get("filled_qty") or exit_row.get("filled_qty")
    broker_pnl = details.get("broker_realized_pnl")
    shared_status = str(dict_or_empty(bundle.get("shared_facts")).get("status") or "").lower()
    lifecycle_status = str(dict_or_empty(bundle.get("lifecycle")).get("status") or "").lower()
    return bool(
        (timestamp and action == "SELL")
        or (timestamp and filled_quantity)
        or broker_pnl is not None
        or shared_status in {"closed", "sold", "realized"}
        or lifecycle_status in {"closed", "sold", "realized"}
    )


def holding_seconds(entry_ts: Any, exit_ts: Any, fallback: Any) -> Any:
    existing = meaningful(fallback)
    if existing is not None:
        try:
            if float(existing) > 0:
                return existing
        except (TypeError, ValueError):
            pass
    entry_dt = parse_ts(entry_ts)
    exit_dt = parse_ts(exit_ts)
    if entry_dt is None or exit_dt is None or exit_dt < entry_dt:
        return fallback
    return int((exit_dt - entry_dt).total_seconds())


def candidate_by_symbol(rows: Any, symbol: str) -> dict[str, Any]:
    if not symbol or not isinstance(rows, list):
        return {}
    for row in rows:
        if isinstance(row, dict) and str(row.get("symbol") or "") == symbol:
            return dict(row)
    return {}


def scanner_evidence_context(evidence: Mapping[str, Any], selected_symbol: str) -> dict[str, Any]:
    selected_rank = None
    selected_candidate = None
    ranking_rows: list[dict[str, Any]] = []
    for event in evidence.get("candidate_ranking_tables") or []:
        payload = event.get("payload") if isinstance(event, dict) and isinstance(event.get("payload"), dict) else {}
        rows = [dict(row) for row in payload.get("rows") or [] if isinstance(row, dict)]
        if rows and not ranking_rows:
            ranking_rows = rows[:10]
        for row in rows:
            if not isinstance(row, dict) or str(row.get("symbol") or "") != selected_symbol:
                continue
            selected_rank = row.get("rank")
            selected_candidate = dict(row)
            break
        if selected_candidate:
            break
    playbook = None
    for event in evidence.get("candidate_selection_reasons") or []:
        payload = event.get("payload") if isinstance(event, dict) and isinstance(event.get("payload"), dict) else {}
        strategist_ref = dict_or_empty(payload.get("strategist_constraints_ref"))
        playbook = meaningful(payload.get("playbook"), strategist_ref.get("selected_playbook"))
        if playbook is not None:
            break
    return {
        "selected_rank": selected_rank,
        "selected_candidate": selected_candidate,
        "playbook": playbook,
        "post_strategist_top10": ranking_rows,
        "reconstructed_pre_adjust_top10": sorted(
            ranking_rows,
            key=lambda row: (
                -float(row.get("pre_adjust_score_total") or 0.0),
                -float(row.get("confidence") or 0.0),
                float(row.get("risk_score") or 0.0),
            ),
        ),
    }


def monitor_evidence_counts(evidence: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "entry_decision_count": len(evidence.get("entry_decision_details") or []),
        "exit_decision_count": len(evidence.get("exit_decision_details") or []),
        "state_transition_count": len(evidence.get("state_transitions") or []),
        "threshold_snapshot_count": len(evidence.get("threshold_snapshots") or []),
    }


def closeout_broker_skip_row(closeout: Mapping[str, Any], *, trade_id: str) -> dict[str, Any]:
    steps = dict_or_empty(closeout.get("steps"))
    broker = dict_or_empty(steps.get("broker_closed_trade_reconciliation"))
    for row in broker.get("skipped") or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("trade_id") or "") == trade_id:
            return {
                "trade_id": trade_id,
                "symbol": str(row.get("symbol") or ""),
                "reason": str(row.get("reason") or "broker_closed_trade_unresolved"),
                "snapshot_path": str(broker.get("snapshot_path") or ""),
            }
    return {}


def entry_contexts(entry: Mapping[str, Any], facts: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str]:
    scanner_context = dict_or_empty(entry.get("scanner_context"))
    strategist_context = dict_or_empty(entry.get("strategist_context"))
    monitor_context = dict_or_empty(entry.get("monitor_context"))
    selected_symbol = str(scanner_context.get("selected_symbol") or facts.get("symbol") or "")
    return scanner_context, strategist_context, monitor_context, selected_symbol


def _evaluation_exclusion(evaluation_exclusion: Mapping[str, Any], trade_id: str) -> tuple[bool, bool, bool]:
    active = bool(evaluation_exclusion.get("active")) and str(evaluation_exclusion.get("trade_id") or trade_id) == trade_id
    scopes = {str(value).strip() for value in (evaluation_exclusion.get("scopes") or []) if str(value).strip()}
    behavior = active and bool(scopes & {"behavior_attribution", "promotion_metrics"})
    exit_metric = active and bool(scopes & {"exit_horizon_attribution", "exit_quality_promotion"})
    return active, behavior, exit_metric


def classify_trade_integrity(
    *,
    inventory: Mapping[str, Any],
    entry: Mapping[str, Any],
    realized_exit: bool,
    entry_ts: Any,
    exit_ts: Any,
    broker_exit_authoritative: bool,
    pnl_source: Any,
    closeout_broker_skip: Mapping[str, Any],
    existing_broker_truth: bool,
    partial_exit_duplicate: Mapping[str, Any],
    evaluation_exclusion: Mapping[str, Any],
    behavior_metric_excluded: bool,
    exit_metric_excluded: bool,
) -> tuple[IntegrityStatus, list[str], list[str]]:
    defects: list[str] = []
    watch_items: list[str] = []
    if inventory["missing_required"]:
        watch_items.extend(f"missing:{name}" for name in inventory["missing_required"])
    if not entry:
        defects.append("entry_missing")
    if realized_exit and not parse_ts(exit_ts):
        if broker_exit_authoritative:
            watch_items.append("broker_exit_timestamp_unavailable")
        else:
            defects.append("exit_timestamp_invalid")
    if parse_ts(entry_ts) and parse_ts(exit_ts) and parse_ts(exit_ts) < parse_ts(entry_ts):
        defects.append("exit_before_entry")
    if realized_exit and not str(pnl_source or "").startswith(("lifecycle", "broker", "ai_trade_report", "exit.")):
        watch_items.append("pnl_authority_weak")
    if not realized_exit:
        watch_items.append("trade_open_or_exit_missing")
    if closeout_broker_skip and not existing_broker_truth:
        defects.append("broker_closed_trade_unresolved")
        watch_items.append(f"broker_reconciliation_skipped:{closeout_broker_skip.get('reason')}")
    if partial_exit_duplicate:
        defects.append("broker_day_partial_exit_duplicate")
        watch_items.append(f"partial_exit_duplicate_parent:{partial_exit_duplicate.get('parent_trade_id')}")
    if behavior_metric_excluded:
        defects.append("confirmed_runtime_defect")
        watch_items.append(
            f"evaluation_exclusion:{evaluation_exclusion.get('reason_code') or 'confirmed_runtime_defect'}"
        )
    elif exit_metric_excluded:
        watch_items.append(f"exit_metric_exclusion:{evaluation_exclusion.get('reason_code') or 'runtime_incident'}")

    metric_exclusion_only = bool(defects) and set(defects) <= {
        "broker_day_partial_exit_duplicate",
        "confirmed_runtime_defect",
    }
    if "exit_before_entry" in defects or "entry_missing" in defects:
        integrity = IntegrityStatus.BLOCKER
    elif metric_exclusion_only:
        integrity = IntegrityStatus.WATCH
    elif defects:
        integrity = IntegrityStatus.FAIL
    elif watch_items:
        integrity = IntegrityStatus.WATCH
    else:
        integrity = IntegrityStatus.PASS
    return integrity, defects, watch_items


def _legacy_field_source(legacy: Mapping[str, Any], key: str) -> Any:
    return (
        ((legacy.get("provenance") or {}).get("field_sources") or {}).get(key)
        if isinstance(legacy.get("provenance"), dict)
        else ""
    )


def assemble_q9_trade_read_model(
    *,
    trade_dir: str,
    legacy: Mapping[str, Any],
    facts: Mapping[str, Any],
    bundle: dict[str, Any],
    ai_report: Mapping[str, Any],
    trade_id: str,
    day: str,
    symbol: str,
    lifecycle: Mapping[str, Any],
    entry: dict[str, Any],
    exit_row: dict[str, Any],
    exit_artifact: Mapping[str, Any],
    realized_exit: bool,
    inventory: Mapping[str, Any],
    partial_exit_duplicate: Mapping[str, Any],
    closeout_broker_skip: Mapping[str, Any],
    evaluation_exclusion: Mapping[str, Any],
    scanner_context: Mapping[str, Any],
    strategist_context: Mapping[str, Any],
    monitor_context: Mapping[str, Any],
    selected_symbol: str,
    scanner_evidence: Mapping[str, Any],
    monitor_evidence: Mapping[str, Any],
    q9_snapshot: Mapping[str, Any],
    q9_snapshot_source: str,
    horizon_contract: Any,
    decompose: Callable[[Any], Any],
) -> dict[str, Any]:
    entry_ts = meaningful(entry.get("timestamp"), entry.get("ts"), facts.get("entry_ts"))
    entry_details = dict_or_empty(entry.get("execution_details"))
    entry_price = meaningful(
        entry.get("filled_price"),
        entry_details.get("filled_price"),
        entry_details.get("avg_price"),
        entry.get("avg_price"),
        entry.get("price"),
    )
    exit_ts = meaningful(exit_row.get("timestamp"), exit_row.get("ts"), facts.get("exit_ts")) if realized_exit else None
    legacy_pnl_source = _legacy_field_source(legacy, "pnl_pct")
    exit_details = dict_or_empty(exit_row.get("execution_details"))
    shared_facts = dict_or_empty(bundle.get("shared_facts"))
    broker_exit_authoritative = bool(
        exit_row.get("broker_day_authoritative") or exit_details.get("broker_day_authoritative")
    )
    broker_pnl_pct = (
        exit_details.get("broker_realized_pnl_pct")
        if exit_details.get("broker_realized_pnl_pct") is not None
        else exit_row.get("broker_realized_pnl_pct")
    )
    broker_pnl = (
        exit_details.get("broker_realized_pnl")
        if exit_details.get("broker_realized_pnl") is not None
        else exit_row.get("broker_realized_pnl")
    )
    pnl_ratio = broker_pnl_pct if broker_pnl_pct is not None else facts.get("pnl_pct")
    pnl_source = "exit.execution_details.broker_realized_pnl_pct" if broker_pnl_pct is not None else legacy_pnl_source
    exclusion_active, behavior_metric_excluded, exit_metric_excluded = _evaluation_exclusion(evaluation_exclusion, trade_id)
    existing_broker_truth = bool(
        realized_exit
        and (
            broker_exit_authoritative
            or broker_pnl_pct is not None
            or str(shared_facts.get("pnl_truth_source") or "").startswith(("kiwoom.", "broker"))
            or str(shared_facts.get("price_truth_source") or "").startswith(("kiwoom.", "broker"))
        )
    )
    integrity, defects, watch_items = classify_trade_integrity(
        inventory=inventory,
        entry=entry,
        realized_exit=realized_exit,
        entry_ts=entry_ts,
        exit_ts=exit_ts,
        broker_exit_authoritative=broker_exit_authoritative,
        pnl_source=pnl_source,
        closeout_broker_skip=closeout_broker_skip,
        existing_broker_truth=existing_broker_truth,
        partial_exit_duplicate=partial_exit_duplicate,
        evaluation_exclusion=evaluation_exclusion,
        behavior_metric_excluded=behavior_metric_excluded,
        exit_metric_excluded=exit_metric_excluded,
    )

    post_exit = (
        exit_artifact.get("post_exit_shadow")
        if isinstance(exit_artifact.get("post_exit_shadow"), dict)
        else bundle.get("post_exit_shadow")
        if isinstance(bundle.get("post_exit_shadow"), dict)
        else exit_row.get("post_exit_shadow")
        if isinstance(exit_row.get("post_exit_shadow"), dict)
        else {}
    )
    commander_final = dict_or_empty(scanner_context.get("commander_final"))
    scanner_control = dict_or_empty(q9_snapshot.get("scanner_control"))
    pre_strategist_universe = dict_or_empty(q9_snapshot.get("scanner_pre_strategist_universe"))
    strategist_selection = dict_or_empty(q9_snapshot.get("strategist_selection"))
    if not commander_final and isinstance(q9_snapshot.get("commander_final"), dict):
        commander_final = dict(q9_snapshot.get("commander_final") or {})
    raw_scanner_top10 = (
        list(scanner_control.get("top10") or [])
        if isinstance(scanner_control.get("top10"), list)
        else list(scanner_context.get("raw_scanner_top10") or [])
    )
    post_strategist_top10 = (
        list(strategist_selection.get("post_strategist_top10") or [])
        if isinstance(strategist_selection.get("post_strategist_top10"), list)
        else list(scanner_evidence.get("post_strategist_top10") or [])
    )
    raw_scanner_top1 = (
        raw_scanner_top10[0]
        if raw_scanner_top10
        else scanner_context.get("raw_scanner_top1")
        or scanner_context.get("pre_strategist_top1")
        or scanner_context.get("unbiased_top_candidate")
    )
    post_strategy_top1 = (
        post_strategist_top10[0] if post_strategist_top10 else (scanner_context.get("top_candidates") or [None])[0]
    )
    selected_candidate = dict_or_empty(scanner_evidence.get("selected_candidate"))
    if not selected_candidate:
        selected_candidate = candidate_by_symbol(post_strategist_top10, selected_symbol) or candidate_by_symbol(
            raw_scanner_top10, selected_symbol
        )
    provenance = legacy.get("provenance") if isinstance(legacy.get("provenance"), dict) else None
    return {
        "schema_version": "q9_trade_read_model.v1",
        "contract_version": CONTRACT_VERSION,
        "evidence_class": EvidenceClass.REALIZED.value if realized_exit else EvidenceClass.UNAVAILABLE.value,
        "trade_id": trade_id,
        "day": day,
        "symbol": symbol,
        "controlled_mock_lane": (
            dict(bundle.get("controlled_mock_lane") or {})
            if isinstance(bundle.get("controlled_mock_lane"), dict)
            else dict(ai_report.get("controlled_mock_lane") or {})
            if isinstance(ai_report.get("controlled_mock_lane"), dict)
            else {}
        ),
        "status": str(
            lifecycle.get("status")
            or ((bundle.get("shared_facts") or {}).get("status") if isinstance(bundle.get("shared_facts"), dict) else "")
            or facts.get("execution_label")
            or ""
        ),
        "entry": {
            "timestamp": entry_ts,
            "price": entry_price,
            "quantity": entry.get("qty") or entry.get("quantity"),
            "reason": facts.get("entry_reason"),
        },
        "exit": {
            "timestamp": exit_ts,
            "price": exit_row.get("price"),
            "quantity": exit_row.get("qty") or exit_row.get("quantity"),
            "reason": facts.get("exit_reason"),
            "broker_authoritative": broker_exit_authoritative,
            "broker_truth_source": str(
                exit_row.get("broker_day_truth_source") or exit_details.get("broker_day_truth_source") or ""
            ),
        },
        "outcome": {
            "net_return_pct": round(float(pnl_ratio) * 100.0, 6) if realized_exit and pnl_ratio is not None else None,
            "net_return_ratio": float(pnl_ratio) if realized_exit and pnl_ratio is not None else None,
            "realized_pnl": broker_pnl if realized_exit and broker_pnl is not None else (facts.get("pnl") if realized_exit else None),
            "pnl_source": pnl_source,
            "holding_seconds": holding_seconds(entry_ts, exit_ts, facts.get("hold_duration_sec")),
        },
        "horizon_contract": horizon_contract,
        "selection": {
            "scanner_top1": post_strategy_top1,
            "raw_scanner_top1": raw_scanner_top1,
            "selected_symbol": selected_symbol,
            "selected_rank": scanner_context.get("selected_rank") or scanner_evidence.get("selected_rank"),
            "selected_candidate": selected_candidate,
            "runner_ups": scanner_context.get("runner_ups") or [],
            "post_strategist_top10": post_strategist_top10,
            "reconstructed_pre_adjust_top10": scanner_evidence.get("reconstructed_pre_adjust_top10") or [],
            "raw_scanner_top10": raw_scanner_top10,
            "pre_strategist_full_universe_top20": list(pre_strategist_universe.get("intrinsic_ranked_top20") or [])[:20],
            "pre_strategist_source_universe": dict(pre_strategist_universe.get("source_universe_before_filters") or {}),
            "raw_scanner_snapshot_source": (
                scanner_control.get("source") or scanner_context.get("raw_scanner_snapshot_source") or ""
            ),
            "raw_scanner_control_scope": str(scanner_control.get("scope") or ""),
            "raw_scanner_universe_control_available": bool(scanner_control.get("universe_control_available")),
            "q9_decision_id": str(q9_snapshot.get("decision_id") or scanner_context.get("q9_decision_id") or ""),
            "q9_snapshot_source": q9_snapshot_source,
            "commander_final": commander_final,
            "commander_final_explicit": bool(
                commander_final.get("decision_id")
                and (
                    commander_final.get("selected_symbol")
                    or commander_final.get("veto")
                    or commander_final.get("no_trade")
                )
            ),
            "selection_mismatch": (
                dict(scanner_context.get("selection_mismatch") or {})
                if isinstance(scanner_context.get("selection_mismatch"), dict)
                else {}
            ),
            "score_decomposition": {
                "raw_scanner_top1": decompose(raw_scanner_top1),
                "post_strategy_top1": decompose(post_strategy_top1),
                "selected_candidate": decompose(selected_candidate),
            },
            "strategist_playbook": (
                strategist_context.get("playbook") or scanner_evidence.get("playbook") or facts.get("playbook")
            ),
            "strategist_run_id": (
                strategist_selection.get("strategist_run_id") or strategist_context.get("entry_strategist_run_id")
            ),
        },
        "monitor": {
            "entry_context": monitor_context,
            "entry_reason": facts.get("entry_reason"),
            "exit_reason": facts.get("exit_reason"),
            "primary_blocker": facts.get("primary_blocker_if_no_buy"),
            **monitor_evidence,
            "post_exit": post_exit,
        },
        "baseline_versions": {
            "q9_contract": CONTRACT_VERSION,
            "q8_contract": str(scanner_context.get("q8_contract_version") or ""),
            "tactic_contract": str(_legacy_field_source(legacy, "tactic_contract_version")),
            "strategist_prompt": str(strategist_context.get("prompt_version") or ""),
            "cost_model": str(
                monitor_context.get("cost_model_version") or monitor_context.get("broker_cost_profile_version") or ""
            ),
            "strategy_policy": str(_legacy_field_source(legacy, "strategy_policy_source")),
        },
        "integrity": {
            "status": integrity.value,
            "defects": defects,
            "watch_items": watch_items,
            "required_artifact_complete": inventory["complete"],
            "closeout_broker_reconciliation": {
                "status": (
                    "skipped_but_existing_broker_truth_available"
                    if closeout_broker_skip and existing_broker_truth
                    else "skipped_unresolved"
                    if closeout_broker_skip
                    else "not_flagged"
                ),
                **closeout_broker_skip,
            },
            "partial_exit_duplicate": partial_exit_duplicate,
            "evaluation_exclusion": (
                {
                    **evaluation_exclusion,
                    "active": exclusion_active,
                    "behavior_metric_excluded": behavior_metric_excluded,
                    "exit_metric_excluded": exit_metric_excluded,
                }
                if evaluation_exclusion
                else {}
            ),
        },
        "provenance": {
            "trade_dir": trade_dir,
            "legacy_read_model_schema": (provenance or {}).get("schema_version") if provenance is not None else "",
            "field_sources": (provenance or {}).get("field_sources") if provenance is not None else {},
        },
    }


# --- A7.1b: Q13 entry timing -------------------------------------------------


ENTRY_TIMING_HORIZONS = ("+5m", "+15m", "+30m", "+60m")
EXCLUDED_DEFECTS = {"broker_day_partial_exit_duplicate", "confirmed_runtime_defect"}


def candidate_symbol(candidate: Any) -> str:
    return str(candidate.get("symbol") or "").strip() if isinstance(candidate, Mapping) else ""


def candidate_rank(candidate: Any) -> int | None:
    value = num(candidate.get("rank") if isinstance(candidate, Mapping) else None)
    return int(value) if value is not None else None


def windows_by_decision_id(payload: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in payload.get("windows") or []:
        if not isinstance(row, dict):
            continue
        decision_id = str(row.get("decision_id") or "").strip()
        if decision_id:
            out[decision_id] = dict(row)
    return out


def row_at_or_before(rows: Sequence[Mapping[str, Any]], at_epoch: int) -> Mapping[str, Any] | None:
    prior = [row for row in rows if int(row.get("ts") or 0) <= at_epoch]
    return prior[-1] if prior else None


def pre_entry_move_pct(
    *,
    symbol: str,
    decision_epoch: int,
    entry_price: float | None,
    minute_rows_by_symbol: Mapping[str, list[Mapping[str, Any]]],
) -> tuple[float | None, dict[str, Any]]:
    if not symbol or decision_epoch <= 0 or entry_price is None or entry_price <= 0:
        return None, {"available": False, "reason": "missing_symbol_time_or_entry_price"}
    base = row_at_or_before(list(minute_rows_by_symbol.get(symbol) or []), decision_epoch)
    if not base:
        return None, {"available": False, "reason": "minute_row_before_decision_unavailable"}
    base_price = num(base.get("close") or base.get("price"))
    if base_price is None or base_price <= 0:
        return None, {"available": False, "reason": "decision_base_price_unavailable"}
    return round(((entry_price / base_price) - 1.0) * 100.0, 4), {
        "available": True,
        "decision_base_price": base_price,
        "decision_base_ts": base.get("raw_ts") or base.get("ts"),
    }


def forward_from_outcome(outcome: Mapping[str, Any]) -> dict[str, Any]:
    checkpoints = mapping(outcome.get("checkpoints"))
    return {
        "available": bool(outcome.get("available")),
        "reason": outcome.get("reason"),
        "observed_checkpoint_count": outcome.get("observed_checkpoint_count"),
        "checkpoints": {
            horizon: dict(checkpoints.get(horizon) or {"status": "pending"}) for horizon in ENTRY_TIMING_HORIZONS
        },
    }


def checkpoint(forward: Mapping[str, Any], horizon: str) -> Mapping[str, Any]:
    return mapping(mapping(forward.get("checkpoints")).get(horizon))


def is_excluded_model(model: Mapping[str, Any]) -> bool:
    defects = {str(value) for value in (mapping(model.get("integrity")).get("defects") or [])}
    return bool(defects & EXCLUDED_DEFECTS)


def entry_stage_timing(model: Mapping[str, Any], window: Mapping[str, Any]) -> dict[str, Any]:
    """Anchor/stage epochs for one trade; zero means the stage timestamp is absent."""
    selection = mapping(model.get("selection"))
    controlled_lane = mapping(model.get("controlled_mock_lane"))
    horizon_contract = mapping(model.get("horizon_contract"))
    independent_lane = str(controlled_lane.get("selection_authority") or "") == "deterministic_independent_lane"
    lane_signal_epoch = int(num(controlled_lane.get("signal_epoch")) or 0)
    decision_epoch = (
        lane_signal_epoch
        if independent_lane and lane_signal_epoch > 0
        else int(num(window.get("decision_epoch")) or epoch(window.get("generated_at")))
    )
    entry = mapping(model.get("entry"))
    strategist_payload = mapping(window.get("strategist_selection"))
    return {
        "independent_lane": independent_lane,
        "lane_signal_epoch": lane_signal_epoch,
        "decision_epoch": decision_epoch,
        "entry_epoch": epoch(entry.get("timestamp")),
        "entry_price": num(entry.get("price")),
        "scanner_time": 0 if independent_lane else decision_epoch,
        "strategist_time": 0
        if independent_lane
        else stage_epoch(strategist_payload, "generated_at", "confirmed_at", "updated_at", "timestamp"),
        "selected_time": lane_signal_epoch
        if independent_lane
        else stage_epoch(selection, "selected_at", "selected_candidate_time", "timestamp"),
        "strategy_horizon": str(
            horizon_contract.get("strategy_horizon") or horizon_contract.get("source_strategy_horizon") or ""
        ),
    }


def _delay(entry_epoch: int, stage: int) -> int | None:
    return int(entry_epoch - stage) if entry_epoch > 0 and stage > 0 else None


def entry_timing_row(
    model: Mapping[str, Any],
    timing: Mapping[str, Any],
    *,
    label: str,
    reasons: list[str],
    pre_move: float | None,
    pre_move_meta: Mapping[str, Any],
    forward: Mapping[str, Any],
) -> dict[str, Any]:
    selection = mapping(model.get("selection"))
    controlled_lane = mapping(model.get("controlled_mock_lane"))
    outcome = mapping(model.get("outcome"))
    independent_lane = bool(timing["independent_lane"])
    entry_epoch = int(timing["entry_epoch"])
    scanner_time = int(timing["scanner_time"])
    strategist_time = int(timing["strategist_time"])
    selected_time = int(timing["selected_time"])
    decision_epoch = int(timing["decision_epoch"])
    cp = {horizon: checkpoint(forward, horizon) for horizon in ENTRY_TIMING_HORIZONS}
    missing_stage_timestamps = [] if independent_lane else [
        name
        for name, value in (
            ("strategist_confirm_time", strategist_time),
            ("selected_candidate_time", selected_time),
        )
        if value <= 0
    ]
    quality: dict[str, Any] = {}
    for metric, field in (("return_pct", "return_pct"), ("mfe_pct", "mfe_pct"), ("mae_pct", "mae_pct")):
        for horizon in ENTRY_TIMING_HORIZONS:
            quality[f"{horizon}_{metric}"] = cp[horizon].get(field)
    quality.update(
        {
            "immediate_adverse_move": bool((num(cp["+5m"].get("mae_pct")) or 0.0) <= -0.55),
            "immediate_favorable_move": bool((num(cp["+5m"].get("mfe_pct")) or 0.0) >= 0.50),
            "forward_available": bool(forward.get("available")),
        }
    )
    return {
        "trade_id": str(model.get("trade_id") or ""),
        "symbol": str(model.get("symbol") or ""),
        "label": label,
        "label_reasons": reasons,
        "scanner_top1_symbol": candidate_symbol(selection.get("raw_scanner_top1")),
        "post_strategy_top1_symbol": candidate_symbol(selection.get("scanner_top1")),
        "selected_symbol": str(selection.get("selected_symbol") or ""),
        "selected_rank": (
            None
            if independent_lane
            else selection.get("selected_rank") or candidate_rank(selection.get("selected_candidate"))
        ),
        "selection_authority": "deterministic_independent_lane" if independent_lane else "main_scanner_pipeline",
        "controlled_lane_id": str(controlled_lane.get("lane_id") or ""),
        "decision_anchor_time": iso(decision_epoch),
        "strategy_horizon": str(timing["strategy_horizon"]) or "unknown",
        "stage_timing_status": "COMPLETE" if not missing_stage_timestamps else "PARTIAL",
        "missing_stage_timestamps": missing_stage_timestamps,
        "scanner_top1_time": iso(scanner_time),
        "post_strategy_top1_time": iso(strategist_time),
        "strategist_confirm_time": iso(strategist_time),
        "selected_candidate_time": iso(selected_time),
        "actual_entry_time": iso(entry_epoch),
        "scanner_to_entry_delay_sec": _delay(entry_epoch, scanner_time),
        "strategist_to_entry_delay_sec": _delay(entry_epoch, strategist_time),
        "selected_to_entry_delay_sec": _delay(entry_epoch, selected_time),
        "decision_window_to_entry_delay_sec": _delay(entry_epoch, decision_epoch),
        "pre_entry_move_pct": pre_move,
        "pre_entry_move_meta": pre_move_meta,
        "entry_return_pct": outcome.get("net_return_pct"),
        "entry_forward_quality": quality,
    }


def _mean_or_none(values: Sequence[float | None], digits: int) -> float | None:
    present = [float(v) for v in values if v is not None]
    return round(sum(present) / len(present), digits) if present else None


def entry_timing_label_summary(rows: Sequence[Mapping[str, Any]], labels: Sequence[str]) -> list[dict[str, Any]]:
    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get("label") or "INSUFFICIENT_EVIDENCE")].append(row)
    out: list[dict[str, Any]] = []
    for label in labels:
        group = groups.get(label, [])
        realized = [num(row.get("entry_return_pct")) for row in group]
        out.append(
            {
                "label": label,
                "trade_count": len(group),
                "performance": performance_metrics([float(v) for v in realized if v is not None]),
                "avg_scanner_to_entry_delay_sec": _mean_or_none(
                    [num(row.get("scanner_to_entry_delay_sec")) for row in group], 2
                ),
                "avg_5m_mfe_pct": _mean_or_none(
                    [num(mapping(row.get("entry_forward_quality")).get("+5m_mfe_pct")) for row in group], 4
                ),
                "avg_5m_mae_pct": _mean_or_none(
                    [num(mapping(row.get("entry_forward_quality")).get("+5m_mae_pct")) for row in group], 4
                ),
            }
        )
    return out


# --- A7.1c: horizon alignment observation statistics -------------------------


def _fallback_text(value: Any, fallback: str = "unknown") -> str:
    text = str(value or "").strip()
    return text if text else fallback


def horizon_group_key(row: Mapping[str, Any], dimensions: tuple[str, ...]) -> tuple[str, ...]:
    lane = row.get("entry_lane_observation")
    lane = dict(lane) if isinstance(lane, Mapping) else {}
    values = {
        "time_bucket": _fallback_text(lane.get("time_bucket")),
        "tactic": _fallback_text(row.get("quant_tactic_id")),
        "primary_lane": _fallback_text(lane.get("primary_lane")),
        "market_regime_rail": _fallback_text(lane.get("market_regime_rail")),
        "selection_role": _fallback_text(row.get("shadow_role")),
    }
    return tuple(values[name] for name in dimensions)


def profit_factor(values: list[float]) -> float:
    gains = sum(value for value in values if value > 0)
    losses = -sum(value for value in values if value < 0)
    if losses <= 0:
        return 999.0 if gains > 0 else 0.0
    return round(gains / losses, 4)


def horizon_observation_stats(
    observations: Sequence[tuple[Mapping[str, Any], float]],
    *,
    cost_pct: float,
    day_of: Callable[[Mapping[str, Any]], str],
) -> dict[str, Any]:
    """Cost-adjusted, concentration and leave-one-day-out stats for one combo/horizon.

    Eligibility thresholds and decisions are applied by the caller.
    """
    gross_values = [value for _, value in observations]
    net_values = [value - cost_pct for value in gross_values]
    days = Counter(day_of(row) or "unknown" for row, _ in observations)
    symbols = Counter(_fallback_text(row.get("symbol")) for row, _ in observations)
    count = len(observations)
    daily_net: dict[str, list[float]] = defaultdict(list)
    for (row, _), net_value in zip(observations, net_values):
        daily_net[day_of(row) or "unknown"].append(net_value)
    daily_net_returns = {day: round(sum(values) / len(values), 4) for day, values in sorted(daily_net.items())}
    leave_one_day_out: dict[str, float | None] = {}
    for excluded_day in daily_net:
        retained = [value for day, values in daily_net.items() if day != excluded_day for value in values]
        leave_one_day_out[excluded_day] = round(sum(retained) / len(retained), 4) if retained else None
    observed_lodo = [value for value in leave_one_day_out.values() if value is not None]
    return {
        "count": count,
        "net_values": net_values,
        "days": days,
        "symbols": symbols,
        "max_day_share": max(days.values()) / count if days else 1.0,
        "max_symbol_share": max(symbols.values()) / count if symbols else 1.0,
        "avg_gross": sum(gross_values) / count,
        "avg_net": sum(net_values) / count,
        "profit_factor": profit_factor(net_values),
        "daily_net_returns": daily_net_returns,
        "leave_one_day_out": leave_one_day_out,
        "worst_lodo": min(observed_lodo) if observed_lodo else None,
        "robust_across_days": bool(observed_lodo) and all(value > 0 for value in observed_lodo),
    }
