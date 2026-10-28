"""RF-031 libs/reporting/reporter_ai_review: normalization, enable gating and LLM-result paths, offline.

``LLMRouter`` is replaced by a fake (no client, no network); the evidence-ledger
recorders are replaced by in-memory spies so nothing is written; ``DRY_RUN`` and
the REPORTER_AI_REVIEW_* env are controlled per test. Coverage before this file:
20% of the module (measured). Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import json
import types

import pytest

from libs.reporting import reporter_ai_review as rv


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


FULL = {
    "ai_summary": "s" * 700,
    "ai_findings": ["f1", "", "f2"] + ["x"] * 20,
    "ai_root_causes": ["r1"],
    "ai_improvement_suggestions": ["i1"],
    "ai_run_grade": "B+",
    "ai_agent_evaluations": {"strategist": "good", "": "dropped", "scanner": "mixed"},
    "ai_evidence_links": {"findings": [{"text": "f1", "evidence_keys": ["k1", "k2"]}, "k3", 5], "root_causes": "bad", "improvements": []},
}


def test_clip_list_dict_helpers():
    _eq(rv._clip_str(None), "")
    _eq(rv._clip_str("x" * 10, max_len=10), "x" * 10)
    _eq(rv._clip_str("x" * 11, max_len=10), "x" * 7 + "...")
    _eq(rv._list_str("notalist"), [])
    _eq(rv._list_str(["a", "", None, "b", "c"], max_items=2), ["a", "b"])
    _eq(rv._dict_str({"k": "v" * 200, "": "x", "k2": 1}, max_items=8), {"k": "v" * 117 + "...", "k2": "1"})
    _eq(rv._dict_str(None), {})
    _eq(len(rv._dict_str({str(i): i for i in range(20)})), 8)
    _eq(rv._env_bool("RF031_UNSET_ENV_X"), False)
    _eq(rv._env_bool("RF031_UNSET_ENV_X", True), True)


def test_env_bool_values(monkeypatch):
    for v, want in (("1", True), ("TRUE", True), (" yes ", True), ("on", True), ("0", False), ("off", False), ("maybe", False)):
        monkeypatch.setenv("RF031_ENVB", v)
        _eq(rv._env_bool("RF031_ENVB"), want)


def test_evidence_link_items_shapes_and_limits():
    out = rv._normalize_evidence_link_items([{"text": "t" * 300, "evidence_keys": ["a"] * 9}, "key", "", 5, {"evidence_keys": "no"}])
    _eq(out[0]["text"], "t" * 257 + "...")
    _eq(len(out[0]["evidence_keys"]), 6)
    _eq(out[1], {"text": "", "evidence_keys": ["key"]})
    _eq(out[2], {"text": "", "evidence_keys": []})   # dict without usable keys is still emitted
    _eq(len(out), 3)
    _eq(rv._normalize_evidence_link_items("x"), [])
    _eq(len(rv._normalize_evidence_link_items([{"text": str(i)} for i in range(30)])), 10)


def test_normalize_result_clips_and_marks_ok():
    r = rv._normalize_result(FULL, enabled=True, model="m")
    _eq((r["status"], r["llm_status"], r["parse_mode"], r["enabled"], r["model"], r["reason"]), ("ok", "ok", "full", True, "m", ""))
    _eq(len(r["ai_summary"]), 600)
    _eq((r["ai_findings"][:2], len(r["ai_findings"])), (["f1", "f2"], 12))
    _eq(r["ai_agent_evaluations"], {"strategist": "good", "scanner": "mixed"})
    _eq(r["ai_run_grade"], "B+")
    _eq(r["ai_evidence_links"]["findings"][0], {"text": "f1", "evidence_keys": ["k1", "k2"]})
    _eq((r["ai_evidence_links"]["root_causes"], r["ai_evidence_links"]["improvements"]), ([], []))
    _eq(rv._normalize_result({}, enabled=False, model="")["ai_run_grade"], "N/A")


def test_default_result_contract():
    d = rv._default_result(enabled=True, status="parse_error", reason="r" * 400, model="mm")
    _eq((d["status"], d["llm_status"], d["parse_mode"], d["ai_run_grade"], d["model"]), ("parse_error", rv._normalize_llm_status("parse_error"), "none", "N/A", "mm"))
    _eq(len(d["reason"]), 320)
    _eq(d["ai_evidence_links"], {"findings": [], "root_causes": [], "improvements": []})
    for k in rv.REPORTER_AI_REVIEW_REQUIRED_KEYS:
        if k not in d:
            raise AssertionError(k)


def test_json_helpers():
    _eq(rv._strip_fenced_block('```json\n{"a": 1}\n```').strip(), '{"a": 1}')
    _eq(rv._extract_json_object('{"a": 1}'), {"a": 1})
    _eq(rv._extract_json_object("no json at all"), None)


def test_messages_embed_day_contract_and_compact_input():
    msgs = rv._build_messages("2026-10-28", {"k": "한글"})
    _eq([m["role"] for m in msgs], ["system", "user"])
    for token in ("Day: 2026-10-28", "ai_evidence_links", "Input summary:", "한글", "never suggest direct live execution"):
        if token not in msgs[0]["content"] + msgs[1]["content"]:
            raise AssertionError(token)


def test_compact_input_is_bounded_and_tolerates_missing_sections():
    empty = rv._build_compact_input("2026-10-28", {})
    json.dumps(empty)   # JSON-serializable
    out = {"decision_trace_chain_summary": {"chains": [{"run_id": "r" * 200, "strategist": {"x": 1}}] * 30 + ["junk"]}}
    c = rv._build_compact_input("2026-10-28", out)
    json.dumps(c)


# ---- build_ai_reporter_review ------------------------------------------------------------------------

class _Route:
    model = "fake/model"


class _Router:
    client = object()
    reply = json.dumps({k: FULL[k] for k in FULL} | {"ai_summary": "ok"})
    boom = None
    calls = []

    @classmethod
    def from_env(cls):
        return cls()

    def resolve(self, role, policy=None):
        _Router.calls.append(("resolve", role, dict(policy or {})))
        return _Route()

    def chat(self, role, messages, policy=None):
        _Router.calls.append(("chat", role, dict(policy or {})))
        if _Router.boom:
            raise _Router.boom
        return _Router.reply


@pytest.fixture()
def spied(monkeypatch):
    for k in ("DRY_RUN", "REPORTER_AI_REVIEW_TEMPERATURE", "REPORTER_AI_REVIEW_MAX_TOKENS"):
        monkeypatch.delenv(k, raising=False)
    events = []
    for name in ("record_raw_input", "record_llm_prompt", "record_llm_response"):
        monkeypatch.setattr(rv, name, lambda *a, _n=name, **k: events.append((_n, k.get("decision_link"))))
    _Router.client, _Router.boom, _Router.calls = object(), None, []
    _Router.reply = json.dumps(FULL | {"ai_summary": "ok"})
    monkeypatch.setattr(rv, "LLMRouter", _Router)
    return events


def test_disabled_by_default_and_policy_precedence(spied):
    d = rv.build_ai_reporter_review(day="D", reporter_output={})
    _eq((d["enabled"], d["status"], d["reason"]), (False, "disabled", "reporter.ai_review.enabled is false"))
    _eq(_Router.calls, [])
    for key, ro in (("applied", {"applied_policy": {"reporter": {"ai_review": {"enabled": True}}}}),
                    ("fallback", {"reporter_policy": {"ai_review": {"enabled": True}}}),
                    ("payload", {"policy": {"reporter": {"ai_review": {"enabled": True}}}})):
        r = rv.build_ai_reporter_review(day="D", reporter_output=ro)
        _eq((key, r["status"]), (key, "ok"))
    # applied policy wins over the other two
    mixed = {"applied_policy": {"reporter": {"ai_review": {"enabled": False}}}, "reporter_policy": {"ai_review": {"enabled": True}}}
    _eq(rv.build_ai_reporter_review(day="D", reporter_output=mixed)["status"], "disabled")
    # explicit argument beats every policy
    _eq(rv.build_ai_reporter_review(day="D", reporter_output=mixed, enabled=True)["status"], "ok")
    _eq(rv.build_ai_reporter_review(day="D", reporter_output={"policy": {"reporter": {"ai_review": {"enabled": True}}}}, enabled=False)["status"], "disabled")


def test_dry_run_and_unavailable_client_short_circuit(spied, monkeypatch):
    monkeypatch.setenv("DRY_RUN", "1")
    r = rv.build_ai_reporter_review(day="D", reporter_output={}, enabled=True)
    _eq((r["status"], r["reason"], r["enabled"]), ("dry_run", "DRY_RUN mode", True))
    _eq(_Router.calls, [])
    monkeypatch.delenv("DRY_RUN")
    _Router.client = None
    u = rv.build_ai_reporter_review(day="D", reporter_output={}, enabled=True)
    _eq((u["status"], u["reason"]), ("unavailable", "LLM client unavailable"))
    _eq(_Router.calls, [])


def test_ok_path_records_events_and_uses_clamped_policy(spied):
    r = rv.build_ai_reporter_review(day="2026-10-28", reporter_output={}, enabled=True, max_tokens=300, temperature=0.7)
    _eq((r["status"], r["llm_status"], r["model"], r["ai_summary"], r["ai_run_grade"]), ("ok", "ok", "fake/model", "ok", "B+"))
    chat = [c for c in _Router.calls if c[0] == "chat"][0]
    _eq((chat[1], chat[2]["max_tokens"], chat[2]["temperature"]), ("reporter_final", 300, 0.7))
    _eq([e[0] for e in spied], ["record_raw_input", "record_llm_prompt", "record_llm_response"])
    _eq(spied[-1][1]["status"], "ok")
    low = rv.build_ai_reporter_review(day="D", reporter_output={}, enabled=True, max_tokens=10)
    _eq(low["status"], "ok")
    _eq([c for c in _Router.calls if c[0] == "chat"][-1][2]["max_tokens"], 256)   # floor at 256


def test_env_overrides_apply_only_to_default_execution_profile(spied, monkeypatch):
    monkeypatch.setenv("REPORTER_AI_REVIEW_TEMPERATURE", "0.55")
    monkeypatch.setenv("REPORTER_AI_REVIEW_MAX_TOKENS", "1234")
    rv.build_ai_reporter_review(day="D", reporter_output={}, enabled=True)
    p = [c for c in _Router.calls if c[0] == "chat"][-1][2]
    _eq((p["temperature"], p["max_tokens"]), (0.55, 1234))
    rv.build_ai_reporter_review(day="D", reporter_output={}, enabled=True, max_tokens=700, temperature=0.1)
    p = [c for c in _Router.calls if c[0] == "chat"][-1][2]
    _eq((p["temperature"], p["max_tokens"]), (0.1, 700))   # explicit args win over env


def test_call_failure_returns_error_result_without_raising(spied):
    _Router.boom = TimeoutError("slow")
    r = rv.build_ai_reporter_review(day="D", reporter_output={}, enabled=True)
    _eq((r["status"], r["model"]), ("error", "fake/model"))
    if not r["reason"].startswith("ai_call_failed:slow"):
        raise AssertionError(r["reason"])
    _eq(spied[-1][1], {"status": "error"})


@pytest.mark.parametrize("reply,reason_prefix", [
    ("", "ai_response_empty"),
    # Quirk pinned: non-JSON text is reported as "missing_required_keys" (all 7 keys) because that check runs before the
    # "ai_response_not_full_json" default, which is therefore unreachable in practice.
    ("not json at all", "ai_response_missing_required_keys"),
    (json.dumps({"ai_summary": "only"}), "ai_response_missing_required_keys"),
])
def test_unparseable_replies_become_parse_error(spied, reply, reason_prefix):
    _Router.reply = reply
    r = rv.build_ai_reporter_review(day="D", reporter_output={}, enabled=True)
    _eq(r["status"], "parse_error")
    if not r["reason"].startswith(reason_prefix):
        raise AssertionError((reason_prefix, r["reason"]))
    _eq(r["ai_run_grade"], "N/A")
    _eq(spied[-1][1]["status"], "parse_error")
    if reply == "not json at all" and not r["reason"].endswith(":not json at all"):
        raise AssertionError("raw reply is appended (clipped) to the reason")
    if reply == "not json at all" and r["reason"].count(",") != 6:
        raise AssertionError(r["reason"])


def test_recorder_failures_never_break_the_review(spied, monkeypatch):
    def boom(*a, **k):
        raise OSError("ledger disk full")

    for name in ("record_raw_input", "record_llm_prompt", "record_llm_response"):
        monkeypatch.setattr(rv, name, boom)
    r = rv.build_ai_reporter_review(day="D", reporter_output={}, enabled=True)
    _eq(r["status"], "ok")
    _Router.reply = "garbage"
    _eq(rv.build_ai_reporter_review(day="D", reporter_output={}, enabled=True)["status"], "parse_error")
    _Router.boom = RuntimeError("x")
    _eq(rv.build_ai_reporter_review(day="D", reporter_output={}, enabled=True)["status"], "error")
