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

## 현재 할 일 — RF-044/045 신규 B 실제 구현 선별 통합 인계 (2026-10-29 KST)
- **정확 B SOURCE:** `14558ddc004037530925cc4f023d6d81a0a62158`, [#12 6498984560](https://github.com/hbombheart1230-dotcom/agentra/issues/12#issuecomment-6498984560) RF-044 실제 2 함수 MOVE + 정상 unittest 2 PASS / pytest 1 PASS exit0; [#12 6497629752](https://github.com/hbombheart1230-dotcom/agentra/issues/12#issuecomment-6497629752) RF-045 `__getattr__` copy/deepcopy 회귀 정상 unittest 1 PASS / pytest 1 PASS exit0. 기존 B G2 실행을 C04 신규 pytest로 오인 금지.
- **C04 코드 통합:** `100aedcdcc5746d73c991b517f0771177d997b7c` (pre-HEAD `584a698389b2f1cb1b38a7012a411cef02af3700`, fast-forward, 5경로). RF-044: integration의 `libs/contracts/agent_outputs.py`에서 **오직 두 함수 몸체만** B의 원시그니처 lazy wrapper로 교체, 나머지 98KB 기존 facade 유지(타 브랜치의 무관한 supervisor/executor builder 삭제 회피); B 신규 `libs/contracts/agent_output_parts/commander_shadow_runtime.py` 및 `tests/test_rf044_commander_shadow_runtime_owner.py` 2개 blob 정확 복사. 실제 함수 몸체는 owner로 이동, 원본 facade 2개 thin wrapper. RF-045: B `libs/core/event_logger_compat.py` 및 `tests/test_p15_event_logger_copy_guard.py` blob 정확 복사. 통합 후 5경로 원격 SHA 재조회 일치.
- **G3 범위/재사용:** RF-044 새 owner blob `1e0f7e75`, test `80ab7ce5`; facade `a671e097` (B 전체 facade blob과 다름: 다른 builder는 integration 그대로 보존). 두 wrapper 텍스트 B와 동일, 기존 계산 함수와 신규 owner의 정규화된 본문 일치(RF-044 actual-runtime), observations는 동등한 signal fallback/position 판정으로 축약, helper `agent_output_values.py` 및 `commander_output_context.py` B/integration blob 동일. RF-045 source `715f2687`, test `295e49be`, 직접 dependency `libs/core/event_logger.py` 양쪽 `de869be7` 동일. **G3_REUSE는 이 두 변경 경계의 기존 B normal exit0에 한정**; 새로운 integration checkout pytest/smoke **NOT_RUN**. C05가 동일 범위 G3 수용 여부를 판단하고 RF/STATUS를 단독 변경. RF-045 log move collision TOCTOU(D2)는 별도 OPEN/SAFETY_HOLD이며 copy guard PASS를 RF-045 전체 안전 종결로 간주하지 않음.
- **자동 CI:** integration 코드 push의 [P1.5 Shared Offline Safety run 40893754131](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/40893754131) **in_progress(최초 조회)**; 성공 여부 확인 전 PASS 주장 금지. 수동 dispatch 0, full/-O/직접 pytest NOT_RUN. 완료되면 정확 SHA·관련 job 범위만 인수; 실패 시 실패 경계와 owner 구분.
- **NEXT:** C05에 RF-044 G1/G2/G3 scoped evidence READY, RF-045 copy-guard scoped G3 + D2 안전 부채를 #36으로 인계. A RF-031은 `reporter_ai_review_input.py` 실제 owner/source/normal exit0/push가 아직 없으므로 C02/Claude A 담당 BLOCKED. 다음 새 READY 함수 이동만 선별 처리. RF-016/028/029/051/054/058/067 반복 금지. 실계좌·주문·운영 배포/비격리 `--apply` 금지.
