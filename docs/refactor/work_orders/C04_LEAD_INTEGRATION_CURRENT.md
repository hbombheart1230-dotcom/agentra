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

## 현재 상태 — 2026-10-30 15:35 KST / 신규 A9+B10 실제 19 BODY MOVEs 통합

- **최종 코드 통합 SHA:** `b982de992b239f7f906d3da041e486faabb1e66c` (parent `00a3b744cea69cedc410373b21b35036ed557ff6`). `integration/p1.5` 비강제 fast-forward 푸시 및 remote tree 32/32 blob 일치 확인. A/B 신규 code+test 32개 경로. GitHub compare 정확 1 commit / 32 paths.
- **Claude A RF-035 A1–A9:** [#11 6516383361](https://github.com/hbombheart1230-dotcom/agentra/issues/11#issuecomment-6516383361), actor SOURCE `85549ddb008a2b7a542f6518062db7f279398c9e`, C02 blob `7f3c2af364622e4ee77bb76d16ab239b22c1327c`. integration 원본 `strategist_llm_summary.py` blob `2d1b76fa3f53a2a18e3eb116fc38fcea255d64a9`가 actor before와 **정확히 동일**해 actor after `93c71e03103c8a39d7280806a1f15792db3611c3`를 안전 적용. 신규 Owner 4개 + 기존 Owner 2개 확장; 원시그니처 wrapper 유지. 9개 신규 tests 포함 총 16 경로. Worker normal 400 PASS 및 405 관련 기존 tests PASS 보고, exact worker SHA. C04 직접 pytest NOT_RUN; 같은 source+test blobs로 G3_REUSE (해당 범위).
- **Codex B RF-044 B1–B10:** [#12 6516379802](https://github.com/hbombheart1230-dotcom/agentra/issues/12#issuecomment-6516379802), actor SOURCE `30a28fffc2c07274206e63717ff1f1561d5f941e`, C01 blob `7b633cf2eabd65be4b489906c0d6732a953527a0`. actor 원본 `agent_outputs.py` blob `b8060eb65d0d1b73d9fb49d7cf6b0d1730cee5de`와 integration 원본 `354f4ba29ff230b472ff85284c1baecd07ccc772`는 전체가 다르지만 **10개 이동 대상 원함수 블록 10/10 정확 동일**. 10개만 actor after thin wrappers로 선택 교체, 나머지 integration 함수 33개 동일 보존. 선택 교체 결과 source blob `0ab92db0ff3397b3cb336b71b7098089ca0d508a`; 신규 Owner 5개, tests 10개, 총 16 경로. Worker normal targeted 10 PASS exit0. 전체 체크아웃 facade 호출 targeted smoke **NOT_VERIFIED**; Owner tests만으로 facade PASS 주장 금지. G3 B facade scope PARTIAL, C05 판정 대기.
- **검증 및 CI:** C04 신규 직접 pytest/stdlib smoke 0, 전체 suite 0, 수동 GitHub Actions dispatch 0. 신규 코드 통합 SHA의 자동 CI는 마지막 조회 시 workflow run 없음(`NOT_VERIFIED`); 성공으로 기록하지 않는다. A/B 원격 actor tests의 같은 code/test blob 증거만 범위 한정 재사용. 기존 RF-016/028/029·RF-051/054/058 중복 통합/테스트 0. 실계좌/실주문/운영 배포 0.
- **C05 NEXT:** #36에 G3 신규 19개 BODY MOVE 및 코드 SHA를 인계하고, RF-035/RF-044 기존 DONE 중복 승격 없이 TARGET_GAP 19건 해소로만 반영. 기존 누적 DONE 32/93은 **이전 확인값**이며 이 통합 자체로 신규 DONE 0. B facade smoke가 필요한 경우 실제 준비된 전체 체크아웃에서 영향 10함수만 1회 targeted 검증; 환경 부재 시 `NOT_VERIFIED`. C03 신규 A/B 주문을 다시 공급할 때 SOURCE/TARGET 겹침·신규 함수 body 여부를 우선 확인. `RF-041` nonfinite price / `RF-045` TOCTOU 보호 HOLD, RunLab 별도 유지.
