# D00 — Agentra P1.5 공통 개발·안전·검증 계약

> **활성 규칙만 유지.** 과거 BATCH·PR31·CLI 티키타카·날짜별 실행 기록은 Git 이력에 보존하며 현재 작업 권한이 아니다. 모든 역할은 먼저 [CURRENT](refactor/work_orders/CURRENT.md)를 읽는다. D00은 최초·변경·충돌·안전 판단 때 읽고, 같은 SHA면 반복 전문 열람하지 않는다.

## 1. 범위·정본·소유권
- P1.5는 Agentra **전체 ROOT→LEAF** 리팩터링이다. [**T00 전체 목표트리**](refactor/architecture/T00_TARGET_TREE.md)에서 10개 루트·26개 libs 패키지의 목표 경계를 찾는다. P1.5.0~11의 기존 최종 합격 기준, 동결 V3, [STATUS](refactor/plan/STATUS.md), [FILE_COVERAGE](refactor/plan/FILE_COVERAGE_63182ab2.csv), 각 [RF](refactor/plan/pending/)의 소유권·계약을 유지한다. 신규 계획·중복 문서·Issue 댓글·자체 감사 도구를 불필요하게 만들지 않는다.
- 정규 브랜치: `main`(승인 전 수정 금지), `integration/p1.5`(GPT 지팀장 단일 관리 writer), `work/p15-a-reporter-pure-20261021`(Claude A), `work/p15-b-operator-structure-20261022`(Codex B). 기존 임시 브랜치는 미통합 변경·소비자·보존 SHA 확인 후에만 정리한다. 신규 브랜치/worktree·force push·무승인 merge/rebase 금지.
- 매 실행 repo ROOT, checkout, origin/integration 및 자기 원격 HEAD를 확인한다. CURRENT와 RF는 integration 정본, 실제 개발과 HANDOFF는 각 A/B 기존 브랜치에 작성한다. 정상적인 integration↔A/B divergence 자체는 BLOCKED 사유가 아니다. push는 같은 원격 브랜치 HEAD와 fast-forward 여부를 확인한다.
- RF 소유권 외 파일은 읽기 전용. 공유 계약·교차 RF·소비자 이동은 별도 RF와 소유권·승인 게이트를 따른다. RF-013 owner 9파일과 RF-030/035 소비자는 별도 입장·검증. RF-021 안전 HOLD 유지.

## 2. 작업·증거·기록
- `CURRENT`는 **작업 경로만**(약 1~2KB). 회차별 SHA/테스트/일지 누적 금지. 배정은 링크 한 줄만 변경. 상세 근거는 기존 RF·troubleshooting, 전체 진행은 STATUS, 이전 실행은 Git 이력.
- 개발자 각자 고정 경로 `docs/refactor/work_orders/HANDOFF_A.md` 또는 `HANDOFF_B.md`를 **자기 작업 브랜치에서만** 갱신한다. 최신 회차 **10~20줄 요약으로 교체**하며 과거 회차 누적 금지. RUN_ID, 담당 RF별 상태·후보 코드 SHA·변경 경로, normal/-O 명령/exit/PASS 또는 NOT_RUN, peer verdict/REWORK/BLOCKED, patchnotes, CI exact SHA/URL/상태, GPT_ACTION_REQUIRED를 포함한다. HANDOFF 커밋 SHA와 코드 SHA는 구분하고 push 후 원격 HEAD를 재조회해 검증한다. 자기 커밋 SHA를 사전에 파일 안에 기재하지 않는다. 원격 미보존은 HANDOFF_NOT_PERSISTED.
- 실질적 변경이 없으면 NO_CHANGE/NO_WORK를 보고하되 **빈 문서 커밋 금지**. 근거가 새로 생긴 경우에만 RF/HANDOFF/STATUS/troubleshooting을 갱신한다. 소스 변경 시 UI 연결 patchnotes **JSON·MD 동기화**. 테스트 임시 산출물은 격리·성공 자동 정리·실패 제한 보존.
- 작업은 `pending/RF-xxx.md → verification/claude`(Claude 작성/B 검증) 또는 `verification/codex`(Codex 작성/A 검증) `→ done/RF-xxx.md`. **93개 RF 각각 한 상태 폴더에만** 둔다. 후보 SHA·self normal/-O·근거가 있을 때 GPT가 기존 RF를 검증 큐로 이동한다. BLOCKED/REWORK도 큐 유지하고 원작성자에게 수정 재배정; 다른 독립 RF는 계속한다. GPT만 최종 done 이동.

## 3. 개발·독립 검증·통합
- 개발은 기존 코드 재사용·의미 있는 분리 또는 KEEP_VERIFIED를 선택하고 import/call/DTO/State/IO/예외/side effect/거래 안전의 동등성을 확인한다. 소유 경계·양성/음성·실패 경로를 포함한 **위험 표적 테스트**를 normal과 `python -O`로 수행하고 정확한 후보 SHA를 push한다. 단순 KEEP도 BASE blob과 소비자 계약 증거가 필요하다.
- 상대 검증은 **별도 독립 read-only 세션**에서 정확한 BASE→후보 SHA와 변경 경계만 확인한다. 개발자가 상대 CLI를 직접 호출할 의무가 없다. 자체 PASS/exit 0/CI GREEN은 peer PASS가 아니다. 검증자는 명시적 PASS/REWORK/BLOCKED, 테스트·exit/NOT_RUN, 실패 근거를 남긴다. 동일 SHA의 불필요한 3,000개 테스트 반복·감사 재귀를 금지하며 새 위험이 있을 때만 범위를 확장한다.
- **검증 속도 게이트:** 실패는 동일 명령·환경의 BASE와 후보 exact SHA를 비교해 기존 CI_RED와 신규 회귀를 분리하고, 재현하지 못한 것은 UNKNOWN으로 남긴다. 지팀장은 새 peer 증거가 도착한 **해당 점검 회차에** PASS/REWORK/BLOCKED와 다음 조치를 판정해 RF에 기록한다. 범위 한정 PASS는 최종 PASS나 DONE으로 승격하지 않는다.
- **검증 중 발견 결함의 실수정 의무:** 독립 검증자가 재현 가능한 실제 결함을 발견하면 실패 node·재현 명령/exit·BASE/후보 SHA·정확한 경로·최소 수정안을 기존 RF/HANDOFF에 남긴다. **해당 RF의 현행 승인 개발 writer는 자기 독점 파일 안의 비안전 결함을 직접 수정·normal/-O 검사·push**해야 하며, `REWORK` 보고만 반복해 작업을 종료할 수 없다. 다음 배정에서 수정된 **새 후보 SHA**를 상대가 검증한다. 기존 BASE에서도 같은 실패이면 `BASELINE_EXISTING`, 환경만의 실패이면 `ENVIRONMENT`로 격리하고 허위 수정·PASS를 만들지 않는다.
- **검증자의 직접 수정은 역할 전환 후:** 검증 read-only 세션에서는 코드 수정·커밋·push 절대 금지. 단, 검증자가 **자기 CURRENT 개발 배정·RF 소유 파일**에서도 동일 결함을 발견하면 검증 세션을 종료하고 **별도 개발 세션에서 직접 수정**한다. 상대 작성 RF를 검증자가 직접 고쳐야 효율적인 경우에는 지팀장이 **수정 전** 해당 RF에 허용 경로·비안전 수정 범위·새 writer·정확한 SHA·원래 작성자 및 새로운 독립 리뷰 책임을 명시하고 CURRENT의 개발/검증 배정을 조정한 뒤, 기존 A/B 작업 브랜치의 별도 개발 세션에서만 수정하도록 할 수 있다. 이는 자동 권한이 아니며 작은 Quick Fix는 아래 기존 예외 규칙이 우선한다. **어느 역할이든 자신이 작성한 신규 delta를 자신이 최종 peer PASS 처리할 수 없다.** 이전 작성자와 새 작성자가 교차된 RF는 수정 delta별 비작성자 독립 증거를 결합해 지팀장이 최종 계약 동등성을 판정하고, 증거 공백이 있으면 BLOCKED를 유지한다. 교차 RF 경로·공개 계약·안전 효과·CI 오라클 변경의 별도 승인 조건은 그대로다.
- **Quick Fix 예외:** GPT가 수정 **전에** 해당 RF에 정확한 파일 경로·기준 SHA·일시 writer 이전의 승인 근거를 기록하고 CURRENT에는 해당 RF 경로만 지정한 작은 비안전 import/path/typo/fixture 수정만 검증자의 **별도 수정 역할 세션**에서 기존 A/B 브랜치에 허용한다. 작성한 검증자는 그 SHA에 최종 독립 PASS 불가; 반대 비작성자가 새 exact SHA를 다시 검증한다. 구조·공개 계약·거래 안전·CI 오라클·교차 소유권은 Quick Fix 불가. CURRENT 포인터 정책을 유지하도록 승인 기록은 해당 RF에 상세화하고 CURRENT에는 그 RF 경로만 지정한다.
- peer PASS 후 **검증 세션과 분리된 통합 단계**에서 승인 RF 경로만 integration 최신 HEAD에 단일 writer/CAS·비강제 선별 반영한다. 전체 A/B 브랜치 병합 금지. writer 잠금/원자성·소유권·충돌 증명이 없으면 INTEGRATION_BLOCKED. 정확한 **새 integration SHA**에 normal/-O 회귀 및 필수 hosted GitHub Actions GREEN을 확인한 뒤에만 GPT가 done 판정한다. CI RED/PENDING/NOT_RUN/UNKNOWN은 PASS가 아니다. 다른 SHA의 과거 CI PASS를 승계하지 않는다.

## 4. 절대 안전·예외
- `main`, 실거래 주문/권한, Broker·Supervisor·Executor·Step5C·UEF 안전 계약·가드·replay/write-safety, CI 오라클·테스트 기대값·allowlist·skip/xfail/waiver는 **명시 승인 없이 변경 금지**. 특히 거부된 CI 오라클 후보 `a0493b60`은 승인되지 않았다. 실패를 숨기거나 안전 경로를 단축해 GREEN으로 만들지 않는다.
- RF-021 안전 HOLD 및 P1.5.0~11 동결 합격 기준 유지. 공유 공개 계약·4-HEAD/PR31 합성·기존 미승인 source admission은 GPT 별도 검토·승인 전 통합 금지. 거래 자격 증명·실계좌를 테스트에 노출하지 않는다.
- 독립 검증은 코드 쓰기·커밋·push·중첩 CLI 없이 수행한다. 안전한 격리가 증명되지 않은 권한 우회 CLI 플래그 금지. 파일 삭제/임시 브랜치 정리는 SHA 보존·PR/CI/예약 작업/워크트리 소비자 확인 후 조건부 수행한다.
- 실제 수행하지 않은 테스트/CI는 NOT_RUN, 조회 불가면 UNKNOWN. 막힌 사유와 **가장 작은 수정·다음 행동**을 보고하고, 승인 없는 오라클 수정 대신 BLOCKED를 유지한다.

## 5. 역할과 보고
- [D01 Codex](../AGENTS.md) / [D02 Claude](../CLAUDE.md)는 역할·검증 큐·HANDOFF 경로만 정의한다. [CURRENT](refactor/work_orders/CURRENT.md)의 최신 배정이 우선하며 D00 안전 게이트를 완화하지 못한다.
- 지팀장은 A/B 원격 HEAD와 HANDOFF의 **최신 회차만**, 변경된 RF·실제 코드/CI 증거만 읽는다. A/B 실제 변경 SHA·normal/-O·peer 결과, 지팀장 큐 이동/통합/DONE, pending/verification/done(총93), CI와 다음 행동을 이 채팅에 간결히 보고한다. 증거 없는 완료 주장·문서만을 위한 커밋 금지.

## 6. 지팀장 차단 해소·검증 적체 운영 루프 (모든 지팀장 점검에 적용)

- **단일 운영 위치:** 규칙은 이 **D00 §6**, 건별 결정·수정 지시는 **해당 RF**, 요약 책임·상태는 **[STATUS](refactor/plan/STATUS.md)**, A/B 실행·결과는 각자 **HANDOFF**, 작업 순서/포인터만 **[CURRENT](refactor/work_orders/CURRENT.md)**에 둔다. 새 총괄 문서·중복 회차 일지는 금지. CURRENT는 이미 D00 링크를 갖고 있으므로 규칙 전문을 복제하지 않는다.
- **점검 입력(매 지팀장 점검의 고정 순서):** CURRENT 최신 HEAD → A/B 원격 HEAD와 최신 HANDOFF → 새 후보·peer 증거가 있는 RF/열린 차단 RF의 *변경분만* → STATUS의 pending/verification/done 수와 hosted CI **정확한 SHA**. D00 및 미변경 증거는 SHA가 같으면 전문 재열람하지 않는다. 이 절차는 지팀장 점검이 수행될 때 적용하며 별도 예약 실행을 자동 생성하지 않는다.
- **BLOCKED/REWORK 처리 책임 = 지팀장:** 문제를 단순 재보고하지 않고 **그 점검 회차에 RF 본문에** (1) 실패 node/원인 분류(`NEW_REGRESSION` / `BASELINE_EXISTING` / `ENVIRONMENT` / `CROSS_RF_OWNER` / `UNKNOWN`), (2) BASE·후보 SHA 및 정확한 영향 경로, (3) 파일별 writer Owner·독립 reviewer, (4) 승인된 최소 수정 또는 읽기 전용 증거 요청, (5) 금지 경계, (6) 재개 트리거·PASS 판정 조건·다음 행동을 명시한다. 증거 부족은 UNKNOWN으로 유지; 임의로 PASS/권한 승격 금지.
- **소유권 충돌 의사결정:** 지팀장이 고정 CSV/각 RF/실제 소비자를 대조해 경로별 단일 writer를 판정한다. **판정 ≠ 변경 승인**. 타 RF 경로·신규 공개 인터페이스·안전 효과·CI oracle은 기존 D00·사용자 승인 게이트가 충족되기 전까지 read-only/BLOCKED. 수행자는 자기 CURRENT 배정과 허용된 소유 파일만 수정, 상대 peer는 별도 read-only 세션으로 검증한다. 과거 오라클/테스트 기대값을 실패 숨기기 용도로 수정할 수 없다.
- **실제 수정 확인 게이트:** `REWORK/FIX_REQUIRED`의 원인이 허가된 RF 독점 파일 안에 있는 재현 가능한 코드 결함이면, 지팀장은 해당 RF에 **FIX_OWNER · 수정 허용 경로 · 실패 node · 요구 코드 delta · 제출할 신규 source SHA · 다음 peer 담당**을 확정하고 개발자가 실제 소스 diff를 제출했는지 확인한다. 소스 diff 없이 반복된 `REWORK`/문서 보완은 해결로 집계하지 않는다. 반대로 `CROSS_RF_OWNER/SAFETY_HOLD/CI_ORACLE` 등 무권한 경계는 원인과 승인 요청만 기록하고 임의 수정시키지 않는다.
- **대기열 관리:** 동일 SHA·동일 실패에 재검증 반복하지 않는다. 증거가 들어오면 같은 점검에서 `PASS_SCOPED/REWORK/BLOCKED`와 다음 **한 가지 실행 행동**을 RF·STATUS에 반영하고, 실행 가능하면 CURRENT의 기존 A/B 순서에 연결한다. 진전 불가능한 RF는 차단 이유·재개 트리거를 남기고 다음 독립 RF로 진행한다. PASS_SCOPED와 KEEP_CANDIDATE는 RF DONE 근거가 아니다.
- **마감/보고:** 승인된 소스는 GPT가 최신 integration에 **RF 소유 경로만 선별 통합**, 새 통합 SHA의 normal/`python -O`·필수 hosted CI GREEN을 확인한 뒤 RF를 DONE으로 이동한다. 점검 보고는 **A/B 진행 → 지팀장 결정·실행(커밋/SHA 또는 미수행 명시) → 차단 RF/CI → 다음 행동** 순서로 간결하게 남긴다. 새 증거가 없으면 NO_CHANGE이며 불필요한 문서 커밋도 금지한다.
