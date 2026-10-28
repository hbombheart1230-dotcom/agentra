"""RF-031 libs/reporting/trade_report_runtime_policy: pure diagnostics/policy contracts.

Measured at 64% before this file. No IO, LLM or network: only dict inputs.
Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import pytest

from libs.reporting import trade_report_runtime_policy as tp

CODES = ["no_executed_lifecycle", "decision_only_run", "hold_only_run", "execution_failed", "missing_story_input",
         "llm_generation_failed", "artifact_write_failed", "missing_report_linkage", "report_not_requested",
         "still_open_lifecycle", "awaiting_exit_for_full_report", "partial_exit_awaiting_full_close"]


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def test_every_known_code_has_distinct_human_and_next_step_text():
    humans = [tp.report_reason_human(c) for c in CODES]
    steps = [tp.report_next_step(c) for c in CODES]
    _eq((len(set(humans)), len(set(steps))), (12, 12))
    generic_h, generic_s = tp.report_reason_human("zzz"), tp.report_next_step("zzz")
    if generic_h in humans or generic_s in steps:
        raise AssertionError("unknown code must map to the generic text")
    _eq((generic_h, generic_s), ("AI report diagnostics are not fully classified.", "Review diagnostics and continue with Operator Brief."))
    for c in (None, "", "  ", "UNKNOWN"):
        _eq((tp.report_reason_human(c), tp.report_next_step(c)), (generic_h, generic_s))
    _eq(tp.report_reason_human("  Decision_Only_Run "), tp.report_reason_human("decision_only_run"))   # trimmed + case-insensitive


def test_base_diagnostics_defaults_and_model_normalization():
    d = tp.base_report_diagnostics("")
    _eq((d["report_status"], d["llm_model_used"], d["llm_provider"], d["generation_attempted"]), ("pending", "openrouter/free", "OpenRouter", False))
    _eq((d["deterministic_report_status"], d["llm_brief_status"], d["ai_trade_report_status"]), ("skipped", "skipped", "skipped"))
    for k in ("story_input_available", "report_output_available", "report_artifact_available"):
        _eq(d[k], False)
    _eq(tp.base_report_diagnostics("some/model")["llm_model_used"] != "", True)
    # independent dicts on every call
    a, b = tp.base_report_diagnostics("x"), tp.base_report_diagnostics("x")
    a["report_status"] = "mutated"
    _eq(b["report_status"], "pending")


def _seed(**kw):
    args = dict(lifecycle_status="closed", story_type="executed", report_requested=True, story_input_available=True, model_hint="", generate_on_open=False)
    args.update(kw)
    return tp.seed_diagnostics_for_policy(**args)


@pytest.mark.parametrize("kw,status,code,attempt", [
    (dict(story_input_available=False), "failed", "missing_story_input", False),
    (dict(report_requested=False), "skipped", "report_not_requested", False),
    (dict(story_type="decision_only"), "skipped", "decision_only_run", False),
    (dict(story_type=" FAILED_EXECUTION "), "skipped", "execution_failed", False),
    (dict(lifecycle_status="partial"), "pending", "partial_exit_awaiting_full_close", False),
    (dict(lifecycle_status=" Open "), "pending", "awaiting_exit_for_full_report", False),
    (dict(), "pending", "", True),
])
def test_seed_decision_table(kw, status, code, attempt):
    out = _seed(**kw)
    d = out["diagnostics"]
    _eq((d["report_status"], d["report_reason_code"], out["should_attempt_generation"]), (status, code, attempt))
    if code:
        _eq((d["report_reason_human"], d["next_expected_step"]), (tp.report_reason_human(code), tp.report_next_step(code)))
    else:
        _eq((d["report_reason_human"], d["next_expected_step"]), ("", ""))
    _eq(d["story_input_available"], kw.get("story_input_available", True))


def test_seed_precedence_and_generate_on_open():
    # a missing story input outranks every other condition
    _eq(_seed(story_input_available=False, report_requested=False, story_type="decision_only")["diagnostics"]["report_reason_code"], "missing_story_input")
    # not requested outranks story type / lifecycle
    _eq(_seed(report_requested=False, story_type="decision_only", lifecycle_status="open")["diagnostics"]["report_reason_code"], "report_not_requested")
    # story type outranks lifecycle
    _eq(_seed(story_type="decision_only", lifecycle_status="open")["diagnostics"]["report_reason_code"], "decision_only_run")
    # generate_on_open lifts only the open/partial waiting states
    for st in ("open", "partial"):
        o = _seed(lifecycle_status=st, generate_on_open=True)
        _eq((o["should_attempt_generation"], o["diagnostics"]["report_reason_code"]), (True, ""))
    _eq(_seed(story_type="decision_only", generate_on_open=True)["should_attempt_generation"], False)
    _eq(_seed(lifecycle_status=None, story_type=None)["should_attempt_generation"], True)


def _policy(**kw):
    return tp.resolve_trade_report_policy(**kw)


def test_policy_defaults_when_no_trade_report_container():
    p = _policy()
    _eq((p["enabled"], p["generate_on_open"], p["policy_source"]), (True, False, "default"))
    _eq(set(p), {"enabled", "generate_on_open", "policy_source", "llm_profile", "llm_primary", "llm_fallback"})
    _eq(p["llm_profile"] != "", True)
    _eq(_policy(runtime_state=None, story_input=None), p)
    _eq(_policy(story_input={"applied_policy": {"reporter": {"trade_report": {}}}}), p)   # empty container is ignored


def test_policy_container_precedence_and_coercion():
    story = {"applied_policy": {"reporter": {"trade_report": {"enabled": False, "generate_on_open": 1}}}}
    commander = {"commander": {"applied_policy": {"reporter": {"trade_report": {"enabled": True, "generate_on_open": True, "policy_source": "custom"}}}}}
    runtime = {"applied_policy": {"reporter": {"trade_report": {"generate_on_open": True}}}}
    a = _policy(story_input={**story, **commander}, runtime_state=runtime)
    _eq((a["enabled"], a["generate_on_open"], a["policy_source"]), (False, True, "story_input.applied_policy"))   # story_input wins
    b = _policy(story_input=commander, runtime_state=runtime)
    _eq((b["enabled"], b["generate_on_open"], b["policy_source"]), (True, True, "custom"))                        # explicit source kept
    c = _policy(story_input={"commander": {"applied_policy": {"reporter": {"trade_report": {"generate_on_open": False}}}}}, runtime_state=runtime)
    _eq((c["enabled"], c["policy_source"]), (True, "story_input.commander.applied_policy"))                       # enabled defaults to True
    d = _policy(runtime_state=runtime)
    _eq((d["enabled"], d["generate_on_open"], d["policy_source"]), (True, True, "runtime_state.applied_policy"))


def test_policy_non_dict_containers_current_behaviour():
    # Quirk pinned, no change made: the llm-slot lookup is guarded with isinstance(), but the container loop that
    # follows is not, so a truthy NON-dict at applied_policy / applied_policy.reporter / commander /
    # commander.applied_policy raises AttributeError instead of falling back to the default policy.
    for bad in ({"applied_policy": "x"}, {"applied_policy": {"reporter": "x"}}, {"commander": "x"},
                {"commander": {"applied_policy": "x"}}, {"applied_policy": ["x"]}):
        with pytest.raises(AttributeError):
            _policy(story_input=bad)
    with pytest.raises(AttributeError):
        _policy(runtime_state={"applied_policy": "x"})
    # falsy or deeper non-dict values are tolerated and give the default policy
    for ok in ({"applied_policy": 0}, {"applied_policy": {"reporter": {"trade_report": "x"}}}, {"applied_policy": {"reporter": {"trade_report": ["x"]}}},
               {"reporter_policy": "x"}):
        _eq(_policy(story_input=ok)["policy_source"], "default")
