from __future__ import annotations

from typing import Any, Dict, List, Mapping

from libs.reporting.trade_execution_outcome_text import build_execution_outcome_human_payload
from libs.reporting.trade_report_common import (
    clip_text as clip,
    format_ratio_pct,
    list_text as _list_text,
    safe_float,
)


def build_scanner_reason_human(scanner: Dict[str, Any], strategist: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _build_news_scanner_contribution_trace = deps["build_news_scanner_contribution_trace"]
    _build_scanner_selection_trace = deps["build_scanner_selection_trace"]
    _list_text = deps["list_text"]
    _scanner_chart_fit_payload = deps["scanner_chart_fit_payload"]
    _scanner_macro_chart_fit_payload = deps["scanner_macro_chart_fit_payload"]
    clip = deps["clip"]
    confidence_label = deps["confidence_label"]
    normalized_feature_coverage = deps["normalized_feature_coverage"]
    safe_float = deps["safe_float"]
    safe_int = deps["safe_int"]
    selected = scanner.get("selected_candidate") if isinstance(scanner.get("selected_candidate"), dict) else {}
    selected_symbol = str(selected.get("symbol") or scanner.get("top_stock") or "").strip()
    ranking_table = [dict(row) for row in list(scanner.get("ranking_table") or []) if isinstance(row, dict)]
    top_ranked_symbols = [str(row.get("symbol") or "").strip() for row in ranking_table if str(row.get("symbol") or "").strip()]
    if not top_ranked_symbols:
        top_ranked_symbols = [str(x or "") for x in list(scanner.get("top_ranked_symbols") or []) if str(x or "").strip()]
    selected_rank = 0
    selected_row = next(
        (row for row in ranking_table if str(row.get("symbol") or "").strip() == selected_symbol),
        {},
    )
    if selected_row:
        selected_rank = safe_int(selected_row.get("rank"), 0)
    elif selected_symbol and selected_symbol in top_ranked_symbols:
        selected_rank = int(top_ranked_symbols.index(selected_symbol) + 1)
    elif selected_symbol:
        selected_rank = 1
    universe_size = max(
        0,
        safe_int(scanner.get("universe_size"), 0)
        or safe_int(scanner.get("candidate_pool_after_filter"), 0)
        or safe_int(scanner.get("candidate_pool_before_filter"), 0)
        or len(ranking_table)
        or len(top_ranked_symbols),
    )
    selected_sources = [str(x or "") for x in list(selected.get("sources") or []) if str(x or "").strip()]
    score_breakdown = selected.get("score_breakdown") if isinstance(selected.get("score_breakdown"), dict) else {}
    component_snapshot = selected.get("component_snapshot") if isinstance(selected.get("component_snapshot"), dict) else {}
    preview_map = {
        str(row.get("symbol") or "").strip(): dict(row)
        for row in list(scanner.get("candidate_preview") or [])
        if isinstance(row, dict) and str(row.get("symbol") or "").strip()
    }
    basis: List[str] = []
    if safe_float(score_breakdown.get("trading_value"), 0.0) > 0:
        basis.append("trading value")
    if safe_float(score_breakdown.get("volume_surge"), 0.0) > 0 or "top_volume" in selected_sources:
        basis.append("turnover and volume")
    if safe_float(score_breakdown.get("theme_boost"), 0.0) > 0 or "sector_theme" in selected_sources:
        basis.append("theme and sector alignment")
    if safe_float(score_breakdown.get("sentiment"), 0.0) > 0:
        basis.append("sentiment support")
    if not basis:
        basis.append("combined scanner ranking score")
    coverage = normalized_feature_coverage(scanner, selected)
    selected_score = selected.get("score_total")
    if selected_score in (None, ""):
        selected_score = selected_row.get("score_total")
    selected_risk = selected.get("risk_score")
    if selected_risk in (None, ""):
        selected_risk = selected_row.get("risk_score")
    selected_confidence = selected.get("confidence")
    if selected_confidence in (None, ""):
        selected_confidence = selected_row.get("confidence")
    scanner_chart_fit = _scanner_chart_fit_payload(selected)
    if not scanner_chart_fit:
        scanner_chart_fit = _scanner_chart_fit_payload(selected_row)
    if not scanner_chart_fit:
        scanner_chart_fit = _scanner_chart_fit_payload(scanner)
    scanner_macro_chart_fit = _scanner_macro_chart_fit_payload(selected)
    if not scanner_macro_chart_fit:
        scanner_macro_chart_fit = _scanner_macro_chart_fit_payload(selected_row)
    if not scanner_macro_chart_fit:
        scanner_macro_chart_fit = _scanner_macro_chart_fit_payload(scanner)
    news_scanner_contribution = _build_news_scanner_contribution_trace(
        selected_symbol=selected_symbol,
        selected_score=selected_score,
        selected_sources=selected_sources,
        score_breakdown=score_breakdown,
        component_snapshot=component_snapshot,
        strategist=strategist if isinstance(strategist, dict) else {},
    )
    top_reasons: List[str] = [
        f"highest combined scanner score ({safe_float(selected_score, 0.0):.3f})",
        f"selected from {', '.join(selected_sources) if selected_sources else 'captured scanner sources'}",
        f"chart feature coverage {coverage['present']}/{coverage['total']}" if coverage["total"] > 0 else "chart feature coverage was not captured",
        f"aligned with strategist playbook {strategist.get('playbook') or 'not_captured'}",
    ]
    runner_ups: List[Dict[str, Any]] = []
    ranked_preview = ranking_table[:3] if ranking_table else []
    for row in ranked_preview:
        symbol = str(row.get("symbol") or "").strip()
        if not symbol or symbol == selected_symbol:
            continue
        preview = preview_map.get(symbol, {})
        why_parts: List[str] = []
        preview_why = clip(preview.get("why") or row.get("why"), max_len=140)
        if preview_why:
            why_parts.append(preview_why)
        score_gap = None
        if selected_score not in (None, "") and row.get("score_total") not in (None, ""):
            score_gap = safe_float(selected_score, 0.0) - safe_float(row.get("score_total"), 0.0)
            why_parts.append(f"score gap {score_gap:.3f}")
        row_risk = row.get("risk_score")
        if selected_risk not in (None, "") and row_risk not in (None, "") and safe_float(row_risk, 0.0) > safe_float(selected_risk, 0.0):
            why_parts.append(
                f"higher risk ({safe_float(row_risk, 0.0):.3f} vs {safe_float(selected_risk, 0.0):.3f})"
            )
        row_confidence = row.get("confidence")
        if selected_confidence not in (None, "") and row_confidence not in (None, "") and safe_float(row_confidence, 0.0) < safe_float(selected_confidence, 0.0):
            why_parts.append(
                f"lower confidence ({safe_float(row_confidence, 0.0):.3f} vs {safe_float(selected_confidence, 0.0):.3f})"
            )
        runner_ups.append(
            {
                "symbol": symbol,
                "rank": safe_int(row.get("rank"), 0),
                "score_total": row.get("score_total"),
                "risk_score": row.get("risk_score"),
                "confidence": row.get("confidence"),
                "scanner_chart_fit": _scanner_chart_fit_payload(row),
                "scanner_macro_chart_fit": _scanner_macro_chart_fit_payload(row),
                "why": "; ".join(why_parts) if why_parts else "lower final ranking than the selected symbol",
            }
        )
        if len(runner_ups) >= 2:
            break
    top_candidates: List[Dict[str, Any]] = []
    for row in ranked_preview:
        symbol = str(row.get("symbol") or "").strip()
        if not symbol:
            continue
        top_candidates.append(
            {
                "rank": safe_int(row.get("rank"), 0),
                "symbol": symbol,
                "score_total": row.get("score_total"),
                "risk_score": row.get("risk_score"),
                "confidence": row.get("confidence"),
                "scanner_chart_fit": _scanner_chart_fit_payload(row),
                "scanner_macro_chart_fit": _scanner_macro_chart_fit_payload(row),
            }
        )
    bullets = [
        f"Universe scanned: {universe_size}",
        f"Selected rank: #{selected_rank}" if selected_rank else "Selected rank: not_captured",
        f"Ranking basis: {', '.join(basis)}",
        f"Selected because: {top_reasons[0]}",
        f"Selection sources: {', '.join(selected_sources) if selected_sources else 'not captured'}",
        f"Chart / feature coverage: {coverage['present']}/{coverage['total']}" if coverage["total"] else "Chart / feature coverage: not captured",
        (
            "Scanner chart-fit: "
            f"{safe_float(scanner_chart_fit.get('score'), 0.0):.3f} "
            f"({scanner_chart_fit.get('authority') or 'not_captured'})"
        )
        if scanner_chart_fit
        else "Scanner chart-fit: not captured",
        (
            "Scanner macro chart-fit: "
            f"{safe_float(scanner_macro_chart_fit.get('score'), 0.0):.3f} "
            f"(bias {safe_float(scanner_macro_chart_fit.get('bias'), 0.0):+.3f})"
        )
        if scanner_macro_chart_fit
        else "Scanner macro chart-fit: not captured",
        (
            "Core score contributions: "
            f"trading_value {safe_float(score_breakdown.get('trading_value'), 0.0):+.3f}, "
            f"momentum {safe_float(score_breakdown.get('momentum'), 0.0):+.3f}, "
            f"trend {safe_float(score_breakdown.get('trend'), 0.0):+.3f}, "
            f"theme_boost {safe_float(score_breakdown.get('theme_boost'), 0.0):+.3f}, "
            f"sentiment {safe_float(score_breakdown.get('sentiment'), 0.0):+.3f}"
        ),
    ]
    sentiment_inputs = news_scanner_contribution.get("sentiment_inputs") if isinstance(news_scanner_contribution.get("sentiment_inputs"), dict) else {}
    if any(sentiment_inputs.get(key) is not None for key in ("news_sentiment_score", "global_sentiment_score", "blended_sentiment_component")):
        bullets.append(
            "Sentiment input trace: "
            f"news={safe_float(sentiment_inputs.get('news_sentiment_score'), 0.0):+.3f}, "
            f"global={safe_float(sentiment_inputs.get('global_sentiment_score'), 0.0):+.3f}, "
            f"blended={safe_float(sentiment_inputs.get('blended_sentiment_component'), 0.0):+.3f}, "
            f"weighted_score={safe_float(sentiment_inputs.get('weighted_sentiment_score_contribution'), 0.0):+.3f}"
        )
    theme_trace = news_scanner_contribution.get("theme_alignment_trace") if isinstance(news_scanner_contribution.get("theme_alignment_trace"), dict) else {}
    bullets.append(
        "Theme linkage: "
        f"matched={bool(theme_trace.get('theme_source_matched'))}, "
        f"theme_boost={safe_float(theme_trace.get('theme_boost_score_contribution'), 0.0):+.3f}, "
        f"themes={', '.join(_list_text(theme_trace.get('strategist_themes'), limit=4, max_len=60)) or 'none captured'}, "
        f"source={theme_trace.get('theme_source') or 'not_captured'}, "
        f"status={theme_trace.get('theme_source_status') or 'not_captured'}, "
        f"reason={theme_trace.get('theme_source_reason') or 'not_captured'}"
    )
    news_linkage = news_scanner_contribution.get("news_linkage_trace") if isinstance(news_scanner_contribution.get("news_linkage_trace"), dict) else {}
    if safe_int(news_linkage.get("symbol_headline_count"), 0) > 0 or safe_int(news_linkage.get("market_headline_count"), 0) > 0:
        bullets.append(
            "News linkage to scanner: "
            f"symbol_headlines={safe_int(news_linkage.get('symbol_headline_count'), 0)}, "
            f"market_headlines={safe_int(news_linkage.get('market_headline_count'), 0)}, "
            f"query_targets={', '.join(_list_text(news_linkage.get('news_query_targets'), limit=5, max_len=60)) or 'not captured'}"
        )
    if top_candidates:
        bullets.append(
            "Top candidates: "
            + "; ".join(
                f"#{safe_int(row.get('rank'), 0)} {row.get('symbol')} score {safe_float(row.get('score_total'), 0.0):.3f}"
                for row in top_candidates
            )
        )
    if runner_ups:
        bullets.append("Why not others: " + "; ".join(f"{row['symbol']} was weaker because {row['why']}" for row in runner_ups))
    scanner_selection_trace = _build_scanner_selection_trace(
        {
            "selected_symbol": selected_symbol,
            "selected_rank": selected_rank,
            "top_candidates": top_candidates,
            "score_breakdown": score_breakdown,
            "selection_basis": "; ".join(top_reasons[:3]) if top_reasons else "",
            "summary": (
                f"Scanner selected {selected_symbol or '-'} as rank #{selected_rank or 1} out of {universe_size or 0} candidates."
            ),
            "scanner_chart_fit": dict(scanner_chart_fit or {}),
            "scanner_macro_chart_fit": dict(scanner_macro_chart_fit or {}),
        },
        scanner,
    )
    scanner_selection_trace["news_scanner_contribution"] = dict(news_scanner_contribution)
    return {
        "selected_symbol": selected_symbol,
        "selected_rank": selected_rank,
        "universe_size": universe_size,
        "selected_score": selected_score,
        "selected_sources": selected_sources,
        "source_scores": selected.get("source_scores") if isinstance(selected.get("source_scores"), dict) else {},
        "score_breakdown": score_breakdown,
        "ranking_basis": basis,
        "confidence": selected_confidence,
        "confidence_label": confidence_label(selected_confidence),
        "top_reasons": top_reasons,
        "top_candidates": top_candidates,
        "runner_ups": runner_ups,
        "ranked_candidates": list(scanner_selection_trace.get("ranked_candidates") or [])[:5],
        "selection_reason": clip(scanner_selection_trace.get("selection_reason"), max_len=260),
        "selected_symbol_score_drivers": dict(scanner_selection_trace.get("selected_symbol_score_drivers") or {}),
        "scanner_chart_fit": dict(scanner_chart_fit or {}),
        "scanner_macro_chart_fit": dict(scanner_macro_chart_fit or {}),
        "news_scanner_contribution": dict(news_scanner_contribution),
        "scanner_selection_trace": dict(scanner_selection_trace or {}),
        "q9_decision_id": str(scanner.get("q9_decision_id") or ""),
        "q9_decision_snapshot": dict(scanner.get("q9_decision_snapshot") or {})
        if isinstance(scanner.get("q9_decision_snapshot"), dict)
        else {},
        "q9_decision_snapshot_path": str(scanner.get("q9_decision_snapshot_path") or ""),
        "summary": (
            f"Scanner selected {selected_symbol or '-'} as rank #{selected_rank or 1} out of {universe_size or 0} candidates "
            f"with score {safe_float(selected_score, 0.0):.3f} because it led on {', '.join(basis[:3])}."
        ),
        "comparison": (
            f"{selected_symbol} ranked #{selected_rank} out of {universe_size} because it had the strongest overall blend of "
            f"{', '.join(basis[:3])}."
            if selected_symbol
            else "Scanner did not record a selected symbol for this run."
        ),
        "bullets": bullets,
    }



