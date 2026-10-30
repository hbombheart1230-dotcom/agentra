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

## 현재 상태 — 2026-10-31 06:35 KST / A RF-035 +8, B RF-065 +1 및 RF-063 +4 선별 통합

- **정확 코드 통합 SHA:** A 최소 통합 `0188e86361a7039ea0501cc0243b1b71a7dca766` → B 선별 통합 `d740171137776296be62ae9cc90d5357da51a35b` (tree `4e4c11209711103dc9a83df3fc37da46fd97c00b`). 각각 expected-head non-force fast-forward 성공. A 14/14, B 7/7, 총 **21/21 원격 Git blob 일치**. 전체 Actor 브랜치 병합 아님.
- **A RF-035:** #11 6533638180, A remote `8bca83003ddb9bb753535f059d9a99b85f054297`, C02 order blob `3cc2763655f94f5a1b272599b5576dfd9d798914`. `libs/reporting/intraday_trade_reports.py` SOURCE blob `819ce8b8`→`2876a230`, Owner 5개에 8 실제 함수 BODY MOVE, 신규 targeted tests 8. A normal targeted `python3 -m pytest -q -p no:cacheprovider tests/test_p15_rf035_06h_*_owner.py` **26 PASS exit0** (#11); fake/tmp/golden/parity. Wide regression 220 PASS/2 FAIL, 두 실패는 A의 baseline 재현 보고(전체 green 주장 금지). C04 직접 pytest=0, manual CI=0.
- **B RF-065 (B0):** #12 6533774550, B remote `5773c4a30ffdead13108f62bb8c8182b9c1909af`. 기존 원본 `run_phase5_validation_bundle.py::_render_bundle_markdown`의 실제 BODY 제거→B owner `phase5_validation_markdown.py`에 단일화, 정확 B thin wrapper와 누락 `phase5_markdown` import를 통합 원본에 최소 패치. 다른 B branch read/CLI refactor를 끌어오지 않음. 통합 SOURCE blob `1beb655b` (actor full-source blob과 다름, 선택 함수/Owner 동일).
- **B RF-063 (B6+B7–B9):** `check_trade_report_runtime_regression.py::_build_parser` 실제 BODY 제거→`trade_artifact_validation_cli.py` 단일 Owner (통합 SOURCE blob `dc882aa5`, B full-source와 다름); `query_strategist_llm_events.py`의 `_to_float/_infer_call_kind/_filtered_events` 실제 BODY 3개→`strategist_event_query_projection.py` (actor SOURCE/Owner 정확 blobs). B normal `python -m unittest tests/test_p15_rf063_21h_owner_smoke.py -v` **3 PASS exit0** (#12); pytest unavailable, stdlib unittest 허용. B source selected 7 files (2 independently patched source, 1 exact source, Owner3, test1) **7/7 remote blob verified**. C04 새 targeted=0; relevant B normal evidence reuse. Exact merged-source test/CI 최종 결과는 별도 확인.
- **B 보류:** RF-063 B5 `validate_trade_artifact_chain`은 Actor remote에 `_legacy_validate_trade_artifact_chain` 이름으로 기존 계산 몸체가 `raise` 뒤에 잔존해 **실제 SOURCE body removal 조건 불충족**; 이 함수와 B1–B4 미검증 범위는 선별 통합하지 않음. B5 제거·정상 targeted 재증명 요청. RF-044 facade smoke NOT_VERIFIED.
- **CI:** 정확 통합 코드 SHA `d7401711` 자동 push [GitHub Actions #41131991422](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/41131991422) `completed` / **SUCCESS** (정확 코드 SHA 확인). 수동 CI dispatch 0, -O/full-suite 반복 0. G3는 G2 scoped reuse로 C05에 인계; C05가 최종 수용/STATUS 판정.
- **성과:** `REFACTOR_CHANGED=13` (A8+B5) / `TARGET_GAP_CLOSED=13` (C05 판정 전 잠정) / `RF_DONE_DELTA=0` (C05 전담). RF-035 기존 DONE, RF-016/028/029/051/054/058 동일 SHA 재통합 0. RunLab #32 latest 6520075820: Exited(255), RUN_SOURCE_SHA UNKNOWN, operational SAFETY_HOLD 유지. 실계좌·실주문·운영 재시작/배포·Broker/Guard/Step5C/UEF 변경 0.
- **NEXT:** C05가 A8/B5 scoped G3를 수용할지 판정; B는 RF-063 B5 중복 계산 제거와 B1–B4의 정확 targeted G2 증거 확보, RF-044 facade smoke. C04는 준비된 신규 delta만 추가 통합하고 C04 문서 외 다른 담당 문서·STATUS 변경 금지.
