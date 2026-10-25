# Agentra P1.5 — CURRENT 작업 큐

> 정본: `integration/p1.5`. [D00 안전·권한](../../ENGINEERING_DELIVERY_POLICY.md) · [D03 실행·검증](D03_DEV_TEAM_RULES.md) · [D01 B](../../../AGENTS.md) · [D02 A](../../../CLAUDE.md) · [STATUS](../plan/STATUS.md)

| 담당 | 지금 실행할 작업 | 다음 작업·해제 조건 |
|---|---|---|
| Claude A ([HANDOFF_A](HANDOFF_A.md)) | [RF-019](../plan/pending/RF-019.md) 잔여 소비자/State/효과 검토 및 B 신규 코드 SHA 독립 peer | [RF-017](../plan/pending/RF-017.md); B [RF-001](../plan/rework/codex/RF-001.md) 수정 SHA 도착 시 우선 peer |
| Codex B ([HANDOFF_B](HANDOFF_B.md)) | [RF-001](../plan/rework/codex/RF-001.md) FIX/KEEP 실제 코드 조치 | 차단 시 근거·해제 조건을 RF에 기록 후 [RF-070](../plan/pending/RF-070.md) 승인된 read-only 범위; A [RF-019](../plan/pending/RF-019.md) 신규 증거 peer |
| 지팀장 | 신규 SHA·peer 판정, [RF-001](../plan/rework/codex/RF-001.md) 물리 큐 중복 해결, [RF-013](../plan/verification/claude/RF-013.md) 소유권·HOLD 판정 | 인수조건 충족 RF 선별 통합 및 통합 SHA normal/-O 검증 |

**기록 위치:** RF = 개별 결정·실패·검증·차단·재개 조건. HANDOFF_A/B = 이번 실행의 신규 코드 SHA·명령·결과. STATUS = RF 집계. CURRENT = 담당·우선순위·링크만. 기존 증거는 재사용한다.

**런검증:** [별도 CURRENT](../../runtime/validation/CURRENT.md) · [D04](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md) · [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32). 코드 수정·RF 판정·통합 권한 없음.
