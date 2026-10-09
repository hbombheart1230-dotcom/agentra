from __future__ import annotations

import json
from typing import Any, Dict, Mapping

def build_strategist_summary_section(market_context: Dict[str, Any], scanner_reason: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _clip = deps["clip"]
    _dedupe_list = deps["dedupe_list"]
    _extract_korea_indices_snapshot = deps["extract_korea_indices_snapshot"]
    _extract_us_indices_snapshot = deps["extract_us_indices_snapshot"]
    _format_korea_indices_sentence = deps["format_korea_indices_sentence"]
    _format_pct_points = deps["format_pct_points"]
    _join_headlines = deps["join_headlines"]
    _listify = deps["listify"]
    _market_token_label = deps["market_token_label"]
    _num_opt = deps["num_opt"]
    _risk_mode_label = deps["risk_mode_label"]
    _scanner_bias_text = deps["scanner_bias_text"]
    _scanner_source_text = deps["scanner_source_text"]
    _select_symbol_headline = deps["select_symbol_headline"]
    _strategy_constraint_text = deps["strategy_constraint_text"]
    _theme_linkage_label = deps["theme_linkage_label"]
    _theme_text = deps["theme_text"]
    regime = _market_token_label(market_context.get("regime")) or ""
    market_sentiment = _market_token_label(market_context.get("market_sentiment")) or ""
    selected_playbook = _market_token_label(market_context.get("selected_playbook")) or _clip(market_context.get("selected_playbook"), max_len=40)
    playbook = _market_token_label(market_context.get("playbook")) or selected_playbook or "not_captured"
    themes = _theme_text(market_context.get("themes") or market_context.get("preferred_themes"), max_items=3)
    risk_mode = _risk_mode_label(market_context.get("risk_mode"))
    preferred_themes = _strategy_constraint_text(market_context.get("preferred_themes"), max_items=4)
    avoid_themes = _strategy_constraint_text(market_context.get("avoid_themes"), max_items=4)
    scanner_bias = _scanner_bias_text(market_context.get("scanner_bias_summary"))
    sentiment = _num_opt(market_context.get("global_sentiment_score"))
    fear_index = market_context.get("fear_index") if isinstance(market_context.get("fear_index"), dict) else {}
    vix_level = _num_opt(market_context.get("vix_level"))
    if vix_level is None:
        vix_level = _num_opt(fear_index.get("level"))
    headline_count = int(float(market_context.get("headline_count") or 0)) if _num_opt(market_context.get("headline_count")) is not None else 0
    query_count = int(float(market_context.get("news_query_count") or 0)) if _num_opt(market_context.get("news_query_count")) is not None else 0
    query_targets = ", ".join(_listify(market_context.get("news_query_targets"), max_items=7, max_len=32))
    stress_flags = _listify(market_context.get("stress_flags"), max_items=4, max_len=48)
    candidate_hints = _listify(market_context.get("candidate_hints"), max_items=4, max_len=48)
    selected_symbol = _clip(scanner_reason.get("selected_symbol"), max_len=24)
    selected_rank = scanner_reason.get("selected_rank")
    selected_score = _num_opt(scanner_reason.get("selected_score"))
    selected_sources = _scanner_source_text(scanner_reason.get("selected_sources"))
    scanner_bias_applied = bool(scanner_reason.get("scanner_bias_applied"))
    contribution = scanner_reason.get("news_scanner_contribution") if isinstance(scanner_reason.get("news_scanner_contribution"), dict) else {}
    core = contribution.get("core_score_contributions") if isinstance(contribution.get("core_score_contributions"), dict) else {}
    sentiment_inputs = contribution.get("sentiment_inputs") if isinstance(contribution.get("sentiment_inputs"), dict) else {}

    def _core_value_opt(key: str) -> Optional[float]:
        row = core.get(key)
        if isinstance(row, dict):
            return _num_opt(row.get("value"))
        return _num_opt(row)

    sentiment_contrib = _core_value_opt("sentiment")
    if sentiment_contrib is None:
        sentiment_contrib = _num_opt(sentiment_inputs.get("weighted_sentiment_score_contribution"))
    theme_boost = _core_value_opt("theme_boost")
    market_titles = _join_headlines(market_context.get("market_news_titles") or market_context.get("market_headlines"), max_items=1, max_len=110)
    symbol_title = _select_symbol_headline(
        market_context.get("symbol_news_titles")
        or market_context.get("symbol_headlines")
        or market_context.get("strategist_symbol_headlines")
        or market_context.get("candidate_news_titles"),
        selected_symbol,
    )
    theme_linkage = _theme_linkage_label(market_context.get("themes") or market_context.get("preferred_themes"))
    theme_source = _clip(market_context.get("theme_source"), max_len=80)
    theme_status = _clip(market_context.get("theme_source_status"), max_len=80)
    theme_reason = _clip(market_context.get("theme_source_reason"), max_len=160)
    theme_top = ", ".join(_listify(market_context.get("theme_strength_top_themes"), max_items=6, max_len=80))

    regime_missing = regime in {"", "not_captured", "unknown", "직접 캡처되지 않음"}
    sentiment_missing = market_sentiment in {"", "not_captured", "unknown", "직접 캡처되지 않음"}
    themes_known = themes not in {"", "not_captured", "unknown", "직접 캡처되지 않음"}

    if regime_missing and sentiment_missing:
        frame_bits: List[str] = []
        if playbook not in {"", "not_captured", "unknown", "직접 캡처되지 않음"}:
            frame_bits.append(f"플레이북 {playbook}")
        if themes_known:
            frame_bits.append(f"핵심 테마 {themes}")
        frame_text = ", ".join(frame_bits) if frame_bits else "핵심 프레임 미확인"
        summary_parts = [f"전략가는 시장 상태 직접 캡처가 제한적이어서 {frame_text} 중심으로 정리했습니다."]
    else:
        summary_parts = [f"전략가는 시장을 {regime or 'not_captured'}, 시장 심리를 {market_sentiment or 'not_captured'}으로 해석했고 {playbook} 플레이북과 {themes} 프레임을 유지했습니다."]
    if not stress_flags:
        summary_parts.append("뚜렷한 스트레스 신호는 확인되지 않았습니다.")
    if selected_symbol:
        scanner_sentence = f"스캐너 연결 종목은 {selected_symbol}입니다."
        if selected_rank not in (None, "") and selected_score is not None:
            scanner_sentence = f"스캐너 연결 종목은 {selected_symbol}이며 순위 {selected_rank}, 점수 {selected_score:.3f}입니다."
        summary_parts.append(scanner_sentence)
    summary = " ".join(summary_parts)

    bullets: List[str] = []
    input_bits: List[str] = []
    if sentiment is not None:
        input_bits.append(f"글로벌 감성 {sentiment:.3f}")
    if vix_level is not None:
        input_bits.append(f"VIX {vix_level:.2f}")
    if headline_count or query_count:
        input_bits.append(f"뉴스 {headline_count}건/{query_count}대상")
    us_indices = _extract_us_indices_snapshot(market_context.get("key_events") or market_context.get("key_events_hint"))
    if us_indices:
        input_bits.append(
            f"미국 지수 S&P500 {_format_pct_points(us_indices.get('sp500'))}, Nasdaq {_format_pct_points(us_indices.get('nasdaq'))}, Dow {_format_pct_points(us_indices.get('dow'))}"
        )
    if input_bits:
        bullets.append("핵심 입력은 " + ", ".join(input_bits) + "입니다.")
    korea_indices_text = _format_korea_indices_sentence(_extract_korea_indices_snapshot(market_context))
    if korea_indices_text:
        bullets.append("전략가는 국내 지수 " + korea_indices_text + "를 시장 상태 입력으로 사용했습니다.")

    if regime_missing and sentiment_missing:
        interpretation_bits = [f"플레이북 {playbook}"]
        if themes_known:
            interpretation_bits.append(f"핵심 테마 {themes}")
        interpretation_bits.append("스트레스 신호 없음" if not stress_flags else "스트레스 신호 " + ", ".join(stress_flags))
        bullets.append("전략 해석은 " + ", ".join(interpretation_bits) + " 기준이었습니다.")
    else:
        interpretation_bits = [f"시장 상태 {regime}", f"시장 심리 {market_sentiment}", f"플레이북 {playbook}", f"핵심 테마 {themes}"]
        if stress_flags:
            interpretation_bits.append("스트레스 신호 " + ", ".join(stress_flags))
        else:
            interpretation_bits.append("스트레스 신호 없음")
        bullets.append("전략 해석은 " + ", ".join(interpretation_bits) + " 기준이었습니다.")

    if query_targets:
        bullets.append(f"전략가가 관찰한 대상은 다음과 같았습니다: {query_targets}.")
    if risk_mode or selected_playbook:
        if risk_mode and selected_playbook:
            bullets.append(f"전략가 운용 기준은 리스크 모드 {risk_mode}이었고, 선택 플레이북은 {selected_playbook}이었습니다.")
        elif risk_mode:
            bullets.append(f"전략가 운용 기준은 리스크 모드 {risk_mode}였습니다.")
        else:
            bullets.append(f"전략가 운용 기준에서 선택 플레이북은 {selected_playbook}이었습니다.")
    if preferred_themes or avoid_themes:
        theme_pref_bits: List[str] = []
        if preferred_themes:
            theme_pref_bits.append(f"선호 테마 {preferred_themes}")
        if avoid_themes:
            theme_pref_bits.append(f"회피 테마 {avoid_themes}")
        bullets.append("전략가 선호/회피 기준은 " + ", ".join(theme_pref_bits) + "이었습니다.")
    if theme_source or theme_status or theme_reason:
        bullets.append(
            "전략가 테마 강도 입력은 "
            f"source={theme_source or 'not_captured'}, "
            f"status={theme_status or 'not_captured'}, "
            f"reason={theme_reason or 'not_captured'}, "
            f"top_themes={theme_top or 'none'} 기준이었습니다."
        )
    if scanner_bias:
        bullets.append(f"스캐너 바이어스는 {scanner_bias} 기준이었습니다.")
    if candidate_hints:
        bullets.append("전략가 후보 힌트는 " + ", ".join(candidate_hints) + "였습니다.")
    if market_titles or symbol_title:
        if market_titles and symbol_title and selected_symbol:
            linkage_line = f"뉴스 연결 해석은 시장 뉴스로 {theme_linkage} 맥락을 확인했고, 종목 뉴스로 {selected_symbol} 선정 근거를 보강했습니다."
        elif market_titles:
            linkage_line = f"뉴스 연결 해석은 시장 뉴스로 {theme_linkage} 맥락을 확인했습니다."
        elif symbol_title and selected_symbol:
            linkage_line = f"뉴스 연결 해석은 종목 뉴스로 {selected_symbol} 선정 근거를 보강했습니다."
        else:
            linkage_line = "뉴스 연결 해석은 headline evidence로 확인됐습니다."
        if selected_sources:
            linkage_line += f". 선정 소스는 {selected_sources}였습니다."
        evidence_parts: List[str] = []
        if market_titles:
            evidence_parts.append(f"시장: {market_titles}")
        if symbol_title:
            evidence_parts.append(f"종목: {symbol_title}")
        if evidence_parts:
            linkage_line += " 참조 headline: " + " / ".join(evidence_parts)
        bullets.append(linkage_line)
        if selected_sources:
            bullets.append(f"이 해석은 {selected_sources} 축으로 연결했습니다.")
    contribution_bits: List[str] = []
    if sentiment_contrib is not None:
        contribution_bits.append(f"감성 기여 {sentiment_contrib:+.3f}")
    if theme_boost is not None:
        contribution_bits.append(f"테마 가점 {theme_boost:+.3f}")
    if selected_sources:
        contribution_bits.append(f"선정 소스 {selected_sources}")
    if scanner_bias_applied:
        contribution_bits.append("바이어스 적용")
    if contribution_bits:
        bullets.append("스캐너 반영은 " + ", ".join(contribution_bits) + " 기준으로 정리됐습니다.")
    if selected_symbol:
        symbol_bits = [selected_symbol]
        if selected_rank not in (None, ""):
            symbol_bits.append(f"{selected_rank}위")
        if selected_score is not None:
            symbol_bits.append(f"점수 {selected_score:.3f}")
        bullets.append("종목 연결은 " + ", ".join(symbol_bits) + "로 확인됩니다.")
    return {
        "summary": summary,
        "bullets": _dedupe_list(bullets, max_items=12, max_len=260),
    }



