# Agentra P1.5 — CURRENT (작업 포인터)

> 정본: `integration/p1.5`. **안전·권한 [D00](../../ENGINEERING_DELIVERY_POLICY.md) → 공통 [D03](D03_DEV_TEAM_RULES.md) → 역할 [D01 Codex](../../../AGENTS.md) / [D02 Claude](../../../CLAUDE.md)**. 매회 REWORK → 상대 독립 검증 → 신규 개발 **1→2→3 전부 순회**. RF별 상세 판정은 RF 정본, 집계는 [STATUS](../plan/STATUS.md), 런검증은 별도 D04.

## 규칙 변경 ACK (확인 전 유지)
- 최신 blob: D00 `9224bfd4`, D01 `e386bb7a`, D02 `e5ecd133`, D03 `04a64b5d`. A는 D00·D02·D03, B는 D00·D01·D03 최신본을 실제 읽고 HANDOFF에 각 blob ACK 기록.
- **임시 2회 확인 지시 유지:** A/B 모두 각자 다음 2회 실행에서 D03 전문과 역할별 D01/D02를 읽고 `D03_READ_ACK=<blob>; D01_OR_D02_READ_ACK=<blob>; 적용 RF/다음 행동` 기록. 지팀장이 **각 2회 ACK 확인 후에만** 이 줄 삭제. D03 §3A 테스트 우선 판정 즉시 적용. 기존 PASS/KEEP/peer 증거 재사용; 동일 SHA·테스트 반복 금지.

## 지팀장
- [D00 자율 완료 운영](../../ENGINEERING_DELIVERY_POLICY.md)·[D03 §3/§3A](D03_DEV_TEAM_RULES.md) 기준으로 DONE 후보 우선 판정, 승인 경로만 선별 통합, 통합 SHA normal/-O 검증. 차단은 해당 RF에 기록하고 다음 RF 진행.
- [RF-020 DONE](../plan/done/RF-020.md): Monitor 30/30 KEEP, A 독립 normal/-O 각 528 PASS 및 통합 소유 코드·테스트 동일성 수용, 재실행 금지. [RF-009 DONE](../plan/done/RF-009.md): Graph 3/3 KEEP·A peer 145+33 normal/-O·integration 코드/테스트 동일성 수용, 재실행 금지. [RF-068 DONE](../plan/done/RF-068.md): 8/8 KEEP·독립 peer 및 통합 코드 동등성 normal/-O 수용, 재실행 금지. [RF-013](../plan/verification/claude/RF-013.md): 기존 67 scoped PASS, 신규 9+4 NOT_ADMITTED(오라클·writer 변경 금지). [RF-069](../plan/verification/codex/RF-069.md): CLI 2경계 A 신규 offline/mock peer 수용; UEF5 승인 snapshot 부재 ENVIRONMENT 유지. B는 동일 CLI 재실행하지 않고 RF-070 read-only inventory 진행.

## Claude A — `work/p15-a-reporter-pure-20261021` · [HANDOFF](HANDOFF_A.md)
1. **REWORK:** 없음.
2. **독립 검증:** [001](../plan/verification/codex/RF-001.md). 기존 scoped PASS 재사용, 실제 빠진 위험만 검증. [069](../plan/verification/codex/RF-069.md) 2 CLI peer 완료(재검증 금지), UEF5 승인 snapshot 신규 증거가 생길 때만 peer. 이후 [067](../plan/verification/codex/RF-067.md) → [066](../plan/verification/codex/RF-066.md) → [063](../plan/verification/codex/RF-063.md) → [065](../plan/verification/codex/RF-065.md) → [007](../plan/verification/codex/RF-007.md) → [008](../plan/verification/codex/RF-008.md).
3. **신규 개발:** [019](../plan/pending/RF-019.md) → [017](../plan/pending/RF-017.md).

## Codex B — `work/p15-b-operator-structure-20261022` · [HANDOFF](HANDOFF_B.md)
1. **REWORK:** 없음. RF-009/020 DONE(재검증 금지), RF-001 verification 유지.
2. **독립 검증:** [013](../plan/verification/claude/RF-013.md) 기존 67 owner 105+105 scoped PASS 재사용; 신규 9+4 실패 재실행 금지. 다음 [018](../plan/verification/claude/RF-018.md) → [014](../plan/verification/claude/RF-014.md) → [015](../plan/verification/claude/RF-015.md) → [016](../plan/verification/claude/RF-016.md).
3. **신규 개발:** [069](../plan/verification/codex/RF-069.md) CLI 검증 완료·UEF5 승인 snapshot 대기(재실행 금지) → [070](../plan/pending/RF-070.md) 원소유 launcher 범위 읽기 전용 소비자 인벤토리부터(실행·배포 금지) → [064](../plan/pending/RF-064.md) (BLOCKED, 신규 증거 시만). [030](../plan/pending/RF-030.md)/[035](../plan/pending/RF-035.md)는 조건부 B 구현·A peer; **지팀장 별도 CURRENT 승인 전 wrapper 쓰기 금지**.

> 신규 증거만 처리. 테스트·판정·차단 상세은 해당 RF에서 관리하며 CURRENT에 운영 일지를 누적하지 않는다.
