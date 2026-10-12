"""Strategist news context merging, ranking and sentiment breakdown (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _build_market_news_query_reasoning_r3_impl(
    *,
    state,
    policy,
    global_signal,
    market_context_inputs,
    theme_hints,
    facade,
):
    explicit_targets: List[str] = []
    if isinstance(state.get("news_query_targets"), list):
        explicit_targets.extend([str(x).strip() for x in list(state.get("news_query_targets") or []) if str(x).strip()])
    if isinstance(policy.get("news_query_targets"), list):
        explicit_targets.extend([str(x).strip() for x in list(policy.get("news_query_targets") or []) if str(x).strip()])
    env_targets = str(facade.os.getenv("NEWS_QUERY_TARGETS", "") or "").strip()
    if env_targets:
        explicit_targets.extend([x.strip() for x in env_targets.split(",") if str(x).strip()])

    global_score = facade._signal_score(global_signal)
    macro_risk = facade._to_float(market_context_inputs.get("macro_risk"), 0.0)
    index_trend = facade._to_float(market_context_inputs.get("index_trend"), 0.0)
    realized_volatility = facade._to_float(market_context_inputs.get("realized_volatility"), 0.0)
    market_breadth = facade._to_float(market_context_inputs.get("market_breadth"), 0.0)
    fear_index = global_signal.get("fear_index") if isinstance(global_signal.get("fear_index"), dict) else {}
    vix_level = facade._to_float(fear_index.get("level"), 0.0)
    vix_pressure = facade._to_float(fear_index.get("level_pressure"), 0.0)
    elevated_fear = vix_level >= 25.0 or vix_pressure >= 0.25

    reasons: List[str] = [
        (
            f"global_score={global_score:.2f} macro_risk={macro_risk:.2f} "
            f"index_trend={index_trend:.2f} vix={vix_level:.2f} vix_pressure={vix_pressure:.3f}"
        )
    ]
    if explicit_targets:
        reasons.append(f"explicit_targets_first={', '.join(explicit_targets[:4])}")

    if macro_risk >= 0.65:
        reasons.append("risk-off macro context added oil/fx/geopolitics market queries")
    elif elevated_fear:
        reasons.append("elevated fear index added defensive macro and hedge queries")
    elif global_score <= -0.20:
        reasons.append("risk-off sentiment added oil/fx/geopolitics market queries")
    elif global_score >= 0.20 and index_trend >= -0.05:
        reasons.append("risk-on context added leader/risk-appetite market queries")
    else:
        reasons.append("neutral context kept broad market and macro queries")

    normalized_themes = [str(x).strip() for x in list(theme_hints or []) if str(x).strip()]
    if normalized_themes:
        reasons.append(f"theme hints expanded queries from {', '.join(normalized_themes[:3])}")

    if realized_volatility >= 0.03:
        reasons.append("intraday volatility added 변동성 확대 query")
    if market_breadth <= 0.40:
        reasons.append("weak breadth added 하락 종목 수/약세 업종 queries")
    elif market_breadth >= 0.60:
        reasons.append("strong breadth added 상승 종목 수/주도 섹터 queries")

    for key in ("macro_events", "global_events", "major_events"):
        values = state.get(key)
        if isinstance(values, list):
            normalized = [str(x).strip() for x in list(values or []) if str(x).strip()]
            if normalized:
                reasons.append(f"macro events appended {', '.join(normalized[:2])}")
                break

    return "; ".join(reasons)


def _news_context_summary_r3_impl(news_signal_map, news_items_by_symbol, *, facade):
    total = 0
    unavailable = 0
    fallback = 0
    ok = 0
    score_sum = 0.0
    score_cnt = 0
    headline_count = 0

    for symbol, sig in news_signal_map.items():
        _ = symbol
        total += 1
        st = str((sig or {}).get("status") or "").strip().lower()
        if st == "ok":
            ok += 1
        elif st == "fallback":
            fallback += 1
        elif st == "unavailable":
            unavailable += 1
        try:
            score_sum += float((sig or {}).get("score") or 0.0)
            score_cnt += 1
        except Exception:
            pass

    for rows in (news_items_by_symbol or {}).values():
        if isinstance(rows, list):
            headline_count += len(rows)

    avg_score = (score_sum / float(score_cnt)) if score_cnt > 0 else 0.0
    return {
        "signal_total": int(total),
        "ok": int(ok),
        "fallback": int(fallback),
        "unavailable": int(unavailable),
        "avg_score": float(facade._clamp(avg_score, -1.0, 1.0)),
        "headline_count": int(headline_count),
    }


def _merge_news_contexts_r3_impl(candidate_ctx, market_ctx, *, facade):
    cand_total = int(candidate_ctx.get("signal_total") or 0)
    market_total = int(market_ctx.get("signal_total") or 0)
    total = cand_total + market_total
    avg_score = 0.0
    if total > 0:
        avg_score = (
            (facade._to_float(candidate_ctx.get("avg_score"), 0.0) * float(cand_total))
            + (facade._to_float(market_ctx.get("avg_score"), 0.0) * float(market_total))
        ) / float(total)
    return {
        "signal_total": int(total),
        "ok": int(candidate_ctx.get("ok") or 0) + int(market_ctx.get("ok") or 0),
        "fallback": int(candidate_ctx.get("fallback") or 0) + int(market_ctx.get("fallback") or 0),
        "unavailable": int(candidate_ctx.get("unavailable") or 0) + int(market_ctx.get("unavailable") or 0),
        "avg_score": float(facade._clamp(avg_score, -1.0, 1.0)),
        "headline_count": int(candidate_ctx.get("headline_count") or 0) + int(market_ctx.get("headline_count") or 0),
        "candidate_signal_total": int(cand_total),
        "candidate_headline_count": int(candidate_ctx.get("headline_count") or 0),
        "market_signal_total": int(market_total),
        "market_headline_count": int(market_ctx.get("headline_count") or 0),
    }


def _sample_news_for_evidence_r3_impl(news_items_by_symbol, *, max_symbols, max_items_per_symbol, facade):
    out: Dict[str, Any] = {}
    for symbol, rows in list(news_items_by_symbol.items())[:max_symbols]:
        sample: List[Any] = []
        if isinstance(rows, list):
            for item in rows[:max_items_per_symbol]:
                if isinstance(item, dict):
                    sample.append(
                        {
                            "title": str(item.get("title") or ""),
                            "source": str(item.get("source") or ""),
                            "published_at": str(item.get("published_at") or ""),
                        }
                    )
                else:
                    sample.append(str(item))
        out[str(symbol)] = {"count": len(rows) if isinstance(rows, list) else 0, "sample": sample}
    return out


def _rank_news_evidence_rows_r3_impl(items_by_target, signal_map, *, used_targets, scope, max_rows, facade):
    rows: List[Dict[str, Any]] = []
    used_set = {str(item or "").strip() for item in list(used_targets or []) if str(item or "").strip()}
    for target, rows_raw in (items_by_target or {}).items():
        target_text = str(target or "").strip()
        signal = signal_map.get(target_text) if isinstance(signal_map.get(target_text), dict) else {}
        sample_titles: List[str] = []
        for row in list(rows_raw or [])[:3]:
            if isinstance(row, dict):
                title = str(row.get("title") or "").strip()
            else:
                title = str(row or "").strip()
            if title:
                sample_titles.append(title)
        rows.append(
            {
                "target": target_text,
                "scope": str(scope or ""),
                "score": facade._round_optional(signal.get("score"), 4),
                "status": str(signal.get("status") or ""),
                "source": str(signal.get("source") or ""),
                "reason": str(signal.get("reason") or ""),
                "headline_count": int(len(list(rows_raw or []))),
                "sample_titles": sample_titles,
                "used_in_decision": bool(target_text in used_set),
            }
        )
    rows.sort(
        key=lambda row: (
            -abs(float(row.get("score") or 0.0)),
            -int(row.get("headline_count") or 0),
            str(row.get("target") or ""),
        )
    )
    return rows[: max(0, int(max_rows))]


def _global_sentiment_breakdown_payload_r3_impl(global_signal, *, facade):
    weights = global_signal.get("weights") if isinstance(global_signal.get("weights"), dict) else {}
    components = global_signal.get("components") if isinstance(global_signal.get("components"), dict) else {}
    fear_index = global_signal.get("fear_index") if isinstance(global_signal.get("fear_index"), dict) else {}
    neutral_vix = max(1.0, facade._to_float(fear_index.get("neutral_level"), facade._to_float(weights.get("vix_neutral_level"), 20.0)))
    vix_level = facade._to_float(components.get("vix_level"), 0.0)
    vix_level_pressure = max(0.0, min((vix_level - neutral_vix) / neutral_vix, 2.0))
    contributions: List[Dict[str, Any]] = []
    factor_specs = (
        ("sp500", "sp500_ret", 1.0, ""),
        ("nasdaq", "nasdaq_ret", 1.0, ""),
        ("dow", "dow_ret", 1.0, ""),
        ("kospi", "kospi_ret", 1.0, ""),
        ("kosdaq", "kosdaq_ret", 1.0, ""),
        ("vix", "vix_ret", -1.0, "higher VIX change reduces risk appetite"),
        (
            "vix_level",
            "vix_level",
            -1.0,
            "weighted contribution uses normalized vix_level_pressure instead of raw VIX level",
        ),
        ("dxy", "dxy_ret", -1.0, "stronger dollar reduces risk appetite"),
        ("tnx", "tnx_delta", -1.0, "higher yields reduce risk appetite"),
    )
    for weight_key, component_key, direction, note in factor_specs:
        weight = facade._to_float(weights.get(weight_key), 0.0)
        raw_value = facade._to_float(components.get(component_key), 0.0)
        effective_value = vix_level_pressure if component_key == "vix_level" else raw_value
        signed_effective_value = float(direction * effective_value)
        contributions.append(
            {
                "factor": str(component_key),
                "weight": float(weight),
                "raw_value": float(raw_value),
                "effective_value": float(effective_value),
                "signed_effective_value": signed_effective_value,
                "weighted_contribution": float(weight * signed_effective_value),
                "direction": "risk_on_supportive" if direction > 0 else "risk_off_pressure",
                "note": str(note or ""),
            }
        )
    contributions.sort(key=lambda row: -abs(float(row.get("weighted_contribution") or 0.0)))
    return {
        "score": facade._round_optional(global_signal.get("score"), 4),
        "status": str(global_signal.get("status") or ""),
        "source": str(global_signal.get("source") or ""),
        "reason": str(global_signal.get("reason") or ""),
        "raw_score": facade._round_optional(global_signal.get("raw_score"), 4),
        "index_moves": dict(global_signal.get("index_moves") or {}),
        "korea_indices": dict(global_signal.get("korea_indices") or {}),
        "macro_moves": dict(global_signal.get("macro_moves") or {}),
        "fear_index": dict(fear_index or {}),
        "factor_contributions": contributions,
    }


def _merge_news_samples_r3_impl(*samples, limit, facade):
    out: Dict[str, Any] = {}
    for sample in samples:
        if not isinstance(sample, dict):
            continue
        for key, value in sample.items():
            if len(out) >= limit:
                return out
            norm_key = str(key or "").strip()
            if not norm_key or norm_key in out:
                continue
            out[norm_key] = value
    return out
