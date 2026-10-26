# D03 — Agentra P1.5 개발팀 공통 실행·검증 규칙

> **개발팀 정본.** 시작은 [CURRENT](CURRENT.md), 공통 안전·권한·증거는 [D00](../../ENGINEERING_DELIVERY_POLICY.md), 역할/브랜치는 [D01 Codex](../../../AGENTS.md)·[D02 Claude](../../../CLAUDE.md). PC 런검증팀은 별도 D04. D00과 역할별 문서의 내용을 이곳에 복제하지 않는다.

## 1. 개발 범위·단일 소유
- RF 93개·소유 경로: [FILE_COVERAGE](../plan/FILE_COVERAGE_63182ab2.csv); 대상 트리: [T00](../architecture/T00_TARGET_TREE.md); 인수조건은 각 RF, 집계는 STATUS가 정본이다.
- 역할별 작업 브랜치는 D01/D02, **권한·안전·정책 수신·증거 원칙은 D00만** 따른다. 브랜치 divergence 자체는 결함이 아니다.

## 2. 한 회차 실행 — 실제 코드 진척 우선
- **실행 순서:** (1) 자기 RF 개발·실제 FIX, (2) 다음 자기 RF 연속 개발. 상대 read-only peer는 **새 코드 SHA 또는 기존 peer에서 검증하지 않은 최초 integration 격리 조합**의 새 위험 경계만 수행한다. 동일 SHA·동일 조합 반복 금지. A/B는 CURRENT·자기 D01/D02를 매회 읽고 D00·D03은 최초/변경 시 읽는다. 지팀장은 매회 CURRENT→D00→D03→D01/D02 전체를 읽고 결과 판정·통합을 별도 처리한다. REWORK가 차단되면 같은 회차 다음 실행 가능한 RF로 진행한다. 단순 ACK·기존 상태 재보고는 REWORK 조치가 아니다.
- **지팀장 결정:** 원개발자에게는 해결 방법의 선택을 떠넘기지 않고 허용 경로·구체적 수정/KEEP 조건을 준다. 지팀장은 각 RF 다음 행동을 FIX / KEEP / PEER / INTEGRATE / BLOCKED 중 하나로 확정한다. 반복 GPT_ACTION_REQUIRED는 새 문서·ACK 대신 원인 조사 및 직접 판정으로 해소한다.
- **증거 재사용:** 동일 코드 blob·동일 테스트 반복 금지. 기존 blob parity·normal/-O·peer PASS_SCOPED는 유지한다. 미검증 소비자/호출/State/IO/예외/부작용 **위험 경계만** 표적 offline/mock normal/-O 검증한다. 실패는 BASE와 같은 조건으로 비교해 BASELINE_EXISTING / ENVIRONMENT / CROSS_RF_OWNER / UNKNOWN을 분리한다.
- **완료 전환:** RF 인수조건과 독립 검증이 충족되면 지팀장은 같은 회차 선별 통합·통합 SHA normal/-O·DONE 가능성을 판정한다. 직접 수정분도 상대 독립 peer가 필요하다. 불가능하면 실제 차단과 재개 조건을 해당 RF에 기록한다.
- **연속 실행 확인:** 현재 RF의 scoped PASS·HANDOFF 작성은 다음 RF 미착수의 정당한 종료 사유가 아니다. 각 RUN에서 CURRENT에 적힌 후속 실행 가능한 RF를 실제로 시작하고, 미착수 항목마다 `NOT_STARTED_REASON=TIME_LIMIT|ENV_BLOCK|SAFETY_HOLD|NO_EXECUTABLE_OWNER`와 관측 근거·남은 시간/명령·다음 RF를 HANDOFF에 남긴다. 기록 누락은 `CONTINUATION_UNVERIFIED`이며 완료 처리 금지. 정책을 읽었다는 주장만으로 준수 PASS가 되지 않는다.
- **연속 작업 종료 기준:** 예약/수동 실행 모두 환경 한도 내에서 자기 FIX/개발 → 신규 상대 SHA 또는 최초 미검증 격리 조합이 있을 때만 peer → 다음 자기 RF를 계속 소비한다. 단일 PASS·HANDOFF·ACK·상대 SHA 부재는 종료 조건이 아니다. 실행 가능한 owner 작업이 없거나 실행 한도에 도달한 경우에만 종료하고 남은 작업·해제 조건을 남긴다. 50~55분 목표는 강제 체류 시간이 아니며 시간을 채우기 위한 반복 검증 금지.
- 소스 수정 시 import·동적 patchability·공개 API·side effect·거래 안전 동등성 및 UI 연결 patchnotes JSON/MD를 확인한다. 테스트 산출물은 격리·정리하며 오라클 변경으로 실패를 숨기지 않는다.

## 2A. 간결한 지시와 차단 분리
- 안전 검토는 파일 전체가 아닌 구체적인 실행 경로와 외부 효과를 기준으로 판정한다. 정적 읽기·AST·소비자 분석은 지속하며, 위험 명령은 실행하지 않고 다른 허용된 owner 작업을 계속한다. 격리 mock은 외부 부작용이 없음을 확인한 범위에서만 진행한다. D00의 승인 필요 변경·실거래·배포 안전 경계는 유지한다.
- CURRENT는 A/B/지팀장의 **이번 회차 실제 실행 지시판**이다. 담당·RF 순서·즉시 수행할 수정/검증·구체 차단/우회·다음 행동·정본 링크를 짧게 표시한다. A/B는 CURRENT만 읽어 작업을 착수할 수 있어야 하며, 세부 계약은 링크된 RF가 정본이다. 지팀장은 예약 회차마다 증거를 회수해 판정·가능한 선별 통합·다음 작업 갱신을 직접 수행한다. 검사·ACK·HANDOFF만으로 종료하지 않고 안전하게 가능한 코드 진척 또는 RF 게이트 해소를 시도한다. 종료된 회차의 반복 지시·오래된 상태는 최소 증거 SHA만 남기고 축약하며, 공통 정책을 RF마다 복제하지 않는다.

## 2B. 지팀장 대화 기반 자가 개선
- 사용자와의 대화에서 드러난 잘못된 판단·누락·비효율·반복 차단도 운영 개선 증거로 취급한다. 지적 전에 A/B 작업 누락, 정책 수신, RF 물리 큐·STATUS, 독립 peer 배정, 선별 통합, 불필요한 재검증을 자체 감사한다.
- 오류는 증상뿐 아니라 원인이 된 판단·문서·절차를 확인한다. 기존 규칙으로 해결 가능하면 새 규칙을 늘리지 않고 **실제 배정·판정·큐 정합성부터 수정**한다. 반복되는 구조적 문제만 해당 정본 한 곳에 최소 반영한다.
- 다음 실행에서 이전 개선이 실제 적용됐는지 증거로 확인하고, 같은 문제가 재발하면 원인을 다시 분석한다. 문서·ACK가 아닌 코드 SHA 진척, RF 종결, 재작업 감소, 검증 효율, 통합 성공으로 효과를 측정한다. D00 권한·안전 경계와 A/B 실행·지팀장 판정 분리는 유지한다.

## 2C. 지팀장 정책 변경 임시 재수신 지시
- D00·D03·D01·D02 또는 CURRENT의 실행 정책이 변경되면 지팀장은 변경 문서별 원격 blob SHA와 적용 대상(A/B)을 확인하고, CURRENT 상단에 `POLICY_REREAD_REQUIRED` 임시 항목(문서 경로·SHA·대상·수신 상태)을 직접 삽입한다. 기존 D00의 매회 원격 SHA 비교 의무는 그대로 유지한다.
- 지팀장은 다음 A/B HANDOFF의 `POLICY_READ_SHA`·`POLICY_REREAD`·`POLICY_APPLIED_OR_DEFERRED`와 실제 후속 작업을 대조한다. 읽기 ACK만으로 수신 완료로 판정하지 않는다. 미수신 팀의 항목은 남기고, 수신·적용이 확인된 팀만 완료 표시한다.
- 대상 팀 전부가 해당 SHA를 읽고 적용(또는 구체적 안전 이월)한 사실을 지팀장이 확인한 뒤 CURRENT의 임시 항목을 직접 제거한다. 제거 자체는 코드 진척이나 RF DONE이 아니다. 지팀장 실행에서 이를 누락하면 정책 배포는 미완료다.

## 3. RF 판정·검증·통합
- RF 큐는 pending → verification/{claude|codex} ↔ rework/{claude|codex} → done. REWORK 원인이 해결되면 해당 실패를 종결하고, RF 전체 인수조건과 통합 SHA 검증도 충족되면 같은 회차 DONE으로 이동한다. 폴더는 원개발자 기준이며 지팀장만 이동·DONE 판정한다. 이전 파일, 새 파일, CURRENT 링크, STATUS 집계를 함께 점검하고 일부 실패 시 이동 미완료로 기록한다.
- REWORK는 원개발자 소유의 재현된 코드 결함 또는 구체적 계약 미충족에 한정한다. BASE·후보 코드 SHA, 실패 node, 소유자, 허용 경로, FIX/KEEP 조건, 다음 peer를 해당 RF에 기록한다. 기존 BASE 실패, 환경, 타 RF 소유권, 안전 HOLD는 별도 차단으로 분류한다.
- 자체 PASS와 독립 peer PASS를 구별한다. 기존 유효 normal/-O·peer 증거를 재사용하고 새 코드 SHA 또는 최초 미검증 격리 조합의 새 위험만 상대 read-only peer가 확인한다. PASS_SCOPED는 전체 PASS가 아니다. 추가 검증 요구에는 구체적인 실패·미충족 계약 근거가 필요하다.
- 전체 인수조건·peer PASS·소유권 승인 후 지팀장은 소유 경로만 integration/p1.5 최신 HEAD에 선별 통합한다. 통합된 정확한 SHA의 필수 normal/-O PASS 후 DONE. KEEP만으로 DONE 아님. 지팀장 수정도 독립 peer 필수.
- hosted CI 상태 조회는 정기 운영과 DONE 필수 조건에서 제외한다. 기존 CI 워크플로·테스트 오라클은 승인 없이 변경하지 않는다.
- RF-001~093 공통 적용. 공통 규칙은 RF마다 복사하지 않는다.

## 3A. FIX→PEER→INTEGRATE 운영
- 배정된 독점 owner 범위 내 구현은 사전 승인 대기 없이 commit/push한다. 원인 소유자의 재현 FAIL은 다음 실행 첫 작업으로 최소 FIX/KEEP SHA를 제출한다. 교차 소유·안전 경계는 변경하지 않고 차단과 다음 가능한 owner 작업을 분리한다.
- 상대는 **새 source SHA 또는 최초 미검증 integration 격리 조합의 새 위험만** read-only normal/-O peer한다. FAIL이면 원인 SHA·node·재현·소유자·수정조건을 전달하고, PASS_SCOPED면 범위를 한정한다. 같은 증거 재검증이나 ACK 왕복 금지.
- 지팀장은 새 peer 결과를 해당 RF에 FIX/KEEP/PEER/INTEGRATE/BLOCKED로 즉시 판정하고 승인 owner 변경만 integration 최신 HEAD에 선별 반영한다. 통합 exact SHA 필수 검증 PASS 및 RF 인수조건 전부 충족 시에만 DONE. 실행 불가한 테스트는 NOT_RUN으로 남긴다.

## 3B. 지팀장 통합 누락 방지 강제 게이트
- **트리거:** 새 A/B source SHA의 독립 peer 결과가 도착하거나 기존 REWORK가 해결된 모든 회차. 보고·CURRENT/RF 갱신 전에 반드시 아래 단계를 완료하거나 각 단계의 기술적 불가 사유를 기록한다.
- **1. 차분 판정:** 최신 integration HEAD와 후보 SHA의 owner 파일 diff를 확인하고 각 파일을 `ADMIT` / `KEEP_NOOP` / `REJECT`로 분류한다. 전체 브랜치 divergence·다른 RF 실패는 해당 owner 변경의 격리 테스트 생략 사유가 아니다.
- **2. 격리 적용(실행 주체):** 지팀장은 후보·적용 경로·금지 범위·검증 조건을 결정하고, A/B 중 해당 실행 권한과 격리 환경을 가진 담당자에게 실제 적용·검증을 배정한다. 새 조합의 최초 독립 peer는 반대 팀이 read-only로 수행하며 기존 동일 SHA·동일 조합 증거는 재사용한다. 지팀장의 GitHub-only 환경은 A/B 실행 가능한 테스트를 `BLOCKED_ENV`로 고정할 근거가 아니다. ADMIT 후보만 최신 integration 기반 격리 작업장에 적용한다. 권한·안전·소유 경계를 확인하고, 적용 불가 시 파일·오류·해제 조건을 남긴다. KEEP_NOOP는 SHA/내용 동일 근거를 기록한다.
- **3. 필수 검증(책임 분리):** 배정받은 A/B가 격리 후보의 변경 영향 테스트와 동결 필수 normal/-O를 실행하고, 지팀장은 명령·exit·대상 SHA·독립성·오라클 불변을 검토해 수용 여부를 판정한다. **integration 브랜치 쓰기·RF 최종 DONE은 지팀장만 수행**한다. 반영 exact SHA의 필수 검증도 실행 가능한 A/B에 재배정할 수 있으나 지팀장이 결과와 SHA를 최종 확인한다. PASS면 승인된 owner 경로만 integration에 선별 반영하고 **반영된 정확한 integration SHA**를 normal/-O 재검증한다. FAIL은 BASE 대비 신규 회귀·기존 실패를 구분한다. 테스트를 실제 실행하지 않았다면 `NOT_RUN`이며 통합 승인/DONE 금지.
- **4. 종료 판정:** 각 후보를 `INTEGRATED_VERIFIED` / `KEEP_NOOP_VERIFIED` / `REWORK` / `BLOCKED_ENV` / `BLOCKED_SAFETY` / `NOT_RUN` 중 하나로 확정하고 다음 owner·명령·재개 조건을 RF에 남긴다. **문서 커밋, peer PASS, CURRENT 갱신만으로 회차 종료 금지.** 실제 도구/작업장 부재 시 우선 사용 가능한 GitHub/격리 실행 경로를 확인하고, 없으면 정확한 미실행 단계와 환경 제공 조건을 기록한다. 절차상 체크 완료를 소스 진척으로 계산하지 않는다.
- **5. 대시보드 일치:** CURRENT에는 위 결과 상태·코드 SHA·다음 행동만 반영한다. RF의 판정과 CURRENT의 상태가 서로 다르면 회차 미완료. `DONE`은 D00 권한과 D03 전체 인수조건을 모두 충족한 경우에만 허용한다.

## 4. Git 쓰기 차단 대응
- push·파일 수정이 거절되면 실제 오류를 구분하고 최신 원격 SHA 재조회 → 변경 범위·소유권 확인 → 충돌 해소 또는 허용된 최소 단위 재시도를 수행한다. 성공 시 원격 HEAD와 변경 파일을 검증한다.
- 안전 정책 차단은 우회하지 않는다. 동일 실패를 무한 반복하거나 금지된 강제 push로 전환하지 않는다. 허용된 해결 경로가 없으면 BLOCKED와 정확한 재개 조건을 남기고 다른 실행 가능한 RF를 진행한다.

## 5. 최소 보고·큐 갱신
- **CURRENT는 간결한 실행 지시판:** D00/D01/D02/D03·STATUS 및 활성 RF/HANDOFF 링크, 담당별 RF 우선순위·현재 차단·이번 회차 필수 실제 조치·다음 행동을 표시한다. 변경 정책은 핵심 적용 지시 1~3줄과 변경 SHA만 임시로 싣고 수신 확인 후 지팀장이 회수한다. 안전·권한 정본이나 RF 상세 계약을 복제하지 않는다.
- A/B는 실행 종료 시 최신 HANDOFF를 한 번 갱신·push하고 자기 Issue(A #11/B #12)에 RUN_ID당 완료 댓글 한 건을 남긴다. 필수 필드: `POLICY_REMOTE_START_SHA`(CURRENT/D00/D03/역할별), `POLICY_READ_SHA`, `POLICY_REMOTE_END_SHA`, `POLICY_CHANGED`, `POLICY_REREAD`, `POLICY_APPLIED_OR_DEFERRED`, `CONTINUATION_STATUS`, 후속 RF별 `NOT_STARTED_REASON`(미착수 시), RUN_ID, 실제 source SHA(없으면 NO_CHANGE), 변경 owner 경로, 신규 명령·exit/NOT_RUN, peer 범위, BLOCKED 재개 조건, 다음 행동, push 확인. 과거 설명·동일 traceback·전체 테스트 목록 반복 복사 금지. HANDOFF-only는 코드 진척이 아니다.
- 지팀장은 CURRENT → A/B 최신 source SHA·HANDOFF/Issue → 해당 RF 신규 증거 → STATUS 순으로 확인하고, 결과를 A/B 코드 진척 → 실제 판정·통합 SHA → RF/통합 검증 → 다음 행동 순으로 보고한다. 별도 예약 생성·변경은 사용자 승인 없이 하지 않는다.
