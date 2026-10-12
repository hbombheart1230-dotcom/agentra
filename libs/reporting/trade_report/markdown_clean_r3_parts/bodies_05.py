"""Behavior-preserving R3 implementation bodies moved from the public facade.

Each function keeps its original body except that every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module, no getattr fallback,
no entry-time capture), so late/use-time lookup and monkeypatching match the original
module-level resolution. Owner never imports the facade.
"""
from __future__ import annotations


def _build_final_conclusion_r3_impl(report, *, facade):
    section = facade._as_dict(report.get("final_operator_conclusion"))
    shared = facade._as_dict(report.get("shared_facts"))
    reporter_eval = facade._as_dict(report.get("reporter_evaluation"))
    memory = facade._as_dict(report.get("memory_surface"))
    reporter_packet = facade._as_dict(memory.get("reporter_feedback_packet"))
    reporter_ready = reporter_eval.get("status") == "ok" or reporter_packet.get("available")
    status = facade._clip(report.get("status"), 20).lower()
    lines: List[str] = []
    summary = facade._section_summary(section)
    if summary:
        lines.append(summary)
    raw_summary = facade._clip(section.get("summary"), 240)
    if raw_summary and not summary and raw_summary not in lines:
        lines.append(raw_summary)
    if status == "closed":
        symbol = facade._metadata_value(shared.get("symbol") or report.get("symbol") or "해당 거래")
        buy_price = shared.get("broker_buy_price")
        sell_price = shared.get("broker_fill_price")
        if buy_price not in (None, "") and sell_price not in (None, ""):
            lines.append(
                f"현재 판단은 청산 완료입니다. {symbol} 거래는 매수 진입 후 매도 청산까지 기록됐고, "
                f"브로커 매수가/매도가는 {facade._fmt_price(buy_price)} / {facade._fmt_price(sell_price)}였습니다."
            )
        else:
            lines.append(f"현재 판단은 청산 완료입니다. {symbol} 거래는 매수 진입 후 매도 청산까지 기록됐습니다.")
        lines.append("- 현재 판단 액션은 매도입니다.")
    else:
        summary = facade._section_summary(section)
        if summary:
            lines.append(summary)
        lines.append(f"- 현재 판단 액션은 {facade._action_label(section.get('current_action') or report.get('action'))}입니다.")
    for item in facade._listify(section.get("watch_next")):
        translated = facade._translate_watch_item(facade._clip(item, 200))
        if translated:
            if reporter_ready and "동일 일자 리포터 분석 연계" in translated:
                continue
            lines.append(f"- 다음 확인 항목은 {facade._ensure_sentence(translated)}")
    for item in facade._listify(section.get("thesis_invalidation")):
        translated = facade._translate_invalidation_item(facade._clip(item, 200))
        if translated:
            lines.append(f"- 기존 판단이 무효화되는 조건은 {facade._ensure_sentence(translated)}")
    return facade._dedupe(lines)
