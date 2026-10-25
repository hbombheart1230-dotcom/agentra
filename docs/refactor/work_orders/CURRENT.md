# Agentra P1.5 — CURRENT (작업 포인터)

> 정본: `integration/p1.5`. **안전·권한 [D00](../../ENGINEERING_DELIVERY_POLICY.md) → 공통 [D03](D03_DEV_TEAM_RULES.md) → 역할 [D01 Codex](../../../AGENTS.md) / [D02 Claude](../../../CLAUDE.md)**. 실행 가능한 REWORK 조치 → 상대 신규 SHA 독립 검증 → 다음 실행 가능한 RF. RF별 상세 판정은 RF 정본, 집계는 [STATUS](../plan/STATUS.md), 런검증은 별도 D04.

## 현재 공통 차단
- RF-001: B 후보 frozen 28 FAIL. B 수정/KEEP 코드 SHA 필요. rework/codex 정본과 verification/codex 잔존 사본의 물리 중복은 안전한 삭제가 가능할 때 정리하며, 그 전까지 큐 이동 미완료.
- RF-013: 신규 read_models 9경로·RF-030/035 소비자 4경로 및 미승인 오라클 후보는 소유권 판정 전 쓰기·통합 HOLD. 기존 scoped PASS는 재사용.
- 지팀장은 새 증거를 우선 판정하고, 반복 차단은 해결 방법 또는 재개 조건을 확정한다. RF 상세는 각 RF, 집계는 STATUS, 런검증은 별도 CURRENT/D04.

## Claude A — `work/p15-a-reporter-pure-20261021` · [HANDOFF](HANDOFF_A.md)
1. **REWORK:** 현재 배정 없음. 새 지팀장 판정이 나오면 D03에 따라 우선 실행.
2. **독립 검증:** [001](../plan/rework/codex/RF-001.md) 16 alias·90 parity 신규 scoped PASS 수용, B 후보 frozen 734 중 28 FAIL로 원자적 admission HOLD; 동일 테스트 반복 금지, B 수정 SHA가 나올 때만 신규 peer. [069](../plan/verification/codex/RF-069.md) 2 CLI peer 완료(재검증 금지), UEF5 승인 snapshot 신규 증거가 생길 때만 peer. 추가 [070](../plan/pending/RF-070.md) 85/142 wrapper read-only peer 완료(기존 85 재실행 금지); **잔여 57은 실행/peer HOLD**, B의 정적 위험 분류만 확인. 안전/실행 진입점은 격리·NOT_RUN. 이후 [067](../plan/verification/codex/RF-067.md) → [066](../plan/verification/codex/RF-066.md) → [063](../plan/verification/codex/RF-063.md) → [065](../plan/verification/codex/RF-065.md) → [007](../plan/verification/codex/RF-007.md) → [008](../plan/verification/codex/RF-008.md).
3. **신규 개발:** [019](../plan/pending/RF-019.md) 기존 29 owner KEEP·8파일 normal/-O 각 101 PASS 인정; 나머지 21 owner 소비자/State/효과·p171 CROSS_RF_OWNER 실패 node를 분리 제출(101 재실행 금지) → [017](../plan/pending/RF-017.md).

## Codex B — `work/p15-b-operator-structure-20261022` · [HANDOFF](HANDOFF_B.md)
1. **REWORK 실제 조치 1순위: [RF-001](../plan/rework/codex/RF-001.md)** — B 후보 frozen 28 FAIL(integration 734 PASS vs B 706 PASS/28 FAIL normal/-O), 16 alias + core 기존 owner 17경로에서 최소 수정 또는 KEEP 복귀. 신규 타 RF·동결 테스트/오라클 수정 금지. 다음 HANDOFF_B에 실제 수정 CODE_SHA·FIX/KEEP 검증 또는 재현 가능한 BLOCKED 근거와 28 FAIL 변화를 기록. 신규 SHA는 A 독립 peer 후 지팀장 판정. **RF-070 신규 작업보다 먼저 실행**.
2. **독립 검증:** [013](../plan/verification/claude/RF-013.md) 기존 67 owner 105+105 scoped PASS 재사용; 신규 9+4+수정 오라클 후보 REJECT(재실행 금지). RF-030/035 기존 4 wrapper는 read-only 소비자·효과 비교만, 코드 쓰기 금지. RF-001 REWORK 조치 후 [019](../plan/pending/RF-019.md) A 29 owner KEEP·8파일 normal/-O 각 101 PASS의 **신규 위험 경계만** read-only peer. [018](../plan/verification/claude/RF-018.md) 역사 2 FAIL normal/-O BASE 동일로 `HISTORICAL_INVENTORY` 분리(동일 테스트 재실행 금지), 신규 Strategist 소비자/side-effect 증거 시에만 peer. 다음 [014](../plan/verification/claude/RF-014.md) → [015](../plan/verification/claude/RF-015.md) → [016](../plan/verification/claude/RF-016.md).
3. **신규 개발:** [069](../plan/verification/codex/RF-069.md) CLI 검증 완료·UEF5 승인 snapshot 대기(재실행 금지) → [070](../plan/pending/RF-070.md) 기존 142 owner KEEP 인벤토리 수용; 85개 안전 wrapper normal/-O·A peer 완료(85/142 scoped); 잔여 57개는 **위험 launcher 32 / 기타 구현 25**로 B inventory 및 A 독립 정적 분류 완료. **B는 25 기타 구현의 소비자/효과/소유권 추가 read-only 검토만** 허용(32 위험 launcher와 25 모두 실행·mock·수정 금지), A는 RF-019 29 owner의 신규 코드/KEEP 근거 우선. 위험 32는 SAFETY_HOLD, 기타 25도 별도 승인 전 실행 금지, 기존 85 재실행 금지 → [064](../plan/pending/RF-064.md) (BLOCKED, 신규 증거 시만). [030](../plan/pending/RF-030.md)/[035](../plan/pending/RF-035.md)는 조건부 B 구현·A peer; **지팀장 별도 CURRENT 승인 전 wrapper 쓰기 금지**.

> 신규 증거만 처리. 테스트·판정·차단 상세은 해당 RF에서 관리하며 CURRENT에 운영 일지를 누적하지 않는다.
