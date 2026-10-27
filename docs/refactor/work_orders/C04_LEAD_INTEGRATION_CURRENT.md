# C04 — 지팀장② | LEAD 통합·CI 보드

> 진입점 **C04 + [D00](D00_ENGINEERING_DELIVERY_POLICY.md)**. 구 `CURRENT.md` 사용 금지. C05가 실제 물리 `04_LEAD_ACCEPTANCE`에 이동한 RF만 처리한다.

## 지금 하는 일 — LEAD 3건

| 우선 | RF 원본 | 지금 필요한 결과 |
|---|---|---|
| 1 | [RF-046](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-046.md) | 정확한 source 동일성 + 해당 integration SHA의 요구 CI → C6 증거 |
| 2 | [RF-047](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-047.md) | KEEP_VERIFIED·요구 CI 재사용 가능 여부 → C6 증거 |
| 3 | [RF-052](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-052.md) | A 검증된 `receipts.py` 수정만 선별 통합 + 정확한 통합 SHA CI → C6 증거 |

현재 수치는 [STATUS](../plan/STATUS.md)와 [실물 LEAD 큐](../plan/queue/04_LEAD_ACCEPTANCE/)로 매회 다시 확인한다. 위 표는 완료 주장 아님.

## 매회 반드시 실제 실행

1. 링크된 RF **원본 C6 및 최신 C05 수용 기록**을 읽는다. Owner 정확 SHA·반대 peer의 원래 범위 full PASS·C05 C1~C5 승인 대조. 승격 전 RF에 대해 통합하지 않는다.
2. KEEP이면 소스 바이트 일치와 필요한 기존 CI 증거를 확인한다. 변경이면 승인된 최소 파일 diff만 선별 통합한다. A/B 브랜치 전체 병합 금지.
3. **정확한 통합 commit SHA**에 원래 필요한 CI PASS를 매칭한다. 결과가 없으면 `PENDING/NOT_RUN/FAIL`로 기록하며 C05에 DONE으로 넘기지 않는다.
4. C6 근거를 남겨 **[C05](C05_LEAD_CLOSEOUT_CURRENT.md)로 즉시 인계하고 다음 LEAD RF**를 처리한다. 한 건 실패·안전 HOLD 때문에 다른 LEAD 처리 중단 금지.
5. 후보가 진짜 0건이면 `NO_DELTA`; 실행 한도면 `EXECUTION_LIMIT`로 실제 미완료를 명시한다.

**소유권:** C04는 허용된 integration 소스·본 문서의 C6 인계만 수정. RF 체크·물리 큐·STATUS·DONE은 C05. 보호 실행/실거래/운영설정/UEF/frozen 변경은 D00에 따라 별도 승인 필수. 이미 DONE인 RF-043/053과 기존 동일 SHA/범위 테스트 반복 금지.

**보고 1줄/RF:** `RF 링크 | Owner/peer SHA | integration SHA | KEEP/INTEGRATED/BLOCKED | CI 결과 | C05 NEXT`.
