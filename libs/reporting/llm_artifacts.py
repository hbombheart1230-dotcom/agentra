from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from libs.reporting import llm_artifacts_attempt_projection as _attempt_owner
from libs.reporting import llm_artifacts_compact_projection as _compact_owner
from libs.reporting import llm_artifacts_hash_projection as _hash_owner
from libs.reporting import llm_artifacts_path_projection as _path_owner
from libs.reporting import llm_artifacts_prompt_projection as _prompt_owner
from libs.reporting import llm_artifacts_run_paths as _run_paths_owner
from libs.reporting import llm_artifacts_status_projection as _status_owner
from libs.reporting import llm_artifacts_trade_lookup as _lookup_owner
from libs.reporting import llm_artifacts_trade_path_projection as _trade_path_owner
from libs.runtime.llm_report_classifier import find_llm_run_dir


def canonical_trade_day_root(reports_root: Path, day: str) -> Path:
    return _path_owner.canonical_trade_day_root(reports_root, day)


def iter_trade_dirs(trade_day_root: Path) -> List[Path]:
    return _lookup_owner.iter_trade_dirs(trade_day_root)


def find_trade_dir(trade_day_root: Path, trade_id: str) -> Path | None:
    return _lookup_owner.find_trade_dir(trade_day_root, trade_id, facade=sys.modules[__name__])


def _repo_root_from_reports_root(reports_root: Path) -> Path:
    return _path_owner._repo_root_from_reports_root(reports_root)


def _looks_like_trade_day_dir(path: Path) -> bool:
    return _lookup_owner._looks_like_trade_day_dir(path)


def misplaced_trade_day_root(reports_root: Path, day: str) -> Path | None:
    return _lookup_owner.misplaced_trade_day_root(reports_root, day, facade=sys.modules[__name__])


def resolve_trade_day_root(reports_root: Path, day: str) -> Path:
    return _lookup_owner.resolve_trade_day_root(reports_root, day, facade=sys.modules[__name__])


def iter_trade_day_roots(reports_root: Path) -> List[Path]:
    return _lookup_owner.iter_trade_day_roots(reports_root, facade=sys.modules[__name__])


def list_misplaced_trade_day_roots(reports_root: Path) -> List[Path]:
    return _lookup_owner.list_misplaced_trade_day_roots(reports_root, facade=sys.modules[__name__])


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def split_prompt_messages(messages: Any) -> Tuple[str, str]:
    return _prompt_owner.split_prompt_messages(messages)


def split_prompt_text(prompt_text: Any) -> Tuple[str, str]:
    return _prompt_owner.split_prompt_text(prompt_text)


def normalize_llm_status(value: Any, *, default: str = "fallback") -> str:
    return _status_owner.normalize_llm_status(value, default=default)


def canonical_llm_status(value: Any, *, default: str = "fallback") -> str:
    return _status_owner.canonical_llm_status(value, default=default, facade=sys.modules[__name__])


def classify_llm_exception(exc: Exception) -> str:
    return _status_owner.classify_llm_exception(exc)


def make_attempt(
    *,
    step: str,
    messages: Any,
    raw_response_text: Any,
    parsed_output: Any,
    model: Any,
    provider: Any = "OpenRouter",
    latency_ms: Any = 0,
    status: Any = "ok",
    meta: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _attempt_owner.make_attempt(
        step=step,
        messages=messages,
        raw_response_text=raw_response_text,
        parsed_output=parsed_output,
        model=model,
        provider=provider,
        latency_ms=latency_ms,
        status=status,
        meta=meta,
        facade=sys.modules[__name__],
    )


def build_llm_response_artifact(
    *,
    component: str,
    run_id: Any,
    trade_id: Any = "",
    story_id: Any = "",
    day: Any = "",
    status: Any = "ok",
    attempts: List[Dict[str, Any]] | None = None,
    parsed_output: Any = None,
    model_info: Dict[str, Any] | None = None,
    latency_ms: Any = 0,
    meta: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _attempt_owner.build_llm_response_artifact(
        component=component,
        run_id=run_id,
        trade_id=trade_id,
        story_id=story_id,
        day=day,
        status=status,
        attempts=attempts,
        parsed_output=parsed_output,
        model_info=model_info,
        latency_ms=latency_ms,
        meta=meta,
        facade=sys.modules[__name__],
    )


def llm_artifact_paths(reports_root: Path, day: str, run_id: str, component: str) -> Dict[str, Path]:
    return _run_paths_owner.llm_artifact_paths(reports_root, day, run_id, component, facade=sys.modules[__name__])


def _json_stable_text(payload: Any) -> str:
    return _hash_owner.json_stable_text(payload, facade=sys.modules[__name__])


def _sha256_text(text: Any) -> str:
    return _hash_owner.sha256_text(text, facade=sys.modules[__name__])


def persist_llm_artifact_refs(
    *,
    artifact: Dict[str, Any],
    reports_root: Path,
    day: str,
    run_id: str,
    component: str,
) -> Dict[str, Any]:
    src = dict(artifact or {})
    if not src:
        return {}
    paths = llm_artifact_paths(Path(reports_root), str(day or "").strip(), str(run_id or "").strip(), str(component or "").strip())
    prompt_payload = {
        "schema_version": "llm_prompt_raw.v1",
        "component": str(component or "").strip(),
        "run_id": str(run_id or ""),
        "day": str(day or ""),
        "saved_at": utc_now_iso(),
        "stage": str(src.get("stage") or ""),
        "stage_index": src.get("stage_index"),
        "stage_name": str(src.get("stage_name") or ""),
        "call_kind": str(src.get("call_kind") or ""),
        "stage_component": str(src.get("stage_component") or ""),
        "system_prompt": str(src.get("system_prompt") or ""),
        "user_prompt": str(src.get("user_prompt") or ""),
        "attempts": [
            {
                "step": str(row.get("step") or ""),
                "system_prompt": str(row.get("system_prompt") or ""),
                "user_prompt": str(row.get("user_prompt") or ""),
            }
            for row in list(src.get("attempts") or [])
            if isinstance(row, dict)
        ],
    }
    response_payload = {
        "schema_version": "llm_response_raw.v1",
        "component": str(component or "").strip(),
        "run_id": str(run_id or ""),
        "day": str(day or ""),
        "saved_at": utc_now_iso(),
        "status": str(src.get("status") or ""),
        "llm_status": str(src.get("llm_status") or src.get("status") or ""),
        "model": str(src.get("model") or ""),
        "provider": str((src.get("model_info") or {}).get("provider") or src.get("provider") or ""),
        "stage": str(src.get("stage") or ""),
        "stage_index": src.get("stage_index"),
        "stage_name": str(src.get("stage_name") or ""),
        "call_kind": str(src.get("call_kind") or ""),
        "stage_component": str(src.get("stage_component") or ""),
        "raw_response_text": str(src.get("raw_response_text") or ""),
        "parsed_output": src.get("parsed_output") if isinstance(src.get("parsed_output"), (dict, list)) else {},
        "attempts": [
            {
                "step": str(row.get("step") or ""),
                "raw_response_text": str(row.get("raw_response_text") or ""),
                "status": str(row.get("status") or ""),
                "error": str(row.get("error") or ""),
            }
            for row in list(src.get("attempts") or [])
            if isinstance(row, dict)
        ],
    }
    prompt_text = _json_stable_text(prompt_payload)
    response_text = _json_stable_text(response_payload)
    prompt_hash = _sha256_text(prompt_text)
    response_hash = _sha256_text(response_text)
    meta_payload = {
        "schema_version": "llm_artifact_meta.v1",
        "component": str(component or "").strip(),
        "run_id": str(run_id or ""),
        "day": str(day or ""),
        "saved_at": utc_now_iso(),
        "status": str(src.get("status") or ""),
        "llm_status": str(src.get("llm_status") or ""),
        "model": str(src.get("model") or ""),
        "provider": str((src.get("model_info") or {}).get("provider") or src.get("provider") or ""),
        "latency_ms": int(float(src.get("latency_ms") or 0)),
        "token_usage": dict(src.get("token_usage") or {}) if isinstance(src.get("token_usage"), dict) else {},
        "response_truncated": bool(src.get("response_truncated")),
        "repair_used": bool(src.get("repair_used")),
        "llm_error_type": str(src.get("llm_error_type") or ""),
        "stage": str(src.get("stage") or ""),
        "stage_index": src.get("stage_index"),
        "stage_name": str(src.get("stage_name") or ""),
        "call_kind": str(src.get("call_kind") or ""),
        "stage_component": str(src.get("stage_component") or ""),
        "prompt_ref": str(paths["prompt_json"]),
        "response_ref": str(paths["response_json"]),
        "prompt_hash": prompt_hash,
        "response_hash": response_hash,
    }

    write_json(paths["prompt_json"], prompt_payload)
    write_json(paths["response_json"], response_payload)
    write_json(paths["meta_json"], meta_payload)
    summary_refs: Dict[str, str] = {}
    component_key = str(component or "").strip()
    if component_key == "strategist" or component_key.startswith("strategist_stage"):
        try:
            from libs.reporting.strategist_llm_summary import generate_strategist_llm_summary

            summary_md, summary_json, _summary_payload = generate_strategist_llm_summary(paths["response_json"])
            summary_refs = {
                "strategist_summary_md_ref": str(summary_md),
                "strategist_summary_json_ref": str(summary_json),
            }
        except Exception:
            summary_refs = {}

    compact = dict(src)
    compact.pop("system_prompt", None)
    compact.pop("user_prompt", None)
    compact.pop("raw_response_text", None)
    compact_attempts: List[Dict[str, Any]] = []
    for row in list(compact.get("attempts") or []):
        if not isinstance(row, dict):
            continue
        compact_attempts.append(
            {
                "step": str(row.get("step") or ""),
                "status": str(row.get("status") or ""),
                "latency_ms": int(float(row.get("latency_ms") or 0)),
                "error": str(row.get("error") or ""),
            }
        )
    compact["attempts"] = compact_attempts
    compact["prompt_ref"] = str(paths["prompt_json"])
    compact["response_ref"] = str(paths["response_json"])
    compact["llm_meta_ref"] = str(paths["meta_json"])
    compact.update(summary_refs)
    compact["prompt_hash"] = prompt_hash
    compact["response_hash"] = response_hash
    compact["status"] = str(src.get("status") or "")
    compact["llm_status"] = str(src.get("llm_status") or src.get("status") or "")
    return compact


def write_json(path: Path, payload: Dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(text or ""), encoding="utf-8")
    return path


def build_compact_input_artifact(
    *,
    component: str,
    run_id: Any,
    trade_id: Any = "",
    story_id: Any = "",
    day: Any = "",
    source_artifact_path: Any = "",
    source_input: Any = None,
    compact_input: Any = None,
) -> Dict[str, Any]:
    return _compact_owner.build_compact_input_artifact(
        component=component,
        run_id=run_id,
        trade_id=trade_id,
        story_id=story_id,
        day=day,
        source_artifact_path=source_artifact_path,
        source_input=source_input,
        compact_input=compact_input,
        facade=sys.modules[__name__],
    )


def trade_artifact_paths(
    reports_root: Path,
    day: str,
    trade_id: str,
    *,
    prefer_existing_day_root: bool = False,
    time_bucket: str | None = None,
) -> Dict[str, Path]:
    return _trade_path_owner.trade_artifact_paths(
        reports_root,
        day,
        trade_id,
        prefer_existing_day_root=prefer_existing_day_root,
        time_bucket=time_bucket,
        facade=sys.modules[__name__],
    )


def operator_summary_artifact_root(reports_root: Path) -> Path:
    """Canonical operator-facing report root.

    Passing either `reports` or `reports/operator_summary` should resolve to
    the same active operator-summary surface without double nesting.
    """
    return _path_owner.operator_summary_artifact_root(reports_root)


def daily_artifact_paths(reports_root: Path, day: str) -> Dict[str, Path]:
    """Canonical daily reporting paths under reports/operator_summary/daily/YYYY-MM-DD/."""
    return _path_owner.daily_artifact_paths(reports_root, day, facade=sys.modules[__name__])


def symbol_artifact_paths(reports_root: Path, symbol: str) -> Dict[str, Path]:
    """Canonical symbol-history reporting paths under reports/operator_summary/symbols/<SYMBOL>/."""
    return _path_owner.symbol_artifact_paths(reports_root, symbol, facade=sys.modules[__name__])


def weekly_artifact_paths(reports_root: Path, week: str) -> Dict[str, Path]:
    """Canonical operator weekly summary paths under reports/operator_summary/weekly/YYYY-Www/."""
    return _path_owner.weekly_artifact_paths(reports_root, week, facade=sys.modules[__name__])


def monthly_artifact_paths(reports_root: Path, month: str) -> Dict[str, Path]:
    """Canonical operator monthly summary paths under reports/operator_summary/monthly/YYYY-MM/."""
    return _path_owner.monthly_artifact_paths(reports_root, month, facade=sys.modules[__name__])
