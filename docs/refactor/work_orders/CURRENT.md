# Agentra P1.5 — CURRENT (이번 턴)

| 담당 | 지금 턴에 할 일 |
|---|---|
| **A Claude** | **다음 A 소유 미완료 RF 개발 착수.** RF-029 기존 KEEP/FIX0 증거는 재실행하지 말고 지팀장 판정 대기. 물리 큐의 A 소유·비동결 RF를 확인해 번호와 대상 파일을 HANDOFF에 명시하고 실제 owner 코드 작업 진행. |
| **B Codex** | **[RF-070](../plan/queue/02_DEVELOPING/CODEX_B/RF-070.md) 개발 계속.** 안전한 잔여 owner의 소비자·IO·효과 경계에서 실제 수정 진행. 위험 launcher HOLD. 다음 작업은 [RF-066](../plan/queue/02_DEVELOPING/CODEX_B/RF-066.md). |
| **지팀장** | **[RF-029](../plan/queue/01_PENDING/CLAUDE_A/RF-029.md) 기존 증거 직접 인수 판정** 및 peer 이동/구체 FIX 결정. [RF-001](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-001.md) exact integration SHA 검증 배정·결과 판정, [RF-028](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-028.md) B 독립 peer 배정·결과 판정·큐 이동 관리. A의 다음 RF 번호 확정. |

**예약 운영:** 1시간 실행 한도에 도달하면 **하던 작업과 마지막 코드 SHA·미완료 지점 그대로 다음 회차에 이어서 수행**한다. 매회 처음부터 재검증하거나 모든 RF 완료를 요구하지 않는다. B의 RF-001 검증·RF-028 peer는 지팀장이 별도 게이트로 관리하며 B 개발을 불필요하게 중단시키지 않는다.

**정본:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) · [D03](D03_DEV_TEAM_RULES.md) · [A 역할](../../../CLAUDE.md) · [B 역할](../../../AGENTS.md) · [RF 큐 D05](D05_RF_PHYSICAL_QUEUE_20261026.md) · [시도 감사 D06](D06_RF_ATTEMPT_AND_AUDIT_20261026.md) · [STATUS](../plan/STATUS.md). 완료 이력은 CURRENT에 반복 기재하지 않는다.

**안전:** 소유권·main·실거래·안전 계약·동결 테스트/CI 오라클 무승인 변경 금지. 부분 PASS·BLOCKED·NOT_RUN은 DONE 아님. GitHub 쓰기 실패는 원인별 허용된 방법으로 재시도하고 실제 SHA 확인.
