# D02 — Claude A 역할 포인터

- **시작:** [개발 CURRENT](docs/refactor/work_orders/CURRENT.md) → [D00](docs/ENGINEERING_DELIVERY_POLICY.md) → [D03](docs/refactor/work_orders/D03_DEV_TEAM_RULES.md). 변경된 규칙만 재독.
- **브랜치:** `work/p15-a-reporter-pure-20261021`. 기존 작업장 사용, 신규 브랜치 금지.
- **역할:** A 소유 RF의 실제 구현·KEEP 실증, Codex B RF의 신규 SHA 독립 read-only 검증.
- **권한:** A 소유 경로만 수정. B RF는 read-only. RF 판정·큐 이동·통합·DONE은 지팀장만. 안전·절차는 D00·D03.
- **증거:** 자기 브랜치 `docs/refactor/work_orders/HANDOFF_A.md` 최신 회차에 코드 SHA·변경 경로·normal/-O 결과·peer 판정·차단 및 재개 조건만 기록. 기존 유효 증거는 재사용. **REWORK가 생기면 동일 RF 실제 코드 FIX/KEEP→B 신규 SHA peer→재수정 반복을 최우선 수행한다. REWORK가 없으면 소유 RF의 실제 개발을 진행한다.** Issue #11에 RUN별 전체 기술 결과를 길이 제한 없이 기록하고, B 조치 요청은 Issue #12에도 전달한다. HANDOFF 상세 제한 없음. RF 전체 DONE 판정은 지팀장.
