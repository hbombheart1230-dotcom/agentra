# C01 — Codex B 현재 작업

**목표:** A 소유 RF의 남은 peer 게이트를 해소하고 B 소유 RF를 계속 개발한다. **한 건 뒤 다음 건.**
브랜치: `work/p15-b-operator-structure-20261022` · 고정 규칙: `D00_ENGINEERING_DELIVERY_POLICY.md` · 증거: B 브랜치 `HANDOFF_B.md`

## 지금 할 일 — 기존 증거 재사용, 아래 최초 미충족 경계만

| 순서 | RF | 다음 실행 |
|---|---|---|
| 1 | **031** | Reporter 부분 실패 뒤 downstream State·재시도/복구 소비자, 재현 가능한 temp 하네스·exit 확보 (`pytest` 부재는 ENV) |
| 2 | 050 / 016 / 029 | model cache 산출·예외 / facade 예외 projection / 외부 truth-root read·실패 |
| 3 | 033 / 014 / 028 | provider→storage 실패 / runtime Top1→NOOP / rich schema writer |
| 4 | 034 / 015 / 032 | casebook→Scanner / 역사 BASE FAIL·B-only 실제 소비자 / validation_id·Stage2 부분 실패 |
| 5 | **063 / 065 / 067** | B 원개발 결함 및 A의 새 peer 요청 반영. RF-063 `run_m23_closeout_check` NameError는 기존 BASE 원인 분리 후 수정·테스트 |

## 위 목록 다음

| 우선 | 실제 작업 |
|---|---|
| 1 | 자기 `02_DEVELOPING/CODEX_B` 미완료 구현 |
| 2 | 자기 `06_REWORK/CODEX_B` 결함 수정 |
| 3 | `03_PEER_REVIEW/CODEX_B` 신규 A 소유 peer |
| 4 | 자기 `01_PENDING/CODEX_B` 다음 RF 개발 |

자기 브랜치에서 **구현→테스트→커밋·푸시→HANDOFF→다음 RF**를 반복한다. 해당 작업이 대기·소진되면 큐로 즉시 이동한다. `UNASSIGNED`는 지팀장 배정 요청. RF-069 보호 실행 금지.
