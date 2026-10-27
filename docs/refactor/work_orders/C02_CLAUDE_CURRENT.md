# C02 — Claude A 현재 작업 (2026-10-27 · 구현·최소 인계)

**작업 브랜치:** `work/p15-a-reporter-pure-20261021` (마지막 확인 HEAD `ccb0a4ea`). **정본 규칙:** [D00 §2.1](D00_ENGINEERING_DELIVERY_POLICY.md), [STATUS](../plan/STATUS.md), [LEAD 작업표](../plan/queue/04_LEAD_ACCEPTANCE/LEAD_CURRENT.md). A는 A 소유 원개발자, B 소유 RF 독립 peer다. 개인 승인·지팀장 인계 확인을 기다리지 않는다.

## P0 공통 RunLab #32 — 지팀장 배정 조사 (D04)

**사건:** [RUNLAB32-20261027 OPEN](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md) · [D04](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md). **개발 Claude A**는 `RL32-REPORT`(broker round trip 대비 `trade_index=[]`, realised sample 누락, operator GREEN vs reconciliation mismatch, stale metrics)의 **Reporter/metrics/visibility read-only trace 및 temp fake 소비자 확인**만 담당한다. 10/27 신규 SELL의 Reporter 반영 여부는 아직 UNKNOWN이며 RunLab 17/19시가 관측한다. `RUN_SOURCE_SHA=UNKNOWN` 때문에 현재 개발 HEAD 회귀라 단정하지 않는다. FILE_COVERAGE 파일 owner 매핑: `libs/reporting/operator_visibility.py` RF-030, `libs/reporting/{metrics_report_generator,reporter_bundle_runtime_parts/closed_sell_reconciliation}.py` RF-035, `apps/operator_ui/data_access_trade_index_projection.py` RF-001. **파일 owner이지 원인 확정 아님.** source SHA·입력 이벤트 provenance·출력 일관성·미실행 효과·실제 결함 RF 후보만 HANDOFF_A에 기록해 지팀장에 전달한다. 보호 readiness/Executor/운영 데이터 변경은 무승인 금지. P0 신규 사실 처리 후 RF-052/035 및 일반 RF 개발을 계속한다. RF-043/053 DONE 재실행 금지.

## RF 단계·체크 책임 (D00 §2.1)

- **A Owner:** RF-014/015/016/028/029/031/032/033/034/050은 `03_PEER_REVIEW/CLAUDE_A`(기존 LEAD에서 반환). A는 본래 C1~C3/적용 C5 근거를 전체 소유 범위 기준으로 명시하고, B peer가 원래 조건 중 실제 부족한 경계만 확인하도록 인계한다. 부분 PASS/기존 기준선 실패를 전체 PASS·신규 회귀로 바꾸지 않는다.
- **A Peer:** B 소유 RF-067/069는 `03_PEER_REVIEW/CODEX_B`, RF-063/065는 `02_DEVELOPING/CODEX_B`. RF-063 TEXT/JSON × normal/-O 4/4 재실행 금지, 067/069 기존 scoped 검증도 재사용. RF-069 UEF5 snapshot은 승인 전 `NOT_RUN/SAFETY_BLOCKED`.
- **A/B 모두:** C1~C3 Owner 제출은 전체 독립 인수가 아니며, C1~C5 필수 체크와 전체 독립 peer PASS가 없는 한 `04_LEAD_ACCEPTANCE`에 올리지 않는다. **체크 박스·STATUS 정합성은 지팀장이 갱신**하고 A는 HANDOFF에 SOURCE SHA/커버리지와 최초 부족한 C조건만 보고한다.

## 우선 14건 — A 담당별 미완료 체크 실행표

[STATUS](../plan/STATUS.md)의 RF 원본 체크에 연결한 **첫 미완료 조건**이다. A Owner는 기존 C1~C3/SOURCE 근거를 필요한 범위에서 보완하고, A peer는 B가 제출한 근거를 독립 판단한다. **체크 판정·STATUS/C6/C7은 지팀장** 책임이며, 반복 검증은 금지한다.

| A 역할 / RF | 먼저 해제할 원본 조건과 실행 |
|---|---|
| Owner **015** | **C3:** Monitor BASE 역사 11 FAIL의 node별 자료를 B에 전달, B-only Commander frozen inventory 1건은 별도 식별 |
| Owner **050** | **C4:** LLM router/cache 8-owner SOURCE/원래 호출·캐시 계약 제공 → B 10/10 scoped peer 대조 후 지팀장 판정 |
| Owner **031** | **C2:** Reporter writer/State/실패 원래 범위 증거와 B caller 8/8 대조; 부족한 계약만 보완 |
| Owner **014** | **C4:** Scanner shim→RF-009 repeat/risk/NOOP 필수 범위 제공 → B peer |
| Owner **016** | **C4:** Strategist 외부 facade 원래 호출 계약/SOURCE 제공 → B peer |
| Owner **028** | **C4:** trade_report rich schema 필수 소비자 계약 제공 → B peer |
| Owner **029** | **C4:** trade_story facade→bundle 필수 계약 제공 → B peer |
| Owner **033** | **C4:** Q10/Q12 input_worker→publish_input 원래 수용 범위 제공 → B peer |
| Owner **034** | **C4:** alpha casebook→Scanner 계약 제공 → B peer; 보호 UEF 실행 금지 |
| Owner **032** | **C2:** evaluation writer/validation-id 동등성 근거 제공 → B peer; UEF 보호 NOT_RUN |
| Peer **063 DEV** | **C1:** B 잔여 63-owner 근거 도착 시 원래 범위만 독립 peer, 기존 TEXT/JSON × normal/-O 4/4 재실행 금지 |
| Peer **065 DEV** | **C1:** B research 54-owner 분류/효과 근거 수신 후 누락된 원래 계약만 peer |
| Peer **067 PEER** | **C4:** root wrapper 기존 독립 2건 근거 범위 명시, 부족한 필수 경계만 peer |
| Peer **069 PEER** | **C3 SAFETY_BLOCKED:** 역사 UEF5 승인 전 NOT_RUN; 기존 2 CLI scoped 근거만 재사용 |

**인계:** `RF | C번호 | SOURCE SHA | OWNER/PEER 범위·기존 증거 | PASS/SCOPED_PASS/PARTIAL/NOT_RUN | 첫 미충족·해제 담당`. 완료된 RF-043/053은 이 실행표 대상이 아니며 재대기·재검증하지 않는다.

## 현재 작업

1. **RF-052 코드 수정·B path scoped peer 완료, 전체 원래 범위 미종결:** `libs/market_data/receipts.py` source blob `10283d8f`, Windows drive/UNC/backslash traversal 처리. A owner 증거: targeted pytest **40 PASS**(전 39 PASS/1 FAIL), normal/-O path harness exit0. UEF5 history 11 FAIL/49 PASS/2 ERROR는 integration 기존 실패와 동일하므로 **RF-052 신규 회귀로 오인 금지**. B `B-20261027-RF052-ARCHIVE-PATH`는 수정 blob `10283d8f` Windows/UNC/backslash traversal normal/-O exit0/0 **path 경계 PEER_PASS**. 원래 2-owner C1~C5 전체·integration CI 미완료로 DONE/통합은 보류한다.
2. **RF-046/047/054/058 KEEP 후보:** A owner의 source/import/기존 테스트 범위 검증 근거는 HANDOFF_A run141b를 재사용. **B 독립 peer와 통합 큐 소유 확정 전 전체 DONE 아님.** RF-054/058의 실제 writer/effect는 원래 수용 조건에 필요한 범위만 적어 B에 인계한다.
3. **RF-043 DONE:** A `libs/catalog` 6개 + B exact-source 11/11 independent peer → 지팀장 KEEP_VERIFIED `05_DONE`. A 재실행 금지.
4. **RF-035:** 원래 파일 119 중 RF-074 frozen oracle 충돌 93은 변경 금지, editable 26에서 **실제 원래 RF 수용 조건/버그 수정에 필요한 것만** 다룬다. 무의미한 새 광범위 소비자·IO 전수조사 금지. RF-030 보호 HOLD 및 RF-069 승인 전 UEF5 snapshot 실행 금지.
5. **A run142 RF-021/041/051/053 Owner 인수 및 RF-053 DONE:** RF-021 `02_DEVELOPING/CLAUDE_A` 콜드 import 순환 수정 blob `dc9d6528`, A 65 PASS 및 baseline 실패집합 동일 보고. **원 RF 32개 SAFETY_HOLD_KEEP와 보호 효과 판정 미완료, B peer/코드 통합 전**. RF-051 `02_DEVELOPING/CLAUDE_A` yfinance 네트워크/쓰기 fake owner 효과만 좁게 확인. RF-041 `libs/ai` 6개는 `03_PEER_REVIEW/CLAUDE_A` (B 11/11 peer, RF-021 patch integration 의존); RF-053 `libs/news` 12개는 B 15/15 peer 인수로 `05_DONE/CLAUDE_A` KEEP_VERIFIED. RF-051 A fake yfinance/network/write 4/4 owner 효과 증거 완료, B peer 대기. 자기 A 검증을 B PASS로 표기 금지.
6. **B 소유 반환 RF-063/065(DEV), 067/069(PEER):** 기존 A 독립 PASS를 재사용한다. 특히 RF-063 수정 `fdde6c82` TEXT/JSON × normal/-O 4/4는 다시 실행하지 않는다. B가 **새로 변경한 SOURCE SHA** 또는 기존 원래 조건의 미충족 항목이 생겼을 때만 새로운 peer. 이후 일반 RF 계속 CLAIM/개발.

## 인계·안전

- HANDOFF_A는 **새 source, RF owner CLAIM, 검증 범위·SHA·명령·exit·외부효과, 다음 RF만 증분 기록**. Issue #11 반복 상태 댓글 불필요.
- 원개발의 PASS는 peer PASS로 쓰지 않는다. 그러나 B peer가 전체 원래 범위를 충족하면 지팀장 임의 테스트 추가 없이 통합/CI→DONE 한다.
- `main`, 실거래·주문, Broker/Supervisor/Executor/Step5C/UEF 계약, frozen oracle/CI, 비밀·운영 데이터·배포·예약 변경 금지. Mock/temp-only, UI patchnotes 및 테스트 임시산출물 정리 유지.

## 지팀장 C03 신규 배정 델타 (2026-10-27 · 원개발/독립 peer 증거는 HANDOFF_A가 정본)
- **RF-052 C1 (A Owner):** 원본 2파일 `KEEP_CANDIDATE`를 `__init__.py` KEEP 및 `receipts.py@10283d8f` 수정/KEEP 최종 ACTION·소비자·예외/효과·정확 SOURCE SHA로 **HANDOFF_A에 한 번만** 명시해 C05에 인계하라. B `B-20261027-RF052-FULL-PEER` 40/40 normal/-O 및 Windows/UNC scoped peer **재실행 금지**. 아직 integration receipts는 이전 blob.
- **RF-046/047 C1 (A Owner):** 원본 `KEEP_CANDIDATE` 2+4파일을 A=integration=B exact blobs에 근거한 **최종 KEEP_VERIFIED ACTION/소비자/효과**로 정리해 C05에 인계하라. B `B-20261027-RF046-047-KEEP` 63/63 normal/-O peer는 재실행 금지. C05만 전체 C1~C5/LEAD를 판단한다.
- **RF-015/050:** A run145 BASE 11-node 분류와 run146 8-owner caller/cache 계약은 **이미 제출 완료**. 같은 owner 검증 반복 금지. RF-015 C3 B 매칭 및 RF-050 C4 B 독립 fake 대기; 신규 근거가 요구될 때만 A 응답.
- **RF-067 C4 (A Peer):** B가 A run138 delegated target 증거를 먼저 매칭해 **정확히 남은 원래 안전 경계**를 지정할 때만 peer 수행. 승인 없는 UEF/real preflight·운영/Windows 실호출 금지.
- **RunLab #32:** B 소스 trace는 주문 제출 후 로그 누락의 **가능 경로**일 뿐 실제 런 원인 확정 아님. A는 이미 보고한 Reporter visibility gap의 안전한 설계 후보만 유지하고, 보호 코드 수정/운영 실행은 승인 전 NOT_RUN.
