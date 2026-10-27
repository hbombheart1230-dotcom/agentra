# P1.5 작업 문서 — 현재 실행 진입점

**읽기 순서:** [C00 지팀장 CURRENT](CURRENT.md) → [D00 공통 계약](D00_ENGINEERING_DELIVERY_POLICY.md) → [LEAD 14건 최종 종결표](../plan/queue/04_LEAD_ACCEPTANCE/LEAD_CURRENT.md) → 필요한 개별 RF. [STATUS](../plan/STATUS.md)는 마지막 확인된 실물 상태다.

**역할별 현재 작업:** [C01 Codex B](C01_CODEX_CURRENT.md) · [C02 Claude A](C02_CLAUDE_CURRENT.md).

**원칙:** 원래 RF 필수 수용 조건에 대한 반대 작업자의 유효한 독립 peer PASS를 지팀장은 재테스트하지 않는다. SHA·통합 충돌·보호 경계·필수 CI만 확인하고 충족 즉시 DONE. `SCOPED_PASS`는 전체 PASS가 아니지만 무관한 Windows/CLI/State 전수검증을 신규 게이트로 추가하지 않는다. 보호 주문/UEF/frozen oracle/운영 경계는 별도 승인 전 금지.

**기록:** 과거 D03·D05·D06, 개별 RF 문서의 예전 HOLD/지시, 기존 evidence·archive는 시점별 실행 이력이다. **원래 각 RF의 작업 목표와 DONE 체크는 유지**하며 현재 작업 지시로는 최신 D00·C00·LEAD_CURRENT가 우선한다.
