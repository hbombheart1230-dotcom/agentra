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

## 현재 상태 — 2026-10-31 07:35 KST / A RF-035 +8, B RF-063 +8 선별 통합

- **정확 코드 통합 SHA:** `91b2600d149b724213ea72a929f44143c4f9cf24` (tree `6e4a843a579801b4a2ae3bfa3e8ed819827cfe9b`). Base `4eda3d91481fc0c8d1ca755e346530c8a3daf0fd`; expected-head non-force fast-forward, 원격 HEAD/tree 재조회 일치. A/B **30/30 Git blob 독립 비교** 성공 (A 15, B 15); 전체 Actor 브랜치 병합 아님.
- **A RF-035 A-07:** #11 comment 6534641555, A remote `8256523b1222de59ac4c4978d3937b9cd3a092aa`, C02 order blob `b251450dfc5fbbb21b9143793bd47208750f7eba`. `libs/reporting/intraday_trade_reports.py` 6 함수와 `trade_bundle_assembly.py` 2 함수의 원본 계산 BODY 제거→신규 단일 Owner 5개; 기존 시그니처 thin wrapper/필요 facade 유지. SOURCE2+Owner5+test8 = 15/15 exact. Actor 정상 `python3 -m unittest tests/test_p15_rf035_07h_*_owner.py` **24 tests OK exit0**; -O 재실행 불필요. Actor wide regression 254 PASS/2 FAIL, 두 실패는 actor baseline 재현 보고(전체 green 주장 금지).
- **B RF-063 B-07:** #12 comment 6534633604, B remote `291582e0d83e50390b8abfe64aaefa34815f21e1`, C01 order blob `130987fe5f755fae641c47afa25f6d3f694a1999`. `check_reports_trades_health.py` 7 함수와 `check_reporter_upgrade_regression.py` 1 함수의 실제 BODY를 신규 단일 Owner 5개로 이동, 원본 thin wrapper/call-time facade 보존. SOURCE2+Owner5+test8 = 15/15 exact. Actor 정상 `python -m unittest tests/test_p15_rf063_07h_b{1..8}_*_owner.py -v` (실제 8개 명시 경로) **8 PASS exit0**; 해당 파일 8개 정상 범위 재사용. 단독 B 브랜치의 다른 미검증 변경은 미통합.
- **C04 G3:** 통합 30/30 원격 blob 일치, 원본 SOURCE 4개 모두 사전 integration blob이 각 Actor 이전 blob과 동일했고 신규 Owner/test 26개 모두 기존 integration에 부재. Actor exact source+Owner+test scoped normal evidence 재사용; C04 새 pytest=0, manual CI dispatch=0. 자동 push 안전 CI [#41138831129](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/41138831129) 정확 SHA `91b2600d` **QUEUED** (최종 conclusion NOT_VERIFIED); 기존 성공으로 표시 금지. CI 자동 트리거를 수동 중복 dispatch하지 않음.
- **잔여/판정:** RF-035는 기존 DONE이며 RF_DONE_DELTA=0. RF-063 전체 G1/G2/G3/DONE은 C05 독점; 이전 B5 `validate_trade_artifact_chain`의 `_legacy_validate_trade_artifact_chain` 중복 dead body 및 과거 B1–B4 미통합/검증, RF-044 facade smoke NOT_VERIFIED 유지. B-07 신규 8개만 scoped G3 후보로 인계. RF-065 기존 B0 scoped G3 이력은 유지하되 재통합하지 않음. RF-016/028/029/051/054/058 동일 SHA 중복 통합 0.
- **성과:** `REFACTOR_CHANGED=16` (A8+B8), `TARGET_GAP_CLOSED_CANDIDATE=16`, `KEEP_VERIFIED_ONLY=0`, `RF_DONE_DELTA=0`. 기존 DONE32/93은 마지막 C05 기준이며 이 회차 신규 DONE 주장 금지. RunLab #32 latest 6520075820: runtime Exited(255), RUN_SOURCE_SHA UNKNOWN, operational SAFETY_HOLD. 실계좌·실주문·운영 재시작/배포·Broker/Guard/Step5C/UEF/frozen oracle/CI workflow 변경 0.
- **NEXT:** C05가 A8/B8 exact scoped G3 및 RF 전체 단계 판정. C03/B는 RF-063 B5 dead duplicate와 기존 B1–B4의 증거/통합 공백을 해소하고 RF-065 나머지 Owner/KEEP을 확인. C04는 새로운 code/test delta만 추가 통합하며 본인 C04 문서 외 RF/STATUS/다른 담당 C파일 변경 금지.
