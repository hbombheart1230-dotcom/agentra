# C04 — 지팀장 · 선별 통합/CI

## FAST-3 G3 재실행 중복 방지 — C04 실제 판단 절차
- **1단계 대상 검증:** RF의 G1 원격 OWNER SOURCE SHA와 integration의 실제 파일별 Git blob을 대조하고, G2의 정확 SOURCE SHA·영향 테스트/실제 exit0 증거를 확인한다. 단순 문서 HEAD 변경으로 `SOURCE_CHANGED`를 판단하지 않는다.
- **2단계 증거 재사용:** 같은 대상 source+consumer 경계, 동일 테스트·의존성·CI 워크플로 상태에 대해 이미 성공한 정상 smoke/targeted pytest 또는 exact relevant CI 증거가 있으면 `G3_REUSE`로 수용한다. SOURCE 또는 테스트/의존성/보호 경계가 바뀌었으면 관련 범위만 재검증한다. 이전 기록의 PASS가 현재 코드에 해당하는지 불명확하면 재사용 불가, 하지만 full suite로 확대하지 않는다.
- **3단계 명시적 분기:** `KEEP_BLOB_IDENTICAL + VALID_RELEVANT_EVIDENCE` ⇒ **새 CI/pytest 실행 요청 0**, C05에 G3 증거 전달. `SOURCE_CHANGED` 또는 `TEST/DEPENDENCY/WORKFLOW_CHANGED` ⇒ 대상 변경분을 최소 통합하고 **관련 smoke/pytest 1회 또는 유효한 CI 1개** 확인. `DOCS_STATUS_ONLY` ⇒ **신규 CI dispatch 0 / smoke 반복 0**. `NO_MATCHING_EVIDENCE` ⇒ targeted smoke 1회만 실행(실행 환경 부재 시 G3 BLOCKED, 성공으로 간주 금지).
- **4단계 중복 dispatch 락:** 실제 GitHub Actions 수동 dispatch 이전 **기존 run의 head SHA, workflow/테스트 범위, conclusion을 조회**하고, 동등하게 성공한 run이나 같은 범위의 진행 중 run이 있으면 또 요청하지 않는다. 한 번 실행한 후 해당 `RF | owner blobs | integration/source SHA | relevant test list | PASS/FAIL | run_id 또는 local command | reuse/new/blocked` 근거를 #36 한 번만 보고한다. `python -O`/full hosted CI는 FAST-3 강제요건 아님.
- GitHub Actions `push` 트리거/branch protection·workflows·frozen oracle는 변경하지 않는다. 현재 `.github/workflows/p15-shared-candidate.yml`은 코드/테스트 변경 Push에서 자동 실행될 수 있으므로 이것을 삭제/비활성화한다고 주장하지 않는다. **중복 수동 실행 요청만 차단**하고 정상적인 자동 안전 CI는 유지한다.

## FAST-3 간소 통합 우선 (2026-10-29 승인)
- D00 §2 FAST-3가 아래 구 C1~C7/full independent C4/매 RF 전체 hosted normal/-O CI 요구보다 우선한다. **G1/G2 MET인 RF를 G3로 처리**한다. C05의 과거 7개 전수 수용을 기다리지 말고 실제 새로운 G1/G2 상태를 원격에서 확인한다.
- KEEP이면 해당 코드의 integration blob 동일성 확인 후 기존 정상 smoke/CI evidence 1개로 G3 제출 가능. 변경 있으면 최소 파일 선택 통합 후 **변경 경계 관련 smoke/pytest 1회** 또는 해당 integration SHA의 기존 관련 CI 성공으로 G3 제출한다. 전체 suite, -O 반복, 반대 전체 peer, 새 hosted CI 매번 강제하지 않는다.
- 최우선 RF-016(기존 G1/G2 충족)부터 즉시 처리. 통합 결과 없으면 새 G3를 꾸며내지 않고 BLOCKED(scope/명령/NEXT). #36에 필요한 새 증거만 제출.
- mock/paper 실행은 모의 모드·계정이 확인된 환경에서만, 실제 런검증은 별도 단계. 실계좌 real mode는 무승인 실행 금지.

**입력:** [Issue #11 Claude A](https://github.com/hbombheart1230-dotcom/agentra/issues/11) · [Issue #12 Codex B](https://github.com/hbombheart1230-dotcom/agentra/issues/12) · [Issue #32 RunLab](https://github.com/hbombheart1230-dotcom/agentra/issues/32)의 **새 댓글 delta만** → C05가 실제 `04_LEAD_ACCEPTANCE`로 이동한 RF. [D00](D00_ENGINEERING_DELIVERY_POLICY.md) 준수. [#36](https://github.com/hbombheart1230-dotcom/agentra/issues/36)은 결과 출력 전용. 오래된 A/B HANDOFF 재독·갱신 금지.

## 현재 할 일 — RF-016 G3_REUSE 인수 (2026-10-29 KST)
- **물리 LEAD 1건:** `04_LEAD_ACCEPTANCE/CLAUDE_A/RF-016.md` (G1/G2 MET, G3 C04 증거 제출 후 C05 종결 대기). RF-067은 기존 DONE이며 재실행·재통합 금지. 신규 RF-016 코드 통합은 **KEEP 8/8**; 소스 cherry-pick/전체 브랜치 병합 없음.
- **정확 통합 소스:** `integration/p1.5@8546db4dd03983c8d128b9d7bdee1b928f87c5e3` (판정 전 SHA). 고정 A `2bce7dcaaadebe9fe825dcf9d2f5e1b1f667ad33` 대비 `libs/agents/strategist/` 8개 Owner Git blob 전부 동일. 관련 `libs/runtime/strategist/**`, `graphs/nodes/strategist_node.py`, `libs/research/strategy_memory_store.py`, 테스트 3개, P172 fixture/capture, requirements/pytest 설정 동일. `scripts/refactor/shared_strategist_contracts.py` 전체 blob은 변경되었으나 RF-016 테스트가 호출하는 `current_contract`, `restore_candidate`, `historical_source`, `git_source`, `require`, `functions`, `dump`, `Unqualify`, `verify_b_sources` 구현은 양 SHA 간 텍스트 동일; 다른 S5 범위의 새 테스트 성공으로 과장하지 않음.
- **G3_REUSE / VALID_RELEVANT_EVIDENCE:** C05가 원격 RF 원본과 [#36 6494153259](https://github.com/hbombheart1230-dotcom/agentra/issues/36#issuecomment-6494153259)에서 인수한 A 고정 SOURCE read-only `tests/test_p172_strategist_s1_057_migration.py` **94 PASS normal**, `test_strategist_reasoning_quality.py` **2 PASS**, `test_strategist_frame_llm_integration.py` **3 PASS**, temp fake 정상 exit0 보고를 관련 불변 코드/테스트 범위에 한정해 재사용. C04 직접 pytest/CI 실행 **NOT_RUN**, hosted workflow의 다른 safety SUCCESS를 RF-016 targeted PASS로 오인하지 않음. 관련 동일 테스트 중복 실행·수동 dispatch **0**. 새 테스트/의존성/보호 경계 변경 시 이 재사용은 무효이고 해당 경계만 1회 검증.
- **C04 결정:** `KEEP_BLOB_IDENTICAL + G3_REUSE` → **G3 evidence READY / C05 즉시 인계**. C04가 RF 원본 G3 체크·물리 DONE/STATUS를 직접 쓰지 않는다. C05는 원격 증거를 최종 수용해 `05_DONE`/STATUS 동기화. 운영/실계좌 real, 외부 네트워크, 비격리 `--apply` 및 RunLab RUNTIME_VERIFIED는 본 판단 밖이며 HOLD.
- **차단/다음:** 현재 RF-016에 신규 C04 코드/CI 차단 없음. C05가 G3 evidence의 범위·기존 PASS provenance를 거부하면 정확 불일치 대상만 `G3_BLOCKED`로 환원해 targeted smoke 1회(실행환경 부재 시 명령/실행 담당 명시). 다른 READY LEAD 유입 시 최신 HEAD·원격 Owner blob·G1/G2·충돌을 새로 검사. C04 상태 변화 없으면 중복 커밋/댓글 금지.
