# Agentra P1.5 — CURRENT (최신 실행 정본)

**정본:** `integration/p1.5`의 이 파일. **상시 규칙/LEAD 자동 처리 의무:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md). 여기에는 **최신 큐·A/B 실행 지시·이번 회차 예외만** 남긴다. 작업 브랜치 CURRENT 사용 금지.

## 현재 큐·지팀장 우선 처리

- **물리 큐:** PENDING 61 / DEVELOPING 4 / PEER_REVIEW 3 / LEAD_ACCEPTANCE 14 / REWORK 0 / DONE 11 = **93**, 중복·누락 0 (최근 원격 tree 확인).
- **LEAD 14건:** RF-001/007/008/016/028/029/031/032/033/034/063/065/067/069. 지팀장은 A/B 새 증거와 동시에 전건 직접 처리하고, 검증 가능한 것은 직접 검증·종결한다. 기존 수용 증거·잔여 게이트는 [STATUS](../plan/STATUS.md) 및 RF 원본 참조. **RF-007 신규 유입:** A run109 5일/14거래 synthetic E2E smoke/public-profile exit 0, `apps/web` subtree 동일; exact-SHA CI·소비자 게이트 미충족. 같은 E2E 반복 금지.
- **RF-069:** 승인 historical UEF5 snapshot path/SHA/use-scope 부재로 ENV BLOCKED. 승인 전 fixture·오라클 생성 금지.
- **런검증 #32:** broker/local SELL 누락·stale BUY guard·GREEN 불일치, OCI 실행 SHA 미입증. RunLab read-only provenance, 안전 코드/재배포 무승인 금지.
- **troubleshooting:** open 4 / closed 0; 해제 증거 없으면 이동 금지.

## Claude A — `work/p15-a-reporter-pure-20261021`

**A P0 1순위 — RF-050 신규 원개발** [02_DEVELOPING/CLAUDE_A](../plan/queue/02_DEVELOPING/CLAUDE_A/RF-050.md). 8 `libs/llm/` owner만, `libs/llm/router.py::LLMRouter.chat`, `libs/llm/llm_router.py::LLMRouter.resolve/chat`, `libs/llm/model_catalog.py::{resolve_policy_llm_slot,resolve_model_profile}`의 구형/현재 API consumers와 Commander `applied_policy.llm`→role env→model fallback·동적 import·UI/Reporter/Strategist/스케줄·실제 State/IO를 READ-ONLY로 분류. `ACTIVE/FALLBACK/COMPAT/DORMANT/REMOVE_CANDIDATE/SAFETY_HOLD`별 8 owner 파일 인벤토리. 합성 policy·model name만 `/tmp/rf050_policy_lookup.py` fake/monkeypatch로 사용해 **`python /tmp/rf050_policy_lookup.py`**, **`python -O /tmp/rf050_policy_lookup.py`** 최초 marker/exit·SOURCE_SHA 제출. 실제 OpenRouter/Kiwoom 호출·model default 변경·소스 제거/이동/설정 변경 **승인 전 금지**. 실행 불가면 효과 차단 경계를 적고 static 8파일 소비자를 계속; B가 RF-070 등 새 결과를 낸 경우 RF-050 한정 신규 안전 peer 작업으로 이동.

**A P1 — 기존 B 코드 후속 LEAD 신규 독립 경계 지원** [RF-063](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-063.md) / [RF-067](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-067.md). 기존 diagnostics audit·metrics tmp writer, root check_ 두 wrapper alias/runpy, normal/-O marker는 이미 수용돼 재실행 금지. 새 `scripts/diagnostics/check_alert_policy_v1.py::{_build_parser,_evaluate_alerts}` pure JSON metrics fake 입력과 cp949 decode/encode 사유 분리를 `/tmp/rf063_alert_locale_peer.py`에서 normal/`-O` 최초 테스트하라. `python /tmp/rf063_alert_locale_peer.py` / `python -O /tmp/rf063_alert_locale_peer.py` marker·exit; 실제 `main`/report write/환경·broker 접근 금지. 이후 RF-067 `scripts/check_real_execution_preflight.py` AST-only public consumer/Windows PATH/env timing, broker preflight 실행 금지; 새 safe peer 없으면 RF-050 조사 계속. 기존 RF-065 `--no-fetch` normal/-O·RF-033 capture·RF-032 writer 원개발 재실행 금지.


## Codex B — `work/p15-b-operator-structure-20261022`

**B P0 1순위 — RF-032 LEAD 미충족 신규 write peer** [RF-032](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-032.md). A run108 temp writer 결과를 재실행하지 말고 별도 **`/tmp/rf032_writer_peer.py`**에서 `libs/reporting/evaluation/pipeline.py::build_q9_evaluation`의 **nonempty synthetic trade**, missing/bad rows·예외, 출력 모든 파일의 `resolve().is_relative_to(tmp/reports/evaluation)` 진위, State 불변, tmp outside writes=0을 검증. `python /tmp/rf032_writer_peer.py` / `python -O /tmp/rf032_writer_peer.py` 실제 exit/marker, A source `c3462ec3`·integration blob 제출. `all(... or True...)` 같은 항등참 금지, `recover_forward=True` real fetch/UEF·broker 실행 금지. 불가능한 기능만 SAFETY_HOLD하고 즉시 RF-033.

**B P0 2순위 — RF-033 LEAD 새 capture peer** [RF-033](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-033.md). `libs/reporting/baseline_btc_woori_tech/point_in_time_capture.py::{load_capture_snapshot,load_captured_sources,merge_capture_into_signal_payload}`의 malformed JSON/missing day/duplicate epoch/타임스탬프 문자열 예외와 data_provider consumer 계약을 독립 tmp/no-fetch fake로 `/tmp/rf033_capture_peer.py`에서 처음 확인. `python /tmp/rf033_capture_peer.py` / `python -O /tmp/rf033_capture_peer.py`, marker·exit 및 BASE 동등성. 기존 provider/comparison와 run108 A capture 재실행 금지. `ValueError`가 BASE에도 있으면 신규 CODE REWORK로 기록하지 말고 기존 예외와 하드닝 제안을 분리. 이후 RF-070.

**B P1 3순위 — RF-070** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-070.md). 기존 85/142 wrappers, 25 OTHER+32 safety, AST 41 재실행 금지. 25 OTHER 중 3건(Operator SERVER_BIND, Reporter WRITE, scheduled SCHEDULER) 이미 지팀장 분류 완료. **나머지 22개 정확 경로**별 `__main__/argv/cwd/env`, Windows/Docker/CLI/스케줄 동적 소비자, 효과 token, `ACTIVE/COMPAT/SAFETY_HOLD`, SHA를 채워라. 안전한 parser 최초 신규 mock만 `/tmp/rf070_parser_fake.py`에서 `python /tmp/rf070_parser_fake.py` / `python -O /tmp/rf070_parser_fake.py` marker/exit; 실제 launcher/bind/order/운영 writes 금지. 막히면 RF-066.

**B P1 4순위 — RF-066** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-066.md). 기존 17 AST/OrderClient fake/M22 1 consumer PASS 재사용. 잔여 16 CLI 파일별 호출·error propagation·temp-only 소비자 근거 제출, 새 안전 fake parser만 `python /tmp/rf066_next_parser.py` / `python -O /tmp/rf066_next_parser.py` marker/exit; broker/Step5D/SQLite/운영 sync/delete 금지. 막히면 RF-071.

**B P2 5순위 — RF-071** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-071.md). `scripts/approval_cli.py::main(argv)` 권한 경계 및 root 42 launcher FILE::SYMBOL 정적 분류. `/tmp/rf071_entry_static.py` 최초 추가 순수 parse 소비자만 `python /tmp/rf071_entry_static.py` / `python -O /tmp/rf071_entry_static.py`; 기존 `RF071_ENTRY_STATIC_OK` 동일 하네스 재실행 금지. 승인/cleanup/restart/order main 금지. 이후 [RF-014](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-014.md) Scanner dynamic Top1/p171 fake peer `python /tmp/rf014_scanner_consumer_peer.py` / `python -O /tmp/rf014_scanner_consumer_peer.py`와 [RF-015](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-015.md) Monitor State/event fake peer `python /tmp/rf015_monitor_consumer_peer.py` / `python -O /tmp/rf015_monitor_consumer_peer.py` 신규 경계, 기존 pure 1함수 peer 중복 금지.


## 지팀장 다음 행동

A/B 신규 SHA·[Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32) 인수 → **LEAD 14건 전건 직접 판정/검증/큐 처리** → 허용 source 선별 통합 → troubleshooting → 다음 배정 → STATUS → **CURRENT 마지막 갱신**. 세부 상시 절차는 D00에만 둔다.
