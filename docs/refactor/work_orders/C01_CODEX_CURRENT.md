# C01 — Codex B | 현재 실행 링크

> **절대 규칙: 한 RF/한 체크/한 HANDOFF로 예약 종료 금지. 가능한 RF를 연속 수행.** 정본 [D00](D00_ENGINEERING_DELIVERY_POLICY.md) · [전체 STATUS](../plan/STATUS.md) · [C03 배정](C03_LEAD_TRIAGE_CURRENT.md). `CURRENT.md` 사용 금지. 브랜치 `work/p15-b-operator-structure-20261022`.

## 🔴 현재 최우선 — **RF 전체 종결을 앞당길 반대 peer 먼저**

A 최신 [HANDOFF_A](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-a-reporter-pure-20261021/docs/refactor/work_orders/HANDOFF_A.md) run166(조회 A HEAD `525705f6`; run166은 HANDOFF 정적 출처 분류만 추가), B HEAD `7e47cd6a` 확인. **RF-067은 C05가 C4 MET·LEAD 이동 완료**(C04 C6 대기), RF-046/047/052 DONE. B RF-033 9/9 scoped peer, RF-028/029 scoped peer 및 RF-065 출력 seam 증거는 전체 C4 PASS와 구분. 최신 RF·SOURCE/HEAD를 매회 재조회하고 이미 수용된 RF-067 C4 재검증 금지.

| 우선 | RF 원본 직접 링크 | B 역할 · **이번 회차 행동** |
|---:|---|---|
| 1 | [RF-015](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-015.md) | **반대 peer C4**: A run149 19-owner KEEP/State/event와 run145 BASE 11 FAIL 기존 분류를 재사용. B의 최신 `PEER_PARTIAL`은 full PASS가 아님. **원래 19 owner C2/C3/C4의 최초 부족 계약 하나**만 대조·검증해 정확 SOURCE/결과 제출. B-only Commander frozen failure를 Monitor 회귀로 둔갑시키지 말 것. |
| 2 | [RF-031](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-031.md) | **반대 peer C2/C4**: A run150 22-owner ACTION 및 B 최신 real caller cache/memory + partial JSON/MD OSError regeneration **SCOPED_PASS** 수용. 기존 두 marker 재실행 금지. frozen 13 보호를 분리하고 원래 writer/State/실패 계약에서 **처음 빠진 한 소비자만** 제시; full C4 여부는 정확 범위로 판정. |
| 3 | [RF-067](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-067.md) | **C05 C4 MET/LEAD 승인 완료**: A run165의 원래 공개 14-wrapper 독점 범위 `PEER_PASS` 인수. B는 추가 C4·fake-wrapper 검증/Owner 증거 재제출 **하지 않는다**. 보호 diagnostics target 실제 UEF/Broker 실행 NOT_RUN 유지. **다음 책임 C04** exact integration SHA KEEP·필수 CI C6 → C05 C7/DONE; B는 RF-015/031·다른 미완료 RF에 집중. |
| 4 | [RF-065](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/02_DEVELOPING/CODEX_B/RF-065.md) | **Owner C1/C2**: 54-owner ACTION map은 C1 후보·원본 미체크. 이전 지정 temp-root 밖 8개 산출물의 원인을 B가 `run_integrated_trade_validation.py`의 누락된 `output_root` 전달로 분류, B `1641cfef` / blob `4119747f`에서 default/explicit root seam 수정. fake downstream normal/`-O` **SCOPED_PASS** 및 **A run161 독립 공개 CLI fake 14/14 SCOPED_PASS** 확보(실 writer NOT_RUN, 전체 A peer PASS 아님, integration 미통합). **B**는 정확 SOURCE·C1 ACTION 및 원래 C2/C3 미충족 1개만 제출하고 RF-015/031 peer 우선; **A**의 run161 성공 범위 재실행 금지; 추가 원래 C4 부족 경계만 지정. 보호/운영 root 재실행 금지. |
| 5 | [RF-014](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-014.md) | **반대 peer C4**: A run148 20-owner ACTION, B 20/20 static 및 shim→RF-009 dynamic scoped 재사용. A의 원래 C2/C3 잔여가 확인되면 그 **한 계약만** 반대 peer; C1 static PASS만으로 전체 C4 PASS 선언 금지. |
| 6 | [RF-050](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-050.md) | **반대 peer C4**: A run146 caller/cache 지도, 기존 B fake 10/10 재사용. A의 8-owner 최종 C1 ACTION이 도착한 뒤 원래 UI caller/cache failure 한 경계만 peer; 운영 정책/실 모델 변경 금지. |
| 7 | [RF-063](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/02_DEVELOPING/CODEX_B/RF-063.md) | **Owner C1**: 76 owner 진단 파일 ACTION/consumer 남은 원래 범위만. |

**RF-033 신규 peer 재사용:** B `7e47cd6a` HANDOFF는 `input_worker→publish_input` temp 소비자 normal/`-O` 각 **9 PASS, 2 deselected**(`exchange_calendars` 미설치)로 `PEER_PASS_SCOPED`만 입증했다. 45-owner 전체 C4는 미완료. 기존 9/9 재실행 금지; 다음 안전 경계는 RF-034 casebook→Scanner 또는 RF-033 원래 남은 소비자 1개. 환경 의존성 실패를 신규 소스 회귀로 단정하지 않는다.

**우선순위 규칙:** 안전하고 READY인 반대 peer RF가 있으면 **RF-065 CLI 하나씩 검증하는 작업보다 먼저** 처리한다. RF-015/031에서 이미 full peer 가능한 조건을 갖췄으면 정확 SHA·원래 전체 범위 근거로 PASS를 제출해 C03/C05가 즉시 판정하도록 한다. 그럴 수 없으면 최초 미충족 원래 C번호/경계만 지목하고 **즉시 다음 RF**로 넘어간다.

**RF-065 검사 부풀리기 금지:** C1은 54파일의 ACTION·Owner·KEEP/WRAPPER/SAFETY_HOLD 근거이고, CLI 전체 1개씩 빈 입력 실행은 C1 자체와 동의어가 아니다. **매 CLI temp-fake 추가 실행을 RF-065 C1의 일괄 완료 전제조건으로 새로 만들지 말 것.** C2(효과/IO/State), C3(회귀)에서 원본 계약을 만족하는 데 필요한 대표·위험·실패 경계만 식별해 실행하고, 불충분하면 원래 계약에 연결된 부족분을 좁혀 제출한다. 기존 SCOPED_PASS는 보존하되 full PASS로 둔갑시키지 않는다.

**연속 실행·회전:** 한 RF의 안전한 신규 세부 경계 **2~3개**를 완료했거나 동일 유형의 scoped 증거가 반복되면 다른 READY RF의 C1~C4/실제 소스 결함·peer 인수로 **우선 이동**한다. 이것은 세션 종료 지시가 아니라 RF 사이의 작업 전환 지시다. 원래 RF 종료 게이트를 약화하지 않는다. 차단된 RF는 사유+담당만 남기고 다른 READY로 진행한다.

## ▶ 다음 RF — 중단 없이 순환

| RF 원본 링크 | B 역할 · 진행 |
|---|---|
| [RF-015](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-015.md) | Peer · BASE 11 FAIL 자료와 B-only frozen 회귀 분리, 실제 남은 체크 확인 |
| [RF-016](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-016.md) · [RF-028](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-028.md) · [RF-029](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-029.md) | **Peer C4** · A run158 RF-028 85/85·RF-029 38/38 최종 정적 C1 ACTION 수령. B는 **RF-028 132/132, RF-029 35/35 normal/`-O` scoped peer 완료**. 기존 성공 범위 재실행 금지; 원래 85/38-owner C4 전체 범위 중 최초 미검증 소비자/효과 경계만 특정. Owner C1 재실행 금지 |
| [RF-032](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-032.md) · [RF-033](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-033.md) · [RF-034](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-034.md) | **Peer C4** · A run157 RF-033 45/45·RF-034 40/40 최종 정적 ACTION, run159 RF-032 107 KEEP+28 SAFETY_HOLD 정적 ACTION 수령. B는 원래 input_worker/publish_input·casebook/Scanner·writer/validation-id의 안전한 최초 미검증 경계만. UEF/closeout 실제 실행 금지 |
| [RF-066](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/02_DEVELOPING/CODEX_B/RF-066.md) · [RF-070](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/02_DEVELOPING/CODEX_B/RF-070.md) · [RF-071](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/02_DEVELOPING/CODEX_B/RF-071.md) | Owner · 순차 실행 가능한 일반 RF |
| [RF-069](https://github.com/hbombheart1230-dotcom/agentra/blob/integration/p1.5/docs/refactor/plan/queue/03_PEER_REVIEW/CODEX_B/RF-069.md) | **SAFETY_BLOCKED** · 승인 전 historical UEF5 snapshot NOT_RUN |
| [RunLab #32 원본](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md) | [20:09 FINAL](https://github.com/hbombheart1230-dotcom/agentra/issues/32#issuecomment-6440428084): BUY `0017713` broker 체결/local 0, SELL `0045749` 체결·guard TTL+10.5h, Reporter 누락. **B**는 RF-012/055 ORDER 제출→로컬 로그 및 RF-048 guard 만료/filled-truth를 read-only/fake로만 추적. `RUN_SOURCE_SHA=UNKNOWN`; 운영·보호 코드 변경 금지 |

## ▶ 신규 B Owner 부분 근거 — 다음 안전 작업

- **RF-066:** normal 11 PASS + `python -O` 11 collected/exit0(최적화 pytest assert 제거로 assertion PASS 추정 금지). 직접 demo는 yfinance 시도 `SCOPED_FAIL/SAFETY_HOLD`; fake scanner fallback으로 네트워크 시도 0을 증명하는 안전 경계만 진행. 나머지 16-owner C1/C2/C3와 A 독립 peer 대기.
- **RF-070:** 두 launcher parser normal/`-O` scoped + reporter temp writer 8/8 normal/`-O` scoped 재사용. 남은 20 OTHER launcher 정적 ACTION/소비자·효과만 처리, 32 위험 launcher main/server/운영 실행 HOLD.
- **RF-071:** 42 owner 중 3개 정적 ACTION(2 COMPAT wrapper, `approval_cli.py` Step5C 승인 보호 HOLD) 재사용. 남은 39 owner의 안전한 정적/격리 효과·소비자 판정 진행; 실제 승인 CLI/주문 실행 금지.

## 🟢 C03 신규 PENDING 공급 — B Owner 후보 6건

**A 신규 CLAIM 인계:** [RF-040](../plan/queue/02_DEVELOPING/CLAUDE_A/RF-040.md)·[RF-061](../plan/queue/02_DEVELOPING/CLAUDE_A/RF-061.md)은 C05가 DEV로 이동했고 A `525705f6` run164~166에서 원래 C2/C3 Owner KEEP 후보와 실패 출처를 제출했다. RF-040 19-file normal/`-O` 각각 **1377 PASS/5 FAIL**(동일 실패); run166 정적 Git 근거는 **3건 shallow-history 객체 부재 + 2건 A 브랜치 별도 RF-021/RF-030 변경**으로 분류, BASE/integration 직접 재현 NOT_RUN. RF-061 Step5C 직접 테스트 NOT_RUN. **B는 A의 기존 5 FAIL 출처 분류를 반복하지 말고** 원래 C4 중 보호 제외 첫 미검증 소비자·효과 경계만 exact SOURCE로 독립 확인한다. **B는 정확 A/integration SOURCE의 안전한 원래 C4 경계를 독립 검토**하되 C03의 C1~C3 수용과 보호 경계를 분리하고 RF-015/031 우선. RF-040 Executor, RF-061 Step5C 보호 실행·수정 금지; Owner 증거를 full peer로 오인 금지.

**[C03의 현재 미CLAIM READY 10건 배정표](C03_LEAD_TRIAGE_CURRENT.md)를 따른다.** 이 표는 `01_PENDING/UNASSIGNED`의 후보이며 **현재 CLAIM/DEV/DONE이 아니다**. 기존 C1~C5 우선 미완료·peer/full PASS를 포기하지 않는다. **최대 2건만 동시 CLAIM**, 자기 기존 브랜치 HANDOFF에 독점·CLAIM/SOURCE SHA를 적고 C05의 실물 큐/STATUS 동기화를 기다리는 동안 다른 안전 READY RF도 계속한다.

| 순서 | RF 원본 | 신규 B Owner 후보 | 첫 원래 C1 범위·주의 |
|---:|---|---|---|
| 1 | [RF-044](../plan/queue/01_PENDING/UNASSIGNED/RF-044.md) | **B Owner 후보** · libs/contracts · 16파일 | 호환/DTO 계약; 타 RF 소유 DTO 변경 금지 |
| 2 | [RF-045](../plan/queue/01_PENDING/UNASSIGNED/RF-045.md) | **B Owner 후보** · libs/core · 10파일 | core 공개 API·의존성·회귀 |
| 3 | [RF-024](../plan/queue/01_PENDING/UNASSIGNED/RF-024.md) | **B Owner 후보** · Runtime quant · 18파일 | quant 원래 계약·효과 구분; 보호 거래 경계 미수정 |
| 4 | [RF-010](../plan/queue/01_PENDING/UNASSIGNED/RF-010.md) | **B Owner 후보** · Monitor graph · 1파일 | monitor_node 1파일, A RF-015와 소비자 충돌 확인; 안전 실행 금지 |
| 5 | [RF-011](../plan/queue/01_PENDING/UNASSIGNED/RF-011.md) | **B Owner 후보** · Commander graph · 3파일 | Commander/trading graph 3파일, Broker/Executor/Step5C 보호 구간 제외 |
| 6 | [RF-059](../plan/queue/01_PENDING/UNASSIGNED/RF-059.md) | **B Owner 후보** · libs/strategies · 21파일 | 전략 패키지 import/caller 계약·mock; 실거래/전략 정책 무승인 변경 금지 |

- **즉시 CLAIM 후보:** [RF-044](../plan/queue/01_PENDING/UNASSIGNED/RF-044.md) → [RF-045](../plan/queue/01_PENDING/UNASSIGNED/RF-045.md). 중복 CLAIM/보호 조건이 있으면 이유만 기록하고 순서상 다음 후보로 이동. 남은 후보는 선점하지 말고 소진 시 차례로 선택한다.
- **작업 단위:** 해당 RF 원본 `DONE 체크` C1~C3·정확 CODE/RESEARCH FILE_COVERAGE → 변경 필요할 때 자기 범위 내 최소 diff/격리 normal/-O·fake 확인 → `HANDOFF_B`에 최초 증거·차단·다음 RF. 외부 소비자나 타 RF 소유 파일은 읽기 전용, 보호 경계는 별도 승인 전 수정/실행 금지.
- **C05만** PENDING→DEV 물리 이동, RF 체크와 STATUS/Owner 정합성 처리를 수행. C03은 신규 후보 보충, 반대 peer 인계·C01/C02 배정만 한다. PENDING 숫자는 C05 실제 이동 전까지 그대로다.

## 무조건 끝까지 수행하는 루프

**RF 링크 열기 → 그 RF 원본 `DONE 체크`의 미완료 확인 → 수행/독립 검증 → 자기 [HANDOFF_B](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-b-operator-structure-20261022/docs/refactor/work_orders/HANDOFF_B.md) 증분 기록·커밋/푸시 → 다음 READY RF.** 여기의 문구를 RF에 복제하지 않는다.

- **정지 금지:** 첫 작업 종료, 첫 커밋, 한 건 PASS, 첫 HANDOFF, peer/지팀장 응답 대기만으로 세션을 종료하지 않는다. 한 RF가 BLOCKED면 원본에 근거가 있는 안전 사유를 HANDOFF에 적고 **바로 다른 RF**를 수행한다. 독립 실행 가능한 READY RF가 0개거나 실제 실행 한도에 닿을 때만 종료할 수 있다. 예약 회차 밖에서 자동 지속된다고 주장하지 않는다.
- **진실성:** Owner는 자기 B 브랜치에 소스/테스트 커밋·푸시. Peer는 상대 A 정확 SHA 독립 검증. `SCOPED_PASS`를 전체 `PASS`로 바꾸지 않고 기존 PASS 중복 재실행 금지. **원본 RF 체크·물리 이동·STATUS는 C05만 수정**한다. RF-043/053 DONE, RF-052/046/047은 이미 **DONE**이므로 기존 peer 재실행·재배정 금지.
- **실행 한도 보고:** `EXECUTION_LIMIT`로 끝날 때는 D00 §4 형식의 `LIMIT_TYPE | EVIDENCE | LAST_DONE | NOT_DONE | NEXT`를 **실제 제한 신호 기준**으로 함께 남긴다. 제한값·원인 불명은 `UNKNOWN/NOT_VERIFIED`, 추정한 시간·호출수·크레딧을 사실처럼 쓰지 않는다. 가능한 READY RF가 남으면 첫 작업 완료만으로 종료하지 않는다.
- **보고 한 줄:** `RF 링크 | 원래 C번호 | SOURCE SHA | 증거 PASS/PARTIAL/NOT_RUN | 남은 C번호 | 해제 담당 | NEXT RF 링크`. [Issue #12](https://github.com/hbombheart1230-dotcom/agentra/issues/12)는 마일스톤 기록만. [D00 안전 규칙](D00_ENGINEERING_DELIVERY_POLICY.md)은 절대 완화 금지.

**이번 회차가 끝날 때 필수 숫자:** `실제 처리 RF 수 / 완료 체크 증거 수 / 코드 변경 RF 수 / peer 검증 수 / 다음 READY RF`. 문서/댓글 개수를 실적이라 부르지 않는다.
