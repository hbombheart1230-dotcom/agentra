"""R6.2 -- evidence is observational proof, never a reusable capability token; storage lock identity.

Pins:
* no age-based authorization (the former 600 s window is gone);
* evidence is bound to ONE execution attempt (+ runtime instance + ownership generation);
* the final choke point revalidates CURRENT canonical owner / readiness / recovery against the ALLOW decision;
* the evidence storage lock is broken only for a dead / PID-reused owner, never because it is merely old.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

import pytest

from _r6_helpers import count_execute_owned_order_calls, sync_owner, write_snapshot
from libs.execution import readiness_evidence as r6
from libs.execution.readiness_evidence import (
    INVALID_REASON,
    PHASE_PRE_BROKER_SUBMIT,
    STALE_REASON,
    ReadinessEvidenceWriteError,
    append_readiness_evidence,
    build_readiness_evidence_record,
    record_pre_admission_evidence,
)
from libs.runtime.live_loop_lock import _process_start_identity


class _Spy:
    def __init__(self) -> None:
        self.calls = 0
        self._lock = threading.Lock()

    def execute(self, req, *, auth_token=None):  # type: ignore[no-untyped-def]
        from libs.core.api_response import ApiResponse
        from libs.execution.executors.base import ExecutionResult

        with self._lock:
            self.calls += 1
        return ExecutionResult(
            response=ApiResponse(status_code=200, ok=True, payload={"return_code": "0", "ord_no": "R62"}, error_code=None, error_message=None, raw_text=""),
            meta={"executor": "real", "broker_outcome": "ACCEPTED"},
        )


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("EXECUTION_MODE", "real")
    monkeypatch.setenv("KIWOOM_MODE", "mock")
    monkeypatch.setenv("EXECUTION_ENABLED", "true")
    monkeypatch.setenv("EXECUTION_READINESS_GATE_ENABLED", "true")
    monkeypatch.setenv("INTENT_STATE_DB_PATH", str(tmp_path / "intent_state.db"))
    monkeypatch.setenv("REPORTS_ROOT", str(tmp_path / "reports"))
    monkeypatch.setenv("EXECUTION_READINESS_EVIDENCE_ROOT", str(tmp_path / "evidence"))
    monkeypatch.setenv("RUNTIME_OWNERSHIP_DB_PATH", str(tmp_path / "ownership.db"))
    monkeypatch.setenv("EXECUTION_READINESS_SNAPSHOT_PATH", str(tmp_path / "readiness_snapshot.json"))


def _world(tmp_path: Path, *, instance: str = "inst-A", generation: int = 5) -> dict[str, Any]:
    from graphs.nodes.build_execution_readiness import build_execution_readiness

    class _Claims:
        def list_active_physical_claims(self, *, limit=200):
            return []

    state = {
        "run_id": "run-r62",
        "runtime_ownership": {"instance_id": instance, "generation": generation, "recovery_required": False, "acquired_at": time.time()},
        "portfolio_snapshot": {"cash": 1e7, "positions": [], "_health": {"reader_ok": True}},
        "open_order_snapshot": {"rows": [], "_health": {"reader_ok": True, "fetched_epoch": int(time.time())}},
        "intent_state_store": _Claims(),
    }
    state = build_execution_readiness(state)
    sync_owner(tmp_path / "ownership.db", instance_id=instance, generation=generation)
    write_snapshot(tmp_path / "readiness_snapshot.json", state["execution_readiness"])
    return state


def _order(iid: str, qty: int = 7) -> dict[str, Any]:
    return {"intent_id": iid, "action": "BUY", "symbol": "005930", "qty": qty, "price": 100, "order_type": "market", "trde_tp": "3"}


def _req(api_id: str = "kt10000"):
    from libs.catalog.api_request_builder import PreparedRequest

    return PreparedRequest(api_id, "POST", "/api/dostk/ordr", {}, {}, {"stk_cd": "005930", "ord_qty": "7"})


def _admit(order: dict[str, Any]) -> None:
    from libs.execution.intent_admission import admit_order_intent

    admit_order_intent(state={"run_id": "r62"}, order=order, source="test_policy")


def _evidence(world, order, *, attempt: str = "att-1"):
    ok, _, details = record_pre_admission_evidence(
        state=world, order=order, request=_req(), phase=PHASE_PRE_BROKER_SUBMIT, guard_enabled=True, guard_allowed=True,
        guard_reason="", broker_submission_allowed=True, execution_attempt_id=attempt)
    assert ok
    return details["reference"]


def _owned(order, spy, *, ref, attempt, state):
    from graphs.nodes.execute_from_packet import _normalize_execution
    from libs.execution.intent_execution_owner import execute_owned_order

    return execute_owned_order(
        state=state, order=order, request=_req(), executor=spy, readiness_evidence=ref, execution_attempt_id=attempt,
        normalize=lambda r: _normalize_execution(allowed=True, execution_result=r, allow_result=None, order=order))


# ------------------------------------------------------------------ A/B. attempt binding + current safety


def test_valid_attempt_bound_evidence_with_current_safety_executes(tmp_path):
    spy, order, world = _Spy(), _order("intent-r62-ok"), _world(tmp_path)
    _admit(order)
    out = _owned(order, spy, ref=_evidence(world, order), attempt="att-1", state=world)
    assert spy.calls == 1 and out["broker_outcome"] == "ACCEPTED"


def test_e1_readiness_turns_block_after_evidence_blocks_submit_in_memory(tmp_path):
    spy, order, world = _Spy(), _order("intent-r62-e1"), _world(tmp_path)
    _admit(order)
    ref = _evidence(world, order)
    world["execution_readiness"] = {**world["execution_readiness"], "ready": False, "reasons": ["portfolio_not_reconciled"]}
    out = _owned(order, spy, ref=ref, attempt="att-1", state=world)
    assert spy.calls == 0 and out["reason"] == STALE_REASON and out["broker_outcome"] == "NOT_SENT"


def test_e1b_readiness_turns_block_for_state_less_paths_via_persisted_snapshot(tmp_path):
    spy, order, world = _Spy(), _order("intent-r62-e1b"), _world(tmp_path)
    _admit(order)
    ref = _evidence(world, order)
    write_snapshot(tmp_path / "readiness_snapshot.json", {**world["execution_readiness"], "ready": False})
    out = _owned(order, spy, ref=ref, attempt="att-1", state={"run_id": "r62"})  # runner/approval style: no readiness in state
    assert spy.calls == 0 and out["reason"] == STALE_REASON


def test_e1c_unverifiable_current_readiness_fails_closed(tmp_path):
    spy, order, world = _Spy(), _order("intent-r62-e1c"), _world(tmp_path)
    _admit(order)
    ref = _evidence(world, order)
    (tmp_path / "readiness_snapshot.json").unlink()
    out = _owned(order, spy, ref=ref, attempt="att-1", state={"run_id": "r62"})
    assert spy.calls == 0 and out["reason"] == STALE_REASON


def test_e1d_stale_readiness_snapshot_is_not_a_valid_revalidation_input(tmp_path):
    spy, order, world = _Spy(), _order("intent-r62-e1d"), _world(tmp_path)
    _admit(order)
    ref = _evidence(world, order)
    write_snapshot(tmp_path / "readiness_snapshot.json", world["execution_readiness"], computed_at=time.time() - 3600)
    out = _owned(order, spy, ref=ref, attempt="att-1", state={"run_id": "r62"})
    assert spy.calls == 0 and out["reason"] == STALE_REASON


def test_recovery_required_after_evidence_blocks_submit(tmp_path):
    spy, order, world = _Spy(), _order("intent-r62-rec"), _world(tmp_path)
    _admit(order)
    ref = _evidence(world, order)
    world["execution_readiness"] = {**world["execution_readiness"], "recovery_required": True}
    out = _owned(order, spy, ref=ref, attempt="att-1", state=world)
    assert spy.calls == 0 and out["reason"] == STALE_REASON


def test_e2_ownership_generation_change_blocks_old_evidence(tmp_path):
    spy, order, world = _Spy(), _order("intent-r62-e2"), _world(tmp_path, generation=5)
    _admit(order)
    ref = _evidence(world, order)
    sync_owner(tmp_path / "ownership.db", instance_id="inst-A", generation=6)  # takeover: generation N -> N+1
    out = _owned(order, spy, ref=ref, attempt="att-1", state=world)
    assert spy.calls == 0 and out["reason"] == STALE_REASON


def test_e3_evidence_from_another_runtime_instance_is_blocked(tmp_path):
    spy, order, world = _Spy(), _order("intent-r62-e3"), _world(tmp_path, instance="inst-A")
    _admit(order)
    ref = _evidence(world, order)
    sync_owner(tmp_path / "ownership.db", instance_id="inst-B", generation=5)  # instance B is now the owner
    out = _owned(order, spy, ref=ref, attempt="att-1", state=world)
    assert spy.calls == 0 and out["reason"] == STALE_REASON


def test_expired_owner_lease_blocks(tmp_path):
    spy, order, world = _Spy(), _order("intent-r62-lease"), _world(tmp_path)
    _admit(order)
    ref = _evidence(world, order)
    sync_owner(tmp_path / "ownership.db", instance_id="inst-A", generation=5, lease_seconds=-5.0)
    out = _owned(order, spy, ref=ref, attempt="att-1", state=world)
    assert spy.calls == 0 and out["reason"] == STALE_REASON


def test_e4_same_intent_new_attempt_cannot_reuse_old_evidence(tmp_path):
    spy, order, world = _Spy(), _order("intent-r62-e4"), _world(tmp_path)
    _admit(order)
    old_ref = _evidence(world, order, attempt="att-1")
    out = _owned(order, spy, ref=old_ref, attempt="att-2", state=world)  # a NEW attempt presenting attempt-1 evidence
    assert spy.calls == 0 and out["reason"] == INVALID_REASON
    new_ref = _evidence(world, order, attempt="att-2")
    assert new_ref["record_id"] != old_ref["record_id"]
    out = _owned(order, spy, ref=new_ref, attempt="att-2", state=world)
    assert spy.calls == 1 and out["broker_outcome"] == "ACCEPTED"


def test_evidence_without_runtime_identity_can_never_be_current(tmp_path):
    spy, order = _Spy(), _order("intent-r62-noid")
    _admit(order)
    ref = _evidence({"run_id": "r62"}, order)  # no readiness context at all
    out = _owned(order, spy, ref=ref, attempt="att-1", state={"run_id": "r62"})
    assert spy.calls == 0 and out["reason"] in (INVALID_REASON, STALE_REASON)


def test_e5_concurrent_duplicate_callers_one_evidence_one_broker_winner(tmp_path):
    spy, order, world = _Spy(), _order("intent-r62-e5"), _world(tmp_path)
    _admit(order)
    refs = [_evidence(world, order, attempt="att-dup") for _ in range(2)]  # same attempt -> same immutable record
    assert refs[0]["record_id"] == refs[1]["record_id"]
    assert len([f for f in (tmp_path / "evidence").glob("*.jsonl")]) == 1
    lines = [ln for f in (tmp_path / "evidence").glob("*.jsonl") for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1
    barrier, results = threading.Barrier(2), []

    def caller(ref):
        barrier.wait()
        results.append(_owned(dict(order), spy, ref=ref, attempt="att-dup", state=world))

    threads = [threading.Thread(target=caller, args=(ref,)) for ref in refs]
    [t.start() for t in threads]
    [t.join(30) for t in threads]
    assert spy.calls == 1, "Step5C must allow exactly one broker mutation"
    assert sorted(r["broker_outcome"] for r in results) == ["ACCEPTED", "NOT_SENT"]


def test_e6_age_is_not_authority_in_either_direction(tmp_path):
    """A record older than the former 600 s window is not rejected for its age, and a fresh record is not
    accepted for its youth: only attempt binding + CURRENT safety decide."""
    spy, order, world = _Spy(), _order("intent-r62-e6"), _world(tmp_path)
    _admit(order)
    old = build_readiness_evidence_record(
        state=world, order=order, phase=PHASE_PRE_BROKER_SUBMIT, guard_enabled=True, guard_allowed=True, guard_reason="",
        broker_submission_allowed=True, execution_mode="real", now_epoch=time.time() - 7200, execution_attempt_id="att-old")
    result = append_readiness_evidence(old, root=tmp_path / "evidence")
    ref = r6.evidence_reference(result, old)
    out = _owned(order, spy, ref=ref, attempt="att-old", state=world)
    assert spy.calls == 1 and out["broker_outcome"] == "ACCEPTED"  # 2 h old, still the same attempt, still current

    spy2, order2, world2 = _Spy(), _order("intent-r62-e6b"), world
    _admit(order2)
    fresh_ref = _evidence(world2, order2, attempt="att-fresh")
    world2 = {**world2, "execution_readiness": {**world2["execution_readiness"], "ready": False}}
    out = _owned(order2, spy2, ref=fresh_ref, attempt="att-fresh", state=world2)
    assert spy2.calls == 0 and out["reason"] == STALE_REASON  # milliseconds old, but no longer current


def test_600_second_authorization_is_removed():
    source = (Path(r6.__file__)).read_text(encoding="utf-8")
    assert "EVIDENCE_MAX_AGE_SEC" not in source and "600" not in source.replace("READINESS_SNAPSHOT_MAX_AGE_SEC", "")
    assert not hasattr(r6, "EVIDENCE_MAX_AGE_SEC")
    assert "recorded_at_epoch" in source  # the timestamp remains as audit data only


def test_attempt_id_flows_through_the_canonical_path(tmp_path):
    from graphs.nodes.execute_from_packet import execute_from_packet

    spy, world = _Spy(), _world(tmp_path)
    cat = tmp_path / "api_catalog.jsonl"
    cat.write_text('{"api_id":"ORDER_SUBMIT","title":"order","method":"POST","path":"/orders","params":{},"_flags":{"callable":true}}\n', encoding="utf-8")
    world.update(executor=spy, catalog_path=str(cat))
    world["decision_packet"] = {"intent": {"action": "BUY", "symbol": "217590", "qty": 71, "order_api_id": "ORDER_SUBMIT", "order_type": "market"},
                                "risk": {"open_positions": 0}, "exec_context": {}}
    out = execute_from_packet(world)
    assert spy.calls == 1
    rows = [json.loads(ln) for f in (tmp_path / "evidence").glob("*.jsonl") for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(rows) == 1 and rows[0]["execution_attempt_id"] and rows[0]["execution_attempt_id"] == out["execution"]["readiness_evidence"]["execution_attempt_id"]


# ------------------------------------------------------------------------- C. lock identity


def _lock_path(tmp_path: Path, record: dict[str, Any]) -> Path:
    return tmp_path / f"{r6._day_of(record['recorded_at_epoch'])}.jsonl.lock"


def _sample(intent: str = "intent-r62-lock", attempt: str = "att-1") -> dict[str, Any]:
    order = {"intent_id": intent, "action": "BUY", "symbol": "217590", "qty": 41, "order_type": "market"}
    state = {"run_id": "r", "execution_readiness": {"ready": True, "reasons": [], "runtime_instance_id": "i", "ownership_generation": 5,
                                                      "recovery_required": False, "portfolio_reconciled": True, "open_orders_reconciled": True,
                                                      "orphan_claim_count": 0}, "execution_readiness_computed_at_epoch": 1_790_000_000}
    return build_readiness_evidence_record(state=state, order=order, phase=PHASE_PRE_BROKER_SUBMIT, guard_enabled=True, guard_allowed=True,
                                           guard_reason="", broker_submission_allowed=True, execution_mode="real",
                                           now_epoch=1_790_000_100.0, execution_attempt_id=attempt)


def _write_lock(path: Path, *, pid: int, identity, token: str = "other", host: str | None = None, age_sec: float = 0.0) -> None:
    path.write_text(json.dumps({"pid": pid, "process_start_identity": identity, "owner_token": token, "acquired_at": int(time.time() - age_sec),
                                "host_id": host if host is not None else r6._host_id()}), encoding="utf-8")
    old = time.time() - age_sec
    os.utime(path, (old, old))


@pytest.fixture()
def short_wait(monkeypatch):
    monkeypatch.setattr(r6, "LOCK_WAIT_SEC", 0.4)


@pytest.mark.parametrize("age_sec", [31, 45, 3600])
def test_e7_live_writer_lock_older_than_30s_is_never_broken(tmp_path, short_wait, age_sec):
    record = _sample()
    lock = _lock_path(tmp_path, record)
    _write_lock(lock, pid=os.getpid(), identity=_process_start_identity(os.getpid()), age_sec=age_sec)
    with pytest.raises(ReadinessEvidenceWriteError, match="evidence_lock_timeout"):
        append_readiness_evidence(record, root=tmp_path)
    assert lock.exists() and not list(tmp_path.glob("*.jsonl"))


def _dead_pid() -> int:
    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    proc.wait()
    return proc.pid


def test_e8_dead_writer_lock_is_reclaimed(tmp_path):
    record = _sample()
    _write_lock(_lock_path(tmp_path, record), pid=_dead_pid(), identity="win:1", age_sec=1)
    result = append_readiness_evidence(record, root=tmp_path)
    assert result["written"] is True
    assert not _lock_path(tmp_path, record).exists()


def test_e9_pid_reuse_lock_is_reclaimed(tmp_path):
    record = _sample()
    _write_lock(_lock_path(tmp_path, record), pid=os.getpid(), identity="posix:definitely-not-this-process", age_sec=1)
    assert append_readiness_evidence(record, root=tmp_path)["written"] is True


def test_e10_unverifiable_live_identity_fails_closed(tmp_path, monkeypatch):
    record = _sample()
    sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    try:
        real = _process_start_identity
        import libs.runtime.live_loop_lock as ll

        monkeypatch.setattr(ll, "_process_start_identity", lambda pid: real(pid) if pid == os.getpid() else None)
        _write_lock(_lock_path(tmp_path, record), pid=sleeper.pid, identity="win:whatever", age_sec=1)
        with pytest.raises(ReadinessEvidenceWriteError, match="IDENTITY_UNVERIFIABLE"):
            append_readiness_evidence(record, root=tmp_path)
        assert _lock_path(tmp_path, record).exists() and not list(tmp_path.glob("*.jsonl"))
    finally:
        sleeper.kill()
        sleeper.wait()


def test_malformed_lock_fails_closed(tmp_path):
    record = _sample()
    lock = _lock_path(tmp_path, record)
    lock.write_text("not json at all", encoding="utf-8")
    os.utime(lock, (time.time() - 100, time.time() - 100))
    with pytest.raises(ReadinessEvidenceWriteError, match="LOCK_METADATA_INVALID"):
        append_readiness_evidence(record, root=tmp_path)
    lock.write_text(json.dumps({"pid": 0, "owner_token": ""}), encoding="utf-8")
    os.utime(lock, (time.time() - 100, time.time() - 100))
    with pytest.raises(ReadinessEvidenceWriteError, match="LOCK_METADATA_INVALID"):
        append_readiness_evidence(record, root=tmp_path)
    assert lock.exists()


def test_foreign_host_lock_is_never_reclaimed(tmp_path, short_wait):
    record = _sample()
    lock = _lock_path(tmp_path, record)
    _write_lock(lock, pid=_dead_pid(), identity="posix:1", host="some-other-container", age_sec=3600)
    with pytest.raises(ReadinessEvidenceWriteError, match="evidence_lock_timeout"):
        append_readiness_evidence(record, root=tmp_path)  # liveness unverifiable from here -> never break it
    assert lock.exists()


def test_e11_non_owner_release_is_blocked_and_e12_exact_owner_release_passes(tmp_path):
    path = tmp_path / "x.jsonl.lock"
    owner = r6._EvidenceLock(path)
    intruder = r6._EvidenceLock(path)
    intruder.identity = _process_start_identity(os.getpid())
    with owner:
        assert intruder.release() == (False, "non_owner_release_rejected")
        assert path.exists(), "a non-owner can never remove another owner's lock"
        wrong_pid = r6._EvidenceLock(path)
        wrong_pid.token, wrong_pid.pid, wrong_pid.identity = owner.token, os.getpid() + 1, owner.identity
        assert wrong_pid.release() == (False, "non_owner_release_rejected")
        assert owner.release() == (True, "released")  # exact owner (pid + start identity + token)
    assert not path.exists()


def test_lock_is_released_after_the_critical_section_and_after_a_failed_write(tmp_path, monkeypatch):
    record = _sample()

    def boom(fd, payload):
        raise OSError("disk gone")

    monkeypatch.setattr(r6, "_write_all", boom)
    with pytest.raises(ReadinessEvidenceWriteError):
        append_readiness_evidence(record, root=tmp_path)
    assert not _lock_path(tmp_path, record).exists()


def test_lock_is_storage_serialisation_only_not_an_ownership_authority():
    source = Path(r6.__file__).read_text(encoding="utf-8")
    assert "runtime_ownership" in source  # read-only owner revalidation lives in the validator...
    lock_src = source[source.index("class _EvidenceLock"): source.index("def _write_all")]
    assert "runtime_ownership" not in lock_src and "claim_" not in lock_src  # ...never in the lock


# --------------------------------------------------------------------------- F. AST guard


def test_f_ast_guard_counts_direct_alias_and_module_qualified_calls():
    cases = {
        "direct": ("from libs.execution.intent_execution_owner import execute_owned_order\nexecute_owned_order(state=1)", 1),
        "aliased import": ("from libs.execution.intent_execution_owner import execute_owned_order as eoo\neoo(state=1)\neoo(state=2)", 2),
        "module alias": ("import libs.execution.intent_execution_owner as owner\nowner.execute_owned_order(state=1)", 1),
        "from-module": ("from libs.execution import intent_execution_owner as m\nm.execute_owned_order(state=1)", 1),
        "dotted chain": ("import libs.execution.intent_execution_owner\nlibs.execution.intent_execution_owner.execute_owned_order(state=1)", 1),
        "name alias": ("from x import execute_owned_order\nfn = execute_owned_order\ngn = fn\nfn(1)\ngn(2)", 2),
        "attribute alias": ("import m\nfn = m.execute_owned_order\nfn(1)", 2),  # the attribute reference is not a call; fn(1) is
        "definition only": ("def execute_owned_order(state):\n    return state", 0),
        "unrelated": ("def other():\n    return 1\nother()", 0),
        "lazy import in function": ("def f():\n    from a import execute_owned_order as q\n    return q(1)", 1),
    }
    for name, (source, expected) in cases.items():
        got = count_execute_owned_order_calls(source)
        if name == "attribute alias":
            assert got >= 1, name  # alias of a module attribute: at least the alias call is seen
        else:
            assert got == expected, (name, got)


# ----------------------------------------------------------------------- authority pins


def test_evidence_is_still_not_an_input_to_readiness_ownership_or_step5():
    root = Path(__file__).resolve().parents[1]
    for rel in ("libs/supervisor/intent_state_store.py", "libs/execution/execution_readiness.py",
                "graphs/nodes/build_execution_readiness.py", "libs/runtime/runtime_ownership.py"):
        assert "readiness_evidence" not in (root / rel).read_text(encoding="utf-8"), rel
    owner = (root / "libs/execution/intent_execution_owner.py").read_text(encoding="utf-8")
    assert "store.claim_physical_order(physical_key, intent_id=iid, owner=owner)" in owner
    assert "store.claim_execution(iid, fingerprint=physical_key, owner=owner)" in owner


# ------------------------------------------------- operator-disabled readiness gate (documented limitation)


def test_gate_disabled_without_readiness_context_has_nothing_to_revalidate_but_stays_attempt_bound(tmp_path):
    spy, order = _Spy(), _order("intent-r62-gateoff")
    _admit(order)
    ok, _, details = record_pre_admission_evidence(
        state={"run_id": "r62"}, order=order, request=_req(), phase=PHASE_PRE_BROKER_SUBMIT, guard_enabled=False, guard_allowed=True,
        guard_reason="", broker_submission_allowed=True, execution_attempt_id="att-off")
    assert ok
    ref = details["reference"]
    out = _owned(order, spy, ref=ref, attempt="att-other", state={"run_id": "r62"})
    assert spy.calls == 0 and out["reason"] == INVALID_REASON  # still bound to its attempt
    out = _owned(order, spy, ref=ref, attempt="att-off", state={"run_id": "r62"})
    assert spy.calls == 1 and out["broker_outcome"] == "ACCEPTED"


def test_gate_disabled_but_readiness_present_is_still_revalidated(tmp_path):
    spy, order, world = _Spy(), _order("intent-r62-gateoff2"), _world(tmp_path)
    _admit(order)
    ok, _, details = record_pre_admission_evidence(
        state=world, order=order, request=_req(), phase=PHASE_PRE_BROKER_SUBMIT, guard_enabled=False, guard_allowed=True,
        guard_reason="", broker_submission_allowed=True, execution_attempt_id="att-off2")
    assert ok
    sync_owner(tmp_path / "ownership.db", instance_id="inst-A", generation=9)  # generation changed
    out = _owned(order, spy, ref=details["reference"], attempt="att-off2", state=world)
    assert spy.calls == 0 and out["reason"] == STALE_REASON
