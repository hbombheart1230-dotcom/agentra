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
6. **예약:** A/B 모두 기존 개발 브랜치의 고정 `docs/refactor/work_orders/HANDOFF_A.md` / `HANDOFF_B.md`에 실제 예약 실행 결과 push 확인. 예약은 배정권·독립 PASS가 아니며 매 회차 원격 SHA/실행 증거를 검증한다. GitHub 이벤트 자동 트리거는 NOT_ENABLED.

## 2026-10-23 11:10 UTC 지팀장 최신 수거 판정

- **원격 확인:** 직전 integration `c4ae36f5`, A `37586187` (HANDOFF 상단 RUN `10:58Z-...-4`, 추가 증거 `11:08Z-...-4b`), B `1fbfb78e` (RUN `B-20261023T090903Z`). 두 HANDOFF의 GitHub 영속화 확인. A/B 모두 **신규 소스 변경 없음**. 기록 내부 `PUSH_VERIFIED: PENDING_AT_WRITE`는 원격 커밋 존재와 구분; A RUN_ID/NOT_RUN 혼재는 다음 회차 정정 필요.
- **A RF-013/018:** `BLOCKED / KEEP_VERIFIED_NOT_ACCEPTED`, 소스 후보 `a21401db`, 새 HANDOFF `bd11c774` (RUN `2026-10-23T-claude-a-sched-3`, 신규 소스 없음). A가 소스-only detached 후보에서 가드 normal/`python -O` 각각 **185 passed / 1 failed** 보고(11:08Z 재실행 포함): HANDOFF 경로에 따른 기존 7 실패 중 6건 분리. 잔여 1건은 historical S5 integrated-scope gate가 A 후보의 Reporter 관련 변경·테스트 **51경로**를 허용 범위 밖으로 보고한 것(A 자체 결과, GPT 실행 NOT_RUN; 정적 호출 확인). S5 고정 통합 게이트와 A RF별 검증은 적용 대상/기준 SHA를 분리해야 하며 **오라클 변경 승인 아님**. 기존 2290 passed / 1 failed / 58 errors는 해결되지 않음. 자체 보고이며 **독립 peer NOT_RUN**. **지시:** A는 공유 오라클 무단 수정 없이 RF-013/018 자체 소유 범위 테스트·독립 검증 증거를 보강하고, 다음 HANDOFF에는 단일 UTC RUN_ID와 신규 실행/과거 인용·normal/-O·push 확인을 분리 기록. RF-026의 exit_policy ↔ monitor_exit 순환은 GitHub 소스 정적 확인 완료, BASE 런타임 재현은 A 보고이며 **RF-026 PENDING / SAFETY_HOLD**, GPT 소유권 경계 판정 전 소스 수정 금지.
- **B RF-001:** `VERIFY_PENDING` (소유권·구조 계약 근거 필요); **RF-020:** `NO_WORK / VERIFY_PENDING` (전체 소유 파일 MOVE/KEEP/WRAPPER 증거와 테스트 없이 완료 불가). 기존 코드 후보 `a3d60e37`; 이번 회차 normal/-O `NOT_RUN`. 브랜치 정리 `VERIFY_PENDING`, 클라우드 외 worktree/process `UNKNOWN`.
- **CI_RED:** 후보 `a0493b60`, handoff `59e34204`; B의 이전 read-only 검증은 pinned history `613a945d` 객체/경로 부재로 setup ERROR, optimized `NOT_RUN`. **PEER_PENDING / REWORK_REQUIRED**, 통합 금지. B는 정확한 history/object 검증과 normal/-O 독립 결과를 먼저 보강한다.
- **hosted CI:** `138bdaed` 5개 workflow job/log 직접 확인 **1 PASS / 4 FAIL**. Shared/Reporting은 과거 B-stage 경로 인벤토리와 현재 문서 변경 충돌, Design Guard/T4는 `read-only peer-review gate missing`으로 실패. 상세 job/로그 근거는 [기존 CI 트러블슈팅](../plan/troubleshooting/open/P15_DOC_CI_COMPAT_20261023.md)에 기록. 오라클 약화·무단 수정 금지.
- **결론:** 정규 검증 큐 0건, **RF DONE 0건**, CI_RED 통합 0건. B HANDOFF는 이전 회차 `d06190d9` 그대로(신규 테스트 NOT_RUN). **B 지시:** CI_RED 고정 history 객체/경로 확인 → 독립 normal/-O 재검증, RF-001 소유권 증거 보강; RF-020은 NO_WORK 유지. **GPT:** RF-026 교차 소유권·안전 영향과 A의 S5 고정 경로 계약 적용 범위 판정. 새 브랜치·RF·RUN 문서 생성 금지.

## 현재 검증 상태와 역사

- 마지막 직접 확인 `c4ae36f5`의 5개 hosted Actions **1 PASS / 4 FAIL** (job 완료 재조회); 이번 문서 갱신 SHA의 CI는 **NOT_RUN/UNKNOWN**. 과거 `b768b2b3`의 필수 6/6 PASS는 다른 SHA의 이전 증거이며 현재 GREEN이 아니다. CI 수리 후보는 아직 integration 미반영.
- 합성 `d73be191`과 PR31은 normal/`python -O`·독립검증·exact-SHA hosted CI 이전에 통합 금지.
- 역사적 `DOC-A` · `DOC_FREEZE` · `P1.5.2 OPEN` · `P1.5.3`, Issue #20과 Issues #16–#19 CLOSED는 provenance. 구 BATCH/T00 재활성 및 불필요 Issue 댓글 금지.

## 두 클라우드 예약의 공통 한 줄 프롬프트

`Agentra P1.5 {Claude A|Codex B}: GitHub integration/p1.5의 CURRENT와 D00/D01/D02를 따른다. 매 실행 배정 RF 전부 개발·normal/-O·patchnotes·SHA push 후 작성자 verification 큐에 인수인계하고, 상대 검증 큐는 별도 독립 읽기 전용 세션으로 검증한다. 독립 PASS한 정상 RF만 분리 통합·exact-SHA CI 확인, 예외는 GPT 승인 대기. 상대 CLI 호출·무승인 브랜치·force·main·실거래 금지. 각 RF SHA·테스트·검증·CI·BLOCKED만 보고한다.`
