from __future__ import annotations

from typing import Any, Mapping


def translate_text(text: Any, *, deps: Mapping[str, Any]) -> str:
    _action_label = deps["action_label"]
    _axis_label = deps["axis_label"]
    _clip = deps["clip"]
    _metadata_value = deps["metadata_value"]
    _translate_reason_phrase = deps["translate_reason_phrase"]
    raw = html.unescape(_clip(text, 800))
    if not raw:
        return ""
    exact = {
        "hold": "현재 포지션 판단은 보유 유지입니다.",
        "open trade": "아직 청산 체결이 확인되지 않아 포지션이 열려 있습니다.",
        "Current lifecycle status is closed. Entry and exit are connected in one lifecycle story.": "이번 라이프사이클은 종결 상태이며, 진입과 청산이 하나의 거래 흐름으로 연결됐습니다.",
        "Supervisor approved the order because Allowed.": "슈퍼바이저는 주문을 승인했고 가드 판단은 허용이었습니다.",
        "Approval mode: not captured in the execution trace": "승인 모드는 실행 추적에는 별도로 남아 있지 않습니다.",
        "Holding-phase evidence is thin; preserve more monitor context between entry and exit.": "보유 구간 근거는 제한적이며 진입과 청산 사이 모니터 맥락이 충분하지 않습니다.",
        "Execution outcome summary was not captured.": "거래 생애주기 실행 요약은 기록되지 않았습니다.",
        "Lifecycle conclusion was not captured.": "최종 생애주기 결론은 기록되지 않았습니다.",
        "Final decision basis: Scanner selected the highest-ranked candidate after strategist-guided weighting, source scoring, and risk penalties.": "최종 선정 기준은 전략가 가중치, source 점수, 위험 패널티를 반영한 뒤 스캐너 최고 순위 후보를 채택한 것입니다.",
        "Warnings and missing links were recorded for operator follow-up.": "운영자 후속 확인이 필요한 경고와 누락 연결을 정리했습니다.",
        "Link same-day reporter analysis to this lifecycle for a complete quality review.": "동일 일자 리포터 분석을 이 거래 생애주기에 연결해 결과 평가를 보강해야 합니다.",
        "Entry execution evidence is incomplete; preserve BUY linkage for closed-trade diagnosis.": "진입 실행 근거가 불완전해, 닫힌 거래 진단을 위해 BUY 연결 기록을 더 보존해야 합니다.",
        "Same-price round trips produced fee/tax drag; tighten follow-through evidence before repeating quick reversals.": "동일가 왕복 거래에서 수수료와 세금 손실이 발생했으므로, 빠른 재진입 전에는 후속 탄력 근거를 더 확인해야 합니다.",
    }
    if raw in exact:
        return exact[raw]
    replaced = raw
    replaced = replaced.replace("Market Sentiment", "시장 심리")
    replaced = replaced.replace("Stress Flags", "스트레스 신호")
    replaced = replaced.replace("Scanner Rank", "스캐너 순위")
    replaced = replaced.replace("Tie Break Rule", "동률 해소 기준")
    replaced = replaced.replace("Trailing stop", "추적 손절")
    replaced = replaced.replace("Hard stop", "고정 손절")
    replaced = replaced.replace("Adaptive stop", "상황 적응형 손절")
    replaced = replaced.replace("Take profit", "목표 수익 실현")
    replaced = replaced.replace("Partial take profit", "1차 일부 익절")
    replaced = replaced.replace("Profit ladder", "구간별 분할 익절")
    replaced = replaced.replace("Risk/reward take profit", "손익비 익절")
    replaced = replaced.replace("VWAP extension take profit", "VWAP 과확장 익절")
    replaced = replaced.replace("Resistance take profit", "저항권 익절")
    replaced = replaced.replace("Volume exhaustion take profit", "거래량 둔화 익절")
    replaced = replaced.replace("Opening gap profit take", "갭 추격 빠른 익절")
    replaced = replaced.replace("Time-decay profit exit", "시간 경과 수익 보전")
    replaced = replaced.replace("VWAP breakdown", "VWAP 이탈")
    replaced = replaced.replace("broad_market_leaders", "시장 대표주")
    replaced = replaced.replace("illiquid_microcap", "유동성 낮은 초소형주")
    replaced = replaced.replace("headline_only_momentum", "헤드라인 추격형 모멘텀")
    replaced = replaced.replace("high_gap_speculative", "갭 과열 투기형")
    replaced = replaced.replace("브로드마켓 리더", "시장 대표주")
    replaced = replaced.replace("밸런스드", "균형형")
    replaced = replaced.replace("turnover and volume", "회전율/거래량")
    replaced = replaced.replace("정서 지원", "감성 지원")
    replaced = replaced.replace("top_value", "거래대금 상위")
    replaced = replaced.replace("top_change_rate", "등락률 상위")
    replaced = replaced.replace(
        "pullback rebound above vwap with volume confirmation",
        "VWAP 위 되돌림 반등과 거래량 확인",
    )
    replaced = replaced.replace(
        "눌림목 rebound above vwap with volume confirmation",
        "VWAP 위 되돌림 반등과 거래량 확인",
    )
    replaced = replaced.replace(
        "pullback structure above vwap with volume confirmation",
        "VWAP 위 눌림목 구조와 거래량 확인",
    )
    replaced = replaced.replace(
        "눌림목 structure above vwap with volume confirmation",
        "VWAP 위 눌림목 구조와 거래량 확인",
    )
    replaced = replaced.replace(
        "breakout above recent high with vwap hold and volume confirmation",
        "VWAP 유지와 거래량 확인이 있는 최근 고점 돌파",
    )
    replaced = replaced.replace(
        "breakout above recent high with vwap structure confirmation",
        "직전 고점 돌파와 VWAP 구조 확인",
    )
    replaced = re.sub(r"스캐너 1순위\s+([A-Z0-9]+)은", r"스캐너 상위 후보 \1은", replaced)
    replaced = replaced.replace(" 이유로 막혔고", " 이유로 보류됐고")
    replaced = replaced.replace(" 사유로 막힌 뒤", " 사유로 보류된 뒤")
    replaced = replaced.replace("news/global sentiment contribution was", "뉴스/글로벌 심리 기여도")
    replaced = replaced.replace("Peak Drawdown", "고점 대비 하락폭 기준")
    replaced = replaced.replace("peak_drawdown", "고점 대비 하락폭 기준")
    replaced = replaced.replace("partial_take_profit", "1차 일부 익절")
    replaced = replaced.replace("profit_ladder", "구간별 분할 익절")
    replaced = replaced.replace("risk_reward_take_profit", "손익비 익절")
    replaced = replaced.replace("vwap_extension_take_profit", "VWAP 과확장 익절")
    replaced = replaced.replace("resistance_take_profit", "저항권 익절")
    replaced = replaced.replace("volume_exhaustion_take_profit", "거래량 둔화 익절")
    replaced = replaced.replace("opening_gap_profit_take", "갭 추격 빠른 익절")
    replaced = replaced.replace("time_decay_profit_exit", "시간 경과 수익 보전")
    replaced = replaced.replace("hard_stop", "고정 손절 기준")
    replaced = replaced.replace("intraday low break", "장중 저점 이탈 기준")
    replaced = replaced.replace("intraday_low_break", "장중 저점 이탈 기준")
    replaced = replaced.replace("below_vwap_reclaim_not_ready", "VWAP 재회복 미완료")
    replaced = replaced.replace("슈퍼바이저 결정: approve", "슈퍼바이저 결정은 승인입니다.")
    replaced = replaced.replace("슈퍼바이저 결정: approved", "슈퍼바이저 결정은 승인입니다.")
    replaced = replaced.replace("가드 판단 사유는 Allowed입니다", "가드 판단 사유는 허용입니다.")
    replaced = replaced.replace("가드 판단 사유는 allowed입니다", "가드 판단 사유는 허용입니다.")
    replaced = replaced.replace("액션 검토: SELL", "검토 액션은 매도입니다.")
    replaced = replaced.replace("액션 검토: BUY", "검토 액션은 매수입니다.")
    replaced = replaced.replace("확인였습니다", "확인이었습니다")
    replaced = replaced.replace("입니다..", "입니다.")
    replaced = replaced.replace(
        "진입 신뢰도 점수는 0.55로 기준 0.55를 하회했습니다.",
        "진입 게이트 점수는 기준 0.55와 같은 수준이었습니다.",
    )
    if m := re.fullmatch(
        r"News input:\s*(\d+)\s+headlines were considered across\s*(\d+)\s+targets\s*\((\d+)\s+market\s*/\s*(\d+)\s+candidate signals\)\.?",
        raw,
        re.I,
    ):
        return f"뉴스 입력은 {m.group(1)}건 헤드라인, 조회 대상 {m.group(2)}개 ({m.group(3)} 시장 / {m.group(4)} 후보 신호)를 반영했습니다."
    if m := re.fullmatch(r"소스 조합:\s*(.+)에서 선정됨", replaced):
        return f"선정 소스는 {m.group(1)}입니다."
    if m := re.fullmatch(r"Scanner Rank:\s*([0-9]+)\?*\s*/\s*Total Score:\s*([0-9.]+)", raw, re.I):
        return f"스캐너 순위는 {m.group(1)}위였고 총점은 {m.group(2)}였습니다."
    if m := re.fullmatch(r"Scanner Rank:\s*(.+)", raw, re.I):
        cleaned = m.group(1).replace("?", "").strip()
        return f"스캐너 순위: {cleaned}"
    if m := re.fullmatch(r"Tie Break Rule:\s*(.+)", raw, re.I):
        return f"동률 해소 기준: {m.group(1)}"
    if m := re.fullmatch(r"Universe scanned:\s*(\d+)", raw, re.I):
        return f"비교한 후보 수는 {m.group(1)}개였습니다."
    if m := re.fullmatch(r"Selected rank:\s*#?(\d+)", raw, re.I):
        return f"실제 선택 순위는 {m.group(1)}위였습니다."
    if m := re.fullmatch(
        r"Actual traded symbol\s+([A-Z0-9]+)\s+had scanner rank\s+#?(\d+);\s*score\s*([0-9.]+);\s*confidence\s*([0-9.]+);\s*risk\s*([0-9.]+)\.?",
        raw,
        re.I,
    ):
        score = m.group(3).rstrip(".")
        confidence = m.group(4).rstrip(".")
        risk = m.group(5).rstrip(".")
        return (
            f"실제 체결 종목 {m.group(1)}은 스캐너 {m.group(2)}위였고, "
            f"점수는 {score}, 신뢰도는 {confidence}, 위험 점수는 {risk} 수준으로 집계됐습니다."
        )
    if m := re.fullmatch(r"fallback observed in\s*(\d+)/(\d+)\s*route-tagged runs\.?", raw, re.I):
        return f"차순위 재평가 경로는 전체 {m.group(2)}회 중 {m.group(1)}회 관측됐습니다."
    if m := re.fullmatch(r"Fallback entry trigger:\s*(.+)", raw, re.I):
        return f"fallback 진입 트리거는 {_translate_reason_phrase(m.group(1))}였습니다."
    if m := re.fullmatch(r"Supervisor verdict:\s*(.+)", raw, re.I):
        verdict = m.group(1).strip().lower()
        return f"슈퍼바이저 최종 판단은 {'승인' if verdict == 'approve' else _metadata_value(m.group(1))}입니다."
    if m := re.fullmatch(r"Supervisor allow:\s*(.+)", raw, re.I):
        verdict = m.group(1).strip().lower()
        return f"주문 허용 여부는 {'허용' if verdict in {'yes', 'true', 'allowed'} else _metadata_value(m.group(1))}입니다."
    if m := re.fullmatch(r"Guard reason:\s*(.+)", raw, re.I):
        return f"가드 판단 사유는 {_metadata_value(m.group(1))}입니다."
    if m := re.fullmatch(r"Action reviewed:\s*(.+)", raw, re.I):
        return f"검토한 액션은 {_action_label(m.group(1))}입니다."
    if m := re.fullmatch(r"Symbol reviewed:\s*(.+)", raw, re.I):
        return f"검토한 종목은 {m.group(1).strip()}입니다."
    if m := re.fullmatch(
        r"Entry reason:\s*Scanner selected\s+([A-Z0-9]+)\s+as rank #(\d+)\s+out of\s+(\d+)\s+candidates with score\s+([0-9.]+)\s+because it led on\s+(.+?)\.?",
        raw,
        re.I,
    ):
        rationale = m.group(5)
        rationale = rationale.replace("trading value", "거래대금")
        rationale = rationale.replace("theme and sector alignment", "테마 및 섹터 정합성")
        rationale = rationale.replace("theme alignment", "테마 정합성")
        rationale = rationale.replace("sector alignment", "섹터 정합성")
        return (
            f"진입 이유는 {m.group(1)}이 {m.group(3)}개 후보 중 {m.group(2)}위, "
            f"점수 {m.group(4)}로 선정됐고 {rationale}에서 앞섰기 때문입니다."
        )
    if replaced.startswith("SELL was triggered because "):
        reason = replaced[len("SELL was triggered because ") :].strip().rstrip(".")
        return f"{_axis_label(reason)}으로 청산"
    return replaced


