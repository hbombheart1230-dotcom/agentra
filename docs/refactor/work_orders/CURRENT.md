# Agentra P1.5 — CURRENT (지팀장 LEAD 13건 직접 판정 후 / 2026-10-26 19시 KST)

**유일한 시작점:** `hbombheart1230-dotcom/agentra` / `integration/p1.5` / 이 파일. **운영:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md), 필요할 때만 **아래 배정 RF**를 읽는다. 작업 브랜치 CURRENT·과거 HANDOFF 지시는 사용하지 않는다.

## 지팀장 B 슬롯 최신 실행 — RF-007 E2E 독립 peer 인수 (2026-10-26)

- **실제 GitHub 물리 이동:** RF-007 `03_PEER_REVIEW/CLAUDE_A` → `04_LEAD_ACCEPTANCE/FROM_CODEX_B` 단일 git tree 커밋 `9bd49b65`. 이전 경로 404, 새 경로 존재 확인. A [run109](https://github.com/hbombheart1230-dotcom/agentra/issues/11#issuecomment-6413694611) synthetic 5일/14거래 loopback E2E `node e2e/smoke.mjs` 및 `node e2e/public-profile.mjs` 각각 exit 0. `apps/web/` git subtree BASE/B/integration 동일 `a96c7deb`, 신규 코드 통합 0. **LEAD_HOLD / NOT_DONE**: exact-SHA hosted CI·전체 소비자/의존성 게이트 미완료. 이전 Vitest/build/E2E 반복 금지.
- **최신 큐 (STATUS `b7a60b80`):** PENDING **61** / DEVELOPING **4** / PEER_REVIEW **3** / LEAD_ACCEPTANCE **14** / REWORK **0** / DONE **11** = 93. GitHub queue 13개 폴더 전수 고유 RF 93/93, 중복·누락 0. 아래 13 LEAD/61·4·4·13은 **이전 회차 기준선**이고 최신값으로 오인 금지.
- **A:** RF-050은 이미 `02_DEVELOPING/CLAUDE_A` 정식 배정. LLM 8 owner read-only consumer·env·fallback/Commander policy 조사 및 최초 synthetic pure normal/-O 수행. 승인 없는 모델 기본값 변경·실제 API·코드 삭제 금지.
- **B:** RF-070 미분류 22 OTHER 파일별 argv/env/IO/동적·외부 소비자·ACTIVE/COMPAT/SAFETY_HOLD 완성, 막히면 RF-066 16 owner → RF-071. 안전 런처 실행 금지.
- **런검증 #32 / 장애:** 17:38 broker/local SELL provenance UNKNOWN, BUY guard stale, readiness/Operator GREEN vs reconciliation mismatch, OCI source SHA 불명. 코드 REWORK·실거래 안전 변경 금지. troubleshooting open 4/closed 0, 종료조건 충족 0. RF-007 제외 다른 RF 큐 이동 0. CURRENT 마지막 반영.

## 지팀장 필수 실행 슬롯 — LEAD 큐 우선

**이 절은 [D00 §2](D00_ENGINEERING_DELIVERY_POLICY.md)의 자동 실행 의무를 현재 회차에 적용한다.** 별도 사용자 지시를 기다리지 않는다. A/B 신규 진척 확인 즉시 `04_LEAD_ACCEPTANCE` **전건**을 지팀장 자신의 작업으로 직접 처리한다. 증거 재사용 → 가능한 신규 직접 검증/선별 통합 → DONE·REWORK·구체적 차단 확정 및 물리 큐 이동 → 새 A/B 작업 배정 순서. **A/B 배정·STATUS/CURRENT 갱신만 하고 LEAD 실물 처리를 생략하면 `EXECUTION_INCOMPLETE`**. HOLD를 반복하거나 최종 판정을 A/B에 재위임하지 않는다. 승인·실행환경·독립 peer가 필요한 경우에는 정확한 게이트만 남기고 안전한 다음 RF를 진행한다. 모든 DONE은 D00의 전체 인수·필수 검증을 충족해야 한다.

**현행 LEAD 14건:** RF-001/007/008/016/028/029/031/032/033/034/063/065/067/069. RF-007은 새로 인수한 synthetic E2E peer의 범위만 인정, 정확 SHA hosted CI·잔여 소비자 게이트 HOLD. RF-001의 기존 787×2, RF-032/033/065의 신규 run108, 기타 기존 peer는 반복 금지. **우선 지팀장 본인이 14건 각각 DONE 가능 여부와 남은 최초 직접 실행 가능한 게이트를 확인**한다. 상세 과거 판정·실패 분류는 [STATUS](../plan/STATUS.md) 및 각 RF가 정본이며 이 CURRENT에 반복 기재하지 않는다.

**공통 실행:** A/B는 최신 integration CURRENT만 읽고 자기 코드 브랜치에서 수행, 안전한 최초 신규 경계 normal/`python -O` 실제 exit·SHA 제출, 시간·RF 개수 제한 없음. 중복 검증·ACK-only 종료 금지. main/실거래/거래 안전 계약/동결 테스트·CI/예약·운영 데이터·승인 없는 삭제 금지. **회차 종료 순서:** 신규 증거 → LEAD 전건 직접 판정/가능한 조치 → 선별 통합·정확 SHA 검증 → troubleshooting open/closed → STATUS → CURRENT 마지막.

## Claude A — `work/p15-a-reporter-pure-20261021`

**A P0 1순위 — RF-050 신규 원개발** [02_DEVELOPING/CLAUDE_A](../plan/queue/02_DEVELOPING/CLAUDE_A/RF-050.md). 8 `libs/llm/` owner만, `libs/llm/router.py::LLMRouter.chat`, `libs/llm/llm_router.py::LLMRouter.resolve/chat`, `libs/llm/model_catalog.py::{resolve_policy_llm_slot,resolve_model_profile}`의 구형/현재 API consumers와 Commander `applied_policy.llm`→role env→model fallback·동적 import·UI/Reporter/Strategist/스케줄·실제 State/IO를 READ-ONLY로 분류. `ACTIVE/FALLBACK/COMPAT/DORMANT/REMOVE_CANDIDATE/SAFETY_HOLD`별 8 owner 파일 인벤토리. 합성 policy·model name만 `/tmp/rf050_policy_lookup.py` fake/monkeypatch로 사용해 **`python /tmp/rf050_policy_lookup.py`**, **`python -O /tmp/rf050_policy_lookup.py`** 최초 marker/exit·SOURCE_SHA 제출. 실제 OpenRouter/Kiwoom 호출·model default 변경·소스 제거/이동/설정 변경 **승인 전 금지**. 실행 불가면 효과 차단 경계를 적고 static 8파일 소비자를 계속; B가 RF-070 등 새 결과를 낸 경우 RF-050 한정 신규 안전 peer 작업으로 이동.

**A P1 — 기존 B 코드 후속 LEAD 신규 독립 경계 지원** [RF-063](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-063.md) / [RF-067](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-067.md). 기존 diagnostics audit·metrics tmp writer, root check_ 두 wrapper alias/runpy, normal/-O marker는 이미 수용돼 재실행 금지. 새 `scripts/diagnostics/check_alert_policy_v1.py::{_build_parser,_evaluate_alerts}` pure JSON metrics fake 입력과 cp949 decode/encode 사유 분리를 `/tmp/rf063_alert_locale_peer.py`에서 normal/`-O` 최초 테스트하라. `python /tmp/rf063_alert_locale_peer.py` / `python -O /tmp/rf063_alert_locale_peer.py` marker·exit; 실제 `main`/report write/환경·broker 접근 금지. 이후 RF-067 `scripts/check_real_execution_preflight.py` AST-only public consumer/Windows PATH/env timing, broker preflight 실행 금지; 새 safe peer 없으면 RF-050 조사 계속. 기존 RF-065 `--no-fetch` normal/-O·RF-033 capture·RF-032 writer 원개발 재실행 금지.

## Codex B — `work/p15-b-operator-structure-20261022`

**B P0 1순위 — RF-032 LEAD 미충족 신규 write peer** [RF-032](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-032.md). A run108 temp writer 결과를 재실행하지 말고 별도 **`/tmp/rf032_writer_peer.py`**에서 `libs/reporting/evaluation/pipeline.py::build_q9_evaluation`의 **nonempty synthetic trade**, missing/bad rows·예외, 출력 모든 파일의 `resolve().is_relative_to(tmp/reports/evaluation)` 진위, State 불변, tmp outside writes=0을 검증. `python /tmp/rf032_writer_peer.py` / `python -O /tmp/rf032_writer_peer.py` 실제 exit/marker, A source `c3462ec3`·integration blob 제출. `all(... or True...)` 같은 항등참 금지, `recover_forward=True` real fetch/UEF·broker 실행 금지. 불가능한 기능만 SAFETY_HOLD하고 즉시 RF-033.

**B P0 2순위 — RF-033 LEAD 새 capture peer** [RF-033](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-033.md). `libs/reporting/baseline_btc_woori_tech/point_in_time_capture.py::{load_capture_snapshot,load_captured_sources,merge_capture_into_signal_payload}`의 malformed JSON/missing day/duplicate epoch/타임스탬프 문자열 예외와 data_provider consumer 계약을 독립 tmp/no-fetch fake로 `/tmp/rf033_capture_peer.py`에서 처음 확인. `python /tmp/rf033_capture_peer.py` / `python -O /tmp/rf033_capture_peer.py`, marker·exit 및 BASE 동등성. 기존 provider/comparison와 run108 A capture 재실행 금지. `ValueError`가 BASE에도 있으면 신규 CODE REWORK로 기록하지 말고 기존 예외와 하드닝 제안을 분리. 이후 RF-070.

**B P1 3순위 — RF-070** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-070.md). 기존 85/142 wrappers, 25 OTHER+32 safety, AST 41 재실행 금지. 25 OTHER 중 3건(Operator SERVER_BIND, Reporter WRITE, scheduled SCHEDULER) 이미 지팀장 분류 완료. **나머지 22개 정확 경로**별 `__main__/argv/cwd/env`, Windows/Docker/CLI/스케줄 동적 소비자, 효과 token, `ACTIVE/COMPAT/SAFETY_HOLD`, SHA를 채워라. 안전한 parser 최초 신규 mock만 `/tmp/rf070_parser_fake.py`에서 `python /tmp/rf070_parser_fake.py` / `python -O /tmp/rf070_parser_fake.py` marker/exit; 실제 launcher/bind/order/운영 writes 금지. 막히면 RF-066.

**B P1 4순위 — RF-066** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-066.md). 기존 17 AST/OrderClient fake/M22 1 consumer PASS 재사용. 잔여 16 CLI 파일별 호출·error propagation·temp-only 소비자 근거 제출, 새 안전 fake parser만 `python /tmp/rf066_next_parser.py` / `python -O /tmp/rf066_next_parser.py` marker/exit; broker/Step5D/SQLite/운영 sync/delete 금지. 막히면 RF-071.

**B P2 5순위 — RF-071** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-071.md). `scripts/approval_cli.py::main(argv)` 권한 경계 및 root 42 launcher FILE::SYMBOL 정적 분류. `/tmp/rf071_entry_static.py` 최초 추가 순수 parse 소비자만 `python /tmp/rf071_entry_static.py` / `python -O /tmp/rf071_entry_static.py`; 기존 `RF071_ENTRY_STATIC_OK` 동일 하네스 재실행 금지. 승인/cleanup/restart/order main 금지. 이후 [RF-014](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-014.md) Scanner dynamic Top1/p171 fake peer `python /tmp/rf014_scanner_consumer_peer.py` / `python -O /tmp/rf014_scanner_consumer_peer.py`와 [RF-015](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-015.md) Monitor State/event fake peer `python /tmp/rf015_monitor_consumer_peer.py` / `python -O /tmp/rf015_monitor_consumer_peer.py` 신규 경계, 기존 pure 1함수 peer 중복 금지.

## RunLab #32 / Troubleshooting

[Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32): 2026-10-26 EOD BUY/SELL broker fill vs local SELL 미기록·stale BUY guard·readiness/Operator GREEN과 reconciliation mismatch·OCI image source SHA UNKNOWN. 관측된 일관성 위험은 인정하되 **검증 이미지/실제 submitting owner 미입증**이므로 REWORK/안전 코드/재배포 무승인 금지. RunLab은 기존 주문 0019354/0020349의 읽기 전용 trace·image revision provenance를 보강한다.

`docs/refactor/plan/troubleshooting/open/` 4건·`closed/` .gitkeep 외 해결 기록 0; 아직 4건 모두 종료조건 불충족. 해결이 실제 증명된 건만 `closed/` 이동한다. 최신 확인한 queue 93/93 unique, STATUS와 물리 파일 일치. **종료 순서:** 신규 증거 → 지팀장 직접 RF 판정/큐·통합 → 필수 exact SHA 검증 → troubleshooting → STATUS → **CURRENT 마지막**.
