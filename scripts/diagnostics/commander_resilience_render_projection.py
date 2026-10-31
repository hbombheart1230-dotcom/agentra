from pathlib import Path
from typing import Any, Dict, List


def _print_human(path: Path, rows: List[Dict[str, Any]], summary: Dict[str, Any], *, facade: Any) -> None:
    printer = getattr(facade, "print", print)
    printer("=== Commander Resilience Events ==="); printer(f"path={path}"); printer(f"total_matched={summary.get('total_matched')} shown={summary.get('shown')}")
    printer(f"cooldown_transition_total={summary.get('cooldown_transition_total')} intervention_total={summary.get('intervention_total')} error_total={summary.get('error_total')}")
    printer(f"latest_run_id={summary.get('latest_run_id')} latest_status={summary.get('latest_status')}")
    for rec in rows:
        ts, run_id, event = str(rec.get("ts") or ""), str(rec.get("run_id") or ""), str(rec.get("event") or "")
        payload = rec.get("payload") if isinstance(rec.get("payload"), dict) else {}; key = ""
        if event == "transition": key = f"transition={payload.get('transition')} status={payload.get('status')} reason={payload.get('reason')} cooldown_until_epoch={payload.get('cooldown_until_epoch')}"
        elif event == "resilience": key = f"reason={payload.get('reason')} incident_count={payload.get('incident_count')} incident_threshold={payload.get('incident_threshold')} cooldown_until_epoch={payload.get('cooldown_until_epoch')}"
        elif event == "intervention": key = f"type={payload.get('type')} at_epoch={payload.get('at_epoch')}"
        elif event == "error": key = f"error_type={payload.get('error_type')} error={payload.get('error')}"
        elif event == "end": key = f"status={payload.get('status')} path={payload.get('path')}"
        elif event == "route": key = f"mode={payload.get('mode')}"
        printer(f"{ts} run_id={run_id} event={event} {key}".strip())
