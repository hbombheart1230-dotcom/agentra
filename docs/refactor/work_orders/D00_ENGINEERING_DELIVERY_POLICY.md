# D00 — Agentra P1.5 공통 실행 계약 (간소화, 2026-10-27)

> 홍사장 지시로 중복 검증·반복 승인·매회 문서 동기화 의무를 축소한다. RF-001~093 종결 목표와 안전 보호 경계는 유지한다.

## 1. 역할과 작업 권한

| 담당 | 기존 브랜치 | 정본 진입점 | 책임 |
|---|---|---|---|
| 지팀장 | `integration/p1.5` | `CURRENT.md` (C00) | RF 원본 체크리스트·STATUS 정합성, 단계 게이트, peer 수용·안전 통합·DONE 판정 |
| Claude A | `work/p15-a-reporter-pure-20261021` | `C02_CLAUDE_CURRENT.md` | A 소유 구현, B 소유 독립 peer |
| Codex B | `work/p15-b-operator-structure-20261022` | `C01_CODEX_CURRENT.md` | B 소유 구현, A 소유 독립 peer |

- D00과 C00/C01/C02 정본은 `integration/p1.5:docs/refactor/work_orders/`이다. A/B 작업 브랜치에 남은 옛 지시는 무시한다.
- 일반 RF의 개발·테스트·수정·peer·커밋·푸시는 사전 일괄 승인됨. 개별 착수 승인, 지팀장 답변, HANDOFF 수락을 기다리지 않는다.
- 신규 브랜치·tag·PR·worktree 생성, `main` 변경 금지. A/B는 기존 브랜치만 사용한다.
- 미배정 일반 RF는 두 작업자의 최신 CLAIM만 확인해 중복 없이 자율 선택한다. 충돌한 RF만 뒤로 미루고 다른 RF를 진행한다.

## 2. 완료 기준 — 독립 검증 PASS 우선

1. **Owner:** 원래 RF의 명시된 수용 조건에 맞춰 구현·테스트하고 SOURCE SHA, 변경 범위, 실제 명령·결과(또는 정적 검증 근거), 미실행 경계를 HANDOFF에 기록한다.
2. **Peer:** 반대 개발자가 **해당 SOURCE SHA와 원래 RF 수용 범위**를 독립 검증한다. self-peer 금지. `PASS`·`FAIL`·`SCOPED_PASS`·`NOT_RUN` 중 정확히 판정하고 재현 근거를 남긴다.
3. **지팀장:** 유효한 전체 범위 peer PASS이면 **재테스트 없이 인수한다.** SOURCE SHA 대응, 통합 대상 diff/충돌·보호 경계, 필요한 integration CI 상태만 확인한다. peer의 PASS는 '독립 검증 PASS'로 표기하며 '지팀장 직접 실행 PASS'로 바꾸어 쓰지 않는다.
4. **종결:** 원래 RF 수용 조건 충족 + 유효 peer PASS + 안전한 통합(이미 동일 소스면 `KEEP_VERIFIED`) + **해당 통합 SHA에 요구되는 CI PASS**이면 그 회차에 `04_LEAD_ACCEPTANCE → 05_DONE`까지 이동한다. 별도 승인 회차나 임의의 추가 테스트는 요구하지 않는다. 실패한 기존 수용 조건은 `06_REWORK`로 보낸다.

- `01_PENDING → 02_DEVELOPING → 03_PEER_REVIEW → 04_LEAD_ACCEPTANCE → 05_DONE/06_REWORK`의 **실물 RF 경로는 유지**하되, LEAD는 검증팀 뒤에 또 한 번 테스트하는 단계가 아니다.
- **동일 SOURCE SHA·동일 수용 범위의 성공 증거는 재사용**한다. normal/`python -O`/CI를 지팀장이나 상대 개발자에게 중복 수행시키지 않는다. 반대로 증거 없는 검증을 PASS로 간주하지 않는다.
- 소비자/State/IO/예외·Windows·CLI 전체 전수검증을 **모든 RF의 공통 추가 게이트로 부과하지 않는다.** 원래 RF 수용 조건 또는 확인된 결함에 직접 필요한 부분만 검증한다. `SCOPED_PASS`가 원래 필수 범위를 미충족했다면 누락 조건 **하나와 담당자**를 특정한다.
- RF 범위 밖에서 새로 발견한 품질 개선·운영 검증은 별도 후속 RF/이슈로 분리한다. 이 때문에 이미 충족된 무관한 일반 RF를 HOLD하지 않는다. 단, 발견된 결함이 원래 RF 수용 조건 또는 아래 보호 경계를 실제로 침해한다면 DONE 처리하지 않는다.
- `KEEP_VERIFIED`는 실제 소스 변경이 없어도 동일 소스·peer·integration/CI 조건이 확인되면 DONE 가능. 문서만 갱신했다고 코드 실적을 만들지 않는다.

## 2.1 RF 원본 7개 체크리스트와 실물 단계 진입 게이트 (2026-10-27 확정)

**RF 문서의 원래 `## DONE 체크` 7항목은 완료 판정의 기준이며 지팀장 관리 대상이다.** 증거 없이 체크하지 않고, A/B Owner의 실행 보고를 독립 peer PASS 또는 지팀장 직접 PASS로 바꿔 쓰지 않는다.

| 원래 RF 조건 | 주된 수용 단계 | 필수 확인 |
|---|---|---|
| C1 파일별 MOVE/KEEP/WRAPPER/SAFETY_HOLD | DEV 제출 → PEER 검증 | 전 Owner 파일 ACTION 및 근거. KEEP도 증거 필수 |
| C2 책임·기존 계약 동등성 | DEV 제출 → PEER 검증 | 원래 범위의 import/caller/IO/State/예외·효과 중 실제 필수 계약 |
| C3 normal/-O 및 실패·경계 | DEV 제출 → PEER 검증 | 원래 명시된 필수 회귀; 기존 BASE 실패는 별도 식별 |
| C4 반대 개발자의 독립 peer | PEER | 정확 SOURCE SHA, 실제 실행/정적 증거 및 미실행 경계. `SCOPED_PASS`는 전체 PASS 아님 |
| C5 변경 시 patchnotes·소유권 정합성 | DEV/PEER | 실제 적용 조건이면 증거로 확인. 불필요하면 이유를 명시한 `N/A` |
| C6 통합/KEEP 및 필수 integration CI | LEAD | 실제 integration SOURCE/commit SHA, 필요한 CI 결과. 불필요한 CI는 원래 계약 근거로 NOT_REQUIRED |
| C7 실물 DONE·STATUS/CSV | LEAD | C6까지 충족한 동일 회차에 수행, 실제 물리 파일 및 집계 대조 |

- 상태 구분: `MET`=원래 조건 충족 근거와 범위 확인, `N/A`=사유가 적힌 조건부 비적용, `PARTIAL`=부분 증거만 확인, `PENDING`=미판정/미제출, `MISSING`=원래 필수 누락 확정, `SAFETY_BLOCKED`=보호 승인·환경 조건으로 미실행. **`[x]`는 MET 또는 사유 있는 N/A일 때만**. STATUS의 실제 검증 완료 수치에는 N/A를 섞지 않는다.
- `01_PENDING → 02_DEVELOPING`: Owner CLAIM·물리 독점 확인. `02_DEVELOPING → 03_PEER_REVIEW`: Owner가 C1~C3 및 적용되는 C5 **원래 범위에 대한 검증 가능한 완료 주장·SOURCE SHA·근거를 제출**한 경우만. 이 시점의 Owner 제출은 최종 MET가 아니므로 PEER 확인 전 체크박스는 비어 있을 수 있다. 제출이 부족하면 DEV 유지/반환하며 미충족 최초 조건을 명시.
- `03_PEER_REVIEW → 04_LEAD_ACCEPTANCE`: 반대 peer의 **원래 필수 전체 범위 PASS**를 확인해 **C1~C4 및 적용되는 C5가 모두 MET 또는 적법 N/A**로 기록된 때만. `SCOPED_PASS`가 남거나 미체크 C1~C5가 있으면 04에 올리지 않는다. PEER 중 Owner 증거의 실질 누락을 발견하면 Owner DEV로 반환하고, 직접적 신규 회귀·계약 위반만 REWORK 심사한다.
- `04_LEAD_ACCEPTANCE → 05_DONE`: 지팀장이 C6만 통합·필수 CI 인수하고 같은 회차에 C7 처리. C1~C5를 다시 테스트하지 않는다. C6 미충족이면 실제 조건과 담당을 기록하고 필요 단계로 반환. **완료에 가까워 보이거나 대기 기간이 길다는 이유로 04에 올리지 않는다.**
- 기존 기록이 `PEER`인데 C1~C3가 비어 있으면 **Owner 제출과 지팀장 수용 사이의 미확인 상태**다. 지팀장은 기존 HANDOFF/증거를 1회 매칭하고 필요한 조건만 OWNER에 반환한다. 비어 있는 체크를 자동 PASS로 처리하거나 무관한 전체 테스트를 추가하지 않는다.
- `SAFETY_BLOCKED`는 승인 또는 원래 범위에서의 적법한 분리 판정 전 메워지지 않는다. 문서/체크 정리는 사용자 보호 코드 실행·fixture 생성 승인이 아니다.
- **RF 파일의 원본 목표·범위·7개 체크를 먼저**, 변경/검증 기록은 뒤에 날짜순으로 보존한다. 과거 이력의 HOLD/LEAD 표기가 최신 물리 단계·판정을 덮어쓰지 않는다.

## 3. 안전 보호 경계 — 완화 금지

- `main`, 실거래·실주문, Broker/Supervisor/Executor/Step5C/UEF 안전 계약, frozen test/oracle/CI, 비밀정보, 운영 데이터, 배포·예약 설정의 **무승인 변경/실행 금지**. 보호 영역은 별도 명시적 사용자 승인 필요.
- 테스트는 temp 격리·mock/fake 우선, 실제 주문·외부 쓰기·네트워크 효과를 차단한다. 성공 임시 산출물 정리·실패 증거 제한 보존. 관련 UI 변경 시 patchnotes JSON/MD 갱신.
- RunLab [#32](https://github.com/hbombheart1230-dotcom/agentra/issues/32)는 읽기 전용으로 인수하며 운영 런/스케줄을 바꾸지 않는다. mock SELL 출처·체결, broker↔local/guard 불일치, `RUN_SOURCE_SHA=UNKNOWN`은 영향받는 **운영/안전 경계에서 SAFETY_HOLD**를 유지한다. 이것만으로 무관한 코드 RF의 독립 검증 PASS를 무효화하지 않는다.
- RF-069 UEF5 historical snapshot은 path/SHA/use-scope 및 사용자·증거 소유자 승인 전 실행 금지. RF-032/034의 보호 UEF/closeout 경계도 우회 금지.

## 4. 최소 운영·인계

- A/B는 HANDOFF_A/B에 RF, SOURCE SHA, peer 결과, 최초 결함/차단, 다음 RF만 **변경분으로** 기록한다. Issue [#11](https://github.com/hbombheart1230-dotcom/agentra/issues/11)/[#12](https://github.com/hbombheart1230-dotcom/agentra/issues/12)는 주요 체크포인트만 갱신하며 같은 내용을 매 회차 중복 게시하지 않는다.
- 지팀장은 해당 RF의 새 증거만 보고 판정·선별 통합·실물 큐 이동을 수행한다. 전체 93개 RF, 모든 HEAD/HANDOFF/Issue를 **매회 전수 재조회하지 않는다**. 충돌·중복·누락이 의심되거나 상태 변경 시 해당 부분만 확인한다.
- **STATUS.md와 RF 체크리스트의 정합성 유지·갱신 책임은 지팀장 단독**이다. RF 단계·체크·Owner/peer·HOLD·DONE이 변하면 같은 인수 작업에 RF 원본 체크/근거와 STATUS 링크·수치·NEXT를 함께 갱신한다. A/B는 RF 근거·HANDOFF만 제출한다. 93건 전수 조회는 불일치나 실제 전체 검증 필요 시에만 수행하며, 일상에는 바뀐 RF만 확인한다. 동기화 도구 `docs/refactor/tools/sync_rf_checklist_status.py`는 지팀장이 `--write` 후 `--check`로 확인하는 수단이지 자동 완료 승인/Owner 업무가 아니다. C00/C01/C02도 담당/우선순위·물리 큐가 바뀔 때만 정합성 갱신한다.
- 막힌 RF는 부족한 **원래 수용 조건 1개/안전 사유 1개와 해제 담당**만 기록하고 다른 RF로 이동한다. 신규 actionable 증거가 없거나 도구/실행 한도에 도달하면 진척을 꾸미지 않고 `NO_DELTA`/`BLOCKED`/`EXECUTION_LIMIT`로 정상 종료할 수 있다.
- 최종 보고는 **실제 코드·RF 변화, 검증 출처·SOURCE/통합 SHA, PASS/FAIL/NOT_RUN, 다음 RF**만 간결히 남긴다.

## 5. RunLab 공통 트러블슈팅 연동

- 런검증 실행은 [R00](../../runtime/validation/R00_RUNTIME_VALIDATION_RULES.md), 런검증→개발 인계는 [D04](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md), 접수 근거는 [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32)를 정본으로 사용한다.
- 지팀장은 새 관측이 생기면 기존 중복을 제외해 [OPEN 인수대장](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md)에 접수하고 **C00에 담당자·소유 RF 후보·다음 근거**를 배정한다. 실제 RF 소유를 확인하기 전에는 OWNER_MAPPING_PENDING으로 둔다.
- 개발 Codex B는 주문 출처·Guard·reconciliation을, Claude A는 Reporter·metrics 일관성을 **읽기 전용/격리 모의 자료로 조사**한다. RunLab은 이미지 출처·환경/예약·독립 운영 관측을 맡는다. 정식 수정은 확정된 원소유 RF 담당만 수행하며 보호 대상 수정은 별도 사용자 승인이 필요하다.
- 기존 RF 독립 peer PASS를 중복 검증하지 않는다. **RF의 DEV_RESOLVED와 RunLab 사건의 RUNTIME_VERIFIED는 별도**다. 실제 적용 버전에서 증상을 확인하기 전 사건은 OPEN/RUNTIME_PENDING으로 유지한다.
- 새 사실이 있을 때만 C00·STATUS 변경분을 동기화한다. 무관한 RF는 진행하며 승인 없는 주문·운영 변경·재배포·예약 변경을 하지 않는다.
