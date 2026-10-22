"""P1.5 DEV-A (wave A1): BASE (d7ab8294) vs current parity for libs.reporting.reporter_ai_review.

The frozen BASE module is exec'd from Git beside the live one. The whole orchestrator ``build_ai_reporter_review`` is driven
with the same fake ``LLMRouter`` and evidence-ledger recorders on both (nothing real is called); returned dicts, router
role/policy/messages and the ledger call sequence are compared. Pure helpers are compared on adverse inputs, facade seams are
patched identically on both modules, and owner mutants must be detected. Ownership/import/AST boundaries live in
``test_p15_a_reporter_ai_review_boundaries.py``.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import types
from pathlib import Path

import pytest

import libs.reporting.reporter_ai_review as cur
import libs.reporting.reporter_ai_review_parts.compact_input as compact_owner
import libs.reporting.reporter_ai_review_parts.prompting as prompting_owner
import libs.reporting.reporter_ai_review_parts.result_shaping as shaping_owner
import libs.reporting.reporter_ai_review_parts.review_resolution as resolution_owner

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
PATH = "libs/reporting/reporter_ai_review.py"
_BASE: dict = {}


def base():
    if "mod" not in _BASE:
        src = subprocess.check_output(["git", "show", f"{BASE_SHA}:{PATH}"], cwd=ROOT).decode("utf-8-sig")
        mod = types.ModuleType("_p15_reporter_ai_review_base_d7ab8294")
        mod.__file__ = str(ROOT / PATH)
        sys.modules[mod.__name__] = mod
        exec(compile(src, f"<base:{PATH}>", "exec"), mod.__dict__)
        _BASE["mod"] = mod
    return _BASE["mod"]


FULL_JSON = json.dumps({
    "ai_summary": "요약 " * 400, "ai_findings": ["f1", "", "f" * 400, 7] + [f"g{i}" for i in range(20)],
    "ai_root_causes": ["r1"], "ai_improvement_suggestions": ["i1", "i2"], "ai_run_grade": "A+",
    "ai_agent_evaluations": {"strategist": "good", "": "dropped", "k" * 200: "v" * 300, **{f"a{i}": "x" for i in range(15)}},
    "ai_evidence_links": {"findings": [{"text": "t" * 400, "evidence_keys": ["k1", "", "k" * 100, "k3", "k4", "k5", "k6", "k7"]}, "key_only", 5, ""],
                          "root_causes": "not-a-list", "improvements": [{"text": 1}]},
}, ensure_ascii=False)
PARTIAL_JSON = '{"ai_summary": "partial", "ai_findings": ["a"'
MISSING_KEYS_JSON = json.dumps({"ai_summary": "only summary"})
ENABLED_POLICY = {"applied_policy": {"reporter": {"ai_review": {"enabled": True}}}}
LLM_POLICY = {"llm": {"reporter": {"daily": {"primary": "moonshotai/kimi-k2.5", "execution_profile": {"name": "deep_review", "temperature": 0.25, "max_tokens": 4096, "timeout_sec": 33}}}}}


def _out(**extra):
    return {"trade_summary": {"trade_count": "3", "symbols_traded": list("ABCDEFGHIJ")},
            "decision_trace_chain_summary": {"chains": [{"run_id": "r" * 100, "strategist": {"themes": list("abcdef")}, "scanner": {"candidate_pool_size": "4"}, "monitor": {"min_hold_blocked": 1},
                                                          "supervisor": {}, "executor": {"fill_status_summary": "filled"}, "complete_chain": 1}, "junk", {}] + [{}] * 12},
            "ai_evidence_catalog": {"k1": {"summary": "s" * 300}, "k2": "no-dict", "k3": {}},
            "incident_postmortem": {"incidents": [{"a": 1}]}, "improvement_suggestions": list("0123456789"), **extra}


SCENARIOS = {
    "disabled_explicit": dict(kwargs=dict(enabled=False), output=_out()),
    "disabled_no_policy": dict(kwargs={}, output=_out()),
    "enabled_applied_policy_ok": dict(kwargs={}, output=_out(**ENABLED_POLICY, **LLM_POLICY), reply=FULL_JSON),
    "applied_false_beats_fallback_true": dict(kwargs={}, output=_out(applied_policy={"reporter": {"ai_review": {"enabled": False}}}, reporter_policy={"ai_review": {"enabled": True}})),
    "reporter_policy_fallback": dict(kwargs={}, output=_out(reporter_policy={"ai_review": {"enabled": 1}}), reply=FULL_JSON),
    "payload_policy_fallback": dict(kwargs={}, output=_out(policy={"reporter": {"ai_review": {"enabled": True}}}), reply=FULL_JSON),
    "non_dict_policies": dict(kwargs={}, output=_out(applied_policy=[], reporter_policy="x", policy=3)),
    "dry_run": dict(kwargs=dict(enabled=True), output=_out(), env={"DRY_RUN": "1"}),
    "client_unavailable": dict(kwargs=dict(enabled=True), output=_out(), router="no_client"),
    "chat_raises": dict(kwargs=dict(enabled=True), output=_out(), router="raises"),
    "empty_reply": dict(kwargs=dict(enabled=True), output=_out(), reply=""),
    "partial_reply": dict(kwargs=dict(enabled=True), output=_out(), reply=PARTIAL_JSON),
    "missing_required_keys": dict(kwargs=dict(enabled=True), output=_out(), reply=MISSING_KEYS_JSON),
    "not_json": dict(kwargs=dict(enabled=True), output=_out(), reply="sorry, no json " * 30),
    "explicit_params": dict(kwargs=dict(enabled=True, model="openai/gpt-x", temperature=0.9, max_tokens=1234), output=_out(**LLM_POLICY), reply=FULL_JSON),
    "env_execution_fallback": dict(kwargs=dict(enabled=True), output=_out(), reply=FULL_JSON, env={"REPORTER_AI_REVIEW_TEMPERATURE": "0.45", "REPORTER_AI_REVIEW_MAX_TOKENS": "1536"}),
    "policy_beats_env": dict(kwargs=dict(enabled=True), output=_out(**LLM_POLICY), reply=FULL_JSON, env={"REPORTER_AI_REVIEW_TEMPERATURE": "0.45"}),
    "bad_env_number": dict(kwargs=dict(enabled=True), output=_out(), reply=FULL_JSON, env={"REPORTER_AI_REVIEW_MAX_TOKENS": "abc"}),
}


class Harness:
    """Identical fakes on one module; records every call crossing the module boundary."""

    def __init__(self, monkeypatch, mod, scenario):
        self.calls = []
        env = scenario.get("env", {})
        for key in ("DRY_RUN", "REPORTER_AI_REVIEW_TEMPERATURE", "REPORTER_AI_REVIEW_MAX_TOKENS"):
            monkeypatch.delenv(key, raising=False)
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        calls, mode, reply = self.calls, scenario.get("router", "ok"), scenario.get("reply", FULL_JSON)

        class Route:
            def __init__(self, model):
                self.model = model

        class FakeRouter:
            def __init__(self):
                self.client = None if mode == "no_client" else True

            def resolve(self, role, policy=None):
                calls.append(("resolve", role, json.dumps(policy, sort_keys=True, default=repr)))
                return Route((policy or {}).get("model"))

            def chat(self, role, messages, policy=None):
                calls.append(("chat", role, json.dumps(messages, ensure_ascii=False), json.dumps(policy, sort_keys=True, default=repr)))
                if mode == "raises":
                    raise RuntimeError("boom")
                return reply

            @classmethod
            def from_env(cls):
                calls.append(("from_env",))
                return cls()

        monkeypatch.setattr(mod, "LLMRouter", FakeRouter)
        for name in ("record_raw_input", "record_llm_prompt", "record_llm_response"):
            monkeypatch.setattr(mod, name, (lambda n: lambda *a, **k: calls.append((n, json.dumps(k, ensure_ascii=False, sort_keys=True, default=repr))))(name))


def _run(monkeypatch, mod, scenario):
    harness = Harness(monkeypatch, mod, scenario)
    try:
        result = ("ok", json.dumps(mod.build_ai_reporter_review(day="2026-04-07", reporter_output=copy.deepcopy(scenario["output"]), **scenario["kwargs"]),
                                   ensure_ascii=False, default=repr))
    except Exception as exc:  # noqa: BLE001
        result = ("exc", type(exc).__name__, str(exc))
    return result, harness.calls


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_orchestrator_matches_base(monkeypatch, name):
    scenario = SCENARIOS[name]
    expected = _run(monkeypatch, base(), scenario)
    monkeypatch.undo()
    assert _run(monkeypatch, cur, scenario) == expected


def test_scenarios_reach_every_return_path(monkeypatch):
    statuses = {}
    for name, scenario in SCENARIOS.items():
        result, _ = _run(monkeypatch, cur, scenario)
        monkeypatch.undo()
        if result[0] == "ok":
            statuses[name] = json.loads(result[1])["status"]
        else:
            statuses[name] = "exception"
    assert {"disabled", "dry_run", "unavailable", "error", "parse_error", "ok"} <= set(statuses.values())
    assert statuses["applied_false_beats_fallback_true"] == "disabled" and statuses["reporter_policy_fallback"] == "ok"
    assert statuses["bad_env_number"] == "exception"  # float('abc') surfaces exactly as on BASE


HELPER_INPUTS = [None, "", "  x  ", "a" * 500, 7, 0, ["a", "", "b" * 300, 3, None] * 5, {"k": "v", "": "x", "kk" * 50: "w" * 200}, [], {}, object]


def _outcome(fn):
    try:
        return ("ok", json.dumps(fn(), ensure_ascii=False, default=repr))
    except Exception as exc:  # noqa: BLE001
        return ("exc", type(exc).__name__, str(exc))


@pytest.mark.parametrize("name", ["_clip_str", "_list_str", "_dict_str", "_normalize_evidence_link_items", "_normalize_llm_status"])
def test_shaping_helpers_match_base_on_adverse_inputs(name):
    for value in HELPER_INPUTS:
        for kwargs in ({}, {"max_len": 5}, {"max_items": 1}) if name != "_normalize_llm_status" else ({},):
            try:
                expected = _outcome(lambda: getattr(base(), name)(copy.deepcopy(value), **kwargs))
            except TypeError:
                continue
            assert _outcome(lambda: getattr(cur, name)(copy.deepcopy(value), **kwargs)) == expected, (name, value, kwargs)
    for status in ("ok", "error", "OK", "weird", "", "dry_run", "parse_error"):
        assert cur._normalize_llm_status(status) == base()._normalize_llm_status(status)


def test_default_and_normalized_results_match_base():
    for kwargs in ({"enabled": True, "status": "error", "reason": "r" * 500, "model": "m"}, {"enabled": False, "status": "disabled"}):
        assert _outcome(lambda: cur._default_result(**kwargs)) == _outcome(lambda: base()._default_result(**kwargs))
    for obj in (json.loads(FULL_JSON), {}, {"ai_evidence_links": []}, {"ai_run_grade": None}):
        assert _outcome(lambda: cur._normalize_result(copy.deepcopy(obj), enabled=True, model="m")) == _outcome(
            lambda: base()._normalize_result(copy.deepcopy(obj), enabled=True, model="m"))


def test_compact_input_and_messages_match_base():
    inputs = [{}, _out(), {"trade_summary": "x", "decision_trace_chain_summary": {"chains": "no"}}, _out(strategist_evaluation={"themes_proposed": list("abcdefghij")}),
              {"ai_evidence_catalog": {str(i): {"summary": "s"} for i in range(15)}}]
    for out in inputs:
        assert _outcome(lambda: cur._build_compact_input("2026-04-07", copy.deepcopy(out))) == _outcome(lambda: base()._build_compact_input("2026-04-07", copy.deepcopy(out)))
        compact = base()._build_compact_input("2026-04-07", copy.deepcopy(out)) if out is not None else {}
        assert cur._build_messages("2026-04-07", compact) == base()._build_messages("2026-04-07", compact)
    # first 12 chains are read, the one non-dict ("junk") is skipped -> 11 (value equals BASE, asserted above)
    assert len(cur._build_compact_input("d", _out())["decision_trace_chain_samples"]) == 11
    assert cur._build_messages("d", {"x": 1})[0]["role"] == "system"


# --- facade monkeypatch seams: the same patch on BASE and current must give the same output, different from unpatched ---


def _bundle(monkeypatch, mod):
    outputs = []
    for name in ("enabled_applied_policy_ok", "client_unavailable", "parse_error_probe"):
        scenario = SCENARIOS.get(name) or dict(kwargs=dict(enabled=True), output=_out(), reply=MISSING_KEYS_JSON)
        outputs.append(_run(monkeypatch, mod, scenario))
    return json.dumps(outputs, ensure_ascii=False, default=repr)


SEAMS = [
    ("_clip_str", lambda mod: (lambda v, *, max_len=400: "CLIP")),
    ("_list_str", lambda mod: (lambda v, *, max_items=8, max_len=240: ["LIST"])),
    ("_dict_str", lambda mod: (lambda v, *, max_items=8, max_key_len=64, max_val_len=120: {"DICT": "x"})),
    ("_normalize_llm_status", lambda mod: (lambda status: "PATCHED")),
    ("_normalize_evidence_link_items", lambda mod: (lambda v, *, max_items=10: [{"text": "EV", "evidence_keys": []}])),
    ("_default_result", lambda mod: (lambda *, enabled, status, reason="", model="": {"patched": status})),
    ("_normalize_result", lambda mod: (lambda obj, *, enabled, model: {"patched": True})),
    ("_build_compact_input", lambda mod: (lambda day, out: {"patched_compact": day})),
    ("_build_messages", lambda mod: (lambda day, compact_input: [{"role": "user", "content": "PATCHED"}])),
    ("required_key_metadata", lambda mod: (lambda obj, keys: {"required_keys_missing": ["patched"], "required_keys_present": []})),
    ("canonical_llm_status", lambda mod: (lambda status, default="": "CANON")),
    ("REPORTER_AI_REVIEW_REQUIRED_KEYS", lambda mod: ["ai_summary"]),
]


@pytest.mark.parametrize("name,factory", SEAMS, ids=[n for n, _ in SEAMS])
def test_facade_monkeypatch_seams_match_base(monkeypatch, name, factory):
    unpatched = _bundle(monkeypatch, cur)
    monkeypatch.undo()
    outputs = []
    for mod in (base(), cur):
        monkeypatch.setattr(mod, name, factory(mod))
        outputs.append(_bundle(monkeypatch, mod))
        monkeypatch.undo()
    assert outputs[1] == outputs[0] and outputs[1] != unpatched


# --- mutation checks: breaking an owner must break parity (the comparison is not vacuous) ---------------------------


@pytest.mark.parametrize(
    "owner,name,mutant",
    [
        (shaping_owner, "_clip_str_impl", lambda v, *, max_len=400, facade: str(v or "")),
        (shaping_owner, "_list_str_impl", lambda v, *, max_items=8, max_len=240, facade: []),
        (shaping_owner, "_dict_str_impl", lambda v, *, max_items=8, max_key_len=64, max_val_len=120, facade: {}),
        (shaping_owner, "_normalize_result_impl", lambda obj, *, enabled, model, facade: {"status": "ok"}),
        (shaping_owner, "_default_result_impl", lambda *, enabled, status, reason="", model="", facade: {"status": status}),
        (compact_owner, "_build_compact_input_impl", lambda day, out, *, facade: {"day": day}),
        (prompting_owner, "_build_messages_impl", lambda day, compact_input, *, facade: []),
        (resolution_owner, "resolve_ai_review_enabled", lambda reporter_output, enabled: bool(enabled)),
        (resolution_owner, "resolve_parse_mode", lambda parsed_result: "none"),
        (resolution_owner, "resolve_parse_failure_reason", lambda parsed_result, key_meta: "changed"),
    ],
)
def test_owner_mutants_are_detected(monkeypatch, owner, name, mutant):
    expected = _bundle(monkeypatch, base())
    monkeypatch.undo()
    assert _bundle(monkeypatch, cur) == expected  # green baseline first
    monkeypatch.undo()
    monkeypatch.setattr(owner, name, mutant)
    if hasattr(cur, name):  # names bound into the facade namespace at import
        monkeypatch.setattr(cur, name, mutant)
    mutated = _bundle(monkeypatch, cur)
    monkeypatch.undo()
    if name == "resolve_ai_review_enabled":  # only the policy-driven scenarios can see this one
        expected = json.dumps([_run(monkeypatch, base(), SCENARIOS["reporter_policy_fallback"])], default=repr)
        monkeypatch.undo()
        monkeypatch.setattr(owner, name, mutant)
        monkeypatch.setattr(cur, name, mutant)
        mutated = json.dumps([_run(monkeypatch, cur, SCENARIOS["reporter_policy_fallback"])], default=repr)
    assert mutated != expected
