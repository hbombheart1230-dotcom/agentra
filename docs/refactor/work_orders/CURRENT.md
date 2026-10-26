# Agentra P1.5 — CURRENT (지팀장 실행 지시판)

**정본 바로가기:** [D00 안전·권한](../../ENGINEERING_DELIVERY_POLICY.md) · [D01 Codex B](../../../AGENTS.md) · [D02 Claude A](../../../CLAUDE.md) · [D03 개발·검증](D03_DEV_TEAM_RULES.md) · [D04 런검증](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md) · [STATUS/전체 RF 큐](../plan/STATUS.md) · [RF 소유 범위](../plan/FILE_COVERAGE_63182ab2.csv)

**공통 실행:** 확인 → 가능한 owner FIX/KEEP·실제 검증 → 다음 RF. 검사·ACK·HANDOFF만으로 종료 금지. 신규 SHA·REWORK 없음은 자기 RF 중단 사유가 아님. 위험 **명령만** HOLD하고 안전한 다른 작업 계속. 기존 동일 SHA normal/-O·peer 증거 재사용. 미착수 시 실제 차단/시간/환경과 재개 명령 기록. D00 안전·승인 경계 준수.

**POLICY_REREAD_REQUIRED (임시, 지팀장 회수):** A/B는 [D03](D03_DEV_TEAM_RULES.md) 변경 blob `471d7ab3bae33cdaa369ed80fb354ec5717c632c`를 전문 재독하고 HANDOFF에 원격 SHA·읽은 SHA·실제 적용 및 연속 RF 착수 기록. **A PENDING / B PENDING**. 변경 핵심: CURRENT를 회차별 구체 실행 지시판으로 사용, 확인 뒤 실제 조치와 다음 RF를 진행. 지팀장이 양쪽 수신·적용 확인 후 이 항목 직접 삭제. 이전 D03 blob `89826e10`의 미확인 수신 요구도 최신 SHA 수신으로 함께 해소.

## A Claude — Reporter · [HANDOFF_A (작업 브랜치)](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-a-reporter-pure-20261021/docs/refactor/work_orders/HANDOFF_A.md)
1. **[RF-013](../plan/verification/claude/RF-013.md) — 즉시 진행:** 67 owner KEEP, coverage 92%. 잔여 `strategy_read_model_bodies_01`(71%), `pipeline_trace_bodies_01`(81%), `post_exit_recap_bodies_01`(81%), `entry_blocker_bodies_01`(84%)의 **실제 미검증 소비자/폴백 위험**을 격리 fake normal/-O로 검증. 결함 확인 시 owner 범위 최소 FIX→검증. 단순 숫자 채우기·실제 `KiwoomOrderFillReader.from_env` 호출·미승인 9+4 경로·오라클 수정 금지.
2. **[RF-019](../plan/pending/RF-019.md) → [RF-017](../plan/pending/RF-017.md) → [RF-018](../plan/verification/claude/RF-018.md):** 각 RF의 기존 증거를 재사용해 남은 인수조건·소비자 위험을 처리. RF-018은 JSON 실패 fallback 잠재 3건을 동일 BASE 입력으로 재현하고 공개 소비자·안전 영향 판별; 승인 없는 안전 계약 FIX 금지. RF-019·RF-017은 현재 pending 큐에 있으며, 기존 증거가 있더라도 지팀장 판정 전 DONE으로 간주하지 않는다.
3. **[RF-001](../plan/verification/codex/RF-001.md) peer:** 격리 `cdc3599f` 독립 734×2 PASS 수용 완료. 동일 조합 재검증 금지; 신규 코드 SHA/새 위험이 있을 때만 peer.

## B Codex — Operator/Monitor · [HANDOFF_B (작업 브랜치)](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-b-operator-structure-20261022/docs/refactor/work_orders/HANDOFF_B.md)
1. **[RF-001](../plan/verification/codex/RF-001.md) — 즉시 진행:** `cdc3599f` 격리 후보에서 `tests/test_operator_ui.py` **normal/-O**를 fastapi 구비 환경에서 실행하고 UI patchnotes JSON/MD 확인. 결함 시 승인된 **두 owner hunk만** 최소 FIX→검증. 기존 B/A 734×2 및 17 differential PASS 재사용; 전체 B branch 혼합 통합 금지.
2. **[RF-070](../plan/verification/codex/RF-070.md):** 잔여 기타 25개 구현의 소비자·IO·side effect·소유권을 정적 분류한 후 안전한 격리 mock 경계 실제 검증/필요한 owner FIX. 위험 launcher 32개 운영 실행 금지; 기존 85/142 PASS 재사용.
3. **[RF-066](../plan/verification/codex/RF-066.md):** `demo_m7_dry_run_pipeline.py`의 실제 `main()`·운영 파일 쓰기·주문 접근만 HOLD. 임시 경로 + fake OrderClient로 `build_demo_catalog`/소비자 경계를 안전하게 normal/-O 검증; 격리 불확실 시 그 명령만 NOT_RUN, 다른 16 owner로 즉시 진행. 단일 파일 BLOCKED로 회차 종료 금지.

## 지팀장 — 매 예약 회차 직접 회수·판정
1. A/B 최신 코드 SHA·HANDOFF·실제 실행 결과 확인 후 **미착수 사유를 잔여 RF와 대조**. `NO_EXECUTABLE_OWNER`·`다음 회차` 자동 승인 금지; 실제 조치 없는 보고는 진척 0.
2. **[RF-001](../plan/verification/codex/RF-001.md):** A 격리 peer PASS 재사용. B UI normal/-O·patchnotes·33 owner 계약을 수용할 수 있으면 두 owner hunk만 선별 통합 → **반영 exact integration SHA** 필수 normal/-O 배정·검증 → DONE 판정. 미충족 게이트는 명시하고 다른 RF 판정/통합 계속.
3. **[RF-013](../plan/verification/claude/RF-013.md)·[RF-018](../plan/verification/claude/RF-018.md)·[RF-070](../plan/verification/codex/RF-070.md)·[RF-066](../plan/verification/codex/RF-066.md):** 신규 증거를 KEEP/FIX/PEER/INTEGRATE/BLOCKED로 판정하고 해결된 RF는 물리 큐·STATUS 갱신. 안전 HOLD는 해당 명령에만 적용.
4. 정책 D03 `471d7ab3` A/B 실제 재독·적용 확인 후 위 임시 정책 항목 **직접 회수**. 실행 끝에는 이 CURRENT의 완료 항목을 제거하고 다음 구체 작업으로 교체.

**현재 큐 (마지막 확인):** pending **71** · verification **14** · rework **0** · DONE **8**. 최신 [STATUS](../plan/STATUS.md) 우선. **이번 문서 변경 자체는 RF 진척·테스트 PASS·통합 DONE이 아님.**
