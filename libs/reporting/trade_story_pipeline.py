from __future__ import annotations

import html
import re
from typing import Any, Dict, List, Mapping

from libs.reporting.reasoning_trace import (
    build_reasoning_provenance,
    build_reasoning_trace_from_summaries,
    normalize_reasoning_provenance_aliases,
    normalize_reasoning_trace_aliases,
)
from libs.reporting.strategy_read_model import (
    build_news_symbol_linkage_view,
    build_strategist_feedback_input_view,
)
from libs.reporting.trade_read_model import normalize_trade_report_section
from libs.reporting.trade_report_ai import resolve_shared_trade_facts
from libs.reporting.trade_report_common import (
    clip_text as clip,
    format_exit_label,
    format_pct,
    format_ratio_pct,
    is_empty_placeholder as _is_empty_placeholder,
    list_text as _list_text,
    merge_missing_values as _merge_missing_values,
    safe_float,
    safe_int,
    utc_now_iso,
)
from libs.reporting.trade_scanner_fallback_anchor import (
    reanchor_scanner_selection_for_monitor_fallback,
)
from libs.reporting.trade_fallback_text import (
    EXECUTION_OUTCOME_NOT_CAPTURED,
    LIFECYCLE_CONCLUSION_NOT_CAPTURED,
    REPORTER_LINKAGE_NOT_CAPTURED,
    lifecycle_conclusion_summary_is_placeholder,
)
from libs.reporting.trade_execution_outcome_text import (
    build_execution_outcome_fallback_from_lifecycle,
    execution_outcome_summary_is_placeholder,
)
from libs.reporting.trade_reporter_status_text import normalize_reporter_status_human
from libs.reporting.trade_story_evidence import (
    derive_evidence_provenance as _derive_evidence_provenance_impl,
    has_substantive_exit_evidence as _has_substantive_exit_evidence_impl,
    set_or_replace_placeholder as _set_or_replace_placeholder_impl,
)
from libs.reporting.trade_story_pipeline_evidence_hydration import (
    normalized_feature_coverage_from_scanner_evidence as _normalized_feature_coverage_from_scanner_evidence_impl,
    build_scanner_selection_trace as _build_scanner_selection_trace_impl,
    build_news_scanner_contribution_trace as _build_news_scanner_contribution_trace_impl,
    attach_news_scanner_contribution as _attach_news_scanner_contribution_impl,
    enrich_scanner_reason_from_evidence as _enrich_scanner_reason_from_evidence_impl,
    enrich_filters_from_evidence as _enrich_filters_from_evidence_impl,
    hydrate_canonical_agent_artifacts as _hydrate_canonical_agent_artifacts_impl,
    resolve_selection_monitor_artifact as _resolve_selection_monitor_artifact_impl,
    safe_read_json_file as _safe_read_json_file_impl,
)
from libs.reporting.trade_story_pipeline_human_payloads import (
    build_filters_human as _build_filters_human_impl,
    build_scanner_reason_human as _build_scanner_reason_human_impl,
    build_monitor_reason_human as _build_monitor_reason_human_impl,
    build_market_context_human as _build_market_context_human_impl,
    build_execution_outcome_human as _build_execution_outcome_human_impl,
    build_monitor_blocker_trace as _build_monitor_blocker_trace_impl,
    build_monitor_stop_policy_trace as _build_monitor_stop_policy_trace_impl,
    normalize_stop_thresholds as _normalize_stop_thresholds_impl,
    resolve_adaptive_stop_loss_pct as _resolve_adaptive_stop_loss_pct_impl,
    resolve_strategist_adaptive_exit as _resolve_strategist_adaptive_exit_impl,
)
from libs.reporting.trade_story_pipeline_story_assembly import (
    build_trade_story_input as _build_trade_story_input_impl,
    build_report_section_seeds as _build_report_section_seeds_impl,
    build_lifecycle_bundle as _build_lifecycle_bundle_impl,
    build_timeline as _build_timeline_impl,
    collect_story_warnings as _collect_story_warnings_impl,
    compact_canonical_monitor as _compact_canonical_monitor_impl,
    normalize_trade_lifecycle_for_story_input as _normalize_trade_lifecycle_for_story_input_impl,
)
from libs.core.symbols import normalize_symbol


def _has_substantive_exit_evidence(exit_payload: Any) -> bool:
    return _has_substantive_exit_evidence_impl(exit_payload)


def _set_or_replace_placeholder(target: Dict[str, Any], key: str, value: Any) -> None:
    _set_or_replace_placeholder_impl(target, key, value)


def _derive_evidence_provenance(bundle_out: Dict[str, Any]) -> Dict[str, Any]:
    return _derive_evidence_provenance_impl(bundle_out)


def _safe_read_json_file(path_value: Any) -> Dict[str, Any]:
    return _safe_read_json_file_impl(path_value)


def _hydrate_canonical_agent_artifacts(
    bundle_out: Dict[str, Any],
    canonical_agent_artifacts: Dict[str, Any] | None,
) -> Dict[str, Any]:
    return _hydrate_canonical_agent_artifacts_impl(
        bundle_out,
        canonical_agent_artifacts,
        read_json_file=_safe_read_json_file,
    )


def _resolve_selection_monitor_artifact(
    bundle_out: Dict[str, Any],
    canonical_agent_artifacts: Dict[str, Any] | None,
) -> Dict[str, Any]:
    return _resolve_selection_monitor_artifact_impl(
        bundle_out,
        canonical_agent_artifacts,
        read_json_file=_safe_read_json_file,
    )


def _headline_text(row: Any) -> str:
    item = row if isinstance(row, dict) else {}
    for key in ("title", "headline", "summary", "description", "text", "news_title"):
        text = clip(item.get(key), max_len=180)
        if text:
            return text
    return ""


def _clean_news_fragment(value: Any, *, max_len: int = 180) -> str:
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return clip(text, max_len=max_len)


def _news_item_field(raw: Any, field: str) -> str:
    text = str(raw or "")
    for quote in ("'", '"'):
        marker = f"{field}={quote}"
        start = text.find(marker)
        if start < 0:
            continue
        start += len(marker)
        end = text.find(f"{quote}, ", start)
        if end < 0:
            end = text.find(quote, start)
        if end > start:
            return _clean_news_fragment(text[start:end])
    return ""


def _news_sample_parts(raw: Any) -> Dict[str, str]:
    if isinstance(raw, dict):
        return {
            "title": _clean_news_fragment(
                raw.get("title") or raw.get("headline") or raw.get("news_title")
            ),
            "summary": _clean_news_fragment(
                raw.get("summary") or raw.get("description") or raw.get("text"),
                max_len=260,
            ),
            "symbol": _norm_symbol_text(raw.get("symbol") or raw.get("code") or raw.get("ticker")),
        }
    return {
        "title": _news_item_field(raw, "title") or _clean_news_fragment(raw),
        "summary": _news_item_field(raw, "summary"),
        "symbol": _norm_symbol_text(_news_item_field(raw, "symbol")),
    }


def _norm_symbol_text(value: Any) -> str:
    return normalize_symbol(value, allow_test_symbols=True).strip().upper()


def _symbol_name_from_text(text: Any, symbol: str) -> str:
    target = _norm_symbol_text(symbol)
    if not target:
        return ""
    cleaned = _clean_news_fragment(text, max_len=320)
    pattern = rf"([A-Za-z0-9가-힣&·.\-\s]{{1,40}})\(\s*{re.escape(target)}\s*\)"
    match = re.search(pattern, cleaned)
    if not match:
        return ""
    name = re.sub(r"\s+", " ", str(match.group(1) or "")).strip(" ,;:·-")
    if not name:
        return ""
    # Keep the nearest token phrase; news snippets often have a long prefix.
    pieces = re.split(r"[,\s]+", name)
    return pieces[-1].strip() if pieces else name


def _sample_title_directly_matches_symbol(parts: Dict[str, str], symbol: str) -> bool:
    target = _norm_symbol_text(symbol)
    title = str(parts.get("title") or "")
    if not target or not title:
        return False
    if target in title:
        return True
    symbol_name = _symbol_name_from_text(parts.get("summary"), target)
    return bool(symbol_name and symbol_name in title)


def _format_symbol_news_headline(symbol: str, title: str, *, indirect: bool = False) -> str:
    target = _norm_symbol_text(symbol)
    cleaned = _clean_news_fragment(title)
    if not cleaned:
        return ""
    if re.match(r"\s*\d{6}\s*:", cleaned):
        return cleaned
    if indirect:
        return f"{target}: 관련 테마 뉴스 - {cleaned}" if target else f"관련 테마 뉴스 - {cleaned}"
    return f"{target}: {cleaned}" if target else cleaned


def _collect_symbol_headlines_from_ranked_rows(rows: Any, *, symbol: str, limit: int = 3) -> List[str]:
    if not isinstance(rows, list):
        return []
    target = _norm_symbol_text(symbol)
    if not target:
        return []
    direct: List[str] = []
    indirect: List[str] = []
    for row in rows:
        item = row if isinstance(row, dict) else {}
        row_target = _norm_symbol_text(
            item.get("target")
            or item.get("symbol")
            or item.get("code")
            or item.get("ticker")
        )
        if row_target and row_target != target:
            continue
        samples = item.get("sample_titles") or item.get("sample") or item.get("headlines") or []
        if not isinstance(samples, list):
            samples = [samples]
        if not samples:
            samples = [item]
        for sample in samples:
            parts = _news_sample_parts(sample)
            title = parts.get("title") or ""
            if not title:
                continue
            sample_symbol = _norm_symbol_text(parts.get("symbol"))
            summary_has_target = bool(target in str(parts.get("summary") or ""))
            title_is_direct = _sample_title_directly_matches_symbol(parts, target)
            if sample_symbol and sample_symbol != target and not summary_has_target:
                continue
            bucket = direct if title_is_direct else indirect
            headline = _format_symbol_news_headline(target, title, indirect=not title_is_direct)
            if headline and headline not in bucket:
                bucket.append(headline)
    picked = direct if direct else indirect
    return picked[: max(1, int(limit))]


def _headline_matches_symbol(row: Any, symbol: str) -> bool:
    item = row if isinstance(row, dict) else {}
    target = _norm_symbol_text(symbol)
    if not target:
        return False
    scalar_candidates = [
        item.get("symbol"),
        item.get("code"),
        item.get("ticker"),
        item.get("query_target"),
        item.get("query"),
        item.get("news_query_target"),
    ]
    for candidate in scalar_candidates:
        if _norm_symbol_text(candidate) == target:
            return True
    for key in ("symbols", "tickers", "related_symbols"):
        values = item.get(key)
        if not isinstance(values, list):
            continue
        for candidate in values:
            if _norm_symbol_text(candidate) == target:
                return True
    joined = " ".join(
        [
            str(item.get("title") or ""),
            str(item.get("headline") or ""),
            str(item.get("summary") or ""),
            str(item.get("description") or ""),
            str(item.get("query_target") or ""),
        ]
    ).upper()
    return bool(target and target in joined)


def _collect_top_headlines(rows: Any, *, limit: int = 3, symbol: str = "") -> List[str]:
    if not isinstance(rows, list):
        return []
    filtered: List[str] = []
    fallback: List[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        text = _headline_text(row)
        if not text:
            continue
        if text not in fallback:
            fallback.append(text)
        if symbol and _headline_matches_symbol(row, symbol) and text not in filtered:
            filtered.append(text)
    picked = filtered if symbol else fallback
    return picked[: max(1, int(limit))]


def _raw_strategist_evidence(bundle_out: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(bundle_out.get("strategist_evidence"), dict):
        return dict(bundle_out.get("strategist_evidence") or {})
    evidence = bundle_out.get("evidence") if isinstance(bundle_out.get("evidence"), dict) else {}
    if isinstance(evidence.get("strategist"), dict):
        return dict(evidence.get("strategist") or {})
    return {}


def _strategist_trace_source(
    canonical_strategist: Dict[str, Any],
    raw_strategist_evidence: Dict[str, Any],
) -> Dict[str, Any]:
    source = dict(canonical_strategist or {})
    raw = raw_strategist_evidence if isinstance(raw_strategist_evidence, dict) else {}
    # Raw evidence carries the structured news rows. Prefer those over stale
    # flattened market_context headlines when rebuilding reports.
    if raw.get("news_evidence_ranked") is not None:
        source["news_evidence_ranked"] = raw.get("news_evidence_ranked")
    if raw.get("market_context_snapshots") is not None and source.get("market_context_snapshots") is None:
        source["market_context_snapshots"] = raw.get("market_context_snapshots")
    return source


def _title_prefixed_symbol(value: Any) -> str:
    match = re.match(r"\s*(\d{6})\s*:", str(value or ""))
    return match.group(1) if match else ""


def _list_text_for_symbol(values: Any, *, symbol: str, limit: int = 3, max_len: int = 180) -> List[str]:
    target = _norm_symbol_text(symbol)
    rows = _list_text(values, limit=50, max_len=max_len)
    if not target:
        return rows[: max(1, int(limit))]
    matched: List[str] = []
    untagged: List[str] = []
    has_detectable_symbol = False
    for row in rows:
        row_symbol = _title_prefixed_symbol(row)
        if row_symbol:
            has_detectable_symbol = True
        if row_symbol == target and row not in matched:
            matched.append(row)
        elif not row_symbol and row not in untagged:
            untagged.append(row)
    if matched:
        return matched[: max(1, int(limit))]
    if not has_detectable_symbol:
        return untagged[: max(1, int(limit))]
    return []


def _korea_indices_bullet(korea_indices: Any) -> str:
    packet = korea_indices if isinstance(korea_indices, dict) else {}
    indices = packet.get("indices") if isinstance(packet.get("indices"), dict) else {}
    parts: List[str] = []
    for name in ("KOSPI", "KOSDAQ"):
        row = indices.get(name) if isinstance(indices.get(name), dict) else {}
        if not row:
            continue
        parts.append(
            f"{name} current={format_pct(row.get('current'))} "
            f"previous_close={format_pct(row.get('previous_close'))} "
            f"change={format_pct(row.get('change_pct'))}%"
        )
    return "; ".join(parts)


def _top_numeric_drivers(values: Any, *, limit: int = 4) -> Dict[str, float]:
    if not isinstance(values, dict):
        return {}
    scored: List[tuple[float, str, float]] = []
    for key, value in values.items():
        try:
            numeric = float(value)
        except Exception:
            continue
        if numeric == 0.0:
            continue
        scored.append((abs(numeric), str(key), numeric))
    scored.sort(key=lambda row: (-row[0], row[1]))
    out: Dict[str, float] = {}
    for _, key, numeric in scored[: max(1, int(limit))]:
        out[key] = numeric
    return out


def _scanner_chart_fit_payload(row: Mapping[str, Any] | None) -> Dict[str, Any]:
    obj = dict(row or {}) if isinstance(row, Mapping) else {}
    score = obj.get("scanner_chart_fit_score")
    authority = str(obj.get("scanner_chart_fit_authority") or "").strip()
    components = obj.get("scanner_chart_fit_components") if isinstance(obj.get("scanner_chart_fit_components"), dict) else {}
    if score in (None, "") and not authority and not components:
        return {}
    return {
        "score": safe_float(score, 0.0) if score not in (None, "") else None,
        "authority": authority,
        "components": dict(components or {}),
    }


def _scanner_macro_chart_fit_payload(row: Mapping[str, Any] | None) -> Dict[str, Any]:
    obj = dict(row or {}) if isinstance(row, Mapping) else {}
    score = obj.get("scanner_macro_chart_fit_score")
    authority = str(obj.get("scanner_macro_chart_fit_authority") or "").strip()
    components = (
        obj.get("scanner_macro_chart_fit_components")
        if isinstance(obj.get("scanner_macro_chart_fit_components"), dict)
        else {}
    )
    bias = obj.get("scanner_macro_chart_fit_bias")
    if score in (None, "") and bias in (None, "") and not authority and not components:
        return {}
    return {
        "score": safe_float(score, 0.0) if score not in (None, "") else None,
        "bias": safe_float(bias, 0.0) if bias not in (None, "") else None,
        "authority": authority,
        "components": dict(components or {}),
    }


def _candidate_sources_from_score_breakdown(score_breakdown: Mapping[str, Any] | None) -> List[str]:
    scores = dict(score_breakdown or {})
    sources: List[str] = []
    if safe_float(scores.get("trading_value"), 0.0) > 0.0:
        sources.append("top_value")
    if safe_float(scores.get("volume_surge"), 0.0) > 0.0:
        sources.append("top_volume")
    if safe_float(scores.get("theme_boost"), 0.0) > 0.0:
        sources.append("sector_theme")
    if safe_float(scores.get("sentiment"), 0.0) > 0.0:
        sources.append("sentiment")
    return sources


def _selection_basis_from_scores(
    score_breakdown: Mapping[str, Any] | None,
    sources: List[str],
) -> List[str]:
    scores = dict(score_breakdown or {})
    basis: List[str] = []
    if safe_float(scores.get("trading_value"), 0.0) > 0.0 or "top_value" in sources:
        basis.append("trading value")
    if safe_float(scores.get("volume_surge"), 0.0) > 0.0 or "top_volume" in sources:
        basis.append("turnover and volume")
    if safe_float(scores.get("theme_boost"), 0.0) > 0.0 or "sector_theme" in sources:
        basis.append("theme and sector alignment")
    if safe_float(scores.get("sentiment"), 0.0) > 0.0 or "sentiment" in sources:
        basis.append("sentiment support")
    if not basis and safe_float(scores.get("momentum"), 0.0) > 0.0:
        basis.append("momentum")
    if not basis and safe_float(scores.get("trend"), 0.0) > 0.0:
        basis.append("trend")
    if not basis:
        basis.append("combined scanner ranking score")
    return basis


def _scanner_candidate_row_from_evidence(
    scanner_evidence: Mapping[str, Any] | None,
    *,
    selected_symbol: str,
) -> Dict[str, Any]:
    symbol = str(selected_symbol or "").strip()
    if not symbol:
        return {}
    evidence = dict(scanner_evidence or {})
    for collection_name in ("candidate_ranking_tables", "selection_outputs"):
        for event in list(evidence.get(collection_name) or []):
            payload = event.get("payload") if isinstance(event, dict) and isinstance(event.get("payload"), dict) else {}
            rows: List[Any] = []
            if collection_name == "candidate_ranking_tables":
                rows = list(payload.get("rows") or [])
            else:
                rows = list(payload.get("ranking_top_n") or payload.get("scanner_top_candidates") or [])
                selected_candidate = payload.get("selected_candidate") if isinstance(payload.get("selected_candidate"), dict) else {}
                if selected_candidate:
                    rows.append(selected_candidate)
            for row in rows:
                if not isinstance(row, dict) or str(row.get("symbol") or "").strip() != symbol:
                    continue
                candidate = dict(row)
                score_breakdown = (
                    candidate.get("score_breakdown")
                    if isinstance(candidate.get("score_breakdown"), dict)
                    else {}
                )
                if not isinstance(candidate.get("sources"), list):
                    candidate["sources"] = _candidate_sources_from_score_breakdown(score_breakdown)
                return candidate
    return {}


def _build_strategist_evidence_trace(
    strategist: Dict[str, Any],
    *,
    selected_symbol: str = "",
    fallback_market_titles: Any = None,
    fallback_candidate_titles: Any = None,
) -> Dict[str, Any]:
    data = strategist if isinstance(strategist, dict) else {}
    news_ranked_raw = data.get("news_evidence_ranked")
    news_ranked = news_ranked_raw if isinstance(news_ranked_raw, dict) else {}
    if not news_ranked and isinstance(news_ranked_raw, list):
        for event in news_ranked_raw:
            payload = event.get("payload") if isinstance(event, dict) else {}
            if isinstance(payload, dict) and (
                payload.get("candidate_news_ranked") is not None
                or payload.get("market_news_ranked") is not None
            ):
                news_ranked = dict(payload)
                break
    global_signal = data.get("global_sentiment_signal") if isinstance(data.get("global_sentiment_signal"), dict) else {}
    fear_index = data.get("fear_index") if isinstance(data.get("fear_index"), dict) else {}
    if not fear_index and isinstance(global_signal.get("fear_index"), dict):
        fear_index = dict(global_signal.get("fear_index") or {})
    market_rows = list(news_ranked.get("market_news_ranked") or [])
    candidate_rows = list(news_ranked.get("candidate_news_ranked") or [])
    market_headlines = _collect_top_headlines(market_rows, limit=3)
    symbol_headlines = _collect_symbol_headlines_from_ranked_rows(
        candidate_rows,
        symbol=selected_symbol,
        limit=3,
    ) or _collect_top_headlines(candidate_rows, limit=3, symbol=selected_symbol)
    if not market_headlines:
        market_headlines = _list_text(fallback_market_titles, limit=3, max_len=180)
    if not symbol_headlines:
        symbol_headlines = _list_text_for_symbol(
            fallback_candidate_titles,
            symbol=selected_symbol,
            limit=3,
            max_len=180,
        )
    candidate_hints = _list_text(
        data.get("candidate_symbols_hint"),
        limit=8,
        max_len=24,
    )
    key_events = _list_text(
        data.get("key_events") if data.get("key_events") is not None else data.get("key_events_hint"),
        limit=6,
        max_len=180,
    )
    return {
        "candidate_hints": candidate_hints,
        "news_query_targets": _list_text(
            data.get("news_query_targets")
            if data.get("news_query_targets") is not None
            else news_ranked.get("news_query_targets"),
            limit=8,
            max_len=80,
        ),
        "market_headlines": market_headlines,
        "symbol_headlines": symbol_headlines,
        "global_sentiment_signal": dict(global_signal or {}),
        "korea_indices": dict(global_signal.get("korea_indices") or {}) if isinstance(global_signal.get("korea_indices"), dict) else {},
        "fear_index": dict(fear_index or {}),
        "key_events": key_events,
    }


def _scanner_evidence_trace_deps() -> Dict[str, Any]:
    return {
        "scanner_chart_fit_payload": _scanner_chart_fit_payload,
        "scanner_macro_chart_fit_payload": _scanner_macro_chart_fit_payload,
        "top_numeric_drivers": _top_numeric_drivers,
        "clip": clip,
        "safe_int": safe_int,
        "collect_top_headlines": _collect_top_headlines,
        "list_text": _list_text,
        "optional_float": _optional_float,
        "safe_float": safe_float,
        "build_news_scanner_contribution_trace": _build_news_scanner_contribution_trace,
        "set_or_replace_placeholder": _set_or_replace_placeholder,
    }

def _build_scanner_selection_trace(scanner_reason: Dict[str, Any], scanner_artifact: Dict[str, Any]) -> Dict[str, Any]:
    return _build_scanner_selection_trace_impl(scanner_reason, scanner_artifact, deps=_scanner_evidence_trace_deps())

def _optional_float(value: Any) -> Any:
    if value in (None, ""):
        return None
    return safe_float(value, 0.0)


def _build_news_scanner_contribution_trace(
    *,
    selected_symbol: str,
    selected_score: Any,
    selected_sources: List[str],
    score_breakdown: Dict[str, Any],
    component_snapshot: Dict[str, Any],
    strategist: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_news_scanner_contribution_trace_impl(
        selected_symbol=selected_symbol,
        selected_score=selected_score,
        selected_sources=selected_sources,
        score_breakdown=score_breakdown,
        component_snapshot=component_snapshot,
        strategist=strategist,
        deps=_scanner_evidence_trace_deps(),
    )

def _attach_news_scanner_contribution(
    *,
    scanner_reason_human: Dict[str, Any],
    scanner_selection_trace: Dict[str, Any],
    canonical_scanner: Dict[str, Any],
    canonical_strategist: Dict[str, Any],
    selected_symbol: str,
) -> None:
    return _attach_news_scanner_contribution_impl(
        scanner_reason_human=scanner_reason_human,
        scanner_selection_trace=scanner_selection_trace,
        canonical_scanner=canonical_scanner,
        canonical_strategist=canonical_strategist,
        selected_symbol=selected_symbol,
        deps=_scanner_evidence_trace_deps(),
    )

def _normalize_stop_thresholds(thresholds: Dict[str, Any]) -> Dict[str, Any]:
    return _normalize_stop_thresholds_impl(thresholds)


def _resolve_strategist_adaptive_exit(monitor: Dict[str, Any]) -> Dict[str, Any]:
    return _resolve_strategist_adaptive_exit_impl(monitor)


def _resolve_adaptive_stop_loss_pct(monitor: Dict[str, Any], thresholds: Dict[str, Any]) -> Any:
    return _resolve_adaptive_stop_loss_pct_impl(monitor, thresholds)


def _build_monitor_stop_policy_trace(monitor: Dict[str, Any], thresholds: Dict[str, Any]) -> Dict[str, Any]:
    return _build_monitor_stop_policy_trace_impl(monitor, thresholds)


def _build_monitor_blocker_trace(monitor: Dict[str, Any]) -> Dict[str, Any]:
    return _build_monitor_blocker_trace_impl(monitor)


def _source_confidence_label(source: Any) -> str:
    raw = str(source or "").strip().lower()
    if raw in {"canonical", "normalized_trade_artifact", "normalized_trade"}:
        return "high"
    if raw in {"direct_artifact", "direct"}:
        return "medium"
    if raw in {"event_log", "fallback", "inferred"}:
        return "low"
    return "low"


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def compute_evidence_completeness(story_input: Dict[str, Any]) -> Dict[str, Any]:
    obj = dict(story_input or {})
    required_sections = [
        "market_context_human",
        "scanner_reason_human",
        "filters_human",
        "monitor_reason_human",
        "guard_reason_human",
        "execution_outcome_human",
        "operator_conclusion_human",
    ]
    present_sections: List[str] = []
    missing_sections: List[str] = []
    for key in required_sections:
        value = obj.get(key)
        if isinstance(value, dict) and (_is_present(value.get("summary")) or _is_present(value.get("bullets"))):
            present_sections.append(key)
        elif _is_present(value):
            present_sections.append(key)
        else:
            missing_sections.append(key)
    score = float(len(present_sections)) / float(len(required_sections)) if required_sections else 1.0
    return {
        "required_sections": required_sections,
        "present_sections": present_sections,
        "missing_sections": missing_sections,
        "completeness_score": score,
    }


def _safe_path_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_ref_map(values: Any) -> Dict[str, str]:
    if not isinstance(values, dict):
        return {}
    out: Dict[str, str] = {}
    for key, value in values.items():
        out[str(key)] = _safe_path_text(value)
    return out


def _resolve_commander_source_ref(refs: Dict[str, Any], section_provenance: Dict[str, Any]) -> str:
    ref_map = _safe_ref_map(refs)
    section_map = dict(section_provenance or {})
    return str(
        ref_map.get("canonical_commander_json")
        or ref_map.get("canonical_commander")
        or (section_map.get("market_context_human") or {}).get("artifact_path")
        or (section_map.get("operator_conclusion_human") or {}).get("artifact_path")
        or ""
    )


def _commander_reasoning_flag(source: Dict[str, Any], commander_summary: Dict[str, Any], key: str) -> bool:
    summary_obj = dict(commander_summary or {})
    if key in summary_obj and isinstance(summary_obj.get(key), bool):
        return bool(summary_obj.get(key))
    latest_provenance = source.get("latest_reasoning_trace_provenance")
    if isinstance(latest_provenance, dict) and key in latest_provenance and isinstance(latest_provenance.get(key), bool):
        return bool(latest_provenance.get(key))
    commander_obj = source.get("commander")
    if isinstance(commander_obj, dict) and key in commander_obj and isinstance(commander_obj.get(key), bool):
        return bool(commander_obj.get(key))
    return False


def _commander_reasoning_source_priority(source: Dict[str, Any], commander_summary: Dict[str, Any]) -> List[str]:
    summary_obj = dict(commander_summary or {})
    latest_provenance = source.get("latest_reasoning_trace_provenance") if isinstance(source.get("latest_reasoning_trace_provenance"), dict) else {}
    commander_obj = source.get("commander") if isinstance(source.get("commander"), dict) else {}
    for candidate in (latest_provenance, commander_obj, summary_obj):
        values = [str(x or "").strip() for x in list(candidate.get("source_priority") or []) if str(x or "").strip()]
        if values:
            return values
    return []


def build_commander_evidence(commander_payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(commander_payload or {})
    return {
        "schema_version": "commander_evidence.v1",
        "session_type": str(payload.get("session_type") or ""),
        "market_regime_summary": str(payload.get("market_regime_summary") or ""),
        "goal": str(payload.get("goal") or ""),
        "decision_path": str(payload.get("final_runtime_path") or payload.get("path") or ""),
        "invocation_plan": [str(x or "") for x in list(payload.get("agent_invocation_plan") or []) if str(x or "").strip()],
        "final_reason": str(payload.get("final_reason") or payload.get("reason") or ""),
    }


def _story_assembly_deps() -> Dict[str, Any]:
    return {
        "commander_reasoning_flag": _commander_reasoning_flag,
        "commander_reasoning_source_priority": _commander_reasoning_source_priority,
        "resolve_commander_source_ref": _resolve_commander_source_ref,
        "safe_ref_map": _safe_ref_map,
        "build_reasoning_provenance": build_reasoning_provenance,
        "build_reasoning_trace_from_summaries": build_reasoning_trace_from_summaries,
        "compute_evidence_completeness": compute_evidence_completeness,
        "normalize_reasoning_provenance_aliases": normalize_reasoning_provenance_aliases,
        "normalize_reasoning_trace_aliases": normalize_reasoning_trace_aliases,
        "resolve_shared_trade_facts": resolve_shared_trade_facts,
        "list_text": _list_text,
        "normalize_trade_report_section": normalize_trade_report_section,
        "attach_news_scanner_contribution": _attach_news_scanner_contribution,
        "build_monitor_blocker_trace": _build_monitor_blocker_trace,
        "build_monitor_stop_policy_trace": _build_monitor_stop_policy_trace,
        "build_scanner_selection_trace": _build_scanner_selection_trace,
        "build_strategist_evidence_trace": _build_strategist_evidence_trace,
        "compact_canonical_monitor": _compact_canonical_monitor,
        "derive_evidence_provenance": _derive_evidence_provenance,
        "has_substantive_exit_evidence": _has_substantive_exit_evidence,
        "hydrate_canonical_agent_artifacts": _hydrate_canonical_agent_artifacts,
        "is_empty_placeholder": _is_empty_placeholder,
        "raw_strategist_evidence": _raw_strategist_evidence,
        "resolve_selection_monitor_artifact": _resolve_selection_monitor_artifact,
        "set_or_replace_placeholder": _set_or_replace_placeholder,
        "strategist_trace_source": _strategist_trace_source,
        "build_execution_outcome_fallback_from_lifecycle": build_execution_outcome_fallback_from_lifecycle,
        "build_news_symbol_linkage_view": build_news_symbol_linkage_view,
        "build_operator_conclusion_human": build_operator_conclusion_human,
        "build_report_section_provenance_seeds": build_report_section_provenance_seeds,
        "build_report_section_seeds": build_report_section_seeds,
        "build_section_provenance": build_section_provenance,
        "build_strategist_feedback_input_view": build_strategist_feedback_input_view,
        "enrich_filters_from_evidence": enrich_filters_from_evidence,
        "enrich_scanner_reason_from_evidence": enrich_scanner_reason_from_evidence,
        "execution_outcome_summary_is_placeholder": execution_outcome_summary_is_placeholder,
        "lifecycle_conclusion_summary_is_placeholder": lifecycle_conclusion_summary_is_placeholder,
        "normalize_reporter_status_human": normalize_reporter_status_human,
        "reanchor_scanner_selection_for_monitor_fallback": reanchor_scanner_selection_for_monitor_fallback,
        "EXECUTION_OUTCOME_NOT_CAPTURED": EXECUTION_OUTCOME_NOT_CAPTURED,
        "LIFECYCLE_CONCLUSION_NOT_CAPTURED": LIFECYCLE_CONCLUSION_NOT_CAPTURED,
        "REPORTER_LINKAGE_NOT_CAPTURED": REPORTER_LINKAGE_NOT_CAPTURED,
    }

def build_lifecycle_bundle(
    *,
    day: str,
    trade_id: str,
    run_id: str,
    symbol: str,
    lifecycle: Dict[str, Any],
    strategist_summary: Dict[str, Any],
    scanner_summary: Dict[str, Any],
    monitor_summary: Dict[str, Any],
    commander_summary: Dict[str, Any],
    story_input: Dict[str, Any],
    diagnostics: Dict[str, Any],
    canonical_refs: Dict[str, Any],
    llm_refs: Dict[str, Any],
    artifact_links: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_lifecycle_bundle_impl(
        day=day,
        trade_id=trade_id,
        run_id=run_id,
        symbol=symbol,
        lifecycle=lifecycle,
        strategist_summary=strategist_summary,
        scanner_summary=scanner_summary,
        monitor_summary=monitor_summary,
        commander_summary=commander_summary,
        story_input=story_input,
        diagnostics=diagnostics,
        canonical_refs=canonical_refs,
        llm_refs=llm_refs,
        artifact_links=artifact_links,
        deps=_story_assembly_deps(),
    )

def _section_source_entry(
    *,
    source: str,
    artifact_path: str = "",
) -> Dict[str, str]:
    return {
        "source": str(source or "fallback"),
        "artifact_path": str(artifact_path or ""),
        "confidence": _source_confidence_label(source),
    }


def build_section_provenance(bundle_out: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    artifacts = bundle_out.get("artifacts") if isinstance(bundle_out.get("artifacts"), dict) else {}
    evidence_provenance = _derive_evidence_provenance(bundle_out)

    def _agent_source(agent: str) -> str:
        return str(evidence_provenance.get(agent) or "fallback").strip().lower()

    def _agent_path(agent: str) -> str:
        canonical_key = f"canonical_{agent}_json"
        canonical_path = str(artifacts.get(canonical_key) or "").strip()
        if canonical_path:
            return canonical_path
        if agent == "reporter":
            return str(artifacts.get("reporter_analysis_json") or "").strip()
        return str(artifacts.get("agent_pipeline_trace_json") or "").strip()

    strategist_entry = _section_source_entry(
        source=_agent_source("strategist"),
        artifact_path=_agent_path("strategist"),
    )
    scanner_entry = _section_source_entry(
        source=_agent_source("scanner"),
        artifact_path=_agent_path("scanner"),
    )
    monitor_entry = _section_source_entry(
        source=_agent_source("monitor"),
        artifact_path=_agent_path("monitor"),
    )
    supervisor_entry = _section_source_entry(
        source=_agent_source("supervisor"),
        artifact_path=_agent_path("supervisor"),
    )
    executor_entry = _section_source_entry(
        source=_agent_source("executor"),
        artifact_path=_agent_path("executor"),
    )
    reporter_entry = _section_source_entry(
        source=_agent_source("reporter"),
        artifact_path=_agent_path("reporter"),
    )
    commander_entry = _section_source_entry(
        source=_agent_source("commander"),
        artifact_path=_agent_path("commander"),
    )
    return {
        "market_context_human": strategist_entry,
        "scanner_reason_human": scanner_entry,
        "filters_human": scanner_entry,
        "monitor_reason_human": monitor_entry,
        "guard_reason_human": supervisor_entry,
        "execution_outcome_human": executor_entry,
        "reporter_status_human": reporter_entry,
        "operator_conclusion_human": commander_entry,
        "timeline": commander_entry,
    }


def _section_seed_provenance_entry(section_provenance: Dict[str, Any], key: str) -> Dict[str, str]:
    entry = section_provenance.get(key) if isinstance(section_provenance.get(key), dict) else {}
    return {
        "source": str(entry.get("source") or "fallback"),
        "artifact_path": str(entry.get("artifact_path") or ""),
        "confidence": str(entry.get("confidence") or _source_confidence_label(entry.get("source"))),
    }


def build_report_section_seeds(
    *,
    market_context_human: Dict[str, Any],
    scanner_reason_human: Dict[str, Any],
    filters_human: Dict[str, Any],
    monitor_reason_human: Dict[str, Any] | None = None,
    execution_outcome_human: Dict[str, Any] | None = None,
    guard_reason_human: Dict[str, Any] | None = None,
    reporter_status_human: Dict[str, Any] | None = None,
    operator_conclusion_human: Dict[str, Any] | None = None,
) -> Dict[str, Dict[str, Any]]:
    return _build_report_section_seeds_impl(
        market_context_human=market_context_human,
        scanner_reason_human=scanner_reason_human,
        filters_human=filters_human,
        monitor_reason_human=monitor_reason_human,
        execution_outcome_human=execution_outcome_human,
        guard_reason_human=guard_reason_human,
        reporter_status_human=reporter_status_human,
        operator_conclusion_human=operator_conclusion_human,
        deps=_story_assembly_deps(),
    )

def build_report_section_provenance_seeds(section_provenance: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    provenance = dict(section_provenance or {})
    return {
        "market_context_at_entry": _section_seed_provenance_entry(provenance, "market_context_human"),
        "strategist_summary": _section_seed_provenance_entry(provenance, "market_context_human"),
        "why_this_symbol_was_chosen": _section_seed_provenance_entry(provenance, "scanner_reason_human"),
        "entry_decision": _section_seed_provenance_entry(provenance, "scanner_reason_human"),
        "holding_monitoring_story": _section_seed_provenance_entry(provenance, "monitor_reason_human"),
        "exit_decision": _section_seed_provenance_entry(provenance, "execution_outcome_human"),
        "scanner_filters": _section_seed_provenance_entry(provenance, "filters_human"),
        "execution_quality": _section_seed_provenance_entry(provenance, "execution_outcome_human"),
        "guard_approval_result": _section_seed_provenance_entry(provenance, "guard_reason_human"),
        "reporter_evaluation": _section_seed_provenance_entry(provenance, "reporter_status_human"),
        "final_operator_conclusion": _section_seed_provenance_entry(provenance, "operator_conclusion_human"),
    }


def slug(value: Any, *, max_len: int = 80) -> str:
    text = re.sub(r"[^a-zA-Z0-9_-]+", "_", str(value or "").strip()).strip("_")
    if not text:
        return "item"
    return text[: max_len]


def feature_coverage(selected_candidate: Dict[str, Any]) -> Dict[str, Any]:
    feature_snapshot = (
        selected_candidate.get("feature_snapshot") if isinstance(selected_candidate.get("feature_snapshot"), dict) else {}
    )
    keys = [
        "engine_ma20_gap",
        "engine_ma60",
        "engine_ma120",
        "engine_adx14",
        "engine_trend_strength",
        "engine_atr14",
        "engine_volume_spike20",
        "engine_volatility20",
        "engine_vwap_distance",
        "engine_sector_relative_strength",
        "engine_cross_section_rank",
        "engine_regime",
        "engine_signal_score",
    ]
    present: List[str] = []
    missing: List[str] = []
    for key in keys:
        if feature_snapshot.get(key) is None:
            missing.append(key)
        else:
            present.append(key)
    return {
        "present": len(present),
        "total": len(keys),
        "present_keys": present,
        "missing_keys": missing,
    }


def normalized_feature_coverage(scanner: Dict[str, Any], selected_candidate: Dict[str, Any]) -> Dict[str, Any]:
    reported = scanner.get("feature_coverage") if isinstance(scanner.get("feature_coverage"), dict) else {}
    computed = feature_coverage(selected_candidate)
    present = safe_int(reported.get("present"), computed.get("present"))
    total = safe_int(reported.get("total"), computed.get("total"))
    coverage_ratio = safe_float(
        reported.get("coverage_ratio"),
        (present / total) if total > 0 else 0.0,
    )
    quality = str(reported.get("quality") or "").strip().lower()
    if not quality:
        if total <= 0:
            quality = "missing"
        elif coverage_ratio >= 0.75:
            quality = "strong"
        elif coverage_ratio >= 0.5:
            quality = "partial"
        else:
            quality = "weak"
    reported_present_keys = [str(x or "") for x in list(reported.get("present_keys") or []) if str(x or "").strip()]
    reported_missing_keys = [str(x or "") for x in list(reported.get("missing_keys") or []) if str(x or "").strip()]
    computed_present = safe_int(computed.get("present"), 0)
    computed_total = safe_int(computed.get("total"), 0)
    reported_key_counts_match = bool(
        reported_present_keys
        and len(reported_present_keys) == present
        and len(reported_present_keys) + len(reported_missing_keys) == total
    )
    computed_key_counts_match = computed_present == present and computed_total == total
    computed_present_keys = [
        str(x or "") for x in list(computed.get("present_keys") or []) if str(x or "").strip()
    ]
    computed_missing_keys = [
        str(x or "") for x in list(computed.get("missing_keys") or []) if str(x or "").strip()
    ]
    present_keys = reported_present_keys if reported_key_counts_match else (computed_present_keys if computed_key_counts_match else [])
    missing_keys = reported_missing_keys if reported_key_counts_match else (computed_missing_keys if computed_key_counts_match else [])
    return {
        "present": present,
        "total": total,
        "coverage_ratio": coverage_ratio,
        "quality": quality,
        "present_keys": present_keys,
        "missing_keys": missing_keys,
    }


def confidence_label(value: Any) -> str:
    score = safe_float(value, -1.0)
    if score >= 0.85:
        return "high"
    if score >= 0.65:
        return "medium"
    if score >= 0.0:
        return "low"
    return "not_captured"


def execution_mode_label(executor: Dict[str, Any]) -> str:
    effective_mode = str(executor.get("effective_mode") or "").strip().lower()
    broker_env = str(executor.get("broker_env") or "").strip().lower()
    execution_mode = str(executor.get("execution_mode") or executor.get("mode") or "").strip().lower()
    kiwoom_mode = str(executor.get("kiwoom_mode") or "").strip().lower()
    if "mock" in effective_mode or broker_env == "mock" or kiwoom_mode == "mock":
        return "simulation (mock broker)"
    if broker_env == "real" or effective_mode == "real_broker_http":
        return "live broker"
    if execution_mode:
        return execution_mode
    return "decision only"


def classify_story_type(execution: Dict[str, Any], executor: Dict[str, Any]) -> str:
    effective_mode = str(executor.get("effective_mode") or "").strip().lower()
    broker_env = str(executor.get("broker_env") or "").strip().lower()
    kiwoom_mode = str(executor.get("kiwoom_mode") or "").strip().lower()
    execution_attempted = bool(executor.get("execution_attempted")) or bool(execution.get("action"))
    execution_ok = bool(executor.get("execution_ok"))
    if "mock" in effective_mode or broker_env == "mock" or kiwoom_mode == "mock":
        return "simulation"
    if not execution_attempted:
        return "decision_only"
    if execution_attempted and not execution_ok:
        return "failed_execution"
    return "live_trade"


def build_story_id(day: str, execution: Dict[str, Any]) -> str:
    run_id = slug(execution.get("run_id"), max_len=48)
    symbol = slug(execution.get("symbol"), max_len=24)
    action = slug(str(execution.get("action") or "").lower(), max_len=12)
    compact_day = str(day or "").replace("-", "")
    return slug(f"{compact_day}_{symbol}_{action}_{run_id}", max_len=96)


def build_story_contract(bundle_out: Dict[str, Any]) -> Dict[str, Any]:
    execution = bundle_out.get("execution") if isinstance(bundle_out.get("execution"), dict) else {}
    executor = bundle_out.get("executor") if isinstance(bundle_out.get("executor"), dict) else {}
    story_type = classify_story_type(execution, executor)
    mode_label = execution_mode_label(executor)
    story_anchor = (
        f"{execution.get('action') or 'WAIT'} {execution.get('symbol') or (bundle_out.get('scanner') or {}).get('top_stock') or '-'} "
        f"x{execution.get('qty') or 0} | run {bundle_out.get('run_id') or '-'}"
    )
    warnings: List[str] = []
    if story_type == "failed_execution":
        warnings.append("Execution was attempted but did not complete successfully.")
    if story_type == "simulation":
        warnings.append("This story reflects simulation mode, not a live broker fill.")
    return {
        "story_available": bool(execution.get("action") or execution.get("symbol") or (bundle_out.get("scanner") or {}).get("top_stock")),
        "story_type": story_type,
        "execution_mode_label": mode_label,
        "story_anchor": story_anchor,
        "warnings": warnings,
    }


def _human_payload_deps() -> Dict[str, Any]:
    return {
        "build_strategist_evidence_trace": _build_strategist_evidence_trace,
        "korea_indices_bullet": _korea_indices_bullet,
        "list_text": _list_text,
        "format_pct": format_pct,
        "safe_float": safe_float,
        "safe_int": safe_int,
        "build_news_scanner_contribution_trace": _build_news_scanner_contribution_trace,
        "build_scanner_selection_trace": _build_scanner_selection_trace,
        "scanner_chart_fit_payload": _scanner_chart_fit_payload,
        "scanner_macro_chart_fit_payload": _scanner_macro_chart_fit_payload,
        "clip": clip,
        "confidence_label": confidence_label,
        "normalized_feature_coverage": normalized_feature_coverage,
        "build_monitor_blocker_trace": _build_monitor_blocker_trace,
        "build_monitor_stop_policy_trace": _build_monitor_stop_policy_trace,
        "merge_missing_values": _merge_missing_values,
        "format_exit_label": format_exit_label,
        "format_ratio_pct": format_ratio_pct,
    }

def build_market_context_human(strategist: Dict[str, Any]) -> Dict[str, Any]:
    return _build_market_context_human_impl(strategist, deps=_human_payload_deps())

def build_scanner_reason_human(scanner: Dict[str, Any], strategist: Dict[str, Any]) -> Dict[str, Any]:
    return _build_scanner_reason_human_impl(scanner, strategist, deps=_human_payload_deps())

def _evidence_enrichment_deps() -> Dict[str, Any]:
    return {
        "normalized_feature_coverage_from_scanner_evidence": _normalized_feature_coverage_from_scanner_evidence,
        "scanner_candidate_row_from_evidence": _scanner_candidate_row_from_evidence,
        "scanner_chart_fit_from_scanner_evidence": _scanner_chart_fit_from_scanner_evidence,
        "scanner_macro_chart_fit_from_scanner_evidence": _scanner_macro_chart_fit_from_scanner_evidence,
        "selection_basis_from_scores": _selection_basis_from_scores,
        "top_numeric_drivers": _top_numeric_drivers,
        "clip": clip,
        "safe_float": safe_float,
        "safe_int": safe_int,
    }

def _evidence_enrichment_deps() -> Dict[str, Any]:
    return {
        "enrich_filters_from_evidence_impl": _enrich_filters_from_evidence_impl,
        "enrich_scanner_reason_from_evidence_impl": _enrich_scanner_reason_from_evidence_impl,
        "evidence_enrichment_deps": _evidence_enrichment_deps,
    }

def enrich_scanner_reason_from_evidence(
    scanner_reason_human: Dict[str, Any],
    scanner_evidence: Dict[str, Any],
) -> Dict[str, Any]:
    return _enrich_scanner_reason_from_evidence_impl(scanner_reason_human, scanner_evidence, deps=_evidence_enrichment_deps())

def _scanner_chart_fit_from_scanner_evidence(
    scanner_evidence: Dict[str, Any],
    *,
    selected_symbol: str,
) -> Dict[str, Any]:
    symbol = str(selected_symbol or "").strip()
    if not symbol:
        return {}
    ranking_sources: List[Dict[str, Any]] = []
    for row in list((scanner_evidence or {}).get("candidate_ranking_tables") or []):
        payload = row.get("payload") if isinstance(row, dict) and isinstance(row.get("payload"), dict) else {}
        for ranking_row in list(payload.get("rows") or []):
            if isinstance(ranking_row, dict):
                ranking_sources.append(ranking_row)
    for row in list((scanner_evidence or {}).get("selection_outputs") or []):
        payload = row.get("payload") if isinstance(row, dict) and isinstance(row.get("payload"), dict) else {}
        for ranking_row in list(payload.get("ranking_top_n") or []):
            if isinstance(ranking_row, dict):
                ranking_sources.append(ranking_row)
        selected_candidate = payload.get("selected_candidate") if isinstance(payload.get("selected_candidate"), dict) else {}
        if selected_candidate:
            ranking_sources.append(selected_candidate)
    for row in ranking_sources:
        if str(row.get("symbol") or "").strip() != symbol:
            continue
        chart_fit = _scanner_chart_fit_payload(row)
        if chart_fit:
            return chart_fit
    return {}


def _scanner_macro_chart_fit_from_scanner_evidence(
    scanner_evidence: Dict[str, Any],
    *,
    selected_symbol: str,
) -> Dict[str, Any]:
    symbol = str(selected_symbol or "").strip()
    if not symbol:
        return {}
    ranking_sources: List[Dict[str, Any]] = []
    for row in list((scanner_evidence or {}).get("candidate_ranking_tables") or []):
        payload = row.get("payload") if isinstance(row, dict) and isinstance(row.get("payload"), dict) else {}
        for ranking_row in list(payload.get("rows") or []):
            if isinstance(ranking_row, dict):
                ranking_sources.append(ranking_row)
    for row in list((scanner_evidence or {}).get("selection_outputs") or []):
        payload = row.get("payload") if isinstance(row, dict) and isinstance(row.get("payload"), dict) else {}
        for ranking_row in list(payload.get("ranking_top_n") or []):
            if isinstance(ranking_row, dict):
                ranking_sources.append(ranking_row)
        selected_candidate = payload.get("selected_candidate") if isinstance(payload.get("selected_candidate"), dict) else {}
        if selected_candidate:
            ranking_sources.append(selected_candidate)
    for row in ranking_sources:
        if str(row.get("symbol") or "").strip() != symbol:
            continue
        chart_fit = _scanner_macro_chart_fit_payload(row)
        if chart_fit:
            return chart_fit
    return {}


def _normalized_feature_coverage_from_scanner_evidence(
    scanner_evidence: Dict[str, Any],
    *,
    selected_symbol: str,
) -> Dict[str, Any]:
    return _normalized_feature_coverage_from_scanner_evidence_impl(
        scanner_evidence,
        selected_symbol=selected_symbol,
        deps=_scanner_evidence_trace_deps(),
    )

def enrich_filters_from_evidence(
    filters_human: Dict[str, Any],
    scanner_evidence: Dict[str, Any],
    *,
    selected_symbol: str,
    monitor_evidence: Optional[Dict[str, Any]] = None,
    entry_execution_details: Optional[Dict[str, Any]] = None,
    exit_execution_details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return _enrich_filters_from_evidence_impl(
        filters_human,
        scanner_evidence,
        selected_symbol=selected_symbol,
        monitor_evidence=monitor_evidence,
        entry_execution_details=entry_execution_details,
        exit_execution_details=exit_execution_details,
        deps=_evidence_enrichment_deps(),
    )

def build_filters_human(scanner: Dict[str, Any], strategist: Dict[str, Any], supervisor: Dict[str, Any]) -> Dict[str, Any]:
    return _build_filters_human_impl(scanner, strategist, supervisor, deps=_human_payload_deps())

def build_monitor_reason_human(monitor: Dict[str, Any], execution: Dict[str, Any]) -> Dict[str, Any]:
    return _build_monitor_reason_human_impl(monitor, execution, deps=_human_payload_deps())

def build_guard_reason_human(supervisor: Dict[str, Any]) -> Dict[str, Any]:
    allow = bool(supervisor.get("supervisor_allow"))
    verdict = str(supervisor.get("verdict") or "").strip() or ("approve" if allow else "block")
    reason = str(supervisor.get("supervisor_reason") or supervisor.get("guard_reason") or "").strip() or "not captured"
    summary = (
        f"Supervisor approved the order because {reason}."
        if allow
        else f"Supervisor blocked the order because {reason}."
    )
    bullets = [
        f"Supervisor verdict: {verdict}",
        f"Supervisor allow: {'yes' if allow else 'no'}",
        f"Guard reason: {reason}",
        f"Action reviewed: {supervisor.get('action') or 'not_captured'}",
        f"Symbol reviewed: {supervisor.get('symbol') or 'not_captured'}",
        "Approval mode: not captured in the execution trace",
    ]
    return {"summary": summary, "bullets": bullets, "allow": allow, "verdict": verdict}


def build_execution_outcome_human(
    execution: Dict[str, Any],
    executor: Dict[str, Any],
    *,
    story_type: str,
    mode_label: str,
) -> Dict[str, Any]:
    return _build_execution_outcome_human_impl(
        execution,
        executor,
        story_type=story_type,
        mode_label=mode_label,
    )


def build_reporter_status_human(reporter: Dict[str, Any], reporter_day_obj: Dict[str, Any]) -> Dict[str, Any]:
    linked = bool(reporter.get("reporter_analysis_found"))
    day_file_found = bool(reporter.get("reporter_analysis_day_file_found"))
    ai_summary = str(reporter.get("reporter_analysis_summary") or reporter_day_obj.get("ai_summary") or "").strip()
    grade = str(reporter_day_obj.get("ai_run_grade") or "N/A").strip()
    if linked:
        status = "linked"
        reason = "당일 리포터 분석이 이 run에 연결됐습니다."
    elif day_file_found:
        status = "pending"
        reason = "당일 리포터 파일은 있지만 이 run에 대한 개별 평가는 아직 연결되지 않았습니다."
    else:
        status = "missing"
        reason = "당일 리포터 분석은 아직 생성되지 않았습니다."
    if status == "linked":
        summary = ai_summary or reason
    elif ai_summary:
        summary = f"{reason} 중간 요약: {ai_summary}"
    else:
        summary = reason
    bullets = [
        f"리포터 상태는 {status}입니다.",
        f"리포터 판단 사유는 {reason}입니다.",
        f"리포터 등급은 {grade}입니다.",
        f"리포터 요약은 {summary}입니다.",
    ]
    return normalize_reporter_status_human({
        "status": status,
        "reason": reason,
        "grade": grade,
        "summary": summary,
        "bullets": bullets,
    })


def build_operator_conclusion_human(
    *,
    execution: Dict[str, Any],
    scanner_reason_human: Dict[str, Any],
    filters_human: Dict[str, Any],
    monitor_reason_human: Dict[str, Any],
    execution_outcome_human: Dict[str, Any],
    reporter_status_human: Dict[str, Any],
) -> Dict[str, Any]:
    action = str(execution.get("action") or "").upper() or "WAIT"
    outcome_text = str(execution_outcome_human.get("summary") or "").upper()
    outcome_ko = str(execution_outcome_human.get("summary") or "")
    if action != "SELL" and ("SELL" in outcome_text or "매도" in outcome_ko):
        action = "SELL"
    elif action not in {"BUY", "SELL"} and ("BUY" in outcome_text or "매수" in outcome_ko):
        action = "BUY"
    watch_next: List[str] = []
    invalidation: List[str] = [
        "거시 환경이 부정적으로 전환되는지 확인해야 합니다.",
        "테마나 섹터 강도가 약해지는지 확인해야 합니다.",
        "스캐너와 모니터 판단이 다시 어긋나는지 확인해야 합니다.",
    ]
    if action == "BUY":
        summary_prefix = "현재 판단은 진입 유지입니다."
        watch_next.append("보유 포지션의 손절과 익절 기준이 유지되는지 확인해야 합니다.")
        watch_next.append("선택된 테마와 종목의 상대 강도가 유지되는지 확인해야 합니다.")
    elif action == "SELL":
        summary_prefix = "현재 판단은 청산 완료입니다."
        watch_next.append("이번 청산이 방어적으로 타당했는지, 과도한 노이즈 청산은 아니었는지 복기해야 합니다.")
        watch_next.append("재진입은 쿨다운 이후 새 스캐너 확인이 있을 때만 검토해야 합니다.")
    elif action == "HOLD":
        summary_prefix = "현재 판단은 보유 유지입니다."
        watch_next.append("보유 근거가 약해지는지와 모니터 경고 축 변화를 계속 확인해야 합니다.")
    else:
        summary_prefix = "현재 판단은 관망입니다."
        watch_next.append("새로운 스캐너 순위와 모니터 확인이 나올 때까지 관망해야 합니다.")
    if reporter_status_human.get("status") != "linked":
        watch_next.append("동일 일자 리포터 분석 연계가 가능해지면 후속 확인이 필요합니다.")
    if "FAIL" in " ".join(row.get("status") or "" for row in list(filters_human.get("checks") or [])):
        watch_next.append("실패했거나 비어 있던 필터를 다시 확인하기 전에는 다음 사이클을 공격적으로 해석하면 안 됩니다.")
    summary = (
        f"{summary_prefix} "
        f"{execution_outcome_human.get('summary') or scanner_reason_human.get('summary') or monitor_reason_human.get('summary')}"
    )
    return {
        "current_action": action,
        "summary": summary,
        "watch_next": watch_next[:6],
        "thesis_invalidation": invalidation[:6],
    }


def build_timeline(
    *,
    commander: Dict[str, Any],
    market_context_human: Dict[str, Any],
    scanner_reason_human: Dict[str, Any],
    monitor_reason_human: Dict[str, Any],
    guard_reason_human: Dict[str, Any],
    execution_outcome_human: Dict[str, Any],
    reporter_status_human: Dict[str, Any],
    execution: Dict[str, Any],
) -> List[Dict[str, Any]]:
    return _build_timeline_impl(
        commander=commander,
        market_context_human=market_context_human,
        scanner_reason_human=scanner_reason_human,
        monitor_reason_human=monitor_reason_human,
        guard_reason_human=guard_reason_human,
        execution_outcome_human=execution_outcome_human,
        reporter_status_human=reporter_status_human,
        execution=execution,
    )


def collect_story_warnings(
    *,
    story_contract: Dict[str, Any],
    market_context_human: Dict[str, Any],
    filters_human: Dict[str, Any],
    reporter_status_human: Dict[str, Any],
    execution_outcome_human: Dict[str, Any],
) -> List[str]:
    return _collect_story_warnings_impl(
        story_contract=story_contract,
        market_context_human=market_context_human,
        filters_human=filters_human,
        reporter_status_human=reporter_status_human,
        execution_outcome_human=execution_outcome_human,
    )


def _normalize_trade_lifecycle_for_story_input(
    bundle_out: Dict[str, Any],
    *,
    trade_lifecycle: Dict[str, Any] | None = None,
    existing_story_input: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _normalize_trade_lifecycle_for_story_input_impl(
        bundle_out,
        trade_lifecycle=trade_lifecycle,
        existing_story_input=existing_story_input,
    )


def build_trade_story_input_from_bundle(
    bundle_out: Dict[str, Any],
    *,
    trade_lifecycle: Dict[str, Any] | None = None,
    existing_story_input: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    normalized_lifecycle = _normalize_trade_lifecycle_for_story_input(
        bundle_out,
        trade_lifecycle=trade_lifecycle,
        existing_story_input=existing_story_input,
    )
    story_input = build_trade_story_input(
        bundle_out,
        trade_lifecycle=normalized_lifecycle if normalized_lifecycle else trade_lifecycle,
    )
    existing = existing_story_input if isinstance(existing_story_input, dict) else {}
    for key in (
        "report_runtime_mode",
        "skip_separated_report_llm",
        "entry_strategist_run_id",
        "strategy_anchor_run_id",
    ):
        if key not in story_input and key in existing:
            story_input[key] = existing.get(key)
    for key in ("trade_id", "day", "run_id"):
        if story_input.get(key) in (None, "", [], {}) and existing.get(key) not in (None, "", [], {}):
            story_input[key] = existing.get(key)
    return story_input


def _compact_canonical_monitor(canonical_monitor: Dict[str, Any] | None) -> Dict[str, Any]:
    return _compact_canonical_monitor_impl(canonical_monitor)


def build_trade_story_input(
    bundle_out: Dict[str, Any],
    *,
    trade_lifecycle: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _build_trade_story_input_impl(bundle_out, trade_lifecycle=trade_lifecycle, deps=_story_assembly_deps())

def render_bundle_markdown(out: Dict[str, Any]) -> str:
    story_contract = out.get("story_contract") if isinstance(out.get("story_contract"), dict) else {}
    lines: List[str] = []
    lines.append(f"# Aggregated Execution Bundle ({out.get('run_id')})")
    lines.append("")
    lines.append(f"- day: **{out.get('day')}**")
    lines.append(f"- story_anchor: **{story_contract.get('story_anchor') or '-'}**")
    lines.append(f"- story_type: **{story_contract.get('story_type') or '-'}**")
    lines.append(f"- execution_mode: **{story_contract.get('execution_mode_label') or '-'}**")
    lines.append("")
    sections = [
        ("Market Context", out.get("market_context_human")),
        ("Why This Symbol", out.get("scanner_reason_human")),
        ("Filters / Gates", out.get("filters_human")),
        ("Monitor / Trigger Reasoning", out.get("monitor_reason_human")),
        ("Guard / Approval", out.get("guard_reason_human")),
        ("Execution Outcome", out.get("execution_outcome_human")),
        ("Reporter Status", out.get("reporter_status_human")),
        ("Operator Conclusion", out.get("operator_conclusion_human")),
    ]
    for title, section in sections:
        data = section if isinstance(section, dict) else {}
        lines.append(f"## {title}")
        lines.append("")
        if data.get("summary"):
            lines.append(str(data.get("summary")))
            lines.append("")
        for bullet in list(data.get("bullets") or [])[:8]:
            lines.append(f"- {bullet}")
        lines.append("")
    lines.append("## Timeline")
    lines.append("")
    for row in list(out.get("timeline") or [])[:10]:
        if not isinstance(row, dict):
            continue
        lines.append(f"- {row.get('step')}: {row.get('summary') or '-'}")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    for key, value in dict(out.get("artifacts") or {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    return "\n".join(lines)


def render_summary_markdown(out: Dict[str, Any]) -> str:
    bundles = out.get("bundles") if isinstance(out.get("bundles"), list) else []
    lines: List[str] = []
    lines.append(f"# Live Execution Bundles ({out.get('day')})")
    lines.append("")
    lines.append(f"- bundle_count: **{out.get('bundle_count')}**")
    lines.append(f"- canonical_trades_root: `{out.get('canonical_trades_root')}`")
    lines.append("")
    if not bundles:
        lines.append("No executed BUY/SELL runs were found for the selected day.")
        lines.append("")
        return "\n".join(lines)
    lines.append("## Bundles")
    lines.append("")
    for row in bundles:
        lines.append(
            f"- `{row.get('run_id')}` {row.get('action')} {row.get('symbol')} x{row.get('qty')} "
            f"story=`{row.get('story_type')}` report=`{row.get('trade_report_json_path')}`"
        )
    lines.append("")
    return "\n".join(lines)
