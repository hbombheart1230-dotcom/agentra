from libs.reporting.trade_story_assembly_parts.reasoning_provenance import build_story_reasoning_provenance


def _deps():
    return {
        "_commander_reasoning_flag": lambda *args: args[2] == "shadow_used",
        "_commander_reasoning_source_priority": lambda *args: ["canonical", "derived"],
        "_resolve_commander_source_ref": lambda *args: "commander.json",
        "build_reasoning_provenance": lambda **kwargs: dict(kwargs),
        "normalize_reasoning_provenance_aliases": lambda payload, fallback: dict(fallback),
    }


def test_story_provenance_prefers_canonical_artifact_references():
    result = build_story_reasoning_provenance(
        {"commander": {}, "strategist_summary": {"strategist_fallback_used": False}},
        bundle_reasoning_provenance={},
        canonical_agent_artifacts={
            "canonical_commander_json": "commander.json",
            "canonical_strategist_json": "strategy.json",
            "canonical_scanner_json": "scanner.json",
            "canonical_monitor_json": "monitor.json",
        },
        evidence_provenance={"strategist": "fallback"},
        section_provenance={},
        deps=_deps(),
    )
    assert result["commander_context_source"] == "canonical"
    assert result["strategist_source_ref"] == "strategy.json"
    assert result["scanner_source_ref"] == "scanner.json"
    assert result["monitor_source_ref"] == "monitor.json"
    assert result["source_priority"] == ["canonical", "derived"]


def test_story_provenance_keeps_derived_source_when_no_canonical_artifact():
    result = build_story_reasoning_provenance(
        {"strategist_summary": {"strategist_fallback_used": True}},
        bundle_reasoning_provenance={},
        canonical_agent_artifacts={},
        evidence_provenance={"commander": "derived", "strategist": "direct",
                             "scanner": "direct", "monitor": "direct"},
        section_provenance={"market_context_human": {"source": "local"}},
        deps=_deps(),
    )
    assert result["commander_context_source"] == "derived"
    assert result["strategist_plan_source"] == "local"
    assert result["scanner_reason_source"] == "direct"
    assert result["monitor_reason_source"] == "direct"
    assert result["strategist_fallback_used"] is True
