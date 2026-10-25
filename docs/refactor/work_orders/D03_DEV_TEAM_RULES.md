# D03 — Agentra P1.5 개발팀 공통 실행·검증 규칙

> **개발팀 정본.** 시작은 [CURRENT](CURRENT.md), 공통 안전·권한·증거는 [D00](../../ENGINEERING_DELIVERY_POLICY.md), 역할/브랜치는 [D01 Codex](../../../AGENTS.md)·[D02 Claude](../../../CLAUDE.md). PC 런검증팀은 별도 D04. D00과 역할별 문서의 내용을 이곳에 복제하지 않는다.

## 1. 정본·소유권
- P1.5 전체 ROOT→LEAF 범위는 [T00](../architecture/T00_TARGET_TREE.md), RF 93개·소유 파일은 [FILE_COVERAGE](../plan/FILE_COVERAGE_63182ab2.csv), 상태는 [STATUS](../plan/STATUS.md), 건별 인수조건·차단·결정은 **해당 RF**가 정본이다. 동결 V3/P1.5.0~11 기준 유지.
- `integration/p1.5`와 RF/CURRENT/STATUS는 **지팀장 단일 writer**; A/B는 각자 기존 work 브랜치의 소유 파일과 HANDOFF만 수정. 타 RF 파일·공개 공유 계약은 read-only, 별도 소유권/승인 판단 전 변경 금지. 정상적인 브랜치 divergence는 차단 사유가 아니다.
- 시작 시 repo ROOT·checkout·원격 HEAD·정확한 후보 SHA를 확인하고, push 후 원격 HEAD를 재확인한다. 기존 작업장·사용자 데이터 보존. D00 금지 사항은 모든 단계에 우선한다.

## 2. 한 회차 실행 — 개발을 멈추지 않는 루프
- **반드시 1→2→3 모두 순회:** (1) CURRENT의 자기 원개발자 REWORK에서 승인된 최소 수정/KEEP 실증, (2) 상대 RF 신규 SHA·새 증거만 별도 read-only 독립 검증, (3) 자기 신규 RF 개발. 앞 순위를 수행해도 다음 순위를 확인한다. 차단된 RF만 건너뛰며 회차당 RF 1건 제한 없음.
- **증거 재사용:** 동일 SHA·동일 테스트 재실행 금지. 이미 입증된 blob parity·normal/-O·peer PASS_SCOPED는 유지한다. KEEP은 의미 없는 소스 수정을 요구하지 않고, 미검증 소비자/호출/State/IO/예외/부작용 **위험 경계만** 표적 offline/mock normal·`python -O`로 확인한다. 새 회귀는 BASE와 같은 조건으로 비교해 BASELINE_EXISTING/ENVIRONMENT/CROSS_RF_OWNER/UNKNOWN을 분리한다.
- **빠른 검증 전환:** RF에 적힌 **잔여 인수조건**이 충족되면 지팀장은 같은 점검 회차에 verification 복귀를 판정하고 상대는 신규 경계만 독립 검증한다. 새 코드 SHA 또는 유효한 독립 검증 증거를 회차 목표로 삼되, 실제 도구 한도·권한 차단이면 원인/재개 트리거를 남긴다. 임의로 PASS/DONE을 만들지 않는다.
- 소스 수정 시 기존 import·동적 patchability·공개 API·side effect·거래 안전 동등성 및 UI 연결 patchnotes JSON/MD를 확인한다. 테스트 산출물은 격리·정리하며 오라클 변경으로 실패를 숨기지 않는다.

## 3. RF 상태·독립 검증·통합
- **RF 단일 위치:** `pending/` → `verification/{claude|codex}/` ↔ `rework/{claude|codex}/` → `done/`; 하위 폴더명은 **원개발자**다. 큐 이동·최종 DONE은 지팀장만. 원개발자만 REWORK 소유 경로 수정, 검증자는 상대 RF의 코드·테스트·fixture 수정 금지.
- REWORK는 독립 검증에서 재현된 소유 경로 결함 또는 **구체적 미충족 계약**에 한정. 지팀장은 RF에 BASE/후보 SHA·실패 node·FIX_OWNER·허용 경로·최소 보완 또는 KEEP 실증·다음 peer를 명시한다. 기존 BASE 실패·환경 문제·교차 소유권·안전/CI 오라클 HOLD만으로 REWORK를 만들지 않는다.
- 자체 테스트 PASS ≠ peer PASS. 상대는 정확한 후보 SHA와 변경된 위험 경계만 별도 read-only 세션에서 검증하고 PASS/REWORK/BLOCKED·명령·exit·근거를 보고한다. PASS_SCOPED ≠ 전체 PASS.
- **통합/DONE:** 전체 peer PASS 및 소유권 승인 후 지팀장이 해당 RF 소유 경로만 `integration/p1.5` 최신 HEAD에 CAS/비강제 선별 반영(브랜치 통째 병합 금지). 새 통합 **정확한 SHA**의 normal/-O 및 필수 hosted GitHub Actions GREEN 확인 후에만 DONE. CI RED/UNKNOWN/NOT_RUN은 GREEN이 아니다. 기존 CI 오라클은 변경하지 않는다.


## 3A. 테스트 우선 종결 판정 (RF-001~093 공통)
- **테스트와 코드가 판정 기준:** 해당 RF 인수조건을 커버하는 기존 normal/-O 테스트 PASS 및 기존 peer 근거는 그대로 인정한다. 문서/HANDOFF만 변경되면 코드·테스트 blob 동일성을 확인해 증거를 재사용한다. SHA는 테스트 대상 코드 식별자이며 문서 커밋 HEAD 자체를 새 코드로 취급하지 않는다.
- **PASS 범위 명시:** 테스트 PASS 숫자만으로 미실행 계약까지 PASS라 하지 않는다. 다만 미충족 주장 시 지팀장은 **정확한 테스트 부재/실패 사례, 변경 경로·호출자, 실제 위험** 중 구체적 근거를 RF에 적는다. 기존 테스트가 해당 동작을 이미 검증하면 추가 테스트·REWORK 요구 금지. 구체적 근거가 없으면 '추가 검증 요구'를 해제하고 peer/통합 판단으로 진행한다.
- **REWORK는 코드 결함에만:** 재현 가능한 소유 코드 결함 또는 변경으로 생긴 구체적 회귀가 확인된 경우에만 원개발자 REWORK. 미실행·기존 BASE 실패·CI 조회 불가·타 RF 소유권 HOLD·증거 서식 미비는 별도 BLOCKED/운영 조치로 분리하고 신규 코드 수정 요구 금지.
- **검증은 한 번, 통합은 따로:** 원개발자 표적 테스트 → 상대 변경 범위 read-only peer → 지팀장 선별 통합 → 통합 SHA의 기존 필수 CI/normal/-O → DONE. 이미 입증된 단계는 반복하지 않는다. CI UNKNOWN/NOT_RUN은 FAIL로 간주하지 않지만 GREEN으로도 간주하지 않으며, CI 실행·조회 원인 확인은 지팀장 책임이다. CI/안전 가드·오라클 및 DONE 필수 게이트는 변경하지 않는다.
- **93개 RF 적용:** 이 절은 RF-001~093 전체에 즉시 적용하며 93개 RF에 동일 문구 복사 금지. 각 RF에는 필요할 때만 '기존 유효 PASS / 미충족 구체 사례 / 담당자 / 다음 판정'을 짧게 갱신한다.

## 4. 기록·지팀장 책임
- `CURRENT` = **작업 포인터/규칙 변경 알림만**. `RF` = 해당 건의 결정·잔여 증거·재개 조건. `STATUS` = 전체 현황. `HANDOFF_A/B` = **최신 실행 10~20줄만 교체**, 과거는 Git 이력. 새 총괄 문서·반복 일지·빈 커밋 금지.
- HANDOFF는 RUN_ID, 시작/후보 **코드 SHA**(HANDOFF 커밋과 구분), RF별 변경 경로, normal/-O 명령·exit, 독립 verdict, BLOCKED 원인·재개 트리거, patchnotes, CI SHA/상태, GPT_ACTION_REQUIRED, push 확인을 간결히 담는다. 실질적 새 증거가 없으면 NO_CHANGE로 보고하고 문서만 커밋하지 않는다.
- 지팀장은 매 점검 **CURRENT → A/B 원격 HEAD·최신 HANDOFF → 변경된 RF 증거 → 런검증 [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32) 신규 내용 → STATUS·exact-SHA CI**만 확인. 멈춘 RF는 그 회차에 직접 소유권·원인·최소 다음 행동을 확정하고 실행 가능한 다음 RF로 넘긴다. 새 peer 증거는 같은 회차에 판정하고, 완전 peer PASS는 선별 통합/CI 단계로 즉시 넘긴다. 같은 SHA 전수 재검증·중복 감사 금지.
- 보고는 **A/B 진행 → 지팀장 실제 조치/커밋 → RF·CI → 다음 행동** 순서. 계획·부분 PASS·NOT_RUN을 DONE으로 보고하지 않는다. 별도 예약 생성/변경은 사용자 승인 없이 하지 않는다.
