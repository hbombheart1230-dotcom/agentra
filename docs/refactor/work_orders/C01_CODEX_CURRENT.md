# C01 — Codex B 현재 작업

**목표:** A 소유 RF의 남은 peer 게이트를 해소하고 B 소유 RF를 계속 개발한다. **한 건 뒤 다음 건.**
브랜치: `work/p15-b-operator-structure-20261022` · 고정 규칙: `D00_ENGINEERING_DELIVERY_POLICY.md` · 증거: B 브랜치 `HANDOFF_B.md`

## 지금 할 일 — 기존 증거 재사용, 아래 최초 미충족 경계만

| 순서 | RF | 다음 실행 |
|---|---|---|
| 1 | **031** | downstream JSON-only 복구 scoped 완료 증거 재사용; 실제 caller 최종 State·재시도 경계/재현 명령만 확인 |
| 2 | 050 / 016 / 029 | cache reload·facade 예외 기존 증거 재사용, 남은 전체 소비자·nested State 예외 / 외부 truth-root 실패 |
| 3 | 033 / 014 / 028 | partial JSON·Top1·in-process writer scoped peer 재사용, 남은 실제 producer/Graph/외부 rich schema 소비자 |
| 4 | 034 / 015 / 032 | valid sources scoped peer 재사용, casebook→Scanner 전체 소비자 / 역사 BASE FAIL·B-only 소비자 / validation_id 신뢰 경계 |
| 5 | **063 / 065 / 067** | B 원개발 즉시 보완. RF-063 `run_m23_closeout_check`는 A 재현 SHA와 B 미재현 SHA 대조→결함이면 자기 브랜치에서 바로 수정·테스트→A peer 인계 |

## 위 목록 다음

| 우선 | 실제 작업 |
|---|---|
| 1 | 자기 `02_DEVELOPING/CODEX_B` 미완료 구현 |
| 2 | 자기 `06_REWORK/CODEX_B` 결함 수정 |
| 3 | `03_PEER_REVIEW/CODEX_B` 신규 A 소유 peer |
| 4 | 자기 `01_PENDING/CODEX_B` 다음 RF 개발 |

**일반 RF는 사용자·지팀장 개별 승인 대기 없이** 자기 브랜치에서 **구현→테스트→커밋·푸시→HANDOFF·#12→다음 RF**를 반복한다. 자기 큐 소진 시 양쪽 HEAD·HANDOFF·Issue를 확인하여 중복 없는 `01_PENDING/UNASSIGNED` 일반 RF를 **자율 CLAIM하고 즉시 개발**한다. 지팀장은 다음 회차 물리 Owner를 동기화한다. 보호 RF-069는 실행 금지.
