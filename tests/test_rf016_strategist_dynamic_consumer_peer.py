"""RF-016 focused offline peer probes: real owners, fake facades, zero external effects.

This is additional C4 evidence, not a substitute for the original 8-owner C4 matrix.
Run on an exact detached source checkout with both normal and -O pytest.
"""
from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace

import pytest

from libs.agents.strategist.context import news_compaction as news
from libs.agents.strategist.output import strategic_answers as answers
from libs.runtime.strategist.policy.node_policy_projection import (
    strat_policy_commander_context_policy_adjustment,
)


def _news_facade():
    return SimpleNamespace(
        _round_optional=lambda value, digits=4: (
            round(float(value), digits) if value is not None else None
        ),
        _news_item_title_for_llm=lambda row, *, max_len: str(
            (row or {}).get("title") or ""
        )[:max_len],
        _news_signal_label=lambda score: "negative" if score is not None and score < 0 else "neutral",
    )


def test_news_compaction_to_selected_signal_preserves_order_without_input_mutation():
    signal_map = {"005930": {"score": -0.8, "status": "valid"}}
    sample = {"005930": {"count": 1, "sample": [{"title": "  Warning  "}]}}
    original = deepcopy((signal_map, sample))
    rows = news._compact_news_signal_summary_for_llm_r3_impl(
        signal_map=signal_map,
        sample=sample,
        symbols=["005930", "005930"],
        limit=5,
        facade=_news_facade(),
    )
    assert len(rows) == 1
    assert rows[0]["symbol"] == "005930"
    assert rows[0]["score"] == -0.8
    assert rows[0]["label"] == "negative"
    assert rows[0]["headline_count"] == 1
    selected = news._selected_symbol_news_signal_for_llm_r3_impl(
        rows, "005930", facade=_news_facade()
    )
    assert selected == rows[0] and selected is not rows[0]
    assert selected["top_evidence"] is rows[0]["top_evidence"]  # existing shallow-copy contract
    assert (signal_map, sample) == original


def test_news_compaction_malformed_count_and_row_fail_as_existing_contract():
    f = _news_facade()
    with pytest.raises(ValueError):
        news._compact_news_signal_summary_for_llm_r3_impl(
            signal_map={}, sample={"005930": {"count": "invalid", "sample": []}},
            symbols=["005930"], limit=1, facade=f,
        )
    with pytest.raises(AttributeError):
        news._selected_symbol_news_signal_for_llm_r3_impl(
            ["malformed-row"], "005930", facade=f,
        )
    missing = news._selected_symbol_news_signal_for_llm_r3_impl(
        [], "005930", facade=f,
    )
    assert missing["status"] == "missing" and missing["symbol"] == "005930"


def _answer_kwargs(commander_context, facade):
    return dict(
        commander_context=commander_context,
        market_regime="risk_off",
        market_sentiment="bearish",
        key_events=["event"],
        themes=["semiconductors"],
        avoid_themes=[],
        playbook="defensive",
        scanner_bias="cautious",
        scanner_priority=["risk"],
        trade_aggressiveness="low",
        risk_tone="conservative",
        monitor_guidance="observe",
        report_focus=["quality"],
        recent_strategy_feedback={},
        strategy_memory={},
        read_model_facts={},
        reports_root=None,
        facade=facade,
    )


def test_strategic_answers_reads_dynamic_memory_seam_and_keeps_baseline_nested_alias():
    nested = {"reasons": ["existing"]}
    refresh = {
        "selected_symbol": "005930",
        "selected_rank": 1,
        "scanner_primary_candidate": {"symbol": "005930", "meta": nested},
    }
    commander_context = {"strategist_refresh_context": refresh}
    before = deepcopy(commander_context)
    seen = []
    facade = SimpleNamespace(
        _round_optional=lambda value, digits=4: value,
        _build_symbol_refresh_memory_excerpt=lambda *a: (
            seen.append(a) or {"symbol": "005930", "nested": nested}
        ),
    )
    out = answers._build_strategic_answers_r3_impl(
        **_answer_kwargs(commander_context, facade)
    )
    q15 = out["q15_commander_refresh_context"]
    assert seen == [("005930", {}, None)]
    assert q15["selected_symbol"] == "005930"
    assert q15["selected_symbol_was_rank1"] is True
    assert q15["selected_symbol_memory"]["nested"] is nested
    assert q15["scanner_primary_candidate"] is not refresh["scanner_primary_candidate"]
    assert q15["scanner_primary_candidate"]["meta"] is nested
    assert commander_context == before
    refresh["selected_rank"] = "not-an-integer"
    with pytest.raises(ValueError):
        answers._build_strategic_answers_r3_impl(
            **_answer_kwargs(commander_context, facade)
        )


def _policy_kwargs(facade, *, read_model_facts=None):
    return dict(
        state={"runtime_phase": "session", "candidates": [{"symbol": "005930"}]},
        market_regime="risk_off",
        playbook="defensive",
        market_sentiment="bearish",
        key_events=[],
        themes=[],
        avoid_themes=[],
        scanner_bias="cautious",
        scanner_priority=[],
        trade_aggressiveness="low",
        risk_tone="conservative",
        monitor_guidance="observe",
        report_focus=[],
        recent_strategy_feedback={},
        strategy_memory_advisory={},
        reports_root=None,
        read_model_facts={} if read_model_facts is None else read_model_facts,
        news_query_reasoning="market risk",
        monitor_policy={},
        exit_policy={},
        ai_overrides={},
        monitor_entry_policy_validation={},
        monitor_entry_policy={},
        facade=facade,
    )


def _policy_facade(memory, calls):
    def strategic_answers(**kwargs):
        calls.append(("answers", kwargs))
        return {"q15_commander_refresh_context": {"selected_symbol_memory": memory}}

    def directives(**kwargs):
        calls.append(("directives", kwargs))
        return {"ok": True}

    return SimpleNamespace(
        _build_commander_context_summary=lambda **kwargs: {
            "strategist_refresh_context": {"selected_symbol": "005930"},
            "strategist_refresh_requested": True,
        },
        _build_strategic_answers=strategic_answers,
        _build_strategist_plan=lambda **kwargs: {"source": "fake"},
        _build_monitor_entry_policy_rationale=lambda **kwargs: "default",
        _summarize_monitor_entry_policy_for_adjustment=lambda value: {},
        build_default_monitor_entry_policy=lambda: SimpleNamespace(to_dict=lambda: {}),
        _normalize_policy_adjustment_surface=lambda **kwargs: {},
        _normalize_strategy_adjustment_directives=directives,
    )


def test_policy_consumer_passes_facade_payload_and_preserves_existing_nested_alias():
    calls = []
    nested = {"rank": [1]}
    memory = {"nested": nested}
    facts = {"signals": {"source": "fake"}}
    before = deepcopy(facts)
    facade = _policy_facade(memory, calls)
    result = strat_policy_commander_context_policy_adjustment(
        **_policy_kwargs(facade, read_model_facts=facts)
    )
    assert len(result) == 6
    assert result[3]["q15_commander_refresh_context"]["selected_symbol_memory"] is memory
    assert [kind for kind, _ in calls] == ["answers", "directives"]
    answer_kwargs, directive_kwargs = calls[0][1], calls[1][1]
    assert answer_kwargs["read_model_facts"] == facts
    assert answer_kwargs["read_model_facts"] is not facts  # top-level copy
    assert answer_kwargs["read_model_facts"]["signals"] is facts["signals"]
    assert directive_kwargs["selected_symbol_memory"] == memory
    assert directive_kwargs["selected_symbol_memory"] is not memory
    assert directive_kwargs["selected_symbol_memory"]["nested"] is nested
    assert facts == before


def test_policy_consumer_propagates_facade_error_without_mutating_input():
    calls = []
    facts = {"signals": {"source": "fake"}}
    facade = _policy_facade({}, calls)

    def bad_answers(**kwargs):
        raise RuntimeError("injected downstream failure")

    facade._build_strategic_answers = bad_answers
    before = deepcopy(facts)
    with pytest.raises(RuntimeError, match="injected downstream failure"):
        strat_policy_commander_context_policy_adjustment(
            **_policy_kwargs(facade, read_model_facts=facts)
        )
    assert facts == before
    assert calls == []
