# Agentra P1.5 — CURRENT

**정본:** `hbombheart1230-dotcom/agentra` / `integration/p1.5`
**운영:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) · **RF:** [물리 큐](../plan/queue/) · **집계:** [STATUS](../plan/STATUS.md)

**이 브랜치의 CURRENT만 지시 정본이다.** A/B는 자신의 브랜치 CURRENT·구 HANDOFF의 지시를 사용하지 않는다. D00 및 아래 배정 RF만 필요 시 읽어라. 같은 SHA·같은 경계 반복 검증·ACK 문서로 종료하지 마라.

## Claude A — `work/p15-a-reporter-pure-20261021`

1. **즉시 실행: RF-031 원개발** [02_DEVELOPING/CLAUDE_A](../plan/queue/02_DEVELOPING/CLAUDE_A/RF-031.md). `libs/reporting/(trade_report_|reporter_|trade_story_)*.py` 22개 독점 owner의 실제 BASE/통합/작업 tree blob 및 책임·소비자·patchability·LLM/IO/State·예외·부작용 차분을 조사하라. RF-074 동결 `test_target_tree_discipline_and_no_forbidden_surface`를 변경 없이 보존하고 owner 변경 가능 경계부터 판별하라. 합법적 최소 코드 FIX가 가능하면 실제 source SHA+표적 normal/-O exit+오라클 PASS를 제출하라. 불가하면 파일별 KEEP와 위험 근거를 제출하고 다음 실행 가능한 RF로 이어가라.
2. **RF-030은 개발 중단 / 지팀장 승인 대기** [01_PENDING/CLAUDE_A](../plan/queue/01_PENDING/CLAUDE_A/RF-030.md). A `03b255e5` 순수 렌더 추출은 인정하지만 원본 RF-074 동결 오라클 변경 전 PASS→후 FAIL. run 102의 16/16 forbidden owner 판정으로 현재 허용 가능한 source 대안 없음. 사용자 승인 없이 frozen test/CI·allowlist 변경하거나 day-loader 패치를 적용하지 마라. 본 후보를 integration에 제안·재검증하지 마라.
3. **RF-063/065 독립 peer의 '새 경계'만 계속** [RF-063](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-063.md) · [RF-065](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-065.md). run 102 AST + 130/130 import-only × BASE/integration × normal/-O byte-identical exit 0은 지팀장이 수용했다. 재실행하지 마라. 운영 CLI/실데이터/쓰기/주문/프로세스가 수반되는 `__main__`은 SAFETY_HOLD. 새 안전 격리 consumer/CLI 경계에 한해 read-only peer하고 SHA·명령·exit·차단 범위를 제출하라.
4. **RF-008** [LEAD](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-008.md) A 기존 1270 PASS/1 BASELINE FAIL·State 5종 peer는 수용 완료. 재실행 금지. standalone `run_strategist`/외부 read-only 시세 fail-soft는 지팀장이 별도 경계를 명시하기 전까지 이관 대기. **RF-007** fastapi ENV 차단, **RF-067** 14 import peer PASS/실제 CLI HOLD 유지. RF-028/029 자체 85/38 KEEP 증거 반복 금지.

**출력:** 자신의 작업 브랜치에서 실제 source SHA·새 테스트 명령/normal/-O exit·미검증 경계·안전 HOLD만 HANDOFF_A 및 Issue #11로 제출. 작업 브랜치 CURRENT를 덮어쓰거나 지팀장 큐를 이동하지 마라.

## Codex B — `work/p15-b-operator-structure-20261022`

1. **최우선 RF-001 사후 통합 정확-SHA 검증** [LEAD](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-001.md). `integration/p1.5` HEAD SHA를 즉시 확인하고 별도 read-only 격리 checkout에서 `tests/test_p153_operator_ui_moved_bodies.py`, `tests/test_operator_ui_data_access_phase2.py`, `tests/test_operator_ui.py`를 각각 normal/`python -O`로 실행, 정확한 SHA·명령·exit·노드 결과를 제출하라. 기존 격리 후보 734×2 / UI 53×2 / A 최초 peer는 **재실행하지 마라**. HEAD 이동 시 최신 SHA에서 최초 1회만 증명하라. 코드·동결 테스트 수정 금지.
2. **RF-028/029 최초 B peer** [RF-028](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-028.md) · [RF-029](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-029.md). A 85/38 owner blob BASE 동일·자체 KEEP 증거 수용. RF-028의 동적 소비자·IO/State·예외 새 위험 경계, RF-029의 `trade_story_pipeline.py` / `read_artifact_selection.py` 입력 우선순위·예외·효과 경계를 offline/read-only normal/-O 최초 확인하고 SHA·명령·exit를 제출하라. RF-030 A 후보는 frozen 오라클 HOLD이므로 독립 peer 실행하지 마라.
3. **RF-066** [개발](../plan/queue/02_DEVELOPING/CODEX_B/RF-066.md): 기존 `build_demo_catalog` normal marker 및 optimized exit-only 반복 금지. 임시 경로·가짜 `OrderClient`를 강제한 소비자/요청형태·실패 입력 normal/-O의 **독립적인 성공 marker**를 만들고 exit 0을 증명하라. 실제 `main()`/broker/order·운영 경로 쓰기 금지; 격리 실패면 해당 경계만 NOT_RUN 후 다른 RF 진행.
4. **RF-070** [개발](../plan/queue/02_DEVELOPING/CODEX_B/RF-070.md): 85/142 wrapper 기존 scoped PASS 재사용, 잔여 25개의 실행 소비자·IO·State/효과 AST 분류를 끝내라. 32 위험 launcher 실행 금지. **RF-018** [peer](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-018.md) 기존 BASE 동일 prose fallback 분류 반복하지 말고 미검증 경계가 있을 때만 신규 peer; **RF-069** [LEAD](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-069.md) UEF5 승인된 snapshot 없는 ENV BLOCK 유지.

**출력:** 신규 코드 SHA·실제 명령·normal/-O exit·독립 peer·HOLD를 HANDOFF_B 및 Issue #12로 제출. 전체 브랜치 병합이나 RF 판정·큐 이동 금지.

## 지팀장 — `integration/p1.5`

1. A run 102의 RF-030 16/16 frozen closed path 위반·RF-063/065 130 import-only peer와 B RF-066 부분 검증을 인수했다. **RF-030→PENDING/CLAUDE_A HOLD, RF-031→DEVELOPING/CLAUDE_A 배정**. RF-063/065는 PEER_SCOPED_ACCEPTED지만 실제 CLI 미완료이므로 PEER 유지. RF-001/008/069은 LEAD 유지, RF-028/029/018은 새 peer 결과 전 PEER 유지. 이번 회차 코드 선별 통합 0, DONE 0.
2. Issue [#32](https://github.com/hbombheart1230-dotcom/agentra/issues/32): 예약 미구성·실행 이미지 SHA 미입증은 RUNLAB 환경, 모의 BUY ACCEPTED의 FILL/CANCEL/TTL 관측은 UNKNOWN. RUNLAB 17/19시 신규 증거를 기다려 재현된 코드 결함만 기존 소유 RF에 연결하라. 런타임/예약/실거래 무승인 수정 금지.
3. 매 회차 [troubleshooting/open](../plan/troubleshooting/open/) 및 [closed](../plan/troubleshooting/closed/) 확인. 현재 open 4/closed 0; 해결 조건 충족한 건만 원자 이동하고 STATUS 갱신. 소스 통합 허용은 owner exact blob·상대 신규 peer·동결 오라클 normal/-O·patchnotes 증명이 모두 있는 최소 범위만.
4. **다음 실행 순서:** A/B 신규 소스·peer·Issue #32 수신 → 지팀장 직접 RF FIX/KEEP/PEER/INTEGRATE/BLOCKED 및 큐 판정 → 허용 소스만 선별 통합·정확 SHA 검증 → 다음 소유 RF 배정 → **마지막 CURRENT/STATUS 동기화**. main/거래 안전/동결 test·CI/예약 무승인 변경 금지.

**물리 큐 기준(2026-10-26 지팀장 A 슬롯):** PENDING **66** (UNASSIGNED **65**, CLAUDE_A **1: RF-030 HOLD**) / DEVELOPING **3** (A RF-031; B RF-066/070) / PEER **10** / LEAD **3** / REWORK **0** / DONE **11** = **93 RF**. RF-071은 미배정. 전체 DONE은 완전 인수·필수 정확-SHA 증명까지 유보한다.
