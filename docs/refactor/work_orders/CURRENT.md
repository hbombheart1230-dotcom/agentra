# Agentra P1.5 — CURRENT 작업 큐

> 정본: `integration/p1.5`. [D00 안전·권한](../../ENGINEERING_DELIVERY_POLICY.md) · [D03 실행·검증](D03_DEV_TEAM_RULES.md) · [D01 B](../../../AGENTS.md) · [D02 A](../../../CLAUDE.md) · [STATUS](../plan/STATUS.md)

| 담당 | 지금 실행할 작업 | 다음 작업·해제 조건 |
|---|---|---|
| Claude A ([HANDOFF_A](HANDOFF_A.md)) | **RF-001 B `b994a133` exact-SHA read-only peer 최우선:** `_strategist_risk_tone`·`_strategist_monitor_guidance`의 use-time facade/monkeypatch, risk_tone→risk_mode, blank/exception 경계 normal/-O. B 기존 path inventory FAIL과 신규 후보 회귀 분리. | RF-019 미완료 owner 실제 코드 작업. A RF-013 원복 `e7471a2e`는 B peer 대기; A 2863 PASS 재실행 금지. |
| Codex B ([HANDOFF_B](HANDOFF_B.md)) | **RF-013 A `e7471a2e` exact-SHA read-only peer 최우선:** 원본 RF-074/p171 두 FAIL node normal/-O 및 삭제 모듈 잔존 import 확인. 56경로 원복이 기존 승인 코드에 미친 영향 분리. | RF-001 `b994a133` 후보 frozen path-set 차단은 integration 기준과 동일 검사로 분리; 자기 RF-001 다음 owner-local 구현 계속. 32 위험 launcher 실행 금지. |
| 지팀장 | **신규 소스 확인:** A `e7471a2e` 56경로 원복, 자체 normal/-O 각 2863 PASS/4 SKIP; B `b994a133` 2 Python owner 함수 분리, focused normal/-O 각 3 PASS. GitHub commit diff 직접 확인. 둘 다 peer NOT_RUN, 통합 NOT_RUN. | RF-013 회귀 FIX_CANDIDATE / PEER=B, RF-001 FIX_CANDIDATE / PEER=A; 독립 peer 후 최소 owner 변경만 선별 통합 및 통합 SHA normal/-O. 통합 전 DONE 금지. |

**기록 위치:** RF = 개별 결정·실패·검증·차단·재개 조건. HANDOFF_A/B = 이번 실행의 신규 코드 SHA·명령·결과. STATUS = RF 집계. CURRENT = 담당·우선순위·링크만. 기존 증거는 재사용한다.

**런검증:** [별도 CURRENT](../../runtime/validation/CURRENT.md) · [D04](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md) · [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32). 코드 수정·RF 판정·통합 권한 없음.
