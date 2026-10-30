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

## 현재 상태 — 2026-10-30 16:35 KST / A10+B8 신규 18 BODY MOVEs 선별 통합

- **최종 코드 통합 SHA:** `0f55b843de35408eff0a06fd06c2c520319cd5ac` (parent `833309f632134a2be4571d5766333c134ea39035`). `integration/p1.5` non-force expected-HEAD fast-forward 성공. Compare 정확 1 commit / **31 code+test paths**, remote Git tree **31/31 blob exact** 확인. 실주문·운영 배포 0.
- **Claude A RF-035 A1–A10:** [#11 6517271675](https://github.com/hbombheart1230-dotcom/agentra/issues/11#issuecomment-6517271675), remote SOURCE `1cc562b4319a3d7008bd38c1efcc7d699dd7da16`, C02 blob `7c2cdb74f6deedd6d161c959ff5fa4a914dc5142`. `libs/reporting/llm_artifacts.py` integration pre blob `06dd435f68aeae0043e43f27f0b1600fa3e61b0c` == A actor parent, actor after `1c093529d1885e976a49a190a125bcdb99c84afa` exact 반영. 실제 BODY 10개 → Owner 5개, thin wrapper·호출 시 facade 유지. 신규 Owner 5 + test 10 + source 1 = **16 exact blobs**. A normal targeted **65 PASS exit0** worker-reported, 동일 source/test blob에 한정 G3_REUSE. 기존 연관 17 failures는 worker가 원본 복원 상태에서도 재현했다고 보고했으며, C04 직접 재현/전체 suite 검증은 NOT_RUN; 관련 회귀 없음으로 단정 금지.
- **Codex B RF-044 B1–B8:** [#12 6517189060](https://github.com/hbombheart1230-dotcom/agentra/issues/12#issuecomment-6517189060), remote SOURCE `3f36f7185a5db639ce73fd93b0f62695f5df2570`, C01 blob `1264b7480f9af841fed45c5d3a8eb49d8d793bc0`. Actor source `agent_outputs.py` pre `fdd9948f2264a63344bb6a8807ea5851fcf686bb` → after `c8d78ee370f7d1dabe61584003692d36a3991d51`. Integration source pre `0ab92db0ff3397b3cb336b71b7098089ca0d508a` was divergent: **8 selected original function bodies match 7/8 exact, remaining commander-output body whitespace-only difference**, so only 8 actor thin wrappers selectively replaced, 35 other function blocks preserved. Result integration source blob `ccfc2b8990e0bb6980c4274d46178c85d949085f`; 6 new Owner modules + 8 tests exact actor blobs; **15 paths**. Worker normal targeted **8 PASS exit0**, full-repo integration facade-call targeted smoke **NOT_VERIFIED**, G3 facade scope PARTIAL; Owner-only PASS를 facade PASS로 확대 금지.
- **CI:** exact code SHA GitHub Actions [#41021352642](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/41021352642) **QUEUED at first read**; success claim 금지, final result 재조회. C04 직접 pytest 0, full suite 0, manual dispatch 0. 자동 safety CI는 신규 18함수 targeted 테스트와 별개. 기존 RF-016/028/029·RF-051/054/058 재통합·반복 테스트 0.
- **C05 NEXT:** #36에 코드 SHA·Owner/consumer scope·worker normal tests·B facade NOT_VERIFIED·CI status 전달. RF-035/RF-044는 기존 DONE이므로 **TARGET_GAP_CLOSED +18**, **RF_DONE_DELTA=0**. 마지막 C05 확인 누적 DONE **32/93**은 과거 값, 이 회차 신규 DONE 아님. B facade 8개 및 이전 미검증 10개는 준비된 전체 checkout에서 실제 영향 범위 normal targeted 1회만, 환경 없으면 BLOCKED/NOT_VERIFIED. C03 다음 신규 A/B 주문 공급·Owner 충돌 검증, RF-041/RF-045 안전 HOLD와 RunLab 운영 장애는 별도.
