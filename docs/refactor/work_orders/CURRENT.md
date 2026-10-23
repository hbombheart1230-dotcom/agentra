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
5. **브랜치·안전:** 상시 `main`/`integration/p1.5`/A/B 4개. 실행 전 checkout/BASE/HEAD/원격 push 권한 확인. divergence 시 강제 push, 무단 merge/rebase, 자동 신규 브랜치 금지. 위 `claude/...`는 기존 승인된 단일 임시 예외이며 검증·보존·소비자 확인 후 정리. `main`, 실거래, Supervisor/Executor/Step5C/UEF, CI 오라클 무승인 수정 금지.
6. **예약:** Claude 2시간 루틴 활성 **보고만 있음**(GitHub Connector/Repository 자동 승계 미검증). Codex 예약은 실제 실행 증거 확인 전 미확정. GitHub 이벤트 자동 트리거는 NOT_ENABLED. 예약은 배정권이 아니며 매 실행 GitHub 인증/checkout 및 (RF, 역할, SHA) 중복을 확인한다.

## 현재 검증 상태와 역사

- 마지막 확인된 integration HEAD `87647c98`: 5개 hosted Actions 중 **1 PASS / 4 FAIL**. 과거 `b768b2b3`의 필수 6/6 PASS는 별도 SHA의 이전 증거이며 현재 GREEN이 아니다. CI 수리 후보는 아직 integration 미반영.
- 합성 `d73be191`과 PR31은 normal/`python -O`·독립검증·exact-SHA hosted CI 이전에 통합 금지.
- 역사적 `DOC-A` · `DOC_FREEZE` · `P1.5.2 OPEN` · `P1.5.3`, Issue #20과 Issues #16–#19 CLOSED는 provenance. 구 BATCH/T00 재활성 및 불필요 Issue 댓글 금지.

## 두 클라우드 예약의 공통 한 줄 프롬프트

`Agentra P1.5 {Claude A|Codex B}: GitHub integration/p1.5의 CURRENT와 D00/D01/D02를 따른다. 매 실행 배정 RF 전부 개발·normal/-O·patchnotes·SHA push 후 작성자 verification 큐에 인수인계하고, 상대 검증 큐는 별도 독립 읽기 전용 세션으로 검증한다. 독립 PASS한 정상 RF만 분리 통합·exact-SHA CI 확인, 예외는 GPT 승인 대기. 상대 CLI 호출·무승인 브랜치·force·main·실거래 금지. 각 RF SHA·테스트·검증·CI·BLOCKED만 보고한다.`
