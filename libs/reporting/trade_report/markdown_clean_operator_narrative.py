"""Markdown-clean operator narrative: sentence/translation helpers and entry/guard/timeline section bullets (pure text composition).

Bodies moved from the Markdown-clean public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _translate_watch_item_r3_impl(text, *, facade):
    raw = facade._clip(text, 200)
    mapping = {
        "Lifecycle status: closed": "라이프사이클 상태 종결",
        "Monitor trigger changes": "모니터 트리거 변화",
        "Macro/news shifts": "거시 환경 및 뉴스 변화",
        "VWAP retest": "VWAP 재확인",
    }
    return mapping.get(raw, facade._translate_text(raw))


def _translate_reason_phrase_r3_impl(text, *, facade):
    raw = facade._clip(text, 200).strip().strip(".")
    mapping = {
        "breakout above recent high with vwap structure confirmation": "직전 고점 돌파와 VWAP 구조 확인",
        "breakout above recent high with vwap hold and volume confirmation": "VWAP 유지와 거래량 확인이 있는 최근 고점 돌파",
        "pullback structure above vwap with volume confirmation": "VWAP 위 눌림목 구조와 거래량 확인",
        "pullback rebound above vwap with volume confirmation": "VWAP 위 되돌림 반등과 거래량 확인",
    }
    return mapping.get(raw.lower(), facade._translate_text(raw))


def _translate_invalidation_item_r3_impl(text, *, facade):
    raw = facade._clip(text, 200)
    mapping = {
        "stop-loss breach": "손절 기준 이탈",
        "monitor and scanner divergence": "모니터와 스캐너 판단 발산",
        "negative macro regime shift": "거시 환경의 부정적 전환",
        "prior low break": "직전 저점 이탈",
    }
    return mapping.get(raw, facade._translate_text(raw))


def _humanize_reporter_recommendation_r3_impl(text, *, facade):
    raw = facade._clip(text, 240)
    if raw == "Same-day closed trades are loss-heavy; keep defensive entry posture until follow-through quality improves.":
        return "당일 닫힌 거래가 손실 쪽으로 기울어 있어, 추세 연속성 품질이 회복되기 전까지는 진입을 더 방어적으로 유지해야 합니다."
    if raw == "Cached strategist reuse is elevated; compare refresh cadence against fresh full-cycle opportunities.":
        return "기존 전략가 재사용 비중이 높아, 새 전체 재평가 경로를 얼마나 자주 허용할지 다시 점검해야 합니다."
    if raw == "Top blocker is confidence_ok; inspect whether this gate is dominating no-trade outcomes.":
        return "no-trade를 가장 많이 막은 축이 진입 게이트였으니, 이 gate가 과도하게 지배적인지 다시 점검해야 합니다."
    if raw == "Monitor-only share is high; review hold-management concentration before widening entry tuning.":
        return "모니터 단독 경로 비중이 높으니, 진입 조건을 넓히기 전에 보유 관리가 한쪽에 과도하게 쏠리지 않았는지 먼저 점검해야 합니다."
    return facade._translate_text(raw)


def _bullet_lines_r3_impl(section, *, skip_prefixes, facade):
    lines: List[str] = []
    for raw in facade._listify(section.get("bullets")):
        text = facade._translate_text(raw)
        if not text:
            continue
        if facade._looks_corrupted(text):
            continue
        lowered = text.lower()
        if any(lowered.startswith(prefix.lower()) for prefix in skip_prefixes):
            continue
        lines.append(f"- {text}")
    return lines


def _section_summary_r3_impl(section, *, facade):
    summary = facade._translate_text(section.get("summary"))
    if facade._looks_corrupted(summary):
        return ""
    return summary


def _build_entry_decision_r3_impl(report, *, facade):
    section = facade._as_dict(report.get("entry_decision"))
    lines: List[str] = []
    summary = facade._section_summary(section)
    if summary and not facade._looks_corrupted(summary):
        lines.append(summary)
    for bullet in facade._bullet_lines(section):
        lines.append(bullet)
    return facade._dedupe(lines)


def _build_guard_approval_r3_impl(report, *, facade):
    section = facade._as_dict(report.get("guard_approval_result"))
    lines: List[str] = []
    raw_summary = facade._clip(section.get("summary"), 120).strip().lower()
    summary = facade._section_summary(section)
    if summary and raw_summary not in {"guard", "approval", ""} and not facade._looks_corrupted(summary):
        lines.append(summary)
    repeated = {
        "- 가드 승인 결과를 정리했습니다.",
        "- 슈퍼바이저는 주문을 승인했습니다.",
        "- 가드 판단은 허용이었습니다.",
    }
    for bullet in facade._bullet_lines(section):
        if summary and bullet in repeated:
            continue
        lines.append(bullet)
    if not lines:
        lines.append("- 가드 승인 결과는 별도 예외 없이 통과했습니다.")
    return facade._dedupe(lines)


def _build_timeline_r3_impl(report, *, facade):
    lines: List[str] = []
    for row in facade._listify(report.get("full_timeline")):
        item = facade._as_dict(row)
        event = facade._clip(item.get("event"), 40).lower()
        desc = facade._clip(item.get("description"), 240)
        if not desc:
            continue
        if m := facade.re.fullmatch(r"Entry BUY was executed by run (.+)\.", desc):
            lines.append(f"- 진입: run {m.group(1)}에서 매수 진입이 실행됐습니다.")
        elif m := facade.re.fullmatch(r"Exit SELL was executed by run (.+)\.", desc):
            lines.append(f"- 청산: run {m.group(1)}에서 매도 청산이 실행됐습니다.")
        elif event == "entry":
            lines.append(f"- 진입: {facade._translate_text(desc)}")
        elif event == "exit":
            lines.append(f"- 청산: {facade._translate_text(desc)}")
        else:
            lines.append(f"- {facade._translate_text(desc)}")
    return lines


def _extract_metadata_from_texts_r3_impl(texts, *, facade):
    lines: List[str] = []
    for text in texts:
        raw = facade._clip(text, 240)
        if not raw:
            continue
        source_match = facade.re.search(r"source=([A-Za-z0-9_.:/-]+)", raw)
        status_match = facade.re.search(r"status=([A-Za-z0-9_.:/-]+)", raw)
        if source_match:
            lines.append(f"- 데이터 출처: {source_match.group(1)}")
        if status_match:
            lines.append(f"- 상태: {facade._metadata_value(status_match.group(1))}")
    return lines


def _monitor_delta_interpretation_r3_impl(rows, *, facade):
    notes: List[str] = []
    for raw in rows:
        row = facade._as_dict(raw)
        field = facade._clip(row.get("field"), 80)
        delta = facade._num_opt(row.get("delta"))
        if field == "breakout_buffer_pct" and delta is not None and delta > 0:
            notes.append("돌파 확인 버퍼를 키워 추격 진입을 더 보수적으로 막았습니다.")
        elif field == "max_extended_from_vwap_pct" and delta is not None and delta < 0:
            notes.append("VWAP 기준 과확장 추격 허용 범위를 줄여 현재 가격 부담이 큰 진입을 줄였습니다.")
        elif field == "volume_ratio_min" and delta is not None and delta > 0:
            notes.append("거래량 확인 기준을 높여 힘이 약한 종목 진입을 더 엄격하게 걸렀습니다.")
    return " ".join(notes[:3])


def _entry_reason_line_r3_impl(values, *, facade):
    needles = ("진입 사유", "직전 고점", "vwap", "리바운드", "돌파", "rebound", "breakout")
    for raw in values:
        text = facade._translate_text(raw).strip()
        if not text or facade._is_post_entry_gate_text(text) or facade._is_entry_gate_status_text(text):
            continue
        lowered = text.lower()
        if any(needle in lowered for needle in needles):
            return text.rstrip(".")
    return ""


def _entry_confidence_line_r3_impl(values, *, facade):
    for raw in values:
        text = facade._translate_text(raw).strip()
        if not text or facade._is_post_entry_gate_text(text):
            continue
        lowered = text.lower()
        if "신뢰도" in text or "confidence" in lowered:
            return text.rstrip(".")
    return ""


def _normalize_entry_confidence_for_operator_summary_r3_impl(value, *, action, buy_price, facade):
    text = str(value or "").strip()
    if (
        text
        and "미통과" in text
        and "진입 게이트" in text
        and str(action or "").strip() == "매도"
        and buy_price not in (None, "")
    ):
        return "진입 게이트 상세는 실제 BUY 체결 이후 사후 모니터 재평가와 혼재될 수 있어 확정 표시하지 않습니다"
    return text


def _correct_final_operator_summary_r3_impl(summary, *, action, facade):
    text = str(summary or "").strip()
    action_label = str(action or "").strip()
    if not text:
        return ""
    if action_label == "매도":
        return facade.re.sub(r"현재 판단은 진입 유지(?:입니다|이다)\.?", "현재 판단은 청산 완료입니다.", text, count=1)
    if action_label == "매수":
        return facade.re.sub(r"현재 판단은 청산 완료(?:입니다|이다)\.?", "현재 판단은 진입 유지입니다.", text, count=1)
    return text


def _reason_summary_line_r3_impl(tags, prefix, *, facade):
    phrases: List[str] = []
    seen = set()
    for raw in tags:
        text = facade._reason_tag_summary(str(raw))
        if text and text not in seen:
            seen.add(text)
            phrases.append(text)
    if not phrases:
        return None
    return f"- {prefix} {', '.join(phrases[:4])}."


def _ensure_sentence_r3_impl(text, *, facade):
    raw = facade._clip(text, 240).strip()
    if not raw:
        return ""
    if raw.endswith(("?", "!", "요.", "입니다.", "였습니다.", "합니다.", "됩니다.", "다.", ".")):
        return raw
    return raw + "입니다."


def _noun_predicate_was_r3_impl(text, *, facade):
    raw = facade._clip(text, 240).strip()
    if not raw:
        return "-"
    last = raw[-1]
    if "가" <= last <= "힣":
        base = ord(last) - ord("가")
        has_batchim = (base % 28) != 0
        return raw + ("이었습니다" if has_batchim else "였습니다")
    return raw + "이었습니다"


def _first_nonempty_r3_impl(values, *, facade):
    for value in values:
        if facade._clip(value, 240):
            return value
    return ""


def _market_context_summary_from_raw_r3_impl(summary, *, facade):
    raw = facade._clip(summary, 400)
    if not raw:
        return ""
    lowered = raw.lower()
    if "regime" not in lowered and "market sentiment" not in lowered and "playbook" not in lowered:
        return ""
    regime_match = facade.re.search(r"([A-Za-z_-]+)\s+Regime", raw, facade.re.I)
    sentiment_match = facade.re.search(r"([A-Za-z_-]+)\s+Market Sentiment", raw, facade.re.I)
    playbook_match = facade.re.search(r"([A-Za-z_-]+)\s+playbook", raw, facade.re.I)
    regime = regime_match.group(1) if regime_match else "-"
    sentiment = sentiment_match.group(1) if sentiment_match else "-"
    playbook = playbook_match.group(1) if playbook_match else "-"
    return f"- 시장 상태는 {regime}, 시장 심리는 {sentiment}, 선택 플레이북은 {playbook}입니다."
