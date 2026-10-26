# Agentra P1.5 — CURRENT (지팀장 실행 지시판)

**정본 파일 위치:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) · [D03](D03_DEV_TEAM_RULES.md) · [D05](D05_RF_PHYSICAL_QUEUE_20261026.md) · [D06](D06_RF_ATTEMPT_AND_AUDIT_20261026.md). D00은 내용 변경 없이 이동.

**D05/D06 물리 큐 전환 (ACTIVE):** [D05 물리 큐](D05_RF_PHYSICAL_QUEUE_20261026.md) · [D06 시도/핑퐁 감사](D06_RF_ATTEMPT_AND_AUDIT_20261026.md). 폴더 표기는 `CLAUDE_A` / `CODEX_B`. 93 RF는 `plan/queue/`에 단일 물리 경로로 이관. `plan/queue/`가 유일한 활성 RF 큐이며 과거 경로는 사용하지 않는다. A/B 예약 변경 없음. 새 문서 작성은 RF 코드 진척이나 DONE이 아니다.

**정본:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) · [D01 B](../../../AGENTS.md) · [D02 A](../../../CLAUDE.md) · [D03](D03_DEV_TEAM_RULES.md) · [STATUS](../plan/STATUS.md) · [FILE_COVERAGE](../plan/FILE_COVERAGE_63182ab2.csv). **원칙:** 자기 owner 개발 → 신규 SHA만 상대 peer → 지팀장 선별 통합·exact SHA 검증·DONE. HANDOFF/ACK만으로 회차 종료 금지. 위험 명령만 HOLD, 안전한 다음 RF 계속. main·실거래·안전 계약·오라클·예약 무승인 변경 금지.

**POLICY_REREAD_REQUIRED (A/B):** 원격 D03 [현재 `d281c4dd`](D03_DEV_TEAM_RULES.md) (A 최종 수신 `4fe849a8` / run 98, B 최종 `471d7ab3` / run `B-20261026T0410Z`; 신규 `d281c4dd` 양쪽 미수신), 역할 정본 [D01 `b1865860`](../../../AGENTS.md) / [D02 `82396714`](../../../CLAUDE.md)도 이전 HANDOFF 이후 변경. A/B는 다음 실행 CURRENT·자기 역할 정본 전문 및 변경 D03 전문을 재독하고 시작/종료 SHA·실제 적용을 HANDOFF에 증명. A의 `4fe849a8` 수신은 직전 유효 증거이나 신규 `d281c4dd` 및 D05 `0b877de8` 수신·적용 완료는 아님. B `B-20261026T0410Z` RF-066 scoped 실행 수용, 정책·후속 착수는 `CONTINUATION_UNVERIFIED`. 수신·적용 확인 후 지팀장이 임시 항목 삭제.

## A Claude — 지금 할 일
**[RF-029](../plan/queue/01_PENDING/CLAUDE_A/RF-029.md)**: trade_story 및 trade_read_model_parts 38 owner. 미충족 소비자·IO/State 계약만 확인하고 결함이 있으면 최소 FIX·신규 소스 SHA 제출. 결함이 없으면 KEEP 인수 판정 요청 후 다음 A owner RF로 진행. 기존 검증 반복 금지.

## B Codex — 지금 할 일
1. **[RF-001](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-001.md)**: 최신 integration HEAD에서 지정된 3개 테스트 normal/-O 최초 실행, 실제 SHA·exit 제출. 과거 격리 PASS 반복 금지.
2. **[RF-028](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-028.md)**: 최초 독립 peer. 신규 동적 소비자·IO/State 위험 경계만 판정.
3. **[RF-070](../plan/queue/02_DEVELOPING/CODEX_B/RF-070.md) → [RF-066](../plan/queue/02_DEVELOPING/CODEX_B/RF-066.md)**: 안전한 owner의 실제 최소 FIX·신규 소스 SHA 우선. 위험 launcher·실제 주문 HOLD.

## 지팀장 — 즉시 처리
- RF-001 exact integration SHA 검증 수신 → 33 owner 인수 판정 → 충족 시 DONE 물리 이동.
- RF-028 B peer 수신 → LEAD_ACCEPTANCE 이동 및 KEEP 인수 판정.
- RF-029 기존 KEEP 증거 직접 판정 → peer 이동 또는 특정 FIX 배정.
- RF 큐·STATUS 일치 확인. 같은 SHA 테스트 반복 금지. GitHub 쓰기 실패 시 허용된 방식으로 재시도하고 원격 SHA 확인.
