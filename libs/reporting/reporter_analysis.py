from __future__ import annotations

import json
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .operator_visibility import (
    generate_decision_story_report,
    generate_operator_daily_summary,
    generate_run_card_report,
)
from .event_log_reader import iter_jsonl_events
from .reporter_ai_review import build_ai_reporter_review
from .trade_explain import generate_trade_explain_report, official_trade_explain_report_dir
from libs.core.symbols import normalize_symbol
from libs.research.evidence_ledger import record_decision_bridge, record_raw_input
from libs.research.strategy_memory_store import (
    resolve_strategy_memory_daily_dir,
    resolve_strategy_memory_path,
    save_strategy_feedback,
)
import sys as _r3_sys
from libs.agents.reporter.read_models.reporter_analysis_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _to_epoch_r4_impl,
    _top_chain_run_ids_r4_impl,
    _make_evidence_ref_r4_impl,
    _decision_trace_agent_payload_r4_impl,
    _execution_rows_by_run_r4_impl,
    _build_trade_decision_summaries_r4_impl,
    _build_strategy_effectiveness_r4_impl,
    _build_overtrading_diagnostics_r4_impl,
    _build_incident_postmortem_r4_impl,
    _build_market_context_r4_impl,
    _extract_report_focus_targets_r4_impl,
)
from libs.agents.reporter.read_models.reporter_analysis_bodies_02 import (  # R-4 owner bodies (facade-injected)
    _build_decision_chains_r4_impl,
    _build_decision_trace_chain_summary_r4_impl,
    _build_trade_summary_section_r4_impl,
    _build_ai_evidence_catalog_r4_impl,
    _infer_ai_evidence_keys_r4_impl,
    _hydrate_ai_evidence_details_r4_impl,
    _first_nonempty_str_r4_impl,
    _ensure_min_ai_review_payload_r4_impl,
    _build_strategy_frame_summary_r4_impl,
)
from libs.agents.reporter.read_models.reporter_analysis_bodies_03 import (  # R-4 owner bodies (facade-injected)
    _build_strategist_evaluation_r4_impl,
    _build_scanner_evaluation_r4_impl,
    _build_monitor_evaluation_r4_impl,
    _build_supervisor_activity_r4_impl,
    _build_report_views_r4_impl,
    _build_improvement_suggestions_r4_impl,
)
from libs.agents.reporter.read_models.reporter_analysis_bodies_04 import (  # R-4 owner bodies (facade-injected)
    _to_markdown_r4_impl,
)
from libs.agents.reporter.read_models.reporter_analysis_r8_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _latest_day_r4_impl,
)
from libs.agents.reporter.read_models import analysis_report_projection as _analysis_projection  # P1.5 DEV-A read-model


def _safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(float(v))
    except Exception:
        return int(default)


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)


def _normalize_live_symbol(value: Any) -> str:
    return normalize_symbol(value, allow_test_symbols=False)


def _to_epoch(ts: Any) -> Optional[int]:
    return _to_epoch_r4_impl(ts, facade=_r3_sys.modules[__name__])


def _utc_day(ts: Any) -> Optional[str]:
    epoch = _to_epoch(ts)
    if epoch is None:
        return None
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%d")


def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    out: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if isinstance(obj, dict):
                out.append(obj)
    return out


def _latest_day(path: Path) -> Optional[str]:
    return _latest_day_r4_impl(path, facade=_r3_sys.modules[__name__])


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return obj if isinstance(obj, dict) else {}


def _reason_text(reason: Any) -> str:
    s = str(reason or "").strip()
    return s if s else "unspecified"


def _top_chain_run_ids(trace_summary: Dict[str, Any], agent_key: str, *, limit: int = 3) -> List[str]:
    return _top_chain_run_ids_r4_impl(trace_summary, agent_key, limit=limit, facade=_r3_sys.modules[__name__])


def _make_evidence_ref(*, path: Any, field: str, run_ids: Optional[List[str]] = None, summary: Any = "") -> Dict[str, Any]:
    return _make_evidence_ref_r4_impl(path=path, field=field, run_ids=run_ids, summary=summary, facade=_r3_sys.modules[__name__])


def _decision_trace_agent_payload(row: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """Return (agent, payload) from `stage=decision_trace` rows.

    Expected event payload shape:
    {
      "agent": "strategist|scanner|monitor|supervisor|executor",
      "payload": {...}
    }
    """
    return _decision_trace_agent_payload_r4_impl(row, facade=_r3_sys.modules[__name__])


def _execution_rows_by_run(executions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    return _execution_rows_by_run_r4_impl(executions, facade=_r3_sys.modules[__name__])


def _build_trade_decision_summaries(trade_explain_obj: Dict[str, Any]) -> Dict[str, Any]:
    return _build_trade_decision_summaries_r4_impl(trade_explain_obj, facade=_r3_sys.modules[__name__])


def _build_intent_flow_analysis(
    *,
    day_rows: List[Dict[str, Any]],
    intents_path: Optional[Path],
    day: str,
    operator_summary_obj: Dict[str, Any],
) -> Dict[str, Any]:
    created = 0
    approved = 0
    executed = 0
    blocked = 0
    status_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()

    if intents_path is not None and intents_path.exists():
        for row in _iter_jsonl(intents_path):
            ts = row.get("ts")
            if _utc_day(ts) != day:
                continue
            status = str(row.get("status") or "").strip().lower()
            reason = _reason_text(row.get("reason"))
            if status:
                status_counts[status] += 1
                if status == "approved":
                    approved += 1
                elif status == "executed":
                    executed += 1
                elif status in ("rejected", "failed"):
                    blocked += 1
                    reason_counts[reason] += 1
            else:
                created += 1

    for row in day_rows:
        stage = str(row.get("stage") or "").strip()
        event = str(row.get("event") or "").strip()
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        if stage == "execute_from_packet" and event == "verdict" and payload.get("allowed") is False:
            blocked += 1
            reason_counts[_reason_text(payload.get("reason"))] += 1
        if stage == "monitor" and event == "summary":
            if bool(payload.get("min_hold_blocked")):
                reason_counts["min_hold_blocked"] += 1
            if bool(payload.get("sell_cooldown_blocked")):
                reason_counts["sell_cooldown_blocked"] += 1
            mr = str(payload.get("monitor_reason") or "").strip()
            if mr:
                reason_counts[f"monitor:{mr}"] += 1

    metrics_exec = (
        operator_summary_obj.get("raw_snapshot", {}).get("metrics_execution", {})
        if isinstance(operator_summary_obj.get("raw_snapshot"), dict)
        else {}
    )
    if created <= 0:
        created = _safe_int(metrics_exec.get("intents_created"), created)
    if blocked <= 0:
        blocked = _safe_int(metrics_exec.get("intents_blocked"), blocked)
    if approved <= 0:
        approved = _safe_int(metrics_exec.get("intents_approved"), approved)
    if executed <= 0:
        executed = _safe_int(metrics_exec.get("intents_executed"), executed)

    return {
        "intents_created": int(created),
        "intents_blocked": int(blocked),
        "intents_approved": int(approved),
        "intents_executed": int(executed),
        "status_counts": dict(status_counts),
        "reason_top": dict(reason_counts.most_common(12)),
    }


def _build_strategy_effectiveness(
    *,
    day_rows: List[Dict[str, Any]],
    trade_explain_obj: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_strategy_effectiveness_r4_impl(day_rows=day_rows, trade_explain_obj=trade_explain_obj, facade=_r3_sys.modules[__name__])


def _build_overtrading_diagnostics(
    *,
    trade_explain_obj: Dict[str, Any],
    intent_flow: Dict[str, Any],
    rapid_threshold_sec: int,
) -> Dict[str, Any]:
    return _build_overtrading_diagnostics_r4_impl(trade_explain_obj=trade_explain_obj, intent_flow=intent_flow, rapid_threshold_sec=rapid_threshold_sec, facade=_r3_sys.modules[__name__])


def _build_incident_postmortem(
    *,
    overtrading: Dict[str, Any],
    intent_flow: Dict[str, Any],
    day_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return _build_incident_postmortem_r4_impl(overtrading=overtrading, intent_flow=intent_flow, day_rows=day_rows, facade=_r3_sys.modules[__name__])


def _build_market_context(*, trade_explain_obj: Dict[str, Any], day_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return _build_market_context_r4_impl(trade_explain_obj=trade_explain_obj, day_rows=day_rows, facade=_r3_sys.modules[__name__])


def _extract_report_focus_targets(day_rows: List[Dict[str, Any]]) -> List[str]:
    return _extract_report_focus_targets_r4_impl(day_rows, facade=_r3_sys.modules[__name__])


def _build_decision_chains(day_rows: List[Dict[str, Any]], *, limit: int = 200) -> Dict[str, Any]:
    return _build_decision_chains_r4_impl(day_rows, limit=limit, facade=_r3_sys.modules[__name__])


def _build_decision_trace_chain_summary(day_rows: List[Dict[str, Any]], *, limit: int = 200) -> Dict[str, Any]:
    return _build_decision_trace_chain_summary_r4_impl(day_rows, limit=limit, facade=_r3_sys.modules[__name__])


def _build_trade_summary_section(
    *,
    trade_decision: Dict[str, Any],
    decision_chains: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_trade_summary_section_r4_impl(trade_decision=trade_decision, decision_chains=decision_chains, facade=_r3_sys.modules[__name__])


def _build_ai_evidence_catalog(out: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return _build_ai_evidence_catalog_r4_impl(out, facade=_r3_sys.modules[__name__])


def _infer_ai_evidence_keys(text: str, catalog: Dict[str, Dict[str, Any]]) -> List[str]:
    return _infer_ai_evidence_keys_r4_impl(text, catalog, facade=_r3_sys.modules[__name__])


def _hydrate_ai_evidence_details(
    texts: List[Any],
    link_items: Any,
    catalog: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    return _hydrate_ai_evidence_details_r4_impl(texts, link_items, catalog, facade=_r3_sys.modules[__name__])


def _first_nonempty_str(*values: Any) -> str:
    return _first_nonempty_str_r4_impl(*values, facade=_r3_sys.modules[__name__])


def _ensure_min_ai_review_payload(
    *,
    out: Dict[str, Any],
    ai_review: Dict[str, Any],
) -> Dict[str, Any]:
    return _ensure_min_ai_review_payload_r4_impl(out=out, ai_review=ai_review, facade=_r3_sys.modules[__name__])


def _build_strategy_frame_summary(day_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return _build_strategy_frame_summary_r4_impl(day_rows, facade=_r3_sys.modules[__name__])


def _build_strategist_evaluation(day_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return _build_strategist_evaluation_r4_impl(day_rows, facade=_r3_sys.modules[__name__])


def _build_scanner_evaluation(day_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return _build_scanner_evaluation_r4_impl(day_rows, facade=_r3_sys.modules[__name__])


def _build_monitor_evaluation(
    *,
    day_rows: List[Dict[str, Any]],
    overtrading: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_monitor_evaluation_r4_impl(day_rows=day_rows, overtrading=overtrading, facade=_r3_sys.modules[__name__])


def _build_supervisor_activity(day_rows: List[Dict[str, Any]], *, intent_flow: Dict[str, Any]) -> Dict[str, Any]:
    return _build_supervisor_activity_r4_impl(day_rows, intent_flow=intent_flow, facade=_r3_sys.modules[__name__])


def _build_report_views(
    *,
    day: str,
    trade_summary: Dict[str, Any],
    monitor_eval: Dict[str, Any],
    scanner_eval: Dict[str, Any],
    supervisor_activity: Dict[str, Any],
    incidents: Dict[str, Any],
    improvement_suggestions: List[str],
) -> Dict[str, Any]:
    return _build_report_views_r4_impl(day=day, trade_summary=trade_summary, monitor_eval=monitor_eval, scanner_eval=scanner_eval, supervisor_activity=supervisor_activity, incidents=incidents, improvement_suggestions=improvement_suggestions, facade=_r3_sys.modules[__name__])


def _build_improvement_suggestions(
    *,
    strategist_eval: Dict[str, Any],
    scanner_eval: Dict[str, Any],
    monitor_eval: Dict[str, Any],
    supervisor_activity: Dict[str, Any],
    incidents: Dict[str, Any],
    report_focus_targets: List[str],
) -> List[str]:
    return _build_improvement_suggestions_r4_impl(strategist_eval=strategist_eval, scanner_eval=scanner_eval, monitor_eval=monitor_eval, supervisor_activity=supervisor_activity, incidents=incidents, report_focus_targets=report_focus_targets, facade=_r3_sys.modules[__name__])


def _to_markdown(out: Dict[str, Any]) -> str:
    return _to_markdown_r4_impl(out, facade=_r3_sys.modules[__name__])


def generate_reporter_analysis_report(
    event_log_path: Path,
    report_dir: Path,
    *,
    day: Optional[str] = None,
    intents_path: Optional[Path] = None,
    reports_root: Optional[Path] = None,
    rapid_cycle_threshold_sec: int = 120,
    ai_review_enabled: Optional[bool] = None,
    ai_review_model: Optional[str] = None,
    ai_review_temperature: Optional[float] = None,
    ai_review_max_tokens: int = 900,
    generate_decision_story: bool = False,
    generate_run_cards: bool = False,
) -> Tuple[Path, Path, Dict[str, Any]]:
    """Generate enhanced reporter analysis from append-only logs.

    Reporter remains passive: this function reads logs only and derives reports.
    """
    report_dir.mkdir(parents=True, exist_ok=True)
    root = reports_root or report_dir.parent
    canonical_reports_root = _canonical_reports_root(root)
    target_day = str(day or _latest_day(event_log_path) or date.today().isoformat())
    reporter_run_id = f"reporter-{target_day}"

    # OOM RCA follow-up (2026-09-23): this used to scan _iter_jsonl's
    # unbounded read of the ENTIRE events.jsonl history on every call --
    # this function is reachable from the standard live intraday trade
    # report path (live_execution_bundle_runner.py, cache-miss trigger),
    # not just the once-daily EOD cascade, so the unbounded scan could fire
    # repeatedly through the trading day as the log kept growing. Reuses
    # the same day-scoped, disk-cached reader already used elsewhere in
    # the reporting stack (libs/reporting/event_log_reader.py) -- day_rows
    # itself is still a materialized list here (this function's ~10
    # downstream _build_*(day_rows) helpers all need independent list
    # access, unlike operator_visibility.py's decision_story/run_card,
    # which were rewritten to stream), so this fixes the unbounded-total-
    # history growth, not day-size scaling.
    day_rows = []
    for row in iter_jsonl_events(event_log_path, day=target_day):
        ts = row.get("ts") or (row.get("payload") or {}).get("ts")
        day_rows.append({**row, "_day": _utc_day(ts)})
    try:
        record_raw_input(
            run_id=reporter_run_id,
            agent="reporter",
            stage="post_run_analysis",
            raw_input={
                "target_day": target_day,
                "event_log_path": str(event_log_path),
                "day_row_count": int(len(day_rows)),
                "rapid_cycle_threshold_sec": int(rapid_cycle_threshold_sec),
                "reports_root": str(root),
            },
            decision_link={"stage": "reporter_analysis_start"},
        )
    except Exception:
        pass

    trade_md, trade_js, trade_obj = generate_trade_explain_report(
        event_log_path,
        official_trade_explain_report_dir(canonical_reports_root),
        day=target_day,
        max_executions=300,
        max_sell_pairs=300,
    )
    op_md, op_js = generate_operator_daily_summary(
        event_log_path,
        root,
        day=target_day,
        metrics_report_dir=root / "metrics",
        m30_post_golive_dir=root / "milestones" / "m30_post_golive",
        m30_golive_dir=root / "milestones" / "m30_golive",
        m31_slo_incident_dir=root / "m31_slo_incident",
    )
    manual_dir = root / "dev" / "manual"
    ds_md = manual_dir / "decision_story" / f"decision_story_{target_day}.md"
    rc_md = manual_dir / "run_cards" / f"run_cards_{target_day}.md"
    ds_obj: Dict[str, Any] = {"story_total": 0, "generated": False}
    rc_obj: Dict[str, Any] = {"card_total": 0, "generated": False}
    if bool(generate_decision_story):
        ds_md, ds_obj = generate_decision_story_report(
            event_log_path,
            manual_dir / "decision_story",
            day=target_day,
        )
        ds_obj = {**dict(ds_obj or {}), "generated": True}
    if bool(generate_run_cards):
        rc_md, rc_obj = generate_run_card_report(
            event_log_path,
            manual_dir / "run_cards",
            day=target_day,
        )
        rc_obj = {**dict(rc_obj or {}), "generated": True}

    op_obj = _read_json(op_js)
    trade_decision = _build_trade_decision_summaries(trade_obj)
    intent_flow = _build_intent_flow_analysis(
        day_rows=day_rows,
        intents_path=intents_path,
        day=target_day,
        operator_summary_obj=op_obj,
    )
    sections = _analysis_projection.build_analysis_sections(
        day_rows=day_rows,
        trade_obj=trade_obj,
        trade_decision=trade_decision,
        intent_flow=intent_flow,
        target_day=target_day,
        rapid_cycle_threshold_sec=rapid_cycle_threshold_sec,
        facade=_r3_sys.modules[__name__],
    )
    daily_operator = _analysis_projection.build_daily_operator_report(
        op_obj=op_obj, market_context=sections["market_context"], incident=sections["incident"],
        facade=_r3_sys.modules[__name__],
    )
    js_path = report_dir / f"reporter_analysis_{target_day}.json"
    md_path = report_dir / f"reporter_analysis_{target_day}.md"

    out = _analysis_projection.build_base_report(
        target_day=target_day,
        trade_decision=trade_decision,
        intent_flow=intent_flow,
        daily_operator=daily_operator,
        **sections,
        trade_js=trade_js,
        trade_md=trade_md,
        op_js=op_js,
        op_md=op_md,
        generate_decision_story=generate_decision_story,
        generate_run_cards=generate_run_cards,
        ds_md=ds_md,
        rc_md=rc_md,
        path_exists=lambda p: p.exists(),
        ds_obj=ds_obj,
        rc_obj=rc_obj,
        js_path=js_path,
        md_path=md_path,
        facade=_r3_sys.modules[__name__],
    )

    try:
        ai_review = build_ai_reporter_review(
            day=target_day,
            reporter_output=out,
            enabled=ai_review_enabled,
            model=ai_review_model,
            temperature=ai_review_temperature,
            max_tokens=max(256, int(ai_review_max_tokens)),
        )
    except Exception as e:
        ai_review = _analysis_projection.ai_review_error_payload(e, enabled=ai_review_enabled, model=ai_review_model)
    _analysis_projection.apply_ai_review_projection(out, ai_review, facade=_r3_sys.modules[__name__])
    try:
        memory_record = save_strategy_feedback(run_id=reporter_run_id, reporter_output=out)
        memory_meta = (
            memory_record.get("_strategy_memory_meta")
            if isinstance(memory_record.get("_strategy_memory_meta"), dict)
            else {}
        )
        out["strategy_memory_record"] = {
            "strategy_memory_path": str(memory_meta.get("strategy_memory_path") or resolve_strategy_memory_path()),
            "strategy_memory_daily_dir": str(resolve_strategy_memory_daily_dir()),
            "daily_summary_path": str(memory_meta.get("daily_summary_path") or ""),
            "storage_mode": str(memory_meta.get("storage_mode") or "append_jsonl_with_daily_latest"),
            "run_id": str(memory_record.get("run_id") or reporter_run_id),
            "timestamp": str(memory_record.get("timestamp") or ""),
            "feedback_window_day": target_day,
        }
    except Exception as exc:
        out["strategy_memory_record"] = {
            "strategy_memory_path": str(resolve_strategy_memory_path()),
            "strategy_memory_daily_dir": str(resolve_strategy_memory_daily_dir()),
            "daily_summary_path": "",
            "storage_mode": "append_jsonl_with_daily_latest",
            "run_id": str(reporter_run_id),
            "timestamp": "",
            "error": f"strategy_memory_save_failed:{exc}",
        }
    try:
        record_decision_bridge(
            run_id=reporter_run_id,
            agent="reporter",
            stage="post_run_analysis",
            raw_input={
                "source_reports": dict(out.get("source_reports") or {}),
                "report_focus_targets": list(out.get("report_focus_targets") or []),
            },
            parsed_output={
                "trade_summary": dict(out.get("trade_summary") or {}),
                "strategy_frame_summary": dict(out.get("strategy_frame_summary") or {}),
                "decision_trace_chain_summary": dict(out.get("decision_trace_chain_summary") or {}),
                "monitor_evaluation": dict(out.get("monitor_evaluation") or {}),
                "supervisor_activity": dict(out.get("supervisor_activity") or {}),
                "ai_review": dict(out.get("ai_review") or {}),
                "strategy_memory_record": dict(out.get("strategy_memory_record") or {}),
            },
            decision_link={
                "decision_chain": {
                    "theme": str(((out.get("strategist_evaluation") or {}).get("themes_proposed") or [""])[0] if isinstance((out.get("strategist_evaluation") or {}).get("themes_proposed"), list) and ((out.get("strategist_evaluation") or {}).get("themes_proposed") or []) else ""),
                    "scanner_selected": str(((out.get("scanner_evaluation") or {}).get("selected_symbol_top") or {}).get("symbol") or ""),
                    "entry_reason": str(((out.get("monitor_evaluation") or {}).get("monitor_reason_top") or {}).get("entry_signal") or ""),
                    "exit_reason": str(((out.get("monitor_evaluation") or {}).get("monitor_reason_top") or {}).get("confirmed_exit_signal") or ""),
                }
            },
        )
    except Exception:
        pass

    js_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_to_markdown(out), encoding="utf-8")
    return md_path, js_path, out
def _canonical_reports_root(path: Path) -> Path:
    candidate = Path(path)
    for parent in (candidate, *candidate.parents):
        if parent.name == "reports":
            return parent
    return candidate
