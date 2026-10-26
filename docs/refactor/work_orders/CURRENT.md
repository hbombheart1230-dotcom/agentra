# Agentra P1.5 — CURRENT

**정본:** `hbombheart1230-dotcom/agentra` / `integration/p1.5`
**운영:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) · **RF:** [물리 큐](../plan/queue/) · **집계:** [STATUS](../plan/STATUS.md)

**이 브랜치의 CURRENT만 지시 정본이다.** A/B는 자신의 브랜치 CURRENT·구 HANDOFF의 지시를 사용하지 않는다. D00 및 아래 배정 RF만 필요 시 읽어라. 같은 SHA·같은 경계 반복 검증·ACK 문서로 종료하지 마라.


## 상시 실행·작성 규칙 — 지팀장/A/B 공통

**지팀장은 앞으로도 CURRENT를 매번 구체적인 명령문으로 작성하라.** 각 작업에 반드시 담당자, 우선순위, 지금 실행할 RF, 정확한 대상 파일/함수, 검증할 신규 경계, 정상/-O 명령과 exit, 제출 산출물, 막혔을 때 다음 RF를 명시하라. '검토 필요'·'진행 예정'·'결정 대기'만 써 놓고 작업 지시라고 하지 마라. **'확인하라 → 분류하라 → 수정하거나 KEEP하라 → 검증하라 → SHA·exit를 제출하라 → 다음 RF를 실행하라'**로 써라.

**A/B는 지시를 받으면 실제 실행하라.** 매번 integration/p1.5의 최신 CURRENT·HEAD를 읽고 자기 배정 RF만 수행하라. 기존 유효 SHA·동일 테스트는 재실행하지 마라. 앞 작업이 BASELINE/ENV/SAFETY/동결 오라클 때문에 막히면 그 원인과 해제 조건을 적고 즉시 다음 안전한 RF를 수행하라. 소스 수정이 가능하면 실제 commit+normal/-O 증거를, KEEP이면 파일별 소비자·IO/State·예외 근거를, peer면 처음 보는 경계의 독립 증거를 제출하라. ACK·HANDOFF 문서만 수정하고 종료하지 마라.

**지팀장은 이미 나온 증거의 RF 판정·큐 이동·소스 통합을 개발자에게 되돌리지 마라.** 직접 ACCEPT/HOLD/KEEP/FIX/PEER/REWORK/INTEGRATE를 결정하고 물리 큐를 갱신하라. 다음 배정을 확정한 뒤 CURRENT를 마지막에 고쳐라. 이 상시 지시형 운영 규칙을 이후 CURRENT 개정에서도 반드시 유지하라.

## 지팀장 P0 — LEAD_ACCEPTANCE 병목 직접 소진 (2026-10-26)

**담당: 지팀장 / 신규 A·B 배정보다 우선.** 물리 `04_LEAD_ACCEPTANCE` 12건 전수 경로와 SHA를 열거해 기존 원개발·독립 peer·normal/-O·소비자/IO/State·예외·exact integration SHA·CI 증거로 **각각 직접** ACCEPT/DONE, HOLD, REWORK 판정하라. A/B에게 최종 판정을 재위임하지 않는다. 재검증은 새로운 위험 경계에만 허용한다. KEEP_NOOP도 전체 owner·공개 소비자·CI 게이트 충족 시 DONE 가능하며, 부분 PASS·NOT_RUN은 DONE 금지. 최종 통과 건은 `05_DONE`으로 단일 물리 경로 이동하고 STATUS를 동기화하라. 이동 후 93 RF 고유 ID/누락/중복 0 및 정확한 integration SHA 확인. 막힌 건은 누락 게이트와 해제 조건을 RF별 기록하고 즉시 다음 LEAD RF 판정으로 전환하라.

**기존 확인된 HOLD:** RF-008 standalone/외부 read-only fail-soft 및 BASE 기존 FAIL, RF-028 85-owner 소비자/효과, RF-029 38-owner 소비자/CI, RF-063 진단 CLI 효과/locale, RF-065 연구 CLI 효과/locale, RF-067 14-owner Windows PATH·Scheduler/preflight. RF-001의 과거 exact `b5fe3dd9` 787×2 PASS는 재실행하지 않되 현행 SHA/hosted CI 범위를 구별한다. 남은 LEAD 경로도 전수 확인한다. #32 SELL provenance·BUY guard·reconciliation/Operator GREEN·image SHA는 런환경/미확정 후보로만 보존하고 안전 계약/배포/REWORK 무승인 변경 금지.

**회차 종료조건:** 실제 RF 판정 및 가능한 물리 이동·선별 통합 먼저, open/closed troubleshooting의 종료 증거 확인, STATUS 변경 시 갱신, A/B 신규 안전 경계 재배정, CURRENT **마지막 갱신**. 이동·통합 0이면 그 원인과 해제 조건을 명시하고 EXECUTION_INCOMPLETE 보고. 기존 valid normal/-O·peer 재실행 금지.

## 지팀장 B 슬롯 최신 결정 — 4 RF peer 수용 후 LEAD 12건 (2026-10-26)

**완료:** B Issue #12 RUN B-20261026T093354Z의 RF-031 fake timeout/exception, RF-033 malformed summary/Q9 no-fetch, RF-034 truthy/stage2, RF-032 malformed time/tmp inventory 독립 normal/-O exit 0을 지팀장이 직접 PEER_SCOPED_ACCEPTED 판정. **RF-031/033/034/032를 `03_PEER_REVIEW/CODEX_B` → `04_LEAD_ACCEPTANCE/FROM_CLAUDE_A` 물리 이동**하고 이전 파일 4건 부재 확인. 4건 전부 KEEP_NOOP_CANDIDATE/NOT_DONE. 소스 통합 0, DONE 0. **큐:** PENDING 62 / DEVELOPING 3 / PEER 5 / LEAD 12 / REWORK 0 / DONE 11 = 93(전체 경로 전수 NOT_RUN). STATUS 갱신 완료. RF-030 frozen FAIL 후보 통합 금지.

**지팀장 다음 P0:** LEAD 12건 각각 기존 SOURCE_SHA/독립 peer/소비자·IO·예외/normal·-O/exact integration SHA·hosted CI 완료 여부를 직접 분류하고, 충분한 증거를 가진 RF만 DONE으로 물리 이동. 현재 RF-031/032/033/034는 신규 독립 scoped peer는 충족했지만 전체 owner 효과·hosted CI 미충족이므로 HOLD; 기존 marker 반복 금지. 기존 8 LEAD도 누락 게이트별 판정하라. 전체 93 물리 경로 중복·누락 0은 아직 NOT_RUN이므로 반드시 검사. Issue #32 미확정 SELL provenance·stale guard·GREEN/reconciliation mismatch 및 OCI SHA는 CODE REWORK 단정 금지. open/closed troubleshooting 현행 listing API 오류로 전수 NOT_RUN, 기존 open4/closed0의 해결 증거 없음·이동 없음.

**A 즉시 실행:** RF-033 `point_in_time_capture.py::merge_capture_into_signal_payload` 합성 tmp·no-fetch 최초 경계 `python /tmp/rf033_capture_owner.py` / `python -O /tmp/rf033_capture_owner.py` exit/marker/SOURCE_SHA 제출, 위험 시 RF-032 `evaluation/pipeline.py::_write_json/_write_text` AST+tmp-only 효과 경계로 이동. **B 즉시 실행:** 기존 RF-031/033/034/032 peer marker 재실행 금지. RF-070 25 OTHER 정적 분류를 파일별 ACTIVE/COMPAT/SAFETY_HOLD로 마무리하되 실제 main/bind/scheduler 실행 금지, `python /tmp/rf070_static_dispositions.py` / `python -O /tmp/rf070_static_dispositions.py` 최초 미검증 경계만 marker/exit 제출. 막히면 RF-066 17 owner 중 최초 안전 fake parser 경계로 전환. A/B는 RF 최종 판정/큐 이동을 하지 않는다.

## Claude A — `work/p15-a-reporter-pure-20261021`

**인수 완료·재실행 금지:** run106 RF-033 provider `fg=12 dp=21`; run107 RF-067 두 root wrapper, RF-065 agent-effectiveness scorecard, RF-063 metrics schema CLI normal/-O exit 0은 지팀장이 수용했다. **RF-067은 LEAD로 이동**, A는 동일 wrapper peer 재실행 금지. RF-063 metrics CLI는 쓰기형(tmp-only)이지 read-only가 아니다. RF-030 `03b255e5` frozen RF-074 충돌 후보는 통합 금지 HOLD.

**1순위 — RF-033 잔여 원개발 IO 경계** [03_PEER_REVIEW/CODEX_B](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-033.md). `libs/reporting/baseline_btc_woori_tech/point_in_time_capture.py::merge_capture_into_signal_payload` → `load_capture_snapshot/load_captured_sources`를 **synthetic tmp root, 기존 08:55 capture·깨진 JSON·누락 day·중복 epoch·malformed ts**로 최초 확인. `capture_q12_btc_0855_snapshot` 실제 fetch/쓰기 호출 금지. 입력 payload 불변·읽기 경로·fallback_reason·예외 전파 분류. `python /tmp/rf033_capture_owner.py` / `python -O /tmp/rf033_capture_owner.py` marker·exit·SOURCE_SHA·BASE 차분 제출. 네트워크/브로커/운영 root 차단. 이건 **A 원개발 추가 증거**이지 B 독립 peer 대체가 아니다. 위험하면 HOLD 후 RF-032.

**2순위 — RF-032 평가 writer 효과 경계** [03_PEER_REVIEW/CODEX_B](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-032.md). `libs/reporting/evaluation/pipeline.py::{_write_json,_write_text,build_q9_evaluation}` AST/read-only로 먼저 쓰기·호출·`recover_forward=True`의 `allow_fresh_fetch=True`를 분리. **절대 fresh fetch 실행 금지**; safe `recover_forward=False` + fake dependencies + tmp-root-only write가 증명될 때만 `python /tmp/rf032_writer_owner.py` / `python -O /tmp/rf032_writer_owner.py` 첫 정상/최적화 exit·marker·tmp 밖 쓰기 0 제출. 불가 시 SAFETY_HOLD 후 RF-065.

**3순위 — RF-065 잔여 연구 CLI** [04_LEAD_ACCEPTANCE/FROM_CODEX_B](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-065.md). `scripts/research/run_alpha_hypothesis_competition.py::main`→`libs.research.alpha_competition.run_alpha_hypothesis_competition`을 AST-only로 우선 분류; 기본 fetch=True이므로 직접 main 실행 금지. `--no-fetch`·fake dependency·tmp-only 출력 효과가 안전할 때만 `python /tmp/rf065_alpha_cli_peer.py` / `python -O /tmp/rf065_alpha_cli_peer.py` 신규 marker/exit·효과 0 제출. 막히면 RF-007 ENV 상태 기록 후 다음 안전한 RF.

**후속 슬롯(현재 미활성) — RF-050 LLM 퇴역 판단** [01_PENDING/UNASSIGNED](../plan/queue/01_PENDING/UNASSIGNED/RF-050.md). 현재 A의 RF-067→065→063→007에서 안전하게 가능한 새 경계를 먼저 수행하라. **지팀장이 물리 큐를 02_DEVELOPING/CLAUDE_A로 옮겨 정식 배정하기 전에는 RF-050 원개발·소스 수정 실행 금지.** 정식 배정되면 `libs/llm/{router.py,llm_router.py,model_catalog.py,model_catalog_store.py,model_names.py,json_response.py,openrouter_client.py,__init__.py}` 8 Owner의 public/static/dynamic/env/scheduler 소비자·fallback·IO/State/예외를 처음 조사한다. 첫 경계 `router.py::LLMRouter.chat/ModelSpec` vs `llm_router.py::LLMRouter.resolve/chat`, `model_catalog.py::resolve_policy_llm_slot`; synthetic offline read-only harness `/tmp/rf050_retirement_boundary.py` 생성 후 `python /tmp/rf050_retirement_boundary.py` / `python -O /tmp/rf050_retirement_boundary.py`, 최초 marker/exit, FILE::SYMBOL별 ACTIVE/FALLBACK/COMPAT/DORMANT/REMOVE_CANDIDATE/SAFETY_HOLD·SOURCE_SHA 제출. 실제 provider·주문·운영 파일·동결 오라클·모델 교체 금지; 외부 소비자 불확실 시 HOLD하고 이후 안전한 RF 계속. **별도 사용자 승인 전 실제 삭제 금지**.


**A 제출:** 실제 SOURCE_SHA, 최초 미검증 경계·normal/-O 명령/exit·효과 차단·CODE/BASELINE/ENV/SAFETY, KEEP/FIX/HOLD. Issue #11/HANDOFF는 결과만, RF 큐·CURRENT 직접 수정 금지. 반복 없이 다음 RF 연속 진행.

## Codex B — `work/p15-b-operator-structure-20261022`

**1순위 — RF-031 A KEEP 독립 peer** [03_PEER_REVIEW/CODEX_B](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-031.md). A 22/22 BASE 동일, 13 frozen HOLD, 9 FIX 미입증, 56 BASELINE/CROSS_RF FAIL은 인수 완료. `libs/reporting/reporter_analysis.py::generate_reporter_analysis_report`의 `_iter_jsonl`→tmp `write_text`→feedback State/예외 순서를 먼저 정적 확인하고 합성 temp logs + fake feedback/LLM/운영 쓰기 차단 하네스 `python /tmp/rf031_peer_boundary.py` / `python -O /tmp/rf031_peer_boundary.py` **최초 독립** 실행, marker/exit·입력 불변·IO/예외 제출. 쓰기 차단 불가면 `trade_report_ai._router_chat_with_hard_timeout` fake timeout/exception 경계만; 둘 다 위험하면 SAFETY_HOLD 후 **RF-033**.

**2순위 — RF-033 A 45-owner KEEP 독립 peer** [03_PEER_REVIEW/CODEX_B](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-033.md). A `RF033_BOUNDARY_OK` 반복 금지. `libs/reporting/baseline_btc_woori_tech/comparison.py::build_comparison`의 missing/malformed summary·`_read` 깨진 JSON, `forward_returns.py::{attach_forward_returns,summarize}`의 입력 State 불변·Q9 early-return/no-fetch를 **새 fake 입력 조합**에서 `python /tmp/rf033_b_peer.py` / `python -O /tmp/rf033_b_peer.py` marker/exit·SOURCE_SHA 제출. network/broker/운영 쓰기 차단. 막히면 **RF-034**.

**3순위 — RF-034 A 40-owner KEEP 독립 peer** [03_PEER_REVIEW/CODEX_B](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-034.md). `libs/reporting/alpha_research_board/canonical.py::{_normalize_status,_fixed_validation_status,_production_promotion_status,canonicalize_board}`의 `window_complete='no'` truthy 현상은 생산자 `runtime_validation.py` bool 계약과 구별해 BASELINE_DESIGN vs CODE 판정; 합성 14행·missing stage2·State 불변을 `python /tmp/rf034_b_peer.py` / `python -O /tmp/rf034_b_peer.py` marker/exit로 최초 독립 확인. A 임시 patch 재적용·frozen RF-074 변경 금지. 막히면 **RF-032**.

**4순위 — RF-032 A 135-owner KEEP 독립 peer** [03_PEER_REVIEW/CODEX_B](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-032.md). `libs/reporting/evaluation/artifact_inventory.py::is_regular_session_evaluation_row`의 malformed `generated_at` fail-open/naive UTC 및 `build_artifact_inventory` tmp read-only, `attribution_score_v0.py::_selection_integrity` 비숫자 예외를 `python /tmp/rf032_b_peer.py` / `python -O /tmp/rf032_b_peer.py` 최초 독립 검증, marker/exit·SOURCE_SHA 제출. 29 write owner·UEF 안전/동결 계약 실행·수정 금지. 막히면 **RF-070**.

**5순위 — RF-070 자체 원개발** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-070.md). 기존 85/142 mock·25 OTHER/32 SAFETY_HOLD 정적 반복 금지. `scripts/run_operator_ui.py::_parse_args/main`, `run_reporter_analysis_report.py::_build_parser/main`, `run_scheduled_intelligence.py::main`을 첫 AST-only/no-import/no-main 대상으로 `python /tmp/rf070_static_dispositions.py` / `python -O /tmp/rf070_static_dispositions.py` marker/exit 제출; 나머지 22 OTHER 파일별 argv/cwd/env/caller/IO/State/exception KEEP/HOLD 25행 완성. 서버 bind/운영 쓰기·스케줄러·32 위험 launcher 직접 실행 금지. 막히면 **RF-066**.

**6순위 — RF-066 자체 후속** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-066.md). 기존 fake OrderClient request4/error1/temp1 normal/-O PASS 반복 금지. `scripts/examples/demo_m22_skill_flow.py` 및 `scripts/maintenance/` 잔여 16 owner 소비자/CLI/IO·예외를 파일별 분류, 첫 순수 fake 경계 `python /tmp/rf066_next_consumer.py` / `python -O /tmp/rf066_next_consumer.py` marker/exit. broker/order/SQLite/외부 catalog sync 금지. 막히면 **RF-071**.

**7순위 — RF-071** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-071.md). `scripts/analyze_entry_blockers.py`, `benchmark_operator_visibility_memory.py`, `approval_cli.py::main(argv)`의 AST-only wrapper/권한/효과 구별, `python /tmp/rf071_entry_static.py` / `python -O /tmp/rf071_entry_static.py` marker/exit. 실제 승인·cleanup·restart·주문 명령 금지. 이어서 peer **RF-016→014→015**의 CURRENT 기존 범위 중 최초 미검증 안전 함수로 진행(상대 peer 동일 SHA 반복 금지).

**신규 보강 — RF-070 퇴역 분류 및 RF-050 후속 독립 peer.** 현재 B 순서 RF-031→033→034→032→070→066→071 및 최초 독립 normal/-O는 그대로 유지한다. RF-031의 기존 B peer를 완료한 뒤, RF-070에서 `run_operator_ui.py::_parse_args/main`, `run_reporter_analysis_report.py::_build_parser/main`, `run_scheduled_intelligence.py::main`의 공개 CLI/argv/cwd/env/Windows Scheduler·Docker·UI 소비자와 부작용을 `/tmp/rf070_static_dispositions.py`에서 AST-only로 구분하고 `python /tmp/rf070_static_dispositions.py` / `python -O /tmp/rf070_static_dispositions.py` marker/exit·25행 추가 분류를 제출한다. 32 위험 launcher 실행/예약 변경 금지; UNKNOWN이면 COMPAT/SAFETY_HOLD 후 RF-066. RF-050이 **A 정식 배정·후보 제출 및 지팀장 peer 명령을 받은 이후에만** B가 기존 증거 반복 없이 `router.py` legacy raw response→현행 text router와 primary/fallback 우선순위의 새로운 synthetic peer를 `/tmp/rf050_b_peer.py`에서 정상/-O 각 실행하고 marker/exit/source SHA 제출한다. RF-050 원개발 owner 파일 수정 및 사용자 미승인 삭제 금지.


**B 제출:** RF별 exact SOURCE_SHA, 신규 독립 normal/-O marker·exit, fake 입력·효과 차단, 파일별 KEEP/FIX/HOLD, CODE/BASELINE/ENV/UNKNOWN 분류, 다음 RF. Issue #12/HANDOFF는 결과 제출만, CURRENT·큐 변경 금지. RF-001 exact `b5fe3dd9` 787×2 PASS 및 RF-028 use-time peer는 이미 수용·재실행 금지. 시간 상한 없음.

## 지팀장 — `integration/p1.5`

**이번 회차 실제 판정:** A run106/107의 신규 증거를 직접 인수. **RF-067을 PEER_REVIEW/CLAUDE_A → LEAD_ACCEPTANCE/FROM_CODEX_B로 물리 이동**, `PEER_SCOPED_ACCEPTED / KEEP_NOOP_CANDIDATE / NOT_DONE`. RF-063/065는 신규 tmp-only 쓰기형 CLI 경계를 추가 수용, RF-033 provider는 A 원개발 증거로만 수용(B peer 대기). B HEAD `5fb0e131` 신규 소스·peer 0, 현재 B 1순위 RF-031 유지. 코드 선별 통합 후보 없음(새 source 0; RF-030 frozen FAIL 후보 제외), DONE 0, REWORK 0.

**RF-067 남은 인수 게이트:** 14 owner 공개 CLI 전체의 Windows PATH/Task Scheduler 소비자, 안전 preflight 효과, 최신 integration exact SHA/hosted CI. A가 검증한 두 wrapper를 재실행하지 않는다. 지팀장이 전체 계약 충족 증거를 직접 판정할 때까지 LEAD HOLD.

**런검증 #32:** broker SELL 원인 UNKNOWN, local/broker mismatch, stale BUY guard, image source SHA 미입증은 환경·미확정 코드 후보. 원인 재현 전 코드 REWORK·거래 안전 수정·운영 재배포 금지. `troubleshooting/open` 4건은 종료조건 미충족, `closed` 0건.

**과거 회차 물리 큐(역사값):** PENDING 62 / DEVELOPING 3 / PEER_REVIEW 9 / LEAD_ACCEPTANCE 8 / REWORK 0 / DONE 11 = 93. 현행 값은 위 최신 결정 참조. 부분 PASS·NOT_RUN ≠ DONE. 지팀장 자체 latest integration exact-SHA hosted CI NOT_RUN.

**승인 문서 반영(2026-10-26):** D00 §3A + RF-050/031/070/090 퇴역 게이트를 사용자 승인에 따라 문서로만 반영. SOURCE 삭제/선별 통합 0, 보호 계약·CI·예약·운영 모델 변경 0. 기존 RF 93개와 11 DONE, 신규 A/B 증거 인수 및 RF 기존 우선순위는 유지한다. RF-050/090은 PENDING, RF-031 peer 및 RF-070 기존 개발이 우선. **지팀장 다음 실제 행동:** A/B 신규 diff·런검증을 먼저 판정 → 신규 안전한 RF 검증·통합 → RF-070 최초 퇴역 소비자 근거 인수 → A의 기존 RF 우선 범위 소진 시 RF-050을 물리 큐 이동해 최초 LLM 후보 분류 배정 → SOURCE 삭제는 개별 사용자 승인·독립 peer·정확 통합 SHA CI 확인 후에만. CURRENT 갱신은 이번 문서 커밋의 마지막 작성 대상으로 둔다.


**다음 지팀장 루프:** integration CURRENT 단독 시작 → A/B HEAD·신규 evidence 및 #32 확인 → 새로운 peer RF 직접 판정·원자 이동 → 소스 delta가 있을 때만 frozen/peer/patchnotes 검증 후 허용 파일 선별 통합 → open/closed 실제 종료만 이동 → STATUS 동기화 → CURRENT 마지막 갱신. main·실거래·거래 안전·동결 테스트/CI·예약 무승인 변경 금지.
