# C01 — Codex B 현재 작업 (2026-10-27 · 독립 검증 우선)

**작업 브랜치:** `work/p15-b-operator-structure-20261022` (마지막 확인 HEAD `43017525`). **정본 규칙:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md), [LEAD 작업표](../plan/queue/04_LEAD_ACCEPTANCE/LEAD_CURRENT.md). B는 A 소유 RF의 **독립 검증자**, B 소유 RF의 구현자다. 새 지팀장 승인 회차를 만들지 않는다.

## P0 공통 RunLab #32 — 지팀장 배정 조사 (D04)

**사건:** [RUNLAB32-20261027 OPEN](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md) · [D04](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md). **개발 Codex B**는 `RL32-ORDER/GUARD`(mock SELL 출처/로컬 기록 누락, buy/sell fill-truth·TTL, broker↔local reconciliation, readiness) **소스 읽기 전용 추적·격리 fake 재현만 담당**한다. `execute_from_packet.py` 등 보호 경로는 임의 수정하지 않는다. 실행 이미지 `RUN_SOURCE_SHA=UNKNOWN`이므로 현재 개발 HEAD 결함이라고 단정하지 않는다. 확인한 source SHA·producer/consumer·재현 범위/NOT_RUN·소유 RF 후보를 HANDOFF_B의 신규 delta로 지팀장에게 전달한다. **RF 소유 판정·안전 변경 승인은 지팀장/사용자**. 별도 RunLab PC의 Codex 스케줄 작업을 변경하거나 대신 실행하지 않는다. P0 신규 사실 인수 후 기존 RF-052/043 peer·일반 RF 개발을 계속한다.

## 즉시 실행

1. **RF-052 — 신규 A 패치 B 독립 peer:** A 브랜치 최신 `ba32a86a`, `libs/market_data/receipts.py::resolve_archive_path` Windows drive/UNC/backslash traversal 보완. A의 `pytest` 40 PASS·normal/-O 경계 결과는 원개발 근거. **B가 수정 SOURCE blob `10283d8f`의 경로 거부·정상 경로 유지·관련 호출자에 대해 독립 오프라인 peer**를 제출. UEF5 보호 계약, frozen oracle, 운영 데이터 실행·변경 금지. RF-052는 integration 실물 `03_PEER_REVIEW/CLAUDE_A` 배정 완료·코드 미통합; 정확 source 확인.
2. **RF-043 — A 소유 `libs/catalog` 6개 KEEP_VERIFIED 후보:** 기존 A 자체 normal/-O는 peer가 아니다. 원래 RF 수용 조건과 source/integration byte identity를 확인해 **최소 독립 peer**를 수행하고 결과 제출. 임의 모든 소비자/State/예외 전수 확장 금지.
3. **LEAD 기존 scoped 증거 재사용:** RF-031 실제 caller 8/8, RF-050 fake router 10/10, RF-029 truth-root, RF-016 nested projection, RF-014 Top1 등 B 기존 PASS를 **그대로 지팀장에 인계**. 원래 수용 조건이 실제 비어 있을 때만 해당 첫 결함/조건을 추가 검증한다. 같은 명령·동일 경계 재실행 금지.
4. **A run142 신규 peer·원개발 게이트:** RF-041 `libs/ai` 6개, RF-053 `libs/news` 12개 KEEP 후보의 동일 SOURCE SHA·원래 범위 독립 peer. RF-021 A `libs/runtime/monitor_exit/policy_map_builder.py` 수정 blob `dc9d6528`(cold import circular ImportError fix) 독립 peer는 보호 실행 없이 격리 temp로만; 원 RF 32 owner의 SAFETY_HOLD_KEEP는 승인 없이 해제/통합 금지. RF-051 `libs/market` 8개는 네트워크·쓰기 fake 효과 A owner 미완료라 DEVELOPING. RF-021/051은 `02_DEVELOPING/CLAUDE_A`, RF-041/053은 `03_PEER_REVIEW/CLAUDE_A`로 integration 실물 이동 완료. 동일 검증 반복 금지.
5. **B owner RF-066/070/071 → 일반 UNASSIGNED:** 자기 코드 개발을 진행한다. 다른 RF가 BLOCKED라도 계속 진행한다. A의 RF-046/047/054/058 KEEP 후보는 원개발 근거일 뿐, B peer는 아직 확인되지 않았으므로 중복 없는 범위에서 후속 독립 검증한다.

## 증거·안전

- HANDOFF_B에 `RF | SOURCE SHA | original acceptance coverage | PEER_PASS / SCOPED_PASS / FAIL / NOT_RUN | command·exit | external effects | NEXT`의 **새 변화만** 기록. Issue #12 반복 댓글 금지.
- **Peer PASS면 지팀장이 직접 새 Python/Windows 테스트를 요구하는 단계가 없다.** 지팀장에게 SHA·통합·CI 판정만 넘긴다.
- `main`, 실거래·주문, Broker/Supervisor/Executor/Step5C/UEF 안전 계약, frozen CI/oracle, 비밀·운영데이터·배포·예약 무승인 변경/실행 금지. Mock/temp-only. UI 변경 시 patchnotes, 테스트 산출물 보존정책 준수.
