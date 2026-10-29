# D00 — Agentra P1.5 단일 실행·권한 계약

**정본:** `integration/p1.5`. 이 문서는 **지팀장 C03~C05의 작업 설계·안전·수용 정본**이다. A/B는 개별 회차 실행 명령인 C01/C02만 진입점으로 읽으며, 이 문서나 RF/큐를 매회 재독하지 않는다. 지팀장이 필요한 보호 조건을 작업별 명령서에 명시한다. 작업 지시: [C01](C01_CODEX_CURRENT.md) Codex B · [C02](C02_CLAUDE_CURRENT.md) Claude A · [C03](C03_LEAD_TRIAGE_CURRENT.md) 지팀장 배정 · [C04](C04_LEAD_INTEGRATION_CURRENT.md) 통합/CI · [C05](C05_LEAD_CLOSEOUT_CURRENT.md) 최종 STATUS. 구 핸드오프와 회차별 문서는 역사 자료이며 새 보고 경로가 아니다.

## 1. 진입점·원격 보고의 단일 정본
| 담당 | 소스 작업 브랜치 | **새 결과의 유일한 보고 위치** |
|---|---|---|
| Claude A | `work/p15-a-reporter-pure-20261021` | [Issue #11](https://github.com/hbombheart1230-dotcom/agentra/issues/11) 댓글 |
| Codex B | `work/p15-b-operator-structure-20261022` | [Issue #12](https://github.com/hbombheart1230-dotcom/agentra/issues/12) 댓글 |
| RunLab | 별도 관측 환경(개발 브랜치 금지) | [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32) 댓글 |
| 지팀장 C03/C04/C05 | `integration/p1.5` | [Issue #36](https://github.com/hbombheart1230-dotcom/agentra/issues/36) 판정·변경 **출력 전용** |

- 지팀장의 외부 delta 입력은 **#11·#12·#32 최근 신규 댓글 3곳만**이다. 읽은 댓글 ID/시각 이후의 새 사실만 처리한다. #36은 결과 발행처이며 네 번째 필수 입력이 아니다. 최초 정합성 확인이나 사건 참조가 필요할 때만 원본 RF·코드·CI·STATUS를 선택적으로 열며 매회 전수 재독 금지.
- A/B는 **자신의 기존 브랜치에서 소스 코드·코드 테스트만 수정/커밋/푸시**한다. 문서·Markdown·CSV·RF 원본·큐·STATUS·CURRENT·HANDOFF·patchnotes·manifest·policy·GitHub Issue 본문 수정은 **지팀장 독점**이다. A/B는 자기 이슈 **댓글만 작성**하고, 문서·patchnotes가 필요하면 해당 코드 SHA를 근거로 지팀장에 요청한다. 과거 HANDOFF는 읽기 전용 이력이며 절대 갱신하지 않는다.
- 지팀장 C03은 코드 검토·실행할 파일/함수/수정·이동 방법/상대 SHA 검증을 구체적으로 결정·C01/C02 작성하며 RunLab 접수와 작업 진입점 수정을 맡고, C04는 승인된 최소 소스 선별 통합·정확 SHA CI, C05는 RF C1~C7 판정·RF 원본/큐/STATUS·LEAD_CURRENT 단일 작성자다. **문서 수정 권한은 지팀장에게만** 있고 C03~C05 사이에서도 같은 대상의 동시 쓰기를 금지한다. 지팀장이 코드 통합을 수행할 때만 `integration/p1.5` 소스를 수정한다.
**C01~C05 지시서 갱신 책임(필수):** C03은 #11·#12·#32 신규 결과와 실제 원본 코드·소유권·보호 경계를 직접 분석하고 **C01(B), C02(A)**를 다음 회차에 수행할 정확한 파일·함수·구체 수정/이동/검증/상대 SHA·커밋·푸시 명령으로 작성·교체·푸시한다. C03 자신 문서는 자신의 작업 설계 규칙이 실질적으로 변할 때만 갱신한다. C01/C02에는 RF 번호, 큐 탐색, D00 재독, 장황한 과거 기록, 자율 작업 선정을 넣지 않는다. C04는 LEAD 후보·통합/CI 근거가 바뀌면 **C04 본인 문서**를, C05는 RF 단계·체크·DONE/STATUS가 바뀌면 **C05 본인 문서**를 같은 실행에서 수정·푸시한다. **다른 담당의 C파일을 수정하지 않는다. A/B의 어떤 문서 쓰기도 금지.** 세 담당은 변경 후 원격 파일을 재조회하고 다음 예약이 바로 실행 가능한 최신 지시인지 확인한다. 변화가 없으면 C파일 수정·문서 커밋 0. 과거 기록을 누적하지 않고 기존 행을 교체하며 내용은 실행 순서·차단 조건·다음 안전 RF만 유지한다.

- A/B의 **C01/C02에 명시된** 구현·테스트·반대 peer·자기 브랜치 커밋/푸시는 사전 승인된 작업이다. 지정된 **모든 항목을 각각 필수 과제로 수행**한다. 번호는 순서/선택권을 뜻하지 않으며, 첫 PASS·커밋·부분 장애로 종료하지 않는다. 한 과제가 막히면 **다른 안전한 지정 과제 전부를 계속** 수행한다. 새 작업은 A/B가 고르지 않고 C03이 다음 회차 명령서에 쓴다. 작업별 명령서가 위험·권한 조건을 명시하지 못한 경우 불명확한 효과를 실행하지 말고 지팀장에 즉시 차단 사실을 알린다. `NO_DELTA`는 지정된 안전 작업이 실제로 모두 완료·차단되고 새 명령도 없을 때만 적는다. Git 인증 실패·pytest 부재는 `BLOCKED`이며 `PUSH_VERIFIED` 아님.

## 1.1 작업 원본 탐색·승인 (지팀장 전담)
- **C03/C05**는 `origin/integration/p1.5`에서 현재 RF 원본의 정확한 경로·단계·Owner·독점 파일 범위 및 C1~C7을 조회한다. C03은 코드·테스트·호출자·효과와 기존 증거를 확인하고 A/B가 수행할 **개별 파일·함수·수정/이동/검증 단계**만 C01/C02에 작성한다. 다른 Owner/보호 코드 변경이 필요하면 C03/C05 권한 판단 전 지시하지 않는다.
- **A/B는 C01/C02 단일 진입점만 읽는다.** D00·CURRENT·RF 원본·큐 탐색은 작업자가 매회 할 일이 아니다. 지팀장이 현재 단계, 안전 조건, 허용 범위와 상대 검증 SHA를 누락 없이 전달할 책임이 있다. 실행 중 새 지시로 바뀌어도 시작 때 읽은 작업을 끝내거나 실제 한도를 기록한 뒤 다음 회차에 반영한다.
- **C05**는 정확 SOURCE SHA·독립 peer·C1~C7 근거로 실제 단계와 STATUS를 수용·종결한다. A/B가 RF Markdown·체크박스·큐·CSV·STATUS를 수정하거나 옮기지 않는다. C04의 통합·CI 및 C05의 DONE 권한은 그대로 유지한다.

## 2. 수용·RF 단계 정본 (완화 금지)
- 원본 RF의 작업 목표/원래 `## DONE 체크` C1~C7이 기준이다. C1=모든 owner 파일 MOVE/KEEP/WRAPPER/SAFETY_HOLD 행동 근거, C2=원래 import/caller/IO/State/예외/효과 동등성, C3=원래 normal/`python -O` 테스트·음성/실패 계약, C4=**반대 팀의 정확 SOURCE SHA 전체 원래 범위 독립 PASS**, C5=코드/UI/소유권 관련 patchnotes·메타 정합성(비적용 시 근거 있는 N/A), C6=승인된 최소 통합 또는 source 동일성 KEEP + 해당 source/commit SHA에 요구되는 CI, C7=RF 원본 체크·실제 DONE 이동·STATUS 동기화.
- 상태는 `MET`, 사유 있는 `N/A`, `PARTIAL`, `PENDING`, `MISSING`, `SAFETY_BLOCKED`. `SCOPED_PASS`와 Owner self-pass는 C4 전체 PASS가 아니다. N/A를 PASS 수에 합산하지 않는다. 같은 source/범위 증거는 재사용; 원래 RF 범위 밖 전수 검증을 새 공통 게이트로 요구하지 않는다.
## 2.1 실물 단계 게이트

- 물리 단계: `01_PENDING → 02_DEVELOPING → 03_PEER_REVIEW → 04_LEAD_ACCEPTANCE → 05_DONE` (직접 계약 회귀는 근거 있는 `06_REWORK`). 01→02 owner CLAIM/중복 방지, 02→03 원래 C1~C3/C5 근거+SOURCE, 03→04 C1~C5 전체 충족+full independent peer, 04→05 C04 C6 필수 CI→C05 C6/C7+STATUS 처리. **C05만 단계 이동·원본 체크/DONE**, C04만 통합. 코드를 바꾼 A/B의 C5 문서는 지팀장이 해당 SHA에 맞춰 수정한 뒤 게이트 판정한다.

## 2.2 문서 전용 후속 커밋의 Hosted CI 재사용 예외 (홍사장 승인 2026-10-28)

- **기본 원칙은 정확 integration SHA normal/`python -O` hosted CI PASS**이다. 다만 통과한 통합 커밋 `CI_BASE_SHA` 이후 현재 `integration/p1.5` HEAD까지 **문서 전용 후속 커밋**뿐이고 아래 조건을 전부 검증한 경우에만, C04/C05가 같은 코드/테스트 상태에 대한 기존 hosted CI 증거를 **`CI_PASS_AT_BASE + DOC_ONLY_EQUIVALENT_AT_HEAD`**로 인수할 수 있다. **`CI_PASS_AT_HEAD`로 허위 표기 금지.**
- **검증 필수:** (1) CI 실행 URL/ID·`head_sha`·normal 및 `-O` 각각 SUCCESS를 원격 Actions에서 확인, (2) `CI_BASE_SHA...현재 HEAD` 전체 commit/diff 및 분기 선후관계를 확인해 변경 파일이 `docs/refactor/work_orders/C01_CODEX_CURRENT.md`~`C05_LEAD_CLOSEOUT_CURRENT.md`, `D00_ENGINEERING_DELIVERY_POLICY.md`, `docs/refactor/plan/STATUS.md`, `docs/refactor/plan/queue/**/RF-*.md`, `docs/refactor/plan/queue/04_LEAD_ACCEPTANCE/LEAD_CURRENT.md` 등 지팀장 소유 **순수 상태/지시 Markdown**에만 한정됨을 증명. (3) 모든 RF 원본 owner 코드 blob·실행/검증 코드·테스트/오라클·의존성·CI/workflow·환경/설정/매니페스트/보호 계약·실행시 읽는 문서나 데이터는 **변경 0**임을 확인. 문서도 런타임 또는 테스트 입력으로 쓰이면 이 예외에서 제외한다. (4) 새 코드·테스트·위험 권한 변경, 불명확한 diff/조상 관계, 실패·취소·미실행 CI, 스코프 미충족 시 **즉시 재사용 불가**: 해당 코드 상태의 새 CI가 필요하다.
- 해당 RF의 C1~C5·전체 반대 peer PASS·source KEEP blob 동일성·안전 HOLD는 **그대로 필수**다. C04는 `CI_BASE_SHA / RUN_ID / PASS(normal,-O) / HEAD_SHA / DOC_ONLY_DIFF_PATHS / CODE_TEST_WORKFLOW_DIFF=0 / SOURCE_BLOB_PARITY / EXCLUSIONS`를 한 번만 증거로 인계하고, C05는 그 뒤 생기는 지팀장 상태/체크/큐 정리 Markdown 커밋까지 동일 불변성을 재검증해 C6/C7 종결한다. **C04/C05가 기록용 Markdown을 푸시할 때마다 CI를 다시 돌리는 루프 금지.** CI를 새로 실행하지 않은 사실 자체는 반드시 구별해 기록한다.
- 이 예외는 RF 완료 증거의 재사용에만 적용하며 GitHub branch protection, CI workflow, frozen test, Broker/UEF/real 안전 게이트를 바꾸거나 우회하는 승인이 아니다.

## 3. 안전 경계·작업 격리
- 무승인 실계좌·실주문·브로커/운영 외부 쓰기, Broker/Supervisor/Executor/Step5C/UEF 안전 계약, frozen test/oracle/CI, 비밀정보, 운영 DB·State·데이터, 배포·예약 변경/실행 금지. 별도의 명시적 사용자 승인이 필요하다. mock/temp/fake 우선, 실런 RunLab와 개발 테스트를 구별한다.
- RF-069 UEF5 historical snapshot은 경로·SHA·use-scope 및 사용자/증거 소유자 승인 전 `NOT_RUN/SAFETY_BLOCKED`. RF-032/034 UEF·closeout 보호를 우회하지 않는다. RunLab #32의 `RUN_SOURCE_SHA=UNKNOWN`은 운영 버전 검증 차단이지 자동 코드 회귀 판정이 아니다.
- 새 브랜치·tag·PR·worktree, `main` 변경, force push, 이력 rewrite 금지. 허용된 브랜치 최신 HEAD/소유 파일 확인 후 작업, 경합 시 재조회. UI code와 patchnotes 등 문서 동반 변경이 필요하면 지팀장 작업을 별도로 요청한다.

## 4. 이슈 댓글·진척 기록
- A/B는 신규 성과·막힘 발생 시 **자기 Issue 댓글만**: `ORDER_STEP | SOURCE_SHA | CHANGED_CODE/TEST_PATHS | COMMAND + normal/-O result or NOT_RUN | PUSH_VERIFIED/FAILED | BLOCKER/NEXT` (RF/C1~C7 귀속 판정은 지팀장 담당). 실험은 실제 명령과 종료코드 구분. 댓글에 반복 증거 전체 복사 금지; 이미 공유한 댓글 링크로 재사용. 코드 변화 없는 문서/검증 기록용 커밋 금지.
- 지팀장은 #11·#12·#32의 **신규** 사실만 인수해 관련 RF 원본을 직접 확인한다. 실제 배정·상태 변경 시에만 C문서/RF/STATUS 등을 갱신. **새 판정만 #36 댓글**: `C03|C04|C05 | INPUT_COMMENT | RF | DECISION | SOURCE/PEER SHA | CI | UPDATED_PATHS | BLOCKER/NEXT`. 변경 없으면 쓰기/댓글 0.
- RF 원본 이동/체크 갱신 시 C05가 `python docs/refactor/tools/sync_rf_checklist_status.py --write` 및 `--check` 실행(실행 환경이 없으면 `NOT_RUN` 명시), 총 93 RF 유일성과 stage 수 검증. CI 완료 전 DONE 증가 금지.
- 장애와 제한은 구분: `NO_DELTA`(실제로 새 안전 작업도 없음), `BLOCKED`(권한/환경/정확 C 차단), `EXECUTION_LIMIT`(실제 도구 한도 신호 확인). 한도 때만 `LIMIT_TYPE | EVIDENCE | LAST_DONE | NOT_DONE | NEXT` 기록; 추정 수치·크레딧 원인 단정 금지.

## 5. RunLab 분리
- 정본 [R00](../../runtime/validation/R00_RUNTIME_VALIDATION_RULES.md)·[D04](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md)·[RunLab CURRENT](../../runtime/validation/CURRENT.md)·[Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32). RunLab은 관측·새 사실을 #32 댓글로만, 지팀장은 신규 건만 사건 대장에 접수/원 RF owner 판정. 개발 `DEV_RESOLVED` ≠ 런타임 `RUNTIME_VERIFIED`; 승인된 적용 이미지·실증 없이 사건 CLOSED 불가. 안전 HOLD는 영향 경계에만 적용한다.
