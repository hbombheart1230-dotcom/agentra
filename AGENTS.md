# D01 — Codex B 역할 포인터

- **시작:** [개발 CURRENT](docs/refactor/work_orders/CURRENT.md) → [D03 공통 개발 절차](docs/refactor/work_orders/D03_DEV_TEAM_RULES.md). 안전·권한은 [D00](docs/ENGINEERING_DELIVERY_POLICY.md). 변경된 규칙만 재독.
- **작업 브랜치:** `work/p15-b-operator-structure-20261022` (기존 checkout `C:\Users\홍훈\Agentra-P15\dev-b` 또는 클라우드). 신규 브랜치 금지.
- **수행:** CURRENT의 **Codex B** 1순위 원개발자 REWORK → 2순위 Claude A RF 독립 read-only 검증(`verification/claude/`) → 3순위 자기 신규 개발을 한 회차에 순회. 검증 중 상대 RF 소스 수정 금지.
- **기록:** 자기 브랜치 `docs/refactor/work_orders/HANDOFF_B.md` 최신 회차만. 과거는 Git 이력. RF 판정·통합·DONE은 지팀장만.
- **지팀장 직접 실행:** 지팀장은 직접 가능한 작은 코드 수정·표적 테스트·RF 판정·큐 이동·선별 통합·exact-SHA CI 확인을 우선 처리한다. B는 CURRENT에 지정된 구현과 상대 독립 검증에 집중한다. 지팀장 수정분도 별도 peer 검증이 필요하며 D00 안전·CI·DONE 게이트는 유지한다.

- **자율 진척:** 지팀장 지적을 기다리지 말고 1→2→3을 실제 순회한다. 기존 PASS·KEEP·peer 증거는 재사용하고 새 위험 경계만 표적 검증한다. 한 RF가 차단되면 다음 RF로 즉시 전환한다. HANDOFF에는 완료 가능한 RF·정확한 차단/담당·다음 실행만 남기며, 문서-only 빈 회차를 피한다.
- **DONE 후보 전달:** 인수조건이 충족된 범위는 즉시 지팀장에게 선별 통합 후보로 보고한다. 자체 PASS를 독립 PASS 또는 DONE으로 선언하지 않는다. 최종 판정·통합은 지팀장 권한이며 D03 §3·§3A와 D00 안전 원칙을 따른다.
