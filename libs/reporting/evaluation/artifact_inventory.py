from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from libs.reporting.json_array_stream import iter_json_array
from libs.reporting.quant_shadow_forward_outcomes import attach_forward_outcomes

from . import fast08_evidence_inventory as _ev


Q9_DECISION_SCHEMA = _ev.Q9_DECISION_SCHEMA
_KRX_SYMBOL_RE = _ev.KRX_SYMBOL_RE
_synthetic_identity = _ev.synthetic_identity
_regular_session_window = _ev.regular_session_window


def is_synthetic_evaluation_row(row: dict[str, Any]) -> bool:
    return _synthetic_identity(row)


def is_regular_session_evaluation_row(row: dict[str, Any]) -> bool:
    return _regular_session_window(row)


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def iter_trade_dirs(reports_root: Path, day: str) -> list[Path]:
    root = Path(reports_root) / "trades" / day
    if not root.exists():
        return []
    return sorted({path.parent for path in root.rglob("lifecycle_bundle.json")})


def _record(path: Path, *, required: bool) -> dict[str, Any]:
    exists = path.exists()
    payload = read_json(path) if exists and path.suffix.lower() == ".json" else {}
    return {
        "path": str(path),
        "required": required,
        "exists": exists,
        "size_bytes": path.stat().st_size if exists else 0,
        "modified_epoch": path.stat().st_mtime if exists else None,
        "schema_version": str(payload.get("schema_version") or ""),
        "evidence_status": str(payload.get("evidence_status") or ""),
        "forward_windows_complete": bool(payload.get("forward_windows_complete")),
        "missing_reason": "" if exists else "artifact_not_found",
    }


def _iter_shadow_payloads(reports_root: Path, day: str):
    """Yield each non-empty shadow payload of `day` one at a time, in file-name order.

    Streaming (rather than collecting a list) keeps only one parsed payload alive at a
    time; a trading day's full list was ~300 MiB of parsed objects and, loaded twice
    here, was a large part of the closeout peak that OOM-killed the 1 GiB container.
    """
    shadow_root = Path(reports_root).parent / "data" / "logs" / "quant_shadow_candidates" / day
    if not shadow_root.exists():
        return
    for shadow_path in sorted(shadow_root.glob("*.json")):
        if shadow_path.name == "latest.json":
            continue
        shadow = read_json(shadow_path)
        if shadow:
            yield shadow


def load_q9_pre_strategist_rows(reports_root: Path, day: str) -> list[dict[str, Any]]:
    pre_rows: list[dict[str, Any]] = []
    for shadow in _iter_shadow_payloads(reports_root, day):
        generated_at = str(shadow.get("generated_at") or "")
        for raw in shadow.get("q9_decision_candidates") or []:
            if (
                not isinstance(raw, dict)
                or str(raw.get("q9_decision_role") or "")
                != "P_SCANNER_PRE_STRATEGIST_UNIVERSE"
            ):
                continue
            row = dict(raw)
            row.setdefault("_payload_generated_at", generated_at)
            if _synthetic_identity(row) or not _regular_session_window(
                {"generated_at": generated_at}
            ):
                continue
            pre_rows.append(row)
    return pre_rows


def _load_forward_recovery_candles(
    reports_root: Path, day: str
) -> dict[str, list[dict[str, Any]]]:
    payload = read_json(
        Path(reports_root)
        / "evaluation"
        / "daily"
        / day
        / "q9_forward_recovery_candles.json"
    )
    by_symbol = payload.get("minute_rows_by_symbol")
    return {
        str(symbol): [dict(row) for row in rows if isinstance(row, dict)]
        for symbol, rows in (by_symbol.items() if isinstance(by_symbol, dict) else [])
        if isinstance(rows, list)
    }


def _q9_daily_diagnostics(reports_root: Path, day: str, record: dict[str, Any]) -> dict[str, Any]:
    path = Path(record.get("path") or "")
    # The ~120 MB windows file is streamed one window at a time; each window is classified
    # (synthetic / post-session / trusted scanner window) and only the counts and trusted windows'
    # generated_at survive.
    tally = _ev.Q9WindowTally()
    if path.exists():
        try:
            for row in iter_json_array(path, "windows", strict=True):
                tally.add(row)
        except (OSError, ValueError):
            tally.reset()  # unreadable windows file == no windows (what read_json -> {} gave)
    # Only the payload count and the generated_at of payloads that carry q9 decision
    # candidates are needed below, so reduce each payload to that as it streams past.
    shadow_payload_count = 0
    shadow_times = []
    for shadow in _iter_shadow_payloads(reports_root, day):
        shadow_payload_count += 1
        if shadow.get("q9_decision_candidates"):
            parsed = _parse_window_kst(shadow.get("generated_at"))
            if parsed is not None:
                shadow_times.append(parsed)
    pre_rows = load_q9_pre_strategist_rows(reports_root, day)
    recovery_candles = _load_forward_recovery_candles(reports_root, day)
    observed_rows = (
        attach_forward_outcomes(
            pre_rows,
            minute_rows_by_symbol=recovery_candles or None,
        )
        if pre_rows
        else []
    )
    closeout = read_json(Path(reports_root) / "operator_summary" / "daily" / day / "closeout_maintenance.json")
    coverage = _ev.session_coverage(
        window_times=tally.trusted_window_times, shadow_times=shadow_times, closeout=closeout
    )
    record.update(
        _ev.q9_diagnostics_fields(
            record,
            tally=tally,
            coverage=coverage,
            shadow_payload_count=shadow_payload_count,
            pre_row_count=len(pre_rows),
            forward=_ev.forward_outcome_tally(observed_rows),
            recovery_artifact_used=bool(recovery_candles),
        )
    )
    return record


_parse_window_kst = _ev.parse_window_kst


def inventory_trade(trade_dir: Path) -> dict[str, Any]:
    paths: Iterable[tuple[str, Path, bool]] = (
        ("lifecycle_bundle", trade_dir / "lifecycle_bundle.json", True),
        ("entry", trade_dir / "entry.json", True),
        ("exit", trade_dir / "exit.json", False),
        ("scanner_evidence", trade_dir / "evidence" / "scanner_evidence.json", True),
        ("strategist_evidence", trade_dir / "evidence" / "strategist_evidence.json", True),
        ("commander_evidence", trade_dir / "evidence" / "commander_evidence.json", True),
        ("monitor_evidence", trade_dir / "evidence" / "monitor_evidence.json", True),
        ("ai_trade_summary", trade_dir / "reports" / "ai_trade_summary.json", False),
        ("post_exit_shadow", trade_dir / "reports" / "post_exit_shadow_recap.json", False),
    )
    artifacts = {name: _record(path, required=required) for name, path, required in paths}
    return _ev.trade_inventory(str(trade_dir), trade_dir.name, artifacts)


def build_artifact_inventory(reports_root: Path, day: str) -> dict[str, Any]:
    trades = [inventory_trade(path) for path in iter_trade_dirs(reports_root, day)]
    daily_root = Path(reports_root) / "operator_summary" / "daily" / day
    daily = {
        name: _record(daily_root / filename, required=required)
        for name, filename, required in (
            ("daily_summary", "daily_summary.json", True),
            ("operator_summary", "operator_summary.json", False),
            ("q8_shadow_blocker_review", "q8_shadow_blocker_review.json", True),
            ("closeout_maintenance", "closeout_maintenance.json", False),
            ("q9_decision_windows", "q9_decision_windows.json", False),
        )
    }
    daily["q9_vs_samsung_hynix_comparison"] = _record(
        Path(reports_root)
        / "evaluation"
        / "baseline_samsung_hynix"
        / day
        / "q9_vs_samsung_hynix_daily_comparison.json",
        required=False,
    )
    daily["q9_decision_windows"] = _q9_daily_diagnostics(
        reports_root,
        day,
        daily["q9_decision_windows"],
    )
    return _ev.inventory_summary(day, trades, daily)
