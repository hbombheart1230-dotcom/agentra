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
- **지팀장:** A/B 신규 증거와 런검증 결과 인수 → RF 직접 FIX/KEEP/PEER/INTEGRATE/BLOCKED 판정·큐 이동 → 승인 가능한 소유 코드 선별 통합·검증 인수 → 다음 작업 배정 → **마지막에 CURRENT/STATUS 갱신**.
- 실행 가능 작업이 남아 있으면 단일 PASS·ACK·HANDOFF로 종료하지 않는다. 막힌 작업은 원인·해제 조건을 남기고 다른 RF를 진행한다. 이미 결정할 수 있는 일을 개발자에게 반복 위임하지 않는다.

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

## 4. 트러블슈팅

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
