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

## 현재 상태 — 2026-10-30 23:35 KST / RF-035 A8 통합, RF-065 B0 코드 결함 차단

- **정확 통합 코드 SHA:** `06e3904092c1ce8f65a2cef99e74cfab4da650df` (parent `e8296c14979f787269291d1b73de1f46ccf1c841`). 비강제 expected-HEAD fast-forward 성공. A 원격 `4c0db15690c15f8e3609a3d4befa2ee91af0d5f3`, #11 `6525028712`, C02 blob `e26c5c04e3422e3eb2dd987933d6e31a1c55fffc`. 원격 코드/테스트 Git blob **14/14 일치**: SOURCE 2, 신규 Owner 4, 신규 targeted tests 8.
- **A RF-035 BODY MOVE 8:** `daily_report_generator.py` pre `cfcc8fc70cd2b72168dcea4f40a3f01d1b1cdfbf` → `eee37fe6d8c97b23cafbff184142bfcbda4a2944`, `market_regime_rail_review.py` pre `e6cfd5280d597602ba167ec1d3cc5fac29080a3c` → `778c8f2dfc4657a2a5f12e89adca0f55c9a01b23`. `_iter_events`, `_find_trade_dir`, `_broker_closed_symbols_from_alignment`, `_render_residual_positions_markdown` → daily read/trade Owners; `_to_float`, `_indicator`, `_change_pct`, `render_market_regime_rail_markdown` → market scalar/markdown Owners. Exact-signature thin wrappers, call-time facade, target→source 역수입 없음. SOURCE pre-blob integration과 A 주문 일치; 신규 target 4개 통합 전 404.
- **G2/G3:** A worker normal `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_23h_*_owner.py` **31 PASS exit0** (#11 `6525028712`). 동일 14개 code/test blob을 통합했으므로 범위 한정 `G3_REUSE`; C04 직접 pytest 0, 수동 CI 0. Worker 기존 379 PASS/1 SKIP/1 FAIL(UEF5 stdlib import guard, 변경 전에도 FAIL 보고); 이 기존 실패를 신규 RF-035 PASS로 포장하지 않음. Push 자동 CI [#41073424695](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/41073424695) 현재 조회 `completed / success` (정확 code SHA, 자동 push CI; 수동 dispatch 0).
- **B RF-065 B0 차단:** B 원격 `e28d1a9d04ecd497dbce1a85abf9d2cb88dd186c`, #12 `6524800387`. `run_phase5_validation_bundle.py` wrapper와 신규 `phase5_validation_markdown.py`는 원격 G1 코드 2개가 있으나 **SOURCE wrapper가 `phase5_markdown._render_bundle_markdown(...)`을 호출하면서 `phase5_markdown` import/binding 없음 → 실행 시 NameError**. `py_compile exit0`만 보고, 정상 targeted pytest/smoke exit0 없음. **G1 기능 결함 + G2 MISSING → G3 BLOCKED**, B 통합 0. B는 source에 `from scripts.research import phase5_validation_markdown as phase5_markdown` 등 유효 import를 추가하고 fake payload 정상/예외·facade.json/_safe_rel seam parity targeted normal exit0 후 재푸시 필요. B RF-063 이전 `6aa9a0a0` 로컬 tree unavailable, G1 원격 미전달.
- **분리:** REFACTOR_CHANGED=8, TARGET_GAP_CLOSED=8, RF_DONE_DELTA=0. RF-035 기존 DONE이며 마지막 C05 누적 32/93(최신 물리 단계/STATUS C05 판정). RF-016/028/029, RF-051/054/058 동일 SHA 재통합 0. RF-044 전체 facade smoke NOT_VERIFIED. RunLab #32 RUN_SOURCE_SHA UNKNOWN/Exited(255) 안전 HOLD, 실주문·실계좌·운영 배포/재시작 없음.
- **NEXT:** #36에 A exact G3_REUSE, B0 결함과 G1/G2 차단 및 CI 상태 인계; C05 G3/STATUS 판정. B는 RF-065 B0 정상 import/targeted 증거와 RF-063 원격 SHA를 재제출. KEEP/DOCS_ONLY는 신규 pytest/CI 0. 기존 통합 SHA/함수 재반복 금지.
