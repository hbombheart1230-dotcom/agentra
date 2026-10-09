from __future__ import annotations

import json
from typing import Any, Dict, Mapping

def build_market_context_summary(section: Any, *, scanner_reason: Dict[str, Any] | None = None, deps: Mapping[str, Any]) -> str:
    _clip = deps["clip"]
    _extract_korea_indices_snapshot = deps["extract_korea_indices_snapshot"]
    _extract_us_indices_snapshot = deps["extract_us_indices_snapshot"]
    _format_korea_indices_sentence = deps["format_korea_indices_sentence"]
    _format_pct_points = deps["format_pct_points"]
    _market_token_label = deps["market_token_label"]
    _num_opt = deps["num_opt"]
    _theme_text = deps["theme_text"]
    market = section if isinstance(section, dict) else {}
    scanner = scanner_reason if isinstance(scanner_reason, dict) else {}
    regime = _market_token_label(market.get("regime")) or ""
    market_sentiment = _market_token_label(market.get("market_sentiment")) or ""
    selected_playbook = _market_token_label(market.get("selected_playbook")) or _clip(market.get("selected_playbook"), max_len=40)
    playbook = _market_token_label(market.get("playbook")) or selected_playbook or "not_captured"
    themes = _theme_text(market.get("themes") or market.get("preferred_themes"), max_items=3)
    sentiment = _num_opt(market.get("global_sentiment_score"))
    fear_index = market.get("fear_index") if isinstance(market.get("fear_index"), dict) else {}
    vix_level = _num_opt(market.get("vix_level"))
    if vix_level is None:
        vix_level = _num_opt(fear_index.get("level"))
    headline_count = int(float(market.get("headline_count") or 0)) if _num_opt(market.get("headline_count")) is not None else 0
    query_count = int(float(market.get("news_query_count") or 0)) if _num_opt(market.get("news_query_count")) is not None else 0
    us_indices = _extract_us_indices_snapshot(market.get("key_events") or market.get("key_events_hint"))
    korea_indices_text = _format_korea_indices_sentence(_extract_korea_indices_snapshot(market))
    selected_symbol = _clip(scanner.get("selected_symbol"), max_len=24)

    regime_missing = regime in {"", "not_captured", "unknown", "직접 캡처되지 않음"}
    sentiment_missing = market_sentiment in {"", "not_captured", "unknown", "직접 캡처되지 않음"}
    playbook_known = playbook not in {"", "not_captured", "unknown", "직접 캡처되지 않음"}
    themes_known = themes not in {"", "not_captured", "unknown", "직접 캡처되지 않음"}

    if regime_missing and sentiment_missing and (playbook_known or themes_known):
        frame_bits: List[str] = []
        if playbook_known:
            frame_bits.append(f"플레이북 {playbook}")
        if themes_known:
            frame_bits.append(f"핵심 테마 {themes}")
        frame_text = ", ".join(frame_bits) if frame_bits else "핵심 프레임 미확인"
        sentences: List[str] = [
            f"시장 상태/심리 직접 캡처는 제한적이지만, {frame_text} 기준으로 정리했습니다."
        ]
    else:
        regime_text = regime or "not_captured"
        sentences = [
            f"시장 상태 {regime_text} 기준에서 플레이북 {playbook}로 운용했습니다."
        ]

    metric_bits: List[str] = []
    if sentiment is not None:
        metric_bits.append(f"글로벌 감성 {sentiment:.3f}")
    if vix_level is not None:
        metric_bits.append(f"VIX {vix_level:.2f}")
    if metric_bits:
        sentences.append(", ".join(metric_bits) + " 입력은 시장 안정성 점검에 반영되었습니다.")
    if us_indices:
        sentences.append(
            f"미국 지수는 S&P500 {_format_pct_points(us_indices.get('sp500'))}, "
            f"Nasdaq {_format_pct_points(us_indices.get('nasdaq'))}, Dow {_format_pct_points(us_indices.get('dow'))}였습니다."
        )
    if korea_indices_text:
        sentences.append(f"국내 지수는 {korea_indices_text} 기준으로 반영했습니다.")
    if headline_count or query_count:
        sentences.append(
            f"뉴스 입력 {headline_count}건과 조회 대상 {query_count}개를 함께 반영했습니다."
        )
    if themes_known:
        theme_sentence = f"핵심 테마는 {themes}로 정리됐습니다."
        if selected_symbol:
            theme_sentence = f"핵심 테마 {themes} 기준에서 {selected_symbol}이 스캐너 연결 종목으로 확인됐습니다."
        sentences.append(theme_sentence)
    return " ".join(sentences[:5]).strip()



def build_market_context_bullets(section: Any, *, scanner_reason: Dict[str, Any] | None = None, deps: Mapping[str, Any]) -> List[str]:
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
    _select_symbol_headline = deps["select_symbol_headline"]
    _theme_text = deps["theme_text"]
    data = section if isinstance(section, dict) else {}
    scanner = scanner_reason if isinstance(scanner_reason, dict) else {}
    regime = _market_token_label(data.get("regime")) or ""
    market_sentiment = _market_token_label(data.get("market_sentiment")) or ""
    selected_playbook = _market_token_label(data.get("selected_playbook")) or _clip(data.get("selected_playbook"), max_len=40)
    playbook = _market_token_label(data.get("playbook")) or selected_playbook or "not_captured"
    themes = _theme_text(data.get("themes") or data.get("preferred_themes"), max_items=4)
    sentiment = _num_opt(data.get("global_sentiment_score"))
    fear_index = data.get("fear_index") if isinstance(data.get("fear_index"), dict) else {}
    vix_level = _num_opt(data.get("vix_level"))
    if vix_level is None:
        vix_level = _num_opt(fear_index.get("level"))
    vix_change = _num_opt(fear_index.get("change_pct"))
    headline_count = int(float(data.get("headline_count") or 0)) if _num_opt(data.get("headline_count")) is not None else 0
    query_count = int(float(data.get("news_query_count") or 0)) if _num_opt(data.get("news_query_count")) is not None else 0
    us_indices = _extract_us_indices_snapshot(data.get("key_events") or data.get("key_events_hint"))
    korea_indices_text = _format_korea_indices_sentence(_extract_korea_indices_snapshot(data))
    market_titles = _join_headlines(data.get("market_news_titles") or data.get("market_headlines"), max_items=2, max_len=180)
    symbol_title = _select_symbol_headline(
        data.get("symbol_news_titles")
        or data.get("symbol_headlines")
        or data.get("strategist_symbol_headlines")
        or data.get("candidate_news_titles"),
        _clip(scanner.get("selected_symbol"), max_len=24),
    )
    targets = ", ".join(_listify(data.get("news_query_targets"), max_items=7, max_len=40))
    theme_source = _clip(data.get("theme_source"), max_len=80)
    theme_status = _clip(data.get("theme_source_status"), max_len=80)
    theme_reason = _clip(data.get("theme_source_reason"), max_len=160)
    theme_top = ", ".join(_listify(data.get("theme_strength_top_themes"), max_items=6, max_len=80))

    bullets: List[str] = []
    regime_missing = regime in {"", "not_captured", "unknown", "직접 캡처되지 않음"}
    sentiment_missing = market_sentiment in {"", "not_captured", "unknown", "직접 캡처되지 않음"}
    themes_known = themes not in {"", "not_captured", "unknown", "직접 캡처되지 않음"}
    if regime_missing and sentiment_missing and (playbook != "not_captured" or themes_known):
        bullets.append(
            f"시장 상태/심리 직접 캡처는 제한적이며, 플레이북 {playbook}, 핵심 테마 {themes if themes_known else 'not_captured'} 기준으로 해석했습니다."
        )
    else:
        bullets.append(
            f"시장 상태는 {regime or 'not_captured'}, 시장 심리는 {market_sentiment or 'not_captured'}, 플레이북은 {playbook}, 핵심 테마는 {themes} 기준입니다."
        )
    if sentiment is not None or vix_level is not None:
        metric = []
        if sentiment is not None:
            metric.append(f"글로벌 감성 {sentiment:.3f}")
        if vix_level is not None:
            change_text = f", 변화율 {_format_pct_points(vix_change)}" if vix_change is not None else ""
            metric.append(f"VIX {vix_level:.2f}{change_text}")
        bullets.append("변동성/심리 입력은 " + ", ".join(metric) + "입니다.")
    if us_indices:
        bullets.append(
            f"미국 지수는 S&P500 {_format_pct_points(us_indices.get('sp500'))}, "
            f"Nasdaq {_format_pct_points(us_indices.get('nasdaq'))}, Dow {_format_pct_points(us_indices.get('dow'))}였습니다."
        )
    if korea_indices_text:
        bullets.append(f"국내 지수는 {korea_indices_text}입니다.")
    if headline_count or query_count or targets:
        bullets.append(
            f"뉴스 입력은 {headline_count}건 헤드라인, 조회 대상은 {query_count}개"
            + (f" ({targets})" if targets else "")
            + "를 반영했습니다."
        )
    if market_titles:
        bullets.append(f"주요 시장 뉴스는 {market_titles}입니다.")
    if symbol_title:
        bullets.append(f"대표 종목/섹터 뉴스는 {symbol_title}입니다.")
    if theme_source or theme_status or theme_reason:
        bullets.append(
            "키움 테마 packet은 "
            f"source={theme_source or 'not_captured'}, "
            f"status={theme_status or 'not_captured'}, "
            f"reason={theme_reason or 'not_captured'}, "
            f"top_themes={theme_top or 'none'} 상태였습니다."
        )
    return _dedupe_list(bullets, max_items=10, max_len=260)



