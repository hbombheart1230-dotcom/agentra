# D03 — Agentra P1.5 개발팀 공통 실행·검증 규칙

> **개발팀 정본.** 시작은 [CURRENT](CURRENT.md), 공통 안전·권한·증거는 [D00](../../ENGINEERING_DELIVERY_POLICY.md), 역할/브랜치는 [D01 Codex](../../../AGENTS.md)·[D02 Claude](../../../CLAUDE.md). PC 런검증팀은 별도 D04. D00과 역할별 문서의 내용을 이곳에 복제하지 않는다.

## 1. 정본·소유권
- P1.5 전체 ROOT→LEAF 범위는 [T00](../architecture/T00_TARGET_TREE.md), RF 93개·소유 파일은 [FILE_COVERAGE](../plan/FILE_COVERAGE_63182ab2.csv), 상태는 [STATUS](../plan/STATUS.md), 건별 인수조건·차단·결정은 **해당 RF**가 정본이다. 동결 V3/P1.5.0~11 기준 유지.
- `integration/p1.5`와 RF/CURRENT/STATUS는 **지팀장 단일 writer**; A/B는 각자 기존 work 브랜치의 소유 파일과 HANDOFF만 수정. 타 RF 파일·공개 공유 계약은 read-only, 별도 소유권/승인 판단 전 변경 금지. 정상적인 브랜치 divergence는 차단 사유가 아니다.
- 시작 시 repo ROOT·checkout·원격 HEAD·정확한 후보 SHA를 확인하고, push 후 원격 HEAD를 재확인한다. 기존 작업장·사용자 데이터 보존. D00 금지 사항은 모든 단계에 우선한다.

## 2. 한 회차 실행 — 실제 코드 진척 우선
- **정책 최신성 필수 게이트:** 매 실행 시작 시 CURRENT의 `POLICY_NOTICE`와 integration 원격 D00·D03·D01(B)/D02(A)의 최신 blob SHA를 확인하고, 이전 회차 HANDOFF에 기록된 읽은 SHA와 비교한다. SHA가 달라진 문서는 반드시 새 본문을 읽고 변경된 규칙을 적용한 뒤 작업한다. SHA가 같으면 기존 본문 재사용 가능. 읽기 실패 시 이전 정책을 임의 적용하여 완료 처리하지 말고 재시도하고 BLOCKED 원인을 기록한다. HANDOFF에 `POLICY_SHA_BEFORE/AFTER`, `POLICY_CHANGED`, `POLICY_READ=PASS/BLOCKED`를 기록한다.

- **우선순위:** (1) 실행 가능한 자기 REWORK의 최소 수정·KEEP 실증 또는 재현 가능한 기술 차단 근거, (2) 상대 RF **신규 코드 SHA·위험 경계만** 독립 read-only 검증, (3) 자기 신규 RF 개발. REWORK가 차단되면 같은 회차 다음 실행 가능한 RF로 진행한다. 단순 ACK·기존 상태 재보고는 REWORK 조치가 아니다.
- **지팀장 결정:** 원개발자에게는 해결 방법의 선택을 떠넘기지 않고 허용 경로·구체적 수정/KEEP 조건을 준다. 지팀장은 각 RF 다음 행동을 FIX / KEEP / PEER / INTEGRATE / BLOCKED 중 하나로 확정한다. 반복 GPT_ACTION_REQUIRED는 새 문서·ACK 대신 원인 조사 및 직접 판정으로 해소한다.
- **증거 재사용:** 동일 코드 blob·동일 테스트 반복 금지. 기존 blob parity·normal/-O·peer PASS_SCOPED는 유지한다. 미검증 소비자/호출/State/IO/예외/부작용 **위험 경계만** 표적 offline/mock normal/-O 검증한다. 실패는 BASE와 같은 조건으로 비교해 BASELINE_EXISTING / ENVIRONMENT / CROSS_RF_OWNER / UNKNOWN을 분리한다.
- **완료 전환:** RF 인수조건과 독립 검증이 충족되면 지팀장은 같은 회차 선별 통합·통합 SHA normal/-O·DONE 가능성을 판정한다. 직접 수정분도 상대 독립 peer가 필요하다. 불가능하면 실제 차단과 재개 조건을 해당 RF에 기록한다.
- **시간 예산 기반 연속 작업(A/B 공통, 예약·수동 강제 실행):** 회차는 단일 검증/단일 RF 단위가 아니라 연속 개발 세션이다. 1시간 주기 작업의 기본 목표는 가능한 경우 회차당 약 50~55분의 실질 작업이며, 실행 환경의 시간·토큰·도구 한도나 다음 예약과의 중첩 위험이 있으면 그 한도 안에서 최대한 진행한다. 1개 테스트 PASS, KEEP 근거 1건, peer 완료, 코드 변경 없음, HANDOFF 기록, 상대 신규 SHA 없음은 종료 조건이 아니다. 각 작업 직후 미검증 owner/소비자/State/IO·효과 경계 → 다음 자기 RF → 허용된 독립 peer 순으로 실행 가능한 작업을 계속 선택하고, 완료한 범위와 다음 미완료 범위를 구분한다. 위험 launcher 실행, 권한 없는 수정, 무승인 오라클·안전 계약 변경은 시간 목표를 이유로 허용되지 않는다. 허용된 모든 작업이 실제로 소진·차단되었거나 실행 환경 한도에 도달한 경우에만 조기 종료하며, 경과 시간·수행 작업 수·남은 작업·종료 사유를 HANDOFF에 남긴다. 시간만 채우기 위한 동일 증거 반복·불필요한 테스트는 금지한다.
- **조기 종료·NO_CHANGE 게이트(A/B 공통):** 신규 코드 SHA나 상대 신규 증거가 없다는 사실만으로 회차를 종료하지 않는다. CURRENT의 자기 미완료 RF에서 아직 검증되지 않은 허용 owner/소비자/State/IO/예외·효과 경계를 찾아 실제 구현·KEEP 검증을 진행한다. 현재 RF가 차단되면 같은 회차 다음 실행 가능한 자기 RF로 이동한다. 안전·소유권·환경 때문에 모든 허용 작업이 불가능한 경우에만 구체적 차단 대상·근거·해제 조건을 보고한다. 신규 결과가 전혀 없을 때의 NO_CHANGE는 이 탐색과 실행 가능성 판단 후에만 허용하며, 미검증 범위가 남은 상태의 단순 대기·기존 증거 반복을 작업 완료로 보고하지 않는다.
- 소스 수정 시 import·동적 patchability·공개 API·side effect·거래 안전 동등성 및 UI 연결 patchnotes JSON/MD를 확인한다. 테스트 산출물은 격리·정리하며 오라클 변경으로 실패를 숨기지 않는다.

## 3. RF 판정·검증·통합
- RF 큐는 pending → verification/{claude|codex} ↔ rework/{claude|codex} → done. REWORK 원인이 해결되면 해당 실패를 종결하고, RF 전체 인수조건과 통합 SHA 검증도 충족되면 같은 회차 DONE으로 이동한다. 폴더는 원개발자 기준이며 지팀장만 이동·DONE 판정한다. 이전 파일, 새 파일, CURRENT 링크, STATUS 집계를 함께 점검하고 일부 실패 시 이동 미완료로 기록한다.
- REWORK는 원개발자 소유의 재현된 코드 결함 또는 구체적 계약 미충족에 한정한다. BASE·후보 코드 SHA, 실패 node, 소유자, 허용 경로, FIX/KEEP 조건, 다음 peer를 해당 RF에 기록한다. 기존 BASE 실패, 환경, 타 RF 소유권, 안전 HOLD는 별도 차단으로 분류한다.
- 자체 PASS와 독립 peer PASS를 구별한다. 기존 유효 normal/-O·peer 증거를 재사용하고 신규 코드 SHA와 미검증 위험만 상대 read-only peer가 확인한다. PASS_SCOPED는 전체 PASS가 아니다. 추가 검증 요구에는 구체적인 실패·미충족 계약 근거가 필요하다.
- 전체 인수조건·peer PASS·소유권 승인 후 지팀장은 소유 경로만 integration/p1.5 최신 HEAD에 선별 통합한다. 통합된 정확한 SHA의 필수 normal/-O PASS 후 DONE. KEEP만으로 DONE 아님. 지팀장 수정도 독립 peer 필수.
- hosted CI 상태 조회는 정기 운영과 DONE 필수 조건에서 제외한다. 기존 CI 워크플로·테스트 오라클은 승인 없이 변경하지 않는다.
- RF-001~093 공통 적용. 공통 규칙은 RF마다 복사하지 않는다.

## 3A. 자율 개발·REWORK 핑퐁·가시성
- **사전 컨펌 최소화:** 이미 배정된 RF의 독점 소유 파일 및 D00 안전 경계 안에서 A/B는 지팀장 매회 승인을 기다리지 않고 실제 소스 수정·테스트·commit·push를 연속 수행한다. 새로운 공유 소유권, 안전 계약, 실거래, 동결 오라클 변경만 지팀장/사용자 승인 경계로 분리한다.
- **REWORK 즉시 우선:** 상대 검증 FAIL로 재현 가능한 owner-local 결함이 확인되면 지팀장이 해당 RF에 FAIL node·검증 SHA·수정 소유자·허용 경로·합격 조건을 기록한다. 원개발자는 다음 회차 첫 작업으로 해당 RF의 **실제 코드 수정 SHA**를 제출한다. 상대는 새 SHA의 실패 경계만 독립 재검증하고 결과를 자신의 Issue 및 상대 Issue에 전달한다. FAIL이면 같은 RF에서 FIX→PEER를 반복하고, PASS이면 지팀장이 통합/잔여 인수조건을 판정한다. 소스 수정 없이 동일 SHA의 ACK/커버리지 반복은 REWORK 해소로 인정하지 않는다.
- **상세 보고:** 매 RUN_ID별 GitHub Issue #11(A)/#12(B)에 변경 파일·함수·전후 동작·코드 SHA·명령/exit·실패 traceback 또는 실패 node·REWORK 원인·수정 시도·재검증 결과·미완료 인수조건·다음 owner/action을 빠짐없이 기록한다. 분량 제한 없음. HANDOFF에도 재현 가능한 상세 근거와 최종 답변을 기록한다. 다른 팀이 조치해야 하는 FAIL은 상대 Issue에도 동일 RF·SHA·재현 조건·요구 행동을 명시한다.
- **지팀장 책임:** 두 Issue/HANDOFF의 신규 RUN_ID를 대조해 각 RF의 FIX/PEER/REWORK/INTEGRATE/DONE 결정을 정본 RF에 기록하고 상대에게 재전달한다. REWORK 수정 지시가 이미 승인된 소유 경계 내라면 추가 컨펌을 만들지 않는다. 진척은 검증 건수가 아니라 **새 소스 SHA, 해결된 FAIL node, 상대 재검증, RF 종결, 통합 SHA**로 보고한다.

## 3B. 회차 종료 및 실패 전달의 강제 조건
- A/B는 상대의 새 SHA가 없어도 자기 RF 소유 범위의 실제 구현 또는 미충족 인수조건 종결을 계속한다. 이미 확인한 동일 SHA PASS·BASELINE 미재실행·정적 읽기 1건만으로 세션 종료할 수 없다.
- 재현된 자기 브랜치 회귀는 RF 번호와 관계없이 원인 소유자에게 즉시 전달한다. 원인 RF와 발견 RF를 분리 기록하고, 안전한 자기 소유 경로에서는 기존 승인 범위 안에서 FIX/KEEP 원복을 즉시 수행한다. 교차 소유 파일은 임의 수정하지 않고 최소 파일·소비자·필요 승인만 기록한 뒤 다른 실행 가능한 owner 작업을 진행한다.
- 다음 회차 첫 작업은 (1) 미해결 owner-local FAIL의 실제 FIX/KEEP SHA, (2) 새 상대 SHA peer, (3) 다음 자기 owner 코드 작업 순서다. 조기 종료 시 실행 가능한 owner 작업이 없다는 파일별 근거와 실행 환경 한도를 함께 남긴다. 반복된 GPT_ACTION_REQUIRED만으로 종료하지 않는다.
- 정책 갱신 수신 여부는 각 HANDOFF의 읽은 blob SHA와 Issue 댓글로 확인한다. 최신 지시를 읽지 않은 실행은 정책 적용 완료로 보지 않는다. Issue 댓글은 송신 증거이고 상대 수신·실행 증거가 아니므로 새 소스 SHA와 독립 peer 결과를 별도로 확인한다.

## 4. Git 쓰기 차단 대응
- push·파일 수정이 거절되면 실제 오류를 구분하고 최신 원격 SHA 재조회 → 변경 범위·소유권 확인 → 충돌 해소 또는 허용된 최소 단위 재시도를 수행한다. 성공 시 원격 HEAD와 변경 파일을 검증한다.
- 안전 정책 차단은 우회하지 않는다. 동일 실패를 무한 반복하거나 금지된 강제 push로 전환하지 않는다. 허용된 해결 경로가 없으면 BLOCKED와 정확한 재개 조건을 남기고 다른 실행 가능한 RF를 진행한다.

## 5. 기록·지팀장 책임
- `CURRENT` = **작업 포인터/규칙 변경 알림만**. `RF` = 해당 건의 결정·잔여 증거·재개 조건. `STATUS` = 전체 현황. `HANDOFF_A/B` = **최신 실행의 상세 기술 보고(분량 제한 없음)**, 과거는 Git 이력. 새 총괄 문서·반복 일지·빈 커밋 금지.
- HANDOFF는 RUN_ID, 시작/후보 **코드 SHA**(HANDOFF 커밋과 구분), RF별 변경 경로, normal/-O 명령·exit, 독립 verdict, BLOCKED 원인·재개 트리거, patchnotes, GPT_ACTION_REQUIRED, push 확인을 간결히 담는다. **매 실행(예약·수동 강제 포함)마다 코드 변경 유무와 무관하게 HANDOFF 최신 회차를 교체·commit·push한다.** 신규 결과가 없으면 `NO_CHANGE`와 실행 시각/RUN_ID, 시작·종료 원격 코드 SHA, 확인한 미완료 RF·실행 가능성·차단 사유, 실제 명령/NOT_RUN, 다음 행동을 짧게 남긴다. 신규 검증·peer 결과가 있으면 명령·exit·대상 SHA를 반드시 남긴다. **각 회차의 최종 사용자용 작업 완료 답변을 HANDOFF에 구체적으로 수록하고, 해당 담당 GitHub Issue(A #11, B #12)에 같은 RUN_ID의 완료 댓글을 1회 append한다.** Issue는 누적 실행 이력, HANDOFF는 최신 회차 및 Git 이력으로 관리한다. 댓글에는 시작·종료 시각/실질 작업 시간, 연속 처리 작업 수, 실제 코드 SHA/변경 파일, RF별 PASS_SCOPED/FAIL/BLOCKED/NOT_RUN, 다음 작업, 조기 종료 이유, HANDOFF 링크, push 검증 결과를 담는다. 코드 변경 0·NO_CHANGE·push 실패도 보고 의무가 사라지지 않는다. push 실패 시 Issue 댓글로 실패 사유를 남기고, Issue 댓글 실패 시 HANDOFF에 오류를 남긴다. 둘 다 실패하면 최종 답변에 전송 실패를 명시한다. 동일 RUN_ID 중복 댓글 금지. HANDOFF-only 커밋은 실행 관측용이며 코드 진척·RF PASS·DONE으로 세지 않는다. 동일 실행의 중복 커밋과 근거 없는 내용 반복은 금지하되 필요한 코드 diff·실패 traceback·수정 지시·재검증·결과 상세 기록은 길이 제한 없이 허용한다.
- 지팀장은 매 점검 **CURRENT → A/B 원격 HEAD·최신 HANDOFF → 변경된 RF 증거 → 런검증 [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32) 신규 내용 → STATUS**만 확인. 멈춘 RF는 그 회차에 직접 소유권·원인·최소 다음 행동을 확정하고 실행 가능한 다음 RF로 넘긴다. 새 peer 증거는 같은 회차에 판정하고, 완전 peer PASS는 선별 통합/통합 SHA normal/-O 검증 단계로 즉시 넘긴다. 같은 SHA 전수 재검증·중복 감사 금지.
- 보고는 **A/B 진행 → 지팀장 실제 조치/커밋 → RF·통합 검증 → 다음 행동** 순서. 계획·부분 PASS·NOT_RUN을 DONE으로 보고하지 않는다. 별도 예약 생성/변경은 사용자 승인 없이 하지 않는다.
