# Agentra P1.5 — CURRENT 작업 큐

**POLICY_NOTICE (A/B 다음 실행 강제 확인):** D00·D03 연속 작업 및 매 실행 HANDOFF+Issue 완료 보고 규칙이 변경됐다. `integration/p1.5`의 D00·D03와 B는 D01(`AGENTS.md`), A는 D02(`CLAUDE.md`) **최신 원격 blob SHA 확인 → 이전 읽은 SHA와 비교 → 변경된 본문 필독**. Codex B는 이전 HANDOFF의 D00 `05223b75`/D03 `dba165fd`를 최신 정책으로 간주하지 말 것. 정책 확인 없이 `NO_CHANGE`·조기 종료 불가. 각 회차 HANDOFF 최신 기록 push + Issue A #11/B #12 누적 완료 댓글 필수. 1시간 예약은 단일 테스트 후 종료하지 않고 실행 가능한 RF를 연속 소비. 지팀장은 양쪽 수신 확인 후 이 임시 공지를 제거한다.

> 정본: `integration/p1.5`. [D00 안전·권한](../../ENGINEERING_DELIVERY_POLICY.md) · [D03 실행·검증](D03_DEV_TEAM_RULES.md) · [D01 B](../../../AGENTS.md) · [D02 A](../../../CLAUDE.md) · [STATUS](../plan/STATUS.md)

| 담당 | 지금 실행할 작업 | 다음 작업·해제 조건 |
|---|---|---|
| Claude A ([HANDOFF_A](HANDOFF_A.md)) | [RF-019](../plan/pending/RF-019.md) 남은 약 5문장·p171 CROSS_RF 소비자/State 증거 보완(기존 99.6% 자체 PASS 재실행 금지); B 신규 코드 SHA만 peer | [RF-017](../plan/pending/RF-017.md); B [RF-001](../plan/verification/codex/RF-001.md) 수정 SHA 도착 시 우선 peer |
| Codex B ([HANDOFF_B](HANDOFF_B.md)) | [RF-017](../plan/pending/RF-017.md) **integration exact SHA `3f1677cc`의 5-owner KEEP** public import/projection/negative peer normal/-O (A branch에는 4경로 없음; 기존 56 BASELINE 재실행 금지); [RF-019](../plan/pending/RF-019.md) evidence 외 신규 위험 경계만 peer; [RF-070](../plan/pending/RF-070.md) 잔여 25개 기타 구현 read-only 소비자·효과 경계 정리 | [RF-001](../plan/verification/codex/RF-001.md) 신규 owner-local 결함 SHA 도착 시만 재개; 32개 위험 launcher 실행 금지 |
| 지팀장 | RF-017 5 owner BASE=integration `3f1677cc` blob 5/5 동일 직접 확인; A branch 4경로 부재는 후보 트리 문제로 분리, B peer 대상 integration KEEP으로 확정(RF-017 기록). A RF-017 273문장 100% normal/-O SELF_PASS_SCOPED, B peer NOT_RUN. RF-019 A 29-owner 약 99.6% SELF_PASS_SCOPED 및 B evidence/guard/practical/overlay normal/-O 독립 scoped PASS 수용; p171 CROSS_RF·잔여 State/효과 미종결. 신규 SHA·peer 판정, [RF-001](../plan/verification/codex/RF-001.md) KEEP 복귀 후 남은 전체 인수조건·교차 RF 차단 판정, [RF-013](../plan/verification/claude/RF-013.md) 소유권 HOLD 유지 | 인수조건 충족 RF만 선별 통합 및 통합 SHA normal/-O 검증 |

**기록 위치:** RF = 개별 결정·실패·검증·차단·재개 조건. HANDOFF_A/B = 이번 실행의 신규 코드 SHA·명령·결과. STATUS = RF 집계. CURRENT = 담당·우선순위·링크만. 기존 증거는 재사용한다.

**런검증:** [별도 CURRENT](../../runtime/validation/CURRENT.md) · [D04](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md) · [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32). 코드 수정·RF 판정·통합 권한 없음.
