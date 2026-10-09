from libs.reporting.trade_story_assembly_parts.lifecycle_human import build_lifecycle_human_fallback


def _deps():
    return {
        "EXECUTION_OUTCOME_NOT_CAPTURED": "outcome not captured",
        "LIFECYCLE_CONCLUSION_NOT_CAPTURED": "conclusion not captured",
        "REPORTER_LINKAGE_NOT_CAPTURED": "reporter not linked",
        "build_execution_outcome_fallback_from_lifecycle": lambda *args, **kwargs: {
            "summary": "derived execution", "bullets": ["derived detail"]
        },
        "build_operator_conclusion_human": lambda **kwargs: {
            "summary": "derived operator", "current_action": "HOLD",
            "watch_next": ["continue monitoring"],
            "thesis_invalidation": ["stop invalidation"],
        },
        "execution_outcome_summary_is_placeholder": lambda value: not value,
        "lifecycle_conclusion_summary_is_placeholder": lambda value: not value,
        "normalize_reporter_status_human": lambda payload: payload,
    }


def _call(**overrides):
    args = {
        "bundle_out": {},
        "entry": {"action": "BUY", "reason_human": "selection"},
        "holding": {"run_ids": ["r1"], "monitor_updates": ["holding"]},
        "exit_ctx": {}, "summary": {}, "reporter": {},
        "status": "open", "entry_action": "BUY",
        "exit_action": "", "lifecycle_action": "HOLD", "symbol": "005930",
        "market_context_human": {}, "scanner_reason_human": {}, "filters_human": {},
        "deps": _deps(),
    }
    args.update(overrides)
    return build_lifecycle_human_fallback(
        args.pop("bundle_out"),
        **args,
    )


def test_missing_human_sections_are_derived_without_broker_or_llm():
    market, scanner, monitor, guard, execution, reporter, operator = _call()
    assert market["summary"] == "Market context was not captured."
    assert scanner["summary"] == "selection"
    assert monitor["summary"] == "Holding updates captured from 1 monitor runs."
    assert execution == {"summary": "derived execution", "bullets": ["derived detail"]}
    assert operator["summary"] == "derived operator"
    assert guard == {}
    assert reporter["summary"] == "reporter not linked"


def test_captured_human_truth_keeps_priority_and_missing_fields_are_filled():
    result = _call(
        bundle_out={
            "market_context_human": {"summary": "canonical market"},
            "scanner_reason_human": {"summary": "canonical scanner"},
            "monitor_reason_human": {"summary": "canonical monitor"},
            "execution_outcome_human": {"summary": "confirmed execution"},
            "operator_conclusion_human": {"summary": "human conclusion"},
        },
        market_context_human={"summary": "canonical market"},
        scanner_reason_human={"summary": "canonical scanner"},
    )
    market, scanner, monitor, guard, execution, reporter, operator = result
    assert market["summary"] == "canonical market"
    assert scanner["summary"] == "canonical scanner"
    assert monitor["summary"] == "canonical monitor"
    assert execution["summary"] == "confirmed execution"
    assert execution["bullets"] == ["derived detail"]
    assert operator["summary"] == "human conclusion"
    assert operator["current_action"] == "HOLD"
    assert operator["watch_next"] == ["continue monitoring"]
