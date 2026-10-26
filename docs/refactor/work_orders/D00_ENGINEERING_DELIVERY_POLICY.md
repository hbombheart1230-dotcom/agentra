# D00 — Agentra P1.5 개발·검증·통합 운영 규칙

**정본:** `integration/p1.5`의 [CURRENT](CURRENT.md). D00은 **상시 규칙**, CURRENT는 **현재 배정·큐·차단**, 개별 RF는 **소유권·증거·최종 판정**, Git 커밋은 **지난 회차 이력**이다. 작업 브랜치 CURRENT와 이전 회차 STATUS를 실행 정본으로 사용하지 않는다.

## 1. 단일 작업장·권한

| 역할 | 유일한 작업 브랜치 | 책임 |
| --- | --- | --- |
| Claude A | `work/p15-a-reporter-pure-20261021` | 자기 RF 구현·테스트, B 변경 독립 peer |
| Codex B | `work/p15-b-operator-structure-20261022` | 자기 RF 구현·테스트, A 변경 독립 peer |
| 지팀장 | `integration/p1.5` | 소유권 조정·RF 최종 판정·큐 이동·선별 통합·DONE |

- **추가 `lead/*`, 임시 작업/백업 브랜치·worktree, PR은 사용자 승인 없이 만들지 않는다.** GitHub 쓰기 충돌이 발생해도 새 브랜치로 우회하지 않는다. 최신 integration HEAD 재조회 → 충돌 해결 가능 범위 내 비강제 재시도; 불가능하면 `GIT_BLOCKED`로 기록하고 중단한다.
- `main`, 실거래·주문, Broker/Supervisor/Executor/Step5C/UEF 안전 계약, 동결 테스트·CI, 예약·배포·운영 데이터·비밀정보는 **명시적 사용자 승인 없이 변경 금지**. 기존 승인 범위를 넘는 소스 변경도 사전 논의·승인한다.

## 2. 매회 실행 — 변경분만, 코드·RF 종결 우선

1. **CURRENT 하나로 시작.** 필요할 때만 D00·배정 RF·실제 source·테스트·증거를 읽는다. A/B 두 작업 브랜치 HEAD, integration HEAD, RF 실물 큐, 최신 RunLab Issue #32의 **지난 처리 이후 신규 변화**를 조회한다.
2. **새 증거가 없으면 `NO_DELTA`:** LEAD 14건 같은 목록 재판정, 같은 SHA·경계 재실행, 새로운 테스트 하네스 제작, STATUS/CURRENT/RF/HANDOFF 커밋, 신규 브랜치 생성 모두 금지. 짧게 `NO_DELTA / 코드0 / DONE0 / 다음 해제 조건`만 보고하고 종료한다. 이미 A/B에 배정된 최초 검증을 지팀장이 매회 또 수행해 예약을 채우지 않는다.
3. **변경이 있으면 영향받은 RF만 재판정.** 먼저 새 A/B source·peer·RunLab 결과를 확인하고 필요 시 최초 안전 검증을 한 뒤, 영향을 받은 LEAD·신규 도착 건을 지팀장 본인이 최종 `ACCEPT/DONE`, `REWORK`(재현된 원개발 결함), `HOLD/BLOCKED`(정확한 최초 미검증 게이트·해제 책임)으로 판정한다. 전체 LEAD 큐의 위치·중복 여부는 간단히 집계하되 **전건 RF 본문을 반복 재작성하지 않는다.** 기존 근거만으로 이미 완료조건이 충족된 미처리 RF가 발견되면 즉시 종결한다.
4. **실제 조치부터.** 수용 가능한 소스 변경은 파일 단위로 안전하게 선별 통합하고 필요 테스트·독립 peer·통합 **코드/테스트/workflow SHA**를 검증한다. 완료조건 충족 RF는 같은 회차에 `04_LEAD_ACCEPTANCE → 05_DONE` **원자적 이동**하고 구 경로 삭제·원격 단일 경로·commit SHA를 확인한다. 안전 차단은 우회하지 않는다.
5. 해결된 troubleshooting만 `open → closed` 이동 → 다음 A/B 작업 배정 → STATUS **교체 갱신** → **CURRENT 마지막 교체 갱신**. 변경할 내용이 없으면 어느 문서도 commit하지 않는다. 단순 `HOLD`, ACK, 보고서, fake PASS는 코드 진척 또는 DONE이 아니다.

**종료 규칙:** 실질적인 새 증거가 있는데 지팀장 직접 판정·가능한 RF 이동을 건너뛰면 `EXECUTION_INCOMPLETE`. **새 증거가 없고 기다리는 외부/peer/승인 게이트가 정확히 지정되어 있으면 `NO_DELTA`는 정상 종료**이며 의무적으로 신규 검증을 발명하지 않는다. 실제 코드 변경과 RF DONE이 필요한 상황에서 문서만 계속 생산하지 않는다.

## 3. RF·검증·효과 계약

- RF-001~093은 항상 하나의 물리 위치: `01_PENDING/{CLAUDE_A,CODEX_B,UNASSIGNED}` → `02_DEVELOPING/{CLAUDE_A,CODEX_B}` → `03_PEER_REVIEW/{CLAUDE_A,CODEX_B}`(peer팀) → `04_LEAD_ACCEPTANCE/{FROM_CLAUDE_A,FROM_CODEX_B}` → `05_DONE/{CLAUDE_A,CODEX_B}`; `06_REWORK/{CLAUDE_A,CODEX_B}`. 원개발/독립 peer/최종 지팀장 소유 구분을 지킨다.
- 실물 Owner·direct/dynamic import, CLI·웹·Docker·Windows·스케줄러·외부 소비자, State·파일 읽기/쓰기·LLM/네트워크/주문 효과, 예외·fallback, BASE 대비 차이를 증거로 검증. `KEEP_VERIFIED`는 독립 peer와 수용 게이트를 충족하면 코드 변경 없이도 DONE 가능. **scoped PASS만으로 전체 RF DONE은 금지**.
- 기존 normal/`python -O`/peer/CI 증거는 **같은 소스·테스트·workflow Git tree**와 동등성이 증명되면 재사용한다. 문서-only 새 HEAD마다 hosted CI를 재요구하지 않되 source 변경이 있으면 해당 통합 SHA에 필요한 새 검증을 수행한다. 하지 않은 실행은 `NOT_RUN`, 실제 exit 없는 테스트를 PASS로 표기 금지.
- 테스트는 격리된 temp root 및 효과 차단. 성공 임시 산출물은 정리하고 실패 증거는 보존량 제한. 운영 파일·실제 계좌·실거래 브로커·보호 UEF/frozen oracle 직접 실행/수정 금지. 소스/UI가 변경되면 연결된 UI patchnotes JSON/MD도 정합하게 업데이트한다.
- 미사용·legacy·중복 후보는 `ACTIVE/FALLBACK/COMPAT/DORMANT/REMOVE_CANDIDATE/SAFETY_HOLD`로 실제 소비자·외부 계약까지 분류. 정적 검색 0건은 삭제 허가가 아니다. `REMOVE_CANDIDATE`도 삭제 승인이 아니며 user 승인·Owner 최소 diff·독립 peer·통합 검증 전 제거하지 않는다.

## 4. CURRENT·STATUS 길이·이력 관리

- **CURRENT는 현재 상태와 다음 최초 실행만**, 권장 **5KB 이하**. **STATUS는 현재 큐·변경 성과·미해결 차단만**, 권장 **8KB 이하**. 한 파일당 **최상위 제목 1개**, 회차별 새 절·구분선·`이 절이 과거보다 우선` 누적 금지. 반드시 **본문을 통째로 교체**하고 오래된 회차를 제외한다.
- 자세한 실패·명령·SHA·peer 근거는 **해당 RF 또는 기존 HANDOFF/Issue**에만 기록한다. Git 기록 자체가 변경 이력이고, CURRENT/STATUS에 과거 전문을 반복하지 않는다. 검증 하네스는 재사용 가능한 최초 경계일 때만 만들며 증거를 위한 증거 생성 금지.
- 우선순위는 **실제 코드 진척·RF 종결·기술 차단 해제 > 문서·증거 커밋 수**. 같은 HOLD와 담당자 지시를 단순 재서술하지 않는다.

## 5. 사고·런검증·보고

- 새 실패는 정확 SHA·명령·exit로 `CODE / BASELINE / ENV / GIT_TOOL / SAFETY_OWNER` 구분. 정당한 재시도 후 해결되지 않으면 최초 해제 조건만 해당 RF·troubleshooting에 기록. 동일 실패 무한 반복·가드 우회 금지.
- 런검증 [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32)는 신규 실증에 한해 읽기 전용 인수; 매일 일반 최종 보고는 필요 시 인수한다. SELL provenance·OCI SHA 등이 UNKNOWN이면 코드 REWORK로 단정하지 않고 운영 변경·재배포를 멈춘다.
- 보고는 **신규 진척 → 실제 코드/RF 조치 → 검증 PASS/FAIL/NOT_RUN·SHA → 다음 최초 행동**. LEAD 신규 유입·DONE·REWORK·잔여와 실제 통합 커밋을 짧게 표시하며, 변화가 없으면 `NO_DELTA`만 보고한다.
