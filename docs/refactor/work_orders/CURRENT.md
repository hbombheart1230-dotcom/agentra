# Agentra CURRENT — P1.5 전체 리팩터링

> **유일한 활성 배정판:** 매 실행 원격 `integration/p1.5` CURRENT부터 확인. [D00](../../ENGINEERING_DELIVERY_POLICY.md) · [D01 Codex](../../../AGENTS.md) · [D02 Claude](../../../CLAUDE.md). 불변 문서는 재독하지 않는다.

## 현재 배정 (CURRENT가 유일한 배정 권한)

- 전체 ROOT→LEAF 3985파일/298폴더, RF 93개. [STATUS](../plan/STATUS.md) · [단독 파일 소유권](../plan/FILE_COVERAGE_63182ab2.csv) · [기존 P1.5.0~11 최종 12개 합격 기준](../plan/criteria/).
- **Claude A:** [RF-013 Reporter](../plan/pending/RF-013.md), [RF-018 Strategist](../plan/pending/RF-018.md). 기존 브랜치 `work/p15-a-reporter-pure-20261021`.
- **Codex B:** [RF-001 Operator UI](../plan/pending/RF-001.md), [RF-020 Monitor](../plan/pending/RF-020.md), [구 브랜치 정리 종료 증거](../plan/troubleshooting/open/P15_BRANCH_CLEANUP.md). 기존 브랜치 `work/p15-b-operator-structure-20261022`.
- **정규 RF 검증 큐:** Claude 작성 → [verification/claude](../plan/verification/claude/)에서 Codex 검증; Codex 작성 → [verification/codex](../plan/verification/codex/)에서 Claude 검증. 현재 0건 대기, 최종 DONE 0건.
- **별도 CI_RED 검증 대기(Codex B):** [CI 호환성 트러블슈팅](../plan/troubleshooting/open/P15_DOC_CI_COMPAT_20261023.md), 임시 `claude/agentra-p15-cloud-setup-v5ue0u` @ `59e34204abb66562780773b649576fa142976041` (코드 `a0493b60`, 인수인계 `d629bc31`). **SELF_PASS / PEER_PENDING**. 일반 RF가 아니며 새 RF 생성 금지. GPT가 CI 오라클 검증 후 수용·통합 결정.
- **GPT 지팀장:** 위 CI_RED 예외·[4-HEAD 합성 후보 d73be191](../plan/troubleshooting/open/P15_SOURCE_ADMISSION.md) source admission, RF 배정·최종 DONE. 합성 후보는 아직 SOURCE_ADMISSION_PENDING.

## 동일 실행 절차 — Claude/Codex, 로컬/클라우드 공통

1. **조회:** 최신 CURRENT, 본인 배정 pending RF **전부**, 반대쪽 검증 큐, 일회성 작업을 순회한다. 한 건 BLOCKED여도 다른 작업은 계속한다. 미배정 RF·다른 RF 소유 파일 수정 금지.
2. **개발:** 기존 소스 재사용 → 계약·입출력·부작용 동등성 → normal/`python -O`·경계 회귀 → UI patchnotes JSON/MD → 정확한 SHA 원격 push → **작성자 기준** `pending → verification/<author>` 인수인계. 공용 큐 상태 이동은 GPT/승인 publisher가 반영한다. SELF_PASS는 독립 PASS가 아니다.
3. **독립 검증:** 반대쪽 **별도 세션**이 exact SHA를 읽기 전용 검증한다. **로컬·클라우드 모두 상대 CLI 직접 호출·티키타카 의무 폐지.** 리뷰 세션 수정/커밋/푸시/다른 CLI 실행 금지. 실제 테스트 exit·PASS/REWORK/BLOCKED·NOT_RUN 기록.
4. **통합:** 정상 RF는 독립 PASS 후 별도 통합 단계에서 검증자가 승인 경로만 단일 writer/CAS·비강제 통합해 그 SHA의 normal/`-O`·필수 hosted CI 확인. CI 미통과·충돌·잠금 불명은 BLOCKED. **CI 오라클, PR31/4-HEAD, 안전·공유 계약은 GPT 별도 승인**. 최종 `verification → done`은 GPT만 결정.
5. **브랜치·안전:** 상시 `main`/`integration/p1.5`/A/B 4개. **integration과 A/B 개발 브랜치의 분기는 정상이며 개발 BLOCKED 사유가 아니다.** RF·D00/D01/D02는 integration에서 읽고 코드 작업은 해당 A/B 브랜치에서 수행한다(기존 A/B 브랜치에 RF 문서가 없어도 integration RF를 참고). 로컬 개발 커밋이 **원격 같은 A/B 브랜치 HEAD**의 자손이면 정상 fast-forward push할 수 있다. 동일 브랜치의 원격 HEAD가 변경돼 fast-forward 불가하거나 소유권/계약이 충돌할 때만 BLOCKED로 보고한다. 실행 전 checkout/BASE/원격 HEAD/권한 확인. 강제 push, 무단 merge/rebase, 자동 신규 브랜치 금지. 위 `claude/...`는 기존 승인된 단일 임시 예외이며 검증·보존·소비자 확인 후 정리. `main`, 실거래, Supervisor/Executor/Step5C/UEF, CI 오라클 무승인 수정 금지.
6. **예약:** Claude 2시간 루틴 활성 **보고만 있음**(GitHub Connector/Repository 자동 승계 미검증). Codex 예약은 실제 실행 증거 확인 전 미확정. GitHub 이벤트 자동 트리거는 NOT_ENABLED. 예약은 배정권이 아니며 매 실행 GitHub 인증/checkout 및 (RF, 역할, SHA) 중복을 확인한다.

## 2026-10-23 지팀장 수거 판정 — 사용자 전달 A/B 예약 종료 보고

- **출처 구분:** Claude A 07:39 UTC 및 Codex B 종료 보고는 사용자 전달 내용이며 GitHub RF에 영속화되지 않았다. 원격 A `a21401db`, B `a3d60e37` HEAD를 재조회해 일치 확인. 이번 예약 실행의 신규 push 없음; `HANDOFF_NOT_PERSISTED`. 이를 독립 PASS 또는 RF 완료로 인정하지 않는다.
- **A RF-013/RF-018:** `BLOCKED / KEEP_VERIFIED_NOT_ACCEPTED`. A 보고의 normal/-O 각각 2290 passed, 1 failed, 58 errors는 전부 PASS가 아니다. RF-026 소유 `libs/runtime/exit_policy.py` 순환 import 주장에 대해 담당 RF-026에서 원인/재현/영향 분리 확인 필요. A는 전체 integration merge/rebase 없이 기존 RF 범위의 테스트·동등성 증거를 보강하고, 변경 없는 파일을 DONE 처리하지 않는다.
- **B RF-001:** `VERIFY_PENDING` (소유권·구조 계약 미완). **RF-020:** `NO_WORK / VERIFY_PENDING` (브랜치 diff 없음만으로 완료 불가). 브랜치 정리 `VERIFY_PENDING`. 두 정규 검증 큐 0건, DONE 0건 유지.
- **CI_RED 예외:** 후보 `a0493b60` / 인수인계 `59e34204`는 B 보고상 독립 검증 normal setup 오류, `python -O NOT_RUN`; `PEER_PENDING / REWORK_REQUIRED`. GPT 별도 CI 오라클 승인 전 통합 금지.
- **CI 관측(사용자 전달, 재확인 필요):** `9ad952a0`에서 Scripts PASS, Shared Candidate FAIL, Reporting/Web FAIL, Reporting Regression/Design Guard 및 T4는 RUNNING으로 보고됨. 종료 상태 및 필수 전체 PASS 미확인.
- **지팀장 다음 행동:** A/B는 신규 RF·별도 RUN 문서 생성 없이 기존 브랜치의 허가된 인수인계 위치를 확정할 때까지 종료 보고에 `HANDOFF_NOT_PERSISTED` 명시. GPT는 RF-026 소유권/순환 import 재현, CI_RED 독립 검증 실패 근거, RF-001 소유권 계약을 우선 판정한다. CURRENT는 요약 판단만 기록하며 세부 RF 인수인계/상태 이동은 증거·단일 writer 확인 후 수행한다.

## 현재 검증 상태와 역사

- 이전 확인 integration HEAD `87647c98`: 5개 hosted Actions 중 **1 PASS / 4 FAIL**. 과거 `b768b2b3`의 필수 6/6 PASS는 별도 SHA의 이전 증거이며 현재 GREEN이 아니다. CI 수리 후보는 아직 integration 미반영.
- 합성 `d73be191`과 PR31은 normal/`python -O`·독립검증·exact-SHA hosted CI 이전에 통합 금지.
- 역사적 `DOC-A` · `DOC_FREEZE` · `P1.5.2 OPEN` · `P1.5.3`, Issue #20과 Issues #16–#19 CLOSED는 provenance. 구 BATCH/T00 재활성 및 불필요 Issue 댓글 금지.

## 두 클라우드 예약의 공통 한 줄 프롬프트

`Agentra P1.5 {Claude A|Codex B}: GitHub integration/p1.5의 CURRENT와 D00/D01/D02를 따른다. 매 실행 배정 RF 전부 개발·normal/-O·patchnotes·SHA push 후 작성자 verification 큐에 인수인계하고, 상대 검증 큐는 별도 독립 읽기 전용 세션으로 검증한다. 독립 PASS한 정상 RF만 분리 통합·exact-SHA CI 확인, 예외는 GPT 승인 대기. 상대 CLI 호출·무승인 브랜치·force·main·실거래 금지. 각 RF SHA·테스트·검증·CI·BLOCKED만 보고한다.`
