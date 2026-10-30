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
from libs.reporting import llm_artifacts_prompt_projection as _prompt_owner
from libs.reporting import llm_artifacts_status_projection as _status_owner
from libs.runtime.llm_report_classifier import find_llm_run_dir


def canonical_trade_day_root(reports_root: Path, day: str) -> Path:
    return Path(reports_root) / "trades" / str(day or "").strip()


def iter_trade_dirs(trade_day_root: Path) -> List[Path]:
    root = Path(trade_day_root)
    if not root.exists() or not root.is_dir():
        return []
    found: Dict[str, Path] = {}
    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        name = str(path.name or "").strip()
        if name in {"reports", "brief", "ai_trade_report", "lifecycle", "strategist", "evidence"}:
            trade_root = path.parent
        else:
            trade_root = path
        trade_name = str(trade_root.name or "").strip()
        if not trade_name.startswith("TRD_") and not (
            (path / "lifecycle_bundle.json").exists()
            or (path / "aggregated_execution_bundle.json").exists()
            or (path / "trade_lifecycle.json").exists()
        ):
            continue
        found[str(trade_root.resolve())] = trade_root
    return sorted(found.values(), key=lambda item: (item.parent.name, item.name))


def find_trade_dir(trade_day_root: Path, trade_id: str) -> Path | None:
    normalized_trade_id = str(trade_id or "").strip()
    if not normalized_trade_id:
        return None
    root = Path(trade_day_root)
    direct = root / normalized_trade_id
    if direct.exists() and direct.is_dir():
        return direct
    for trade_dir in iter_trade_dirs(root):
        if trade_dir.name == normalized_trade_id:
            return trade_dir
    return None


def _repo_root_from_reports_root(reports_root: Path) -> Path:
    root = Path(reports_root)
    if root.name == "reports":
        return root.parent
    return root


def _looks_like_trade_day_dir(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    try:
        for child in path.iterdir():
            if not child.is_dir():
                continue
            if str(child.name or "").startswith("TRD_"):
                return True
            for grandchild in child.iterdir():
                if grandchild.is_dir() and str(grandchild.name or "").startswith("TRD_"):
                    return True
        return False
    except Exception:
        return False


def misplaced_trade_day_root(reports_root: Path, day: str) -> Path | None:
    normalized_day = str(day or "").strip()
    if not normalized_day:
        return None
    primary = canonical_trade_day_root(reports_root, normalized_day)
    repo_root = _repo_root_from_reports_root(reports_root)
    candidate = repo_root / normalized_day
    if candidate == primary:
        return None
    if not _looks_like_trade_day_dir(candidate):
        return None
    return candidate


def resolve_trade_day_root(reports_root: Path, day: str) -> Path:
    primary = canonical_trade_day_root(reports_root, day)
    if primary.exists():
        return primary
    fallback = misplaced_trade_day_root(reports_root, day)
    if fallback is not None:
        return fallback
    return primary


def iter_trade_day_roots(reports_root: Path) -> List[Path]:
    roots: List[Path] = []
    seen_days: set[str] = set()
    canonical_root = Path(reports_root) / "trades"
    if canonical_root.exists():
        for child in sorted(path for path in canonical_root.iterdir() if path.is_dir()):
            roots.append(child)
            seen_days.add(child.name)
    repo_root = _repo_root_from_reports_root(reports_root)
    for child in sorted(path for path in repo_root.iterdir() if path.is_dir()):
        if child.name in seen_days:
            continue
        if not _looks_like_trade_day_dir(child):
            continue
        roots.append(child)
    return roots


def list_misplaced_trade_day_roots(reports_root: Path) -> List[Path]:
    repo_root = _repo_root_from_reports_root(reports_root)
    canonical_root = Path(reports_root) / "trades"
    canonical_days = {
        child.name
        for child in canonical_root.iterdir()
        if canonical_root.exists() and child.is_dir()
    } if canonical_root.exists() else set()
    out: List[Path] = []
    for child in sorted(path for path in repo_root.iterdir() if path.is_dir()):
        if child.name in canonical_days:
            continue
        if not _looks_like_trade_day_dir(child):
            continue
        out.append(child)
    return out


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
    run_base = find_llm_run_dir(Path(reports_root), str(day or "").strip(), str(run_id or "").strip())
    base = run_base / str(component or "").strip()
    return {
        "base_dir": base,
        "prompt_json": base / "prompt.json",
        "response_json": base / "response.json",
        "meta_json": base / "meta.json",
    }


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
    normalized_day = str(day or "").strip()
    normalized_trade_id = str(trade_id or "").strip()
    trade_day_root = (
        resolve_trade_day_root(reports_root, normalized_day)
        if prefer_existing_day_root
        else canonical_trade_day_root(reports_root, normalized_day)
    )
    existing_trade_root = find_trade_dir(trade_day_root, normalized_trade_id)
    if existing_trade_root is not None:
        trade_root = existing_trade_root
    else:
        bucket = str(time_bucket or "").strip()
        if bucket:
            trade_root = trade_day_root / bucket / normalized_trade_id
        else:
            trade_root = trade_day_root / normalized_trade_id
    legacy_root = reports_root / "trades" / normalized_day[:4] / normalized_day[5:7] / normalized_trade_id
    # Phase 3 primary structure (operator-facing):
    # reports/trades/<day>/<trade_id>/
    #   lifecycle_bundle.json, entry.json, hold.json, exit.json
    #   evidence/*.json
    #   reports/*.json|md
    reports_dir = trade_root / "reports"
    evidence_dir = trade_root / "evidence"
    lifecycle_bundle_json = trade_root / "lifecycle_bundle.json"
    entry_json = trade_root / "entry.json"
    hold_json = trade_root / "hold.json"
    exit_json = trade_root / "exit.json"
    commander_evidence_json = evidence_dir / "commander_evidence.json"
    monitor_evidence_json = evidence_dir / "monitor_evidence.json"

    # Legacy normalized layout (read fallback only).
    legacy_normalized_strategist_dir = trade_root / "strategist"
    legacy_normalized_ai_report_dir = trade_root / "ai_trade_report"
    legacy_normalized_lifecycle_dir = trade_root / "lifecycle"
    return {
        "trade_root": trade_root,
        "legacy_trade_root": legacy_root,
        "reports_dir": reports_dir,
        "evidence_dir": evidence_dir,
        "strategist_dir": reports_dir,
        "ai_trade_report_dir": reports_dir,
        "brief_dir": reports_dir,
        "lifecycle_dir": trade_root,
        "lifecycle_bundle_json": lifecycle_bundle_json,
        "entry_json": entry_json,
        "hold_json": hold_json,
        "exit_json": exit_json,
        # Compact trade-scoped LLM status artifacts (no raw body content).
        "strategist_llm_response_json": reports_dir / "strategist_llm_response.json",
        "strategist_summary_md": reports_dir / "strategist_summary.md",
        "strategist_summary_json": reports_dir / "strategist_summary.json",
        "ai_trade_report_llm_response_json": reports_dir / "ai_trade_report_llm_response.json",
        "brief_llm_response_json": reports_dir / "brief_llm_response.json",
        # Deprecated intermediate artifacts (no forward writes in Phase 3).
        "strategist_input_json": trade_root / "strategist_input.json",
        "strategist_compact_input_json": trade_root / "strategist_compact_input.json",
        "ai_trade_report_input_json": trade_root / "ai_trade_report_input.json",
        "ai_trade_report_compact_input_json": trade_root / "ai_trade_report_compact_input.json",
        "brief_input_json": trade_root / "brief_input.json",
        "brief_compact_input_json": trade_root / "brief_compact_input.json",
        # Operator-facing summary reports.
        "ai_trade_report_json": reports_dir / "ai_trade_report.json",
        "ai_trade_report_md": reports_dir / "ai_trade_report.md",
        "ai_trade_summary_input_json": reports_dir / "ai_trade_summary_input.json",
        "ai_trade_summary_json": reports_dir / "ai_trade_summary.json",
        "ai_trade_summary_md": reports_dir / "ai_trade_summary.md",
        "ai_trade_summary_llm_response_json": reports_dir / "ai_trade_summary_llm_response.json",
        "brief_json": reports_dir / "operator_brief.json",
        "brief_md": reports_dir / "operator_brief.md",
        # Deprecated compatibility files (read fallback only).
        "trade_lifecycle_json": trade_root / "trade_lifecycle.json",
        "aggregated_execution_bundle_json": trade_root / "aggregated_execution_bundle.json",
        # Evidence set.
        "strategist_evidence_json": evidence_dir / "strategist_evidence.json",
        "scanner_evidence_json": evidence_dir / "scanner_evidence.json",
        "monitor_evidence_json": monitor_evidence_json,
        "monitor_timeline_json": monitor_evidence_json,
        "commander_evidence_json": commander_evidence_json,
        "trade_provenance_json": trade_root / "_provenance.json",
        "trade_health_json": trade_root / "_health.json",
        "trade_artifact_links_json": trade_root / "_artifact_links.json",
        # Legacy normalized read fallbacks.
        "legacy_normalized_strategist_llm_response_json": legacy_normalized_strategist_dir / "strategist_llm_response.json",
        "legacy_normalized_ai_trade_report_input_json": legacy_normalized_ai_report_dir / "ai_trade_report_input.json",
        "legacy_normalized_ai_trade_report_compact_input_json": legacy_normalized_ai_report_dir / "ai_trade_report_compact_input.json",
        "legacy_normalized_ai_trade_report_json": legacy_normalized_ai_report_dir / "ai_trade_report.json",
        "legacy_normalized_ai_trade_report_md": legacy_normalized_ai_report_dir / "ai_trade_report.md",
        "legacy_normalized_ai_trade_report_llm_response_json": legacy_normalized_ai_report_dir / "ai_trade_report_llm_response.json",
        "legacy_normalized_trade_lifecycle_json": legacy_normalized_lifecycle_dir / "trade_lifecycle.json",
        "legacy_normalized_aggregated_execution_bundle_json": legacy_normalized_lifecycle_dir / "aggregated_execution_bundle.json",
        "legacy_normalized_strategist_evidence_json": evidence_dir / "strategist_evidence.json",
        "legacy_normalized_scanner_evidence_json": evidence_dir / "scanner_evidence.json",
        "legacy_normalized_monitor_timeline_json": evidence_dir / "monitor_timeline.json",
        "legacy_trade_story_input_json": legacy_root / "trade_story_input.json",
        "legacy_trade_report_json": legacy_root / "trade_report.json",
        "legacy_trade_report_md": legacy_root / "trade_report.md",
        "legacy_trade_lifecycle_json": legacy_root / "trade_lifecycle.json",
        "legacy_aggregated_execution_bundle_json": legacy_root / "aggregated_execution_bundle.json",
    }


def operator_summary_artifact_root(reports_root: Path) -> Path:
    """Canonical operator-facing report root.

    Passing either `reports` or `reports/operator_summary` should resolve to
    the same active operator-summary surface without double nesting.
    """
    root = Path(reports_root)
    if root.name == "operator_summary":
        return root
    if root.name in {"daily", "weekly", "monthly", "symbols"} and root.parent.name == "operator_summary":
        return root.parent
    return root / "operator_summary"


def daily_artifact_paths(reports_root: Path, day: str) -> Dict[str, Path]:
    """Canonical daily reporting paths under reports/operator_summary/daily/YYYY-MM-DD/."""
    normalized_day = str(day or "").strip()
    operator_root = operator_summary_artifact_root(reports_root)
    daily_root = operator_root / "daily" / normalized_day
    return {
        "root_dir": daily_root,
        "daily_root": daily_root,
        "daily_report_json": daily_root / "daily_report.json",
        "daily_report_md": daily_root / "daily_report.md",
        "daily_summary_json": daily_root / "daily_summary.json",
        "daily_summary_md": daily_root / "daily_summary.md",
        "daily_report_llm_response_json": daily_root / "daily_report_llm_response.json",
        "operator_summary_json": daily_root / "operator_summary.json",
        "operator_summary_md": daily_root / "operator_summary.md",
        "trade_index_json": daily_root / "trade_index.json",
        "legacy_daily_json": operator_root / "daily" / f"daily_{normalized_day}.json",
        "legacy_daily_md": operator_root / "daily" / f"daily_{normalized_day}.md",
        "root_daily_json": operator_root / f"daily_{normalized_day}.json",
        "root_daily_md": operator_root / f"daily_{normalized_day}.md",
    }


def symbol_artifact_paths(reports_root: Path, symbol: str) -> Dict[str, Path]:
    """Canonical symbol-history reporting paths under reports/operator_summary/symbols/<SYMBOL>/."""
    normalized_symbol = str(symbol or "").strip().upper()
    symbol_root = operator_summary_artifact_root(reports_root) / "symbols" / normalized_symbol
    return {
        "root_dir": symbol_root,
        "symbol_trade_report_json": symbol_root / "symbol_trade_report.json",
        "symbol_trade_report_md": symbol_root / "symbol_trade_report.md",
        "symbol_summary_json": symbol_root / "symbol_summary.json",
        "symbol_summary_md": symbol_root / "symbol_summary.md",
        "symbol_memory_json": symbol_root / "symbol_memory.json",
        "trade_history_json": symbol_root / "trade_history.json",
        "daily_index_json": symbol_root / "daily_index.json",
        "latest_snapshot_json": symbol_root / "latest_snapshot.json",
    }


def weekly_artifact_paths(reports_root: Path, week: str) -> Dict[str, Path]:
    """Canonical operator weekly summary paths under reports/operator_summary/weekly/YYYY-Www/."""
    normalized_week = str(week or "").strip()
    weekly_root = operator_summary_artifact_root(reports_root) / "weekly" / normalized_week
    return {
        "root_dir": weekly_root,
        "weekly_root": weekly_root,
        "weekly_summary_json": weekly_root / "weekly_summary.json",
        "weekly_summary_md": weekly_root / "weekly_summary.md",
    }


def monthly_artifact_paths(reports_root: Path, month: str) -> Dict[str, Path]:
    """Canonical operator monthly summary paths under reports/operator_summary/monthly/YYYY-MM/."""
    normalized_month = str(month or "").strip()
    monthly_root = operator_summary_artifact_root(reports_root) / "monthly" / normalized_month
    return {
        "root_dir": monthly_root,
        "monthly_root": monthly_root,
        "monthly_summary_json": monthly_root / "monthly_summary.json",
        "monthly_summary_md": monthly_root / "monthly_summary.md",
    }
