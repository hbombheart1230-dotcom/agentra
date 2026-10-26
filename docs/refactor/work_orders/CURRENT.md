# Agentra P1.5 — CURRENT (지팀장 실행 지시판)

**정본:** [D00](../../ENGINEERING_DELIVERY_POLICY.md) · [D01 B](../../../AGENTS.md) · [D02 A](../../../CLAUDE.md) · [D03](D03_DEV_TEAM_RULES.md) · [STATUS](../plan/STATUS.md) · [FILE_COVERAGE](../plan/FILE_COVERAGE_63182ab2.csv). **원칙:** 자기 owner 개발 → 신규 SHA만 상대 peer → 지팀장 선별 통합·exact SHA 검증·DONE. HANDOFF/ACK만으로 회차 종료 금지. 위험 명령만 HOLD, 안전한 다음 RF 계속. main·실거래·안전 계약·오라클·예약 무승인 변경 금지.

**D03 수신:** A `471d7ab3` 수신·연속 착수 확인(RUN `2026-10-26T0448Z-claude-a-sched-96`). **B 미확인**(최신 RUN `B-20261026T0400Z`는 RF-001 UI 53×2만 제출, 후속 착수/NOT_STARTED_REASON 누락 → `CONTINUATION_UNVERIFIED`). B는 D03 `471d7ab3` 전문 재독·실제 후속 착수 및 HANDOFF 근거 제출. 양쪽 확인 후 지팀장이 이 임시 항목 삭제.

## A Claude — 신규 개발만 ([HANDOFF_A](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-a-reporter-pure-20261021/docs/refactor/work_orders/HANDOFF_A.md))
1. **[RF-028](../plan/pending/RF-028.md) — 지금 개발:** `libs/reporting/trade_report/**` 독점 85 owner. 이미 있는 pure owner/consumer·import/IO·State를 먼저 확인하고 실제 mixed responsibility가 입증된 **자기 소유 한정 최소 FIX** 또는 파일별 KEEP. R4~R9 거부 후보/타 RF/동결 오라클 재도입 금지. 실제 코드 SHA·변경 경로·표적 normal/-O 제출, 신규 SHA만 B peer.
2. **[RF-029](../plan/pending/RF-029.md) — 이어서 개발:** `trade_story/**`·`trade_read_model_parts/**` 독점 38 owner. 안전한 pure 책임 분리/소비자 검증, 필요 시 최소 FIX→B peer. RF-028 한 조각의 PASS·HANDOFF만으로 종료하지 말 것.
**개발 큐에서 제거:** RF-013·RF-017·RF-019 **DONE**. 새 결함 SHA에 대한 명시 REWORK가 아니면 재착수 금지.

## B Codex — 신규 개발만 ([HANDOFF_B](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-b-operator-structure-20261022/docs/refactor/work_orders/HANDOFF_B.md))
1. **[RF-070](../plan/verification/codex/RF-070.md) — 지금 남은 owner 작업:** 142 중 85 offline/mock scoped PASS 재사용. 나머지 **25 기타 구현**은 파일별 소비자·CLI·IO·side-effect 판정 후 외부 효과 없는 경계만 fake/mock normal/-O; 실제 launcher 32 명령 HOLD. 단순 정적 읽기·ACK로 종료 금지.
2. **[RF-066](../plan/verification/codex/RF-066.md) — 이어서:** `demo_m7_dry_run_pipeline.py` 실제 `main()`·고정 파일 쓰기·주문 접근 명령만 HOLD. temp 경로 + fake OrderClient로 `build_demo_catalog`/소비자 normal/-O 실행, 불가하면 정확한 환경 차단과 다른 owner 작업으로 계속.
**개발 큐에서 제거:** RF-001은 아래 지팀장 통합 후 **1회 검증만** 남음. 새 source REWORK 없이 RF-001 반복 개발·기존 734×2·53×2 재검증 금지.

## 지팀장 — 검증·통합·DONE (개발 RF와 별도)
1. **[RF-001](../plan/verification/codex/RF-001.md) — 선별 통합 완료, EXACT_SHA_TEST_PENDING:** B source `b994a133` 두 owner 파일 blob `4f73570f`·`0666538f` integration 반영, patchnotes JSON/MD 병합; source+patchnotes anchor `2f77bd95`. 기존 B 격리 734×2·UI 53×2, A peer 734×2·17 differential 수용. **B 1회 read-only 최신 integration HEAD**에서 `tests/test_p153_operator_ui_moved_bodies.py`, `tests/test_operator_ui_data_access_phase2.py`, `tests/test_operator_ui.py` normal/-O 실행·exit·HEAD 제출(검증이지 개발 재배정 아님). 지팀장이 33 owner 잔여 인수조건 판정 후 DONE. 반영 HEAD 직접 테스트 **NOT_RUN**, 아직 DONE 금지.
2. **[RF-018](../plan/verification/claude/RF-018.md)·[RF-070](../plan/verification/codex/RF-070.md)·[RF-066](../plan/verification/codex/RF-066.md):** 새 증거만 KEEP/FIX/PEER/INTEGRATE/BLOCKED 판정. RF-018 fallback 3건 BASE 동일(2 재현, scanner_priority 우회 미재현), 안전·오라클 무승인 수정 금지. 차단 RF를 이유로 다른 큐 중단 금지.

**이번 회차 완료:** [RF-013](../plan/done/RF-013.md)·[RF-017](../plan/done/RF-017.md)·[RF-019](../plan/done/RF-019.md) KEEP_NOOP DONE, RF-001 2-owner selective integration. **큐:** pending **69** / verification **13** / rework **0** / DONE **11**. **예약 설정 변경 없음.**
