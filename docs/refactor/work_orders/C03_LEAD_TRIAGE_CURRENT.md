# C03 — 지팀장① | RF 판정·A/B 배정 보드

> 진입점 **C03 + [D00](D00_ENGINEERING_DELIVERY_POLICY.md)**. `CURRENT.md`는 폐기된 구 진입점. **이 파일은 실행할 RF 링크만 제시한다.** RF별 세부 지시/검증 목록 재작성 금지.

## 지금 하는 일

| 우선 | 처리 대상 | 이 회차 책임 |
|---|---|---|
| 1 | [A HANDOFF](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-a-reporter-pure-20261021/docs/refactor/work_orders/HANDOFF_A.md) / [B HANDOFF](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-b-operator-structure-20261022/docs/refactor/work_orders/HANDOFF_B.md) | 신규 SOURCE/독립 peer 결과를 **해당 RF 원본 C1~C5에 대조** |
| 2 | B Owner → A Peer: [RF-063](../plan/queue/02_DEVELOPING/CODEX_B/RF-063.md), [RF-065](../plan/queue/02_DEVELOPING/CODEX_B/RF-065.md), [RF-067](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-067.md), [RF-069](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-069.md) | 첫 미충족 체크를 **[C01](C01_CODEX_CURRENT.md)·[C02](C02_CLAUDE_CURRENT.md)**에 RF 링크와 담당만 배정 |
| 3 | A Owner → B Peer: [RF-014](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-014.md), [RF-015](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-015.md), [RF-016](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-016.md), [RF-028](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-028.md), [RF-029](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-029.md), [RF-031](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-031.md), [RF-032](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-032.md), [RF-033](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-033.md), [RF-034](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-034.md), [RF-050](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-050.md) | 기존 독립 증거 재사용, **원본 실제 남은 체크만** 배정 |
| 4 | [STATUS 실물 큐](../plan/STATUS.md) / [LEAD 큐](../plan/queue/04_LEAD_ACCEPTANCE/) | 유효한 C1~C5·반대 peer full PASS 후보를 **C05에 제안** |
| 병행 P0 | [RunLab #32 OPEN](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md) | 신규 사실만 접수·owner 후보 매핑; 보호 실행/원인 단정 금지 |

## 절대 운영 루프

1. 신규 HANDOFF → **실제 RF 원본 `## DONE 체크`** → SOURCE SHA/원래 범위/기존 증거 순으로 확인한다.
2. 필요한 경우에만 C01/C02에 `RF 링크 | 미충족 C번호 | Owner→Peer | 부족 사유 1줄 | 다음 담당` **한 줄** 추가한다. **RF 내용 복붙·독립 재테스트 전수 지시 금지.**
3. 한 RF 차단 시 다음 안전 RF로 넘어가며, A/B가 한 건 끝내고 중단하지 않도록 다음 READY 링크를 유지한다.
4. C1~C5 전체 증거가 충족되면 **C05에 근거만 인계**한다. C03은 RF 체크·상태·STATUS를 고치지 않고 C04 소스를 사전 통합하지 않는다.

**한눈에 보는 최신 상태:** [STATUS](../plan/STATUS.md)가 유일한 수치 정본. 마지막 확인 93 RF: PENDING 51 / DEV 9 / PEER 14 / **LEAD 3** / DONE 16 / REWORK 0. LEAD RF-052/046/047은 **이미 C05가 실물 이동**했으므로 구 'LEAD 0/LEAD_READY 제안' 문구를 다시 쓰지 않는다. 보고: `새로 해제된 체크 수 | 배정 RF 링크 | C05 인계 RF | 실제 BLOCKED 원인`.
