# D00 — Agentra P1.5 공통 실행 계약
> 2026-10-27 · 다섯 예약(A/B/C03/C04/C05)에 동일하게 적용하는 **공통 규칙만** 수록. 담당별 현재 작업은 각 C문서에 둔다.

## 1. 정본·역할·쓰기 권한 (공통)
- 정본 브랜치: `integration/p1.5`; A 개발 브랜치 `work/p15-a-reporter-pure-20261021`, B 개발 브랜치 `work/p15-b-operator-structure-20261022`.
- **각 예약 프롬프트가 자기 C파일을 직접 진입점으로 지정한다.** 구 `CURRENT.md`(C00)는 진입점이 아니며 자동 동기화 대상도 아니다. 각 담당은 **자기 C문서 + 이 D00**을 우선 읽고, 작업에 필요한 RF·HANDOFF·diff·CI만 선택적으로 확인한다.
- C01 = **Codex B**(B Owner 구현, A Owner의 반대 peer), C02 = **Claude A**(A Owner 구현, B Owner의 반대 peer), C03 = **지팀장①**(C1~C5 증거 판정·A/B 배정), C04 = **지팀장②**(승인된 LEAD 소스 통합·C6 CI 확보), C05 = **지팀장③**(유일한 RF 원본 체크·물리 큐·STATUS·C7 DONE 최종 판정).
- **단일 작성자:** A/B는 각각 기존 개발 브랜치와 자기 HANDOFF·자기 작업 노트의 개발 기록만 수정한다. C03은 C03 및 C01/C02의 **배정 델타 부분**만 수정한다(개발 증거 수정 금지). C04는 C04 및 승인된 `integration/p1.5` 일반 소스만 수정한다. C05는 C05, 원본 RF 체크·물리 단계, `STATUS.md`, `LEAD_CURRENT.md`, 관련 정합성 자료만 수정한다. RunLab OPEN 접수·배정 델타는 C03이 관리하며 C05는 연관 RF 단계·STATUS만 관리한다.
- C03의 권고는 물리 이동 승인이 아니고, C04의 통합은 DONE 승인이 아니다. A/B의 Owner 검증은 독립 peer PASS가 아니다. 지팀장 전체의 최종 단일 수용 책임은 C05에 둔다.
- 일반 RF 개발/테스트/peer/커밋/푸시는 일괄 승인되어 있다. 별도 지팀장 응답을 기다리지 않는다. A/B는 기존 CLAIM과 원래 Owner를 존중하고 중복 소유를 피하며, 미배정 일반 RF는 충돌하지 않게 자율 선택할 수 있다.
- **금지:** 새 브랜치·tag·PR·worktree 생성, `main` 변경, 강제 push/lease 없는 덮어쓰기. 모든 쓰기 전에 대상 최신 HEAD·자기 소유 영역을 확인한다. 경합 시 최신 상태를 재확인하고 자기 변경만 적용한다.

## 2. RF 원본 수용 계약 (공통)
- RF 문서의 **원래 목표·범위와 `## DONE 체크` C1~C7**이 판정 정본이다. 검증 기록은 그 뒤에 보존하며 이전 HOLD/LEAD 서술은 최신 물리 단계나 판정을 뒤집지 않는다.
- `C1`: 전체 원 Owner 파일의 MOVE/KEEP/WRAPPER/SAFETY_HOLD ACTION·근거(KEEP 포함).
- `C2`: 원래 필수 책임·import/caller/IO/State/예외/효과 등 계약 동등성.
- `C3`: 원래 명시된 normal/`python -O` 및 실패·경계 검증. 기존 BASE 실패와 신규 회귀 구분.
- `C4`: **반대 작업자**가 **정확 SOURCE SHA + 원래 필수 전체 수용 범위**에 대해 독립 검증·근거·미실행 경계를 갖춘 `PASS`. self-peer 금지.
- `C5`: 실제 코드/UI 변경 시 patchnotes·소유권 정합성. 비적용이면 사유 있는 N/A.
- `C6`: 정확 integration 소스/commit SHA의 안전한 통합 또는 `KEEP_VERIFIED` + **해당 SHA에 원래 요구된 CI PASS**. 불필요한 CI는 근거가 있을 때만 `NOT_REQUIRED`.
- `C7`: 원본 RF 물리 DONE 이동·RF 체크·STATUS/CSV·큐 수치의 동시 정합성 처리.
- 상태: `MET`(증거 충족), `N/A`(사유 있는 비적용), `PARTIAL`, `PENDING`, `MISSING`, `SAFETY_BLOCKED`. 원본 `[x]`는 MET 또는 사유 있는 N/A에만 허용한다. **실제 검증 PASS/MET 수에 N/A를 합산하지 않는다.** `SCOPED_PASS`는 전체 PASS가 아니다.

## 2.1 실물 단계 게이트 (공통)
- 순서: `01_PENDING → 02_DEVELOPING → 03_PEER_REVIEW → 04_LEAD_ACCEPTANCE → 05_DONE`(직접적 원래 계약 회귀는 근거에 따라 `06_REWORK`).
- **01→02:** Owner CLAIM 및 소유 중복 방지 확인.
- **02→03:** Owner가 C1~C3·해당 C5에 대한 검증 가능한 **원래 범위 완료 주장·SOURCE SHA·근거**를 제출. Owner 주장만으로 최종 체크 MET가 되지는 않는다. 누락은 DEV에 남겨 최초 원래 C항목을 돌려준다.
- **03→04:** 원래 C1~C5 전부 MET/적법 N/A이고 반대 peer가 **전체 수용 범위를 PASS**한 경우에만 C05가 체크·물리 이동을 수행한다. 미체크·SCOPED_PASS·SAFETY_BLOCKED가 있으면 LEAD 진입 금지. 실제 Owner 증거 누락은 DEV 반환, 확인된 직접 회귀·계약 위반만 REWORK 심사.
- **04→05:** C04가 C6의 안전한 통합/KEEP·요구 CI 증거를 만들고 C05가 확인하면, **동일 C05 인수 실행 안에서 C6 체크 + C7 물리 DONE/STATUS 처리**한다. 후속 승인 회차나 C1~C5 재테스트를 추가하지 않는다. C6가 없다면 LEAD 대기·필요 단계 반환과 첫 차단 원인을 기록한다.
- 같은 SOURCE SHA·같은 원래 범위의 성공 증거는 재사용한다. 원래 수용 조건 외의 Windows/CLI/State/예외/소비자 전수검증을 일반 공통 게이트로 추가하지 않는다. **전체 peer PASS를 지팀장 직접 실행 PASS라고 표기하지 않는다.** 증거 없는 PASS를 생성하지 않는다.
- 범위 밖 품질 개선은 별도 후속 RF/이슈로 구분해 무관한 RF를 HOLD하지 않는다. 다만 원래 수용 조건 또는 보호 경계 실제 침해는 해당 RF의 DONE을 막는다. `KEEP_VERIFIED`는 소스 일치·전체 peer·필요한 integration CI를 증명하면 코드 변경 없이 종결할 수 있다.

## 3. 안전 경계 (공통·완화 불가)
- 실거래/실주문·외부 쓰기, Broker/Supervisor/Executor/Step5C/UEF 안전 계약, frozen test/oracle/CI, 비밀정보, 운영 DB/State·데이터, 배포·예약/운영 설정의 **무승인 변경·실행 금지**. 보호 변경/실행은 사용자 별도 명시 승인 필요. 문서 정리나 peer PASS는 승인이 아니다.
- 검증은 temp 격리·mock/fake 우선으로 외부 부작용 차단. 성공 임시 산출물 정리, 실패 증거 제한 보존. 관련 UI 변경 시 patchnotes JSON/MD 갱신.
- RF-069 historical UEF5 snapshot은 **경로/SHA/use-scope + 사용자·증거 소유자 승인 전 NOT_RUN/SAFETY_BLOCKED**. RF-032/034의 UEF/closeout 보호도 우회 금지.
- RunLab #32의 mock SELL 출처·체결 불일치, broker↔local/guard, `RUN_SOURCE_SHA=UNKNOWN`은 **영향받는 운영/안전 경계에서만** SAFETY_HOLD. 무관한 코드 RF의 정상 독립 peer 결과를 무효화하지 않는다.

## 4. 증거·상태 동기화 (공통)
- A/B HANDOFF 신규 델타 형식: `RF | SOURCE SHA | Owner/Peer 역할 | 원래 수용 범위 | 실행 명령·결과/정적 근거 | PASS/FAIL/SCOPED_PASS/NOT_RUN | 첫 부족 조건·담당 | NEXT`. Issue #11/#12는 주요 변화만 보고, 매회 복사·중복 댓글 금지.
- **C05만** RF 원본 체크·C1~C7 판정·Owner/peer·실물 이동·STATUS 집계/링크를 수정한다. 상태 변경 시 `python docs/refactor/tools/sync_rf_checklist_status.py --write` 후 `--check`로 변경분과 전체 유일성/단계 수 정합성을 검증한다. 이 도구는 승인·실행·PASS를 생성하지 않는다.
- 93개 RF/모든 HEAD·HANDOFF·Issue 전수 점검은 매 예약에 의무가 아니다. 신규 delta·변경된 RF만 우선 보고, 실제 불일치/충돌/누락이 의심될 때 범위를 넓힌다.
- 막히면 `첫 원래 C조건 하나/보호 사유 하나 + 해제 담당`을 명시하고 다음 RF로 이동. 새 사실이 없으면 `NO_DELTA`, 막힘은 `BLOCKED`, 확인된 실행 한도는 `EXECUTION_LIMIT`로 정직하게 종료. 성과는 **RF 실제 DONE·미충족 C 감소·안전한 코드 통합**, 예약 실행·문서 커밋 수가 아니다.
- **한도 보고 필수:** `EXECUTION_LIMIT`는 **실제 플랫폼·도구의 한도 신호가 확인된 경우에만** 사용한다. 보고에 `LIMIT_TYPE`(TIMEOUT/TOOL_CALLS/TOKENS_CONTEXT/RATE_LIMIT/QUOTA/ENV_RESOURCE/OTHER/UNKNOWN), `EVIDENCE`(도구명·오류/종료 표시·시각·제한 수치 **확인된 것만**), `LAST_DONE`(마지막 실제 RF·SHA·성공 작업), `NOT_DONE`(중단된 단계), `NEXT`(재개 위치·담당)를 적는다. **원인을 추측하거나 크레딧 소진으로 단정하지 않는다.** 원인·수치를 확인 못 하면 `UNKNOWN/NOT_VERIFIED`로 적고, 한도 신호 자체가 없으면 `EXECUTION_LIMIT`라고 주장하지 않는다. `NO_DELTA`·`BLOCKED`와 혼용 금지.

## 5. RunLab #32 공통 연동 계약
- RunLab 정본은 [R00](../../runtime/validation/R00_RUNTIME_VALIDATION_RULES.md)·[D04](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md)·[Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32)·[OPEN 접수대장](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md).
- RunLab 운영은 별도이며 기존 예약·모의 브로커·배포 설정을 무승인 변경/대행 실행하지 않는다. 읽기 전용 증거와 격리 fake만 허용하며 **FILE_OWNER 매핑 ≠ 결함 원인 RF 확정**이다. `RUN_SOURCE_SHA=UNKNOWN`이면 적용 이미지와 현재 개발 소스 동일성을 단정 금지.
- RF의 `DEV_RESOLVED`와 런 사건의 `RUNTIME_VERIFIED`는 별도 판정. 승인된 런 적용 버전에서 증상이 재확인되기 전은 `OPEN/RUNTIME_PENDING`이다. 사건 신규 정보와 RF 원래 체크는 서로 대신하지 않는다.
