"""Behavior-preserving R3 implementation bodies moved from the public facade.

Each function keeps its original body. Names it used as facade module globals are
read from the injected `facade` module at call entry (explicit names, no getattr
fallback), preserving monkeypatch semantics. Owner never imports the facade.
"""
from __future__ import annotations


def _build_final_conclusion_r3_impl(report, *, facade):
    _action_label = facade._action_label
    _as_dict = facade._as_dict
    _clip = facade._clip
    _dedupe = facade._dedupe
    _ensure_sentence = facade._ensure_sentence
    _fmt_price = facade._fmt_price
    _listify = facade._listify
    _metadata_value = facade._metadata_value
    _section_summary = facade._section_summary
    _translate_invalidation_item = facade._translate_invalidation_item
    _translate_watch_item = facade._translate_watch_item
    section = _as_dict(report.get("final_operator_conclusion"))
    shared = _as_dict(report.get("shared_facts"))
    reporter_eval = _as_dict(report.get("reporter_evaluation"))
    memory = _as_dict(report.get("memory_surface"))
    reporter_packet = _as_dict(memory.get("reporter_feedback_packet"))
    reporter_ready = reporter_eval.get("status") == "ok" or reporter_packet.get("available")
    status = _clip(report.get("status"), 20).lower()
    lines: List[str] = []
    summary = _section_summary(section)
    if summary:
        lines.append(summary)
    raw_summary = _clip(section.get("summary"), 240)
    if raw_summary and not summary and raw_summary not in lines:
        lines.append(raw_summary)
    if status == "closed":
        symbol = _metadata_value(shared.get("symbol") or report.get("symbol") or "해당 거래")
        buy_price = shared.get("broker_buy_price")
        sell_price = shared.get("broker_fill_price")
        if buy_price not in (None, "") and sell_price not in (None, ""):
            lines.append(
                f"현재 판단은 청산 완료입니다. {symbol} 거래는 매수 진입 후 매도 청산까지 기록됐고, "
                f"브로커 매수가/매도가는 {_fmt_price(buy_price)} / {_fmt_price(sell_price)}였습니다."
            )
        else:
            lines.append(f"현재 판단은 청산 완료입니다. {symbol} 거래는 매수 진입 후 매도 청산까지 기록됐습니다.")
        lines.append("- 현재 판단 액션은 매도입니다.")
    else:
        summary = _section_summary(section)
        if summary:
            lines.append(summary)
        lines.append(f"- 현재 판단 액션은 {_action_label(section.get('current_action') or report.get('action'))}입니다.")
    for item in _listify(section.get("watch_next")):
        translated = _translate_watch_item(_clip(item, 200))
        if translated:
            if reporter_ready and "동일 일자 리포터 분석 연계" in translated:
                continue
            lines.append(f"- 다음 확인 항목은 {_ensure_sentence(translated)}")
    for item in _listify(section.get("thesis_invalidation")):
        translated = _translate_invalidation_item(_clip(item, 200))
        if translated:
            lines.append(f"- 기존 판단이 무효화되는 조건은 {_ensure_sentence(translated)}")
    return _dedupe(lines)
