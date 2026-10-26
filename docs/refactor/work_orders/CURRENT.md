# Agentra P1.5 — CURRENT

**정본:** `hbombheart1230-dotcom/agentra` / `integration/p1.5`
**운영:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) · **RF:** [물리 큐](../plan/queue/) · **집계:** [STATUS](../plan/STATUS.md)

**이 브랜치의 CURRENT만 지시 정본이다.** A/B는 자신의 브랜치 CURRENT·구 HANDOFF의 지시를 사용하지 않는다. D00 및 아래 배정 RF만 필요 시 읽어라. 같은 SHA·같은 경계 반복 검증·ACK 문서로 종료하지 마라.


## 상시 실행·작성 규칙 — 지팀장/A/B 공통

**지팀장은 앞으로도 CURRENT를 매번 구체적인 명령문으로 작성하라.** 각 작업에 반드시 담당자, 우선순위, 지금 실행할 RF, 정확한 대상 파일/함수, 검증할 신규 경계, 정상/-O 명령과 exit, 제출 산출물, 막혔을 때 다음 RF를 명시하라. '검토 필요'·'진행 예정'·'결정 대기'만 써 놓고 작업 지시라고 하지 마라. **'확인하라 → 분류하라 → 수정하거나 KEEP하라 → 검증하라 → SHA·exit를 제출하라 → 다음 RF를 실행하라'**로 써라.

**A/B는 지시를 받으면 실제 실행하라.** 매번 integration/p1.5의 최신 CURRENT·HEAD를 읽고 자기 배정 RF만 수행하라. 기존 유효 SHA·동일 테스트는 재실행하지 마라. 앞 작업이 BASELINE/ENV/SAFETY/동결 오라클 때문에 막히면 그 원인과 해제 조건을 적고 즉시 다음 안전한 RF를 수행하라. 소스 수정이 가능하면 실제 commit+normal/-O 증거를, KEEP이면 파일별 소비자·IO/State·예외 근거를, peer면 처음 보는 경계의 독립 증거를 제출하라. ACK·HANDOFF 문서만 수정하고 종료하지 마라.

**지팀장은 이미 나온 증거의 RF 판정·큐 이동·소스 통합을 개발자에게 되돌리지 마라.** 직접 ACCEPT/HOLD/KEEP/FIX/PEER/REWORK/INTEGRATE를 결정하고 물리 큐를 갱신하라. 다음 배정을 확정한 뒤 CURRENT를 마지막에 고쳐라. 이 상시 지시형 운영 규칙을 이후 CURRENT 개정에서도 반드시 유지하라.

## Claude A — `work/p15-a-reporter-pure-20261021`

**인수 완료·재실행 금지:** run106 RF-033 provider `fg=12 dp=21`; run107 RF-067 두 root wrapper, RF-065 agent-effectiveness scorecard, RF-063 metrics schema CLI normal/-O exit 0은 지팀장이 수용했다. **RF-067은 LEAD로 이동**, A는 동일 wrapper peer 재실행 금지. RF-063 metrics CLI는 쓰기형(tmp-only)이지 read-only가 아니다. RF-030 `03b255e5` frozen RF-074 충돌 후보는 통합 금지 HOLD.

**1순위 — RF-033 잔여 원개발 IO 경계** [03_PEER_REVIEW/CODEX_B](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-033.md). `libs/reporting/baseline_btc_woori_tech/point_in_time_capture.py::merge_capture_into_signal_payload` → `load_capture_snapshot/load_captured_sources`를 **synthetic tmp root, 기존 08:55 capture·깨진 JSON·누락 day·중복 epoch·malformed ts**로 최초 확인. `capture_q12_btc_0855_snapshot` 실제 fetch/쓰기 호출 금지. 입력 payload 불변·읽기 경로·fallback_reason·예외 전파 분류. `python /tmp/rf033_capture_owner.py` / `python -O /tmp/rf033_capture_owner.py` marker·exit·SOURCE_SHA·BASE 차분 제출. 네트워크/브로커/운영 root 차단. 이건 **A 원개발 추가 증거**이지 B 독립 peer 대체가 아니다. 위험하면 HOLD 후 RF-032.

**2순위 — RF-032 평가 writer 효과 경계** [03_PEER_REVIEW/CODEX_B](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-032.md). `libs/reporting/evaluation/pipeline.py::{_write_json,_write_text,build_q9_evaluation}` AST/read-only로 먼저 쓰기·호출·`recover_forward=True`의 `allow_fresh_fetch=True`를 분리. **절대 fresh fetch 실행 금지**; safe `recover_forward=False` + fake dependencies + tmp-root-only write가 증명될 때만 `python /tmp/rf032_writer_owner.py` / `python -O /tmp/rf032_writer_owner.py` 첫 정상/최적화 exit·marker·tmp 밖 쓰기 0 제출. 불가 시 SAFETY_HOLD 후 RF-065.

**3순위 — RF-065 잔여 연구 CLI** [04_LEAD_ACCEPTANCE/FROM_CODEX_B](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-065.md). `scripts/research/run_alpha_hypothesis_competition.py::main`→`libs.research.alpha_competition.run_alpha_hypothesis_competition`을 AST-only로 우선 분류; 기본 fetch=True이므로 직접 main 실행 금지. `--no-fetch`·fake dependency·tmp-only 출력 효과가 안전할 때만 `python /tmp/rf065_alpha_cli_peer.py` / `python -O /tmp/rf065_alpha_cli_peer.py` 신규 marker/exit·효과 0 제출. 막히면 RF-007 ENV 상태 기록 후 다음 안전한 RF.

**A 제출:** 실제 SOURCE_SHA, 최초 미검증 경계·normal/-O 명령/exit·효과 차단·CODE/BASELINE/ENV/SAFETY, KEEP/FIX/HOLD. Issue #11/HANDOFF는 결과만, RF 큐·CURRENT 직접 수정 금지. 반복 없이 다음 RF 연속 진행.

## Codex B — `work/p15-b-operator-structure-20261022`

**1순위 — RF-031 A KEEP 독립 peer** [03_PEER_REVIEW/CODEX_B](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-031.md). A 22/22 BASE 동일, 13 frozen HOLD, 9 FIX 미입증, 56 BASELINE/CROSS_RF FAIL은 인수 완료. `libs/reporting/reporter_analysis.py::generate_reporter_analysis_report`의 `_iter_jsonl`→tmp `write_text`→feedback State/예외 순서를 먼저 정적 확인하고 합성 temp logs + fake feedback/LLM/운영 쓰기 차단 하네스 `python /tmp/rf031_peer_boundary.py` / `python -O /tmp/rf031_peer_boundary.py` **최초 독립** 실행, marker/exit·입력 불변·IO/예외 제출. 쓰기 차단 불가면 `trade_report_ai._router_chat_with_hard_timeout` fake timeout/exception 경계만; 둘 다 위험하면 SAFETY_HOLD 후 **RF-033**.

**2순위 — RF-033 A 45-owner KEEP 독립 peer** [03_PEER_REVIEW/CODEX_B](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-033.md). A `RF033_BOUNDARY_OK` 반복 금지. `libs/reporting/baseline_btc_woori_tech/comparison.py::build_comparison`의 missing/malformed summary·`_read` 깨진 JSON, `forward_returns.py::{attach_forward_returns,summarize}`의 입력 State 불변·Q9 early-return/no-fetch를 **새 fake 입력 조합**에서 `python /tmp/rf033_b_peer.py` / `python -O /tmp/rf033_b_peer.py` marker/exit·SOURCE_SHA 제출. network/broker/운영 쓰기 차단. 막히면 **RF-034**.

**3순위 — RF-034 A 40-owner KEEP 독립 peer** [03_PEER_REVIEW/CODEX_B](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-034.md). `libs/reporting/alpha_research_board/canonical.py::{_normalize_status,_fixed_validation_status,_production_promotion_status,canonicalize_board}`의 `window_complete='no'` truthy 현상은 생산자 `runtime_validation.py` bool 계약과 구별해 BASELINE_DESIGN vs CODE 판정; 합성 14행·missing stage2·State 불변을 `python /tmp/rf034_b_peer.py` / `python -O /tmp/rf034_b_peer.py` marker/exit로 최초 독립 확인. A 임시 patch 재적용·frozen RF-074 변경 금지. 막히면 **RF-032**.

**4순위 — RF-032 A 135-owner KEEP 독립 peer** [03_PEER_REVIEW/CODEX_B](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-032.md). `libs/reporting/evaluation/artifact_inventory.py::is_regular_session_evaluation_row`의 malformed `generated_at` fail-open/naive UTC 및 `build_artifact_inventory` tmp read-only, `attribution_score_v0.py::_selection_integrity` 비숫자 예외를 `python /tmp/rf032_b_peer.py` / `python -O /tmp/rf032_b_peer.py` 최초 독립 검증, marker/exit·SOURCE_SHA 제출. 29 write owner·UEF 안전/동결 계약 실행·수정 금지. 막히면 **RF-070**.

**5순위 — RF-070 자체 원개발** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-070.md). 기존 85/142 mock·25 OTHER/32 SAFETY_HOLD 정적 반복 금지. `scripts/run_operator_ui.py::_parse_args/main`, `run_reporter_analysis_report.py::_build_parser/main`, `run_scheduled_intelligence.py::main`을 첫 AST-only/no-import/no-main 대상으로 `python /tmp/rf070_static_dispositions.py` / `python -O /tmp/rf070_static_dispositions.py` marker/exit 제출; 나머지 22 OTHER 파일별 argv/cwd/env/caller/IO/State/exception KEEP/HOLD 25행 완성. 서버 bind/운영 쓰기·스케줄러·32 위험 launcher 직접 실행 금지. 막히면 **RF-066**.

**6순위 — RF-066 자체 후속** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-066.md). 기존 fake OrderClient request4/error1/temp1 normal/-O PASS 반복 금지. `scripts/examples/demo_m22_skill_flow.py` 및 `scripts/maintenance/` 잔여 16 owner 소비자/CLI/IO·예외를 파일별 분류, 첫 순수 fake 경계 `python /tmp/rf066_next_consumer.py` / `python -O /tmp/rf066_next_consumer.py` marker/exit. broker/order/SQLite/외부 catalog sync 금지. 막히면 **RF-071**.

**7순위 — RF-071** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-071.md). `scripts/analyze_entry_blockers.py`, `benchmark_operator_visibility_memory.py`, `approval_cli.py::main(argv)`의 AST-only wrapper/권한/효과 구별, `python /tmp/rf071_entry_static.py` / `python -O /tmp/rf071_entry_static.py` marker/exit. 실제 승인·cleanup·restart·주문 명령 금지. 이어서 peer **RF-016→014→015**의 CURRENT 기존 범위 중 최초 미검증 안전 함수로 진행(상대 peer 동일 SHA 반복 금지).

**B 제출:** RF별 exact SOURCE_SHA, 신규 독립 normal/-O marker·exit, fake 입력·효과 차단, 파일별 KEEP/FIX/HOLD, CODE/BASELINE/ENV/UNKNOWN 분류, 다음 RF. Issue #12/HANDOFF는 결과 제출만, CURRENT·큐 변경 금지. RF-001 exact `b5fe3dd9` 787×2 PASS 및 RF-028 use-time peer는 이미 수용·재실행 금지. 시간 상한 없음.

## 지팀장 — `integration/p1.5`

**이번 회차 실제 판정:** A run106/107의 신규 증거를 직접 인수. **RF-067을 PEER_REVIEW/CLAUDE_A → LEAD_ACCEPTANCE/FROM_CODEX_B로 물리 이동**, `PEER_SCOPED_ACCEPTED / KEEP_NOOP_CANDIDATE / NOT_DONE`. RF-063/065는 신규 tmp-only 쓰기형 CLI 경계를 추가 수용, RF-033 provider는 A 원개발 증거로만 수용(B peer 대기). B HEAD `5fb0e131` 신규 소스·peer 0, 현재 B 1순위 RF-031 유지. 코드 선별 통합 후보 없음(새 source 0; RF-030 frozen FAIL 후보 제외), DONE 0, REWORK 0.

**RF-067 남은 인수 게이트:** 14 owner 공개 CLI 전체의 Windows PATH/Task Scheduler 소비자, 안전 preflight 효과, 최신 integration exact SHA/hosted CI. A가 검증한 두 wrapper를 재실행하지 않는다. 지팀장이 전체 계약 충족 증거를 직접 판정할 때까지 LEAD HOLD.

**런검증 #32:** broker SELL 원인 UNKNOWN, local/broker mismatch, stale BUY guard, image source SHA 미입증은 환경·미확정 코드 후보. 원인 재현 전 코드 REWORK·거래 안전 수정·운영 재배포 금지. `troubleshooting/open` 4건은 종료조건 미충족, `closed` 0건.

**물리 큐(이동 후):** PENDING 62 / DEVELOPING 3 / PEER_REVIEW 9 / LEAD_ACCEPTANCE 8 / REWORK 0 / DONE 11 = 93. 부분 PASS·NOT_RUN ≠ DONE. 지팀장 자체 latest integration exact-SHA hosted CI NOT_RUN.

**다음 지팀장 루프:** integration CURRENT 단독 시작 → A/B HEAD·신규 evidence 및 #32 확인 → 새로운 peer RF 직접 판정·원자 이동 → 소스 delta가 있을 때만 frozen/peer/patchnotes 검증 후 허용 파일 선별 통합 → open/closed 실제 종료만 이동 → STATUS 동기화 → CURRENT 마지막 갱신. main·실거래·거래 안전·동결 테스트/CI·예약 무승인 변경 금지.
