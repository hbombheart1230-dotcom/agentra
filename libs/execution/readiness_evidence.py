"""R6 -- immutable per-intent execution-readiness evidence (EVIDENCE ONLY).

Problem (2026-10-06): ``data/state/execution_readiness.json`` is only the *latest* mutable
snapshot, so the readiness value a given BUY/SELL actually saw at execution time could not be
proven afterwards.

This module persists one append-only record per BUY/SELL execution decision, at the point where
the readiness guard verdict is known and BEFORE intent admission / broker submission.

AUTHORITY RULE -- this record is evidence only. It is never read back by any execution path and
never becomes readiness / execution / ownership / Step5C / Step5D authority. The in-memory
``state["execution_readiness"]`` and the existing guard decision stay authoritative.

FAIL-CLOSED SCOPE -- only the caller's evidence contract (``execute_from_packet``) treats a
write failure as "do not submit". Ordinary diagnostic logging elsewhere is unaffected.

Storage: ``data/logs/execution_readiness_evidence/<KST day>.jsonl`` (append-only, one JSON
object per line, O_APPEND, fsync'd). Existing lines are never rewritten. ``record_id`` is a
deterministic digest of the decision identity, so an exact duplicate is detected and not
written twice; every record also carries a ``record_hash`` over its own content and a per-intent
``intent_sequence`` so replays of one intent stay ordered rather than ambiguous.

Prospective only: nothing here reconstructs or back-fills historical readiness.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from libs.core.path_isolation import isolate_canonical_path_for_pytest

SCHEMA_VERSION = "execution_readiness_evidence.v1"
PHASE_GUARD_BLOCK = "readiness_guard_block"
PHASE_PRE_BROKER_SUBMIT = "pre_broker_submit"
DEFAULT_ROOT = Path("data/logs/execution_readiness_evidence")
WRITE_FAILED_REASON = "readiness_evidence_write_failed"

_KST = timezone(timedelta(hours=9))


class ReadinessEvidenceWriteError(RuntimeError):
    """The immutable readiness evidence record could not be persisted."""


def evidence_root(state: Mapping[str, Any]) -> Path:
    override = str(state.get("execution_readiness_evidence_root") or "").strip()
    if override:
        return Path(override)
    return isolate_canonical_path_for_pytest(
        DEFAULT_ROOT, canonical_path=DEFAULT_ROOT, isolated_name="execution_readiness_evidence"
    )


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _text(value: Any) -> str:
    return str(value if value is not None else "").strip()


def _order_symbol(order: Mapping[str, Any]) -> str:
    raw = _text(order.get("symbol") or order.get("stk_cd") or order.get("symbol_raw"))
    return raw[1:] if raw.startswith("A") and len(raw) > 1 else raw


def _opt_int(value: Any) -> Optional[int]:
    try:
        return None if value is None or value == "" else int(value)
    except (TypeError, ValueError):
        return None


def build_readiness_evidence_record(
    *,
    state: Mapping[str, Any],
    order: Mapping[str, Any],
    phase: str,
    guard_enabled: bool,
    guard_allowed: bool,
    guard_reason: str,
    broker_submission_allowed: bool,
    execution_mode: str,
    now_epoch: Optional[float] = None,
) -> Dict[str, Any]:
    """Pure builder: captures the readiness/guard values exactly as the caller holds them now."""
    readiness = state.get("execution_readiness")
    readiness = dict(readiness) if isinstance(readiness, Mapping) else {}
    ownership = state.get("runtime_ownership")
    ownership = dict(ownership) if isinstance(ownership, Mapping) else {}
    meta = order.get("meta") if isinstance(order.get("meta"), Mapping) else {}
    recorded = float(now_epoch if now_epoch is not None else time.time())
    recorded_at = datetime.fromtimestamp(recorded, tz=_KST)
    computed_epoch = _opt_int(state.get("execution_readiness_computed_at_epoch"))

    record: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "evidence_only": True,
        "phase": phase,
        "recorded_at": recorded_at.isoformat(timespec="microseconds"),
        "recorded_at_epoch": round(recorded, 6),
        "intent_id": _text(order.get("intent_id")),
        "run_id": _text(state.get("run_id")),
        "runtime_instance_id": readiness.get("runtime_instance_id"),
        "ownership_generation": readiness.get("ownership_generation"),
        "state_runtime_instance_id": ownership.get("instance_id"),
        "state_ownership_generation": ownership.get("generation"),
        "recovery_required": bool(readiness.get("recovery_required")),
        "state_recovery_required": bool(ownership.get("recovery_required")),
        "portfolio_reconciled": bool(readiness.get("portfolio_reconciled")),
        "open_orders_reconciled": bool(readiness.get("open_orders_reconciled")),
        "orphan_claim_count": readiness.get("orphan_claim_count"),
        "config_valid": bool(readiness.get("config_valid")),
        "execution_enabled": bool(readiness.get("execution_enabled")),
        "readiness_present": bool(readiness),
        "execution_readiness_ready": bool(readiness.get("ready")) if readiness else False,
        "execution_readiness_reasons": [str(r) for r in (readiness.get("reasons") or [])],
        "execution_readiness_computed_at_epoch": computed_epoch,
        "execution_readiness_computed_at": (
            datetime.fromtimestamp(computed_epoch, tz=_KST).isoformat(timespec="seconds")
            if computed_epoch is not None
            else None
        ),
        "execution_readiness_generation": readiness.get("ownership_generation"),
        "guard_enabled": bool(guard_enabled),
        "guard_verdict": "ALLOW" if guard_allowed else "BLOCK",
        "guard_reason": _text(guard_reason),
        "broker_submission_allowed": bool(broker_submission_allowed),
        "execution_mode": _text(execution_mode),
        "symbol": _order_symbol(order),
        "side": _text(order.get("action")).upper(),
        "quantity": _opt_int(order.get("qty") if order.get("qty") is not None else order.get("ord_qty")),
        "order_type": _text(order.get("order_type")),
        "correlation": {
            "intent_id": _text(order.get("intent_id")),
            "run_id": _text(state.get("run_id")),
            "entry_reason": _text(meta.get("entry_reason")),
            "exit_reason": _text(meta.get("exit_reason")),
            "signal_source": _text(meta.get("signal_source") or meta.get("source")),
            "entry_signal_source": _text(meta.get("entry_signal_source")),
            "rationale": _text(order.get("rationale")),
        },
    }
    identity = {
        key: record[key]
        for key in (
            "schema_version", "phase", "intent_id", "runtime_instance_id", "ownership_generation",
            "execution_readiness_computed_at_epoch", "execution_readiness_ready",
            "execution_readiness_reasons", "recovery_required", "portfolio_reconciled",
            "open_orders_reconciled", "guard_enabled", "guard_verdict", "guard_reason",
            "broker_submission_allowed", "symbol", "side", "quantity",
        )
    }
    record["record_id"] = "r6-" + _digest(identity)[:32]
    return record


def _day_path(root: Path, recorded_at_epoch: float) -> Path:
    day = datetime.fromtimestamp(recorded_at_epoch, tz=_KST).strftime("%Y-%m-%d")
    return root / f"{day}.jsonl"


def _scan_existing(path: Path, *, record_id: str, intent_id: str) -> tuple[bool, int]:
    """(duplicate_record_id_present, number_of_existing_records_for_intent)."""
    if not path.exists():
        return False, 0
    duplicate = False
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if record_id in line:
                try:
                    if json.loads(line).get("record_id") == record_id:
                        duplicate = True
                except (ValueError, TypeError):
                    pass
            if intent_id and intent_id in line:
                try:
                    if json.loads(line).get("intent_id") == intent_id:
                        count += 1
                except (ValueError, TypeError):
                    pass
    return duplicate, count


def append_readiness_evidence(record: Mapping[str, Any], *, root: Path) -> Dict[str, Any]:
    """Append one evidence record. Never overwrites, truncates or rewrites existing lines.

    Returns {"written": bool, "duplicate": bool, "record_id": str, "path": str, "intent_sequence": int}.
    Raises ReadinessEvidenceWriteError on any failure (the caller decides fail-closed).
    """
    try:
        body = dict(record)
        record_id = _text(body.get("record_id"))
        if not record_id:
            raise ValueError("record_id_missing")
        path = _day_path(Path(root), float(body.get("recorded_at_epoch") or time.time()))
        path.parent.mkdir(parents=True, exist_ok=True)
        duplicate, existing_for_intent = _scan_existing(path, record_id=record_id, intent_id=_text(body.get("intent_id")))
        if duplicate:
            return {"written": False, "duplicate": True, "record_id": record_id, "path": str(path), "intent_sequence": 0}
        body["intent_sequence"] = existing_for_intent + 1
        body["record_hash"] = _digest({k: v for k, v in body.items() if k != "record_hash"})
        payload = (_canonical_json(body) + "\n").encode("utf-8")
        fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_BINARY", 0), 0o644)
        try:
            written = os.write(fd, payload)
            if written != len(payload):
                raise OSError(f"short_write:{written}/{len(payload)}")
            os.fsync(fd)
        finally:
            os.close(fd)
        return {
            "written": True,
            "duplicate": False,
            "record_id": record_id,
            "path": str(path),
            "intent_sequence": int(body["intent_sequence"]),
        }
    except ReadinessEvidenceWriteError:
        raise
    except Exception as exc:  # any persistence problem -> explicit, typed failure
        raise ReadinessEvidenceWriteError(f"{type(exc).__name__}: {exc}") from exc


__all__ = [
    "DEFAULT_ROOT",
    "PHASE_GUARD_BLOCK",
    "PHASE_PRE_BROKER_SUBMIT",
    "SCHEMA_VERSION",
    "WRITE_FAILED_REASON",
    "ReadinessEvidenceWriteError",
    "append_readiness_evidence",
    "build_readiness_evidence_record",
    "evidence_root",
]
