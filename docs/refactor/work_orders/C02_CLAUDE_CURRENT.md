# C02 — Claude A | 현재 실행 링크

> **절대 규칙: 한 RF/한 체크/한 HANDOFF로 예약 종료 금지. 가능한 RF를 연속 수행.** 정본 [D00](D00_ENGINEERING_DELIVERY_POLICY.md) · [전체 STATUS](../plan/STATUS.md) · [C03 배정](C03_LEAD_TRIAGE_CURRENT.md). `CURRENT.md` 사용 금지. 브랜치 `work/p15-a-reporter-pure-20261021`.

## 🔴 지금 바로 수행 — RF 원본으로 이동

| 순번 | RF 원본 바로가기 | A 역할 | 지금 확인할 원래 미완료 조건 |
|---:|---|---|---|
| 1 | [RF-015](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-015.md) | Owner | **C2**, Monitor State/event/consumer 원래 미충족 확인. 제출된 BASE 11 FAIL은 재실행 금지 |
| 2 | [RF-031](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-031.md) | Owner | **C2**, partial-OSError downstream recovery 근거를 B peer에 전달 |
| 3 | [RF-067](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CODEX_B/RF-067.md) | Peer | **C4**, B가 지정한 미검증 안전 target 한정 독립 fake. 실 preflight/UEF NOT_RUN |
| 4 | [RF-014](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-014.md) | Owner | run148 **20-owner C1 ACTION 제출됨**. 원본 C2/C3 잔여 검토 및 B C4 응답만 |
| 5 | [RF-050](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-050.md) | Owner | 이미 제출한 caller/cache 계약 재사용; B C4 신규 결함·요청에만 응답 |
| 6 | [RF-063](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/02_DEVELOPING/CODEX_B/RF-063.md) · [RF-065](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/02_DEVELOPING/CODEX_B/RF-065.md) | Peer | B 신규 Owner SOURCE/증거 도착 시 미검증 원래 범위만 독립 확인 |

위 표는 **우선순위/링크**일 뿐 새 테스트 명세가 아니다. **RF의 `## DONE 체크`와 최신 검증 이력이 작업 지시 원본**이다. 기존 SOURCE SHA/독립 peer 수용 근거를 재사용한다.

## ▶ 다음 RF — 중단 없이 순환

| RF 원본 링크 | A 역할 · 진행 |
|---|---|
| [RF-016](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-016.md) · [RF-028](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-028.md) · [RF-029](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-029.md) | Owner · 원래 C1~C3 잔여와 B peer 근거 대응 |
| [RF-032](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-032.md) · [RF-033](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-033.md) · [RF-034](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-034.md) | Owner · 원본 안전/효과 경계 준수 |
| [RF-051](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/02_DEVELOPING/CLAUDE_A/RF-051.md) · [RF-054](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/02_DEVELOPING/CLAUDE_A/RF-054.md) · [RF-058](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/02_DEVELOPING/CLAUDE_A/RF-058.md) | Owner · 독립 진행 가능한 안전한 일반 RF |
| [RF-035](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/01_PENDING/CLAUDE_A/RF-035.md) | **PENDING/일부 보호 HOLD**, RF 원본 체크와 승인 가능 범위로만 CLAIM |
| [RF-069](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CODEX_B/RF-069.md) | **SAFETY_BLOCKED** · historical UEF5 승인 전 NOT_RUN |
| [RunLab #32 원본](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md) | P0 신규 정보만 REPORT read-only/격리 fake 조사. 운영·보호 코드 변경 금지 |

## 무조건 끝까지 수행하는 루프

**RF 링크 열기 → 그 RF 원본 `DONE 체크`의 미완료 확인 → 수행/독립 검증 → 자기 [HANDOFF_A](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-a-reporter-pure-20261021/docs/refactor/work_orders/HANDOFF_A.md) 증분 기록·커밋/푸시 → 다음 READY RF.** 여기의 문구를 RF에 복제하지 않는다.

- **정지 금지:** 첫 작업 종료, 첫 커밋, 한 건 PASS, 첫 HANDOFF, peer/지팀장 응답 대기만으로 세션을 종료하지 않는다. 한 RF가 BLOCKED면 원본에 근거가 있는 안전 사유를 HANDOFF에 적고 **바로 다른 RF**를 수행한다. 독립 실행 가능한 READY RF가 0개거나 실제 실행 한도에 닿을 때만 종료할 수 있다. 예약 회차 밖에서 자동 지속된다고 주장하지 않는다.
- **진실성:** Owner는 자기 A 브랜치에 소스/테스트 커밋·푸시. Peer는 상대 B 정확 SHA 독립 검증. `SCOPED_PASS`를 전체 `PASS`로 바꾸지 않고 기존 PASS 중복 재실행 금지. **원본 RF 체크·물리 이동·STATUS는 C05만 수정**한다. RF-043/053 DONE, RF-052/046/047은 이미 LEAD이므로 기존 peer 재실행 금지.
- **보고 한 줄:** `RF 링크 | 원래 C번호 | SOURCE SHA | 증거 PASS/PARTIAL/NOT_RUN | 남은 C번호 | 해제 담당 | NEXT RF 링크`. [Issue #11](https://github.com/hbombheart1230-dotcom/agentra/issues/11)는 마일스톤 기록만. [D00 안전 규칙](D00_ENGINEERING_DELIVERY_POLICY.md)은 절대 완화 금지.

**이번 회차가 끝날 때 필수 숫자:** `실제 처리 RF 수 / 완료 체크 증거 수 / 코드 변경 RF 수 / peer 검증 수 / 다음 READY RF`. 문서/댓글 개수를 실적이라 부르지 않는다.
