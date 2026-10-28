"""RF-061 tool_facade: ``order_place_intent`` auto/manual plumbing and approval-mode env precedence with fakes.

The facade is built with ``__new__`` and fake runner/supervisor/intent_store/approvals; ``order_execute`` is
replaced on the instance by a recorder, so the real Step5C ownership path, Settings, Supervisor and broker are
never constructed or reached. Env flags go through monkeypatch. Explicit raises keep the checks live under
``python -O``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import pytest

from libs.tools import tool_facade as tf


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


@dataclass
class _Decision:
    status: str
    intent: Dict[str, Any] | None = None


class _Supervisor:
    def __init__(self, status="needs_approval", intent_id="i-1"):
        self.status, self.intent_id, self.seen = status, intent_id, []

    def create_intent(self, raw):
        self.seen.append(dict(raw))
        return _Decision(self.status, {**raw, "intent_id": self.intent_id} if self.status != "rejected" else None)


class _Store:
    def __init__(self):
        self.saved = []

    def save(self, intent):
        self.saved.append(dict(intent))


class _Approvals:
    def __init__(self, evidence=(True, "", None), admission=None):
        self.evidence, self.admission, self.admitted, self.sources = evidence, admission, [], []

    def prepare_readiness_evidence(self, intent, *, readiness_state, source):
        self.sources.append(("evidence", source, readiness_state))
        return self.evidence

    def admit_pre_approved_intent(self, intent, *, source):
        self.sources.append(("admit", source, None))
        self.admitted.append(dict(intent))
        return self.admission


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    for name in ("APPROVAL_MODE", "AUTO_APPROVE", "EXECUTION_ENABLED"):
        monkeypatch.delenv(name, raising=False)


def _facade(supervisor=None, approvals=None):
    f = tf.ToolFacade.__new__(tf.ToolFacade)
    f.supervisor = supervisor or _Supervisor()
    f.intent_store = _Store()
    f.approvals = approvals or _Approvals()
    f.executed = []
    f.order_execute = lambda *, intent: f.executed.append(dict(intent)) or {"ok": True, "fake": True}
    return f


@pytest.mark.parametrize("env,expected", [
    ({}, "manual"),
    ({"APPROVAL_MODE": "AUTO"}, "auto"),
    ({"APPROVAL_MODE": "manual", "AUTO_APPROVE": "true"}, "manual"),           # APPROVAL_MODE wins over legacy
    ({"APPROVAL_MODE": "junk", "AUTO_APPROVE": "auto"}, "auto"),
    ({"AUTO_APPROVE": "manual"}, "manual"),
    ({"AUTO_APPROVE": "YES"}, "auto"),
    ({"AUTO_APPROVE": "0"}, "manual"),
])
def test_approval_mode_precedence(monkeypatch, env, expected):
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    _eq(tf._approval_mode(), expected)


def test_execution_enabled_truthy_values(monkeypatch):
    _eq(tf._execution_enabled(), False)
    for v in ("1", "TRUE", " yes ", "y", "On"):
        monkeypatch.setenv("EXECUTION_ENABLED", v)
        _eq(tf._execution_enabled(), True)
    monkeypatch.setenv("EXECUTION_ENABLED", "nope")
    _eq(tf._execution_enabled(), False)


def test_manual_mode_saves_but_never_executes_even_when_execution_is_enabled(monkeypatch):
    monkeypatch.setenv("EXECUTION_ENABLED", "true")
    f = _facade()
    out = f.order_place_intent(side="BUY", symbol="005930", qty="2", price=70000)
    _eq(out["decision"]["status"], "needs_approval")
    _eq((f.supervisor.seen[0]["action"], f.supervisor.seen[0]["qty"], f.supervisor.seen[0]["order_type"]), ("BUY", 2, "market"))
    _eq([s["intent_id"] for s in f.intent_store.saved], ["i-1"])
    _eq(f.executed, [])
    _eq(_facade().order_place_intent(side="x", symbol="s", qty=1)["decision"]["intent"]["action"], "SELL")


def test_auto_mode_is_blocked_without_execution_enabled(monkeypatch):
    monkeypatch.setenv("APPROVAL_MODE", "auto")
    f = _facade()
    out = f.order_place_intent(side="buy", symbol="005930", qty=1)
    if "execution is blocked" not in out["note"]:
        raise AssertionError(out)
    _eq(f.executed, [])


def test_auto_enabled_rejected_decision_is_not_sent_and_not_persisted(monkeypatch):
    monkeypatch.setenv("APPROVAL_MODE", "auto")
    monkeypatch.setenv("EXECUTION_ENABLED", "1")
    f = _facade(_Supervisor(status="rejected"))
    out = f.order_place_intent(side="buy", symbol="005930", qty=1)
    _eq(out["execution"], {"ok": False, "broker_outcome": "NOT_SENT", "reason": "supervisor_rejected"})
    _eq((f.executed, f.intent_store.saved), ([], []))


def test_auto_enabled_gates_on_evidence_then_admission_before_execute(monkeypatch):
    monkeypatch.setenv("APPROVAL_MODE", "auto")
    monkeypatch.setenv("EXECUTION_ENABLED", "true")
    no_evidence = _facade(approvals=_Approvals(evidence=(False, "no_readiness", None)))
    _eq(no_evidence.order_place_intent(side="buy", symbol="s", qty=1, readiness_state={"r": 1})["execution"]["reason"], "no_readiness")
    _eq((no_evidence.executed, no_evidence.approvals.sources), ([], [("evidence", "tool_facade_auto", {"r": 1})]))
    refused = _facade(approvals=_Approvals(admission="not_admitted"))
    _eq(refused.order_place_intent(side="buy", symbol="s", qty=1)["execution"]["reason"], "not_admitted")
    _eq(refused.executed, [])
    good = _facade(approvals=_Approvals(evidence=(True, "", {"execution_attempt_id": "att-9"})))
    out = good.order_place_intent(side="buy", symbol="s", qty=1)
    _eq(out["execution"], {"ok": True, "fake": True})
    _eq((good.executed[0]["intent_id"], good.executed[0]["execution_attempt_id"], good.executed[0]["readiness_evidence"]),
        ("i-1", "att-9", {"execution_attempt_id": "att-9"}))
    _eq([s[0] for s in good.approvals.sources], ["evidence", "admit"])         # evidence is prepared BEFORE admission


def test_auto_enabled_without_an_intent_id_skips_evidence_and_admission_current_contract(monkeypatch):
    # Pinned current behavior, not endorsed: the id-less intent is executed without the evidence/admission step.
    monkeypatch.setenv("APPROVAL_MODE", "auto")
    monkeypatch.setenv("EXECUTION_ENABLED", "true")
    f = _facade(_Supervisor(intent_id=""))
    f.order_place_intent(side="buy", symbol="s", qty=1)
    _eq((len(f.executed), f.approvals.sources), (1, []))
