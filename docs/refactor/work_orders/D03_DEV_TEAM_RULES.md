# D03 — Agentra P1.5 개발팀 공통 실행·검증 규칙

> **개발팀 정본.** 시작은 [CURRENT](CURRENT.md), 공통 안전·권한·증거는 [D00](../../ENGINEERING_DELIVERY_POLICY.md), 역할/브랜치는 [D01 Codex](../../../AGENTS.md)·[D02 Claude](../../../CLAUDE.md). PC 런검증팀은 별도 D04. D00과 역할별 문서의 내용을 이곳에 복제하지 않는다.

## 1. 정본·소유권
- P1.5 전체 ROOT→LEAF 범위는 [T00](../architecture/T00_TARGET_TREE.md), RF 93개·소유 파일은 [FILE_COVERAGE](../plan/FILE_COVERAGE_63182ab2.csv), 상태는 [STATUS](../plan/STATUS.md), 건별 인수조건·차단·결정은 **해당 RF**가 정본이다. 동결 V3/P1.5.0~11 기준 유지.
- `integration/p1.5`와 RF/CURRENT/STATUS는 **지팀장 단일 writer**; A/B는 각자 기존 work 브랜치의 소유 파일과 HANDOFF만 수정. 타 RF 파일·공개 공유 계약은 read-only, 별도 소유권/승인 판단 전 변경 금지. 정상적인 브랜치 divergence는 차단 사유가 아니다.
- 시작 시 repo ROOT·checkout·원격 HEAD·정확한 후보 SHA를 확인하고, push 후 원격 HEAD를 재확인한다. 기존 작업장·사용자 데이터 보존. D00 금지 사항은 모든 단계에 우선한다.

## 2. 한 회차 실행 — 실제 코드 진척 우선
- **우선순위:** (1) 실행 가능한 자기 REWORK의 최소 수정·KEEP 실증 또는 재현 가능한 기술 차단 근거, (2) 상대 RF **신규 코드 SHA·위험 경계만** 독립 read-only 검증, (3) 자기 신규 RF 개발. REWORK가 차단되면 같은 회차 다음 실행 가능한 RF로 진행한다. 단순 ACK·기존 상태 재보고는 REWORK 조치가 아니다.
- **지팀장 결정:** 원개발자에게는 해결 방법의 선택을 떠넘기지 않고 허용 경로·구체적 수정/KEEP 조건을 준다. 지팀장은 각 RF 다음 행동을 FIX / KEEP / PEER / INTEGRATE / BLOCKED 중 하나로 확정한다. 반복 GPT_ACTION_REQUIRED는 새 문서·ACK 대신 원인 조사 및 직접 판정으로 해소한다.
- **증거 재사용:** 동일 코드 blob·동일 테스트 반복 금지. 기존 blob parity·normal/-O·peer PASS_SCOPED는 유지한다. 미검증 소비자/호출/State/IO/예외/부작용 **위험 경계만** 표적 offline/mock normal/-O 검증한다. 실패는 BASE와 같은 조건으로 비교해 BASELINE_EXISTING / ENVIRONMENT / CROSS_RF_OWNER / UNKNOWN을 분리한다.
- **완료 전환:** RF 인수조건과 독립 검증이 충족되면 지팀장은 같은 회차 선별 통합·통합 SHA normal/-O·DONE 가능성을 판정한다. 직접 수정분도 상대 독립 peer가 필요하다. 불가능하면 실제 차단과 재개 조건을 해당 RF에 기록한다.
- **조기 종료·NO_CHANGE 게이트(A/B 공통):** 신규 코드 SHA나 상대 신규 증거가 없다는 사실만으로 회차를 종료하지 않는다. CURRENT의 자기 미완료 RF에서 아직 검증되지 않은 허용 owner/소비자/State/IO/예외·효과 경계를 찾아 실제 구현·KEEP 검증을 진행한다. 현재 RF가 차단되면 같은 회차 다음 실행 가능한 자기 RF로 이동한다. 안전·소유권·환경 때문에 모든 허용 작업이 불가능한 경우에만 구체적 차단 대상·근거·해제 조건을 보고한다. 신규 결과가 전혀 없을 때의 NO_CHANGE는 이 탐색과 실행 가능성 판단 후에만 허용하며, 미검증 범위가 남은 상태의 단순 대기·기존 증거 반복을 작업 완료로 보고하지 않는다.
- 소스 수정 시 import·동적 patchability·공개 API·side effect·거래 안전 동등성 및 UI 연결 patchnotes JSON/MD를 확인한다. 테스트 산출물은 격리·정리하며 오라클 변경으로 실패를 숨기지 않는다.

## 3. RF 판정·검증·통합
- RF 큐는 pending → verification/{claude|codex} ↔ rework/{claude|codex} → done. 폴더는 원개발자 기준이며 지팀장만 이동·DONE 판정한다. 이전 파일, 새 파일, CURRENT 링크, STATUS 집계를 함께 점검하고 일부 실패 시 이동 미완료로 기록한다.
- REWORK는 원개발자 소유의 재현된 코드 결함 또는 구체적 계약 미충족에 한정한다. BASE·후보 코드 SHA, 실패 node, 소유자, 허용 경로, FIX/KEEP 조건, 다음 peer를 해당 RF에 기록한다. 기존 BASE 실패, 환경, 타 RF 소유권, 안전 HOLD는 별도 차단으로 분류한다.
- 자체 PASS와 독립 peer PASS를 구별한다. 기존 유효 normal/-O·peer 증거를 재사용하고 신규 코드 SHA와 미검증 위험만 상대 read-only peer가 확인한다. PASS_SCOPED는 전체 PASS가 아니다. 추가 검증 요구에는 구체적인 실패·미충족 계약 근거가 필요하다.
- 전체 인수조건·peer PASS·소유권 승인 후 지팀장은 소유 경로만 integration/p1.5 최신 HEAD에 선별 통합한다. 통합된 정확한 SHA의 필수 normal/-O PASS 후 DONE. KEEP만으로 DONE 아님. 지팀장 수정도 독립 peer 필수.
- hosted CI 상태 조회는 정기 운영과 DONE 필수 조건에서 제외한다. 기존 CI 워크플로·테스트 오라클은 승인 없이 변경하지 않는다.
- RF-001~093 공통 적용. 공통 규칙은 RF마다 복사하지 않는다.

## 4. Git 쓰기 차단 대응
- push·파일 수정이 거절되면 실제 오류를 구분하고 최신 원격 SHA 재조회 → 변경 범위·소유권 확인 → 충돌 해소 또는 허용된 최소 단위 재시도를 수행한다. 성공 시 원격 HEAD와 변경 파일을 검증한다.
- 안전 정책 차단은 우회하지 않는다. 동일 실패를 무한 반복하거나 금지된 강제 push로 전환하지 않는다. 허용된 해결 경로가 없으면 BLOCKED와 정확한 재개 조건을 남기고 다른 실행 가능한 RF를 진행한다.

## 5. 기록·지팀장 책임
- `CURRENT` = **작업 포인터/규칙 변경 알림만**. `RF` = 해당 건의 결정·잔여 증거·재개 조건. `STATUS` = 전체 현황. `HANDOFF_A/B` = **최신 실행 10~20줄만 교체**, 과거는 Git 이력. 새 총괄 문서·반복 일지·빈 커밋 금지.
- HANDOFF는 RUN_ID, 시작/후보 **코드 SHA**(HANDOFF 커밋과 구분), RF별 변경 경로, normal/-O 명령·exit, 독립 verdict, BLOCKED 원인·재개 트리거, patchnotes, GPT_ACTION_REQUIRED, push 확인을 간결히 담는다. **매 실행(예약·수동 강제 포함)마다 코드 변경 유무와 무관하게 HANDOFF 최신 회차를 교체·commit·push한다.** 신규 결과가 없으면 `NO_CHANGE`와 실행 시각/RUN_ID, 시작·종료 원격 코드 SHA, 확인한 미완료 RF·실행 가능성·차단 사유, 실제 명령/NOT_RUN, 다음 행동을 짧게 남긴다. 신규 검증·peer 결과가 있으면 명령·exit·대상 SHA를 반드시 남긴다. HANDOFF-only 커밋은 실행 관측용이며 코드 진척·RF PASS·DONE으로 세지 않는다. 동일 실행의 중복 커밋·장문 반복은 금지한다.
- 지팀장은 매 점검 **CURRENT → A/B 원격 HEAD·최신 HANDOFF → 변경된 RF 증거 → 런검증 [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32) 신규 내용 → STATUS**만 확인. 멈춘 RF는 그 회차에 직접 소유권·원인·최소 다음 행동을 확정하고 실행 가능한 다음 RF로 넘긴다. 새 peer 증거는 같은 회차에 판정하고, 완전 peer PASS는 선별 통합/통합 SHA normal/-O 검증 단계로 즉시 넘긴다. 같은 SHA 전수 재검증·중복 감사 금지.
- 보고는 **A/B 진행 → 지팀장 실제 조치/커밋 → RF·통합 검증 → 다음 행동** 순서. 계획·부분 PASS·NOT_RUN을 DONE으로 보고하지 않는다. 별도 예약 생성/변경은 사용자 승인 없이 하지 않는다.
