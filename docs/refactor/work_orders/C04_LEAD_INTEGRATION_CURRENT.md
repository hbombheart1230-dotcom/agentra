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

## 현재 할 일 — 2026-10-30 04:3x KST / A15·B3 신규 SOURCE 선별 통합

- **통합 완료:** [code `aae2685ab63754392ca208eca3377d9eba819bdc`](https://github.com/hbombheart1230-dotcom/agentra/commit/aae2685ab63754392ca208eca3377d9eba819bdc), parent `a040fc01759665fab2a7ef92dbb24634b89d31ff`, expected-head non-force fast-forward. 총 16 code/test paths: A facade 1+Owner 6+tests 6, B facade 1+Owner 1+test 1. 원격 16/16 blob 일치 확인. RF/STATUS/workflow/운영 변경 0.
- **A / RF-031 기존 DONE의 추가 TARGET_GAP 6:** [#11 6506098018](https://github.com/hbombheart1230-dotcom/agentra/issues/11#issuecomment-6506098018), source `5b145b149f3ac315a57cb7bd21f93cc75d287c12`. `libs/reporting/reporter_feedback.py`의 `_extract_route_summary/_extract_blocker_totals/_extract_freshness/_extract_reporter_analysis_blocker_totals/_build_dominant_patterns/_build_recommendations` 실제 본문을 각 `reporter_feedback_{route_summary,blocker_totals,freshness,analysis_blockers,dominant_patterns,recommendations}.py` 단일 Owner로 MOVE, facade thin wrapper 유지. integration 13/13 A source/test blobs 동일, pre-source blob `90a6f54e` 동일. A normal targeted **65 PASS exit0**, 기존 관련 **326 PASS** (작업자 보고), direct `libs/core/evidence_identity.py`와 pytest.ini/requirements.txt blob 동일. **G3_REUSE scoped**; 기존 RF-031 DONE 유지, 신규 DONE 0.
- **B / RF-008 pure B3 함수만:** [#12 6505986022](https://github.com/hbombheart1230-dotcom/agentra/issues/12#issuecomment-6505986022), B source `914ab22f4a434bd951a8061d5fe489e1f22ee3e6`. `graphs/nodes/strategist_node.py::_stage_specific_llm_contract` 원본문이 integration와 B-before에서 동일함을 확인하고, thin wrapper와 `stage_contracts.build_stage_specific_contract` import만 최소 hunk 적용. **B 전체 facade 덮어쓰기 금지**. integration facade blob `94f24e54`(B 전체 facade와는 다름), new Owner `libs/runtime/strategist/llm/stage_contracts.py` blob `671292ab`, new test blob `eff3b58b`. B normal targeted **2 PASS exit0** (작업자 보고), 함수/Owner/test 한정 G3_REUSE; RF-008 전체 안전·DONE 선언 금지. B1/B2/B4/B5/B6 NOT_RUN.
- **자동 Actions:** [#40942028951](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/40942028951) exact code SHA `aae2685a`, 후속 확인 `completed/success` (safety 정상 및 safety (-O) job 각각 SUCCESS, 정확 code SHA). 자동 offline safety는 신규 RF 전용 targeted test가 아님. C04 직접 pytest normal/-O/full suite NOT_RUN, 수동 CI dispatch 0, 문서 전용 재CI 0.
- **C05 NEXT:** RF-031 기존 DONE 보존하고 신규 TARGET_GAP_CLOSED 6, RF-008 pure B3 MOVE/G3 경계 수용·RF 원본/STATUS C05 단독 갱신. RF-016/028/029 재통합 금지. RF-041 nonfinite price/RF-045 D2 TOCTOU SAFETY_HOLD, 실계좌·실주문·운영 배포·unsafe apply 금지. 다음 신규 A/B G1/G2 exit0가 오면 최신 원격 HEAD/Owner 충돌 확인 후 선별 통합.
