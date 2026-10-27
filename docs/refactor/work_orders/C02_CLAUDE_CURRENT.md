# C02 — Claude A | 현재 실행 링크

> **절대 규칙: 한 RF/한 체크/한 HANDOFF로 예약 종료 금지. 가능한 RF를 연속 수행.** 정본 [D00](D00_ENGINEERING_DELIVERY_POLICY.md) · [전체 STATUS](../plan/STATUS.md) · [C03 배정](C03_LEAD_TRIAGE_CURRENT.md). `CURRENT.md` 사용 금지. 브랜치 `work/p15-a-reporter-pure-20261021`.

## 🔴 지금 바로 수행 — RF 원본으로 이동

| 순번 | RF 원본 바로가기 | A 역할 | 지금 확인할 원래 미완료 조건 |
|---:|---|---|---|
| 1 | [RF-015](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-015.md) | Owner | **C1/C2 Owner run149 제출 완료**. B C4 원래 19-owner full peer 판단 대기; B-only Commander frozen FAIL을 Monitor 회귀로 보지 않음. run112/145/149 재실행 금지 |
| 2 | [RF-031](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-031.md) | Owner | **C1/C2 Owner run150 제출 완료**. B의 caller-State/partial-OSError scoped peer 수령; B가 지목한 최초 원래 C2 계약 누락에만 대응, 기존 fake 재실행 금지 |
| 3 | [RF-067](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CODEX_B/RF-067.md) | Peer | **C4**: 기존 A 2 root + run151 4 + run138e 4 + run138d 2 = **서로 다른 12/14 root scoped peer**. B가 12 root 정확 SHA·모드 매핑을 제출했고 **A run162가 보호 2 root 공개 import/argv/예외/exit fake-module 20/20 SCOPED_PASS 완료**. **A 다음 작업:** 기존 12개 scoped root + run162 2개 fake wrapper의 정확 SOURCE·모드·효과 경계를 14행 한 표로 합쳐 원래 RF-067 root-wrapper 전체 C4 PASS 가능 여부를 명시하거나 최초 미충족 원래 조건 1개를 지목해 C03/C05 인계. 보호 2개 실 target NOT_RUN/SAFETY_HOLD. 기존 12와 run162 재실행 금지; UEF/real preflight·Windows 운영 실호출 금지 |
| 4 | [RF-014](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-014.md) | Owner | run148 **20-owner C1 ACTION 제출됨**, B static/dynamic scoped 수령. 원래 C2/C3 Scanner consumer·ranking/reject/NOOP 중 최초 빠진 계약만 정리해 B full C4 요청 |
| 5 | [RF-050](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-050.md) | Owner | run146 8-owner caller/cache 지도 재사용. **C1 최종 KEEP/COMPAT/효과 ACTION**을 한 번 확정해 B C4에 인계; 기존 B fake 10/10 재실행 금지 |
| 6 | [RF-065](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/02_DEVELOPING/CODEX_B/RF-065.md) · [RF-063](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/02_DEVELOPING/CODEX_B/RF-063.md) | Peer | **RF-065 신규 B source `1641cfef`, `run_integrated_trade_validation.py@4119747f`**: 이전 default output-root 외부 8개 산출물에 대한 B 수정 후보. **A run161에서 정확 B `1641cfef`/blob `4119747f` 공개 CLI 7 argv × normal/`-O` = 14/14 temp-only fake SCOPED_PASS 완료**. 실제 downstream writer·broker·network·운영 보고서 NOT_RUN, 전체 RF C4 PASS 아님. 같은 범위 재실행 금지; B 54-owner C1 및 원래 C2/C3 남은 계약 대기. RF-063 기존 TEXT/JSON 4/4 peer 재실행 금지; 신규 B 근거만 확인 |

위 표는 **우선순위/링크**일 뿐 새 테스트 명세가 아니다. **RF의 `## DONE 체크`와 최신 검증 이력이 작업 지시 원본**이다. 기존 SOURCE SHA/독립 peer 수용 근거를 재사용한다.

## ▶ 다음 RF — 중단 없이 순환

| RF 원본 링크 | A 역할 · 진행 |
|---|---|
| [RF-016](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-016.md) · [RF-028](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-028.md) · [RF-029](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-029.md) | Owner · **RF-016 run155 8-owner C1 최종 ACTION 제출 완료**(B facade peer 대기). RF-028/029 run158 최종 정적 C1 ACTION 85/85·38/38 제출 완료. A C1 재실행 금지, **B 신규 RF-028 rich-schema 132/132·RF-029 facade→bundle 35/35 normal/`-O` SCOPED_PASS 수령**. 원래 전체 85/38-owner C4는 미충족; B가 최초 미검증 소비자/효과 경계를 특정하도록 인계. RF-029 run153 Owner facade는 B 독립 PASS 아님 |
| [RF-032](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-032.md) · [RF-033](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-033.md) · [RF-034](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-034.md) | Owner · **RF-033/034 run157 최종 정적 C1 ACTION 45/45·40/40, RF-032 run159 정적 ACTION 107 KEEP + 28 SAFETY_HOLD 제출 완료**. C1 재실행 금지, B 독립 C4 원래 필수 범위 대기. RF-032 UEF·RF-034 closeout/UEF 보호 실행 금지 |
| [RF-051](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/02_DEVELOPING/CLAUDE_A/RF-051.md) · [RF-054](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/02_DEVELOPING/CLAUDE_A/RF-054.md) · [RF-058](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/02_DEVELOPING/CLAUDE_A/RF-058.md) | Owner · run154 RF-051/054/058 C1 ACTION 제출 완료. 기존 effect fake 증거와 원래 C2/C3 최초 누락만 보완해 B full peer 요청; 안전한 일반 RF는 계속 진행 |
| [RF-035](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/01_PENDING/CLAUDE_A/RF-035.md) | **PENDING/일부 보호 HOLD**, RF 원본 체크와 승인 가능 범위로만 CLAIM |
| [RF-069](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CODEX_B/RF-069.md) | **SAFETY_BLOCKED** · historical UEF5 승인 전 NOT_RUN |
| [RunLab #32 원본](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md) | [20:09 FINAL](https://github.com/hbombheart1230-dotcom/agentra/issues/32#issuecomment-6440428084)에서 broker BUY `0017713` local 0, SELL `0045749` 체결·Reporter `trade_rows=[]` 확인. **A**는 RF-030/035 REPORT producer 입력 누락·UNKNOWN→GREEN 표시 후보만 read-only/temp-fake로 분리; RUN_SOURCE_SHA UNKNOWN, 보호 oracle/운영 수정 금지 |

## ▶ 신규 B Owner RF peer 준비 조건

- **RF-066:** B normal 11 PASS + `-O` 11 수집/exit0(최적화 pytest assert 제거 경고); 직접 demo yfinance 시도는 `SCOPED_FAIL/SAFETY_HOLD`. B가 fake scanner로 네트워크 시도 0을 증명하고 정확 SOURCE/원래 C1~C3를 제출할 때만 A 독립 peer.
- **RF-070:** B launcher parser 및 reporter synthetic temp writer 8/8 scoped, 아직 전체 Owner C1~C3 아님. 남은 20 OTHER·32 보호 launcher는 B 담당; 실제 server bind/운영 writer peer 금지.
- **RF-071:** B 3/42 entrypoint 정적 ACTION만 제출, `approval_cli.py`는 Step5C SAFETY_HOLD. B 39개 추가 근거 이후 A는 안전한 공개 wrapper 범위만 독립 peer.

## 무조건 끝까지 수행하는 루프

**RF 링크 열기 → 그 RF 원본 `DONE 체크`의 미완료 확인 → 수행/독립 검증 → 자기 [HANDOFF_A](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-a-reporter-pure-20261021/docs/refactor/work_orders/HANDOFF_A.md) 증분 기록·커밋/푸시 → 다음 READY RF.** 여기의 문구를 RF에 복제하지 않는다.

- **정지 금지:** 첫 작업 종료, 첫 커밋, 한 건 PASS, 첫 HANDOFF, peer/지팀장 응답 대기만으로 세션을 종료하지 않는다. 한 RF가 BLOCKED면 원본에 근거가 있는 안전 사유를 HANDOFF에 적고 **바로 다른 RF**를 수행한다. 독립 실행 가능한 READY RF가 0개거나 실제 실행 한도에 닿을 때만 종료할 수 있다. 예약 회차 밖에서 자동 지속된다고 주장하지 않는다.
- **진실성:** Owner는 자기 A 브랜치에 소스/테스트 커밋·푸시. Peer는 상대 B 정확 SHA 독립 검증. `SCOPED_PASS`를 전체 `PASS`로 바꾸지 않고 기존 PASS 중복 재실행 금지. **원본 RF 체크·물리 이동·STATUS는 C05만 수정**한다. RF-043/053 DONE, RF-052/046/047은 이미 **DONE**이므로 기존 peer 재실행·재배정 금지.
- **실행 한도 보고:** `EXECUTION_LIMIT`로 끝날 때는 D00 §4 형식의 `LIMIT_TYPE | EVIDENCE | LAST_DONE | NOT_DONE | NEXT`를 **실제 제한 신호 기준**으로 함께 남긴다. 제한값·원인 불명은 `UNKNOWN/NOT_VERIFIED`, 추정한 시간·호출수·크레딧을 사실처럼 쓰지 않는다. 가능한 READY RF가 남으면 첫 작업 완료만으로 종료하지 않는다.
- **보고 한 줄:** `RF 링크 | 원래 C번호 | SOURCE SHA | 증거 PASS/PARTIAL/NOT_RUN | 남은 C번호 | 해제 담당 | NEXT RF 링크`. [Issue #11](https://github.com/hbombheart1230-dotcom/agentra/issues/11)는 마일스톤 기록만. [D00 안전 규칙](D00_ENGINEERING_DELIVERY_POLICY.md)은 절대 완화 금지.

**이번 회차가 끝날 때 필수 숫자:** `실제 처리 RF 수 / 완료 체크 증거 수 / 코드 변경 RF 수 / peer 검증 수 / 다음 READY RF`. 문서/댓글 개수를 실적이라 부르지 않는다.
