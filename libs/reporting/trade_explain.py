from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from libs.core.symbols import normalize_symbol
from libs.reporting.narrative_axes import build_narrative_explanation, narrative_axis_policy
from libs.reporting.report_metadata import (
    build_data_freshness,
    build_route_provenance,
    render_data_freshness_markdown,
)
from libs.reporting.llm_artifacts import operator_summary_artifact_root
from libs.reporting.report_source_helpers import (
    build_commander_route_summary,
    epoch_to_iso,
    utc_now_iso,
)
import sys as _r3_sys
from libs.reporting import trade_explain_scalar_projection as _scalar_owner
from libs.reporting import trade_explain_path_projection as _path_owner
from libs.reporting import trade_explain_read_projection as _read_owner
from libs.reporting import trade_explain_inventory_projection as _inventory_owner
from libs.agents.reporter.narrative.trade_explain_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _to_epoch_r4_impl,
    _extract_news_items_r4_impl,
    _extract_decision_context_r4_impl,
    _run_context_default_r4_impl,
    _build_run_contexts_r4_impl,
    _apply_commander_route_overlay_r4_impl,
    _build_execution_rows_r4_impl,
    _build_sell_pairs_fifo_r4_impl,
)
from libs.agents.reporter.narrative.trade_explain_r8_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _latest_day_r4_impl,
    _canonical_report_root_r4_impl,
    _to_markdown_r4_impl,
)

OFFICIAL_TRADE_EXPLAIN_RELATIVE_DIR = Path("dev") / "analysis" / "trade_explain"
OFFICIAL_TRADE_EXPLAIN_REPORT_DIR = (Path("reports") / OFFICIAL_TRADE_EXPLAIN_RELATIVE_DIR).as_posix()


def _safe_int(v: Any, default: int = 0) -> int:
    return _scalar_owner._safe_int(v, default)


def _safe_float(v: Any, default: float = 0.0) -> float:
    return _scalar_owner._safe_float(v, default)


def _normalize_live_symbol(value: Any) -> str:
    return normalize_symbol(value, allow_test_symbols=False)


def _to_epoch(ts: Any) -> Optional[int]:
    return _to_epoch_r4_impl(ts, facade=_r3_sys.modules[__name__])


def _utc_day(ts: Any) -> Optional[str]:
    return _scalar_owner._utc_day(ts, facade=_r3_sys.modules[__name__])


def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    return _read_owner._iter_jsonl(path, facade=_r3_sys.modules[__name__])


def _latest_day(path: Path) -> Optional[str]:
    return _latest_day_r4_impl(path, facade=_r3_sys.modules[__name__])


def _canonical_report_root(report_dir: Path) -> Path:
    return _canonical_report_root_r4_impl(report_dir, facade=_r3_sys.modules[__name__])


def official_trade_explain_report_dir(reports_root: Path) -> Path:
    return _path_owner.official_trade_explain_report_dir(reports_root, facade=_r3_sys.modules[__name__])


def build_trade_explain_output_path_metadata(report_dir: Path) -> Dict[str, Any]:
    return _path_owner.build_trade_explain_output_path_metadata(report_dir, facade=_r3_sys.modules[__name__])


def _extract_news_items(news: Dict[str, Any], llm_ctx: Dict[str, Any]) -> List[str]:
    return _extract_news_items_r4_impl(news, llm_ctx, facade=_r3_sys.modules[__name__])


def _extract_decision_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _extract_decision_context_r4_impl(payload, facade=_r3_sys.modules[__name__])


def _run_context_default(run_id: str) -> Dict[str, Any]:
    return _run_context_default_r4_impl(run_id, facade=_r3_sys.modules[__name__])


def _build_run_contexts(rows: List[Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, Any]], Counter]:
    return _build_run_contexts_r4_impl(rows, facade=_r3_sys.modules[__name__])


def _apply_commander_route_overlay(
    by_run: Dict[str, Dict[str, Any]],
    route_summary: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    return _apply_commander_route_overlay_r4_impl(by_run, route_summary, facade=_r3_sys.modules[__name__])


def _build_execution_rows(rows: List[Dict[str, Any]], by_run: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    return _build_execution_rows_r4_impl(rows, by_run, facade=_r3_sys.modules[__name__])


def _build_sell_pairs_fifo(executions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return _build_sell_pairs_fifo_r4_impl(executions, facade=_r3_sys.modules[__name__])


def _report_inventory(day: str, reports_root: Path) -> List[str]:
    return _inventory_owner._report_inventory(day, reports_root, facade=_r3_sys.modules[__name__])


def _to_markdown(
    *,
    day: str,
    event_log_path: Path,
    route_summary: Dict[str, Any],
    freshness: Dict[str, Any],
    data_freshness: Dict[str, Any],
    route_provenance: Dict[str, Any],
    output_path_policy: Dict[str, Any],
    execution_summary: Dict[str, Any],
    agent_activity: Dict[str, Any],
    sell_pairs: List[Dict[str, Any]],
    executions: List[Dict[str, Any]],
    report_inventory: List[str],
    no_trade_summary: Dict[str, Any],
    data_gaps: Dict[str, Any],
) -> str:
    return _to_markdown_r4_impl(day=day, event_log_path=event_log_path, route_summary=route_summary, freshness=freshness, data_freshness=data_freshness, route_provenance=route_provenance, output_path_policy=output_path_policy, execution_summary=execution_summary, agent_activity=agent_activity, sell_pairs=sell_pairs, executions=executions, report_inventory=report_inventory, no_trade_summary=no_trade_summary, data_gaps=data_gaps, facade=_r3_sys.modules[__name__])


def generate_trade_explain_report(
    event_log_path: Path,
    report_dir: Path,
    *,
    day: Optional[str] = None,
    max_executions: int = 120,
    max_sell_pairs: int = 120,
) -> Tuple[Path, Path, Dict[str, Any]]:
    selected_day = str(day or "").strip() or (_latest_day(event_log_path) or "")
    report_dir.mkdir(parents=True, exist_ok=True)
    output_path_policy = build_trade_explain_output_path_metadata(report_dir)

    if not selected_day:
        out = {
            "schema_version": "trade_explain.v1",
            "day": "",
            "event_log_path": str(event_log_path),
            "output_path_policy": output_path_policy,
            "executions_total": 0,
            "sell_pairs_total": 0,
            "report_json_path": "",
            "report_md_path": "",
            "error": "no_day_detected_from_event_log",
        }
        js_path = report_dir / "trade_explain_unknown.json"
        md_path = report_dir / "trade_explain_unknown.md"
        js_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        md_path.write_text("# Trade Explain Report\n\nNo day detected from event log.\n", encoding="utf-8")
        out["report_json_path"] = str(js_path)
        out["report_md_path"] = str(md_path)
        return md_path, js_path, out

    day_rows: List[Dict[str, Any]] = []
    for row in _iter_jsonl(event_log_path):
        if _utc_day(row.get("ts")) != selected_day:
            continue
        day_rows.append(row)

    canonical_report_root = _canonical_report_root(report_dir)
    route_summary = build_commander_route_summary(
        reports_root=canonical_report_root,
        day=selected_day,
        day_rows=day_rows,
    )
    by_run, stage_counts = _build_run_contexts(day_rows)
    by_run = _apply_commander_route_overlay(by_run, route_summary)
    execution_rows = _build_execution_rows(day_rows, by_run)
    sell_pairs = _build_sell_pairs_fifo(execution_rows)
    latest_row: Dict[str, Any] | None = None
    latest_epoch = 0
    run_ids = {str(r.get("run_id") or "").strip() for r in day_rows if str(r.get("run_id") or "").strip()}
    for row in day_rows:
        epoch = _to_epoch(row.get("ts")) or 0
        if epoch >= latest_epoch:
            latest_epoch = epoch
            latest_row = row

    action_counts: Counter = Counter()
    symbol_side_counts: Counter = Counter()
    symbols = set()
    for row in execution_rows:
        action = str(row.get("action") or "").upper()
        symbol = str(row.get("symbol") or "")
        action_counts[action] += 1
        symbol_side_counts[f"{symbol}:{action}"] += 1
        if symbol:
            symbols.add(symbol)

    short_holds = 0
    for pair in sell_pairs:
        if _safe_int(pair.get("hold_duration_sec_avg"), 0) < 120:
            short_holds += 1

    scanner_score_breakdown_missing_total = 0
    news_items_missing_total = 0
    for row in execution_rows:
        top_ranked = row.get("scanner_top_ranked_symbols")
        # Scanner summary currently logs symbols and top score but not per-candidate score_breakdown.
        if not top_ranked:
            scanner_score_breakdown_missing_total += 1
        news_items = row.get("news_items") if isinstance(row.get("news_items"), list) else []
        if not news_items:
            news_items_missing_total += 1

    reports_root = report_dir.parent if report_dir.name else report_dir
    inventory = _report_inventory(selected_day, reports_root)

    execution_tail = execution_rows[-max(1, int(max_executions)) :]
    pair_tail = sell_pairs[-max(1, int(max_sell_pairs)) :]

    execution_summary = {
        "executions_total": int(len(execution_rows)),
        "sell_pairs_total": int(len(sell_pairs)),
        "symbols_executed": sorted(symbols),
        "action_counts": dict(action_counts),
        "symbol_side_counts": dict(symbol_side_counts),
        "short_holds_lt_120s": int(short_holds),
    }
    agent_activity = {
        "stage_counts": dict(stage_counts),
    }
    data_gaps = {
        "scanner_score_breakdown_missing_total": int(scanner_score_breakdown_missing_total),
        "news_items_missing_total": int(news_items_missing_total),
        "note": "news headline text and scanner score_breakdown are limited by current event-log payload policy.",
    }
    no_trade_runs_total = 0
    near_ready_runs_total = 0
    strategist_fallback_total = 0
    route_selected_total: Counter[str] = Counter()
    scanner_monitor_mismatch_total = 0
    dominant_blocker_total: Counter[str] = Counter()
    for ctx in by_run.values():
        if not isinstance(ctx, dict):
            continue
        execution = ctx.get("execution") if isinstance(ctx.get("execution"), dict) else {}
        if execution:
            pass
        monitor_entry = ctx.get("monitor_entry") if isinstance(ctx.get("monitor_entry"), dict) else {}
        no_trade = monitor_entry.get("no_trade_surface") if isinstance(monitor_entry.get("no_trade_surface"), dict) else {}
        handoff = monitor_entry.get("scanner_monitor_handoff") if isinstance(monitor_entry.get("scanner_monitor_handoff"), dict) else {}
        strategist_resolution = ctx.get("strategist_policy_resolution") if isinstance(ctx.get("strategist_policy_resolution"), dict) else {}
        commander_route = ctx.get("commander_route") if isinstance(ctx.get("commander_route"), dict) else {}
        route_selected = str(commander_route.get("route_selected") or "").strip()
        if route_selected:
            route_selected_total[route_selected] += 1
        if bool(commander_route.get("strategist_fallback_used")) or bool(strategist_resolution.get("fallback_used")):
            strategist_fallback_total += 1
        if handoff and str(handoff.get("scanner_vs_monitor_alignment") or "").strip() in {"mismatch", "partial_mismatch", "guard_block"}:
            scanner_monitor_mismatch_total += 1
        if no_trade and str(no_trade.get("no_trade_stage") or "").strip() in {"guard_block", "pre_intent_wait", "pre_intent_noop"} and not execution:
            no_trade_runs_total += 1
            if bool(no_trade.get("near_ready_flag")):
                near_ready_runs_total += 1
            dominant_blocker = str(no_trade.get("dominant_blocker") or no_trade.get("no_trade_reason_code") or "").strip()
            if dominant_blocker:
                dominant_blocker_total[dominant_blocker] += 1
    no_trade_summary = {
        "no_trade_runs_total": int(no_trade_runs_total),
        "dominant_blocker_topN": [
            {"reason": str(reason), "count": int(cnt)}
            for reason, cnt in dominant_blocker_total.most_common(5)
        ],
        "near_ready_runs_total": int(near_ready_runs_total),
        "strategist_fallback_total": int(route_summary.get("strategist_fallback_total") or strategist_fallback_total),
        "route_selected_total": dict(route_summary.get("route_selected_total") or route_selected_total),
        "route_source": str(route_summary.get("route_source") or "unavailable"),
        "route_source_run_count": int(route_summary.get("route_source_run_count") or 0),
        "route_source_missing_count": int(route_summary.get("route_source_missing_count") or 0),
        "route_source_breakdown": dict(route_summary.get("route_source_breakdown") or {}),
        "scanner_monitor_mismatch_total": int(scanner_monitor_mismatch_total),
    }
    freshness = {
        "generated_at": utc_now_iso(),
        "source_run_count": int(len(run_ids)),
        "latest_run_id": str((latest_row or {}).get("run_id") or ""),
        "latest_run_ts": epoch_to_iso(latest_epoch),
    }
    data_freshness = build_data_freshness(
        generated_at=freshness["generated_at"],
        source_run_count=freshness["source_run_count"],
        latest_run_id=freshness["latest_run_id"],
        latest_run_ts=freshness["latest_run_ts"],
        stale=False,
    )
    route_provenance = build_route_provenance(route_summary)

    out: Dict[str, Any] = {
        "schema_version": "trade_explain.v1",
        "day": selected_day,
        "event_log_path": str(event_log_path),
        "generated_at": freshness["generated_at"],
        "source_run_count": freshness["source_run_count"],
        "latest_run_id": freshness["latest_run_id"],
        "latest_run_ts": freshness["latest_run_ts"],
        "data_freshness": data_freshness,
        "route_provenance": route_provenance,
        "narrative_axis_policy": narrative_axis_policy(),
        "output_path_policy": output_path_policy,
        "route_summary": {
            "route_source": str(route_summary.get("route_source") or "unavailable"),
            "route_source_run_count": int(route_summary.get("route_source_run_count") or 0),
            "route_source_missing_count": int(route_summary.get("route_source_missing_count") or 0),
            "route_source_breakdown": dict(route_summary.get("route_source_breakdown") or {}),
            "route_selected_total": dict(route_summary.get("route_selected_total") or {}),
            "strategy_generation_mode_total": dict(route_summary.get("strategy_generation_mode_total") or {}),
            "strategist_fallback_total": int(route_summary.get("strategist_fallback_total") or 0),
        },
        "route_source": str(route_summary.get("route_source") or "unavailable"),
        "route_source_run_count": int(route_summary.get("route_source_run_count") or 0),
        "route_source_missing_count": int(route_summary.get("route_source_missing_count") or 0),
        "execution_summary": execution_summary,
        "agent_activity": agent_activity,
        "report_inventory": inventory,
        "executions": execution_tail,
        "sell_pairs": pair_tail,
        "no_trade_summary": no_trade_summary,
        "data_gaps": data_gaps,
    }

    js_path = report_dir / f"trade_explain_{selected_day}.json"
    md_path = report_dir / f"trade_explain_{selected_day}.md"

    md_body = _to_markdown(
        day=selected_day,
        event_log_path=event_log_path,
        route_summary=out["route_summary"],
        freshness=freshness,
        data_freshness=data_freshness,
        route_provenance=route_provenance,
        output_path_policy=output_path_policy,
        execution_summary=execution_summary,
        agent_activity=agent_activity,
        sell_pairs=pair_tail,
        executions=execution_tail,
        report_inventory=inventory,
        no_trade_summary=no_trade_summary,
        data_gaps=data_gaps,
    )

    js_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(md_body, encoding="utf-8")
    out["report_json_path"] = str(js_path)
    out["report_md_path"] = str(md_path)
    js_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return md_path, js_path, out
