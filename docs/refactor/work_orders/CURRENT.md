# Agentra P1.5 — CURRENT

**원칙:** 한 RF = 한 실행 담당. 완료 이력은 [STATUS](../plan/STATUS.md)·각 RF·HANDOFF에서 확인한다. 이 파일은 **현재 행동만** 적는다.

**정본 읽기:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) → [D03](D03_DEV_TEAM_RULES.md) → [A 역할](../../../CLAUDE.md) / [B 역할](../../../AGENTS.md). 물리 큐 [D05](D05_RF_PHYSICAL_QUEUE_20261026.md)·[D06](D06_RF_ATTEMPT_AND_AUDIT_20261026.md).

## 현재 실행 큐

| 순서 | RF | 현재 실행 담당 | 지금 할 일 | 넘길 조건 |
|---|---|---|---|---|
| A-1 | [029](../plan/queue/01_PENDING/CLAUDE_A/RF-029.md) | **지팀장** | A 기존 38 owner KEEP/FIX0 근거 인수 판정. 새 결함 없으면 peer 이동, 있으면 파일·재현·FIX 범위 특정 | B peer 또는 구체 REWORK |
| A-2 | **다음 A 소유 PENDING RF** | **A Claude** | RF-029 결과 대기 없이, 물리 큐에서 A 소유·비동결·미착수 RF를 선정해 실제 코드 개발. RF 번호·파일·소유권 확인 후 HANDOFF에 기록 | 최소 FIX·소스 SHA·focused normal/-O 또는 근거 있는 KEEP |
| B-1 | [070](../plan/queue/02_DEVELOPING/CODEX_B/RF-070.md) | **B Codex** | 안전한 잔여 owner 중 재현 가능한 소비자·IO/side-effect 결함을 최소 FIX. 위험 launcher 32개 HOLD | 신규 소스 SHA 또는 특정 BLOCKED |
| B-2 | [066](../plan/queue/02_DEVELOPING/CODEX_B/RF-066.md) | **B Codex** | fake OrderClient·임시 경로로 미검증 요청 계약을 확인하고 실제 결함만 FIX. 주문·고정 파일 쓰기 금지 | 신규 소스 SHA 또는 특정 BLOCKED |
| V-1 | [001](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-001.md) | **B Codex (1회 검증)** | 최신 integration HEAD 격리 read-only, 아래 3파일 normal/-O 각 1회; HEAD·exit·실패 node 제출. 개발 반복 금지 | **지팀장**이 33 owner 인수·DONE 판정 |
| V-2 | [028](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-028.md) | **B Codex (최초 peer)** | A 기존 KEEP 증거 재사용, 미검증 동적 소비자·State/IO·예외 경계만 독립 peer | **지팀장**이 LEAD_ACCEPTANCE·KEEP 판정 |

**RF-001 검증 명령 대상:** `tests/test_p153_operator_ui_moved_bodies.py` · `tests/test_operator_ui_data_access_phase2.py` · `tests/test_operator_ui.py`. 동일 세 파일을 `python -m pytest -q`와 `python -O -m pytest -q`로 각각 실행한다.

## 예약 회차 처리

- **A:** A-2 실제 개발을 계속한다. RF-029는 지팀장 판정 대기 중이므로 동일 증거를 반복하지 않는다.
- **B:** B-1 → B-2 개발을 계속한다. V-1/V-2는 **최초 미검증 경계에 한해 1회** 수행하며, 검증 때문에 자기 개발을 계속 미루지 않는다. 한 회차에 전부 못 하면 미착수 이유와 다음 항목을 HANDOFF에 남긴다.
- **지팀장 (매시 02·32분):** A/B 신규 SHA·검증 결과 회수 → RF-029 직접 판정 → V-1/V-2 결과 인수 → 물리 큐 이동·선별 통합·STATUS 정합화. 다음 A RF가 아직 특정되지 않았으면 큐에서 소유권을 확인해 번호를 지정한다.

**금지:** 동일 SHA·동일 테스트 반복, ACK/문서만으로 종료, Issue 댓글로 배정, 다른 RF owner 무단 수정, main·실거래·안전 계약·동결 오라클 무승인 변경. GitHub 쓰기 실패 시 원인 구분·허용된 재시도·원격 SHA 확인; 안전 검사 우회 금지. **NOT_RUN/BLOCKED/부분 PASS ≠ DONE.**
