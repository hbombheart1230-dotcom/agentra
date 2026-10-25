# D01 — Codex B 역할 포인터

- **시작:** [개발 CURRENT](docs/refactor/work_orders/CURRENT.md) → [D00](docs/ENGINEERING_DELIVERY_POLICY.md) → [D03](docs/refactor/work_orders/D03_DEV_TEAM_RULES.md). 변경된 규칙만 재독.
- **브랜치:** `work/p15-b-operator-structure-20261022`. 기존 작업장 사용, 신규 브랜치 금지.
- **역할:** B 소유 RF의 실제 구현·KEEP 실증, Claude A RF의 신규 SHA 독립 read-only 검증.
- **실행:** 실행 가능한 자기 REWORK를 먼저 수정하거나 재현 가능한 기술 차단을 제출한다. 이후 상대 신규 증거 peer와 다음 실행 가능한 자기 RF를 진행한다. 단순 ACK·상태 재보고는 코드 진척이 아니다.
- **권한:** 상대 RF 코드·테스트·fixture 및 미승인 공유 계약·안전·오라클 수정 금지. RF 판정·큐 이동·통합·DONE은 지팀장만.
- **증거:** 자기 브랜치 `docs/refactor/work_orders/HANDOFF_B.md` 최신 회차에 코드 SHA·변경 경로·normal/-O 결과·peer 판정·차단 및 재개 조건만 기록. 동일 증거 반복·문서-only 빈 커밋 금지. D00·D03 게이트 유지.
