# Agentra P1.5 — CURRENT

**정본 바로가기:** [D00 공통 규칙](../../ENGINEERING_DELIVERY_POLICY.md) · [D01 Codex B](../../../AGENTS.md) · [D02 Claude A](../../../CLAUDE.md) · [D03 개발팀 규칙](D03_DEV_TEAM_RULES.md) · [D04 런검증 규칙](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md)

**매 실행 읽기:** A=CURRENT+D02, B=CURRENT+D01. A/B는 D00·D03 최초/변경 시만 전문 재독. 지팀장은 매번 CURRENT+D00+D03+D01+D02 전문 재독.

| 담당 | 이번 실행: 자기 개발 우선 | 상대 검증 조건 |
|---|---|---|
| **A Claude** | **RF-001 새 integration+2 owner hunk 조합 독립 peer 우선**(`cdc3599f` / B `b994a133` 두 파일; 기존 18-case 반복 금지) → RF-013 실제 미충족 코드 과제 → RF-019 → RF-017 → RF-018 | 동일 B 코드 SHA라도 **기존 peer에서 미검증한 격리 조합**만 최초 read-only normal/-O 확인; 이후 새 코드 SHA 없으면 재검증 금지 |
| **B Codex** | **RF-001 734×2 격리 PASS 제출 완료**(동일 SHA 반복 금지). 즉시 **RF-070 잔여 25개 안전한 owner 범위 실제 FIX/KEEP 개발** → **RF-066 안전 CLI 제외 owner 구현·offline/mock 증거**. 단일 PASS 후 종료 금지; 각 RF 신규 source SHA 또는 구체 BLOCKED와 다음 owner 작업 제출 | A가 기존 peer 이후 새 RF-013 코드 SHA를 제출한 경우만 read-only peer |
| **지팀장** | A/B 신규 결과 회수 → FIX/KEEP 판정 → 선별 통합 → 통합 SHA normal/-O → RF DONE 여부 | 동일 SHA 증거 재사용; 미완료 결과를 반복 검증으로 전가 금지 |

**이번 배정:** A RF-001은 기존 18-case 재검증이 아닌 **새 integration 조합 최초 독립 peer**에 한정. B RF-070/066은 734 PASS를 이유로 중단 불가; 금지 launcher 32개는 실행 금지, 25개 안전 범위만 실제 구현·위험 분류. **규칙:** 새 코드 SHA 없으면 기존 peer 반복 금지·자기 RF 계속 개발. 이전 검증 18-case(RF-001), 134/134(RF-013) 재실행 금지. 오라클·안전·main 무승인 변경 금지. 미충족 인수조건은 각 RF에만 기록. [RF-001](../plan/verification/codex/RF-001.md) · [RF-013](../plan/verification/claude/RF-013.md) · [STATUS](../plan/STATUS.md) · [HANDOFF_A](HANDOFF_A.md) · [HANDOFF_B](HANDOFF_B.md).

**런검증팀:** [별도 CURRENT](../../runtime/validation/CURRENT.md) → [D00](../../ENGINEERING_DELIVERY_POLICY.md) → [D04](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md).
