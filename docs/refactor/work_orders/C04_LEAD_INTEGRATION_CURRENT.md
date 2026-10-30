# C04 — 지팀장 · 선별 통합/CI

## 최신 우선 계약 — 구현 변경 묶음만 통합

C01/C02에서 나온 **실제 함수 이동 source+target blob**과 해당 normal targeted exit를 대조해 여러 준비 RF를 한 회차에 통합. 관련 경계 기존 PASS 증거 재사용, 변경 없는 정당한 KEEP은 새 테스트/CI dispatch 0. T00~T09 및 `rf_details/INDEX.md`의 SOURCE/TARGET Owner와 교차 RF 신규 경로 충돌 점검. 아래 이미 DONE인 RF-016/028/029 등 고정 반복 통합 지시는 신규 delta 없으면 적용 금지. 실거래/운영 효과 보호.


## FAST-3 G3 재실행 중복 방지 — C04 실제 판단 절차
- **1단계 대상 검증:** RF의 G1 원격 OWNER SOURCE SHA와 integration의 실제 파일별 Git blob을 대조하고, G2의 정확 SOURCE SHA·영향 테스트/실제 exit0 증거를 확인한다. 단순 문서 HEAD 변경으로 `SOURCE_CHANGED`를 판단하지 않는다.
- **2단계 증거 재사용:** 같은 대상 source+consumer 경계, 동일 테스트·의존성·CI 워크플로 상태에 대해 이미 성공한 정상 smoke/targeted pytest 또는 exact relevant CI 증거가 있으면 `G3_REUSE`로 수용한다. SOURCE 또는 테스트/의존성/보호 경계가 바뀌었으면 관련 범위만 재검증한다. 이전 기록의 PASS가 현재 코드에 해당하는지 불명확하면 재사용 불가, 하지만 full suite로 확대하지 않는다.
- **3단계 명시적 분기:** `KEEP_BLOB_IDENTICAL + VALID_RELEVANT_EVIDENCE` ⇒ **새 CI/pytest 실행 요청 0**, C05에 G3 증거 전달. `SOURCE_CHANGED` 또는 `TEST/DEPENDENCY/WORKFLOW_CHANGED` ⇒ 대상 변경분을 최소 통합하고 **관련 smoke/pytest 1회 또는 유효한 CI 1개** 확인. `DOCS_STATUS_ONLY` ⇒ **신규 CI dispatch 0 / smoke 반복 0**. `NO_MATCHING_EVIDENCE` ⇒ targeted smoke 1회만 실행(실행 환경 부재 시 G3 BLOCKED, 성공으로 간주 금지).
- **4단계 중복 dispatch 락:** 실제 GitHub Actions 수동 dispatch 이전 **기존 run의 head SHA, workflow/테스트 범위, conclusion을 조회**하고, 동등하게 성공한 run이나 같은 범위의 진행 중 run이 있으면 또 요청하지 않는다. 한 번 실행한 후 해당 `RF | owner blobs | integration/source SHA | relevant test list | PASS/FAIL | run_id 또는 local command | reuse/new/blocked` 근거를 #36 한 번만 보고한다. `python -O`/full hosted CI는 FAST-3 강제요건 아님.
- GitHub Actions `push` 트리거/branch protection·workflows·frozen oracle는 변경하지 않는다. 현재 `.github/workflows/p15-shared-candidate.yml`은 코드/테스트 변경 Push에서 자동 실행될 수 있으므로 이것을 삭제/비활성화한다고 주장하지 않는다. **중복 수동 실행 요청만 차단**하고 정상적인 자동 안전 CI는 유지한다.

## FAST-3 간소 통합 우선 (2026-10-29 승인)
- D00 §2 FAST-3가 아래 구 C1~C7/full independent C4/매 RF 전체 hosted normal/-O CI 요구보다 우선한다. **G1/G2 MET인 RF를 G3로 처리**한다. C05의 과거 7개 전수 수용을 기다리지 말고 실제 새로운 G1/G2 상태를 원격에서 확인한다.
- KEEP이면 해당 코드의 integration blob 동일성 확인 후 기존 정상 smoke/CI evidence 1개로 G3 제출 가능. 변경 있으면 최소 파일 선택 통합 후 **변경 경계 관련 smoke/pytest 1회** 또는 해당 integration SHA의 기존 관련 CI 성공으로 G3 제출한다. 전체 suite, -O 반복, 반대 전체 peer, 새 hosted CI 매번 강제하지 않는다.
- RF-016/028/029 및 RF-051/054/058은 DONE이므로 동일 SHA 재검증·재통합 금지. 새 C01/C02 G1/G2 실제 SOURCE와 RF Owner를 우선하고, 통합 결과 없으면 G3를 꾸며내지 않고 BLOCKED(scope/명령/NEXT). #36에는 신규 근거만 제출.
- mock/paper 실행은 모의 모드·계정이 확인된 환경에서만, 실제 런검증은 별도 단계. 실계좌 real mode는 무승인 실행 금지.

**입력:** [Issue #11 Claude A](https://github.com/hbombheart1230-dotcom/agentra/issues/11) · [Issue #12 Codex B](https://github.com/hbombheart1230-dotcom/agentra/issues/12) · [Issue #32 RunLab](https://github.com/hbombheart1230-dotcom/agentra/issues/32)의 **새 댓글 delta만** → C05가 실제 `04_LEAD_ACCEPTANCE`로 이동한 RF. [D00](D00_ENGINEERING_DELIVERY_POLICY.md) 준수. [#36](https://github.com/hbombheart1230-dotcom/agentra/issues/36)은 결과 출력 전용. 오래된 A/B HANDOFF 재독·갱신 금지.

## 현재 상태 — 2026-10-31 00:35 KST / RF-035 A8 통합, B RF-065/063 차단 유지

- **정확 통합 코드 SHA:** `e0619a434f20acf2fd3b31e19c24db685f81e5aa` (parent `26f4fd5f60ae25a7699f28253b45ccc1e6bfba18`, tree `fbd89068b272088967bd08a4b77ba0e82dd6aecc`). Expected-head 비강제 fast-forward 성공, 원격 HEAD 재조회 성공. A remote `78662483e7e50a7445b4a18f5979b55c82bd74c9`, #11 `6526411008`, C02 blob `f48f7859ee0cd8ee8ceac9110a2426217ec23875`. **정확 actor/integration Git blob 21/21:** SOURCE 5, 신규 Owner 8, 신규 targeted tests 8. integration의 SOURCE pre-blob 다섯 개가 C02/A 이전 blob과 일치했고 8 Owner target은 사전 부재. 다른 A 브랜치 변경을 통째로 병합하지 않음.
- **RF-035 실제 BODY MOVE 8:** `daily_report_generator._build_trade_report_integrity` → `daily_report_generator_integrity_projection`; `metrics_report_generator._iter_events` → `metrics_report_generator_read_projection`; `llm_daily_summary._build_messages` → `llm_daily_summary_message_projection`; `strategist_llm_summary._utc_now_iso` → `strategist_llm_summary_clock_projection`; `market_regime_rail_review.load_latest_macro_snapshot` → `market_regime_rail_review_read_projection`; `strategist_llm_summary.render_strategist_llm_summary_markdown` (active last definition only) → `strategist_llm_summary_render_projection`; `daily_report_generator._load_operator_summary_snapshot` → `daily_report_generator_operator_projection`; `llm_daily_summary._is_dry_run` → `llm_daily_summary_env_projection`. 원래 함수 시그니처의 얇은 wrapper와 호출 시 facade helper resolution 보존; 이전 shadowed markdown definition 보존, metrics UTF-8 BOM 보존.
- **G2/G3:** A worker normal `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_00h_*_owner.py` **40 PASS exit0** (#11 `6526411008`); 해당 코드/테스트 정확 21개 blob을 통합하여 **G3_REUSE (scoped)**. C04 직접 pytest 0회, 수동 CI dispatch 0. A의 기존 광역 검사 807 PASS / 1 SKIP / 1 FAIL(기존 UEF5 guard)은 신규 targeted 40 PASS와 별도. 정확 코드 SHA push-trigger 자동 CI [#41082724587](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/41082724587) 마지막 조회 **in_progress**, conclusion 미확정; 수동 중복 실행 금지.
- **B RF-065 B0:** B remote `e28d1a9d04ecd497dbce1a85abf9d2cb88dd186c` 변경 없음, #12 마지막 `6524800387`. `run_phase5_validation_bundle._render_bundle_markdown`가 미import `phase5_markdown` 호출 → runtime NameError, 정상 targeted exit0 없음 (py_compile만). C01 blob `c4c9f73944d504f529267d09ef17312eab690bc6`는 import+fake parity 수정 주문, 실제 수정 원격 미도착. **G1 기능 BLOCKED/G2 MISSING/G3 NOT_INTEGRATED**. RF-063 B1–B9도 원격 신규 구현 미도착; old local-only `6aa9a0a0`은 G1 아님. B 통합 0.
- **성과/보호:** REFACTOR_CHANGED=8, TARGET_GAP_CLOSED=8, RF_DONE_DELTA=0 (RF-035 기존 DONE). C05 최신 확인 누적 DONE 32/93; C05만 물리 단계/STATUS 변경. RF-016/028/029 및 RF-051/054/058 동일 SHA 재통합 0. RF-044 facade-call smoke NOT_VERIFIED. RunLab Exited(255), RUN_SOURCE_SHA UNKNOWN 별도 운영 SAFETY_HOLD. 실주문/실계좌/운영 재시작·배포/보호 Broker·Guard·Step5C·UEF 변경 0.
- **NEXT:** 신규 B 원격 code/test SHA 및 정상 targeted exit0가 제출되면 RF-065 import 결함과 RF-063 각 함수 소유권을 재판정하고 선별 통합. A의 동일 21 blob 반복 통합/pytest/CI 금지. G3 정확 코드 SHA·21/21 blob·40 PASS 재사용·B 차단을 #36으로 C05 인계. C04 문서 변경은 새 pytest/수동 CI 트리거 0.
