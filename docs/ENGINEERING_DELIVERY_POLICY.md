# D00 — Agentra 공통 안전·권한·증거 원칙

> 각 팀은 **자기 CURRENT부터** 읽는다. 미변경 정본·동일 SHA 증거는 반복 조회하지 않는다. 개발팀: [CURRENT](refactor/work_orders/CURRENT.md) → [D03](refactor/work_orders/D03_DEV_TEAM_RULES.md) 및 D01/D02. PC 런검증팀: [검증 CURRENT](runtime/validation/CURRENT.md) → [D04](runtime/validation/D04_RUNTIME_VALIDATION_RULES.md). 런검증팀에는 A/B RF 업무 규칙을 적용하지 않는다.

## 1. 권한·안전 경계
- `main` 수정·병합은 사용자 명시 승인 전 금지. `integration/p1.5` 통합·RF 최종 DONE은 GPT 지팀장 책임이며, 개발 브랜치 전체 일괄 병합·무승인 강제 push 금지.
- 실계좌 주문/실거래 권한, Broker·Supervisor·Executor·Step5C·UEF 거래 안전 계약·가드·replay/write-safety, CI 오라클·테스트 기대값·allowlist·skip/xfail/waiver는 **명시 승인 없이 변경 금지**. 거부된 오라클 후보 `a0493b60`도 미승인 상태다. 테스트를 GREEN으로 만들기 위한 안전 우회 금지.
- P1.5.0~11 동결 합격 기준과 RF-021 안전 HOLD 유지. 공유 공개 계약·4-HEAD/PR31 합성·미승인 source admission은 지팀장 별도 판단·승인 없이는 통합하지 않는다.
- 모의투자 서버에서의 정상 API·주문 검증은 승인된 **런타임 운용** 범위이며, 안전 코드 수정이나 실계좌 권한 허가와는 별개다. 실계좌 자격 증명·개인 비밀은 코드·Git·검증 보고에 노출하지 않는다.

- **지팀장 직접 처리 의무:** GPT 지팀장은 승인된 소유 경계에서 직접 가능한 코드 수정·표적 테스트·RF 판정·큐 이동·CURRENT/STATUS 갱신·선별 통합·exact-SHA CI 확인을 A/B에 불필요하게 재위임하지 않고 즉시 수행한다. 실행 환경이 없으면 NOT_RUN으로 표시하고 실행 담당을 지정한다. 지팀장 직접 수정분도 별도 독립 검증이 필요하며 안전·CI·DONE 게이트는 그대로 유지한다.

## 2. 실행·증거의 신뢰성
- 시작 시 대상 저장소·브랜치·정확한 source SHA·설정 및 역할별 권한을 식별하고, 자기 작업장과 기존 상태·데이터를 보존한다. 권한 없는 수정·삭제·배포·통합을 하지 않는다.
- 수행한 명령, 대상 SHA, 실제 출구 코드·테스트·외부 호출·실패 근거를 기록한다. **NOT_RUN/UNKNOWN/BLOCKED를 PASS로 꾸미지 않는다.** 부분 PASS는 전체 PASS가 아니다.
- 실패는 가능하면 같은 조건의 BASE·후보 비교로 기존 문제와 신규 회귀를 구분한다. 반복 검증·중복 문서·불필요한 전체 테스트·빈 커밋을 피한다. 테스트 산출물은 격리하고 성공분 자동 정리·실패분 제한 보존한다.
- 역할별 상세 개발·독립 검증·선별 통합·exact-SHA CI·DONE 게이트는 **D03**, 실운영 동일 조건 PC 런검증·실제 키움 모의투자 증거는 **D04**가 정본이다. 서로의 승인 권한을 대체하지 않는다.
