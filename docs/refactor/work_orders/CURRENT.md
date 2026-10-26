# Agentra P1.5 — CURRENT 작업 큐

**POLICY_NOTICE (A/B 다음 실행 강제 확인):** D00·D03 연속 작업 및 매 실행 HANDOFF+Issue 완료 보고 규칙이 변경됐다. `integration/p1.5`의 D00·D03와 B는 D01(`AGENTS.md`), A는 D02(`CLAUDE.md`) **최신 원격 blob SHA 확인 → 이전 읽은 SHA와 비교 → 변경된 본문 필독**. Codex B는 이전 HANDOFF의 D00 `05223b75`/D03 `dba165fd`를 최신 정책으로 간주하지 말 것. 정책 확인 없이 `NO_CHANGE`·조기 종료 불가. 각 회차 HANDOFF 최신 기록 push + Issue A #11/B #12 누적 완료 댓글 필수. 1시간 예약은 단일 테스트 후 종료하지 않고 실행 가능한 RF를 연속 소비. 지팀장은 양쪽 수신 확인 후 이 임시 공지를 제거한다.

> 정본: `integration/p1.5`. [D00 안전·권한](../../ENGINEERING_DELIVERY_POLICY.md) · [D03 실행·검증](D03_DEV_TEAM_RULES.md) · [D01 B](../../../AGENTS.md) · [D02 A](../../../CLAUDE.md) · [STATUS](../plan/STATUS.md)

| 담당 | 지금 실행할 작업 | 다음 작업·해제 조건 |
|---|---|---|
| Claude A ([HANDOFF_A](HANDOFF_A.md)) | **1순위 RF-013 branch-local REWORK:** `f67bf1ec` 계열의 미승인 `q8_shadow_readout_p15.py` 및 직접 의존하는 후보를 소유 경계 내에서 최소 원복해 A 브랜치 p171 동결 2 FAIL을 제거하고 실제 source SHA 제출; frozen 테스트·오라클 불변. | B에게 exact SHA peer 요청 후 RF-019 잔여 4문장·다음 실제 owner 구현 진행. 단순 coverage 보고로 종료 금지. |
| Codex B ([HANDOFF_B](HANDOFF_B.md)) | **1순위 RF-001 실제 구현:** 기존 `data_access_core.py` 내부 허용 owner 경계의 최소 책임 분리 코드 SHA 제출. 안전하게 불가능하면 함수·동결 AST 제약과 KEEP 근거를 확정하고 같은 회차 다른 구현 가능한 B RF 진행. | A 신규 RF-013 원복 SHA가 오면 p171 실패 2 node·RF-074 경계 exact-SHA 독립 peer. RF-017 기존 7/7 재실행 금지; RF-070 32 위험 launcher NOT_RUN 유지. |
| 지팀장 | A/B 새 source SHA만 판정하고 RF-013 A branch 회귀와 RF-019 owner 경계를 분리. RF-017 5 owner KEEP 및 B peer 7/7 증거 수용(전체 DONE 아님). RF-001 과거 28 FAIL 해결은 CLOSED, 잔여 인수조건은 별도 추적. | 새 SHA→peer→필요시 REWORK→선별 통합→integration exact-SHA normal/-O 검증 후 DONE. HANDOFF-only를 코드 진척으로 계산하지 않음. |

**기록 위치:** RF = 개별 결정·실패·검증·차단·재개 조건. HANDOFF_A/B = 이번 실행의 신규 코드 SHA·명령·결과. STATUS = RF 집계. CURRENT = 담당·우선순위·링크만. 기존 증거는 재사용한다.

**런검증:** [별도 CURRENT](../../runtime/validation/CURRENT.md) · [D04](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md) · [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32). 코드 수정·RF 판정·통합 권한 없음.
