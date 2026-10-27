# C01 — Codex B | 실행 보드

> **이번 예약은 1개 RF만 하고 끝나는 작업이 아니다.** 진입점 C01 → [D00](D00_ENGINEERING_DELIVERY_POLICY.md). 구 `CURRENT.md` 사용 금지. 개발 브랜치: `work/p15-b-operator-structure-20261022`.

## 지금 할 일 (상세 지시를 여기에 복사하지 말 것)

| 순서 | 담당 | 바로 열 파일 / 실제 다음 행동 |
|---|---|---|
| 1 | B Owner | [RF-063](../plan/queue/02_DEVELOPING/CODEX_B/RF-063.md), [RF-065](../plan/queue/02_DEVELOPING/CODEX_B/RF-065.md) — **원본의 남은 C1~C5** |
| 2 | B Peer | [RF-015](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-015.md), [RF-050](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-050.md), [RF-031](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-031.md) — **원본 미충족 체크에 대한 독립 검증** |
| 3 | B Peer | [RF-014](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-014.md), [RF-016](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-016.md), [RF-028](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-028.md), [RF-029](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-029.md), [RF-032](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-032.md), [RF-033](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-033.md), [RF-034](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-034.md) |
| 4 | B 후속 | [STATUS/실물 큐](../plan/STATUS.md)에서 B 원개발 RF-066/070/071 및 독립 처리 가능한 일반 RF 선택 |
| 병행 P0 | 조사만 | [RunLab #32 OPEN](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md) ORDER/GUARD **새로운 사실만** read-only/격리 fake, 보호 소스 무승인 변경 금지 |

## 절대 실행 규칙 — 매 예약 끝까지 반복

1. 위 **RF 링크를 직접 열어 `## DONE 체크` C1~C5의 빈칸과 RF 자체의 최신 기록**을 확인한다. C01/C03의 과거 설명으로 실제 체크를 대신하지 않는다. 이미 같은 SOURCE SHA·원래 범위로 검증된 항목은 재실행하지 않는다.
2. 안전하게 수행 가능한 **첫 미충족 체크를 실제 구현·검증**한다. Owner라면 자기 브랜치에 필요한 소스/테스트만 수정하고 커밋·푸시한다. Peer라면 반대 팀 정확 SHA를 독립 검증한다. 자가 peer 금지, PASS 과장 금지.
3. [HANDOFF_B](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-b-operator-structure-20261022/docs/refactor/work_orders/HANDOFF_B.md)에 **RF 링크 | C번호 | SOURCE SHA | 결과·증거 | 남은 체크 | 다음 담당**만 증분 기록하고 푸시한다. 원본 RF 체크·물리 이동·STATUS는 **C05만 수정**한다.
4. **바로 다음 RF로 넘어가 1→2→3을 반복한다.** 첫 RF 완료, 일부 PASS, 핸드오프 한 번, 다른 팀/지팀장 응답 대기, 문서 커밋 1회는 **종료 사유가 아니다**. 한 RF가 BLOCKED면 그 RF만 표기하고 다음 안전 RF를 처리한다. 서로 독립한 작업은 한 세션에서 가능한 만큼 계속한다.
5. 종료는 실제 실행/컨텍스트 한도 도달 또는 모든 READY RF가 증거 기반 BLOCKED/없음일 때만. 종료 보고: `이번 회차 실제 수행 RF 수 | 해제한 C | 새 코드/peer 증거 | 남은 READY 수 | 다음 RF`. **프로세스가 종료되면 문서만으로 백그라운드 지속 실행은 보장되지 않는다.**

**완료/중복 금지:** RF-043/053은 DONE. RF-052/046/047의 기존 독립 peer는 인수됨(현재 [LEAD 큐](../plan/queue/04_LEAD_ACCEPTANCE/)); 재실행 금지. [Issue #12](https://github.com/hbombheart1230-dotcom/agentra/issues/12)는 마일스톤 보고만, 최신 세부 증거는 HANDOFF_B. 안전·쓰기권한·C1~C7 기준은 [D00](D00_ENGINEERING_DELIVERY_POLICY.md) 그대로 따른다.
