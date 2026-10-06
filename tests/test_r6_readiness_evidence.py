"""R6 -- immutable per-intent execution-readiness evidence.

Covers the evidence contract only: record content, append-only/idempotent persistence,
evidence-before-broker-submit ordering, fail-closed on evidence write failure, the authority
separation (evidence is never an input to readiness/execution/ownership/Step5C/Step5D), and that
existing guard / routing / strategy behaviour is unchanged.

The 2026-10-06 09:02 BUY / 09:05 SELL are NOT reconstructed here (R6 is prospective only).
"""

from __future__ import annotations

import copy
import json
import re
import time
from pathlib import Path
from typing import Any

import pytest

from graphs.nodes import execute_from_packet as efp
from graphs.nodes.build_execution_readiness import build_execution_readiness
from graphs.nodes.execute_from_packet import execute_from_packet
from libs.execution import readiness_evidence as r6
from libs.execution.readiness_evidence import (
    PHASE_GUARD_BLOCK,
    PHASE_PRE_BROKER_SUBMIT,
    WRITE_FAILED_REASON,
    ReadinessEvidenceWriteError,
    append_readiness_evidence,
    build_readiness_evidence_record,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _real_mode_gate_on(monkeypatch, tmp_path):
    # conftest disables the readiness gate project-wide; R6 tests opt back in.
    monkeypatch.setenv("EXECUTION_READINESS_GATE_ENABLED", "true")
    monkeypatch.setenv("EXECUTION_MODE", "real")
    monkeypatch.setenv("REPORTS_ROOT", str(tmp_path / "reports"))


class _Claims:
    def __init__(self, claims=None):
        self._claims = claims or []

    def list_active_physical_claims(self, *, limit=200):
        return list(self._claims)


class _RecordingExecutor:
    """Never touches a network. Records calls and what evidence existed AT call time."""

    def __init__(self, evidence_root: Path):
        self.calls: list[dict[str, Any]] = []
        self._root = evidence_root

    def execute(self, request):  # type: ignore[no-untyped-def]
        files = sorted(self._root.glob("*.jsonl")) if self._root.exists() else []
        lines = [json.loads(line) for f in files for line in f.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.calls.append(
            {
                "api_id": getattr(request, "api_id", None),
                "body": dict(getattr(request, "body", {}) or {}),
                "evidence_at_submit": lines,
            }
        )

        class _Result:
            payload = {"api_ok": True, "broker_code": "0000", "broker_message": "accepted", "order_id": "STUB-R6", "filled_qty": 0, "filled_price": None}

        return _Result()


def _catalog(tmp_path: Path) -> str:
    cat = tmp_path / "api_catalog.jsonl"
    cat.write_text(
        '{"api_id":"ORDER_SUBMIT","title":"order","method":"POST","path":"/orders","params":{},"_flags":{"callable":true}}\n',
        encoding="utf-8",
    )
    return str(cat)


def _state(
    tmp_path: Path,
    *,
    recovery_required: bool = False,
    instance_id: str = "inst-r6",
    generation: int = 5,
    portfolio_ok: bool = True,
    open_orders_ok: bool = True,
    orphan_claims=None,
    positions=None,
):
    now = int(time.time())
    state: dict[str, Any] = {
        "run_id": "run-r6",
        "runtime_ownership": {
            "instance_id": instance_id,
            "generation": generation,
            "recovery_required": recovery_required,
            "acquired_at": time.time(),
        },
        "portfolio_snapshot": {
            "cash": 10_000_000.0,
            "positions": positions or [],
            "_health": {"reader_ok": bool(portfolio_ok)},
        },
        "open_order_snapshot": {"rows": [], "_health": {"reader_ok": bool(open_orders_ok), "fetched_epoch": now}},
        "intent_state_store": _Claims(orphan_claims),
        "execution_readiness_evidence_root": str(tmp_path / "evidence"),
        "catalog_path": _catalog(tmp_path),
    }
    state = build_execution_readiness(state)
    state["executor"] = _RecordingExecutor(tmp_path / "evidence")
    return state


def _packet(*, action="BUY", symbol="217590", qty=41, meta=None, source=None):
    intent = {"action": action, "symbol": symbol, "qty": qty, "order_api_id": "ORDER_SUBMIT", "order_type": "market"}
    if meta:
        intent["meta"] = meta
    return {"intent": intent, "risk": {"open_positions": 0}, "exec_context": {}}


def _records(tmp_path: Path) -> list[dict[str, Any]]:
    root = tmp_path / "evidence"
    return [json.loads(line) for f in sorted(root.glob("*.jsonl")) for line in f.read_text(encoding="utf-8").splitlines() if line.strip()]


def _run(state, tmp_path, **packet_kwargs):
    state["decision_packet"] = _packet(**packet_kwargs)
    return execute_from_packet(state)


# ------------------------------------------------------------------ 1-3 ready / not ready / recovery


def test_r1_ready_true_writes_evidence_and_allows_submission(tmp_path):
    state = _state(tmp_path)
    assert state["execution_readiness"]["ready"] is True
    out = _run(state, tmp_path, qty=101)
    records = _records(tmp_path)
    assert [r["phase"] for r in records] == [PHASE_PRE_BROKER_SUBMIT]
    rec = records[0]
    assert rec["execution_readiness_ready"] is True
    assert rec["guard_verdict"] == "ALLOW" and rec["guard_enabled"] is True
    assert rec["broker_submission_allowed"] is True
    assert rec["evidence_only"] is True and rec["schema_version"] == "execution_readiness_evidence.v1"
    assert len(state["executor"].calls) == 1
    assert out["execution"]["readiness_evidence"]["record_id"] == rec["record_id"]


def test_r2_ready_false_writes_evidence_and_blocks_submission(tmp_path):
    state = _state(tmp_path, portfolio_ok=False)
    assert state["execution_readiness"]["ready"] is False
    out = _run(state, tmp_path, qty=102)
    records = _records(tmp_path)
    assert [r["phase"] for r in records] == [PHASE_GUARD_BLOCK]
    rec = records[0]
    assert rec["execution_readiness_ready"] is False
    assert rec["guard_verdict"] == "BLOCK" and rec["guard_reason"] == "execution_not_ready"
    assert rec["broker_submission_allowed"] is False
    assert "portfolio_not_reconciled" in " ".join(rec["execution_readiness_reasons"]) or rec["execution_readiness_reasons"]
    assert state["executor"].calls == []
    assert out["execution"]["allowed"] is False and out["execution"]["reason"] == "execution_not_ready"


def test_r3_recovery_required_is_recorded_and_guard_behaviour_preserved(tmp_path):
    # recovery_required stays True while evidence is unhealthy -> existing guard blocks as before.
    state = _state(tmp_path, recovery_required=True, portfolio_ok=False)
    assert state["execution_readiness"]["recovery_required"] is True
    out = _run(state, tmp_path, qty=103)
    rec = _records(tmp_path)[0]
    assert rec["recovery_required"] is True and rec["state_recovery_required"] is True
    assert rec["guard_verdict"] == "BLOCK"
    assert out["execution"]["reason"] == "execution_not_ready"
    assert state["executor"].calls == []


# --------------------------------------------------- 4-7 captured identity / reconciliation inputs


def test_r4_runtime_instance_id_captured(tmp_path):
    state = _state(tmp_path, instance_id="0979b3cd21d94b83")
    _run(state, tmp_path, qty=104)
    rec = _records(tmp_path)[0]
    assert rec["runtime_instance_id"] == "0979b3cd21d94b83"
    assert rec["state_runtime_instance_id"] == "0979b3cd21d94b83"


def test_r5_ownership_generation_captured(tmp_path):
    state = _state(tmp_path, generation=5)
    _run(state, tmp_path, qty=105)
    rec = _records(tmp_path)[0]
    assert rec["ownership_generation"] == 5 and rec["state_ownership_generation"] == 5
    assert rec["execution_readiness_generation"] == 5


def test_r6_portfolio_reconciliation_captured(tmp_path):
    ok = _state(tmp_path, portfolio_ok=True)
    _run(ok, tmp_path, qty=106)
    assert _records(tmp_path)[-1]["portfolio_reconciled"] is True
    bad = _state(tmp_path, portfolio_ok=False)
    _run(bad, tmp_path, qty=107)
    assert _records(tmp_path)[-1]["portfolio_reconciled"] is False


def test_r7_open_order_reconciliation_captured(tmp_path):
    ok = _state(tmp_path, open_orders_ok=True)
    _run(ok, tmp_path, qty=108)
    assert _records(tmp_path)[-1]["open_orders_reconciled"] is True
    bad = _state(tmp_path, open_orders_ok=False)
    _run(bad, tmp_path, qty=109)
    assert _records(tmp_path)[-1]["open_orders_reconciled"] is False


def test_readiness_computed_at_and_orphan_count_captured(tmp_path):
    state = _state(tmp_path)
    before = int(time.time())
    _run(state, tmp_path, qty=110)
    rec = _records(tmp_path)[0]
    assert rec["execution_readiness_computed_at_epoch"] is not None
    assert before - 5 <= rec["execution_readiness_computed_at_epoch"] <= int(time.time())
    assert rec["execution_readiness_computed_at"].startswith("20")
    assert rec["orphan_claim_count"] == 0


# ------------------------------------------------------------------------ 8 ordering


def test_r8_evidence_is_persisted_before_broker_submit(tmp_path):
    state = _state(tmp_path)
    _run(state, tmp_path, qty=111)
    call = state["executor"].calls[0]
    seen = [r for r in call["evidence_at_submit"] if r["phase"] == PHASE_PRE_BROKER_SUBMIT]
    assert len(seen) == 1, "evidence must already be durable when the broker is called"
    assert seen[0]["broker_submission_allowed"] is True
    assert seen[0]["recorded_at_epoch"] <= time.time()


def test_r8b_evidence_precedes_intent_admission(tmp_path, monkeypatch):
    from libs.execution import intent_admission

    order_of_events: list[str] = []
    real_admit = intent_admission.admit_order_intent
    real_append = r6.append_readiness_evidence

    def spy_admit(*args, **kwargs):
        order_of_events.append("admit")
        return real_admit(*args, **kwargs)

    def spy_append(*args, **kwargs):
        order_of_events.append("evidence")
        return real_append(*args, **kwargs)

    monkeypatch.setattr(intent_admission, "admit_order_intent", spy_admit)
    monkeypatch.setattr(r6, "append_readiness_evidence", spy_append)
    state = _state(tmp_path)
    _run(state, tmp_path, qty=112)
    assert order_of_events[:2] == ["evidence", "admit"]


# ----------------------------------------------------------------------- 9 fail-closed


def test_r9_evidence_write_failure_fails_closed_no_broker_submit(tmp_path, monkeypatch):
    def boom(*_a, **_k):
        raise ReadinessEvidenceWriteError("disk full")

    monkeypatch.setattr(r6, "append_readiness_evidence", boom)
    state = _state(tmp_path)
    out = _run(state, tmp_path, qty=113)
    assert state["executor"].calls == []
    assert out["execution"]["allowed"] is False
    assert out["execution"]["reason"] == WRITE_FAILED_REASON
    assert "disk full" in out["execution"]["readiness_evidence"]["error"]


def test_r9b_unwritable_evidence_location_fails_closed(tmp_path):
    state = _state(tmp_path)
    blocker = tmp_path / "evidence_is_a_file"
    blocker.write_text("x", encoding="utf-8")
    state["execution_readiness_evidence_root"] = str(blocker)  # a file, not a directory
    out = _run(state, tmp_path, qty=114)
    assert state["executor"].calls == []
    assert out["execution"]["reason"] == WRITE_FAILED_REASON


def test_r9c_evidence_failure_does_not_create_an_admitted_intent(tmp_path, monkeypatch):
    from libs.execution import intent_admission

    admitted: list[Any] = []
    monkeypatch.setattr(intent_admission, "admit_order_intent", lambda *a, **k: admitted.append(1))
    monkeypatch.setattr(r6, "append_readiness_evidence", lambda *a, **k: (_ for _ in ()).throw(ReadinessEvidenceWriteError("x")))
    state = _state(tmp_path)
    _run(state, tmp_path, qty=115)
    assert admitted == []


def test_r9d_block_path_evidence_failure_still_blocks(tmp_path, monkeypatch):
    monkeypatch.setattr(r6, "append_readiness_evidence", lambda *a, **k: (_ for _ in ()).throw(ReadinessEvidenceWriteError("x")))
    state = _state(tmp_path, portfolio_ok=False)
    out = _run(state, tmp_path, qty=116)
    assert out["execution"]["reason"] == "execution_not_ready"  # the existing block reason is preserved
    assert state["executor"].calls == []


# ------------------------------------------------------- 10 append-only / idempotency


def _sample_record(**overrides):
    order = {"intent_id": "intent-v1-test", "action": "BUY", "symbol": "217590", "qty": 41, "order_type": "market"}
    state = {
        "run_id": "r",
        "execution_readiness": {"ready": True, "reasons": [], "runtime_instance_id": "i", "ownership_generation": 5, "recovery_required": False,
                                  "portfolio_reconciled": True, "open_orders_reconciled": True, "orphan_claim_count": 0},
        "execution_readiness_computed_at_epoch": 1_790_000_000,
    }
    kwargs = dict(state=state, order=order, phase=PHASE_PRE_BROKER_SUBMIT, guard_enabled=True, guard_allowed=True, guard_reason="",
                  broker_submission_allowed=True, execution_mode="real", now_epoch=1_790_000_100.0)
    kwargs.update(overrides)
    return build_readiness_evidence_record(**kwargs)


def test_r10_duplicate_record_is_detected_and_not_written_twice(tmp_path):
    record = _sample_record()
    first = append_readiness_evidence(record, root=tmp_path)
    second = append_readiness_evidence(record, root=tmp_path)
    assert first["written"] is True and first["intent_sequence"] == 1
    assert second["written"] is False and second["duplicate"] is True
    lines = [line for f in tmp_path.glob("*.jsonl") for line in f.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == 1


def test_r10b_replayed_intent_gets_ordered_sequence_not_ambiguity(tmp_path):
    first = append_readiness_evidence(_sample_record(now_epoch=1_790_000_100.0, guard_reason="a"), root=tmp_path)
    second = append_readiness_evidence(_sample_record(now_epoch=1_790_000_160.0, guard_reason="b"), root=tmp_path)
    assert (first["intent_sequence"], second["intent_sequence"]) == (1, 2)
    rows = [json.loads(line) for f in tmp_path.glob("*.jsonl") for line in f.read_text(encoding="utf-8").splitlines()]
    assert [r["intent_sequence"] for r in rows] == [1, 2]
    assert rows[0]["record_id"] != rows[1]["record_id"]


def test_r10c_append_only_prior_records_remain_byte_identical(tmp_path):
    append_readiness_evidence(_sample_record(now_epoch=1_790_000_100.0, guard_reason="a"), root=tmp_path)
    path = next(tmp_path.glob("*.jsonl"))
    before = path.read_bytes()
    append_readiness_evidence(_sample_record(now_epoch=1_790_000_160.0, guard_reason="b"), root=tmp_path)
    after = path.read_bytes()
    assert after.startswith(before) and len(after) > len(before)
    rows = [json.loads(line) for line in after.decode("utf-8").splitlines()]
    for row in rows:
        content = {k: v for k, v in row.items() if k != "record_hash"}
        assert row["record_hash"] == r6._digest(content)  # tamper-evident per-record hash


def test_r10d_record_identity_is_deterministic():
    assert _sample_record()["record_id"] == _sample_record()["record_id"]
    assert _sample_record()["record_id"] != _sample_record(guard_allowed=False)["record_id"]


def test_evidence_module_never_overwrites_or_truncates():
    source = (ROOT / "libs" / "execution" / "readiness_evidence.py").read_text(encoding="utf-8")
    assert "os.O_APPEND" in source
    assert not re.search(r"open\([^)]*[\"']w", source) and "O_TRUNC" not in source and "write_text" not in source


# --------------------------------------------------- 11-14 BUY / SELL / probe / stop-loss paths


def test_r11_buy_path(tmp_path):
    state = _state(tmp_path)
    _run(state, tmp_path, action="BUY", qty=117)
    rec = _records(tmp_path)[0]
    assert (rec["side"], rec["symbol"], rec["quantity"]) == ("BUY", "217590", 117)
    assert state["executor"].calls and state["executor"].calls[0]["api_id"] == "ORDER_SUBMIT"


def test_r12_sell_path(tmp_path):
    positions = [{"symbol": "217590", "qty": 41, "avg_price": 18080.0, "current_price": 17900.0}]
    state = _state(tmp_path, positions=positions)
    _run(state, tmp_path, action="SELL", qty=41)
    rec = _records(tmp_path)[0]
    assert (rec["side"], rec["symbol"], rec["quantity"]) == ("SELL", "217590", 41)
    assert rec["phase"] == PHASE_PRE_BROKER_SUBMIT and len(state["executor"].calls) == 1


def test_r13_opening_rank1_controlled_probe_path(tmp_path):
    state = _state(tmp_path)
    meta = {"entry_reason": "opening_rank1_controlled_probe", "entry_signal_source": "monitor_intraday_entry"}
    _run(state, tmp_path, action="BUY", qty=118, meta=meta)
    rec = _records(tmp_path)[0]
    assert rec["correlation"]["entry_reason"] == "opening_rank1_controlled_probe"
    assert rec["correlation"]["entry_signal_source"] == "monitor_intraday_entry"
    assert rec["correlation"]["intent_id"] == rec["intent_id"] != ""
    assert rec["phase"] == PHASE_PRE_BROKER_SUBMIT and len(state["executor"].calls) == 1


def test_r14_stop_loss_path(tmp_path):
    positions = [{"symbol": "217590", "qty": 42, "avg_price": 18080.0, "current_price": 17900.0}]
    state = _state(tmp_path, positions=positions)
    meta = {"exit_reason": "stop_loss", "source": "monitor_exit_policy"}
    _run(state, tmp_path, action="SELL", qty=42, meta=meta)
    rec = _records(tmp_path)[0]
    assert rec["correlation"]["exit_reason"] == "stop_loss" and rec["side"] == "SELL"
    assert rec["phase"] == PHASE_PRE_BROKER_SUBMIT and len(state["executor"].calls) == 1


# ----------------------------------------------------- 15-19 behaviour / authority unchanged


def test_r15_existing_guard_reasons_preserved(tmp_path):
    missing = {"decision_packet": _packet(qty=119), "catalog_path": _catalog(tmp_path), "execution_readiness_evidence_root": str(tmp_path / "evidence")}
    out = execute_from_packet(missing)
    assert out["execution"]["reason"] == "execution_readiness_missing"  # unchanged block reason
    rec = _records(tmp_path)[0]
    assert rec["readiness_present"] is False and rec["guard_verdict"] == "BLOCK"


def test_r16_r17_step5c_step5d_unchanged_and_orphan_recorded(tmp_path):
    state = _state(tmp_path, orphan_claims=[{"physical_order_key": "k", "intent_id": "i"}])
    out = _run(state, tmp_path, qty=120)
    rec = _records(tmp_path)[0]
    assert rec["orphan_claim_count"] == 1
    assert out["execution"]["reason"] == "execution_not_ready"  # Step5D orphan still blocks, as before
    assert state["executor"].calls == []
    for name in ("intent_execution_owner.py", "intent_state_store.py"):
        source = (ROOT / "libs" / "execution" / name if name.startswith("intent_exec") else ROOT / "libs" / "supervisor" / name).read_text(encoding="utf-8")
        assert "readiness_evidence" not in source  # Step5C/5D code does not know about evidence


def test_r18_broker_routing_unchanged(tmp_path):
    state = _state(tmp_path)
    _run(state, tmp_path, qty=121)
    (call,) = state["executor"].calls
    assert call["api_id"] == "ORDER_SUBMIT"
    assert str(call["body"].get("stk_cd")) in ("217590", "A217590") and str(call["body"].get("ord_qty")) == "121"


def test_r19_strategy_semantics_and_order_unchanged_by_evidence(tmp_path):
    order = {"intent_id": "intent-v1-x", "action": "BUY", "symbol": "217590", "qty": 41, "order_type": "market", "meta": {"score": 1.1}}
    state = {"run_id": "r", "execution_readiness": {"ready": True, "reasons": []}}
    snapshot_order, snapshot_state = copy.deepcopy(order), copy.deepcopy(state)
    record = build_readiness_evidence_record(state=state, order=order, phase=PHASE_PRE_BROKER_SUBMIT, guard_enabled=True,
                                             guard_allowed=True, guard_reason="", broker_submission_allowed=True, execution_mode="real")
    append_readiness_evidence(record, root=tmp_path)
    assert order == snapshot_order and state == snapshot_state  # evidence builder/writer are pure w.r.t. inputs


def test_evidence_is_never_an_authority_input():
    consumers = [
        ROOT / "libs" / "execution" / "execution_readiness.py",
        ROOT / "graphs" / "nodes" / "build_execution_readiness.py",
        ROOT / "libs" / "runtime" / "runtime_ownership.py",
        ROOT / "libs" / "runtime" / "live_loop_runner.py",
        ROOT / "libs" / "execution" / "intent_execution_owner.py",
        ROOT / "libs" / "supervisor" / "intent_state_store.py",
    ]
    for path in consumers:
        assert "readiness_evidence" not in path.read_text(encoding="utf-8"), path.name
    source = (ROOT / "graphs" / "nodes" / "execute_from_packet.py").read_text(encoding="utf-8")
    assert "append_readiness_evidence" in source and "read_readiness_evidence" not in source


def test_readiness_dict_and_guard_inputs_unchanged_by_r6(tmp_path):
    state = _state(tmp_path)
    assert set(state["execution_readiness"]) == {
        "ready", "reasons", "runtime_instance_id", "ownership_generation", "recovery_required", "orphan_claim_count",
        "portfolio_reconciled", "open_orders_reconciled", "config_valid", "execution_enabled",
    }
    assert isinstance(state["execution_readiness_computed_at_epoch"], int)  # separate additive evidence key


def test_mock_mode_and_cancel_do_not_require_or_write_evidence(tmp_path, monkeypatch):
    monkeypatch.setenv("EXECUTION_MODE", "mock")
    state = _state(tmp_path)
    ok, reason, details = efp._record_readiness_evidence(
        state, {"action": "BUY", "intent_id": "i"}, phase=PHASE_PRE_BROKER_SUBMIT, readiness_allowed=True,
        readiness_reason="", readiness_details={"enabled": False}, broker_submission_allowed=True)
    assert ok and details["enabled"] is False and _records(tmp_path) == []
    monkeypatch.setenv("EXECUTION_MODE", "real")
    ok, _, details = efp._record_readiness_evidence(
        state, {"action": "CANCEL", "intent_id": "i"}, phase=PHASE_PRE_BROKER_SUBMIT, readiness_allowed=True,
        readiness_reason="", readiness_details={"enabled": True}, broker_submission_allowed=True)
    assert ok and details["enabled"] is False and _records(tmp_path) == []
