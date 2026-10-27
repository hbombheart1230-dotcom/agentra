# C01 — Codex B 현재 작업 (2026-10-27 · 독립 검증 우선)

**작업 브랜치:** `work/p15-b-operator-structure-20261022` (마지막 확인 HEAD `43017525`). **정본 규칙:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md), [LEAD 작업표](../plan/queue/04_LEAD_ACCEPTANCE/LEAD_CURRENT.md). B는 A 소유 RF의 **독립 검증자**, B 소유 RF의 구현자다. 새 지팀장 승인 회차를 만들지 않는다.

## 즉시 실행

1. **RF-052 — 신규 A 패치 B 독립 peer:** A 브랜치 최신 `ba32a86a`, `libs/market_data/receipts.py::resolve_archive_path` Windows drive/UNC/backslash traversal 보완. A의 `pytest` 40 PASS·normal/-O 경계 결과는 원개발 근거. **B가 수정 SOURCE blob `10283d8f`의 경로 거부·정상 경로 유지·관련 호출자에 대해 독립 오프라인 peer**를 제출. UEF5 보호 계약, frozen oracle, 운영 데이터 실행·변경 금지. RF-052는 현재 integration 실물 큐 승격/통합 전; 먼저 CLAIM 충돌/정확 source 확인.
2. **RF-043 — A 소유 `libs/catalog` 6개 KEEP_VERIFIED 후보:** 기존 A 자체 normal/-O는 peer가 아니다. 원래 RF 수용 조건과 source/integration byte identity를 확인해 **최소 독립 peer**를 수행하고 결과 제출. 임의 모든 소비자/State/예외 전수 확장 금지.
3. **LEAD 기존 scoped 증거 재사용:** RF-031 실제 caller 8/8, RF-050 fake router 10/10, RF-029 truth-root, RF-016 nested projection, RF-014 Top1 등 B 기존 PASS를 **그대로 지팀장에 인계**. 원래 수용 조건이 실제 비어 있을 때만 해당 첫 결함/조건을 추가 검증한다. 같은 명령·동일 경계 재실행 금지.
4. **B owner RF-066/070/071 → 일반 UNASSIGNED:** 자기 코드 개발을 진행한다. 다른 RF가 BLOCKED라도 계속 진행한다. A의 RF-046/047/054/058 KEEP 후보는 원개발 근거일 뿐, B peer는 아직 확인되지 않았으므로 중복 없는 범위에서 후속 독립 검증한다.

## 증거·안전

- HANDOFF_B에 `RF | SOURCE SHA | original acceptance coverage | PEER_PASS / SCOPED_PASS / FAIL / NOT_RUN | command·exit | external effects | NEXT`의 **새 변화만** 기록. Issue #12 반복 댓글 금지.
- **Peer PASS면 지팀장이 직접 새 Python/Windows 테스트를 요구하는 단계가 없다.** 지팀장에게 SHA·통합·CI 판정만 넘긴다.
- `main`, 실거래·주문, Broker/Supervisor/Executor/Step5C/UEF 안전 계약, frozen CI/oracle, 비밀·운영데이터·배포·예약 무승인 변경/실행 금지. Mock/temp-only. UI 변경 시 patchnotes, 테스트 산출물 보존정책 준수.
