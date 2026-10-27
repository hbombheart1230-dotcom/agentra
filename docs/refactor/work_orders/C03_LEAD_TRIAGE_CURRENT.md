# C03 — 지팀장① | 오늘 배정·수용 현황

> **한눈에 보는 RF 라우터.** [D00 원칙](D00_ENGINEERING_DELIVERY_POLICY.md) · [전체 STATUS](../plan/STATUS.md). 구 `CURRENT.md` 사용 금지. **검증 명세는 C03이 쓰지 않는다. 링크의 RF 원본 `## DONE 체크`가 정본이다.**

## 🔴 지금 처리할 RF

| 순번 | 실제 RF 원본 링크 | 다음 행동 / 담당 |
|---:|---|---|
| 1 | [RF-014](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-014.md) | A C1 20-owner 제출 → **B C4 정확 SOURCE·기존 peer 범위 대조** |
| 2 | [RF-031](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-031.md) | **A C2 owner 증거 → B 첫 미검증 recovery peer** |
| 3 | [RF-050](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-050.md) | B C4 UI caller/failure 원래 필수 범위 peer |
| 4 | [RF-015](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-015.md) | A C2 Monitor State/event/consumer; 기존 BASE 11 FAIL 재사용 |
| 5 | [RF-065](../plan/queue/02_DEVELOPING/CODEX_B/RF-065.md) | **B C1** 연구 CLI 잔여 안전 검증; 기존 scoped 재실행 금지 |
| 6 | [RF-063](../plan/queue/02_DEVELOPING/CODEX_B/RF-063.md) | B C1 잔여 owner 근거 |
| 7 | [RF-067](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-067.md) | **A C4** B가 지정한 안전한 미검증 target만 독립 peer |
| 8 | [RF-069](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-069.md) | 역사 UEF5 snapshot **SAFETY_BLOCKED/NOT_RUN**, 다른 RF 진행 |

**나머지 우선 RF:** [RF-016](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-016.md) · [RF-028](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-028.md) · [RF-029](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-029.md) · [RF-032](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-032.md) · [RF-033](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-033.md) · [RF-034](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-034.md). 실제 남은 C 번호·최신 증거는 **각 RF 원본**에서 읽는다.

## ▶ 다음 인계

| 바로가기 | 상태 · C03이 할 일 |
|---|---|
| [C01 B 작업판](C01_CODEX_CURRENT.md) / [C02 A 작업판](C02_CLAUDE_CURRENT.md) | **원본 RF 링크 + 첫 부족 C번호 + 해제 담당**만 최신화. 한 건 후 멈추지 않도록 다음 READY 유지 |
| [A HANDOFF](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-a-reporter-pure-20261021/docs/refactor/work_orders/HANDOFF_A.md) / [B HANDOFF](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-b-operator-structure-20261022/docs/refactor/work_orders/HANDOFF_B.md) | 신규 delta만 대조. 같은 SHA/범위 검증 재실행 금지 |
| [C05 종결판](C05_LEAD_CLOSEOUT_CURRENT.md) / [C04 통합판](C04_LEAD_INTEGRATION_CURRENT.md) | C1~C5 **전체** + 정확 SOURCE·반대 full peer PASS일 때만 C05에 LEAD 제안 |
| [RF-046](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-046.md) · [RF-047](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-047.md) · [RF-052](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-052.md) | **이미 LEAD 3건**. C03 재승인/사전 통합 금지, C04 C6 → C05 C7 |
| [RunLab #32 OPEN](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md) | 적용 SHA UNKNOWN: 새 사실만 분류, 운영/안전 변경 승인 없이 수행 금지 |

## 절대 운영 규칙

- **각 RF 원본의 미체크 C1~C5·최신 검사 기록을 직접 읽고 최초 부족 한 항목만 배정.** 이미 충분한 SOURCE·peer 근거면 C05로 넘긴다. 이 문서에 RF별 기술 지시/근거 표를 복사하지 않는다.
- C01/C02의 **현재 RF 링크/담당 행을 갱신**하되 누적 `C03 delta` 섹션을 끝없이 덧붙이지 않는다. 이미 처리한 배정은 교체/정리한다. 장황한 검증/테스트 세부는 RF와 HANDOFF에 남긴다.
- 막힌 RF 하나가 A/B 전체 세션을 차단하지 않도록 다음 안전 READY를 연결한다. 작업자의 별도 승인 기다림 금지(보호 작업은 별도 명시 승인).
- C03은 C1~C5 근거 **권고/배정만**. 체크·실물 이동·STATUS는 C05, source 통합/CI는 C04 단독. 보고: `RF 링크 | 최초 부족 C | 담당 | C05 인계 여부 | 다음 링크`.

**현재 확인 스냅샷:** 93 RF = PENDING 51 / DEV 9 / PEER 14 / LEAD 3 / DONE 16 / REWORK 0. 우선 14건은 DEV 2 + PEER 12, 신규 LEAD 아님. 최신 [STATUS](../plan/STATUS.md)와 **실물 RF**가 수치 정본이다.
