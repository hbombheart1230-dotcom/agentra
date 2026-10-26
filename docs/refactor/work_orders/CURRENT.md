# Agentra P1.5 — CURRENT (대시보드)

정본: [D00](../../ENGINEERING_DELIVERY_POLICY.md) · [D03](D03_DEV_TEAM_RULES.md) · [D01](../../../AGENTS.md) · [D02](../../../CLAUDE.md) · [STATUS](../plan/STATUS.md)

| 담당 | RF | 현재 상태 | 다음 행동 · 상세 정본 |
|---|---|---|---|
| A Claude | RF-001 peer → RF-018/019/017 | owner `e7471a2e` (NO_CHANGE); RF-018 KEEP_SCOPED | 최초 격리 조합 `cdc3599f` peer; 이후 [RF-018](../plan/verification/claude/RF-018.md) · [HANDOFF_A](HANDOFF_A.md) |
| B Codex | RF-001 검증 → RF-070 → RF-066 | 후보 `b994a133`; 격리 734×2 PASS; RF-070 85/142 | 누락 `test_operator_ui.py` normal/-O·patchnotes → [RF-001](../plan/verification/codex/RF-001.md) · [RF-070](../plan/verification/codex/RF-070.md) · [RF-066](../plan/verification/codex/RF-066.md) |
| 지팀장 | RF 판정·선별 통합 | RF-001 ADMIT_CANDIDATE/NOT_INTEGRATED; RF-066 HOLD scoped | 신규 격리 peer·UI 테스트 수용 후 선별 통합/통합 SHA 검증 · [STATUS](../plan/STATUS.md) |
| PC 런검증팀 | 별도 검증 | D04 권한 경계 | [runtime CURRENT](../../runtime/validation/CURRENT.md) |

큐: pending **71** · verification **14** · rework **0** · done **8** (마지막 확인 집계; 최신 STATUS 우선).
