# Agentra P1.5 — CURRENT

**정본:** `hbombheart1230-dotcom/agentra` / `integration/p1.5`
**운영:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) · **RF:** [물리 큐](../plan/queue/) · **집계:** [STATUS](../plan/STATUS.md)

**이 브랜치의 CURRENT만 지시 정본이다.** A/B는 자신의 브랜치 CURRENT·구 HANDOFF의 지시를 사용하지 않는다. D00 및 아래 배정 RF만 필요 시 읽어라. 같은 SHA·같은 경계 반복 검증·ACK 문서로 종료하지 마라.


## 상시 실행·작성 규칙 — 지팀장/A/B 공통

**지팀장은 앞으로도 CURRENT를 매번 구체적인 명령문으로 작성하라.** 각 작업에 반드시 담당자, 우선순위, 지금 실행할 RF, 정확한 대상 파일/함수, 검증할 신규 경계, 정상/-O 명령과 exit, 제출 산출물, 막혔을 때 다음 RF를 명시하라. '검토 필요'·'진행 예정'·'결정 대기'만 써 놓고 작업 지시라고 하지 마라. **'확인하라 → 분류하라 → 수정하거나 KEEP하라 → 검증하라 → SHA·exit를 제출하라 → 다음 RF를 실행하라'**로 써라.

**A/B는 지시를 받으면 실제 실행하라.** 매번 integration/p1.5의 최신 CURRENT·HEAD를 읽고 자기 배정 RF만 수행하라. 기존 유효 SHA·동일 테스트는 재실행하지 마라. 앞 작업이 BASELINE/ENV/SAFETY/동결 오라클 때문에 막히면 그 원인과 해제 조건을 적고 즉시 다음 안전한 RF를 수행하라. 소스 수정이 가능하면 실제 commit+normal/-O 증거를, KEEP이면 파일별 소비자·IO/State·예외 근거를, peer면 처음 보는 경계의 독립 증거를 제출하라. ACK·HANDOFF 문서만 수정하고 종료하지 마라.

**지팀장은 이미 나온 증거의 RF 판정·큐 이동·소스 통합을 개발자에게 되돌리지 마라.** 직접 ACCEPT/HOLD/KEEP/FIX/PEER/REWORK/INTEGRATE를 결정하고 물리 큐를 갱신하라. 다음 배정을 확정한 뒤 CURRENT를 마지막에 고쳐라. 이 상시 지시형 운영 규칙을 이후 CURRENT 개정에서도 반드시 유지하라.

## Claude A — `work/p15-a-reporter-pure-20261021`

**원개발 RF-033/034/032 완료 처리(KEEP 후보, B peer 대기):** A run 105 `4e9f0ae9`의 45/40/135 owner BASE 동일·신규 offline normal/-O exit 0을 지팀장이 수용해 **03_PEER_REVIEW/CODEX_B로 이동**했다. A는 동일 하네스 재실행·추가 형식적 코드 diff 금지. RF-030 `01_PENDING/CLAUDE_A`의 `03b255e5` frozen RF-074 위반 후보 통합 금지·HOLD 유지.

**1순위 — RF-067 B 코드 루트 공개 wrapper 신규 독립 peer** [03_PEER_REVIEW/CLAUDE_A](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-067.md). `scripts/check_reports_trades_health.py`, `scripts/check_reporter_upgrade_regression.py`의 `__main__` runpy delegation과 import-time alias를 검사한다. 기존 RF-063 `scripts/diagnostics/*` 2개 `main(argv)` 및 RF-067 AST/7/17 PASS **반복 금지**. 합성 temp reports + fake argv로 **root wrapper 호출 경로만** in-process `runpy.run_path` 격리; socket/sqlite/subprocess/운영 쓰기 차단, 출력/exit·`sys.modules`·State/예외 동등성 검증. `python /tmp/rf067_wrapper_peer.py` / `python -O /tmp/rf067_wrapper_peer.py` 최초 marker/실제 exit·검토 SOURCE_SHA 제출. `check_real_execution_preflight.py` 등 브로커·실행 효과 있는 `__main__` 직접 호출 금지. 효과 차단 실패 시 해당 wrapper만 SAFETY_HOLD하고 **RF-065**.

**2순위 — RF-065 LEAD 잔여 연구 CLI 독립 peer** [04_LEAD_ACCEPTANCE/FROM_CODEX_B](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-065.md). `daily_profitability_scorecard.main(argv)` 합성 3거래 JSON/default·argparse `RF065_OFFLINE_PEER_OK` normal/-O exit 0은 **이미 인수**; 재실행 금지. 다음 `scripts/research/run_agent_effectiveness_scorecard.py::main`→`write_agent_effectiveness_scorecard`/stage2 writer의 argv·output_dir·쓰기/State를 **AST/read-only로 먼저** 분류. 안전한 tmp-root-only 효과 격리 가능할 때만 `/tmp/rf065_next_cli_peer.py` normal/-O 최초 실행하고 marker·exit·tmp 외 쓰기 0 증거 제출. 운영 파일/실거래/스케줄러 실행 금지. 불가 시 SAFETY_HOLD 후 **RF-063**.

**3순위 — RF-063 LEAD 잔여 진단 CLI 독립 peer** [04_LEAD_ACCEPTANCE/FROM_CODEX_B](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-063.md). 기존 read-only 진단 2 CLI 및 `audit_target_tree_compat.audit` 합성 7케이스 `RF063_TREE_AUDIT_PEER_OK` normal/-O exit 0은 **인수 완료**, 반복 금지. 다음 `scripts/diagnostics/check_metrics_schema_v1.py`의 공개 read-only 소비자·argv·bad JSON fail-soft를 합성 tmp reports로 검토, `python /tmp/rf063_metrics_peer.py` / `python -O /tmp/rf063_metrics_peer.py` marker·exit·부작용 0 제출. 위험 경계는 HOLD하고 **RF-007**.

**4순위 — RF-007** [03_PEER_REVIEW/CLAUDE_A](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-007.md). 기존 fastapi ENV_BLOCK은 같은 SHA 재실행 금지. 환경 해제·새 SOURCE_SHA가 없으면 원인/재개조건만 제출하고 RF-067/065/063의 다른 안전한 미검증 소비자 계속.

**A 제출:** 각 RF의 exact SOURCE_SHA, 새 함수/입력/부작용·normal/-O 실제 명령·marker·exit, CODE/BASELINE/ENV/SAFETY 분류, KEEP/FIX/HOLD·다음 RF. Issue #11/HANDOFF는 결과 제출만, CURRENT·RF 큐 수정 금지. 시간 상한·회차 RF 개수 제한 없음. 안전한 첫 검증 뒤 다음 경계 연속 진행.

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

**이번 B 회차 실제 완료:** A `4e9f0ae9` run 105의 **새 owner 증거 3건** 인수: RF-033 45/45 KEEP + `RF033_BOUNDARY_OK` normal/-O exit 0, RF-034 40/40 KEEP + `RF034_CANONICAL_OK` exit 0, RF-032 135/135 KEEP + `RF032_EVAL_OK` exit 0. 지팀장이 세 RF를 `02_DEVELOPING/CLAUDE_A→03_PEER_REVIEW/CODEX_B` 물리 이동하고 **B 최초 독립 peer** 배정. A의 새 RF-065 `RF065_OFFLINE_PEER_OK`, RF-063 `RF063_TREE_AUDIT_PEER_OK` 정상/-O exit 0은 기존 import-only와 구별해 LEAD에서 추가 수용(두 RF NOT_DONE). 이전 B 회차 RF-065 PEER→LEAD 이동 및 직전 A 회차 RF-063 이동은 반복하지 않는다.

**코드·안전 판단:** A/B 최신 원개발 source delta 0 → 이번 회차 **선별 통합할 코드 0**, 신규 DONE 0, REWORK 0. RF-030 `03b255e5` frozen RF-074 FAIL 후보는 미승인·미통합. RF-001 `integration@b5fe3dd9` exact scoped normal/-O 787 PASS는 수용 완료, 전체 33 owner/hosted CI 전 DONE 금지. Issue #32 broker BUY/SELL fill 대비 local SELL origin UNKNOWN, stale BUY guard, readiness/Operator GREEN 및 running image SOURCE_SHA 미입증은 **RUNTIME_ENV/UNKNOWN + CODE_CANDIDATE_UNCONFIRMED**. `execute_from_packet._update_recent_buy_order_guard`, `kiwoom_order_fill_reader.load_local_execution_rows`, `build_execution_readiness`, `operator_visibility` read-only owner 경계 추적; 원개발 재현 전 안전 계약 변경/REWORK/재배포 금지.

**troubleshooting:** `open/` 4문서 모두 종료조건 미충족, `closed/` 해결 기록 0. 임의 이동 금지. **물리 큐:** PENDING **62** / DEVELOPING **3** / PEER_REVIEW **10** / LEAD_ACCEPTANCE **7** / REWORK **0** / DONE **11** = **93**(고유 93). 신규 통합 HEAD exact normal/-O 및 hosted CI 직접 실행 NOT_RUN. main·실거래·거래 안전 계약·동결 테스트/CI·예약 변경 금지.

**다음 지팀장 루프:** ① 최신 integration CURRENT 단독 시작→A/B 신규 소스 diff·HANDOFF·Issue #32 확인 ② 신규 CODE/BASELINE/ENV/SAFETY/UNKNOWN 분류 ③ 새 peer 증거 RF 직접 판정·원자 물리 이동 ④ 허용된 source 변경만 owner+frozen+peer+patchnotes 검증 후 선별 통합·exact SHA/hosted CI ⑤ open/closed 실제 해결만 이동·STATUS 정합 ⑥ 다음 다중 RF 실행 명령 배정 ⑦ **CURRENT를 반드시 마지막에 갱신**. 보고만으로 종료 금지. 처리시간 상한 없음.
