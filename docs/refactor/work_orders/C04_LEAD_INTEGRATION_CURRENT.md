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

## 현재 상태 — 2026-10-31 02:35 KST / RF-035 A8 통합, B G2 보류

- **정확 통합 코드 SHA:** `f76df062880918d86766f2f41e5a7d5cdb033669` (parent `cd6236fc026b330c455e91aa3e410bf6a5f41dc3`, tree `5b373e482a5ef647d52fe003e0652c874ec16948`). Expected-head 비강제 fast-forward 성공, 원격 코드/테스트 blob **15/15 일치**. A remote `42240ee55417386f9553ba91f66e5630a88ff682`, #11 comment `6528880739`, C02 order blob `3c45c1aa74ab439df1b0ff2c4da4c37321f43178`. SOURCE `daily_report_runtime/markdown.py` pre-blob `0ed16b2f3d77ed675de1acdbfa5507e4bf53edad`, `trade_explain.py` pre-blob `86418b535aa76bb6a8dc88f1beb9a0809a7bc0f3` both identical on integration before merge. New Owner 5 + targeted tests 8 previously 404. A 전체 브랜치 병합 없이 15 blob만 선별 반영.
- **RF-035 실제 BODY MOVE 8:** `daily_report_runtime/markdown.render_daily_markdown` → `markdown_daily_full_projection.render_daily_markdown`; `trade_explain._safe_int`, `_safe_float`, `_utc_day` → `trade_explain_scalar_projection`; `trade_explain.official_trade_explain_report_dir`, `build_trade_explain_output_path_metadata` → `trade_explain_path_projection`; `trade_explain._iter_jsonl` → `trade_explain_read_projection`; `trade_explain._report_inventory` → `trade_explain_inventory_projection`. SOURCE는 원 시그니처 얇은 wrapper, 기존 facade/monkeypatch 경계 보존. Target는 단일 계산 Owner; real order/운영 효과 없음.
- **G2/G3:** A worker `python3 -m pytest -q -p no:cacheprovider tests/test_p15_rf035_02h_*_owner.py` **normal 32 PASS exit0** (#11 `6528880739`), fake/golden/negative/facade parity. Exact 15 blob selective integration으로 scoped **G3_REUSE**. C04 직접 pytest 0회, 수동 CI dispatch 0. A broader 560 PASS/1 SKIP/3 FAIL은 worker 보고상 기존 재현 실패(UEF5 guard, target tree discipline, python3 executable-name); targeted 32 PASS와 혼동 금지. Exact code SHA의 push-trigger CI는 초기 조회에서 아직 run 없음; 결과 **NOT_VERIFIED**, 수동 중복 dispatch 금지.
- **B RF-063:** B remote HEAD `851085321f46dc9f51fa51a27145a9be001b6a25` unchanged; `_read_json` 1함수 partial remote BODY MOVE는 신규 targeted normal exit0 및 #12 보고 없어 **G2 NOT_VERIFIED / G3 NOT_INTEGRATED**. B2–B9 미완료.
- **B RF-065:** B SOURCE `run_phase5_validation_bundle.py` blob `f7ce771eca2286bd6d647641a001f06f0932193c` unchanged, unimported `phase5_markdown` runtime NameError; **G3 BLOCKED**. C01 B0 import+fake parity test 요구 유효.
- **성과/보호:** REFACTOR_CHANGED=8, TARGET_GAP_CLOSED=8, RF_DONE_DELTA=0 (RF-035 기존 DONE). C05 마지막 확인 누적 DONE 32/93; C05만 STATUS/단계 변경. RF-016/028/029 및 RF-051/054/058 동일 SHA 재통합 0. RF-044 full facade smoke NOT_VERIFIED. RunLab Exited(255)/RUN_SOURCE_SHA UNKNOWN 별도 SAFETY_HOLD. 실계좌/실주문/운영 재시작·배포/보호 Broker·Guard·Step5C·UEF 변경 0.
- **NEXT:** B RF-065 import/normal targeted와 RF-063 원격 code+test SHA·exit0 확보 시 최소 G3 통합. A 동일 15 blob 반복 통합/pytest/수동 CI 금지. #36에 G3 정확 SHA·15/15 blob·32 PASS 재사용·B 차단 인계. 문서 전용 변경 CI/pytest 0.
