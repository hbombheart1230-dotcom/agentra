"""RF-040 executor_agent: fake-injected contract (runner/supervisor/intent_store/ApprovalService are all fakes).

``ApprovalService`` is replaced at module level because its default constructor resolves the canonical
intent-state DB; the real Settings/Supervisor/Step5C ownership paths are never built or reached, and
nothing talks to a broker. MAX_ORDER_* are set through monkeypatch. Explicit raises keep the checks live
under ``python -O``.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict

import pytest

from libs.agent.executor import executor_agent as ea
from libs.execution.executors.base import ExecutionDisabledError


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


@dataclass
class _Decision:
    status: str
    intent: Dict[str, Any] | None = None
    reason: str = ""


@dataclass
class _RunOut:
    ok: bool = True
    run_id: str = ""
    skill: str = ""
    args: Dict[str, Any] = field(default_factory=dict)


class _Runner:
    def __init__(self):
        self.calls = []

    def run(self, *, run_id, skill, args):
        self.calls.append((run_id, skill, args))
        return _RunOut(run_id=run_id, skill=skill, args=dict(args))


class _Supervisor:
    def __init__(self, status="needs_approval"):
        self.status = status
        self.seen = []

    def create_intent(self, raw):
        self.seen.append(dict(raw))
        return _Decision(status=self.status, intent={**raw, "intent_id": "i-1"} if self.status != "rejected" else None)


class _Store:
    def __init__(self):
        self.saved = []

    def save(self, intent):
        self.saved.append(dict(intent))


class _Approvals:
    def __init__(self, store):
        self.store = store
        self.approved = []

    def approve(self, *, intent_id, execution_enabled, execute_fn, readiness_state):
        self.approved.append((intent_id, execution_enabled))
        return {"approved": intent_id, "enabled": execution_enabled}

    def preview(self, *, intent_id=None):
        return {"preview": intent_id}

    def reject(self, *, intent_id=None, reason="rejected"):
        return {"rejected": intent_id, "reason": reason}

    def list_intents(self, limit=10):
        return {"limit": limit}


@pytest.fixture()
def build(tmp_path, monkeypatch):
    monkeypatch.setattr(ea, "ApprovalService", _Approvals)
    for name in ("MAX_ORDER_QTY", "MAX_ORDER_NOTIONAL", "EXECUTION_ENABLED"):
        monkeypatch.delenv(name, raising=False)

    def make(status="needs_approval"):
        runner, sup, store = _Runner(), _Supervisor(status), _Store()
        agent = ea.ExecutorAgent(runner=runner, supervisor=sup, intent_store=store, intent_store_path=tmp_path / "intents.jsonl")
        return agent, runner, sup, store

    return make


def test_unwrap_intent_shapes():
    _eq(ea._unwrap_intent({"intent": {"a": 1}, "status": "x"}), {"a": 1})
    _eq(ea._unwrap_intent({"intent_id": "z"}), {"intent_id": "z"})
    _eq(ea._unwrap_intent("junk"), None)
    _eq(ea._unwrap_intent({"intent": "not-dict", "k": 1}), {"intent": "not-dict", "k": 1})


def test_store_readers_skip_blank_and_corrupt_lines(build, tmp_path):
    agent, *_ = build()
    _eq((agent._load_all_rows(), agent.last_intent()), ([], None))
    (tmp_path / "intents.jsonl").write_text(
        json.dumps({"intent_id": "a"}) + "\n\n{broken\n" + json.dumps({"intent": {"intent_id": "b", "action": "BUY", "symbol": "005930", "qty": 2}}) + "\n",
        encoding="utf-8")
    _eq([r.get("intent_id") for r in agent._load_all_rows() if "intent_id" in r], ["a"])
    _eq(agent.last_intent()["intent_id"], "b")
    _eq(agent._summarize_intent({"intent": {"intent_id": "b", "action": "BUY", "symbol": "005930", "qty": 2}}),
        {"intent_id": "b", "action": "BUY", "symbol": "005930", "qty": 2, "order_type": None, "price": None, "rationale": "", "created_epoch": None})


def test_manual_mode_saves_the_intent_and_never_executes(build):
    agent, runner, sup, store = build()
    out = agent.submit_order_intent(side="Buy", symbol="005930", qty="3", price=70000, rationale="r")
    _eq((out["decision"]["status"], sup.seen[0]["action"], sup.seen[0]["qty"], sup.seen[0]["order_type"]), ("needs_approval", "BUY", 3, "market"))
    _eq([s["intent_id"] for s in store.saved], ["i-1"])
    _eq(runner.calls, [])
    sell = agent.submit_order_intent(side="anything", symbol="x", qty=1)
    _eq(sup.seen[1]["action"], "SELL")                                   # any non-"buy" side maps to SELL
    _eq(runner.calls, [])


def test_auto_without_execution_enabled_is_blocked_and_rejected_is_not_sent(build):
    agent, runner, sup, store = build()
    out = agent.submit_order_intent(side="buy", symbol="005930", qty=1, approval_mode="AUTO", execution_enabled=False)
    if "execution is blocked" not in out["note"]:
        raise AssertionError(out)
    _eq(runner.calls, [])
    rej, runner2, _, store2 = build("rejected")
    out2 = rej.submit_order_intent(side="buy", symbol="005930", qty=1, approval_mode="auto", execution_enabled=True)
    _eq(out2["execution"], {"ok": False, "broker_outcome": "NOT_SENT", "reason": "supervisor_rejected"})
    _eq((runner2.calls, store2.saved), ([], []))                          # nothing persisted or sent for a rejected intent


@pytest.mark.parametrize("env,intent,message", [
    ({"MAX_ORDER_QTY": "5"}, {"action": "BUY", "symbol": "A", "qty": 6, "price": 1}, "exceeds MAX_ORDER_QTY"),
    ({"MAX_ORDER_NOTIONAL": "1000"}, {"action": "BUY", "symbol": "A", "qty": 1}, "Missing price"),
    ({"MAX_ORDER_NOTIONAL": "1000"}, {"action": "BUY", "symbol": "A", "qty": 2, "price": 600}, "exceeds MAX_ORDER_NOTIONAL"),
    ({"MAX_ORDER_NOTIONAL": "1000"}, {"action": "SELL", "symbol": "A", "qty": 1, "price": "abc"}, "Invalid price"),
])
def test_order_guards_raise_before_the_runner_is_called(build, monkeypatch, env, intent, message):
    agent, runner, *_ = build()
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    with pytest.raises(ExecutionDisabledError, match=message):
        agent.execute_order(intent=intent)
    _eq(runner.calls, [])


def test_execute_order_maps_skill_args_for_the_fake_runner(build, monkeypatch):
    agent, runner, *_ = build()
    monkeypatch.setenv("MAX_ORDER_QTY", "junk")                         # unparsable limits are ignored (0 = disabled)
    out = agent.execute_order(intent={"intent": {"action": "SELL", "symbol": "005930", "qty": 4, "order_type": "limit", "price": 71000, "intent_id": "i-9"}})
    _eq(len(runner.calls), 1)
    run_id, skill, args = runner.calls[0]
    _eq(skill, "order.place")
    _eq(len(run_id), 32)
    _eq((args["side"], args["symbol"], args["qty"], args["order_type"], args["price"], args["trde_tp"], args["intent_id"]),
        ("sell", "005930", 4, "limit", 71000, "0", "i-9"))
    _eq(out["skill"], "order.place")
    agent.execute_order(intent={"action": "BUY", "symbol": "x"})
    _eq((runner.calls[1][2]["trde_tp"], runner.calls[1][2]["qty"], runner.calls[1][2]["order_type"]), ("3", 1, "market"))


def test_approve_defaults_execution_flag_from_env_and_delegates(build, monkeypatch):
    agent, *_ = build()
    _eq(agent.approve(intent_id="i-1"), {"approved": "i-1", "enabled": False})
    monkeypatch.setenv("EXECUTION_ENABLED", " YES ")
    _eq(agent.approve(intent_id="i-2")["enabled"], True)
    _eq(agent.approve(intent_id="i-3", execution_enabled=False)["enabled"], False)
    _eq(agent.preview(intent_id="p"), {"preview": "p"})
    _eq(agent.reject(intent_id="r", reason="no"), {"rejected": "r", "reason": "no"})
    _eq(agent.list_intents(limit=2), {"limit": 2})


class _AdmitApprovals(_Approvals):
    """Fake of the Step5C-adjacent admission helpers; the real ApprovalService/canonical DB is never touched."""

    evidence = (True, "", None)
    admission_error = None

    def __init__(self, store):
        super().__init__(store)
        self.admitted = []

    def prepare_readiness_evidence(self, intent, *, readiness_state, source):
        self.seen_readiness = (readiness_state, source)
        return type(self).evidence

    def admit_pre_approved_intent(self, intent, *, source):
        self.admitted.append((dict(intent), source))
        return type(self).admission_error


def _auto(build, monkeypatch, *, evidence=(True, "", None), admission_error=None):
    monkeypatch.setattr(ea, "ApprovalService", _AdmitApprovals)
    _AdmitApprovals.evidence, _AdmitApprovals.admission_error = evidence, admission_error
    agent, runner, sup, store = build()
    monkeypatch.setattr(ea, "ApprovalService", _AdmitApprovals)
    agent.approvals = _AdmitApprovals(store)
    return agent, runner


def test_auto_enabled_blocks_when_readiness_evidence_is_missing(build, monkeypatch):
    agent, runner = _auto(build, monkeypatch, evidence=(False, "readiness_missing", None))
    out = agent.submit_order_intent(side="buy", symbol="005930", qty=1, approval_mode="auto", execution_enabled=True, readiness_state={"x": 1})
    _eq(out["execution"], {"ok": False, "broker_outcome": "NOT_SENT", "reason": "readiness_missing"})
    _eq((runner.calls, agent.approvals.admitted, agent.approvals.seen_readiness), ([], [], ({"x": 1}, "executor_agent_auto")))


def test_auto_enabled_blocks_when_admission_fails_and_executes_only_after_admission(build, monkeypatch):
    agent, runner = _auto(build, monkeypatch, admission_error="not_admitted")
    out = agent.submit_order_intent(side="buy", symbol="005930", qty=1, approval_mode="auto", execution_enabled=True)
    _eq(out["execution"]["reason"], "not_admitted")
    _eq(runner.calls, [])
    ok_agent, ok_runner = _auto(build, monkeypatch, evidence=(True, "", {"execution_attempt_id": "att-1"}))
    res = ok_agent.submit_order_intent(side="buy", symbol="005930", qty=1, approval_mode="auto", execution_enabled=True)
    _eq(len(ok_runner.calls), 1)
    args = ok_runner.calls[0][2]
    _eq((args["intent_id"], args["execution_attempt_id"], args["readiness_evidence"]), ("i-1", "att-1", {"execution_attempt_id": "att-1"}))
    _eq(ok_agent.approvals.admitted[0][1], "executor_agent_auto")
    _eq(res["execution"]["skill"], "order.place")


def test_auto_enabled_without_intent_id_skips_admission_and_executes_current_contract(build, monkeypatch):
    # Current behavior (pinned, not endorsed): admission/readiness run only when the supervisor's intent carries an id.
    agent, runner = _auto(build, monkeypatch)

    class NoIdSupervisor:
        def create_intent(self, raw):
            return _Decision(status="needs_approval", intent={**raw, "intent_id": ""})

    agent.supervisor = NoIdSupervisor()
    agent.submit_order_intent(side="buy", symbol="005930", qty=1, approval_mode="auto", execution_enabled=True)
    _eq((len(runner.calls), agent.approvals.admitted), (1, []))


def test_notional_within_limit_falls_through_to_the_runner(build, monkeypatch):
    agent, runner, *_ = build()
    monkeypatch.setenv("MAX_ORDER_NOTIONAL", "1000")
    agent.execute_order(intent={"action": "BUY", "symbol": "A", "qty": 2, "price": 400})
    _eq(len(runner.calls), 1)
