from __future__ import annotations

from typing import Optional


def resolve_exact_operator_phrase(lowered: str) -> Optional[str]:
    """Return only exact, previously supported operator-facing phrases."""
    exact_mapping = {
        "the decision path was recorded, but the operator-facing summary is limited.": "의사결정 경로는 기록되었지만 운영자용 요약은 제한적으로만 남아 있습니다.",
        "current lifecycle status is closed. entry and exit are connected in one lifecycle story.": "이번 라이프사이클은 종결 상태이며, 진입과 청산이 하나의 거래 흐름으로 연결됐습니다.",
        "current lifecycle status is open. entry and exit are still unfolding within one lifecycle story.": "이번 라이프사이클은 아직 진행 중이며, 진입 이후 청산 판단이 이어지고 있습니다.",
        "supervisor approved the order because allowed.": "슈퍼바이저는 주문을 승인했고 가드 판단은 허용이었습니다.",
        "execution quality details were not captured.": "실행 품질 세부 내용은 별도로 기록되지 않았습니다.",
        "reporter linkage was not available yet.": "리포터 연계 결과는 아직 연결되지 않았습니다.",
        "reporter linkage status was recorded separately.": "리포터 연계 상태는 별도로 기록되어 있습니다.",
        "warnings and missing links were recorded for operator follow-up.": "운영자가 후속 확인해야 할 경고와 누락 링크가 함께 기록되었습니다.",
        "no explicit weaknesses were surfaced beyond the recorded trace.": "기록된 추적 정보 외에 추가 약점은 별도로 확인되지 않았습니다.",
        "ai trade report generation failed after retry attempts. review the saved llm response artifact for details.": "AI 거래 리포트 생성이 재시도 이후에도 완료되지 않았습니다. 저장된 LLM 응답 아티팩트를 함께 확인해 주세요.",
        "ai generation failed before a rendered market-context section was produced.": "시장 환경 요약은 생성 도중 중단되어, 저장된 근거를 기준으로 보수적으로 정리했습니다.",
        "ai generation failed before a rendered symbol-selection section was produced.": "종목 선정 설명은 생성 도중 중단되어, 저장된 선정 근거를 기준으로 보수적으로 정리했습니다.",
        "ai generation failed before a rendered entry-decision section was produced.": "진입 판단 설명은 생성 도중 중단되어, 저장된 진입 근거를 기준으로 보수적으로 정리했습니다.",
        "ai generation failed before a rendered holding-monitoring section was produced.": "보유 관리 설명은 생성 도중 중단되어, 저장된 모니터 기록을 기준으로 보수적으로 정리했습니다.",
        "ai generation failed before a rendered exit-decision section was produced.": "청산 판단 설명은 생성 도중 중단되어, 저장된 청산 근거를 기준으로 보수적으로 정리했습니다.",
        "ai generation failed before a rendered execution-quality section was produced.": "실행 품질 설명은 생성 도중 중단되어, 저장된 실행 기록을 기준으로 보수적으로 정리했습니다.",
        "ai generation failed and no rendered improvement section is available.": "AI 생성이 중단되어 개선 포인트는 저장된 경고와 오류 기록 중심으로 정리했습니다.",
        "ai generation failed. review lifecycle artifacts and the saved llm response artifact before taking action.": "AI 생성이 중단되었습니다. 다음 조치를 하기 전에 lifecycle 아티팩트와 저장된 LLM 응답을 함께 확인해 주세요.",
        "link same-day reporter analysis to this lifecycle for a complete quality review.": "동일 일자 리포터 분석이 아직 이 거래 생애주기에 연결되지 않았습니다.",
        "same-price round trips produced fee/tax drag; tighten follow-through evidence before repeating quick reversals.": "동일가 왕복 거래에서 수수료와 세금 손실이 반복돼, 짧은 반전 시도 전에는 후속 추세 확인을 더 엄격하게 봐야 합니다.",
        "same-day closed trades are loss-heavy; keep defensive entry posture until follow-through quality improves.": "당일 닫힌 거래 손익이 전반적으로 약해, 후속 추세 확인 품질이 개선될 때까지는 방어적인 진입 자세를 유지해야 합니다.",
        "selection": "선정 근거를 정리했습니다.",
        "entry": "진입 판단을 정리했습니다.",
        "filters": "스캐너 필터 점검 결과를 정리했습니다.",
        "guard": "승인 및 가드 판단 결과를 정리했습니다.",
        "execution": "실행 결과를 정리했습니다.",
        "reporter": "리포터 평가를 정리했습니다.",
        "none": "추가 보완 포인트는 제한적입니다.",
        "top value or trading-value input supported the selection": "거래대금 상위 신호가 선정 근거를 뒷받침했습니다.",
        "top volume or turnover input supported the selection": "회전율 신호는 존재했지만 최종 우위 근거로는 약했습니다.",
        "theme boost or sector source matched the strategist frame": "테마 가점과 섹터 소스가 전략가 프레임과 맞아떨어졌습니다.",
        "12/13 captured chart features": "13개 중 12개 차트 피처가 확보됐습니다.",
        "news/global sentiment contribution was 0.295": "뉴스와 글로벌 감성 기여 합산값은 0.295였습니다.",
        "risk score was 0.563 and supervisor allow=true": "리스크 점수는 0.563이었고 supervisor 허용 상태도 유지됐습니다.",
        "price anomaly check was not captured in this run": "이번 run에서는 가격 이상치 점검 결과가 저장되지 않았습니다.",
        "price anomaly check was 기록되지 않음 in this run": "이번 run에서는 가격 이상치 점검 결과가 저장되지 않았습니다.",
        "monitor price cross-check found no anomaly": "모니터 가격 교차검증에서 이상치가 확인되지 않았습니다.",
        "monitor price cross-check flagged an anomaly": "모니터 가격 교차검증에서 이상치가 감지되었습니다.",
        "spread or slippage diagnostics were not captured in this run": "이번 run에서는 호가 스프레드 또는 슬리피지 진단이 저장되지 않았습니다.",
        "spread or slippage diagnostics were 기록되지 않음 in this run": "이번 run에서는 호가 스프레드 또는 슬리피지 진단이 저장되지 않았습니다.",
        "holding-phase evidence is thin; preserve more monitor context between entry and exit.": "보유 구간 근거는 제한적이며 진입과 청산 사이 모니터 맥락이 충분하지 않습니다.",
        "같은 날 생성된 reporter 분석을 이 lifecycle에 연결해 전체 품질 평가를 완성해 주세요.": "동일 일자 리포터 분석이 아직 이 거래 생애주기에 연결되지 않았습니다.",
        "보유 단계 근거가 얇아 진입과 청산 사이의 모니터 맥락을 더 보존해야 합니다.": "보유 구간 근거는 제한적이며 진입과 청산 사이 모니터 맥락이 충분하지 않습니다.",
        "monitor trigger changes": "모니터 트리거 변화",
        "macro/news shifts": "거시 환경 및 뉴스 변화",
        "stop-loss breach": "손절 기준 이탈",
        "monitor and scanner divergence": "모니터와 스캐너 판단 발산",
        "negative macro regime shift": "거시 환경의 부정적 전환",
        "guard reason: allowed": "가드 판단 사유는 허용입니다.",
        "supervisor verdict: approve": "슈퍼바이저 최종 판단은 승인입니다.",
        "broad_market_leaders": "브로드마켓 리더",
        "top_value": "거래대금 상위",
        "top_volume": "거래량 상위",
        "sector_theme": "섹터·테마 정렬",
    }
    if lowered in exact_mapping:
        return exact_mapping[lowered]
    
    return None
