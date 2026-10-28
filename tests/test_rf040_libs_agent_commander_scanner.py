"""RF-040 libs/agent C2/C3: legacy Commander orchestration and static Scanner.

All collaborators are in-memory fakes; the scanner is pinned to
``candidate_source=static`` so the Kiwoom provider is never invoked.
Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import pytest

from libs.agent.commander import CommandResult, Commander
from libs.agent.scanner import Scanner
from libs.agent.strategist import Plan


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


class _Strat:
    def plan(self, *, context):
        return Plan(thesis="t", constraints={}, themes=["x"], candidates=["A"])


class _LegacyStrat:
    def make_plan(self, *, context):
        return {"thesis": "legacy"}


class _Scan:
    def __init__(self, out):
        self.out = out

    def scan(self, *, plan, context):
        return self.out


class _Exec:
    def __init__(self):
        self.calls = []

    def submit(self, *, intent, approval_mode, execution_enabled):
        self.calls.append((intent, approval_mode, execution_enabled))
        return {"decision": {"status": "ok"}}


class _Mon:
    def __init__(self):
        self.calls = []

    def update(self, *, intents, decisions, executions, context):
        self.calls.append((intents, decisions, executions))


class _LegacyMon:
    def __init__(self):
        self.calls = []

    def update(self, *, plan, scan, execution, context):
        self.calls.append((plan, scan, execution))


class _Rep:
    def build(self, *, run_id, context, plan, intents, decisions, executions):
        return {"run_id": run_id, "n": len(intents)}


class _LegacyRep:
    def build(self, **kw):
        raise TypeError("legacy reporter has no run_id signature")

    def build_report(self, *, plan, scan, execution, context):
        return {"legacy": True}


def _cmd(strat=None, scan=None, mon=None, rep=None, ex=None):
    return Commander(strategist=strat or _Strat(), scanner=_Scan(scan), monitor=mon or _Mon(),
                     reporter=rep or _Rep(), executor=ex or _Exec())


def test_list_scan_submits_first_dict_intent_with_safe_defaults():
    ex = _Exec()
    res = _cmd(scan=["junk", {"side": "buy"}, {"side": "sell"}], ex=ex).run(context={"run_id": "r1"})
    _eq(ex.calls, [({"side": "buy"}, "manual", False)])
    _eq(res.scan, {"intents": [{"side": "buy"}, {"side": "sell"}]})
    _eq(res.intent, {"side": "buy"})
    _eq(res.execution, {"decision": {"status": "ok"}})
    _eq(res.report, {"run_id": "r1", "n": 2})
    _eq(res.plan["thesis"], "t")
    _eq(type(res), CommandResult)


def test_dict_scan_variants_normalize_to_intents():
    _eq(_cmd(scan={"intent": {"a": 1}}).run().scan["intents"], [{"a": 1}])
    _eq(_cmd(scan={"intent": [{"a": 1}, 2]}).run().scan["intents"], [{"a": 1}])
    _eq(_cmd(scan={"intents": [{"a": 1}, "x"], "k": 9}).run().scan, {"intents": [{"a": 1}], "k": 9})
    _eq(_cmd(scan={"nothing": 1}).run().scan["intents"], [])


def test_no_intent_means_no_execution_and_empty_monitor_payload():
    ex, mon = _Exec(), _Mon()
    for scan in (None, 5, []):
        res = _cmd(scan=scan, ex=ex, mon=mon).run()
        _eq((res.intent, res.execution), (None, None))
    _eq(ex.calls, [])
    _eq(mon.calls[0], ([], [], []))


def test_approval_and_execution_flags_pass_through_and_run_id_default():
    ex = _Exec()
    res = _cmd(scan=[{"s": 1}], ex=ex).run(approval_mode="auto", execution_enabled=True)
    _eq(ex.calls[0][1:], ("auto", True))
    _eq(len(res.report["run_id"]), 32)


def test_legacy_strategist_monitor_reporter_signatures_still_work():
    mon = _LegacyMon()
    res = _cmd(strat=_LegacyStrat(), scan=[], mon=mon, rep=_LegacyRep()).run()
    _eq(res.report, {"legacy": True})
    _eq(len(mon.calls), 1)
    _eq(res.plan, {"thesis": "legacy"})


def test_provided_intents_pass_through_scanner():
    intents = [{"side": "buy"}]
    _eq(Scanner().scan(plan=Plan("t", {}), context={"intents": intents}), intents)


def test_static_scanner_ranks_by_score_and_keeps_intents_empty():
    plan = Plan("t", {}, themes=["Hot"], candidates=["005930", "000660", "bad"])
    out = Scanner().scan(plan=plan, context={
        "candidate_source": "static",
        "candidate_scores": {"000660": 2.5, "005930": 1.0},
    })
    _eq(out["intents"], [])
    _eq([r["symbol"] for r in out["ranked"]], ["000660", "005930", "BAD"])
    _eq([r["score"] for r in out["ranked"]], [2.5, 1.0, 0.0])
    _eq(out["candidate_source"], "static")
    _eq(out["themes"], ["Hot"])
    _eq(out["candidates"], ["005930", "000660", "BAD"])
    _eq((out["candidate_pool_size"], out["top_stock"], out["score"], out["top_score"]), (3, "000660", 2.5, 2.5))


def test_static_scanner_empty_plan_yields_empty_ranking():
    out = Scanner().scan(plan=Plan("t", {}), context={"candidate_source": "static"})
    _eq((out["ranked"], out["top_stock"], out["score"], out["candidate_pool_size"]), ([], None, None, 0))


def test_run_canonical_delegates_to_runtime(monkeypatch):
    import graphs.commander_runtime as rt

    seen = {}

    def fake(state, *, mode, graph_runner, decide, execute):
        seen.update(state=state, mode=mode)
        return {"ok": True}

    monkeypatch.setattr(rt, "run_commander_runtime", fake)
    src = {"a": 1}
    _eq(_cmd().run_canonical(state=src), {"ok": True})
    _eq(seen["state"], {"a": 1})
    if seen["state"] is src:
        raise AssertionError("state must be copied")
