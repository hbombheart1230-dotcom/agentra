# Agentra P1.5 — CURRENT (지팀장 실행 지시판)

**정본 바로가기:** [D00 안전·권한](../../ENGINEERING_DELIVERY_POLICY.md) · [D01 Codex B](../../../AGENTS.md) · [D02 Claude A](../../../CLAUDE.md) · [D03 개발·검증](D03_DEV_TEAM_RULES.md) · [D04 런검증](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md) · [STATUS/전체 RF 큐](../plan/STATUS.md) · [RF 소유 범위](../plan/FILE_COVERAGE_63182ab2.csv)

**공통 실행:** 확인 → 가능한 owner FIX/KEEP·실제 검증 → 다음 RF. 검사·ACK·HANDOFF만으로 종료 금지. 신규 SHA·REWORK 없음은 자기 RF 중단 사유가 아님. 위험 **명령만** HOLD하고 안전한 다른 작업 계속. 기존 동일 SHA normal/-O·peer 증거 재사용. 미착수 시 실제 차단/시간/환경과 재개 명령 기록. D00 안전·승인 경계 준수.

**POLICY_REREAD_REQUIRED (임시, 지팀장 회수):** A/B는 [D03](D03_DEV_TEAM_RULES.md) 변경 blob `471d7ab3bae33cdaa369ed80fb354ec5717c632c`를 전문 재독하고 HANDOFF에 원격 SHA·읽은 SHA·실제 적용 및 연속 RF 착수 기록. **A 수신·적용 확인 (RUN `2026-10-26T0448Z-claude-a-sched-96`) / B PENDING**. 변경 핵심: CURRENT를 회차별 구체 실행 지시판으로 사용, 확인 뒤 실제 조치와 다음 RF를 진행. 지팀장이 양쪽 수신·적용 확인 후 이 항목 직접 삭제. 이전 D03 blob `89826e10`의 미확인 수신 요구도 최신 SHA 수신으로 함께 해소.

## A Claude — Reporter · [HANDOFF_A (작업 브랜치)](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-a-reporter-pure-20261021/docs/refactor/work_orders/HANDOFF_A.md)
1. **[RF-019](../plan/pending/RF-019.md) — 즉시 실행:** 29 owner 중 잔여 21개 State·IO·소비자·효과 인수조건을 기존 증거 재사용해 실제 판정. 새 위험이 없으면 KEEP 근거를 파일별 확정하고 다음 RF 착수. 소스 수정이 필요할 때만 독점 owner 최소 FIX→B 신규 SHA peer.
2. **[RF-017](../plan/pending/RF-017.md) → [RF-018](../plan/verification/claude/RF-018.md):** RF-017 기존 5개 Commander owner 공개 import·lazy cache·projection/효과 미검증 경계를 normal/-O 표적 처리. RF-018 A RUN `2026-10-26T0448Z-claude-a-sched-96` fallback 3건 BASE 동일: (1) enum 부분일치 재현, (2) scanner_priority 필터 우회 미재현(괄호 오염은 재현), (3) multiline truncation 재현. **BASELINE_EXISTING / KEEP_SCOPED / NOT_DONE**; 안전 계약 무승인 수정 금지, 미검증 소비자만 처리.
3. **[RF-013](../plan/verification/claude/RF-013.md) — 신규 증거 수용, 재실행 금지:** 같은 A RUN에서 잔여 4 owner BASE↔integration normal/-O byte-identical·exit 0, 파일별 95/95/100/100% 보고. 67 owner KEEP, 신규 회귀 0, source `e7471a2e` 유지. **KEEP_SCOPED / NOT_DONE**(전체 소비자·State/IO·효과 및 exact integration SHA 게이트 별도). 신규 위험 없으면 같은 하네스 반복하지 말고 RF-019/017 진행.
4. **[RF-001](../plan/verification/codex/RF-001.md) peer:** 격리 `cdc3599f` 734×2·17 differential 기존 PASS 재사용; 새 B source SHA·위험에 한해 peer.

## B Codex — Operator/Monitor · [HANDOFF_B (작업 브랜치)](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-b-operator-structure-20261022/docs/refactor/work_orders/HANDOFF_B.md)
**B 연속 실행 판정:** 최신 RUN `B-20261026T0400Z`는 RF-001 UI 53×2 PASS만 보고하고 후속 RF 실제 착수·`NOT_STARTED_REASON` 관측 근거가 없음. **CONTINUATION_UNVERIFIED / 코드 진척 0 / 정상 종료 미인정**. D03 §2(14~15행) 기존 계약 적용. HANDOFF-only 보고 반복 금지; 현재 실행 가능한 자기 RF를 순서대로 실제 착수하고 명령·exit·owner 변경 또는 구체 차단을 남길 것.
1. **[RF-001](../plan/verification/codex/RF-001.md) — 즉시 진행:** `cdc3599f` 격리 후보에서 `tests/test_operator_ui.py` normal/-O **각 53 PASS (B HEAD `479b3cc9`, RUN `B-20261026T0400Z`)** 보고 수용. 남은 UI patchnotes JSON/MD 및 33 owner 계약을 확인. 결함 시 승인된 **두 owner hunk만** 최소 FIX→검증. 기존 B/A 734×2 및 17 differential PASS 재사용; 전체 B branch 혼합 통합 금지.
2. **[RF-070](../plan/verification/codex/RF-070.md):** 잔여 기타 25개 구현의 소비자·IO·side effect·소유권을 정적 분류한 후 안전한 격리 mock 경계 실제 검증/필요한 owner FIX. 위험 launcher 32개 운영 실행 금지; 기존 85/142 PASS 재사용.
3. **[RF-066](../plan/verification/codex/RF-066.md):** `demo_m7_dry_run_pipeline.py`의 실제 `main()`·운영 파일 쓰기·주문 접근만 HOLD. 임시 경로 + fake OrderClient로 `build_demo_catalog`/소비자 경계를 안전하게 normal/-O 검증; 격리 불확실 시 그 명령만 NOT_RUN, 다른 16 owner로 즉시 진행. 단일 파일 BLOCKED로 회차 종료 금지.

## 지팀장 — 매 예약 회차 직접 회수·판정
1. A/B 최신 코드 SHA·HANDOFF·실제 실행 결과 확인 후 **미착수 사유를 잔여 RF와 대조**. `NO_EXECUTABLE_OWNER`·`다음 회차` 자동 승인 금지; 실제 조치 없는 보고는 진척 0.
2. **[RF-001](../plan/verification/codex/RF-001.md):** A 격리 peer PASS 재사용. B UI normal/-O·patchnotes·33 owner 계약을 수용할 수 있으면 두 owner hunk만 선별 통합 → **반영 exact integration SHA** 필수 normal/-O 배정·검증 → DONE 판정. 미충족 게이트는 명시하고 다른 RF 판정/통합 계속.
3. **[RF-013](../plan/verification/claude/RF-013.md)·[RF-018](../plan/verification/claude/RF-018.md)·[RF-070](../plan/verification/codex/RF-070.md)·[RF-066](../plan/verification/codex/RF-066.md):** 신규 증거를 KEEP/FIX/PEER/INTEGRATE/BLOCKED로 판정하고 해결된 RF는 물리 큐·STATUS 갱신. 안전 HOLD는 해당 명령에만 적용.
4. 정책 D03 `471d7ab3` **A 재독·연속 착수 확인 완료**, B 미확인. B의 정책 수신·연속 착수 증거 확인 후 임시 정책 항목 **직접 회수**. B의 `CONTINUATION_UNVERIFIED`는 다음 회차 실제 작업으로 해소 확인. 실행 끝에는 이 CURRENT의 완료 항목을 제거하고 다음 구체 작업으로 교체.

**현재 큐 (마지막 확인):** pending **71** · verification **14** · rework **0** · DONE **8**. 최신 [STATUS](../plan/STATUS.md) 우선. **이번 문서 변경 자체는 RF 진척·테스트 PASS·통합 DONE이 아님.**
