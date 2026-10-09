from __future__ import annotations

from typing import Any, Dict, Mapping

def build_seed_strategist_context_and_evidence(story_input: Dict[str, Any], trade_read_model_context: Dict[str, Any], market_context: Dict[str, Any], strategist_evidence_trace: Dict[str, Any], canonical_strategist: Dict[str, Any], canonical_strategist_decision_frame: Dict[str, Any], *, deps: Mapping[str, Any]) -> Any:
    _as_dict = deps["as_dict"]
    _first_nonempty_text = deps["first_nonempty_text"]
    _listify = deps["listify"]
    _compact_scalar_dict = deps["compact_scalar_dict"]

    trade_model_strategist = trade_read_model_context.get("strategist") if isinstance(trade_read_model_context.get("strategist"), dict) else {}
    canonical_trace_summary = (
        _as_dict(story_input.get("strategist_trace_summary"))
        or _as_dict(story_input.get("trace_summary"))
        or _as_dict(canonical_strategist.get("trace_summary"))
        or _as_dict(canonical_strategist.get("strategist_trace_summary"))
    )
    theme_strength_packet = (
        _as_dict(market_context.get("theme_strength_packet"))
        or _as_dict(trade_model_strategist.get("theme_strength_packet"))
        or _as_dict(canonical_strategist.get("theme_strength_packet"))
        or _as_dict(canonical_strategist_decision_frame.get("theme_strength_packet"))
    )
    theme_strength_scores = (
        _as_dict(market_context.get("theme_strength_scores"))
        or _as_dict(trade_model_strategist.get("theme_strength_scores"))
        or _as_dict(canonical_strategist.get("theme_strength"))
        or _as_dict(theme_strength_packet.get("theme_scores"))
    )
    strategist_context = {
        "playbook": _first_nonempty_text(
            market_context.get("playbook"),
            market_context.get("selected_playbook"),
            trade_model_strategist.get("playbook"),
            max_len=80,
        ),
        "selected_playbook": _first_nonempty_text(
            market_context.get("selected_playbook"),
            market_context.get("playbook"),
            trade_model_strategist.get("playbook"),
            max_len=80,
        ),
        "policy_source": _first_nonempty_text(
            market_context.get("policy_source"),
            trade_model_strategist.get("policy_source"),
            max_len=80,
        ),
        "risk_tone": _first_nonempty_text(
            market_context.get("risk_tone"),
            trade_model_strategist.get("risk_tone"),
            canonical_trace_summary.get("risk_tone"),
            canonical_strategist.get("risk_tone"),
            canonical_strategist_decision_frame.get("risk_tone"),
            max_len=40,
        ),
        "trade_aggressiveness": _first_nonempty_text(
            market_context.get("trade_aggressiveness"),
            trade_model_strategist.get("trade_aggressiveness"),
            canonical_trace_summary.get("trade_aggressiveness"),
            canonical_strategist.get("trade_aggressiveness"),
            canonical_strategist_decision_frame.get("trade_aggressiveness"),
            max_len=40,
        ),
        "monitor_guidance": _first_nonempty_text(
            market_context.get("monitor_guidance"),
            trade_model_strategist.get("monitor_guidance"),
            canonical_trace_summary.get("monitor_guidance"),
            canonical_strategist.get("monitor_guidance"),
            canonical_strategist_decision_frame.get("monitor_guidance"),
            max_len=80,
        ),
        "themes": _listify(
            market_context.get("themes")
            or market_context.get("preferred_themes")
            or trade_model_strategist.get("themes"),
            max_items=6,
            max_len=48,
        ),
        "preferred_themes": _listify(
            market_context.get("preferred_themes")
            or market_context.get("themes")
            or trade_model_strategist.get("themes"),
            max_items=6,
            max_len=48,
        ),
        "market_context_summary": _first_nonempty_text(
            market_context.get("summary"),
            trade_model_strategist.get("market_context_summary"),
            max_len=320,
        ),
        "theme_strength_packet": theme_strength_packet,
        "theme_source": _first_nonempty_text(
            market_context.get("theme_source"),
            trade_model_strategist.get("theme_source"),
            canonical_strategist.get("theme_source"),
            canonical_strategist_decision_frame.get("theme_source"),
            theme_strength_packet.get("source"),
            max_len=80,
        ),
        "theme_source_status": _first_nonempty_text(
            market_context.get("theme_source_status"),
            trade_model_strategist.get("theme_source_status"),
            canonical_strategist.get("theme_source_status"),
            canonical_strategist_decision_frame.get("theme_source_status"),
            theme_strength_packet.get("status"),
            max_len=80,
        ),
        "theme_source_reason": _first_nonempty_text(
            market_context.get("theme_source_reason"),
            trade_model_strategist.get("theme_source_reason"),
            canonical_strategist.get("theme_source_reason"),
            canonical_strategist_decision_frame.get("theme_source_reason"),
            theme_strength_packet.get("reason"),
            max_len=160,
        ),
        "theme_strength_top_themes": _listify(
            market_context.get("theme_strength_top_themes") or theme_strength_packet.get("top_themes"),
            max_items=6,
            max_len=80,
        ),
        "theme_strength_scores": theme_strength_scores,
    }

    strategist_evidence = {
        "candidate_hints": _listify(
            strategist_evidence_trace.get("candidate_hints")
            or market_context.get("candidate_hints")
            or story_input.get("strategist_candidate_hints"),
            max_items=8,
            max_len=24,
        ),
        "news_query_targets": _listify(
            strategist_evidence_trace.get("news_query_targets")
            or market_context.get("news_query_targets"),
            max_items=8,
            max_len=80,
        ),
        "market_headlines": _listify(
            strategist_evidence_trace.get("market_headlines")
            or market_context.get("market_headlines")
            or story_input.get("strategist_market_headlines"),
            max_items=3,
            max_len=180,
        ),
        "symbol_headlines": _listify(
            strategist_evidence_trace.get("symbol_headlines")
            or market_context.get("symbol_headlines")
            or story_input.get("strategist_symbol_headlines"),
            max_items=3,
            max_len=180,
        ),
        "global_sentiment_signal": _compact_scalar_dict(
            strategist_evidence_trace.get("global_sentiment_signal") or market_context.get("global_sentiment_signal"),
            max_items=8,
            max_len=120,
        ),
        "fear_index": _compact_scalar_dict(
            strategist_evidence_trace.get("fear_index") or market_context.get("fear_index"),
            max_items=8,
            max_len=120,
        ),
        "key_events": _listify(
            strategist_evidence_trace.get("key_events")
            or market_context.get("key_events")
            or market_context.get("key_events_hint"),
            max_items=6,
            max_len=180,
        ),
    }
    return strategist_context, strategist_evidence

