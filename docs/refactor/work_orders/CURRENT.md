# Agentra P1.5 — CURRENT

**매 실행 읽기:** A=CURRENT+D02, B=CURRENT+D01. A/B는 D00·D03 최초/변경 시만 전문 재독. 지팀장은 매번 CURRENT+D00+D03+D01+D02 전문 재독.

| 담당 | 이번 실행: 자기 개발 우선 | 상대 검증 조건 |
|---|---|---|
| **A Claude** | RF-013 실제 미충족 코드 과제 → RF-019 → RF-017 → RF-018 | B가 **기존 peer 이후 새 RF-001 코드 SHA**를 제출한 경우만 다음 실행에 검증 |
| **B Codex** | RF-001 격리 후보 `cdc3599f` 테스트·실제 FIX 필요시 수정 → RF-070 → RF-066 | A가 **기존 peer 이후 새 RF-013 코드 SHA**를 제출한 경우만 다음 실행에 검증 |
| **지팀장** | A/B 신규 결과 회수 → FIX/KEEP 판정 → 선별 통합 → 통합 SHA normal/-O → RF DONE 여부 | 동일 SHA 증거 재사용; 미완료 결과를 반복 검증으로 전가 금지 |

**규칙:** 새 코드 SHA 없으면 peer 작업 금지·자기 RF 계속 개발. 이전 검증 18-case(RF-001), 134/134(RF-013) 재실행 금지. 오라클·안전·main 무승인 변경 금지. 미충족 인수조건은 각 RF에만 기록. [RF-001](../plan/verification/codex/RF-001.md) · [RF-013](../plan/verification/claude/RF-013.md) · [STATUS](../plan/STATUS.md) · [HANDOFF_A](HANDOFF_A.md) · [HANDOFF_B](HANDOFF_B.md).

**런검증팀:** [별도 CURRENT](../../runtime/validation/CURRENT.md) → D00 → D04.
