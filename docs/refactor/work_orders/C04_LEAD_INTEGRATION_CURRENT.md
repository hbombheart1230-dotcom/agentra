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

## 현재 상태 — 2026-10-30 21:35 KST / RF-035 A8 신규 통합, B G1 미도달

- 정확 코드 통합 SHA: 02280a2f4709d05d547bdbdf728b8c781257aefe (parent ad1b22a50ca00ae9fdbb54ec4f1c91d1bbf338dd). Actor exact-blob tree/commit, expected-HEAD non-force fast-forward 성공. 14 code/test paths, 14/14 exact actor Git blobs 재조회 일치. 실제 SOURCE→TARGET BODY MOVE 8, TARGET_GAP_CLOSED +8, RF_DONE_DELTA=0.
- A / RF-035: [#11 6522784886](https://github.com/hbombheart1230-dotcom/agentra/issues/11#issuecomment-6522784886), actor remote a9303b0d0f653ec266bf3a66c7be6738e7871586, C02 order blob d39bb8e16a9bbd251d8b721385bf3fb8ee027619. strategist_llm_evaluation.py before eecb06d5 → after 123d3346, strategist_llm_summary.py before 93c71e03 → after 59535490; integration pre blobs matched actor pre. Evaluation _bool/_row_closed/_result_pct/_tactic/_quality_label → strategist_llm_evaluation_extra_projection.py; build_strategist_llm_evaluation → strategist_llm_evaluation_build.py; render_strategist_llm_evaluation_lines → existing strategist_llm_evaluation_formatting.py (_format_perf preserved); summary _read_json → strategist_llm_summary_read_projection.py. Eight new targeted tests. Original signature thin wrappers and call-time facade/monkeypatch seam retained, no direct Owner→SOURCE imports.
- G2/G3: A worker reports python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_21h_*_owner.py: 65 PASS normal exit0. Exact same actor source/owner/tests 14/14 integrated; G3_REUSE for changed boundary. Worker additionally reports 543 existing relevant PASS/0 FAIL and optional -O 65 PASS; C04 did not independently execute them. C04 direct pytest 0, manual CI dispatch 0; automatic push CI is separate and not substituted for targeted normal.
- B / RF-063 + RF-065: [#12 6522442813](https://github.com/hbombheart1230-dotcom/agentra/issues/12#issuecomment-6522442813). Current C01 order blob 105012c82b0002ff53a12737860dffdd693ee480. Remote B remains 8fe73f486c4b8ac43f75558b19c403bbe29f6b50. Prior RF-063 nine helper bodies local-only commit 6aa9a0a0 unavailable in fresh workspace; no reviewed remote delivery. G1 NOT_MET / NOT_INTEGRATED. B0 RF-065 markdown incomplete; earlier seven bodies G2 per-function NOT_VERIFIED, G3 BLOCKED. New 21h B1–B9 no remote code/test delta. Older RF-063 globals()/facade defect not cleared.
- C05: RF-035 already 05_DONE → eight more TARGET_GAP closed, RF_DONE_DELTA=0. Last independently checked queue 32/93 DONE; C05 owns fresh physical recount and STATUS. RF-016/028/029 and RF-051/054/058 same-SHA reintegration 0. RF-044 full-checkout facade smoke NOT_VERIFIED. RunLab #32 Exited(255), RUN_SOURCE_SHA UNKNOWN, operational SAFETY_HOLD; no real orders, real mode, restart, deployment, Broker/Guard/Step5C/UEF effects.
- NEXT: New G3 evidence to #36 once with exact code SHA, A G2 65 PASS and B blockers; C05 acceptance. B must supply verified remote SHA and exact relevant normal test evidence before further C04 integration. Unchanged KEEP/DOCS_ONLY new CI/pytest 0.
