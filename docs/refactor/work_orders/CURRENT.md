# Agentra P1.5 — CURRENT (지팀장 2026-10-26 19시 KST 최종 배정)

**유일한 지시 정본:** `hbombheart1230-dotcom/agentra` / `integration/p1.5`의 이 CURRENT. **실행 정책:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md). **RF 실물:** [queue](../plan/queue/). **집계:** [STATUS](../plan/STATUS.md). A/B 자신의 브랜치 CURRENT, 구 HANDOFF, Issue #11/#12 댓글은 작업 배정 정본이 아니다. 필요한 D00와 현재 배정 RF만 읽고 바로 실행한다.

## 공통 실행 계약

지팀장은 A/B 새 source SHA·독립 peer·[런검증 #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32) 증거를 먼저 인수한다. 기존 유효 normal/-O/peer와 같은 SHA·경계는 반복하지 않는다. 신규 코드 diff가 있으면 owner·동결/안전/소비자·patchnotes·독립 peer를 확인한 뒤 허용 파일만 선별 통합하고 정확한 integration SHA 테스트/hosted CI를 판정한다. 신규 코드가 없으면 기존 RF의 실제 판정·물리 큐/STATUS 조치를 직접 수행한다. 판정을 A/B에 재위임하거나 ACK/HANDOFF만 쓰고 종료하지 않는다. 부분 PASS, BLOCKED, NOT_RUN은 DONE이 아니다.

A/B는 `integration/p1.5` 최신 CURRENT/HEAD를 읽고 **자기 코드 브랜치에서** 아래 RF를 실행한다. 신규 경계의 정확한 FILE::SYMBOL, BASE/source SHA, normal/`python -O` 명령·실제 exit/marker, 외부 효과 차단, CODE/BASELINE/ENV/SAFETY 판정, 변경 시 source commit을 제출한다. KEEP은 파일별 소비자·State/IO·예외 근거로 증명한다. 위험/동결/환경에 막히면 해제 조건을 기록하고 즉시 다음 안전한 RF를 수행한다. RF 큐·CURRENT·STATUS 이동/수정은 지팀장 전담.

**금지:** `main`, 실거래, Broker/Supervisor/Executor/Step5C/UEF 거래 안전 계약, 동결 테스트/CI·오라클, A/B/PC 예약·주기, 운영 데이터, 승인 없는 코드 삭제·운영 재배포. 실제 fetch/order/server bind/scheduler 실행으로 검증하지 않는다.

## 지팀장 P0 — LEAD 13건 직접 종결 게이트

**현재 큐:** PENDING **62** / DEVELOPING **3** / PEER_REVIEW **4** / LEAD_ACCEPTANCE **13** / REWORK **0** / DONE **11** = **93**. 원격 tree 전수에서 RF ID 93/93, 중복·누락 0, RF-016 이동 후 단일 경로 확인. A `3ce7aa45`, B `53d8624e`는 신규 owner source delta 0(문서/하네스만). **이번 실제 조치:** RF-016 `03_PEER_REVIEW/CODEX_B` → `04_LEAD_ACCEPTANCE/FROM_CLAUDE_A`, B 최초 strategist pure 함수 scoped peer 정상/-O exit 0 수용; 8 owner BASE/A/integration blob 동일. **RF-016은 LEAD_HOLD / NOT_DONE**. RF-014/015는 각각 기존 BASE 3/11 FAIL의 신규 위험/소비자 peer 부족으로 03에 유지.

**지팀장 LEAD 13개 직접 판정(기존 증거 재사용, 다음 부족분만):**
- RF-001: 통합 `b5fe3dd9` 표적 normal/-O 각 787 PASS 재실행 금지; 33 owner 전체·hosted CI·현행 exact SHA 범위 HOLD.
- RF-008: standalone `run_strategist`/외부 read-only fail-soft, BASE 기존 FAIL과 State 경계 HOLD.
- RF-016: 8 owner 동적 소비자·State/IO/예외, 과거 1060 PASS/1 FAIL 원인, exact integration CI HOLD.
- RF-028: 85 owner 동적 소비자·효과, partial coverage HOLD.
- RF-029: 38 owner 소비자/IO/State, hosted CI HOLD.
- RF-031/032/033/034: B 최초 scoped peer 수용, 각 전체 owner·효과·hosted CI HOLD. RF-032 29 write owner/UEF 직접 실행 금지.
- RF-063: diagnostics CLI 효과·cp949/locale·hosted CI HOLD. `check_metrics_schema_v1.main`은 **tmp-only 쓰기형**, read-only 아님.
- RF-065: research CLI 실제 쓰기·locale·hosted CI HOLD.
- RF-067: 14 owner Windows PATH/Task Scheduler·preflight·hosted CI HOLD.
- RF-069: UEF5 승인 historical snapshot 부재 ENV/CROSS_RF BLOCKED; fixture·오라클 생성 금지.

각 RF의 기존 SOURCE_SHA/상대 peer/normal/-O/consumer/IO/exception/exact integration SHA/hosted CI를 비교하여 **충족 시에만** 지팀장이 `05_DONE`으로 원자 이동한다. 누락 게이트는 RF별 기록 후 즉시 다음 RF. 현행 integration 최신 SHA check-runs 0건, 지팀장 로컬 normal/-O NOT_RUN. 위 13건을 증거 없이 DONE/REWORK로 이동하지 않는다.

## Claude A — `work/p15-a-reporter-pure-20261021`

**A 1순위 RF-033 원개발 잔여** [LEAD RF-033](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-033.md). `libs/reporting/baseline_btc_woori_tech/point_in_time_capture.py::merge_capture_into_signal_payload` → `load_capture_snapshot/load_captured_sources`의 기존 08:55·깨진 JSON·누락 day·중복 epoch·malformed ts를 synthetic tmp-root/no-fetch로 최초 확인. `python /tmp/rf033_capture_owner.py` 및 `python -O /tmp/rf033_capture_owner.py` 실행, exit/marker·SOURCE_SHA·BASE 차분·payload 불변·fallback_reason·예외·tmp 밖 쓰기 0 제출. `capture_q12_btc_0855_snapshot` 실제 fetch/운영 root 실행 금지. run106 provider fake `RF033_PROVIDERS_OK` 재실행 금지.

**A 2순위 RF-032** [LEAD RF-032](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-032.md). `libs/reporting/evaluation/pipeline.py::{_write_json,_write_text,build_q9_evaluation}`을 AST-only로 먼저 분류, `recover_forward=True`의 fresh fetch 절대 실행 금지. fake dependencies + `recover_forward=False` + tmp-root-only가 입증된 경우에만 `python /tmp/rf032_writer_owner.py` / `python -O /tmp/rf032_writer_owner.py`, marker·exit·tmp 밖 쓰기 0. 위험하면 SAFETY_HOLD 후 RF-065.

**A 3순위 RF-065 독립 신규 CLI** [LEAD RF-065](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-065.md). `scripts/research/run_alpha_hypothesis_competition.py::main`→`libs.research.alpha_competition.run_alpha_hypothesis_competition` AST-only 먼저; 기본 fetch=True로 main 직접 실행 금지. `--no-fetch` + fake dependency + tmp-only 증명되면 `python /tmp/rf065_alpha_cli_peer.py` / `python -O /tmp/rf065_alpha_cli_peer.py` 신규 marker·exit·외부 효과 0. 불가하면 RF-007 ENV 원인 기록 후 다음 안전한 RF.

**후속 RF-050:** [PENDING RF-050](../plan/queue/01_PENDING/UNASSIGNED/RF-050.md) LLM 8 owner 퇴역 후보는 지팀장이 정식 `02_DEVELOPING/CLAUDE_A`로 이동하기 전 수정·삭제 금지. 위 A 안전한 신규 경계 소진 후 지팀장이 정식 배정한다. 사용자별 제거 승인 전 source 삭제 금지.

## Codex B — `work/p15-b-operator-structure-20261022`

**B 1순위 RF-070** [DEVELOPING RF-070](../plan/queue/02_DEVELOPING/CODEX_B/RF-070.md). 기존 85/142 wrapper, 25 OTHER+32 safety, 새 `RF070_REMAINING_STATIC_OK nonrunpy=41` 정상/-O exit 0 **재실행 금지**. 지팀장이 원격 소스 blob 확인 후 **3/25** `run_operator_ui.py` COMPAT/BIND_HOLD, `run_reporter_analysis_report.py` COMPAT/WRITE_HOLD, `run_scheduled_intelligence.py` SAFETY_HOLD를 RF-070에 직접 판정했다. **남은 22 OTHER의 정확한 파일명별** `__main__/argv/cwd/env`·Windows/Docker/CLI/외부 소비자·IO/State/예외·ACTIVE/COMPAT/SAFETY_HOLD와 SOURCE_SHA를 RF-070에 완성하라. 신규 안전한 parser fake만 `python /tmp/rf070_parser_fake.py` / `python -O /tmp/rf070_parser_fake.py` 실행해 marker·exit·effects=0 제출. `main`, bind, scheduler, 운영 쓰기, 32 위험 launcher 직접 실행 금지. 22개 분류가 막히면 RF-066으로 전환.

**B 2순위 RF-066** [DEVELOPING RF-066](../plan/queue/02_DEVELOPING/CODEX_B/RF-066.md). 기존 `RF066_INVENTORY_OK files=17` 및 `demo_m22_skill_flow` fake normal/-O 재실행 금지. 잔여 16 owner의 파일별 CLI/argv/소비자·WRITE/SQLITE/ORDER/NETWORK/SYNC/DELETE 효과와 COMPAT/SAFETY_HOLD를 제출하고 최초 새 안전 fake parser 경계만 `python /tmp/rf066_next_parser.py` / `python -O /tmp/rf066_next_parser.py` marker·exit로 검증. 위험하면 RF-071.

**B 3순위 RF-071** [DEVELOPING RF-071](../plan/queue/02_DEVELOPING/CODEX_B/RF-071.md). 기존 `RF071_ENTRY_STATIC_OK` 반복 금지; `scripts/approval_cli.py::main(argv)` 권한 경계·`analyze_entry_blockers.py`·`benchmark_operator_visibility_memory.py`를 AST-only로 구분, 새 fake pure parser가 있을 때만 정상/-O exit 제출. 실제 승인/cleanup/restart/order 금지.

**B 후속 독립 peer RF-014/015:** [RF-014](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-014.md) Scanner의 기존 BASE 3 FAIL과 `p171` dynamic output payload·Top-1/reject/NOOP 경계를 `python /tmp/rf014_scanner_consumer_peer.py` / `python -O /tmp/rf014_scanner_consumer_peer.py`에서 새로운 fake 소비자로 검증. [RF-015](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-015.md) Monitor 11 FAIL의 BASE 동등성·동적 import/State/예외를 `python /tmp/rf015_monitor_consumer_peer.py` / `python -O /tmp/rf015_monitor_consumer_peer.py`에서 새 안전 경계만 확인. 기존 `RF016_014_015_PEER_OK` 순수 함수 1개씩 재실행 금지. RF-016은 이미 LEAD로 이동했고 B 최종 판정 대상 아님.

## 런검증 #32 · 트러블슈팅

Issue #32 2026-10-26 EOD의 broker SELL 1건 local event 누락·BUY guard stale·reconciliation mismatch에도 readiness/Operator GREEN·OCI image SOURCE_SHA 미입증은 **실제 관측된 일관성 위험이나 실행 이미지와 제출 source SHA가 불일치/미입증인 코드 후보**다. `graphs/nodes/execute_from_packet.py`, `build_execution_readiness.py`, `libs/read/kiwoom_order_fill_reader.py`, `libs/reporting/operator_visibility.py`의 읽기 전용 원인 매핑은 허용하되, provenance·exact SHA 재현 전 코드 REWORK/거래 안전·배포 변경 금지. RUNLAB 운영팀은 읽기 전용 근거만 보강한다.

매 회차 [troubleshooting/open](../plan/troubleshooting/open/)과 [closed](../plan/troubleshooting/closed/) 실물을 확인한다. 현행 **open 4 / closed 0**, 원격 tree 전수 확인; 브랜치 local exit, CI 역사/현행 충돌, RF-020 범위, source admission 모두 종료조건 미충족으로 이동 0. 해결된 증거가 생긴 건만 closed로 원자 이동하고 STATUS 갱신한다.

**지팀장 종료 순서:** 새 A/B/런 evidence 인수 → 직접 RF 판정/큐 이동·허용 source 선별 통합 → exact SHA 검증 → troubleshooting 종료 판단 → STATUS 갱신 → **CURRENT 마지막 갱신**. 매번 RF 93개 단일 경로·독립 peer·CI·A/B 누락 자기감사. 코드 diff 없는 회차는 코드 진척 0이라고 명시하고, 실제 RF 조치가 없으면 EXECUTION_INCOMPLETE. `main`·실거래·안전 계약·동결 오라클·예약 무승인 변경 금지.
