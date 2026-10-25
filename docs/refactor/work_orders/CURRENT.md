# Agentra P1.5 — CURRENT (작업 포인터)

> 정본: `integration/p1.5`. **안전·권한 [D00](../../ENGINEERING_DELIVERY_POLICY.md) → 공통 [D03](D03_DEV_TEAM_RULES.md) → 역할 [D01 Codex](../../../AGENTS.md) / [D02 Claude](../../../CLAUDE.md)**. 매회 REWORK → 상대 독립 검증 → 신규 개발 **1→2→3 전부 순회**. RF별 상세 판정은 RF 정본, 집계는 [STATUS](../plan/STATUS.md), 런검증은 별도 D04.

## 규칙 변경 ACK (확인 전 유지)
- 최신 blob: D00 `806d149d`, D01 `2c63bf6b`, D02 `e5ecd133`, D03 `756eda8a`. A는 D00·D02·D03, B는 D00·D01·D03 최신본을 실제 읽고 HANDOFF에 각 blob ACK 기록.
- **임시 2회 확인 지시 유지:** A/B 모두 각자 다음 2회 실행에서 D03 전문과 역할별 D01/D02를 읽고 `D03_READ_ACK=<blob>; D01_OR_D02_READ_ACK=<blob>; 적용 RF/다음 행동` 기록. 지팀장이 **각 2회 ACK 확인 후에만** 이 줄 삭제. D03 §3A 테스트 우선 판정 즉시 적용. 기존 PASS/KEEP/peer 증거 재사용; 동일 SHA·테스트 반복 금지.

## 지팀장
- A/B 코드 SHA·HANDOFF·신규 peer 증거만 확인 → RF 판정/큐 이동 → 소유권 승인된 경로만 선별 통합 → 통합 정확한 SHA normal/-O 확인 → 조건 충족 시 DONE. 지팀장 코드 변경도 상대 peer 필수. 환경 부재 시 NOT_RUN과 실행 담당 명시.
- **RF-013 차단:** 기존 67 owner frozen peer normal/-O 각 105 PASS는 `PEER_SCOPED_PASS`로 인정. 신규 read_models 9 + RF-030/035 wrapper 4는 RF-074 원본 frozen normal/-O 각 104 PASS/1 FAIL로 **NOT_ADMITTED**; writer 비활성, 통합/오라클 변경 금지. 소유권·계약 해결 전 진행 불가. 상세은 [RF-013](../plan/verification/claude/RF-013.md).
- **RF-068:** 기존 metrics/ops 11+11 peer PASS 및 strategist/symbol 15+15 self PASS 재사용. B는 operator_summary 기간별 출력·M28 호환 진입점 2개 경계만 표적 offline/mock; A는 신규 B 15 범위만 peer. 상세은 [RF-068](../plan/pending/RF-068.md).
- hosted CI/GREEN은 D03에 따라 필수 게이트 아님. `main` 병합·실거래·안전/오라클 무승인 변경 금지.

## Claude A — `work/p15-a-reporter-pure-20261021` · [HANDOFF](HANDOFF_A.md)
1. **REWORK:** 없음.
2. **독립 검증:** [020](../plan/verification/codex/RF-020.md) → [009](../plan/verification/codex/RF-009.md) → [001](../plan/verification/codex/RF-001.md). 기존 scoped PASS 재사용, 실제 빠진 위험만 검증. 추가 [068](../plan/pending/RF-068.md) B 신규 strategist/symbol peer. 이후 [067](../plan/verification/codex/RF-067.md) → [066](../plan/verification/codex/RF-066.md) → [063](../plan/verification/codex/RF-063.md) → [065](../plan/verification/codex/RF-065.md) → [007](../plan/verification/codex/RF-007.md) → [008](../plan/verification/codex/RF-008.md).
3. **신규 개발:** [019](../plan/pending/RF-019.md) → [017](../plan/pending/RF-017.md).

## Codex B — `work/p15-b-operator-structure-20261022` · [HANDOFF](HANDOFF_B.md)
1. **REWORK:** 없음. RF-001/009/020은 재현된 신규 소스 결함 없이 verification/codex 복귀(전체 PASS/DONE 아님).
2. **독립 검증:** [013](../plan/verification/claude/RF-013.md) 기존 67 owner 105+105 scoped PASS 재사용; 신규 9+4 실패 재실행 금지. 다음 [018](../plan/verification/claude/RF-018.md) → [014](../plan/verification/claude/RF-014.md) → [015](../plan/verification/claude/RF-015.md) → [016](../plan/verification/claude/RF-016.md).
3. **신규 개발:** [068](../plan/pending/RF-068.md) → [064](../plan/pending/RF-064.md) (BLOCKED, 신규 증거 시만). [030](../plan/pending/RF-030.md)/[035](../plan/pending/RF-035.md)는 조건부 B 구현·A peer; **지팀장 별도 CURRENT 승인 전 wrapper 쓰기 금지**.

> 신규 증거만 처리. 테스트·판정·차단 상세은 해당 RF에서 관리하며 CURRENT에 운영 일지를 누적하지 않는다.
