# Agentra P1.5 — CURRENT (최신 실행 정본)

**정본:** `integration/p1.5`의 이 파일. **상시 규칙/LEAD 자동 처리 의무:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md). 여기에는 **최신 큐·A/B 실행 지시·이번 회차 예외만** 남긴다. 작업 브랜치 CURRENT 사용 금지.

## 현재 큐·지팀장 우선 처리

- **물리 큐:** PENDING 61 / DEVELOPING 4 / PEER_REVIEW 2 / LEAD_ACCEPTANCE 15 / REWORK 0 / DONE 11 = **93**, 중복·누락 0 (최근 원격 tree 확인).
- **LEAD 15건:** RF-001/007/008/014/016/028/029/031/032/033/034/063/065/067/069. 지팀장은 A/B 새 증거와 동시에 전건 직접 처리하고, 검증 가능한 것은 직접 검증·종결한다. 기존 수용 증거·잔여 게이트는 [STATUS](../plan/STATUS.md) 및 RF 원본 참조. **RF-007 신규 유입:** A run109 5일/14거래 synthetic E2E smoke/public-profile exit 0, `apps/web` subtree 동일; exact-SHA CI·소비자 게이트 미충족. 같은 E2E 반복 금지.
- **RF-069:** 승인 historical UEF5 snapshot path/SHA/use-scope 부재로 ENV BLOCKED. 승인 전 fixture·오라클 생성 금지.
- **런검증 #32:** broker/local SELL 누락·stale BUY guard·GREEN 불일치, OCI 실행 SHA 미입증. RunLab read-only provenance, 안전 코드/재배포 무승인 금지.
- **troubleshooting:** open 4 / closed 0; 해제 증거 없으면 이동 금지.

## Claude A — `work/p15-a-reporter-pure-20261021`

**A P0 1순위 — RF-050 신규 원개발** [02_DEVELOPING/CLAUDE_A](../plan/queue/02_DEVELOPING/CLAUDE_A/RF-050.md). 8 `libs/llm/` owner만, `libs/llm/router.py::LLMRouter.chat`, `libs/llm/llm_router.py::LLMRouter.resolve/chat`, `libs/llm/model_catalog.py::{resolve_policy_llm_slot,resolve_model_profile}`의 구형/현재 API consumers와 Commander `applied_policy.llm`→role env→model fallback·동적 import·UI/Reporter/Strategist/스케줄·실제 State/IO를 READ-ONLY로 분류. `ACTIVE/FALLBACK/COMPAT/DORMANT/REMOVE_CANDIDATE/SAFETY_HOLD`별 8 owner 파일 인벤토리. 합성 policy·model name만 `/tmp/rf050_policy_lookup.py` fake/monkeypatch로 사용해 **`python /tmp/rf050_policy_lookup.py`**, **`python -O /tmp/rf050_policy_lookup.py`** 최초 marker/exit·SOURCE_SHA 제출. 실제 OpenRouter/Kiwoom 호출·model default 변경·소스 제거/이동/설정 변경 **승인 전 금지**. 실행 불가면 효과 차단 경계를 적고 static 8파일 소비자를 계속; B가 RF-070 등 새 결과를 낸 경우 RF-050 한정 신규 안전 peer 작업으로 이동.

**A P1 — 기존 B 코드 후속 LEAD 신규 독립 경계 지원** [RF-063](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-063.md) / [RF-067](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-067.md). 기존 diagnostics audit·metrics tmp writer, root check_ 두 wrapper alias/runpy, normal/-O marker는 이미 수용돼 재실행 금지. 새 `scripts/diagnostics/check_alert_policy_v1.py::{_build_parser,_evaluate_alerts}` pure JSON metrics fake 입력과 cp949 decode/encode 사유 분리를 `/tmp/rf063_alert_locale_peer.py`에서 normal/`-O` 최초 테스트하라. `python /tmp/rf063_alert_locale_peer.py` / `python -O /tmp/rf063_alert_locale_peer.py` marker·exit; 실제 `main`/report write/환경·broker 접근 금지. 이후 RF-067 `scripts/check_real_execution_preflight.py` AST-only public consumer/Windows PATH/env timing, broker preflight 실행 금지; 새 safe peer 없으면 RF-050 조사 계속. 기존 RF-065 `--no-fetch` normal/-O·RF-033 capture·RF-032 writer 원개발 재실행 금지.


## Codex B — `work/p15-b-operator-structure-20261022`

**B 완료 증거(재실행 금지):** RF-032 신규 nonempty writer peer `RF032_WRITER_PEER_OK`와 RF-033 malformed capture peer `RF033_CAPTURE_PEER_OK` normal/-O exit0는 지팀장이 LEAD 범위 한정 수용했다(B HANDOFF `f19d3a12`). 두 RF 모두 29 write-owner/UEF 및 45 owner 소비자·exact SHA gate 때문에 NOT_DONE. 같은 하네스·경계 반복 금지.

**B P0 1순위 — RF-070** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-070.md). 기존 85/142 wrappers, 25 OTHER+32 safety, AST 41 재실행 금지. 25 OTHER 중 3건(Operator SERVER_BIND, Reporter WRITE, scheduled SCHEDULER) 이미 지팀장 분류 완료. **나머지 22개 정확 경로**별 `__main__/argv/cwd/env`, Windows/Docker/CLI/스케줄 동적 소비자, 효과 token, `ACTIVE/COMPAT/SAFETY_HOLD`, SHA를 채워라. 안전한 parser 최초 신규 mock만 `/tmp/rf070_parser_fake.py`에서 `python /tmp/rf070_parser_fake.py` / `python -O /tmp/rf070_parser_fake.py` marker/exit; 실제 launcher/bind/order/운영 writes 금지. 막히면 RF-066.

**B P0 2순위 — RF-066** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-066.md). 기존 17 AST/OrderClient fake/M22 1 consumer PASS 재사용. 잔여 16 CLI 파일별 호출·error propagation·temp-only 소비자 근거 제출, 새 안전 fake parser만 `python /tmp/rf066_next_parser.py` / `python -O /tmp/rf066_next_parser.py` marker/exit; broker/Step5D/SQLite/운영 sync/delete 금지. 막히면 RF-071.

**B P1 3순위 — RF-071** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-071.md). `scripts/approval_cli.py::main(argv)` 권한 경계 및 root 42 launcher FILE::SYMBOL 정적 분류. `/tmp/rf071_entry_static.py` 최초 추가 순수 parse 소비자만 `python /tmp/rf071_entry_static.py` / `python -O /tmp/rf071_entry_static.py`; 기존 `RF071_ENTRY_STATIC_OK` 동일 하네스 재실행 금지. 승인/cleanup/restart/order main 금지. 이후 [RF-015](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-015.md) 새 `RF015_MONITOR_CONSUMER_OK` marker를 재실행하지 말고 detached peer가 B-only `libs/agents/monitor/{__init__,contracts}.py` 2개를 import했는지 exact blob/AST 근거로 분리, 역사 11 FAIL의 BASE 동등성만 새로 검증해 제출. [RF-014](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-014.md)는 지팀장이 LEAD로 이동했으므로 기존 `RF014_SCANNER_CONSUMER_OK` Top1 fake 반복 금지; 미검증 dynamic ranking/reject/NOOP와 RF-009/019/030/035/074 교차 소비자만 안전 read-only로 분리.


## 이번 회차 인수·지팀장 직접 판정 (2026-10-26 20시 KST)

- **A HEAD** `07de339f`: RF-007 E2E 이미 수용, 신규 운영 source SHA 없음. **B HEAD** `f19d3a12`: RF-032 writer, RF-033 capture, RF-014 Scanner, RF-015 Monitor 최초 scoped fake peer normal/-O exit0 인수. 신규 운영 source commit 없음. B 브랜치 Monitor 2개 추가 파일은 integration/BASE에 없으므로 무승인 통합 금지.
- **RF-014 실제 물리 이동:** `03_PEER_REVIEW/CODEX_B → 04_LEAD_ACCEPTANCE/FROM_CLAUDE_A`, commit `e3d71e16`. BASE 동일 역사 실패·B 신규 Top1 peer 수용, `KEEP_SCOPED / CROSS_RF_HISTORICAL_HOLD / NOT_DONE`. RF-015는 독립 peer 부분 PASS만 수용, 추가 import 경계·11 FAIL 해소 전 PEER 유지. RF-032/033은 새 writer/capture peer 범위 해소, LEAD/NOT_DONE 유지. 기타 LEAD 12건 기존 HOLD 유지; 새 증거 없는 동일 검증 금지.
- **원격 검증:** RF 93 고유/단일 경로, PENDING 61 / DEVELOPING 4 / PEER 2 / LEAD 15 / DONE 11. 신규 DONE 0, 신규 source 선별 통합 0, exact HEAD CI NOT_RUN. Troubleshooting open 4 / closed 0(해제 증거 없음). Issue #32 SELL origin·BUY guard·OCI SHA UNKNOWN 유지, 코드 REWORK/재배포 금지.
- **지팀장 다음 최초 실행:** LEAD 15건에서 증거 충족 게이트 직접 종결 우선. 특히 RF-014 Scanner dynamic consumer/owner cross-RF, RF-032 29 writer 나머지, RF-033 45 owner consumer 및 exact-SHA CI를 분리해 검증. A는 RF-050, B는 RF-070→RF-066→RF-071→RF-015 신규 경계. STATUS 최신 판정 정본 참조.

## 지팀장 다음 행동

A/B 신규 SHA·[Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32) 인수 → **LEAD 14건 전건 직접 판정/검증/큐 처리** → 허용 source 선별 통합 → troubleshooting → 다음 배정 → STATUS → **CURRENT 마지막 갱신**. 세부 상시 절차는 D00에만 둔다.
