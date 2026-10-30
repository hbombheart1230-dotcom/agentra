from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from libs.reporting.event_log_reader import iter_jsonl_events
from libs.reporting.llm_artifacts import daily_artifact_paths
from libs.reporting.narrative_axes import narrative_axis_policy
from libs.reporting.operator_visibility import (
    build_operator_daily_summary_payload,
    build_operator_summary_snapshot_from_payload,
)
from libs.reporting.operator_period_summary import generate_operator_daily_summary_artifact
from libs.reporting.operator_period_summary import build_residual_positions_payload
from libs.reporting.report_metadata import (
    build_data_freshness,
    build_route_provenance,
)
from libs.reporting.daily_report_runtime.build_model import (
    build_basic_daily_event_summary as _build_basic_daily_event_summary,
    build_event_rows as _build_event_rows,
    build_no_event_daily_payload as _build_no_event_daily_payload,
    enrich_daily_summary_payload as _enrich_daily_summary_payload,
)
from libs.reporting.daily_report_runtime.freshness import (
    build_report_freshness as _build_report_freshness,
    build_snapshot_freshness as _build_snapshot_freshness,
    utc_now_iso as _utc_now_iso,
)
from libs.reporting.daily_report_runtime.markdown import (
    render_daily_markdown as _render_daily_markdown,
    render_no_event_daily_markdown as _render_no_event_daily_markdown,
)
from libs.reporting.daily_report_runtime.symbol_refresh import (
    expected_trade_ids_by_symbol as _expected_trade_ids_by_symbol,
    read_json_list as _read_json_list,
    refresh_symbol_reports as _refresh_symbol_reports,
    symbol_report_is_current as _symbol_report_is_current,
    symbol_report_mode as _symbol_report_mode,
)
from libs.reporting.broker_alignment import build_broker_alignment_report as _build_broker_alignment_report
from libs.reporting.report_source_helpers import build_policy_surface_quality_snapshot
from libs.reporting.symbol_trade_report import build_daily_trade_index
from libs.reporting.symbol_trade_report import collect_symbols_for_day
from libs.core.symbols import normalize_symbol
from libs.reporting import daily_report_generator_read_projection as _read_owner
from libs.reporting import daily_report_generator_trade_projection as _trade_owner


def _iter_events(path: Path) -> Iterable[Dict[str, Any]]:
    return _read_owner._iter_events(path, facade=sys.modules[__name__])


def _load_operator_summary_snapshot(events_path: Path, out_dir: Path, day: str) -> Dict[str, Any]:
    paths = daily_artifact_paths(out_dir, day)
    payload = build_operator_daily_summary_payload(
        events_path,
        out_dir,
        day=day,
        metrics_report_dir=out_dir / "metrics",
        m30_post_golive_dir=out_dir / "milestones" / "m30_post_golive",
        m30_golive_dir=out_dir / "milestones" / "m30_golive",
        m31_slo_incident_dir=out_dir / "m31_slo_incident",
    )
    snapshot = build_operator_summary_snapshot_from_payload(payload)
    snapshot["report_json_path"] = str(paths["operator_summary_json"])
    snapshot["report_md_path"] = str(paths["operator_summary_md"])
    return snapshot


def _load_policy_surface_quality_snapshot(events_path: Path, out_dir: Path, day: str) -> Dict[str, Any]:
    return build_policy_surface_quality_snapshot(events_path, out_dir, day)


def _find_trade_dir(reports_root: Path, day: str, trade_id: str) -> Path | None:
    return _read_owner._find_trade_dir(reports_root, day, trade_id)


def _broker_closed_symbols_from_alignment(broker_alignment: Dict[str, Any] | None) -> set[str]:
    return _trade_owner._broker_closed_symbols_from_alignment(broker_alignment, facade=sys.modules[__name__])


def _build_trade_report_integrity(
    reports_root: Path,
    day: str,
    trade_index: List[Dict[str, Any]],
    broker_alignment: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    missing: List[Dict[str, Any]] = []
    broker_closed_symbols = _broker_closed_symbols_from_alignment(broker_alignment)
    broker_closed_report_open: List[Dict[str, Any]] = []
    for item in trade_index:
        if not isinstance(item, dict):
            continue
        trade_id = str(item.get("trade_id") or "").strip()
        if not trade_id:
            continue
        symbol = normalize_symbol(item.get("symbol"), allow_test_symbols=True)
        lifecycle_status = str(
            item.get("status")
            or item.get("trade_lifecycle_status")
            or item.get("lifecycle_status")
            or ""
        ).strip().lower()
        trade_dir = _find_trade_dir(reports_root, day, trade_id)
        reports_dir = trade_dir / "reports" if trade_dir else None
        checks = {
            "ai_trade_summary_input_json": bool(reports_dir and (reports_dir / "ai_trade_summary_input.json").exists()),
            "ai_trade_summary_json": bool(reports_dir and (reports_dir / "ai_trade_summary.json").exists()),
            "ai_trade_summary_md": bool(reports_dir and (reports_dir / "ai_trade_summary.md").exists()),
        }
        row = {
            "trade_id": trade_id,
            "symbol": symbol or str(item.get("symbol") or ""),
            "lifecycle_status": lifecycle_status,
            "trade_dir": str(trade_dir) if trade_dir else "",
            **checks,
        }
        rows.append(row)
        if symbol and symbol in broker_closed_symbols and lifecycle_status not in ("closed", "done", "completed"):
            broker_closed_report_open.append(
                {
                    "trade_id": trade_id,
                    "symbol": symbol,
                    "lifecycle_status": lifecycle_status or "unknown",
                    "issue": "broker_day_trade_closed_but_report_open",
                }
            )
        if not all(checks.values()):
            missing.append(
                {
                    "trade_id": trade_id,
                    "symbol": row["symbol"],
                    "missing": [key for key, value in checks.items() if not value],
                }
            )
    status = "ok"
    if missing:
        status = "missing_reports"
    if broker_closed_report_open:
        status = "broker_lifecycle_mismatch" if not missing else "missing_reports_and_broker_lifecycle_mismatch"
    return {
        "schema_version": "trade_report_integrity.v1",
        "expected_trade_count": len([x for x in trade_index if isinstance(x, dict) and str(x.get("trade_id") or "").strip()]),
        "checked_trade_count": len(rows),
        "summary_md_count": sum(1 for row in rows if row.get("ai_trade_summary_md")),
        "summary_json_count": sum(1 for row in rows if row.get("ai_trade_summary_json")),
        "summary_input_count": sum(1 for row in rows if row.get("ai_trade_summary_input_json")),
        "missing_count": len(missing),
        "broker_closed_report_open_count": len(broker_closed_report_open),
        "status": status,
        "missing": missing,
        "broker_closed_report_open": broker_closed_report_open,
    }


def _render_residual_positions_markdown(residual: Dict[str, Any]) -> List[str]:
    return _trade_owner._render_residual_positions_markdown(residual)

def generate_daily_report(events_path: Path, out_dir: Path, day: str | None = None) -> Tuple[Path, Path]:
    """Generate a daily markdown + json summary from events.jsonl.

    Notes:
      - Day bucketing uses UTC for deterministic tests and consistent reporting.
      - If `day` is provided, only events matching that UTC day are included.
    """
    out_dir = out_dir.parent if out_dir.name == "daily" else out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    event_rows = iter_jsonl_events(events_path, day=day) if day else _iter_events(events_path)
    rows = _build_event_rows(event_rows)
    if not rows:
        day = day or date.today().isoformat()
        paths = daily_artifact_paths(out_dir, day)
        md_path = paths["daily_report_md"]
        js_path = paths["daily_report_json"]
        trade_index = build_daily_trade_index(out_dir, day)
        symbols_for_day = collect_symbols_for_day(events_path, out_dir, day, trade_index=trade_index)
        symbol_report_refresh = _refresh_symbol_reports(
            events_path=events_path,
            reports_root=out_dir,
            symbols=symbols_for_day,
            trade_index=trade_index,
        )
        generated_symbol_reports = list(symbol_report_refresh.get("generated") or [])
        operator_summary_snapshot = _load_operator_summary_snapshot(events_path, out_dir, day)
        residual_positions = build_residual_positions_payload(reports_root=out_dir, day=day)
        broker_alignment = _build_broker_alignment_report(events_path, out_dir, day)
        trade_report_integrity = _build_trade_report_integrity(out_dir, day, trade_index, broker_alignment)
        report_freshness = {
            "generated_at": _utc_now_iso(),
            "source_run_count": 0,
            "latest_run_id": "",
            "latest_run_ts": "",
        }
        operator_snapshot_freshness = _build_snapshot_freshness(
            snapshot=operator_summary_snapshot,
            source_freshness=report_freshness,
        )
        policy_surface_quality = _load_policy_surface_quality_snapshot(events_path, out_dir, day)
        payload = _build_no_event_daily_payload(
            day=day,
            report_freshness=report_freshness,
            data_freshness=build_data_freshness(
                generated_at=report_freshness["generated_at"],
                source_run_count=report_freshness["source_run_count"],
                latest_run_id=report_freshness["latest_run_id"],
                latest_run_ts=report_freshness["latest_run_ts"],
                stale=False,
            ),
            trade_index=trade_index,
            symbols_for_day=symbols_for_day,
            generated_symbol_reports=generated_symbol_reports,
            symbol_report_refresh=symbol_report_refresh,
            trade_report_integrity=trade_report_integrity,
            broker_alignment=broker_alignment,
            operator_summary_snapshot=operator_summary_snapshot,
            residual_positions=residual_positions,
            policy_surface_quality=policy_surface_quality,
            route_provenance=build_route_provenance(operator_summary_snapshot.get("route_summary") if isinstance(operator_summary_snapshot.get("route_summary"), dict) else {}),
            narrative_axis_policy=narrative_axis_policy(),
        )
        payload["operator_summary_snapshot_freshness"] = operator_snapshot_freshness
        md_text = _render_no_event_daily_markdown(
            day=day,
            payload=payload,
            operator_snapshot_freshness=operator_snapshot_freshness,
            render_residual_positions=_render_residual_positions_markdown,
        )
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(md_text, encoding="utf-8-sig", newline="\n")
        js_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        paths["trade_index_json"].write_text(json.dumps(trade_index, ensure_ascii=False, indent=2), encoding="utf-8")
        generate_operator_daily_summary_artifact(
            reports_root=out_dir,
            day=day,
            daily_report_payload=payload,
        )
        return md_path, js_path

    day = day or sorted({r["_day"] for r in rows})[-1]
    day_rows = [r for r in rows if r["_day"] == day]
    report_freshness = _build_report_freshness(day_rows)

    event_summary = _build_basic_daily_event_summary(day, day_rows)
    summary = dict(event_summary["summary"])
    stage_counter = event_summary["stage_counter"]
    actions = event_summary["actions"]
    approvals = int(event_summary["approvals"])
    blocks = int(event_summary["blocks"])
    trade_index = build_daily_trade_index(out_dir, day)
    symbols_for_day = collect_symbols_for_day(events_path, out_dir, day, trade_index=trade_index)
    symbol_report_refresh = _refresh_symbol_reports(
        events_path=events_path,
        reports_root=out_dir,
        symbols=symbols_for_day,
        trade_index=trade_index,
    )
    generated_symbol_reports = list(symbol_report_refresh.get("generated") or [])
    operator_summary_snapshot = _load_operator_summary_snapshot(events_path, out_dir, day)
    residual_positions = build_residual_positions_payload(reports_root=out_dir, day=day)
    broker_alignment = _build_broker_alignment_report(events_path, out_dir, day)
    trade_report_integrity = _build_trade_report_integrity(out_dir, day, trade_index, broker_alignment)
    operator_summary_snapshot_freshness = _build_snapshot_freshness(
        snapshot=operator_summary_snapshot,
        source_freshness=report_freshness,
    )
    policy_surface_quality = _load_policy_surface_quality_snapshot(events_path, out_dir, day)
    summary = _enrich_daily_summary_payload(
        summary=summary,
        report_freshness=report_freshness,
        data_freshness=build_data_freshness(
            generated_at=report_freshness["generated_at"],
            source_run_count=report_freshness["source_run_count"],
            latest_run_id=report_freshness["latest_run_id"],
            latest_run_ts=report_freshness["latest_run_ts"],
            stale=False,
        ),
        trade_index=trade_index,
        symbols_for_day=symbols_for_day,
        generated_symbol_reports=generated_symbol_reports,
        symbol_report_refresh=symbol_report_refresh,
        trade_report_integrity=trade_report_integrity,
        broker_alignment=broker_alignment,
        operator_summary_snapshot=operator_summary_snapshot,
        residual_positions=residual_positions,
        operator_summary_snapshot_freshness=operator_summary_snapshot_freshness,
        policy_surface_quality=policy_surface_quality,
        route_provenance=build_route_provenance(operator_summary_snapshot.get("route_summary") if isinstance(operator_summary_snapshot.get("route_summary"), dict) else {}),
        narrative_axis_policy=narrative_axis_policy(),
    )

    md_text = _render_daily_markdown(
        day=day,
        summary=summary,
        operator_summary_snapshot_freshness=operator_summary_snapshot_freshness,
        approvals=approvals,
        blocks=blocks,
        symbols_for_day=symbols_for_day,
        actions=actions,
        stage_counter=stage_counter,
        render_residual_positions=_render_residual_positions_markdown,
    )

    paths = daily_artifact_paths(out_dir, day)
    md_path = paths["daily_report_md"]
    js_path = paths["daily_report_json"]
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md_text, encoding="utf-8-sig", newline="\n")
    js_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["trade_index_json"].write_text(json.dumps(trade_index, ensure_ascii=False, indent=2), encoding="utf-8")
    generate_operator_daily_summary_artifact(
        reports_root=out_dir,
        day=day,
        daily_report_payload=summary,
    )
    return md_path, js_path

def main() -> None:
    events_path = Path(os.getenv("EVENT_LOG_PATH", "./data/logs/events.jsonl"))
    out_dir = Path(os.getenv("REPORT_DIR", "./reports"))
    day = os.getenv("REPORT_DAY")  # optional YYYY-MM-DD (UTC)
    result = Reporter().generate_daily_report(
        event_log_path=events_path,
        reports_root=out_dir,
        day=day,
    )
    print(f"Wrote: {result.report_md_path}")
    print(f"Wrote: {result.report_json_path}")

if __name__ == "__main__":
    main()

