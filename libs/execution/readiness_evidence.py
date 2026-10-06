"""R6 / R6.1 / R6.2 -- immutable per-intent execution-readiness evidence (EVIDENCE ONLY).

Problem (2026-10-06): ``data/state/execution_readiness.json`` is only the *latest* mutable
snapshot, so the readiness value a given BUY/SELL actually saw at execution time could not be
proven afterwards.

This module persists one append-only record per BUY/SELL execution decision, at the point where
the readiness guard verdict is known and BEFORE intent admission / Step5C / broker submission.

R6.2: EVIDENCE IS OBSERVATIONAL PROOF, NEVER A CAPABILITY TOKEN. Possessing a valid ALLOW record (of any age)
does not permit anything. The final choke point requires (a) the record to be bound to exactly this
execution attempt (execution_attempt_id), runtime instance and ownership generation, and (b) the CURRENT
canonical owner / readiness / recovery state to still match that ALLOW decision. Timestamps are audit
diagnostics only; there is no age-based authorization window.

AUTHORITY RULE -- this record is evidence only. It is never an input to any readiness,
execution, ownership, Step5C or Step5D decision. The in-memory ``state["execution_readiness"]``
and the existing guard decision stay authoritative. The final mutation choke point
(``execute_owned_order``) only checks that the evidence contract was satisfied (a durable,
matching, valid record exists); it grants no execution authority.

FAIL-CLOSED SCOPE -- only the evidence contract treats a failure as "do not submit". Ordinary
diagnostic logging elsewhere is unaffected.

Storage: ``data/logs/execution_readiness_evidence/<KST day>.jsonl`` (append-only, one JSON object
per line). Existing lines are never rewritten.

R6.1 properties
* The whole read -> validate/dedup -> allocate intent_sequence -> append -> fsync -> read-back
  critical section runs under a per-day interprocess lock (O_CREAT|O_EXCL lock file, the same
  proven pattern as ``libs/kiwoom/token_refresh_guard.py``; bounded wait, stale-lock breaking).
  The lock is storage serialisation only -- it is not an ownership/authority mechanism. Lock
  timeout is a write failure (fail closed), never a fail-open.
* ``record_id`` is a deterministic digest of the decision identity. Same intent + same attempt
  (same readiness computation / verdicts) -> same record_id: a concurrent or repeated writer
  receives a deterministic ``duplicate`` result referencing the single stored record. A new
  legitimate attempt (different readiness computation or verdict) -> new record_id and the next
  ``intent_sequence``.
* Torn/partial writes can never become valid evidence: a record only counts if its line parses
  and its ``record_hash`` verifies; a torn tail left by a crashed writer is isolated by a leading
  newline on the next append and is ignored by every reader; success is only reported after the
  written bytes are read back and verified.
* Prospective only: nothing here reconstructs or back-fills historical readiness.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

import socket
import uuid

from libs.core.path_isolation import isolate_canonical_path_for_pytest

SCHEMA_VERSION = "execution_readiness_evidence.v1"
PHASE_GUARD_BLOCK = "readiness_guard_block"
PHASE_PRE_BROKER_SUBMIT = "pre_broker_submit"
DEFAULT_ROOT = Path("data/logs/execution_readiness_evidence")
WRITE_FAILED_REASON = "readiness_evidence_write_failed"
REQUIRED_REASON = "readiness_evidence_required"
INVALID_REASON = "readiness_evidence_invalid"

LOCK_WAIT_SEC = 5.0  # bounded wait for the storage lock; age NEVER authorises breaking a lock
READINESS_SNAPSHOT_MAX_AGE_SEC = 120.0  # freshness of the persisted readiness snapshot used ONLY as a revalidation input
STALE_REASON = "readiness_evidence_stale"

_KST = timezone(timedelta(hours=9))
_DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_NEW_EXPOSURE_API_IDS = {"kt10000": "BUY", "kt10001": "SELL"}
_NON_EXPOSURE_API_IDS = frozenset({"kt10002", "kt10003"})  # MODIFY / CANCEL
_UNRESOLVED_ORDER_ALIAS = "order_submit"


class ReadinessEvidenceWriteError(RuntimeError):
    """The immutable readiness evidence record could not be persisted."""


# ----------------------------------------------------------------------------- helpers


def evidence_root(state: Mapping[str, Any]) -> Path:
    override = str((state or {}).get("execution_readiness_evidence_root") or "").strip()
    if not override:
        # Process-wide operator configuration (never taken from a caller-supplied evidence reference).
        override = (os.getenv("EXECUTION_READINESS_EVIDENCE_ROOT", "") or "").strip()
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


def _normalize_symbol(raw: Any) -> str:
    text = _text(raw)
    return text[1:] if text.startswith("A") and len(text) > 1 else text


def _order_symbol(order: Mapping[str, Any]) -> str:
    return _normalize_symbol(order.get("symbol") or order.get("stk_cd") or order.get("symbol_raw"))


def _opt_int(value: Any) -> Optional[int]:
    try:
        return None if value is None or value == "" else int(float(value))
    except (TypeError, ValueError):
        return None


def resolve_execution_mode() -> str:
    """Effective execution mode, resolved exactly like graphs/nodes/execute_from_packet.py."""
    mode = (os.getenv("EXECUTION_MODE", "") or "").strip().lower()
    if mode in ("mock", "real"):
        return mode
    try:
        from libs.core.settings import Settings

        base = str(getattr(Settings.from_env(), "kiwoom_mode", "mock") or "mock").strip().lower()
        return "real" if base == "real" else "mock"
    except Exception:
        return "mock"


def is_new_exposure_order(order: Mapping[str, Any], request: Any = None) -> bool:
    """True for a new BUY/SELL order (not CANCEL/MODIFY). Decided by api_id first, then action."""
    api_id = _text(getattr(request, "api_id", None)).lower() if request is not None else ""
    if api_id in _NEW_EXPOSURE_API_IDS:
        return True
    if api_id in _NON_EXPOSURE_API_IDS:
        return False
    return _text(order.get("action")).upper() in ("BUY", "SELL")


# ------------------------------------------------------------------------------- records


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
    source: str = "execute_from_packet",
    execution_attempt_id: str = "",
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
        "source": _text(source),
        "phase": phase,
        "recorded_at": recorded_at.isoformat(timespec="microseconds"),
        "recorded_at_epoch": round(recorded, 6),
        "intent_id": _text(order.get("intent_id")),
        "execution_attempt_id": _text(execution_attempt_id),
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
            "schema_version", "phase", "intent_id", "execution_attempt_id", "runtime_instance_id", "ownership_generation",
            "execution_readiness_computed_at_epoch", "execution_readiness_ready",
            "execution_readiness_reasons", "recovery_required", "portfolio_reconciled",
            "open_orders_reconciled", "guard_enabled", "guard_verdict", "guard_reason",
            "broker_submission_allowed", "symbol", "side", "quantity",
        )
    }
    # Attempt identity is explicit: the same intent + the same execution_attempt_id (+ same readiness
    # computation and verdicts) collapses deterministically; a new attempt is a new record.
    record["record_id"] = "r6-" + _digest(identity)[:32]
    return record


def _day_of(epoch: float) -> str:
    return datetime.fromtimestamp(float(epoch), tz=_KST).strftime("%Y-%m-%d")


def _day_path(root: Path, recorded_at_epoch: float) -> Path:
    return Path(root) / f"{_day_of(recorded_at_epoch)}.jsonl"


def _record_hash_ok(row: Mapping[str, Any]) -> bool:
    expected = row.get("record_hash")
    if not expected:
        return False
    return expected == _digest({k: v for k, v in row.items() if k != "record_hash"})


def _read_valid_records(path: Path) -> List[Dict[str, Any]]:
    """Every line that parses AND verifies its record_hash. Torn / tampered lines are ignored."""
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open("rb") as handle:
        for raw in handle:
            try:
                row = json.loads(raw.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                continue
            if isinstance(row, dict) and _record_hash_ok(row):
                rows.append(row)
    return rows


# --------------------------------------------------------------------------------- lock


def _host_id() -> str:
    try:
        return socket.gethostname()
    except Exception:  # pragma: no cover
        return ""


class _EvidenceLock:
    """Per-day interprocess STORAGE lock with strict live-owner identity (not an ownership authority).

    Uses the proven process-identity primitives of libs/runtime/live_loop_lock.py (pid_exists,
    process_start_identity) and the same exclusive-create + reclaim-guard pattern:

    * live owner (same pid AND same process_start_identity)  -> lock stays valid however old it is
    * dead owner (pid gone)                                    -> reclaim
    * same pid, different start identity (PID reuse)           -> reclaim
    * live pid whose identity cannot be verified               -> fail closed
    * malformed / incomplete lock content                      -> fail closed
    * lock written by another host / PID namespace             -> never reclaimed (liveness cannot be
      verified from here); wait up to the bounded timeout, then fail closed
    * release requires the exact owner token + pid + identity (non-owner release is rejected)
    """

    def __init__(self, path: Path, *, wait_sec: float = LOCK_WAIT_SEC) -> None:
        self.path = Path(path)
        self.wait_sec = float(wait_sec)
        self.token = uuid.uuid4().hex
        self.pid = os.getpid()
        self.identity: Optional[str] = None
        self._held = False

    def _payload(self) -> Dict[str, Any]:
        return {
            "pid": self.pid,
            "process_start_identity": self.identity,
            "owner_token": self.token,
            "acquired_at": int(time.time()),
            "host_id": _host_id(),
        }

    @staticmethod
    def _read(path: Path) -> Optional[Dict[str, Any]]:
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
        return obj if isinstance(obj, dict) else None

    def _try_create(self) -> bool:
        """Publish the lock with its identity content atomically (tmp file + hard link = exclusive)."""
        payload = _canonical_json(self._payload()).encode("utf-8")
        tmp = self.path.with_name(self.path.name + f".new-{self.token}")
        fd = os.open(str(tmp), os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0), 0o644)
        try:
            os.write(fd, payload)
            os.fsync(fd)
        finally:
            os.close(fd)
        try:
            os.link(str(tmp), str(self.path))  # fails if the lock exists -> never exposes a half-written lock
            return True
        except FileExistsError:
            return False
        except OSError:
            # Filesystem without hard links: exclusive create + immediate write; readers give a short grace
            # to partially written content (see __enter__), never treating it as a broken lock.
            try:
                lfd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0), 0o644)
            except FileExistsError:
                return False
            try:
                os.write(lfd, payload)
                os.fsync(lfd)
            finally:
                os.close(lfd)
            return True
        finally:
            try:
                tmp.unlink()
            except OSError:
                pass

    def _reclaim(self, observed: Dict[str, Any]) -> bool:
        """Replace a dead/reused owner's lock. Serialised with a short-lived exclusive guard file."""
        guard = self.path.with_name(self.path.name + ".reclaim-guard")
        try:
            guard_fd = os.open(str(guard), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            return False  # another process is deciding this reclaim right now; favour safety
        try:
            current = self._read(self.path)
            if current != observed:  # the picture changed since we looked
                return False
            tmp = self.path.with_name(self.path.name + f".tmp-{self.token}")
            try:
                tmp.write_text(_canonical_json(self._payload()), encoding="utf-8")
                os.replace(tmp, self.path)
            finally:
                try:
                    tmp.unlink()
                except OSError:
                    pass
            return True
        finally:
            os.close(guard_fd)
            try:
                guard.unlink()
            except OSError:
                pass

    def __enter__(self) -> "_EvidenceLock":
        from libs.runtime.live_loop_lock import _process_start_identity, pid_exists

        self.identity = _process_start_identity(self.pid)
        if not self.identity:
            raise ReadinessEvidenceWriteError("IDENTITY_UNVERIFIABLE:self")
        deadline = time.monotonic() + self.wait_sec
        while True:
            if self._try_create():
                self._held = True
                return self
            observed = self._read(self.path)
            if observed is None:
                if not self.path.exists():
                    continue  # released between our attempt and our read
                try:
                    in_progress = time.time() - self.path.stat().st_mtime < 2.0  # fallback-create grace only
                except OSError:
                    in_progress = False
                if in_progress and time.monotonic() < deadline:
                    time.sleep(0.02)
                    continue
                raise ReadinessEvidenceWriteError("LOCK_METADATA_INVALID")
            pid = _opt_int(observed.get("pid")) or 0
            identity = _text(observed.get("process_start_identity"))
            if pid <= 0 or not identity or not _text(observed.get("owner_token")):
                raise ReadinessEvidenceWriteError("LOCK_METADATA_INVALID")
            if _text(observed.get("host_id")) != _host_id():
                pass  # foreign host / PID namespace: liveness unverifiable -> never reclaim, just wait
            elif not pid_exists(pid):
                if self._reclaim(observed):
                    self._held = True
                    return self
            else:
                current = _process_start_identity(pid)
                if current is None:
                    raise ReadinessEvidenceWriteError("IDENTITY_UNVERIFIABLE:owner")
                if current != identity:  # PID reuse: the original owner is conclusively gone
                    if self._reclaim(observed):
                        self._held = True
                        return self
                # else: confirmed live, identity-matched owner -> age is irrelevant; wait
            if time.monotonic() >= deadline:
                raise ReadinessEvidenceWriteError("evidence_lock_timeout")
            time.sleep(0.02)

    def release(self) -> Tuple[bool, str]:
        """Exact-owner release only."""
        observed = self._read(self.path)
        if observed is None:
            return (True, "noop_no_lock") if not self.path.exists() else (False, "non_owner_release_rejected")
        if (
            _text(observed.get("owner_token")) != self.token
            or _opt_int(observed.get("pid")) != self.pid
            or _text(observed.get("process_start_identity")) != (self.identity or "")
            or not self.identity
        ):
            return False, "non_owner_release_rejected"
        self.path.unlink()
        return True, "released"

    def __exit__(self, *_exc: Any) -> None:
        if self._held:
            self._held = False
            self.release()


def _write_all(fd: int, payload: bytes) -> None:
    """Single append write; tests patch this to simulate partial writes."""
    written = os.write(fd, payload)
    if written != len(payload):
        raise OSError(f"short_write:{written}/{len(payload)}")


# ------------------------------------------------------------------------------ writer


def append_readiness_evidence(record: Mapping[str, Any], *, root: Path) -> Dict[str, Any]:
    """Append one evidence record atomically across processes.

    Returns {"written": bool, "duplicate": bool, "record_id", "path", "day", "intent_sequence"}.
    Raises ReadinessEvidenceWriteError on any failure (the caller decides fail-closed).
    """
    try:
        body = dict(record)
        record_id = _text(body.get("record_id"))
        if not record_id:
            raise ValueError("record_id_missing")
        recorded_epoch = float(body.get("recorded_at_epoch") or time.time())
        path = _day_path(Path(root), recorded_epoch)
        day = _day_of(recorded_epoch)
        path.parent.mkdir(parents=True, exist_ok=True)
        intent_id = _text(body.get("intent_id"))
        with _EvidenceLock(path.with_name(path.name + ".lock"), wait_sec=LOCK_WAIT_SEC):
            existing = _read_valid_records(path)
            for row in existing:
                if row.get("record_id") == record_id:
                    return {
                        "written": False,
                        "duplicate": True,
                        "record_id": record_id,
                        "path": str(path),
                        "day": day,
                        "intent_sequence": int(row.get("intent_sequence") or 0),
                    }
            body["intent_sequence"] = 1 + sum(1 for row in existing if intent_id and row.get("intent_id") == intent_id)
            body["record_hash"] = _digest({k: v for k, v in body.items() if k != "record_hash"})
            payload = (_canonical_json(body) + "\n").encode("utf-8")
            torn_tail = False
            if path.exists() and path.stat().st_size > 0:
                with path.open("rb") as handle:
                    handle.seek(-1, os.SEEK_END)
                    torn_tail = handle.read(1) != b"\n"
            if torn_tail:  # isolate a crashed writer's fragment on its own (invalid) line
                payload = b"\n" + payload
            fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_BINARY", 0), 0o644)
            try:
                _write_all(fd, payload)
                os.fsync(fd)
            finally:
                os.close(fd)
            # Success only after the bytes are read back and verify as a valid record.
            verified = [row for row in _read_valid_records(path) if row.get("record_id") == record_id]
            if len(verified) != 1:
                raise OSError("readback_verification_failed")
        return {
            "written": True,
            "duplicate": False,
            "record_id": record_id,
            "path": str(path),
            "day": day,
            "intent_sequence": int(body["intent_sequence"]),
        }
    except ReadinessEvidenceWriteError:
        raise
    except Exception as exc:  # any persistence problem -> explicit, typed failure
        raise ReadinessEvidenceWriteError(f"{type(exc).__name__}: {exc}") from exc


# ------------------------------------------------------------------ reference / validation


def evidence_reference(result: Mapping[str, Any], record: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "record_id": result.get("record_id"),
        "intent_id": _text(record.get("intent_id")),
        "execution_attempt_id": _text(record.get("execution_attempt_id")),
        "runtime_instance_id": record.get("runtime_instance_id"),
        "ownership_generation": record.get("ownership_generation"),
        "day": result.get("day"),
        "phase": record.get("phase"),
    }


def _current_canonical_owner() -> Optional[Dict[str, Any]]:
    """Read-only view of the canonical runtime owner row (never creates/refreshes/acquires anything)."""
    import sqlite3

    try:
        from libs.runtime.runtime_ownership import resolve_runtime_ownership_db_path

        db = Path(resolve_runtime_ownership_db_path())
        if not db.exists():
            return None
        conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True, timeout=5.0)
        try:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT instance_id, generation, lease_expires_at FROM runtime_ownership WHERE id = 1"
            ).fetchone()
        finally:
            conn.close()
        return dict(row) if row is not None else None
    except Exception:
        return None


def _current_readiness(state: Mapping[str, Any], now: float) -> Optional[Dict[str, Any]]:
    """The CURRENT readiness value: the caller's in-memory authoritative dict if present, else the
    persisted readiness snapshot (fresh only). Read as a revalidation input; never modified."""
    live = state.get("execution_readiness") if isinstance(state, Mapping) else None
    if isinstance(live, Mapping):
        return dict(live)
    try:
        path = Path(os.getenv("EXECUTION_READINESS_SNAPSHOT_PATH", "") or "")
        if not str(path):
            from libs.core.path_isolation import isolate_canonical_path_for_pytest as iso

            default = Path("data/state/execution_readiness.json")
            path = iso(default, canonical_path=default, isolated_name="execution_readiness.json")
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        computed = float(payload.get("computed_at_epoch") or 0.0)
        if not 0.0 <= now - computed <= READINESS_SNAPSHOT_MAX_AGE_SEC:
            return None
        readiness = payload.get("execution_readiness")
        return dict(readiness) if isinstance(readiness, Mapping) else None
    except Exception:
        return None


def revalidate_current_safety(row: Mapping[str, Any], *, state: Mapping[str, Any], now: Optional[float] = None) -> Tuple[bool, str]:
    """Is the original ALLOW decision still safe to act on? Safety-state revalidation only.

    Does NOT recompute strategy or readiness; it only checks that the canonical owner, the readiness
    value and the recovery flag still match the ALLOW the evidence recorded.
    """
    t = float(now if now is not None else time.time())
    if row.get("guard_enabled") is False and not row.get("readiness_present"):
        # The operator disabled the existing readiness gate (EXECUTION_READINESS_GATE_ENABLED=false) and no
        # readiness context existed: there was no readiness ALLOW decision to go stale. The evidence is still
        # bound to this exact attempt/intent/order; only the owner/readiness revalidation is not applicable.
        return True, ""
    instance, generation = row.get("runtime_instance_id"), row.get("ownership_generation")
    if not instance or generation is None:
        return False, INVALID_REASON  # evidence without a runtime identity can never be current
    owner = _current_canonical_owner()
    if owner is None or float(owner.get("lease_expires_at") or 0.0) <= t:
        return False, STALE_REASON  # no verifiable live canonical owner
    if _text(owner.get("instance_id")) != _text(instance) or int(owner.get("generation") or -1) != int(generation):
        return False, STALE_REASON  # runtime instance / ownership generation changed
    current = _current_readiness(state, t)
    if current is None:
        return False, STALE_REASON  # current readiness unverifiable
    if (
        not current.get("ready")
        or bool(current.get("recovery_required"))
        or _text(current.get("runtime_instance_id")) != _text(instance)
        or _opt_int(current.get("ownership_generation")) != int(generation)
    ):
        return False, STALE_REASON  # readiness / recovery / generation no longer match the ALLOW
    return True, ""


def validate_evidence_reference(
    reference: Any,
    *,
    order: Mapping[str, Any],
    root: Path,
    execution_attempt_id: str = "",
    state: Optional[Mapping[str, Any]] = None,
    now_epoch: Optional[float] = None,
) -> Tuple[bool, str]:
    """Prove the evidence contract was satisfied for THIS execution attempt (storage lookup, not trust).

    Valid iff exactly one hash-verified pre_broker_submit record with the referenced record_id exists,
    it was written for this very intent/side/symbol/quantity AND this very execution_attempt_id with
    an ALLOW verdict, AND the current canonical owner / readiness / recovery state still matches it.
    No age window: a timestamp is audit data only. This grants no authority.
    """
    if not isinstance(reference, Mapping):
        return False, REQUIRED_REASON
    attempt = _text(execution_attempt_id)
    record_id = _text(reference.get("record_id"))
    day = _text(reference.get("day"))
    if not attempt:
        return False, REQUIRED_REASON
    if not record_id or not _DAY_RE.match(day) or _text(reference.get("execution_attempt_id")) != attempt:
        return False, INVALID_REASON
    try:
        rows = [row for row in _read_valid_records(Path(root) / f"{day}.jsonl") if row.get("record_id") == record_id]
    except OSError:
        return False, INVALID_REASON
    if len(rows) != 1:
        return False, INVALID_REASON  # missing, or ambiguous duplicate identity
    row = rows[0]
    quantity = _opt_int(order.get("qty") if order.get("qty") is not None else order.get("ord_qty"))
    checks = (
        row.get("schema_version") == SCHEMA_VERSION,
        row.get("phase") == PHASE_PRE_BROKER_SUBMIT,
        row.get("broker_submission_allowed") is True,
        row.get("guard_verdict") == "ALLOW",
        _text(row.get("execution_attempt_id")) == attempt,
        _text(row.get("intent_id")) == _text(order.get("intent_id")) != "",
        _text(row.get("side")) == _text(order.get("action")).upper(),
        _text(row.get("symbol")) == _order_symbol(order),
        row.get("quantity") == quantity,
        _text(row.get("runtime_instance_id")) == _text(reference.get("runtime_instance_id")),
        row.get("ownership_generation") == reference.get("ownership_generation"),
    )
    if not all(checks):
        return False, INVALID_REASON
    return revalidate_current_safety(row, state=state or {}, now=now_epoch)


def require_readiness_evidence_for_order(
    *, state: Mapping[str, Any], order: Mapping[str, Any], request: Any, evidence: Any, execution_attempt_id: str = ""
) -> Tuple[bool, str]:
    """Final mutation choke-point check (execute_owned_order). (ok, reason)."""
    if resolve_execution_mode() != "real" or not is_new_exposure_order(order, request):
        return True, ""  # not production-capable BUY/SELL exposure -> not applicable
    if evidence is None:
        return False, REQUIRED_REASON
    return validate_evidence_reference(
        evidence, order=order, root=evidence_root(state), execution_attempt_id=execution_attempt_id, state=state)


# ----------------------------------------------------------------------- shared helper


def record_pre_admission_evidence(
    *,
    state: Mapping[str, Any],
    order: Mapping[str, Any],
    phase: str,
    guard_enabled: bool,
    guard_allowed: bool,
    guard_reason: str,
    broker_submission_allowed: bool,
    request: Any = None,
    source: str = "execute_from_packet",
    execution_attempt_id: str = "",
) -> Tuple[bool, str, Dict[str, Any]]:
    """The ONE shared R6 pre-admission helper used by every production-capable mutation path.

    Returns (ok, reason, details). ok=False means the evidence could not be persisted and the
    caller MUST NOT admit or submit. details["reference"] is the proof passed to execute_owned_order.
    Scope: new BUY/SELL exposure in real execution mode (CANCEL/MODIFY and mock write nothing).
    """
    action = _text(order.get("action")).upper()
    mode = resolve_execution_mode()
    if mode != "real" or not is_new_exposure_order(order, request):
        return True, "", {"enabled": False, "action": action, "execution_mode": mode}
    attempt = _text(execution_attempt_id) or uuid.uuid4().hex
    try:
        record = build_readiness_evidence_record(
            state=state, order=order, phase=phase, guard_enabled=guard_enabled, guard_allowed=guard_allowed,
            guard_reason=guard_reason, broker_submission_allowed=broker_submission_allowed,
            execution_mode=mode, source=source, execution_attempt_id=attempt,
        )
        result = append_readiness_evidence(record, root=evidence_root(state))
    except Exception as exc:
        return False, WRITE_FAILED_REASON, {
            "enabled": True, "action": action, "phase": phase,
            "error": f"{type(exc).__name__}: {str(exc)[:160]}",
        }
    return True, "", {
        "enabled": True,
        "action": action,
        "phase": phase,
        "record_id": result.get("record_id"),
        "duplicate": bool(result.get("duplicate")),
        "intent_sequence": result.get("intent_sequence"),
        "path": result.get("path"),
        "execution_attempt_id": attempt,
        "reference": evidence_reference(result, record),
    }


__all__ = [
    "DEFAULT_ROOT",
    "READINESS_SNAPSHOT_MAX_AGE_SEC",
    "STALE_REASON",
    "INVALID_REASON",
    "PHASE_GUARD_BLOCK",
    "PHASE_PRE_BROKER_SUBMIT",
    "REQUIRED_REASON",
    "SCHEMA_VERSION",
    "WRITE_FAILED_REASON",
    "ReadinessEvidenceWriteError",
    "append_readiness_evidence",
    "build_readiness_evidence_record",
    "evidence_reference",
    "evidence_root",
    "is_new_exposure_order",
    "record_pre_admission_evidence",
    "require_readiness_evidence_for_order",
    "resolve_execution_mode",
    "revalidate_current_safety",
    "validate_evidence_reference",
]
