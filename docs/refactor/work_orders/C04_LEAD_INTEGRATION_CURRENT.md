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

## 현재 상태 — 2026-10-31 13:35 KST / A RF-035 +8, B RF-063 +6 선별 통합

- **신규 G1/G2 A:** #11 comment 6538883509, actor SHA `4efeab48c58fc08d25d6618325933625265fa2a6`, C02 blob `d5e0099495b7faeea1b23f9425fb6becf0062af8`. RF-035 `q8_shadow_blocker_review.py`의 _text/_to_float/_bool/_candidate_rows/_checkpoint_values/_avg/_decision_for_row/_summarize_group **8 실제 BODY MOVE** → 신규 독점 Owner 5개, 정상 unittest 24 OK exit0. SOURCE integration preimage `7e482261ae1da4824112d8d2fea0b7c6a3aab9c6`와 actor parent 일치. 기존 historical/post_exit Owner 6개 `Mapping` facade lookup 보정(실제 신규 BODY MOVE 아님), 기존 golden 72 PASS actor 보고. `test_closeout_payload_projection.py`는 기존 AST guard가 새 Owner 함수를 검사하도록 경로만 수정(동일 key 불변식), 관련 12 PASS actor 보고. 전체 기존 suite green 주장 금지.
- **신규 G1/G2 B:** #12 comments 6538827947/6538870463, actor code SHA `7f00a91dce9df811859dddff94baf6909d71391c`, final SHA `9ea1f2354617080699fc245e7cd79c666ba3cca0`, C01 blob `42676d182915e35b9a14d66f06f8b9e9e8c49638`. RF-063 B1–B4/B7–B8 **6 실제 BODY MOVE**: query_m25_notification_events.py 4함수 → time/env/cli Owner 3개; query_commander_resilience_events.py 2함수 → resilience Owner 1개. SOURCE integration preimage `ec1f122a60875da5fbea743d42ddeca75bc07c7f` / `caebd5b1466a7f408a70be98ee94b89d5cda5e01`와 actor parent 일치. 정상 unittest 6/6 exit0; B5/B6 nonempty stdout parity 신규 2 PASS, 총 8/8 exit0 actor 보고. B5/B6 함수 재이동 없음.
- **G3:** A/B 신규 source+owner+test **35개 파일**의 exact actor blob 선별 통합 예정/반영, preimage 12/12 확인, 신규 Owner/test 경로 23개 integration 부재 확인. A 8 + B 6 = REFACTOR_CHANGED 14; TARGET_GAP_CLOSED_CANDIDATE 14; KEEP_VERIFIED_ONLY 0; RF_DONE_DELTA 0. Actor exact-scope normal PASS 재사용(G3_REUSE), C04 직접 pytest 0, manual CI dispatch 0. 자동 push CI 최종 결과 별도 확인 전 NOT_VERIFIED. RF-035 기존 DONE 중복 계상 0, RF-063 전체 DONE C05 전담. RF-016/028/029/051/054/058 동일 SHA 중복 통합 0.
- **NEXT:** C05는 정확 통합 SHA·blob 및 G3_REUSE 확인 후 RF-035 기존 DONE 유지, RF-063 전체 단계 판정(과거 B5 중복 계산/남은 Owner 범위 확인). C03은 다음 신규 안전 주문 공급. RunLab #32 RUN_SOURCE_SHA UNKNOWN / SAFETY_HOLD 별개. 실계좌·실주문·운영 재시작/배포, Broker/Guard/Step5C/UEF/State 및 CI workflow 변경 0.
