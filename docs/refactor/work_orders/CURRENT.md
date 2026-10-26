# Agentra P1.5 — CURRENT (지팀장 배정, 이번 턴)

| 담당 | 지금 턴에 실행할 RF와 작업 |
|---|---|
| **A Claude** | **[RF-030](../plan/queue/01_PENDING/UNASSIGNED/RF-030.md) (16 owner, reporting/operator period summary)**: `libs/reporting/operator_period_summary.py` 및 `operator_period_summary_parts/**`, `operator_candidate_decisions.py` 등 [FILE_COVERAGE](../plan/FILE_COVERAGE_63182ab2.csv)의 RF-030 전용 16파일. 소유권·호출/IO/State·실제 혼합 책임을 확인하고 재현 결함은 최소 FIX, 없으면 KEEP 근거 제출. RF-029 38 owner 증거 재검증 금지. 이어서 **[RF-031](../plan/queue/01_PENDING/UNASSIGNED/RF-031.md) (22 owner, reporter AI review)**. |
| **B Codex** | **[RF-071](../plan/queue/01_PENDING/UNASSIGNED/RF-071.md) (42 owner, scripts utilities)**: `scripts/analyze_entry_blockers.py`, `scripts/approval_cli.py`, `scripts/cleanup_pytest_artifacts.py` 등 [FILE_COVERAGE](../plan/FILE_COVERAGE_63182ab2.csv)의 RF-071 전용 42파일. 먼저 읽기/정적 분석으로 실행 효과 분류, 안전한 소비자·CLI 경계만 격리 검증, 실제 결함 최소 FIX 또는 KEEP. 운영 명령·파일 삭제·승인·주문 효과 실행 금지. 이어서 후속 RF는 지팀장 배정 대기. RF-070/066 기존 증거 재실행 금지. |
| **지팀장** | **RF-029 KEEP/FIX0 최종 인수 판정**, RF-070/066 KEEP/HOLD·남은 게이트 판정, RF-001 통합 SHA 검증 및 RF-028 최초 B peer 관리. **RF-030/031/071 신규 착수 철회, PEER_REVIEW와 LEAD_ACCEPTANCE 우선 처리**하고 정확한 경로 확인 후 큐 이동·STATUS 갱신. |

**배정 근거:** BASE `63182ab2`의 FILE_COVERAGE RF-030=16, RF-031=22, RF-071=42 owner. 이는 **이번 턴 실행 지시**이며 아직 물리 큐 이동이나 DONE 판정이 완료됐다는 뜻은 아니다. 세 RF 모두 실제 경로는 `01_PENDING/UNASSIGNED`로 조회·확인됐다. D05에 따라 지팀장이 원자적 이동하기 전까지 물리 상태는 미배정이며, A/B는 CURRENT의 지정된 독점 owner 범위만 착수한다.

**연속 실행:** 예약 한도까지 현재 RF를 진행하고 다음 회차에 그대로 이어간다. 동일 SHA·동일 경계 반복 금지. 신규 source SHA·증거와 미완료 지점만 HANDOFF에 기록.

**정본:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) → [D03](D03_DEV_TEAM_RULES.md) → [A 역할](../../../CLAUDE.md) / [B 역할](../../../AGENTS.md) · [D05 큐](D05_RF_PHYSICAL_QUEUE_20261026.md) · [STATUS](../plan/STATUS.md).

**안전:** main·실거래·안전 계약·동결 오라클·예약 무승인 변경 금지. 부분 PASS/BLOCKED/NOT_RUN ≠ DONE.
