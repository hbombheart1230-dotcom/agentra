# Agentra P1.5 — STATUS (2026-10-27, RF 단계 게이트·원본 체크 정합성)

**정본:** `integration/p1.5`. 운영 기준 [D00](../work_orders/D00_ENGINEERING_DELIVERY_POLICY.md) · 지팀장 현재 [C00](../work_orders/CURRENT.md) · [LEAD 작업표](queue/04_LEAD_ACCEPTANCE/LEAD_CURRENT.md). **이 STATUS는 관측·판정 요약이며 구 회차별 상세 검증 지시를 재발행하지 않는다.** 개별 RF 문서의 예전 `LEAD_HOLD` 문구는 당시 증거 이력이다. 각 RF의 본래 DONE 체크와 보호 경계는 유효하다.

## integration 실물 큐 — 마지막 검증 스냅샷

| PENDING | DEVELOPING | PEER | LEAD | DONE | REWORK | TOTAL |
|---:|---:|---:|---:|---:|---:|---:|
| 51 | 9 | 19 | 0 | 14 | 0 | **93** |

- **기존 우선 14건:** RF-063/065 → DEV(B); RF-067/069 → PEER(B); RF-014/015/016/028/029/031/032/033/034/050 → PEER(A). **이외 DEV 7 / PEER 7 / PENDING 51 / DONE 14**로 실물 93건. 아래 원본 체크 표의 링크를 우선한다.
- **실물 큐 재분류:** 우선 14건을 DEV 2·PEER 12로 재배치. 신규 DONE이 아니라 원래 미완료 조건을 해당 담당자에게 반환한 이동이다. 기존 기록의 LEAD 14 표현은 당시 스냅샷이다.
- **LEAD 공통 새 기준:** 유효한 원래 범위 독립 peer PASS → 지팀장 SOURCE SHA·통합 diff/충돌·보호 경계·필요한 CI 확인 → **같은 회차 DONE**. 지팀장 Python/Windows/전체 소비자 재테스트 없음. Scoped PASS를 전체 PASS로 확대하지 않고, 원래 필수 미충족 1건만 해제 요청. 자세한 14건별 최초 판정은 [LEAD_CURRENT](queue/04_LEAD_ACCEPTANCE/LEAD_CURRENT.md).

<!-- RF_LEAD_CHECKLIST_START -->
## 우선 14건 RF 원본 체크리스트 — 현재 실물 단계 연동

각 RF 원본 `DONE 체크` 7항목의 판정 스냅샷입니다. **MET**는 원래 범위 근거 확인, **N/A**는 근거 있는 조건부 비적용이며 실제 PASS 수치에 더하지 않습니다. 미체크 PARTIAL/PENDING/MISSING/SAFETY_BLOCKED는 미완료입니다. DEV의 Owner 제출은 최종 MET가 아니며, PEER에서는 C1~C5 원래 조건을 전체 범위 독립 증거로 확정합니다. 물리 LEAD 진입에는 C1~C5 충족 + 전체 peer PASS가 필요합니다([D00 §2.1](../work_orders/D00_ENGINEERING_DELIVERY_POLICY.md)). 이 표는 **지팀장이 갱신**합니다.

| RF 원본 | 실물 단계·Owner→Peer | MET · N/A · 남음 | 미충족 체크 | 다음 해제 조건 · 담당 | 상태 |
|---|---|---:|---|---|---|
| [RF-063](queue/02_DEVELOPING/CODEX_B/RF-063.md) | DEV · B → A | MET 1 · N/A 1 · 5남음 | C1,C2,C3,C4,C7 | **C1** diagnostics 잔여 63-owner ACTION 및 CLI/효과/소비자 근거 (**Codex B → Claude A(peer)**) | MISSING |
| [RF-067](queue/03_PEER_REVIEW/CODEX_B/RF-067.md) | PEER · B → A | MET 3 · N/A 1 · 3남음 | C4,C6,C7 | **C4** 14 root wrapper의 원래 필수 CLI/호출 계약에 A 독립 peer 2건이 충분한지 판정; 부족한 경계만 추가 peer (**지팀장→Claude A**) | MISSING |
| [RF-015](queue/03_PEER_REVIEW/CLAUDE_A/RF-015.md) | PEER · A → B | MET 0 · N/A 1 · 6남음 | C1,C2,C3,C4,C6,C7 | **C3** 역사 11 FAIL BASE/후보 node별 분류 (**Codex B**) | MISSING |
| [RF-050](queue/03_PEER_REVIEW/CLAUDE_A/RF-050.md) | PEER · A → B | MET 0 · N/A 1 · 6남음 | C1,C2,C3,C4,C6,C7 | **C4** LLM router/cache 8-owner와 B fake 10/10 범위 대조 (**지팀장**) | MISSING |
| [RF-031](queue/03_PEER_REVIEW/CLAUDE_A/RF-031.md) | PEER · A → B | MET 0 · N/A 1 · 6남음 | C1,C2,C3,C4,C6,C7 | **C2** Reporter writer/State/실패 원래 범위 대조 (**지팀장**) | MISSING |
| [RF-014](queue/03_PEER_REVIEW/CLAUDE_A/RF-014.md) | PEER · A → B | MET 0 · N/A 1 · 6남음 | C1,C2,C3,C4,C6,C7 | **C4** Scanner shim→RF-009 repeat/risk/NOOP 독립 peer (**Codex B**) | MISSING |
| [RF-016](queue/03_PEER_REVIEW/CLAUDE_A/RF-016.md) | PEER · A → B | MET 0 · N/A 1 · 6남음 | C1,C2,C3,C4,C6,C7 | **C4** Strategist 외부 facade 원래 호출 peer 범위 판정 (**지팀장→B**) | MISSING |
| [RF-028](queue/03_PEER_REVIEW/CLAUDE_A/RF-028.md) | PEER · A → B | MET 0 · N/A 1 · 6남음 | C1,C2,C3,C4,C6,C7 | **C4** trade_report rich schema 필수 소비자 peer 판정 (**지팀장→B**) | MISSING |
| [RF-029](queue/03_PEER_REVIEW/CLAUDE_A/RF-029.md) | PEER · A → B | MET 0 · N/A 1 · 6남음 | C1,C2,C3,C4,C6,C7 | **C4** trade_story facade→bundle 독립 peer 판정 (**지팀장→B**) | MISSING |
| [RF-033](queue/03_PEER_REVIEW/CLAUDE_A/RF-033.md) | PEER · A → B | MET 0 · N/A 1 · 6남음 | C1,C2,C3,C4,C6,C7 | **C4** Q10/Q12 input_worker→publish_input peer 범위 판정 (**지팀장→B**) | MISSING |
| [RF-034](queue/03_PEER_REVIEW/CLAUDE_A/RF-034.md) | PEER · A → B | MET 0 · N/A 1 · 6남음 | C1,C2,C3,C4,C6,C7 | **C4** alpha casebook→Scanner peer 범위 판정 (UEF 보호 별도) (**지팀장→B**) | MISSING |
| [RF-032](queue/03_PEER_REVIEW/CLAUDE_A/RF-032.md) | PEER · A → B | MET 0 · N/A 1 · 6남음 | C1,C2,C3,C4,C6,C7 | **C2** evaluation writer/validation-id 원래 범위 대조 (UEF 보호 별도) (**지팀장**) | MISSING |
| [RF-065](queue/02_DEVELOPING/CODEX_B/RF-065.md) | DEV · B → A | MET 0 · N/A 1 · 6남음 | C1,C2,C3,C4,C6,C7 | **C1** research 54-owner KEEP/CLI 효과 분류 원래 조건 판정 (**지팀장**) | MISSING |
| [RF-069](queue/03_PEER_REVIEW/CODEX_B/RF-069.md) | PEER · B → A | MET 0 · N/A 1 · 6남음 | C1,C2,C3,C4,C6,C7 | **C3** UEF5 historical snapshot 경로·SHA·read-only 승인 없음 (**사용자·증거 소유자→B→A**) | SAFETY_BLOCKED |

**우선 14건:** **MET 4/98 · N/A 14/98 · 미완료 80/98**. 실제 DEV 2 + PEER 12, LEAD 0. 물리 DONE은 기존 14건이며 N/A를 증거 PASS로 합산하지 않습니다.

**STATUS 갱신 책임: 지팀장.** RF 변경/증거 인수 및 물리 이동 시 같은 작업에서 `python docs/refactor/tools/sync_rf_checklist_status.py --write` 후 `--check` 확인. 이 도구는 93개 실물 파일의 유일성/단계 수와 우선 14개 원본 체크를 대조하며 RF 합격/안전 실행을 자동 승인하지 않습니다.
<!-- RF_LEAD_CHECKLIST_END -->

## 가장 최근 수용 근거 및 작업 브랜치 신규 변경

- **RF-063 C1 지팀장 신규 실물 판독:** 76/76 원본 소스 read-only 조회, 그중 15행 thin wrapper 13/13의 정확한 source blob→`libs.runtime.entrypoints.*.main` 대상 blob 존재를 정적으로 확인. RF-063 ACTION 표에서 13개 `KEEP_CANDIDATE → WRAPPER` 수정(커밋 `54c9af95`), 잔여 63개는 후보 상태. **C1 PARTIAL 유지**(CLI/normal/-O/효과·A peer NOT_RUN), DEV 1건 단계 유지, 전체 93 큐 변화 0. 다음 Codex B owner 63개 ACTION·효과 증거 → Claude A 독립 peer.
- **RF-063:** B owner `scripts/diagnostics/run_m23_closeout_check.py` 수정 blob `fdde6c82bfc9820b853487904fb491a96cbd3408`, integration 코드 commit `c962e23a5b5395bc489c9793806fede2ff05924e`. Claude A 독립 peer TEXT/JSON × normal/-O **4/4 exit0**, [Actions 40443430786](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/40443430786) shared offline safety 두 잡 **success**. 변경 범위는 **완료된 근거**로 재사용한다. 하지만 기존 RF-063 본래 76-owner DONE 체크의 **전체 범위 충족 판정은 별도**, 현재 실물 `02_DEVELOPING/CODEX_B` 유지(C1~C4 미충족, C6 이미 통합 CI 확인). 76 CLI/Windows 운영 실행이 모두 자동 요구되는 것은 아니며 보호 사항은 개별 HOLD.
- **A 브랜치 최신 확인:** `work/p15-a-reporter-pure-20261021@ccb0a4ea9b509fb96c37a1539e89135ea08534b3`. HANDOFF_A run141b에 **신규 RF-052 Owner CLAIM/코드 수정**과 RF-046/047/054/058 KEEP 후보 검증이 있음. RF-052 `libs/market_data/receipts.py` 수정 blob `10283d8f`, targeted pytest **40 passed**(전 39 PASS/1 FAIL), normal/-O path harness exit0. UEF5 기존 결과 11 FAIL/49 PASS/2 ERROR는 수정 전과 동일하다고 A 보고. 이 결과는 **A 원개발 증거**, **B peer 미확인**, **integration 미통합**이며 승인된 UEF5 변경/운영 테스트가 아님.
- **B 브랜치 최신 확인:** `work/p15-b-operator-structure-20261022@43017525dd733bd2d79e232b3da3ffa4db65ebba`. 기존 RF-031 실제 caller **8/8**, RF-050 fake-router **10/10** 및 RF-029/016/014 scoped 독립 증거는 그대로 재사용. RF-052·RF-043 B peer 결과는 아직 이번 인수에서 확인되지 않았다.
- **A run142 신규:** RF-021 `libs/runtime/monitor_exit/policy_map_builder.py` 콜드 import 순환 의존 해소 blob `dc9d6528`(A 보고 65 PASS, baseline 대비 신규 실패 0, B peer/통합 NOT_RUN). RF-041 `libs/ai` 6파일 65 PASS, RF-051 `libs/market` 8파일 142 PASS(네트워크/쓰기 효과 owner 추가 필요), RF-053 `libs/news` 12파일 48 PASS. A owner 검증만 인수했으며 B peer PASS로 승격하지 않음.
- **RF-015 기존 실패 비교 신규 근거:** A가 B `252 PASS/12 FAIL` vs integration/BASE `253 PASS/11 FAIL`을 독립 재현; 추가 1건은 B-only Commander frozen package inventory. **Monitor 19-owner의 신규 회귀로 판정하지 않는다.** frozen CI/오라클 편집 불허. 불필요한 기준선 검증 재수행 금지.
- **RF-052/046/047:** A 원개발 증거에 따라 PEER 큐로 이동, B 독립 검증 미도착. RF-054/058은 실제 writer/effect 검증 필요해 DEVELOPING 유지. 코드 통합·DONE 0. **RF-043:** catalog 6 source BASE=A=integration 동일, A owner normal/-O 완료. B 원래 범위 독립 peer 필요. 동일 owner 테스트 재실행 금지.

## 우선 14건 미완료 해제 작업·오너

- **지팀장:** 이전 LEAD에서 반환된 우선 14건 중 원래 체크 C1~C5의 증거·SOURCE SHA·peer 범위를 먼저 대조해 04 진입 가능 여부를 판정한 다음 **본래 RF 체크·SOURCE SHA·integration/CI**만 판정. 새 CLI·State·Windows 전수 검증 목록을 만들어 돌아보내지 않는다. 충족하면 즉시 물리 `05_DONE`과 STATUS 해당 항목만 변경. 지금 이 상태표는 DONE 승격 승인 문서가 아니다.
- **B:** RF-052 수정 독립 peer → RF-043/041/053/046/047 KEEP 독립 peer, RF-021 A 패치 `policy_map_builder.py@dc9d6528` cold-import 독립 확인(원래 32 owner/SAFETY_HOLD_KEEP는 개발 계속) → 자기 RF-066/070/071 계속. 자기 원개발 PASS를 독립 peer로 표기하지 않는다.
- **A:** RF-052/046/047/054/058 owner 증거 고정 후 B peer 결과 기다리는 동안 RF-035 허용 26범위·일반 안전 RF 개발. RF-063 기존 4/4 peer 재실행 없음.
- 각 RF는 신규 FAIL/게이트 없는 한 계속 새 검증을 추가하지 않는다. `KEEP_VERIFIED`는 원래 수용 조건을 충족하면 코드 변경 없이 DONE 가능. 작업자가 BLOCKED이면 해당 RF만 차단하고 다른 일반 RF 계속.

## RunLab #32 공통 트러블슈팅 배정 (D04 연동 · 2026-10-27)

- **접수 실물:** [RUNLAB32-20261027 OPEN](troubleshooting/open/RUNLAB32_INTAKE_20261027.md) · [D04 공통 계약](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md) · [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32). 신규 접수는 **RF 큐의 새로운 DONE/REWORK·SOURCE 수정이나 RunLab 실제 테스트 실행이 아니다**.
- **지팀장 P0:** A run143의 integration/BASE × normal/-O 4/4 temp-only trace(지팀장 원격 source blob 3개 대조)를 신규 인수. **REPORT는 local SELL lifecycle producer 부재 시 `trade_index=[]`가 일관되며, realised summary 누락→trading health UNKNOWN이 Operator GREEN을 승격하지 않는 소스 표시 gap**을 분리했다. broker reconciliation 신호는 현재 Operator health 입력에 없음. **ORDER producer 실제 원인은 B read-only/fake 조사 우선**, RF-030 visibility 개선은 A 설계 후보·frozen oracle/보호 승인 전 수정 금지. 적용 이미지 RUN_SOURCE_SHA UNKNOWN이므로 원인/운영 검증은 미확정. 상세 [OPEN 대장](troubleshooting/open/RUNLAB32_INTAKE_20261027.md).
- **지팀장 P0:** #32 관측을 중복 없이 구분하고 FILE_COVERAGE blob `32fecc1b`로 **경로별 파일 Owner 매핑 완료**: ORDER RF-012/055, GUARD RF-012/048, REPORT RF-030/035/001(상세 OPEN 대장). **원인 결함 소유 RF는 `DEFECT_OWNER_PENDING`**(RUN_SOURCE_SHA UNKNOWN)이며, 사용자 승인 필요 여부·다음 증거를 C00에 배정. 개발 Codex B는 `RL32-ORDER/GUARD` **read-only·격리 fake** 원인 추적, 개발 Claude A는 `RL32-REPORT` **read-only·temp fake** 원인 추적, RunLab은 `RL32-IMAGE/OPS` 출처·예약·EOD/FINAL **읽기 전용 관측** 담당.
- **현재 증거 구분:** 10/26 mock broker BUY `0019354`·SELL `0020349` 체결, SELL local 누락/submitter UNKNOWN. 10/27 09:38 BUY guard 비움은 관측됐지만 경위 UNKNOWN; 신규 SELL `0045749` 접수만 확인, **체결·잔고 미확인**. `RUN_SOURCE_SHA=UNKNOWN`으로 최신 개발 HEAD 소스 회귀 판정 불가.
- **별도 종결:** 개발 `DEV_RESOLVED` 후에도 승인된 고정 버전 RunLab 증상 재확인 `RUNTIME_VERIFIED` 전에는 troubleshooting `OPEN/RUNTIME_PENDING`. 안전 계약·운영 DB/State·모의/실 주문·이미지/예약 변경은 승인 전 실행 금지. 무관한 우선 14개 일반 RF를 런검증 안전 HOLD에 일괄 종속시키지 않는다.

## 안전 보호 (RunLab #32 관측을 코드 결함과 분리)

2026-10-27 09:38 KST 마지막 확인: mock SELL `0045749` 체결/출처 UNKNOWN, 전일 SELL `0020349` local 누락, broker/local·guard reconciliation mismatch, OCI `RUN_SOURCE_SHA=UNKNOWN`. **실거래/주문/런검증·Broker/Supervisor/Executor/Step5C/UEF·frozen CI/oracle·비밀/운영데이터·배포·예약** 무승인 실행·변경 금지. RunLab은 읽기 전용으로만 인수하고, RunLab 문제를 무관한 RF 코드 FAIL로 간주하지 않는다.

특히 **RF-069 UEF5 historical snapshot은 path/SHA/use-scope 및 사용자·증거 소유자 승인 전 NOT_RUN/SAFETY_HOLD**. RF-032/034 보호 UEF/closeout도 승인 전 우회 금지. 안전한 일반 RF의 정상 진행은 방해하지 않는다.

## 상태 관리

**지팀장이 RF 체크·Owner/peer·단계·완료·HOLD의 변경 사항을 STATUS와 동기화**한다. 매회 불필요한 전체 HEAD/HANDOFF/Issue 재조회·전체 본문 교체·중복 게시 의무는 없다. 단 상태 변경 때는 현재 RF 원본 및 정확한 실물 경로를 확인한다. 기록에는 실제 실행한 사람, source/commit SHA, 검증 범위·PASS/FAIL/NOT_RUN, 물리 큐 변경, NEXT만 남긴다.
