from __future__ import annotations

from typing import Any, Dict, List, Mapping


def build_market_context(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> List[str]:
    _clip = deps["clip"]
    _dedupe = deps["dedupe"]
    _is_not_captured = deps["is_not_captured"]
    _korea_index_lines = deps["korea_index_lines"]
    _listify = deps["listify"]
    _looks_corrupted = deps["looks_corrupted"]
    _market_context_structured_lines = deps["market_context_structured_lines"]
    _market_context_summary_from_raw = deps["market_context_summary_from_raw"]
    _metadata_value = deps["metadata_value"]
    _mismatched_symbol_news_bullet = deps["mismatched_symbol_news_bullet"]
    _num_opt = deps["num_opt"]
    _playbook_label = deps["playbook_label"]
    _resolve_market_context = deps["resolve_market_context"]
    _risk_mode_label = deps["risk_mode_label"]
    _sample_news_titles = deps["sample_news_titles"]
    _section_summary = deps["section_summary"]
    _theme_label = deps["theme_label"]
    _translate_text = deps["translate_text"]
    context = _resolve_market_context(report)
    lines = []
    summary = _section_summary(context)
    if summary and not _looks_corrupted(summary):
        lines.append(summary)
    structured_summary = _market_context_summary_from_raw(context.get("summary"))
    if structured_summary and structured_summary not in lines:
        lines.append(structured_summary)
    lines.extend(_market_context_structured_lines(context))
    for raw in _listify(context.get("bullets")):
        text = _translate_text(raw)
        if not text:
            continue
        if _looks_corrupted(text):
            continue
        if _mismatched_symbol_news_bullet(text, report.get("symbol")):
            continue
        raw_text = _clip(raw, 240)
        lowered = raw_text.lower()
        if lowered.startswith("global sentiment ") or lowered.startswith("global_sentiment score="):
            continue
        if lowered.startswith("vix "):
            continue
        if lowered.startswith("stress flags:"):
            continue
        if lowered.startswith("news input:"):
            continue
        if "source=" in lowered or "status=" in lowered:
            continue
        if any(key in text for key in ["스캐너 연결 근거는", "전략가 핵심 입력은", "주요 시장 뉴스는"]):
            continue
        if text not in [line.removeprefix("- ").strip() for line in lines]:
            lines.append(f"- {text}")
    headline_count = _num_opt(context.get("headline_count"))
    news_query_count = _num_opt(context.get("news_query_count"))
    market_titles = _sample_news_titles(context.get("market_news_titles"))
    if headline_count is not None and news_query_count is not None:
        lines.append(f"- 뉴스 입력은 {int(news_query_count)}개 관찰 대상에서 {int(headline_count)}개 headline을 검토했습니다.")
    elif headline_count is not None:
        lines.append(f"- 뉴스 입력은 총 {int(headline_count)}개 headline을 검토했습니다.")
    if market_titles:
        lines.append(f"- 참고한 시장 뉴스는 {' / '.join(market_titles)}였습니다.")
    fallback_summary = _translate_text(context.get("strategist_market_context_summary"))
    if (
        fallback_summary
        and not _looks_corrupted(fallback_summary)
        and not fallback_summary.lower().startswith("market regime was ")
    ):
        lines.append(f"- {fallback_summary}")
    regime = context.get("regime")
    sentiment = context.get("market_sentiment")
    playbook = context.get("selected_playbook") or context.get("playbook")
    global_sentiment = _num_opt(context.get("global_sentiment_score"))
    risk_mode = _risk_mode_label(context.get("risk_mode"))
    if not any("시장 상태는" in line or "시장 심리는" in line for line in lines):
        pieces: List[str] = []
        if not _is_not_captured(regime):
            pieces.append(f"시장 상태는 {_metadata_value(regime)}")
        if not _is_not_captured(sentiment):
            pieces.append(f"시장 심리는 {_metadata_value(sentiment)}")
        if not _is_not_captured(playbook):
            pieces.append(f"선택된 전략 프레임은 {_playbook_label(playbook)}")
        if pieces:
            lines.append(f"- {', '.join(pieces)}으로 정리됐습니다.")
    if global_sentiment is not None and not any("글로벌 감성 입력은" in line for line in lines):
        lines.append(f"- 글로벌 감성 입력은 {global_sentiment:.3f}이었고, 전체 위험 톤은 {risk_mode}으로 정리됐습니다.")
    for korea_line in _korea_index_lines(context):
        rendered = f"- 국내 지수는 {korea_line} 기준으로 반영됐습니다."
        if rendered not in lines:
            lines.append(rendered)
    preferred = [_theme_label(x) for x in _listify(context.get("preferred_themes")) if not _is_not_captured(x)]
    avoided = [_theme_label(x) for x in _listify(context.get("avoid_themes")) if not _is_not_captured(x)]
    if preferred and not any("선호 테마는" in line for line in lines):
        lines.append(f"- 선호 테마는 {', '.join(preferred)} 기준으로 정리됐습니다.")
    if avoided and not any("회피 테마는" in line for line in lines):
        lines.append(f"- 회피 테마는 {', '.join(avoided[:3])} 기준으로 정리됐습니다.")
    if not lines:
        lines.append("- 시장 환경 직접 캡처가 충분하지 않아, 저장된 실행 기록과 지휘관 정책 기준으로만 정리했습니다.")
    return _dedupe(lines)


def build_strategist_summary(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> List[str]:
    _as_dict = deps["as_dict"]
    _clip = deps["clip"]
    _dedupe = deps["dedupe"]
    _listify = deps["listify"]
    _looks_corrupted = deps["looks_corrupted"]
    _metadata_value = deps["metadata_value"]
    _mismatched_symbol_news_bullet = deps["mismatched_symbol_news_bullet"]
    _news_linkage_strength_label = deps["news_linkage_strength_label"]
    _noun_predicate_was = deps["noun_predicate_was"]
    _num_opt = deps["num_opt"]
    _playbook_label = deps["playbook_label"]
    _policy_token_label = deps["policy_token_label"]
    _resolve_market_context = deps["resolve_market_context"]
    _sample_news_titles = deps["sample_news_titles"]
    _sample_news_titles_for_symbol = deps["sample_news_titles_for_symbol"]
    _section_summary = deps["section_summary"]
    _translate_text = deps["translate_text"]
    strategist = _as_dict(report.get("strategist_summary"))
    context = _resolve_market_context(report)
    shared = _as_dict(report.get("shared_facts"))
    lines: List[str] = []
    summary = _section_summary(strategist)
    if summary and not _looks_corrupted(summary):
        lines.append(summary)
    for raw in _listify(strategist.get("bullets")):
        text = _translate_text(raw)
        if text and not _looks_corrupted(text):
            if _mismatched_symbol_news_bullet(text, report.get("symbol")):
                continue
            lines.append(f"- {text}")
    context_bullets = [_translate_text(x) for x in _listify(context.get("bullets")) if _translate_text(x)]
    for text in context_bullets:
        if _looks_corrupted(text):
            continue
        if text.startswith("전략가 핵심 입력은") or text.startswith("주요 시장 뉴스는"):
            lines.append(f"- {text}")
    if not lines:
        commander_route = _as_dict(shared.get("commander_route"))
        applied_policy = _as_dict(commander_route.get("applied_policy"))
        interpretation_policy = _as_dict(applied_policy.get("interpretation_policy"))
        entry_style = _playbook_label(interpretation_policy.get("entry_style"))
        notes = [_clip(x, 120) for x in _listify(interpretation_policy.get("notes")) if _clip(x, 120)]
        required = [_policy_token_label(x) for x in _listify(interpretation_policy.get("required_checks")) if _clip(x, 80)]
        blockers = [_policy_token_label(x) for x in _listify(interpretation_policy.get("blockers")) if _clip(x, 80)]
        if entry_style != "-":
            lines.append(f"- 전략가는 최종적으로 {entry_style} 전략 프레임을 유지했습니다.")
        if any("monitor_guidance:defensive_exit" in note for note in notes):
            lines.append("- 청산 쪽에는 방어적 청산 안내를 유지했습니다.")
        if any("vwap_reclaim_required" in note for note in notes):
            lines.append("- 진입 해석에서는 VWAP 재회복 확인을 우선 조건으로 두었습니다.")
        if required:
            if len(required[:3]) == 1:
                lines.append(f"- 핵심 확인 조건은 {_noun_predicate_was(required[0])}.")
            else:
                lines.append(f"- 핵심 확인 조건은 {', '.join(required[:3])}였습니다.")
        if blockers:
            lines.append(f"- 경계 신호는 {', '.join(blockers[:2])}였습니다.")
        if not lines:
            lines.append("- 전략가 요약 직접 캡처가 충분하지 않아, 저장된 지휘관 정책과 실행 기록 기준으로만 정리했습니다.")
    linkage = _as_dict(context.get("news_symbol_linkage"))
    linkage_strength = _news_linkage_strength_label(linkage.get("linkage_strength"))
    selected_vs_runner = _as_dict(linkage.get("selected_vs_runner_up"))
    selected_symbol_raw = selected_vs_runner.get("selected_symbol") or linkage.get("selected_symbol") or report.get("symbol")
    selected_symbol = _metadata_value(selected_symbol_raw)
    market_titles = _sample_news_titles(context.get("market_news_titles"))
    candidate_titles = _sample_news_titles_for_symbol(
        selected_symbol_raw,
        context.get("symbol_news_titles"),
        context.get("symbol_headlines"),
        context.get("strategist_symbol_headlines"),
        context.get("candidate_news_titles"),
    )
    runner_up_symbol = _metadata_value(
        selected_vs_runner.get("runner_up_symbol") or linkage.get("runner_up_symbol")
    )
    selected_headline_count = _num_opt(selected_vs_runner.get("selected_headline_count"))
    runner_up_headline_count = _num_opt(selected_vs_runner.get("runner_up_headline_count"))
    if market_titles or candidate_titles:
        pieces: List[str] = []
        if market_titles:
            pieces.append(f"시장 뉴스 {len(market_titles)}건")
        if candidate_titles:
            pieces.append(f"후보 뉴스 {len(candidate_titles)}건")
        if pieces:
            lines.append(f"- 전략가는 {'과 '.join(pieces)}을 함께 확인했습니다.")
        if candidate_titles:
            lines.append(f"- 전략가가 후보군 판단에 참고한 뉴스는 {' / '.join(candidate_titles)}였습니다.")
        if not selected_symbol or not runner_up_symbol:
            lines.append("- 전략가는 뉴스 입력을 시장 톤 확인과 후보군 보조 비교에 사용했습니다.")
    if selected_symbol and runner_up_symbol and selected_headline_count is not None and runner_up_headline_count is not None:
        if int(selected_headline_count) == 0 and int(runner_up_headline_count) == 0:
            lines.append(
                f"- 뉴스 연결 강도는 {linkage_strength}였고, 선택 종목 {selected_symbol}과 차순위 {runner_up_symbol}에 직접 연결된 뉴스는 모두 없어 시장 톤 확인용으로만 활용했습니다."
            )
        else:
            lines.append(
                f"- 뉴스 연결 강도는 {linkage_strength}였고, 선택 종목 {selected_symbol}과 차순위 {runner_up_symbol}의 직접 연결 뉴스는 {int(selected_headline_count)}건 / {int(runner_up_headline_count)}건이었습니다."
            )
    return _dedupe(lines)


def build_strategist_output_surface(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> List[str]:
    _append_strategy_output_line = deps["append_strategy_output_line"]
    _as_dict = deps["as_dict"]
    _dedupe = deps["dedupe"]
    _entry_watch_execution_lines = deps["entry_watch_execution_lines"]
    _memory_layers_text = deps["memory_layers_text"]
    _rank_scope_text = deps["rank_scope_text"]
    _resolve_strategist_output_surface = deps["resolve_strategist_output_surface"]
    _strategy_output_layer_bits = deps["strategy_output_layer_bits"]
    _strategy_output_list_text = deps["strategy_output_list_text"]
    _strategy_output_text = deps["strategy_output_text"]
    output = _resolve_strategist_output_surface(report)
    if not output:
        return []

    lines: List[str] = []
    thesis = _as_dict(output.get("strategy_thesis"))
    strategy_detail = _as_dict(output.get("strategy_detail"))
    memory = _as_dict(output.get("memory_usage_trace"))
    news = _as_dict(output.get("news_usage_trace"))
    scanner = _as_dict(output.get("scanner_handoff"))
    monitor = _as_dict(output.get("monitor_handoff"))
    permission = _as_dict(output.get("trade_permission_frame"))
    boundary = _as_dict(output.get("responsibility_boundary"))

    if thesis:
        one_line = _strategy_output_text(thesis.get("one_line"), max_len=220)
        parts = []
        playbook = _strategy_output_text(thesis.get("selected_playbook"), max_len=60)
        risk_tone = _strategy_output_text(thesis.get("risk_tone"), max_len=60)
        market_view = _strategy_output_text(thesis.get("market_view"), max_len=120)
        if playbook:
            parts.append(f"playbook={playbook}")
        if risk_tone:
            parts.append(f"risk={risk_tone}")
        if market_view:
            parts.append(f"market={market_view}")
        detail = one_line or "; ".join(parts)
        if one_line and parts:
            detail = f"{one_line} ({'; '.join(parts)})"
        _append_strategy_output_line(lines, "전략가 출력", detail)

    if strategy_detail:
        detail_parts: List[str] = []
        pre_llm = _strategy_output_text(strategy_detail.get("pre_llm_playbook"), max_len=60)
        llm_requested = _strategy_output_text(strategy_detail.get("llm_requested_playbook"), max_len=60)
        final_playbook = _strategy_output_text(strategy_detail.get("final_playbook"), max_len=60)
        tactical = _strategy_output_text(strategy_detail.get("tactical_strategy"), max_len=80)
        if pre_llm or llm_requested or final_playbook:
            detail_parts.append(
                f"playbook 흐름={pre_llm or '-'} -> {llm_requested or '-'} -> {final_playbook or '-'}"
            )
        if tactical:
            detail_parts.append(f"전술={tactical}")
        watch = _as_dict(strategy_detail.get("candidate_watch_policy"))
        if watch:
            watch_scope = _rank_scope_text(watch)
            if watch_scope:
                detail_parts.append(f"후보 감시 제안={watch_scope}")
        scores = _as_dict(strategy_detail.get("strategy_scores"))
        if scores:
            ordered_scores = sorted(
                [(str(name), value) for name, value in scores.items() if str(name or "").strip()],
                key=lambda row: float(row[1]) if isinstance(row[1], (int, float)) else -1.0,
                reverse=True,
            )
            detail_parts.append(
                "전략 점수="
                + ", ".join(f"{_strategy_output_text(name, max_len=50)}={value}" for name, value in ordered_scores[:3])
            )
        _append_strategy_output_line(lines, "전략 디테일", "; ".join(part for part in detail_parts if part))

    execution_lines = _entry_watch_execution_lines(report)
    if execution_lines:
        _append_strategy_output_line(lines, "후보 감시 실행", " ".join(execution_lines[:3]))

    if memory:
        active_layers = _memory_layers_text(memory.get("active_layers"), humanize=False)
        priority = _memory_layers_text(memory.get("priority_order"), arrow=True, humanize=False)
        human_summary = _strategy_output_text(memory.get("human_summary"), max_len=220)
        memory_bits = f"활성 레이어: {active_layers}; 우선순위: {priority}"
        if human_summary:
            memory_bits += f"; {human_summary}"
        _append_strategy_output_line(lines, "메모리", memory_bits)
        layer_bits = _strategy_output_layer_bits(memory.get("layer_decisions"))
        if layer_bits:
            _append_strategy_output_line(lines, "메모리 레이어", layer_bits)

    if news:
        news_summary = (
            _strategy_output_text(news.get("human_summary"), max_len=220)
            or _strategy_output_text(news.get("market_effect"), max_len=180)
            or _strategy_output_text(news.get("scanner_guidance_effect"), max_len=180)
        )
        targets = _strategy_output_list_text(news.get("query_targets"), limit=5)
        confidence = _strategy_output_text(news.get("confidence"), max_len=40)
        news_bits = news_summary
        extras = []
        if targets:
            extras.append(f"대상={targets}")
        if confidence:
            extras.append(f"신뢰도={confidence}")
        if extras:
            news_bits = (news_bits + "; " if news_bits else "") + "; ".join(extras)
        _append_strategy_output_line(lines, "뉴스", news_bits)
        headline_text = _strategy_output_list_text(
            news.get("market_headlines_used") or news.get("candidate_headlines_used"),
            limit=2,
            sep=" / ",
        )
        if headline_text:
            _append_strategy_output_line(lines, "뉴스 입력", headline_text)

    if scanner:
        scanner_parts = []
        ranking = _strategy_output_text(scanner.get("ranking_guidance"), max_len=180)
        prefer = _strategy_output_list_text(scanner.get("prefer_candidate_traits"), limit=3)
        penalize = _strategy_output_list_text(scanner.get("penalize_traits"), limit=3)
        if ranking:
            scanner_parts.append(ranking)
        if prefer:
            scanner_parts.append(f"선호={prefer}")
        if penalize:
            scanner_parts.append(f"회피={penalize}")
        _append_strategy_output_line(lines, "스캐너 인계", "; ".join(scanner_parts))

    if monitor:
        monitor_parts = []
        policy_effect = _strategy_output_text(monitor.get("policy_effect_summary"), max_len=180)
        aggressiveness = _strategy_output_text(monitor.get("entry_aggressiveness"), max_len=60)
        confirmations = _strategy_output_list_text(monitor.get("entry_confirmation"), limit=3)
        hold_off = _strategy_output_list_text(monitor.get("hold_off_conditions"), limit=3)
        if policy_effect:
            monitor_parts.append(policy_effect)
        if aggressiveness:
            monitor_parts.append(f"진입 강도={aggressiveness}")
        if confirmations:
            monitor_parts.append(f"확인={confirmations}")
        if hold_off:
            monitor_parts.append(f"보류={hold_off}")
        _append_strategy_output_line(lines, "모니터 인계", "; ".join(monitor_parts))

    if permission:
        permission_parts = []
        level = _strategy_output_text(permission.get("permission_level"), max_len=60)
        reason = _strategy_output_text(permission.get("reason"), max_len=140)
        allowed = _strategy_output_list_text(permission.get("entry_allowed_if"), limit=2)
        blocked = _strategy_output_list_text(permission.get("entry_blocked_if"), limit=2)
        if level:
            permission_parts.append(f"권한={level}")
        if reason:
            permission_parts.append(reason)
        if allowed:
            permission_parts.append(f"허용={allowed}")
        if blocked:
            permission_parts.append(f"차단={blocked}")
        _append_strategy_output_line(lines, "권한 프레임", "; ".join(permission_parts))

    boundary_text = _strategy_output_list_text(
        scanner.get("not_responsible_for") or boundary.get("not_responsible_for"),
        limit=4,
    )
    if boundary_text:
        _append_strategy_output_line(
            lines,
            "역할 경계",
            f"전략가는 {boundary_text}을 직접 결정하지 않습니다. 최종 종목/순위 설명은 스캐너와 모니터 산출물을 기준으로 해석합니다.",
        )

    return _dedupe(lines)


