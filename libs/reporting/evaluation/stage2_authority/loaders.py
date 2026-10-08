from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from libs.reporting.json_array_stream import iter_json_array


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return dict(value) if isinstance(value, Mapping) else {}


_STAGE2_WINDOW_KEYS = ("decision_id", "run_id", "commander_final", "decision_epoch", "generated_at")


def load_q9_windows(reports_root: Path, start: str, end: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    root = Path(reports_root) / "operator_summary" / "daily"
    if not root.exists():
        return result
    for day_dir in sorted(root.iterdir()):
        if not day_dir.is_dir() or not (start <= day_dir.name <= end):
            continue
        # Streamed and reduced to the window fields stage2_authority.builder reads
        # (decision_id, run_id, commander_final, decision_epoch, generated_at, _day): the file
        # is ~120 MB per day and holding every full window was a large part of the closeout OOM.
        day_rows: dict[str, dict[str, Any]] = {}
        try:
            for raw in iter_json_array(day_dir / "q9_decision_windows.json", "windows"):
                if not isinstance(raw, Mapping):
                    continue
                decision_id = str(raw.get("decision_id") or "").strip()
                if decision_id:
                    row = {key: raw[key] for key in _STAGE2_WINDOW_KEYS if key in raw}
                    row["_day"] = day_dir.name
                    day_rows[decision_id] = row
        except ValueError:
            day_rows = {}  # unreadable file == no windows for that day (as _read_json -> {} gave)
        result.update(day_rows)
    return result


def _parse_response_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    text = str(payload.get("response_text") or "").strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
    except Exception:
        return {}
    return dict(parsed) if isinstance(parsed, Mapping) else {}


def load_stage2_responses(reports_root: Path, start: str, end: str) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    root = Path(reports_root) / "llm"
    if not root.exists():
        return result
    for day_dir in sorted(root.iterdir()):
        if not day_dir.is_dir() or not (start <= day_dir.name <= end):
            continue
        for path in day_dir.glob("**/strategist_stage2_selected_symbol/response.json"):
            payload = _read_json(path)
            run_id = str(payload.get("run_id") or "").strip()
            if not run_id:
                continue
            parsed = _parse_response_payload(payload)
            if not parsed:
                continue
            row = {
                "day": day_dir.name,
                "run_id": run_id,
                "saved_at": str(payload.get("saved_at") or ""),
                "artifact_path": str(path),
                "parsed": parsed,
            }
            key = (day_dir.name, run_id)
            current = result.get(key)
            if current is None or row["saved_at"] >= str(current.get("saved_at") or ""):
                result[key] = row
    return result
