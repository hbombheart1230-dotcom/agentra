# D00 — Agentra P1.5 개발팀 통합 운영 규칙

**정본:** `hbombheart1230-dotcom/agentra` / `integration/p1.5` / [CURRENT](CURRENT.md)

이 문서는 기존 D00·D01·D02·D03·D05·D06의 **실행 규칙**을 통합한다. **CURRENT는 배정**, **개별 RF는 소유 범위·인수조건**, **Git은 변경 이력**이다. 다른 운영 문서를 찾아다니거나 정책 수신 SHA·ACK 장부를 작성하지 않는다.

## 1. 담당·브랜치

| 담당 | 작업 브랜치 | 역할 |
|---|---|---|
| Claude A | `work/p15-a-reporter-pure-20261021` | Reporter 소유 개발, B 변경 독립 peer |
| Codex B | `work/p15-b-operator-structure-20261022` | Operator/Monitor 소유 개발, A 변경 독립 peer |
| 지팀장 | `integration/p1.5` | 작업 배정, RF 판정·이동, 선별 통합, 최종 DONE |

**모두 `integration/p1.5`의 CURRENT에서 시작한다.** A/B는 자기 코드 브랜치에서 소유 코드만 수정한다. 역할별 상세 소유 경로는 해당 RF를 따른다.

## 2. 실행 순서

- **A/B:** CURRENT의 자기 RF 실행 → 필요한 독립 peer → 다음 실행 가능한 RF 연속 진행 → 신규 코드 SHA·테스트 exit·차단·다음 행동만 HANDOFF 보고. 동일 SHA·동일 경계는 재검증하지 않는다.
- **지팀장:** A/B 신규 증거·런검증 인수 → **04_LEAD_ACCEPTANCE 전체를 본인 작업 큐로 직접 처리** → FIX/KEEP/PEER/INTEGRATE/BLOCKED/DONE 판정과 실제 검증·큐 이동·허용 소스 선별 통합 → 필수 정확 SHA 검증 → 미해결 troubleshooting 확인 → 다음 작업 배정 → **STATUS 갱신 → CURRENT 마지막 갱신**.
- **자동 수행 의무:** 사용자 별도 독촉 없이 매 지팀장 작업 회차마다 LEAD 실물 전건 확인·신규 근거 수용·가능한 직접 검증·최종 판정/종결·물리 큐 이동을 우선한다. A/B 배정·보고·문서 갱신만으로 LEAD 처리 의무를 대체할 수 없다. HOLD는 영구 주차가 아니며 각 건의 부족한 최초 경계를 지팀장이 직접 해소 가능한지 먼저 실행·판단하고, 독립 실행 환경이나 승인/증거가 꼭 필요한 부분만 정확히 지정한다. DONE 요건을 충족하면 같은 회차에 직접 DONE 이동한다. 미충족은 근거·해제 조건·책임·다음 최초 행동을 RF에 명시한다. 지팀장 최종 판단을 A/B에 재위임하지 않는다.
- **종료 차단:** LEAD 전건에 대해 이번 회차의 실물 상태와 신규 근거를 처리하지 않았거나, 수행 가능한 직접 조치를 남겨둔 경우 `EXECUTION_INCOMPLETE`로 보고하고 완료를 주장하지 않는다. 새 증거 없이 같은 HOLD 문구만 반복하지 않는다. 실행 가능 작업이 남아 있으면 단일 PASS·ACK·HANDOFF로 종료하지 않는다. 안전·환경·승인 차단은 우회하지 않고 다른 실행 가능 RF를 진행한다.

## 2A. 지팀장 LEAD 큐 자동 처리 의무 (상시 강제)

- **사용자 추가 지시 불필요:** 매 회차 A/B 신규 결과와 동시에 `04_LEAD_ACCEPTANCE` 전건을 지팀장이 직접 점검·판정한다. 새 RF가 LEAD에 도착하면 해당 회차에 즉시 인수한다. A/B 작업 배정·보고만 하고 LEAD를 방치하지 않는다.
- **책임 분리:** A/B는 신규 구현·최초 독립 peer 증거를 제출한다. **RF 최종 ACCEPT/KEEP/FIX/REWORK/BLOCKED, 추가 검증 필요성, 선별 통합, DONE/큐 이동은 지팀장이 직접 결정한다.** 지팀장 판단을 A/B에 되돌려 보내지 않는다.
- **검증 주도:** 기존 동일 SHA·경계의 유효 normal/`python -O`/peer는 재사용한다. 지팀장이 접근 가능한 안전한 신규 검증은 직접 실행하고, 환경상 불가능하면 `NOT_RUN`과 정확한 실행 환경·필요 증거를 명시해 A/B에게 **검증 수행만** 요청한다. 증거 없이 PASS/DONE 주장 금지.
- **종결 우선:** 각 LEAD RF는 이번 회차에 `DONE`(모든 게이트 충족), `REWORK`(재현된 원개발 결함), `BLOCKED/HOLD`(구체적 미충족 게이트·해제권자·다음 최초 경계) 중 하나로 직접 판정한다. HOLD는 영구 주차가 아니다. 해소 가능한 범위를 직접 처리하고, 나머지는 명확한 해제 조건을 둔다. 이미 증거가 충분한 RF를 문서·CI 핑계로 HOLD하지 않는다. 정확 SHA의 CI가 필수인지 여부는 RF·기존 D00 검증 계약에 근거해 판정하고, 불필요한 전수 재실행을 강제하지 않는다.
- **완료 순서:** A/B/RunLab 새 진척 인수 → **LEAD 전건 직접 처리 및 필요 시 실제 검증·선별 통합** → RF 물리 이동·troubleshooting 종결 → 다음 A/B 작업 배정 → STATUS 갱신 → **CURRENT 마지막 갱신**. LEAD를 건너뛰고 배정·문서만 갱신하는 회차는 `EXECUTION_INCOMPLETE`로 보고한다.
- **성과 판정:** 단순 검토·문서 갱신·ACK·HOLD 누적은 DONE이 아니다. 보고는 `LEAD 유입/처리/종결/잔여 및 차단 이유`, 실제 코드 통합, 검증 exit, 다음 행동을 구분한다. **시간·회차당 RF 개수 상한을 임의로 만들지 않는다.** 안전·승인 게이트는 그대로 지킨다.

## 3. RF 큐·검증·통합

**위치:** `docs/refactor/plan/queue/`

```text
01_PENDING/{CLAUDE_A,CODEX_B,UNASSIGNED}
02_DEVELOPING/{CLAUDE_A,CODEX_B}
03_PEER_REVIEW/{CLAUDE_A,CODEX_B}         # 폴더명 = 검증자
04_LEAD_ACCEPTANCE/{FROM_CLAUDE_A,FROM_CODEX_B}
05_DONE/{CLAUDE_A,CODEX_B}
06_REWORK/{CLAUDE_A,CODEX_B}
```

- RF-001~093은 **단 하나의 물리 위치**에 존재한다. PENDING/DEVELOPING/DONE/REWORK 폴더명은 원개발팀, LEAD_ACCEPTANCE의 FROM은 원개발팀 출처다.
- **지팀장만** RF 이동·최종 DONE을 결정한다. 이동할 때 원본 제거와 대상 생성, RF·STATUS·CURRENT 정합성을 한 번에 처리한다.
- 개발자 실제 source SHA·필요한 normal/-O 증거 → 상대 팀 신규 범위 read-only peer → 지팀장 인수·선별 통합 순서. 기존 유효 증거는 재사용한다.
- 재현된 **원개발 코드 결함만 REWORK**. 환경/BASE 기존 실패·안전 HOLD는 구분한다. 원인 FIX/KEEP 후 유효 peer로 해소되면 REWORK를 종결하고 남은 게이트를 분리한다.
- KEEP_NOOP는 코드 동일성과 독립 증거로 직접 종결 가능하다. **전체 RF 인수조건·독립 검증·통합된 정확한 SHA의 필수 normal/-O PASS 후에만 DONE**. 부분 PASS/NOT_RUN/BLOCKED는 DONE이 아니다. 기존 테스트·CI 오라클을 임의 변경하지 않는다.
- RF에는 새로운 근거·결정·다음 작업만 추가한다. 중복 감사·attempt 파일은 만들지 않는다.

## 3A. Legacy & Dead Code Retirement — 기존 RF 내 퇴역 게이트

**적용:** RF-001~093의 앞으로 수행하는 미검증 범위에만 적용한다. 기존 DONE·유효한 SHA/normal/-O/peer 증거를 소급 취소하거나 같은 경계를 재검증하지 않는다. 새 RF·독립 보고 장부를 만들지 않고, 각 RF에 신규 후보·실제 판정·증거만 기록한다.

1. **후보 발견:** 기존 Owner/consumer 분류를 재사용하여 미사용 함수·중복 구현·구형 wrapper/CLI·모델 프로파일·환경변수 별칭을 찾는다. 파일 전체 제거와 함수/설정 일부 제거를 구분한다. 정적 import 검색만으로 미사용 판정하지 않는다.
2. **다중 소비자 확인:** 직접 import/호출, `importlib`·`runpy`·문자열 기반 동적 로딩, `__main__`·BAT/PowerShell/CLI, Commander `applied_policy`·환경변수·fallback, Docker/CI/UI/스케줄러, 테스트/외부 공개 계약을 확인한다. 저장소 바깥 소비자와 Paper/런타임 이미지 출처가 확인되지 않으면 UNKNOWN/HOLD로 남긴다. 런타임 미호출 자체는 제거 증거가 아니다.
3. **분류:** `ACTIVE`(실사용), `FALLBACK`(장애 대응), `COMPAT`(호환 소비자), `DORMANT`(기능 비활성·재사용 가능), `REMOVE_CANDIDATE`(소비자·효과 검증 후 제거 검토), `SAFETY_HOLD`(권한·증거 부족). `KEEP_VERIFIED`와 이 사용 상태는 별개의 축이다. `REMOVE_CANDIDATE`는 삭제 승인·성공 증거가 아니다.
4. **작은 단위로 퇴역:** 제거 후보마다 정확한 `FILE::SYMBOL` 또는 설정 키, 조회한 소비자 경로와 부재 근거, 대체 경로, 외부 효과·입출력/State/예외 계약, 위험·되돌림 방법을 기존 RF에 한 줄 이상 기재한다. 안전성이 증명된 pure/internal 코드에 한해 최소 제거 diff를 제안한다. 미승인 상태에서는 실제 코드 삭제·운영 설정 변경을 수행하지 않는다.
5. **검증과 승인:** **사용자가 제거 범위를 사전 승인한 후** 해당 RF Owner가 격리 브랜치에서 최소 diff와 기존 계약의 normal/`python -O` 명령·실제 exit·source SHA, 필요한 patchnotes를 제출한다. 상대 팀은 기존 증거를 재실행하지 않고 **새 제거 경계**만 독립 read-only peer 검증한다. 지팀장이 OWNER/보호 경계·frozen oracle·정확한 통합 SHA/필수 CI를 판정하고 선별 통합한다.
6. **보호 대상:** Broker/Supervisor/Executor/Step5C/UEF·거래 안전, 운영 데이터·감사/연구 증거, 실제 거래·예약·동결 테스트/CI 및 공개 CLI는 제거 증명이 완결되지 않으면 `SAFETY_HOLD` 또는 `COMPAT`. 기록이 역사적이라는 이유만으로 지우지 않는다. 외부 효과를 확인하려고 라이브 명령을 실행하지 않는다.
7. **한 RF의 결과:** `RETIREMENT: 대상 | 분류 | 소비자·동적·운영 근거 | 제안 KEEP/DEPRECATE/REMOVE/HOLD | SOURCE_SHA | normal/-O·peer | 승인/차단 | 다음 경계`를 기존 RF에 간결히 남긴다. 후보가 없으면 `CANDIDATE_NONE` + 근거를 한 번만 기록한다. 실물 코드/파일 삭제가 없으면 DELETE 성과를 주장하지 않는다.

**우선 시범:** RF-050(LLM 8경로), RF-031(Reporter AI), RF-070(공개 launcher), RF-090(config)의 각기 다른 Owner와 기존 RF 상태를 유지한다. RF-050은 현재 DEVELOPING/CLAUDE_A로 배정되었으며, RF-031은 기존 peer 증거를 재사용하고 신규 경계만 확인한다. RF 번호·큐 총합·CSV 소유권은 이 정책만으로 바뀌지 않는다.

## 4. 트러블슈팅

**장애·STATUS:** 미해결은 [troubleshooting/open](../plan/troubleshooting/open/), 해결 건은 [troubleshooting/closed](../plan/troubleshooting/closed/)에 정리한다. 지팀장은 예약 회차마다 A/B·[런검증 Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32) 신규 결과와 RF를 인수하고, 실제 변경만 [STATUS](../plan/STATUS.md)에 갱신한다.

**실패 직후 바로 BLOCKED로 끝내지 않는다.**

1. 실제 오류·명령·대상 SHA 확인 → CODE / 기존 BASELINE / ENV / GIT·TOOL / SAFETY·OWNER 구분.
2. 허용 범위에서 즉시 복구: SHA 충돌이면 최신 HEAD·차분, 경로 오류면 실제 원격 경로, API 오류면 지원 형식, 요청 크기 오류면 작은 단위로 변경. 테스트 실패는 BASE와 비교한다.
3. 성공 시 실제 원격 커밋·수정 파일·테스트 exit를 확인한다.
4. 해결 불가 시 원인·담당자·해제 조건만 남기고 다음 실행 가능한 RF로 간다.

같은 실패 명령 무한 반복·안전 우회·무승인 강제 push 금지. 환경 테스트는 실행 가능한 A/B 작업장에서 수행하고, 지팀장은 결과 인수·판정 책임을 진다.

## 5. 런검증팀 인계

**원본 증거:** [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32). 런검증팀은 별도 [런검증 CURRENT](../../runtime/validation/CURRENT.md) → R00에 따라 관측한다.

- **거래 안전·중대 장애:** 즉시 인수·판정. **일반 사항:** 평일 19시 최종 독립 결과를 기본으로 인수한다.
- 지팀장은 신규 결과를 **코드 결함 / 환경·예약 / 미확정 관측 / 개선 제안**으로 나눈다. 재현된 코드 결함만 기존 RF에 연결한다. 신규 범위의 결함은 소유 RF 편입 여부를 결정한 후 배정한다.
- 기존 RF에는 `RUNTIME: Issue #32 증거 링크 | 증상 | 지팀장 판정 | 담당·다음 행동`만 추가한다. 원문 복사·중복 RF 생성 금지.
- RUNLAB 환경·예약 문제는 원칙적으로 런검증팀 복구. UNKNOWN은 재현 증거를 특정해 요청하고 코드 결함으로 단정하지 않는다. 런검증팀은 RF·개발 코드·통합 브랜치를 수정하지 않는다.

## 6. 안전·종료

`main`·실거래·거래 안전 계약(Broker/Supervisor/Executor/Step5C/UEF 포함)·동결 테스트/CI·예약 변경은 사용자 승인 없이 금지. RF-021 안전 HOLD와 동결 P1.5 기준을 유지한다. 운영 데이터·비밀정보를 보존하고 안전 가드를 우회하지 않는다.

**보고:** A/B 신규 진척 → 지팀장 실제 판정·통합 → RF·통합 검증 → 다음 행동. 문서·ACK만으로 성과를 주장하지 않는다.
