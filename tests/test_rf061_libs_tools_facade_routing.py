"""RF-061 libs/tools C2/C3: tool_facade.ToolFacade read-side, routing and dispatch args.

The facade is built via ``__new__`` with in-memory fakes for runner/approvals
and an intent store file under tmp_path, so the supervisor, ApprovalService,
skill runner, broker and every real order path are never reached
(Step5C SAFETY_HOLD: order_place_intent is NOT exercised).
Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from libs.tools.tool_facade import ToolFacade


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


@dataclass
class _Out:
    ok: bool = True


class _Runner:
    def __init__(self):
        self.calls = []

    def run(self, *, run_id, skill, args):
        self.calls.append((skill, args))
        return _Out()


class _Approvals:
    def __init__(self):
        self.calls = []

    def approve(self, **kw):
        self.calls.append(("approve", kw))
        return {"approved": True}

    def preview(self, **kw):
        self.calls.append(("preview", kw))
        return {"preview": True}

    def reject(self, **kw):
        self.calls.append(("reject", kw))
        return {"rejected": True}


def _facade(tmp_path, rows=None, raw_lines=None):
    f = ToolFacade.__new__(ToolFacade)
    f.runner, f.approvals = _Runner(), _Approvals()
    f.intent_store_path = tmp_path / "intents.jsonl"
    lines = [json.dumps(r) for r in (rows or [])] + list(raw_lines or [])
    if lines:
        f.intent_store_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return f


def test_load_rows_skips_blank_and_corrupt_lines(tmp_path):
    f = _facade(tmp_path, rows=[{"a": 1}], raw_lines=["", "{bad", '{"b": 2}'])
    _eq(f._load_all_rows(), [{"a": 1}, {"b": 2}])
    _eq(f._last_row(), {"b": 2})
    _eq(_facade(tmp_path / "none")._load_all_rows(), [])
    _eq(_facade(tmp_path / "none")._last_intent(), None)


def test_summarize_intent_accepts_wrapped_and_raw(tmp_path):
    f = _facade(tmp_path)
    want = {"intent_id": "i", "action": "BUY", "symbol": "S", "qty": 1, "order_type": None,
            "price": None, "rationale": "", "created_epoch": None}
    _eq(f._summarize_intent({"ts": 1, "intent": {"intent_id": "i", "action": "BUY", "symbol": "S", "qty": 1}}), want)
    _eq(f._summarize_intent({"intent_id": "i", "action": "BUY", "symbol": "S", "qty": 1}), want)
    _eq(f._summarize_intent("junk")["intent_id"], None)


def test_list_intents_latest_row_wins_newest_first_and_limit(tmp_path):
    rows = [
        {"ts": 1, "intent": {"intent_id": "a", "action": "BUY", "symbol": "S1", "qty": 1}},
        {"ts": 5, "intent_id": "a", "status": "rejected", "reason": "x", "intent": {"intent_id": "a", "action": "BUY", "symbol": "S1", "qty": 1}},
        {"ts": 3, "intent": {"intent_id": "b", "action": "SELL", "symbol": "S2", "qty": 2}},
        {"ts": 9, "note": "no id"},
    ]
    out = _facade(tmp_path, rows=rows).list_intents(limit=5)
    _eq((out["ok"], out["count"]), (True, 2))
    _eq([(i["intent_id"], i["status"], i["reason"], i["ts"]) for i in out["intents"]],
        [("a", "rejected", "x", 5), ("b", "stored", None, 3)])
    _eq(_facade(tmp_path, rows=rows).list_intents(limit=0)["count"], 1)  # limit floors at 1
    _eq(_facade(tmp_path / "none").list_intents(), {"ok": True, "count": 0, "intents": []})


def test_latest_row_by_intent_id_prefers_newer_ts(tmp_path):
    rows = [{"ts": 1, "intent_id": "a", "status": "old"}, {"ts": 2, "intent_id": "a", "status": "new"},
            {"ts": 3, "intent": {"intent_id": "b"}}]
    f = _facade(tmp_path, rows=rows)
    _eq(f._latest_row("a")["status"], "new")
    _eq(f._latest_row("zzz"), None)


def test_append_intent_marker_writes_jsonl_with_optional_execution(tmp_path):
    f = _facade(tmp_path / "sub")
    f._append_intent_marker(intent_id="i", status="rejected", reason="r", intent={"k": 1})
    f._append_intent_marker(intent_id="i", status="done", reason=None, intent={}, execution={"ok": True})
    r1, r2 = f._load_all_rows()
    _eq((r1["intent_id"], r1["status"], r1["reason"], "execution" in r1), ("i", "rejected", "r", False))
    _eq(r2["execution"], {"ok": True})


def test_run_korean_commands_route_to_approvals_with_ids(tmp_path):
    f = _facade(tmp_path)
    f.run("승인?")
    f.run("미리보기 abc ")
    f.run("거절")
    f.run("취소")
    f.run("거절 xyz")
    _eq(f.approvals.calls, [
        ("preview", {"intent_id": None}), ("preview", {"intent_id": "abc"}),
        ("reject", {"intent_id": None, "reason": "rejected"}),
        ("reject", {"intent_id": None, "reason": "rejected"}),
        ("reject", {"intent_id": "xyz", "reason": "rejected"}),
    ])


def test_run_approve_passes_execute_fn_that_dispatches_order_execute(tmp_path, monkeypatch):
    monkeypatch.setenv("EXECUTION_ENABLED", "false")
    f = _facade(tmp_path)
    seen = {}
    f.approvals.approve = lambda **kw: seen.update(kw) or {"ok": 1}
    _eq(f.run("승인"), {"ok": 1})
    _eq((seen["intent_id"], seen["execution_enabled"], seen["readiness_state"]), (None, False, None))
    f.run("승인 iid1")
    _eq(seen["intent_id"], "iid1")
    # execute_fn only reaches the fake runner
    seen["execute_fn"]({"action": "BUY", "symbol": "S", "qty": 2, "intent_id": "iid1"})
    _eq(f.runner.calls[0][0], "order.place")


def test_run_list_quote_help_and_unknown_tool(tmp_path):
    f = _facade(tmp_path)
    _eq(f.run("최근주문")["ok"], True)
    f.run("005930 현재가")
    _eq(f.runner.calls[-1], ("market.quote", {"symbol": "005930"}))
    out = f.run("아무말")  # routes to the 'help' tool, which ToolFacade does not implement
    _eq(out, {"ok": False, "message": "Unknown tool: help"})


def test_order_execute_forwards_identity_and_market_limit_args(tmp_path):
    f = _facade(tmp_path)
    f.order_execute(intent={"ts": 1, "intent": {"action": "sell", "symbol": "S", "qty": None, "order_type": "MARKET",
                                                 "intent_id": "iid", "readiness_evidence": {"e": 1}, "execution_attempt_id": "att"}})
    f.order_execute(intent={"action": "BUY", "symbol": "S", "qty": "3", "order_type": "limit", "price": 7})
    (s1, a1), (s2, a2) = f.runner.calls
    _eq((s1, s2), ("order.place", "order.place"))
    _eq(a1, {"side": "sell", "symbol": "S", "qty": 1, "order_type": "MARKET", "price": None, "trde_tp": "3",
             "intent_id": "iid", "readiness_evidence": {"e": 1}, "execution_attempt_id": "att"})
    _eq((a2["side"], a2["qty"], a2["trde_tp"], a2["intent_id"], a2["readiness_evidence"]), ("buy", 3, "0", "", None))
    # empty/unwrappable intent defaults to a sell of qty 1 with empty identity (documented current behaviour)
    f.order_execute(intent={})
    _eq(f.runner.calls[-1][1]["side"], "sell")
    _eq(f.runner.calls[-1][1]["intent_id"], "")
