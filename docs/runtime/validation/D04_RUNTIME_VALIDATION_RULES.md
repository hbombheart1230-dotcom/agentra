# D04 — RunLab ↔ P1.5 개발팀 공통 트러블슈팅 계약 (2026-10-27)

**정본:** `integration/p1.5`. 이 파일은 이전에 로컬 작업 지시에서 언급됐으나 GitHub에 없었던 `D04_RUNTIME_VALIDATION_RULES.md`를 정식화한 **공통 인계/종결 계약**이다.
- **런검증 수행·예약·실행 권한의 정본:** [R00](R00_RUNTIME_VALIDATION_RULES.md) · [RunLab CURRENT](CURRENT.md).
- **개발 배정·독립 peer·통합·RF DONE 정본:** [D00](../../refactor/work_orders/D00_ENGINEERING_DELIVERY_POLICY.md) · [C00](../../refactor/work_orders/CURRENT.md).
- **원본 관측:** [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32). **현재 사건별 OPEN:** [RunLab #32 인수대장](../../refactor/plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md).
- R00과 D00에 없는 새로운 주문/운영 실행 권한을 D04로 만들어내지 않는다.

## 1. Issue #32 → 지팀장 실제 배정

1. 런검증 Codex(07:00/17:00), Claude(09:30/19:00)는 **실제로 관측한 새 사실만** Issue #32에 제출한다. 안전·중대 이상은 19시를 기다리지 않고 즉시 제출. `RUN_ID / IMAGE_DIGEST / RUN_SOURCE_SHA(or UNKNOWN) / 모의 주문-체결·State 대조 / 증거 위치 / 새 증상 / 환경·코드·안전·원인 미상 후보`를 구분한다. 관측하지 않은 사실을 재현 PASS로 표시하지 않는다.
2. 지팀장은 **#32의 새 증거를 접수한 그 회차에** `docs/refactor/plan/troubleshooting/open/`에서 기존 사건과 동일성/중복을 확인하고, **기존 OPEN에 새 delta를 추가**하거나 새 사건을 OPEN 등록한다. 단순 반복·과거 댓글은 새 건을 만들지 않는다.
3. **같은 회차에 작업 주체를 지정:** `(a) RunLab 환경/운영 읽기 전용 확인`, `(b) A/B의 원인 재현 및 소스 검토`, `(c) 사용자 승인 필요한 보호 안전 수정` 중 하나 이상으로 분류하고 **현재 C00에 1줄 우선 작업·담당·다음 증거**를 넣는다. 원래 소유 RF가 확정됐을 때만 해당 기존 RF/Owner에 배정하고, 불명확하면 지팀장 분류 책임 `OWNER_MAPPING_PENDING`을 유지한다. A/B는 C01/C02의 이 사건 배정을 확인한다.
4. 코드 결함으로 재현된 경우: **원래 Owner가 최소 수정** → 반대 개발자 독립 peer(정확 SHA·원래 수용/수정 범위) → 지팀장 통합 diff/필수 CI만 확인. D00의 **재검증 금지·같은 회차 DONE 원칙**을 따른다. 문제와 무관한 RF를 REWORK/HOLD하지 않는다.
5. 환경 문제면 RunLab 운영 담당자가 **권한 범위의 읽기 전용 진단/복구 계획**을 제시한다. 일정·이미지·컨테이너/설정·운영 상태 변경이나 주문이 필요한 복구는 **사용자의 별도 명시 승인 전 BLOCKED**, 개발팀이 승인 대신 변경하지 않는다. 원인 미상은 `UNKNOWN`으로 남기고 특정한 다음 조사만 수행한다.

## 2. 별도 종료 게이트 — RF DONE ≠ RunLab 트러블슈팅 CLOSED

- **DEV_RESOLVED:** 소스 수정/KEEP의 실제 SOURCE SHA, Owner·독립 peer 범위, integration SHA와 **요구 CI PASS**가 확보된 시점. 원인 분류만/하네스 PASS만으로 실제 RunLab 해소를 주장하지 않는다.
- **RUNTIME_VERIFIED:** *사용자 승인된 환경에서* 고정 `RUN_IMAGE_DIGEST ↔ RUN_SOURCE_SHA` 출처가 입증된 이미지/런을 근거로, 런검증팀이 원 증상과 재발 여부를 독립 확인. 브로커/로컬 대조는 실제 보존 증거로 판단하고, 주문 수락과 체결은 구분한다.
- **CLOSED:** 환경형 사건은 권한 내 복구/확인, 코드형 사건은 DEV_RESOLVED + 적용 버전의 RUNTIME_VERIFIED를 기본 조건으로 한다. **재배포 승인이 없어 런타임 검증이 불가능하면 `DEV_RESOLVED / RUNTIME_PENDING / OPEN` 유지**; 실행하지 않은 운영 PASS를 꾸미지 않는다.
- 한 사건 안의 독립 현상은 각 증거를 남기고 필요한 경우 분리한다. 해결된 부분만 `resolved_subscope`로 적되 남은 안전 불일치를 가리지 않는다.
- `OPEN → CLOSED` 이동은 지팀장이 실제 파일 이동과 STATUS의 변경분만 반영한다. RunLab은 제안·관측만 하며 RF/큐 이동·merge·DONE을 하지 않는다.

## 3. 표준 기록 (신규 사실만)

`ISSUE32_COMMENT | CASE_ID | OBSERVED_RUN_ID | RUN_IMAGE_DIGEST | RUN_SOURCE_SHA/UNKNOWN | SYMPTOM | CONFIDENCE(OBSERVED/REPRODUCED/UNKNOWN) | CATEGORY(CODE/ENV/SAFETY/UNKNOWN) | ASSIGNED_TO | RF_CANDIDATE/CONFIRMED | EVIDENCE_PATH | PROTECTED_APPROVAL_REQUIRED | DEV_STATUS | RUNTIME_STATUS | NEXT`

- raw 원본 증거는 RunLab 보존 위치, 공개 문서는 최소 식별·증거 경로·sanitized summary만 기록한다. 계좌/시크릿/토큰/개인정보 복제 금지.
- **Safety hold는 해당 거래·운영/보호 범위에만**, 일반 P1.5 무관 RF의 진척·기존 정상 peer PASS를 취소하지 않는다.
- `RUN_SOURCE_SHA=UNKNOWN`이면 버전별 운영 PASS는 BLOCKED지만 Docker 건강/실제 모의 브로커 관측은 별도 증거로 유지. HEAD 차이 자체는 결함/재배포 사유가 아니다.
- **변경분만 읽고 갱신:** 매회 Issue #32 전체 과거·93 RF 전체·R00 전체를 재탐색하지 않는다. 동일 SHA/동일 범위 개발 테스트 중복 금지.

## 4. 현재 OPEN 연계

**[RUNLAB32_INTAKE_20261027](../../refactor/plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md)**는 2026-10-26~27 기록을 기반으로 접수한 최초 집계다. 지팀장에게 `ORDER/SELL provenance·Guard/Reconciliation → Codex B 원인 추적`, `Reporter/metrics truth → Claude A 원인 추적`, `OCI provenance·일정/환경 → RunLab 읽기 전용 진단`을 배정하도록 C00에 연결한다. **이 배정은 안전 계약 코드 수정이나 RunLab 재배포 승인과 동일하지 않다.**
