# Agentra P1.5 — CURRENT (지팀장 실행 지시판)

**정본 파일 위치:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) · [D03](D03_DEV_TEAM_RULES.md) · [D05](D05_RF_PHYSICAL_QUEUE_20261026.md) · [D06](D06_RF_ATTEMPT_AND_AUDIT_20261026.md). D00은 내용 변경 없이 이동.

**D05/D06 물리 큐 전환 (ACTIVE):** [D05 물리 큐](D05_RF_PHYSICAL_QUEUE_20261026.md) · [D06 시도/핑퐁 감사](D06_RF_ATTEMPT_AND_AUDIT_20261026.md). 폴더 표기는 `CLAUDE_A` / `CODEX_B`. 93 RF는 `plan/queue/`에 단일 물리 경로로 이관. `plan/queue/`가 유일한 활성 RF 큐이며 과거 경로는 사용하지 않는다. A/B 예약 변경 없음. 새 문서 작성은 RF 코드 진척이나 DONE이 아니다.

**정본:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) · [D01 B](../../../AGENTS.md) · [D02 A](../../../CLAUDE.md) · [D03](D03_DEV_TEAM_RULES.md) · [STATUS](../plan/STATUS.md) · [FILE_COVERAGE](../plan/FILE_COVERAGE_63182ab2.csv). **원칙:** 자기 owner 개발 → 신규 SHA만 상대 peer → 지팀장 선별 통합·exact SHA 검증·DONE. HANDOFF/ACK만으로 회차 종료 금지. 위험 명령만 HOLD, 안전한 다음 RF 계속. main·실거래·안전 계약·오라클·예약 무승인 변경 금지.

**POLICY_REREAD_REQUIRED (A/B):** 원격 D03 [현재 `4fe849a8`](D03_DEV_TEAM_RULES.md) (A 최종 수신 `471d7ab3`, B 미수신), 역할 정본 [D01 `b1865860`](../../../AGENTS.md) / [D02 `82396714`](../../../CLAUDE.md)도 이전 HANDOFF 이후 변경. A/B는 다음 실행 CURRENT·자기 역할 정본 전문 및 변경 D03 전문을 재독하고 시작/종료 SHA·실제 적용을 HANDOFF에 증명. A의 과거 `471d7ab3` 수신은 유효한 과거 증거이나 최신 수신 완료는 아님. B `B-20261026T0410Z` RF-066 scoped 실행 수용, 정책·후속 착수는 `CONTINUATION_UNVERIFIED`. 수신·적용 확인 후 지팀장이 임시 항목 삭제.

## A Claude — 신규 개발만 ([HANDOFF_A](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-a-reporter-pure-20261021/docs/refactor/work_orders/HANDOFF_A.md))
1. **[RF-028](../plan/queue/02_DEVELOPING/CLAUDE_A/RF-028.md) — 지금 개발:** `libs/reporting/trade_report/**` 독점 85 owner. 이미 있는 pure owner/consumer·import/IO·State를 먼저 확인하고 실제 mixed responsibility가 입증된 **자기 소유 한정 최소 FIX** 또는 파일별 KEEP. R4~R9 거부 후보/타 RF/동결 오라클 재도입 금지. 실제 코드 SHA·변경 경로·표적 normal/-O 제출, 신규 SHA만 B peer.
2. **[RF-029](../plan/queue/01_PENDING/CLAUDE_A/RF-029.md) — 이어서 개발:** `trade_story/**`·`trade_read_model_parts/**` 독점 38 owner. 안전한 pure 책임 분리/소비자 검증, 필요 시 최소 FIX→B peer. RF-028 한 조각의 PASS·HANDOFF만으로 종료하지 말 것.
**개발 큐에서 제거:** RF-013·RF-017·RF-019 **DONE**. 새 결함 SHA에 대한 명시 REWORK가 아니면 재착수 금지.

## B Codex — 개발 및 RF-001 통합 검증
**최우선 1회 검증 배정 (지팀장, 2026-10-26):** B는 다음 예약 회차의 첫 실행으로 `origin/integration/p1.5` 최신 HEAD를 격리 read-only 작업장에 checkout하고 정확한 SHA를 기록한 뒤 `python -m pytest -q tests/test_p153_operator_ui_moved_bodies.py tests/test_operator_ui_data_access_phase2.py tests/test_operator_ui.py` 및 `python -O -m pytest -q`에 동일 3파일을 지정해 각 exit/PASS/FAIL을 기록한다. 외부 IO·주문·고정 파일 쓰기 금지. HANDOFF_B에 `RF001_EXACT_INTEGRATION_SHA`, normal/-O exit, 실패 node 및 push 증거를 남긴다. 해당 검증은 개발 재배정이 아니며 기존 격리 734×2·53×2 반복 금지. 테스트 실행이 불가하면 명령·원인·재개 조건을 기록하고 즉시 RF-070→RF-066의 안전한 owner 작업을 이어간다. 지팀장은 결과 도착 시 33 owner 인수조건을 판정하고 PASS면 동일 회차 물리 DONE 이동한다.
 ([HANDOFF_B](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-b-operator-structure-20261022/docs/refactor/work_orders/HANDOFF_B.md))
1. **[RF-070](../plan/queue/02_DEVELOPING/CODEX_B/RF-070.md) — 지금 남은 owner 작업:** 142 중 85 offline/mock scoped PASS 재사용. 나머지 **25 기타 구현**은 파일별 소비자·CLI·IO·side-effect 판정 후 외부 효과 없는 경계만 fake/mock normal/-O; 실제 launcher 32 명령 HOLD. 단순 정적 읽기·ACK로 종료 금지.
2. **[RF-066](../plan/queue/02_DEVELOPING/CODEX_B/RF-066.md) — 이어서:** B `B-20261026T0410Z` 격리 `build_demo_catalog` normal exit 0·marker 2 수용, `-O`는 exit 0만 확인(조건부 marker). 동일 범위 재실행 금지. temp 경로 + fake OrderClient로 **미검증 요청 형태·소비자 경계** normal/-O, 불가 시 정확한 환경 차단과 다음 owner 계속. 실제 `main()`·고정 파일 쓰기·주문 접근 HOLD.
**개발 큐에서 제거:** RF-001은 아래 지팀장 통합 후 **1회 검증만** 남음. 새 source REWORK 없이 RF-001 반복 개발·기존 734×2·53×2 재검증 금지.

## 지팀장 — 검증·통합·DONE (개발 RF와 별도)
**예약 동기화:** 지팀장 A/B 슬롯은 한국시간 매시 02분·32분 교차 실행(2026-10-26 승인). 개발팀 A/B 예약은 기존 설정 유지. 각 회차는 D00/D03에 따라 실제 RF 조치와 원격 결과를 우선하며, 조회만 수행한 경우 완료로 보고하지 않는다.

1. **[RF-001](../plan/queue/04_LEAD_ACCEPTANCE/CODEX_B/RF-001.md) — 선별 통합 완료, EXACT_SHA_TEST_PENDING:** B source `b994a133` 두 owner 파일 blob `4f73570f`·`0666538f` integration 반영, patchnotes JSON/MD 병합; source+patchnotes anchor `2f77bd95`. 기존 B 격리 734×2·UI 53×2, A peer 734×2·17 differential 수용. **B 1회 read-only 최신 integration HEAD**에서 `tests/test_p153_operator_ui_moved_bodies.py`, `tests/test_operator_ui_data_access_phase2.py`, `tests/test_operator_ui.py` normal/-O 실행·exit·HEAD 제출(검증이지 개발 재배정 아님). 지팀장이 33 owner 잔여 인수조건 판정 후 DONE. 반영 HEAD 직접 테스트 **NOT_RUN**, 아직 DONE 금지.
2. **[RF-018](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-018.md)·[RF-070](../plan/queue/02_DEVELOPING/CODEX_B/RF-070.md)·[RF-066](../plan/queue/02_DEVELOPING/CODEX_B/RF-066.md):** 새 증거만 KEEP/FIX/PEER/INTEGRATE/BLOCKED 판정. RF-018 fallback 3건 BASE 동일(2 재현, scanner_priority 우회 미재현), 안전·오라클 무승인 수정 금지. 차단 RF를 이유로 다른 큐 중단 금지.

**이번 회차 완료:** [RF-013](../plan/queue/05_DONE/CLAUDE_A/RF-013.md)·[RF-017](../plan/queue/05_DONE/CLAUDE_A/RF-017.md)·[RF-019](../plan/queue/05_DONE/CLAUDE_A/RF-019.md) KEEP_NOOP DONE, RF-001 2-owner selective integration. **물리 큐 93/93:** pending **68** / developing **3** / peer_review **9** / lead_acceptance **2** / rework **0** / DONE **11**. **예약 설정 변경 없음.**
