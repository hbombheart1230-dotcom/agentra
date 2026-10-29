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

## 현재 할 일 — RF-016 DONE 반영 · 다음 신규 G1/G2 READY 대기 (2026-10-29 KST)
- **물리 LEAD 0건 / DONE 21/93:** C05가 RF-016을 `05_DONE/CLAUDE_A/RF-016.md`로 이동하고 G1/G2/G3 MET 처리. [#36 C05 6495520886](https://github.com/hbombheart1230-dotcom/agentra/issues/36#issuecomment-6495520886), 원격 `integration/p1.5@b5dae0f822a0a7c6c87a5f0bfd78b4cdd9b01b0a` 및 `LEAD_CURRENT.md`에서 확인. RF-067도 기존 DONE. **두 RF 중복 테스트·재통합·G3 댓글 금지.**
- **RF-016 확정 판정:** A 고정 SOURCE `2bce7dcaaadebe9fe825dcf9d2f5e1b1f667ad33` ↔ 판정 integration `8546db4dd03983c8d128b9d7bdee1b928f87c5e3`의 Strategist 8 Owner blob 동일 → KEEP 8/8. 기존 동일 관련 코드/테스트/소비자 경계 정상 targeted 94+2+3 PASS(exit0) 재사용, C04 G3_REUSE [#36 6495425616](https://github.com/hbombheart1230-dotcom/agentra/issues/36#issuecomment-6495425616), C05 G3 MET/DONE. C04 직접 pytest·hosted dispatch NOT_RUN. 이후 정본 문서/STATUS 변경은 RF-016 소스 변경으로 간주하지 않는다.
- **신규 delta:** A 원격 `bed173058613ad97f830001771d0bd7b3c191f30`, B 원격 `617c8429c69c98ac6f707a820d0e6825766f8642` (B local `2055bc6f`는 미푸시). 긴급 `emergency/p15-fixes@73731c8e1e6132edc1061b9e2b2b8d987bbdf404`는 `457ca9f8` 대비 1커밋/신규 테스트 `tests/test_rf016_strategist_dynamic_consumer_peer.py`만 추가; 이 브랜치의 테스트 파일 존재만으로 G2/G3 PASS나 integration 코드 변경으로 판정하지 않는다.
- **다음 C04 작업:** C05가 G1 원격 Owner/KEEP SHA와 G2 관련 정상 exit0로 새 RF를 LEAD에 승격하면, 최신 integration HEAD/owner blob/변경 충돌/테스트·의존성 범위를 확인 → 동일 blob이면 KEEP+기존 관련 PASS 1개 재사용, 다르면 승인된 최소 파일만 선별 통합+관련 정상 smoke/pytest exit0 1회. G3 근거를 #36에 **신규 결과일 때만** 남겨 C05에 DONE 인계. 신규 G1/G2 READY가 아직 확인되지 않은 PEER/DEV RF를 C04가 임의 DONE 처리하지 않는다.
- **차단/안전:** RF-041 nonfinite limit price, RF-045/066 log move race D2, RF-021/032/069 보호 실효과는 영향 범위 HOLD. 첫 미충족 G1/G2는 각 Owner 및 C05 수용 담당, 새 G3 증거 부족 시 C04/승인된 격리 테스트 환경 담당. RunLab #32 SOURCE_UNKNOWN/OPEN, 운영 real·실주문·무승인 `--apply` 금지.
- **CI 중복 방지:** 문서/STATUS만 변경되면 pytest/Actions 수동 dispatch 0. 새 코드/테스트 변경 때 기존 동일 범위 성공/진행 중 Actions를 먼저 조회하고, 관련 smoke/CI 유효 근거만 사용. 전체 suite/-O/full peer/매 RF hosted CI는 FAST-3 필수 아님. 신규 통합·CI 성과가 없으면 #36 반복 댓글 0.
