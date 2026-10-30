from pathlib import Path
from typing import Any, Dict

def _resolve_trade_context(reports_root: Path, day: str, trade_id: str, *, facade) -> Dict[str, Any]:
    trade_paths = facade.trade_artifact_paths(reports_root, day, trade_id)
    entry_payload = facade._read_json(trade_paths["entry_json"])
    exit_payload = facade._read_json(trade_paths["exit_json"])
    hold_payload = facade._read_json(trade_paths["hold_json"])
    lifecycle_bundle = facade._read_json(trade_paths["lifecycle_bundle_json"])
    story_input = facade._read_json(trade_paths["ai_trade_report_input_json"])
    report = facade._read_json(trade_paths["ai_trade_report_json"])
    provenance = facade._read_json(trade_paths["trade_provenance_json"])
    health = facade._read_json(trade_paths["trade_health_json"])
    entry_run_id = str(
        entry_payload.get("run_id")
        or ((lifecycle_bundle.get("lifecycle") or {}).get("entry") or {}).get("run_id")
        or ""
    ).strip()
    exit_run_id = str(
        exit_payload.get("run_id")
        or ((lifecycle_bundle.get("lifecycle") or {}).get("exit") or {}).get("run_id")
        or lifecycle_bundle.get("run_id")
        or ""
    ).strip()
    target_run_id = exit_run_id or entry_run_id
    return {
        "trade_paths": trade_paths,
        "entry_payload": entry_payload,
        "exit_payload": exit_payload,
        "hold_payload": hold_payload,
        "lifecycle_bundle": lifecycle_bundle,
        "story_input": story_input,
        "report": report,
        "provenance": provenance,
        "health": health,
        "entry_run_id": entry_run_id,
        "exit_run_id": exit_run_id,
        "target_run_id": target_run_id,
    }
