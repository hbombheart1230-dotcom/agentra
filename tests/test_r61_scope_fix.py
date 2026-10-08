"""R6.1 -- scope fix: every production-capable BUY/SELL mutation path needs R6 evidence, the final
mutation choke point (execute_owned_order) verifies it, and evidence appends are interprocess-atomic.

Call graph (traced, not assumed) of execute_owned_order callers:
  1. graphs/nodes/execute_from_packet.py   main BUY/SELL (live loop)     -> R6_COVERED (pre-admission evidence)
  2. graphs/nodes/execute_from_packet.py   upper-limit CANCEL            -> not BUY/SELL exposure
  3. graphs/nodes/execute_from_packet.py   unfilled-order-recovery CANCEL-> not BUY/SELL exposure
  4. graphs/nodes/execute_order.py         legacy node, BUY/SELL capable -> R6_COVERED (shared helper + guard)
  5. libs/skills/runner.py                 order.place mutation          -> STRUCTURALLY_BLOCKED w/o evidence ref
     (reached via ToolFacade.order_execute / ExecutorAgent.execute_order from the approval flow)
  6. libs/approval/service.py              approve() / auto-admission    -> R6_COVERED (readiness_state) else blocked
"""

from __future__ import annotations

import json
import multiprocessing
import os
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from libs.execution import readiness_evidence as r6
from libs.execution.readiness_evidence import (
    INVALID_REASON,
    PHASE_PRE_BROKER_SUBMIT,
    REQUIRED_REASON,
    WRITE_FAILED_REASON,
    ReadinessEvidenceWriteError,
    append_readiness_evidence,
    build_readiness_evidence_record,
    record_pre_admission_evidence,
)

from _r6_helpers import sync_owner, write_snapshot

ROOT = Path(__file__).resolve().parents[1]


# ------------------------------------------------------------------------------ helpers


class _Spy:
    def __init__(self) -> None:
        self.calls = 0

    def execute(self, req, *, auth_token=None):  # type: ignore[no-untyped-def]
        from libs.core.api_response import ApiResponse
        from libs.execution.executors.base import ExecutionResult

        self.calls += 1
        return ExecutionResult(
            response=ApiResponse(status_code=200, ok=True, payload={"return_code": "0", "ord_no": "R61"}, error_code=None, error_message=None, raw_text=""),
            meta={"executor": "real", "broker_outcome": "ACCEPTED"},
        )


@pytest.fixture(autouse=True)
def _real_mode(monkeypatch, tmp_path):
    monkeypatch.setenv("EXECUTION_MODE", "real")
    monkeypatch.setenv("KIWOOM_MODE", "mock")
    monkeypatch.setenv("EXECUTION_ENABLED", "true")
    monkeypatch.setenv("APPROVAL_MODE", "manual")
    monkeypatch.setenv("EXECUTION_READINESS_GATE_ENABLED", "true")
    monkeypatch.setenv("INTENT_STATE_DB_PATH", str(tmp_path / "intent_state.db"))
    monkeypatch.setenv("REPORTS_ROOT", str(tmp_path / "reports"))
    monkeypatch.setenv("EXECUTION_READINESS_EVIDENCE_ROOT", str(tmp_path / "evidence"))
    monkeypatch.setenv("RUNTIME_OWNERSHIP_DB_PATH", str(tmp_path / "ownership.db"))
    monkeypatch.setenv("EXECUTION_READINESS_SNAPSHOT_PATH", str(tmp_path / "readiness_snapshot.json"))
    monkeypatch.delenv("AUTO_APPROVE", raising=False)
    monkeypatch.delenv("SYMBOL_ALLOWLIST", raising=False)


def _catalog(tmp_path: Path) -> str:
    p = tmp_path / "catalog.jsonl"
    rows = [
        {"api_id": "kt10000", "method": "POST", "path": "/api/dostk/ordr",
         "params": {"body": ["stk_cd", "ord_qty", "ord_uv", "trde_tp", "cond_uv", "dmst_stex_tp"]}},
    ]
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return str(p)


def _readiness_state(tmp_path: Path, *, ready: bool = True) -> dict[str, Any]:
    from graphs.nodes.build_execution_readiness import build_execution_readiness

    class _Claims:
        def list_active_physical_claims(self, *, limit=200):
            return []

    state = {
        "run_id": "run-r61",
        "runtime_ownership": {"instance_id": "inst-r61", "generation": 5, "recovery_required": False, "acquired_at": time.time()},
        "portfolio_snapshot": {"cash": 1e7, "positions": [], "_health": {"reader_ok": bool(ready)}},
        "open_order_snapshot": {"rows": [], "_health": {"reader_ok": True, "fetched_epoch": int(time.time())}},
        "intent_state_store": _Claims(),
        "execution_readiness_evidence_root": str(tmp_path / "evidence"),
    }
    state = build_execution_readiness(state)
    # canonical owner row + persisted readiness snapshot (the revalidation inputs for paths without state)
    sync_owner(tmp_path / "ownership.db", instance_id="inst-r61", generation=5)
    write_snapshot(tmp_path / "readiness_snapshot.json", state["execution_readiness"])
    return state


def _records(tmp_path: Path) -> list[dict[str, Any]]:
    root = tmp_path / "evidence"
    return [json.loads(line) for f in sorted(root.glob("*.jsonl")) for line in f.read_text(encoding="utf-8").splitlines() if line.strip()]


def _facade(tmp_path: Path, spy: _Spy):
    from libs.tools.tool_facade import ToolFacade

    facade = ToolFacade(catalog=_catalog(tmp_path), event_log=str(tmp_path / "events.jsonl"), intent_store=str(tmp_path / "intents.jsonl"))
    facade.runner.executor = spy
    return facade


def _runner(tmp_path: Path, spy: _Spy):
    from libs.core.settings import Settings
    from libs.skills.runner import CompositeSkillRunner

    runner = CompositeSkillRunner(settings=Settings.from_env(env_path="__missing__.env"), catalog_path=_catalog(tmp_path),
                                  event_log_path=str(tmp_path / "events.jsonl"))
    runner.executor = spy
    return runner


def _store():
    from libs.supervisor.intent_state_store import SQLiteIntentStateStore

    return SQLiteIntentStateStore(os.environ["INTENT_STATE_DB_PATH"])


def _assert_not_admitted(iid: str) -> None:
    """Creation leaves the intent pending_approval; admission is the approved/executing/executed transition."""
    row = _store().get_state(iid)
    assert row is None or row["state"] == "pending_approval", row


# ------------------------------------------------------- A. skills runner (STRUCTURALLY_BLOCKED)


def test_a_skills_runner_cannot_broker_submit_without_r6_evidence(tmp_path):
    spy = _Spy()
    result = _runner(tmp_path, spy).run(
        run_id="r61-a", skill="order.place",
        args={"side": "buy", "symbol": "005930", "qty": 1, "order_type": "market", "trde_tp": "3", "intent_id": "intent-r61-a"},
    )
    assert spy.calls == 0
    assert result.action == "error"
    assert result.meta["blocked_reason"] == REQUIRED_REASON and result.meta["broker_api_called"] is False


def test_a2_skills_runner_rejects_a_forged_evidence_reference(tmp_path):
    spy = _Spy()
    forged = {"record_id": "r6-forged", "day": "2026-10-06", "intent_id": "intent-r61-a2", "execution_attempt_id": "att-a2"}
    result = _runner(tmp_path, spy).run(
        run_id="r61-a2", skill="order.place",
        args={"side": "buy", "symbol": "005930", "qty": 1, "order_type": "market", "trde_tp": "3", "intent_id": "intent-r61-a2",
              "readiness_evidence": forged, "execution_attempt_id": "att-a2"},
    )
    assert spy.calls == 0 and result.meta["blocked_reason"] == INVALID_REASON


# ------------------------------------------------------------------ B. approval service


def test_b_approval_service_blocks_real_buy_without_runtime_readiness_before_admission(tmp_path):
    spy = _Spy()
    facade = _facade(tmp_path, spy)
    created = facade.order_place_intent(side="buy", symbol="005930", qty=1, order_type="market")
    iid = created["decision"]["intent"]["intent_id"]
    out = facade.approve_intent(intent_id=iid)
    assert out["ok"] is False and out["reason"] == "readiness_evidence_required"
    assert spy.calls == 0
    _assert_not_admitted(iid)  # no admission may happen before the evidence contract succeeds


# ---------------------------------------------------------- D. valid evidence: behaviour unchanged


def test_d_approval_service_with_runtime_readiness_persists_evidence_then_executes(tmp_path):
    spy = _Spy()
    facade = _facade(tmp_path, spy)
    created = facade.order_place_intent(side="buy", symbol="005930", qty=1, order_type="market")
    iid = created["decision"]["intent"]["intent_id"]
    out = facade.approve_intent(intent_id=iid, readiness_state=_readiness_state(tmp_path))
    assert out["ok"] is True and out["status"] == "executed"
    assert spy.calls == 1
    (rec,) = _records(tmp_path)
    assert rec["intent_id"] == iid and rec["phase"] == PHASE_PRE_BROKER_SUBMIT and rec["source"] == "approval_service"
    assert rec["execution_readiness_ready"] is True and rec["guard_verdict"] == "ALLOW" and rec["side"] == "BUY"


def test_d2_approval_service_respects_the_readiness_guard_when_not_ready(tmp_path):
    spy = _Spy()
    facade = _facade(tmp_path, spy)
    created = facade.order_place_intent(side="buy", symbol="005930", qty=1, order_type="market")
    iid = created["decision"]["intent"]["intent_id"]
    out = facade.approve_intent(intent_id=iid, readiness_state=_readiness_state(tmp_path, ready=False))
    assert out["ok"] is False and spy.calls == 0
    assert [r["guard_verdict"] for r in _records(tmp_path)] == ["BLOCK"]
    _assert_not_admitted(iid)


def test_d3_approval_auto_mode_requires_evidence_before_admission(tmp_path, monkeypatch):
    monkeypatch.setenv("APPROVAL_MODE", "auto")
    spy = _Spy()
    facade = _facade(tmp_path, spy)
    out = facade.order_place_intent(side="buy", symbol="005930", qty=1, order_type="market")
    assert out["execution"]["reason"].startswith(REQUIRED_REASON) and spy.calls == 0
    iid = out["decision"]["intent"]["intent_id"]
    _assert_not_admitted(iid)


def test_d4_approval_auto_mode_with_runtime_readiness_still_executes(tmp_path, monkeypatch):
    monkeypatch.setenv("APPROVAL_MODE", "auto")
    spy = _Spy()
    facade = _facade(tmp_path, spy)
    out = facade.order_place_intent(side="buy", symbol="005930", qty=1, order_type="market", readiness_state=_readiness_state(tmp_path))
    assert spy.calls == 1 and len(_records(tmp_path)) == 1


def test_d5_mock_mode_is_unchanged(tmp_path, monkeypatch):
    monkeypatch.setenv("EXECUTION_MODE", "mock")
    spy = _Spy()
    facade = _facade(tmp_path, spy)
    created = facade.order_place_intent(side="buy", symbol="005930", qty=1, order_type="market")
    iid = created["decision"]["intent"]["intent_id"]
    out = facade.approve_intent(intent_id=iid)
    assert out["status"] == "executed" and spy.calls == 1 and _records(tmp_path) == []


# --------------------------------------------------------------- C. execute_order node


def _order_node_state(tmp_path: Path, **extra):
    return {
        "catalog_path": _catalog(tmp_path),
        "order_api_id": "kt10000",
        "intent": "buy",
        "context": {"stk_cd": "005930", "ord_qty": "1", "ord_uv": "1000", "trde_tp": "0", "cond_uv": "", "dmst_stex_tp": "KRX"},
        "risk_context": {},
        "unknown_quarantine_guard_path": str(tmp_path / "quarantine"),
        **extra,
    }


def test_c_execute_order_node_cannot_broker_submit_without_readiness_evidence(tmp_path, monkeypatch):
    import graphs.nodes.execute_order as node

    spy = _Spy()
    monkeypatch.setattr(node, "get_executor", lambda *a, **k: spy)
    out = node.execute_order(_order_node_state(tmp_path, execution_readiness_evidence_root=str(tmp_path / "evidence")))
    assert spy.calls == 0
    assert out["execution"]["allowed"] is False and out["execution"]["reason"] == "execution_readiness_missing"
    assert [r["guard_verdict"] for r in _records(tmp_path)] == ["BLOCK"]


def test_c2_execute_order_node_with_valid_readiness_persists_evidence_then_executes(tmp_path, monkeypatch):
    import graphs.nodes.execute_order as node

    spy = _Spy()
    monkeypatch.setattr(node, "get_executor", lambda *a, **k: spy)
    state = _order_node_state(tmp_path, **_readiness_state(tmp_path))
    state["intent_id"] = "intent-r61-c2"
    out = node.execute_order(state)
    assert spy.calls == 1 and out["execution"]["broker_outcome"] == "ACCEPTED"
    (rec,) = _records(tmp_path)
    assert rec["source"] == "execute_order" and rec["phase"] == PHASE_PRE_BROKER_SUBMIT


# ---------------------------------------------------- E. direct execute_owned_order (choke point)


def _direct_order(iid: str, qty: int = 3) -> dict[str, Any]:
    return {"intent_id": iid, "action": "BUY", "symbol": "005930", "qty": qty, "price": 100, "order_type": "market", "trde_tp": "3"}


def _prep_request(api_id: str = "kt10000"):
    from libs.catalog.api_request_builder import PreparedRequest

    return PreparedRequest(api_id, "POST", "/api/dostk/ordr", {}, {}, {"stk_cd": "005930", "ord_qty": "3"})


def _admit(order: dict[str, Any]) -> None:
    from libs.execution.intent_admission import admit_order_intent

    admit_order_intent(state={"run_id": "r61"}, order=order, source="test_policy")


def _owned(order, request, spy, *, evidence=None, state=None, attempt=None):
    from graphs.nodes.execute_from_packet import _normalize_execution
    from libs.execution.intent_execution_owner import execute_owned_order

    return execute_owned_order(
        state=state or {"run_id": "r61"}, order=order, request=request, executor=spy, readiness_evidence=evidence,
        execution_attempt_id=attempt,
        normalize=lambda r: _normalize_execution(allowed=True, execution_result=r, allow_result=None, order=order),
    )


def _evidence_for(tmp_path, order, *, guard_allowed=True, attempt="att-1", state=None):
    world = state or _readiness_state(tmp_path)
    ok, _, details = record_pre_admission_evidence(
        state=world, order=order, request=_prep_request(), phase=PHASE_PRE_BROKER_SUBMIT, guard_enabled=True,
        guard_allowed=guard_allowed, guard_reason="", broker_submission_allowed=guard_allowed, execution_attempt_id=attempt)
    assert ok
    return world, details["reference"]


def test_e_execute_owned_order_without_evidence_fails_closed(tmp_path):
    spy = _Spy()
    order = _direct_order("intent-r61-e")
    _admit(order)
    out = _owned(order, _prep_request(), spy)
    assert spy.calls == 0
    assert out["broker_outcome"] == "NOT_SENT" and out["reason"] == REQUIRED_REASON
    assert _store().get_state("intent-r61-e")["state"] != "executing", "no Step5C claim may be taken without evidence"


def test_e2_execute_owned_order_with_valid_evidence_proceeds(tmp_path):
    spy = _Spy()
    order = _direct_order("intent-r61-e2")
    _admit(order)
    world, ref = _evidence_for(tmp_path, order, attempt="att-e2")
    out = _owned(order, _prep_request(), spy, evidence=ref, state=world, attempt="att-e2")
    assert spy.calls == 1 and out["broker_outcome"] == "ACCEPTED"


@pytest.mark.parametrize("mutate", ["wrong_intent", "wrong_qty", "block_verdict", "unknown_record", "wrong_attempt", "no_attempt"])
def test_e3_invalid_evidence_fails_closed(tmp_path, mutate):
    spy = _Spy()
    order = _direct_order(f"intent-r61-e3-{mutate}", qty=4)
    _admit(order)
    guard_allowed = mutate != "block_verdict"
    world, ref = _evidence_for(tmp_path, order, guard_allowed=guard_allowed, attempt="att-e3")
    ref = dict(ref)
    submit, attempt = dict(order), "att-e3"
    if mutate == "wrong_intent":
        submit["intent_id"] = "intent-r61-other"
        _admit(submit)
    elif mutate == "wrong_qty":
        submit["qty"] = 5
        _admit(submit)
    elif mutate == "unknown_record":
        ref["record_id"] = "r6-" + "0" * 32
    elif mutate == "wrong_attempt":
        attempt = "att-other"
    elif mutate == "no_attempt":
        attempt = None
    out = _owned(submit, _prep_request(), spy, evidence=ref, state=world, attempt=attempt)
    assert spy.calls == 0 and out["broker_outcome"] == "NOT_SENT"
    assert out["reason"] in (INVALID_REASON, REQUIRED_REASON)


def test_e4_cancel_modify_mock_and_read_paths_do_not_require_evidence(tmp_path, monkeypatch):
    spy = _Spy()
    cancel = {"intent_id": "intent-r61-cancel", "action": "CANCEL", "symbol": "005930", "qty": 1, "orig_ord_no": "0001", "order_type": "market", "price": 0}
    from libs.execution.readiness_evidence import require_readiness_evidence_for_order

    assert require_readiness_evidence_for_order(state={}, order=cancel, request=_prep_request("kt10003"), evidence=None) == (True, "")
    assert require_readiness_evidence_for_order(state={}, order=cancel, request=_prep_request("kt10002"), evidence=None) == (True, "")
    monkeypatch.setenv("EXECUTION_MODE", "mock")
    assert require_readiness_evidence_for_order(state={}, order=_direct_order("x"), request=_prep_request(), evidence=None) == (True, "")
    assert spy.calls == 0


# ------------------------------------------------------------------ F. canonical path still passes


def test_f_canonical_execute_from_packet_still_passes_with_evidence_reference(tmp_path):
    from graphs.nodes.execute_from_packet import execute_from_packet

    spy = _Spy()
    state = _readiness_state(tmp_path)
    state.update(executor=spy, catalog_path=_catalog(tmp_path))
    state["decision_packet"] = {
        "intent": {"action": "BUY", "symbol": "217590", "qty": 61, "order_api_id": "ORDER_SUBMIT", "order_type": "market"},
        "risk": {"open_positions": 0}, "exec_context": {},
    }
    out = execute_from_packet(state)
    assert spy.calls == 1 and out["execution"]["broker_outcome"] == "ACCEPTED"
    (rec,) = _records(tmp_path)
    assert out["execution"]["readiness_evidence"]["record_id"] == rec["record_id"]


# ------------------------------------------------------------- G/H/I. concurrent appends (processes)


def _sample(intent_id: str, *, computed_at: int = 1_790_000_000, now_epoch: float = 1_790_000_100.0, reason: str = "",
            attempt: str = "att-1") -> dict[str, Any]:
    order = {"intent_id": intent_id, "action": "BUY", "symbol": "217590", "qty": 41, "order_type": "market"}
    state = {
        "run_id": "r",
        "execution_readiness": {"ready": True, "reasons": [], "runtime_instance_id": "i", "ownership_generation": 5, "recovery_required": False,
                                  "portfolio_reconciled": True, "open_orders_reconciled": True, "orphan_claim_count": 0},
        "execution_readiness_computed_at_epoch": computed_at,
    }
    return build_readiness_evidence_record(
        state=state, order=order, phase=PHASE_PRE_BROKER_SUBMIT, guard_enabled=True, guard_allowed=True, guard_reason=reason,
        broker_submission_allowed=True, execution_mode="real", now_epoch=now_epoch, execution_attempt_id=attempt)


def _worker(root: str, record: dict[str, Any], barrier, queue) -> None:
    barrier.wait()
    try:
        queue.put(append_readiness_evidence(record, root=Path(root)))
    except Exception as exc:  # pragma: no cover - reported to the parent
        queue.put({"error": f"{type(exc).__name__}: {exc}"})


def _run_workers(root: Path, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    context = multiprocessing.get_context("spawn")
    barrier, queue = context.Barrier(len(records)), context.Queue()
    processes = [context.Process(target=_worker, args=(str(root), rec, barrier, queue)) for rec in records]
    for p in processes:
        p.start()
    results = [queue.get(timeout=60) for _ in processes]
    for p in processes:
        p.join(30)
        assert p.exitcode == 0
    return results


def _lines(root: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for f in sorted(root.glob("*.jsonl")) for line in f.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_g_two_processes_same_intent_same_attempt_yield_exactly_one_record(tmp_path):
    record = _sample("intent-r61-g")
    results = _run_workers(tmp_path, [record] * 4)
    assert all("error" not in r for r in results), results
    assert sorted(r["written"] for r in results) == [False, False, False, True]
    assert {r["record_id"] for r in results} == {record["record_id"]}
    rows = _lines(tmp_path)
    assert len(rows) == 1 and rows[0]["intent_sequence"] == 1
    assert [r["intent_sequence"] for r in results if r["duplicate"]] == [1, 1, 1]  # deterministic duplicate answer


def test_h_concurrent_different_intents_all_persist(tmp_path):
    records = [_sample(f"intent-r61-h{i}") for i in range(4)]
    results = _run_workers(tmp_path, records)
    assert all(r.get("written") for r in results), results
    rows = _lines(tmp_path)
    assert sorted(r["intent_id"] for r in rows) == sorted(r["intent_id"] for r in records)
    assert all(r["intent_sequence"] == 1 for r in rows) and len({r["record_id"] for r in rows}) == 4
    assert all(r6._record_hash_ok(r) for r in rows)


def test_i_concurrent_same_intent_later_attempts_get_unique_sequences(tmp_path):
    records = [_sample("intent-r61-i", computed_at=1_790_000_000 + i, now_epoch=1_790_000_100.0 + i, attempt=f"att-{i}") for i in range(4)]
    results = _run_workers(tmp_path, records)
    assert all(r.get("written") for r in results), results
    rows = _lines(tmp_path)
    assert sorted(r["intent_sequence"] for r in rows) == [1, 2, 3, 4]
    assert len({r["record_id"] for r in rows}) == 4


def test_g2_sequential_replay_is_deterministic(tmp_path):
    first = append_readiness_evidence(_sample("intent-r61-g2"), root=tmp_path)
    again = append_readiness_evidence(_sample("intent-r61-g2"), root=tmp_path)
    later = append_readiness_evidence(_sample("intent-r61-g2", computed_at=1_790_000_050, attempt="att-2"), root=tmp_path)
    assert (first["written"], again["written"], later["written"]) == (True, False, True)
    assert (first["intent_sequence"], again["intent_sequence"], later["intent_sequence"]) == (1, 1, 2)


# ----------------------------------------------------------- J. partial / torn writes


def test_j_partial_write_is_never_valid_evidence_and_blocks_submission(tmp_path, monkeypatch):
    from graphs.nodes.execute_from_packet import execute_from_packet

    def torn_write(fd: int, payload: bytes) -> None:
        os.write(fd, payload[: len(payload) // 2])
        raise OSError("disk full mid-write")

    monkeypatch.setattr(r6, "_write_all", torn_write)
    spy = _Spy()
    state = _readiness_state(tmp_path)
    state.update(executor=spy, catalog_path=_catalog(tmp_path))
    state["decision_packet"] = {"intent": {"action": "BUY", "symbol": "217590", "qty": 62, "order_api_id": "ORDER_SUBMIT", "order_type": "market"},
                                "risk": {"open_positions": 0}, "exec_context": {}}
    out = execute_from_packet(state)
    assert spy.calls == 0 and out["execution"]["reason"] == WRITE_FAILED_REASON
    path = next((tmp_path / "evidence").glob("*.jsonl"))
    assert path.read_bytes() and r6._read_valid_records(path) == []  # the torn fragment is not valid evidence


def test_j2_torn_tail_is_isolated_and_later_evidence_is_valid(tmp_path):
    path = tmp_path / f"{r6._day_of(1_790_000_100.0)}.jsonl"
    path.write_bytes(b'{"schema_version":"execution_readiness_evidence.v1","record_id":"r6-torn"')  # no newline
    result = append_readiness_evidence(_sample("intent-r61-j2"), root=tmp_path)
    assert result["written"] is True and result["intent_sequence"] == 1
    valid = r6._read_valid_records(path)
    assert [row["intent_id"] for row in valid] == ["intent-r61-j2"]


def test_j3_readback_verification_failure_is_a_write_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(r6, "_write_all", lambda fd, payload: os.write(fd, b"\n"))  # writes garbage instead of the record
    with pytest.raises(ReadinessEvidenceWriteError):
        append_readiness_evidence(_sample("intent-r61-j3"), root=tmp_path)


def test_j4_tampered_record_is_not_valid_evidence(tmp_path):
    result = append_readiness_evidence(_sample("intent-r61-j4"), root=tmp_path)
    path = Path(result["path"])
    path.write_text(path.read_text(encoding="utf-8").replace('"quantity":41', '"quantity":4100'), encoding="utf-8")
    assert r6._read_valid_records(path) == []


# ---------------------------------------------------------------- K. lock contention


def _live_foreign_lock(tmp_path, record, *, age_sec=3600):
    """A lock held by THIS live test process (so: a live, identity-verified owner) that is very old."""
    from libs.runtime.live_loop_lock import _process_start_identity

    day = r6._day_of(record["recorded_at_epoch"])
    lock = tmp_path / f"{day}.jsonl.lock"
    lock.write_text(json.dumps({
        "pid": os.getpid(), "process_start_identity": _process_start_identity(os.getpid()), "owner_token": "other-writer",
        "acquired_at": int(time.time()) - age_sec, "host_id": r6._host_id()}), encoding="utf-8")
    old = time.time() - age_sec
    os.utime(lock, (old, old))
    return lock


def test_k_lock_contention_is_bounded_and_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(r6, "LOCK_WAIT_SEC", 0.3)
    record = _sample("intent-r61-k")
    lock = _live_foreign_lock(tmp_path, record)
    started = time.monotonic()
    with pytest.raises(ReadinessEvidenceWriteError, match="evidence_lock_timeout"):
        append_readiness_evidence(record, root=tmp_path)
    assert time.monotonic() - started < 3.0
    assert lock.exists(), "a live owner's lock must survive however old it is"
    assert not list(tmp_path.glob("*.jsonl")), "nothing may be written while the lock is held"


def test_k2_lock_contention_blocks_broker_submission(tmp_path, monkeypatch):
    from graphs.nodes.execute_from_packet import execute_from_packet

    monkeypatch.setattr(r6, "LOCK_WAIT_SEC", 0.2)
    real_append = r6.append_readiness_evidence

    def with_lock_held(record, *, root):
        _live_foreign_lock(Path(root), record)
        return real_append(record, root=root)

    monkeypatch.setattr(r6, "append_readiness_evidence", with_lock_held)
    spy = _Spy()
    state = _readiness_state(tmp_path)
    state.update(executor=spy, catalog_path=_catalog(tmp_path))
    state["decision_packet"] = {"intent": {"action": "BUY", "symbol": "217590", "qty": 63, "order_api_id": "ORDER_SUBMIT", "order_type": "market"},
                                "risk": {"open_positions": 0}, "exec_context": {}}
    out = execute_from_packet(state)
    assert spy.calls == 0 and out["execution"]["reason"] == WRITE_FAILED_REASON


# --------------------------------------------------------- M/N. authority and data-integrity pins


def test_m_step5c_step5d_calls_and_authority_separation_unchanged():
    owner = (ROOT / "libs" / "execution" / "intent_execution_owner.py").read_text(encoding="utf-8")
    assert "store.claim_physical_order(physical_key, intent_id=iid, owner=owner)" in owner
    assert "store.claim_execution(iid, fingerprint=physical_key, owner=owner)" in owner
    assert "store.finish_execution(iid, owner=owner" in owner
    for rel in ("libs/supervisor/intent_state_store.py", "libs/execution/execution_readiness.py", "graphs/nodes/build_execution_readiness.py",
                "libs/runtime/runtime_ownership.py"):
        assert "readiness_evidence" not in (ROOT / rel).read_text(encoding="utf-8"), rel


def test_n_yfinance_changes_unchanged():
    support = (ROOT / "libs" / "market" / "yfinance_support.py").read_text(encoding="utf-8")
    assert "DataSourceDependencyError" in support and "dependency_missing:" in support
    assert "yfinance==" in (ROOT / "requirements.txt").read_text(encoding="utf-8")


def test_all_execute_owned_order_callers_are_accounted_for():
    """Fails when a NEW production caller of execute_owned_order appears without a conscious disposition.

    Alias-aware (R6.2): direct calls, `from ... import execute_owned_order as x`, module-qualified calls and
    simple name aliases are counted. Arbitrary dynamic dispatch is intentionally out of scope."""
    from _r6_helpers import count_execute_owned_order_calls

    callers = []
    for base in ("libs", "graphs", "apps", "scripts"):
        for path in (ROOT / base).rglob("*.py"):
            n = count_execute_owned_order_calls(path.read_text(encoding="utf-8-sig"))
            if n:
                callers.append((path.relative_to(ROOT).as_posix(), n))
    assert sorted(callers) == [
        ("graphs/nodes/execute_from_packet.py", 3),  # 1 BUY/SELL (evidence) + 2 CANCEL
        ("graphs/nodes/execute_order.py", 1),        # evidence via shared helper
        ("libs/skills/runner.py", 1),                # evidence reference required (choke point)
    ]
