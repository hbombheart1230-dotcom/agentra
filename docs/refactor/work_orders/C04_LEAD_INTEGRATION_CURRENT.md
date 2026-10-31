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

## 현재 상태 — 2026-10-31 12:35 KST / A RF-035 +8, B RF-063 +2 선별 통합

- **신규 G1/G2:** A #11 comment 6538289132; A actor SHA `d20d9252bd50c1dd284d0563536835a543d6b184`, C02 blob `837b7a680b658e4da246fe42eb070a2cc5e3be7f`. RF-035 A12 실제 BODY MOVE 8개: `q8_historical_review.py` 4개 + `post_exit_shadow_recap.py` 4개 → 8개 신규 Owner, targeted tests 8개. 정상 unittest 24 OK exit0. Integration SOURCE preimage `14c227068e0facd5be52189b3940521e64fb9710` / `36c3fdbaf86998c4194f5fe17c0b793f9a8f8207`와 A 변경 전 blob 일치, Owner 8개 integration 부재 확인. SOURCE wrapper, monkeypatch facade, 출력/예외, fake/temp golden parity 확인. 기존 RF-035 DONE 중복 계상 금지.
- **B 신규 G1/G2:** #12 comment 6538201693; B actor SHA `10a234f02c87f0210e5c50b4e039f7d6907e7aa4` (이전 `4e9cebbbb08a26d4f764de181f30a84b13b3d9a7`), C01 blob `fa87f666b9ef9769b815d3d200f8ebfba20150e3`. RF-063 B5 `_print_human`, B6 `_print_summary` → `strategist_query_render_projection.py`, thin SOURCE wrappers; 정상 unittest 2 OK exit0. Integration SOURCE preimage `f368e15c2783e26f3fd7dd068ff2a167a76b4339`와 B 변경 전 일치, Owner/targeted tests integration 부재 확인. 기존 정상 테스트는 empty rows만 검사하므로 **비어 있지 않은 출력의 광범위한 동등성은 미검증**. B1–B4/B7–B8의 유실된 LOCAL_ONLY 코드는 원격 G1/G2 없음, 이번 통합 0.
- **G3:** A12/B5–B6 exact code/test blob 선별 반영, actor 정상 targeted 증거 재사용(G3_REUSE). C04 직접 pytest=0, manual CI dispatch=0. 자동 push CI 최종 결과는 확인 전 NOT_VERIFIED. C05만 RF 단계/DONE/STATUS 판정. RF-016/028/029/051/054/058 동일 SHA 재통합 0.
- **집계:** REFACTOR_CHANGED=10 (A8+B2); TARGET_GAP_CLOSED_CANDIDATE=10; KEEP_VERIFIED_ONLY=0; RF_DONE_DELTA=0. RunLab #32 마지막 보고 runtime Exited(255), RUN_SOURCE_SHA UNKNOWN, SAFETY_HOLD; 운영 배포/재시작·실주문·실계좌·보호 State/Step5C/UEF/CI workflow 변경 0.
- **NEXT:** C05 A12/B5–B6 G3 수용 판단. B의 남은 B1–B4/B7–B8 재구현·원격 G1/G2 및 비어 있지 않은 렌더 출력 동등성 추가 확인 권장. 신규 delta 없으면 C04 문서/댓글/CI 반복 0.
