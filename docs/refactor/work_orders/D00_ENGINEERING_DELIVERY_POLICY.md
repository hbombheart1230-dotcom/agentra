# D00 — Agentra P1.5 공통 실행 계약

**명령: 읽고 끝내지 마라. RF를 구현·검증·종결하고, 즉시 다음 실행 가능한 RF로 진행하라.**
목표는 RF-001~093 전체 종결이다. 한 RF의 완료·차단·HANDOFF는 예약 실행의 종료 조건이 아니다.

## 1. 권한·진입점

| 실행자 | 기존 브랜치(유일) | 최초 진입 C | 책임 |
|---|---|---|---|
| GPT 지팀장 | `integration/p1.5` | `CURRENT.md` (C00) | 배정·독립 검증 인수·선별 통합·RF 최종 DONE |
| Codex B | `work/p15-b-operator-structure-20261022` | `C01_CODEX_CURRENT.md` | B 소유 RF 구현·A 소유 RF peer |
| Claude A | `work/p15-a-reporter-pure-20261021` | `C02_CLAUDE_CURRENT.md` | A 소유 RF 구현·B 소유 RF peer |

- C 정본은 모두 `integration/p1.5:docs/refactor/work_orders/`. 작업 브랜치의 오래된 CURRENT를 지시로 사용하지 않는다.
- **신규 브랜치·tag·PR·worktree 생성 절대 금지.** 충돌 시 기존 브랜치에서만 안전하게 재시도하고 불가하면 `GIT_BLOCKED`.
- A/B는 **배정된 일반 RF**를 자기 브랜치에서 구현·수정·테스트·커밋·푸시한다. 별도 건별 승인 대기가 아니다. 지팀장은 수용 범위만 integration으로 통합한다.
- 배정 밖 범위, `main`, 거래·보호 계층, 배포·예약·운영 데이터 변경은 **사용자 사전 승인**이 필요하다. D 계열 고정 계약도 승인 후 변경한다.

## 2. 계속 실행하는 RF 루프

| 순서 | 행동 | 완료 기준 |
|---|---|---|
| 1 | 역할 C·RF 실물 큐·자기 HANDOFF의 미처리 경계 확인 | 이미 한 검증 건너뛰기 |
| 2 | 실행 가능한 RF 하나 선택 | 원 Owner·peer 확인 |
| 3 | Owner 구현/테스트 또는 상대 Owner 독립 peer | 실제 소스/소비자/State·IO·예외 증거 |
| 4 | 자기 브랜치 커밋·푸시 및 간결한 HANDOFF | SOURCE SHA·명령·exit·새 결함/게이트 |
| 5 | **즉시 다음 RF 선택, 반복** | 실행 가능 작업 소진·실행 한도까지만 |

- 막힌 RF는 첫 차단 원인과 해제 책임만 기록하고 **다른 RF로 이동**한다. 새 증거가 없으면 개발 가능 큐로 넘어간다.
- A/B 작업 선택 순서: C의 신규 peer/owner 우선 작업 → 자기 `02_DEVELOPING` → `06_REWORK` → 담당 `03_PEER_REVIEW` → 자기 `01_PENDING`. 자기 큐가 비면 지팀장이 `UNASSIGNED`를 배정한다.
- 유효한 동일 SHA·동일 경계 normal/`python -O`/CI는 재사용. 의미 없는 synthetic 테스트·HANDOFF-only 커밋·회차별 문서 누적 금지.
- 작업이 실제로 모두 차단되면 `BLOCKED`/승인 필요 사유·다음 재개 위치를 기록한다. 실행 한도에 도달하면 `EXECUTION_LIMIT`과 다음 RF를 남긴다. **진척을 꾸며 내지 않는다.**

## 3. RF 최종 판정과 필수 경계

| 큐 | 담당·게이트 |
|---|---|
| `01_PENDING` → `02_DEVELOPING` | 원개발 Owner |
| `03_PEER_REVIEW` | 반대 개발자 독립 검증. self-peer 금지 |
| `04_LEAD_ACCEPTANCE` | 지팀장 직접 판정·안전한 선별 통합 |
| `05_DONE` / `06_REWORK` | 지팀장 원격 실물 이동/반려, 93개 유일 경로 확인 |

- Scoped PASS ≠ 전체 DONE. `KEEP_VERIFIED`는 원개발·독립 peer·통합 게이트 충족 시 코드 변경 없이 DONE 가능.
- 보호 구간: `main`, Broker/Supervisor/Executor/Step5C/UEF 계약, 실거래·실주문, frozen test/oracle·CI, 비밀정보·운영 데이터·예약·배포를 무승인 변경/실행하지 않는다.
- 실행 효과는 temp 격리·네트워크/주문 차단. 기존 유효 증거를 재사용하고 새 증거는 실제 SOURCE SHA, 재현 명령, exit, State/IO/예외, 외부 쓰기 여부를 남긴다. 미실행은 `NOT_RUN`.
- 정상 테스트 임시 산출물은 정리하고 실패 증거는 제한 보존. 관련 UI 소스 변경 시 연결된 patchnotes JSON/MD도 갱신한다.

## 4. RunLab #32 — 독립 런검증 경계

- [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32)는 **새 관측만 읽기 전용 인수**한다. 런검증 자체는 `docs/runtime/validation/CURRENT.md`와 `R00_RUNTIME_VALIDATION_RULES.md`를 따른다. 개발 A/B가 런검증 일정·운영 런을 바꾸지 않는다.
- mock SELL 체결/출처, broker↔local·guard·Reporter 일치, OCI `RUN_SOURCE_SHA`가 UNKNOWN이면 `SAFETY_HOLD`. RunLab 관측만으로 REWORK·DONE·재배포·주문을 승인하지 않는다.
- RF-069 historical UEF5 snapshot은 **path/SHA/use-scope와 사용자·증거 소유자 승인 전 실행 금지**. RF-032/034의 보호 UEF/closeout 경계도 승인 전 우회 금지.

## 5. 문서·보고

- D00/루트 `AGENTS.md`/`CLAUDE.md`는 고정 지시. C00/C01/C02는 **현재 우선 RF·다음 선택 위치만** 유지하며 지팀장이 integration에서 관리한다.
| 실행자 | 자기 브랜치 HANDOFF | 작업 체크포인트 |
|---|---|---|
| Claude A | `docs/refactor/work_orders/HANDOFF_A.md` | [Issue #11](https://github.com/hbombheart1230-dotcom/agentra/issues/11) |
| Codex B | `docs/refactor/work_orders/HANDOFF_B.md` | [Issue #12](https://github.com/hbombheart1230-dotcom/agentra/issues/12) |
| 지팀장 | C00·STATUS·RF 큐 | #11/#12 신규 결과 인수 |

- A/B는 자체 선택 RF의 **RF 번호·SOURCE SHA·실제 결과·다음 RF**를 HANDOFF에 남겨 자기 브랜치 커밋·푸시 후 담당 Issue에 신규 체크포인트를 제출한다. 지팀장은 매 회차 A/B 최신 HEAD·HANDOFF·#11/#12 신규 기록을 대조해 판정·통합·다음 배정에 반영한다. Issue의 과거 브랜치·업무 지시는 D/C 정본보다 우선하지 않는다.
### 지팀장 STATUS 관리 — 매 예약 필수

- **매회** 실물 RF 큐·Owner·개수, integration/A/B HEAD, HANDOFF_A/B와 Issue #11/#12의 신규 체크포인트, 승인·차단을 `docs/refactor/plan/STATUS.md`와 대조한다. 확인하지 못한 실물 검증은 `NOT_VERIFIED`로 구분한다.
- RF 상태·담당·검증·차단·SHA·작업 배정 등 **실제 현재 상태가 바뀌면 같은 회차에 STATUS 본문을 전체 교체하고 커밋·푸시한다.** 변화가 없으면 대조만 하고 문서 커밋을 만들지 않는다. 상세 증거는 RF/HANDOFF/Git에 둔다.
- **종료 순서:** RF 판정·가능한 통합/DONE → STATUS 동기화 → 필요한 C01/C02 갱신 → **C00 마지막 갱신**. 필요한 STATUS 갱신을 누락한 실행은 `EXECUTION_INCOMPLETE`로 보고한다. 문서 변경만으로 RF/운영 소스 진척을 주장하지 않는다.
- 보고는 `실제 RF 진척 | SOURCE/commit SHA | PASS/FAIL/BLOCKED/NOT_RUN | 다음 RF` 한 표로 끝낸다.
