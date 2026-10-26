# Agentra PC 런검증팀 — CURRENT

**정본:** `hbombheart1230-dotcom/agentra` / `integration/p1.5`
**운영:** [R00](R00_RUNTIME_VALIDATION_RULES.md) · **증거:** [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32)
**작업 PC:** `C:\AgentraRunLab` — 기존 운영 PC·`C:\Agentco`·개발 브랜치는 변경하지 않는다.

## 실행 (평일 KST)
- **07:00 Codex:** RunLab 기동·RUN_ID·검증 대상 SHA 고정.
- **09:30 Claude:** 같은 RUN_ID·SHA의 장초반 독립 검증.
- **17:00 Codex:** 당일 주문·체결·취소·종료/복구 증거 수집.
- **19:00 Claude:** 최종 독립 검증 후 Issue #32에 신규 결과 게시.

## 현재 미해결 관측
- PC 로컬 예약 실제 활성화 미입증(`SCHEDULE_NOT_CONFIGURED`).
- 실행 중 이미지와 코드 SHA 연결 미입증.
- 2026-10-26 모의 BUY의 최종 체결/취소·TTL 정합성 미확인. 후속 EOD 증거로 사실 관계를 확정한다.
- 메트릭 생성 시점과 실제 주문 시점 차이는 결함 미확정.

**인계:** 안전 문제는 즉시 보고. 일반 결과는 19시 최종 검증에서 묶어 지팀장에게 전달한다. 코드 결함의 RF 편입·개발 배정은 지팀장이 결정한다. 기존 증거 중복 복사 금지.
