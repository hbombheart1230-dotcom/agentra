"""Deterministic Operator Brief section presentation; old frozen builders remain unchanged."""
from __future__ import annotations


def executive_decision(confidence, decision_reason, final_action, selected_rank, selected_symbol, universe_size):
    return {
        'final_action': final_action,
        'symbol': selected_symbol or '-',
        'reason': decision_reason,
        'confidence': confidence,
        'selected_rank': selected_rank or None,
        'universe_size': universe_size or None,
    }


def scanner_focus(canonical_trade, focus_symbol, score_driver_preview, selected_rank, selection_reason_text, top_candidates, universe_size):
    return {
        'summary': selection_reason_text,
        'selected_symbol': focus_symbol,
        'selected_rank': selected_rank or None,
        'universe_size': universe_size or None,
        'top_candidates': list(canonical_trade.get('top_candidates') or top_candidates[:3])[:3],
        'selection_reason': selection_reason_text,
        'score_drivers': score_driver_preview[:4],
    }


def next_step(next_expected_step, operator_takeaway_items, watch_next):
    return {
        'summary': next_expected_step or '-',
        'watch_next': watch_next[:4],
        'operator_takeaways': operator_takeaway_items[:4],
    }


def why_symbol_chosen(canonical_trade, comparison_reasons, selected_rank, selected_symbol, selection_reasons, top_candidates, universe_size):
    return {
        'selected': bool(selected_symbol),
        'universe_size': universe_size or None,
        'selected_rank': selected_rank or None,
        'selection_reasons': selection_reasons or ['selection rationale was not explicitly persisted'],
        'comparison_reasons': comparison_reasons,
        'top_candidates': list(canonical_trade.get('top_candidates') or top_candidates[:3])[:3],
    }


def market_context(canonical_trade, defensive_mode, global_score, macro_summary, news_summary, news_targets, strategist_summary, strategist_trace, vix_level, *, facade):
    return {
        'market_regime': str(canonical_trade.get('market_regime') or strategist_summary.get('market_regime') or strategist_trace.get('market_regime') or '-'),
        'global_sentiment': facade._format_float(global_score, 2) if global_score is not None else '-',
        'vix': facade._format_float(vix_level, 2) if vix_level is not None else '-',
        'macro_summary': macro_summary,
        'news_summary': news_summary,
        'news_targets': facade._clean_brief_list(news_targets, limit=6),
        'defensive_mode': 'enabled' if defensive_mode else 'disabled',
    }


def theme_detection(detected_themes, priority_alignment, theme_match, theme_priority):
    return {
        'detected_themes': detected_themes,
        'symbol_theme_match': theme_match or 'not explicitly tagged',
        'priority_alignment': priority_alignment,
        'theme_priority_bucket': theme_priority,
    }


def scanner_ranking_explanation(canonical_trade, component_scores, positive_factors, ranking_basis, scanner_trace, weak_factors):
    return {
        'ranking_basis': ranking_basis,
        'component_scores': component_scores,
        'tie_break_rule': str(canonical_trade.get('tie_break_rule') or scanner_trace.get('tie_break_rule') or 'higher composite score, then stronger feature coverage'),
        'positive_factors': positive_factors[:5],
        'weak_factors': weak_factors[:4],
    }


def chart_feature_coverage(chart_interpretation, feature_coverage, missing_feature_names, present_feature_names, *, facade):
    return {
        'present': facade._safe_int(feature_coverage.get('present'), 0),
        'total': facade._safe_int(feature_coverage.get('total'), 0),
        'quality': str(feature_coverage.get('quality') or 'missing'),
        'confirmed_features': present_feature_names,
        'missing_features': missing_feature_names,
        'interpretation': chart_interpretation,
    }


def reporter_evaluation(execution_quality, key_finding, monitor_consistency, reporter_reason, reporter_status, run_grade, strategy_alignment, trade_quality):
    return {
        'status': reporter_status,
        'reason': reporter_reason,
        'strategy_alignment': strategy_alignment,
        'execution_quality': execution_quality,
        'monitor_consistency': monitor_consistency,
        'run_grade': run_grade or '-',
        'trade_quality': trade_quality,
        'key_finding': key_finding,
    }


def operator_conclusion(final_action, thesis_invalidation, watch_next):
    return {
        'current_action': final_action,
        'watch_next': watch_next[:4],
        'thesis_invalidation': thesis_invalidation,
    }


def risk_alerts(defensive_mode, thesis_invalidation, weak_factors):
    return {
        'defensive_mode': defensive_mode,
        'weak_factors': weak_factors[:4],
        'thesis_invalidation': thesis_invalidation[:3],
    }

