# C01 — Codex B 현재 작업 (2026-10-27 · 독립 검증 우선)

**작업 브랜치:** `work/p15-b-operator-structure-20261022` (마지막 확인 HEAD `43017525`). **정본 규칙:** [D00 §2.1](D00_ENGINEERING_DELIVERY_POLICY.md), [STATUS](../plan/STATUS.md), [LEAD 작업표](../plan/queue/04_LEAD_ACCEPTANCE/LEAD_CURRENT.md). B는 A 소유 RF의 **독립 검증자**, B 소유 RF의 구현자다. 새 지팀장 승인 회차를 만들지 않는다.

## P0 공통 RunLab #32 — 지팀장 배정 조사 (D04)

**사건:** [RUNLAB32-20261027 OPEN](../plan/troubleshooting/open/RUNLAB32_INTAKE_20261027.md) · [D04](../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md). **개발 Codex B**는 `RL32-ORDER/GUARD`(mock SELL 출처/로컬 기록 누락, buy/sell fill-truth·TTL, broker↔local reconciliation, readiness) **소스 읽기 전용 추적·격리 fake 재현만 담당**한다. `execute_from_packet.py` 등 보호 경로는 임의 수정하지 않는다. 실행 이미지 `RUN_SOURCE_SHA=UNKNOWN`이므로 현재 개발 HEAD 결함이라고 단정하지 않는다. FILE_COVERAGE 파일 owner 매핑: ORDER `graphs/nodes/execute_from_packet.py` RF-012, `libs/read/kiwoom_order_fill_reader.py` RF-055; GUARD `graphs/nodes/build_execution_readiness.py` RF-012, `libs/execution/{recent_order_guard,order_lifecycle_policy,execution_readiness}.py` RF-048. **이것은 파일 owner이지 결함 원인 확정 아님.** 실제 producer/consumer·source SHA·재현 범위/NOT_RUN·결함 owner 후보를 HANDOFF_B 신규 delta로 지팀장에게 전달한다. **RF 소유 판정·안전 변경 승인은 지팀장/사용자**. 별도 RunLab PC의 Codex 스케줄 작업을 변경하거나 대신 실행하지 않는다. P0 신규 사실 인수 후 RF-052 잔여 peer·일반 RF 개발을 계속한다. RF-043/053 DONE 재실행 금지.

## RF 단계·체크 책임 (D00 §2.1)

- **B Owner:** RF-063/065는 `02_DEVELOPING/CODEX_B`, RF-067/069는 `03_PEER_REVIEW/CODEX_B`. RF-063/065의 C1~C3 기존 증거를 완료조건별로 대응시키고 부족한 1개만 보완; RF-069 C3 UEF5 snapshot 승인 전 `SAFETY_BLOCKED/NOT_RUN`; RF-067 C4 독립 A peer의 원래 wrapper 계약 충족 여부만 판단한다. **이전 LEAD 표기는 이력이며 실제 LEAD RF는 0건.**
- **B Peer:** A Owner 기존 10 RF-014/015/016/028/029/031/032/033/034/050은 `03_PEER_REVIEW/CLAUDE_A`에서 원본 C1~C3 Owner 제출 및 C4 peer의 실제 수용 범위를 좁게 매칭한다. 일부 C1~C3가 미체크인 것은 최종 인수 미확정이고, **전체 범위 C1~C5 충족 전 LEAD 반환 금지**.
- 지팀장은 RF 체크 판정·원본 메타·STATUS 수치/링크의 **유일한 갱신 책임자**. B는 HANDOFF_B에 RF·SOURCE SHA·원래 C항목 별 `OWNER_CLAIM/PEER_PASS/SCOPED_PASS/MISSING/NOT_RUN` 근거와 최초 미충족·해제 담당을 보내고, peer의 결과를 스스로 LEAD/DONE으로 변경하지 않는다.

## 우선 14건 — B 담당별 미완료 체크 실행표

[STATUS](../plan/STATUS.md)의 RF 원본 체크에 연결한 **첫 미완료 조건**이다. 기존 독립 검증은 재사용한다. 이 표는 신규 DONE 게이트가 아니다. B는 실제 SOURCE SHA·검증 범위·미실행 사유를 HANDOFF_B에 제출하고, **체크 판정·STATUS/C6/C7은 지팀장**이 갱신한다.

| B 역할 / RF | 먼저 해제할 원본 조건과 실행 |
|---|---|
| Owner **063 DEV** | **C1:** diagnostics 76 중 판정한 13 WRAPPER 외 **63 owner**의 MOVE/KEEP/SAFETY_HOLD·CLI·효과/소비자 근거 정리 → A peer |
| Owner **065 DEV** | **C1:** research **54 owner** KEEP/CLI·효과 ACTION 및 원래 계약 근거 → A peer |
| Owner **067 PEER** | **C4:** 14 root wrapper 전체 계약에 대한 A 독립 **2건 scoped** 대응 범위 인계 → 부족한 경계만 A peer |
| Owner **069 PEER** | **C3 SAFETY_BLOCKED:** UEF5 historical snapshot path/SHA/use-scope·승인 없으므로 NOT_RUN, 보호 영역 실행 금지 |
| Peer **015** | **C3:** historical 11 FAIL의 BASE/후보 node 대조, B-only Commander frozen inventory 추가 실패 1건은 Monitor 회귀로 오인하지 않음 |
| Peer **050** | **C4:** LLM router/cache 8-owner와 기존 B fake 10/10 검증 대응 범위 판정 자료 |
| Peer **031** | **C2:** Reporter writer/State/실패 원래 범위 ↔ B caller 8/8/OSError 근거 매칭, 누락한 Owner 자료는 A에 반환 |
| Peer **014** | **C4:** Scanner shim→RF-009 repeat/risk/NOOP 필수 독립 경계만 확인 |
| Peer **016** | **C4:** Strategist 외부 facade 호출 계약·nested State 기존 증거 범위 대조 |
| Peer **028** | **C4:** trade_report rich schema 필수 소비자 계약과 기존 scoped peer 대조 |
| Peer **029** | **C4:** trade_story facade→bundle 필수 계약과 truth-root peer 대조 |
| Peer **033** | **C4:** Q10/Q12 input_worker→publish_input 원래 필수 peer 범위 |
| Peer **034** | **C4:** alpha casebook→Scanner 필수 peer 범위; UEF/closeout 보호 실행 금지 |
| Peer **032** | **C2:** evaluation writer/validation-id 원래 계약 및 A Owner 증거 대조; UEF 보호 테스트 NOT_RUN |

**인계:** `RF | C번호 | SOURCE SHA | 기존 근거 vs 원래 수용 범위 | PASS/SCOPED_PASS/PARTIAL/NOT_RUN | 첫 미충족·해제 담당`. C1~C3의 원개발 보완은 Owner A/B에게, C6/C7·STATUS는 지팀장에게 남긴다.

## 즉시 실행 — 완료 peer 재실행 금지

1. **완료 인수:** B `B-20261027-RF043-CATALOG` normal/-O 11/11, `B-20261027-RF053-NEWS` 15/15 정확 source peer는 지팀장이 `RF-043/053` **05_DONE KEEP_VERIFIED**로 이동. 이 범위 재실행·재보고 금지.
2. **RF-052:** A `libs/market_data/receipts.py@10283d8f` Windows/UNC/backslash traversal 독립 path peer normal/-O exit0/0 인수. **원래 2-owner C1~C3 및 전체 C4 범위**에서 누락된 첫 항목만 보완·HANDOFF_B에 적고, 보호 UEF5/운영 데이터 변경 금지. A owner 자체 40 PASS와 별도 표기.
3. **RF-041:** A 정확 source 6개(A tree `f9176623`, RF-021 patch 포함) B 독립 11/11 PASS 수용. 현 integration은 RF-021 lazy-import patch 미통합이라 baseline cold-import 실패 존재. 원래 C1~C5 전체 범위·integration 의존성을 좁게 분리해 지팀장에 인계, 보호 RF-021 전체 32 owner 자동 해제 금지.
4. **RF-046/047 및 RF-021:** A KEEP 후보 RF-046(2)/047(4) 최소 독립 peer; RF-021 `dc9d6528` cold import normal/-O 0/0 **scoped peer 완료**, 보호 exit-policy 효과는 NOT_RUN. RF-051 A fake yfinance/network/write 4/4 owner PASS 도착 → B 독립 검증은 원래 필수 효과 경계만.
5. **B 원개발 RF-063/065/067/069 및 RF-066/070/071:** RF-063 76 owner AST 분류(13 WRAPPER, 25 read-static, 38 효과 토큰) 완료, C1은 아직 MISSING. 25 후보 소비자·KEEP 근거부터 진행, 효과형은 temp/fake 또는 SAFETY_HOLD. RF-069 historical UEF5 snapshot 승인 전 NOT_RUN. 다른 RF 차단에도 일반 안전 개발 계속. RunLab #32 ORDER/GUARD read-only/fake 조사와 source SHA 추적을 별도 유지.

## 증거·안전

- HANDOFF_B에 `RF | SOURCE SHA | original acceptance coverage | PEER_PASS / SCOPED_PASS / FAIL / NOT_RUN | command·exit | external effects | NEXT`의 **새 변화만** 기록. Issue #12 반복 댓글 금지.
- **Peer PASS면 지팀장이 직접 새 Python/Windows 테스트를 요구하는 단계가 없다.** 지팀장에게 SHA·통합·CI 판정만 넘긴다.
- `main`, 실거래·주문, Broker/Supervisor/Executor/Step5C/UEF 안전 계약, frozen CI/oracle, 비밀·운영데이터·배포·예약 무승인 변경/실행 금지. Mock/temp-only. UI 변경 시 patchnotes, 테스트 산출물 보존정책 준수.

## 지팀장 C03 신규 배정 델타 (2026-10-27 · 원개발/독립 peer 증거는 HANDOFF_B가 정본)
- **RF-015 C3 (B Peer):** A run145 `aa00bcd9`의 BASE/integration **253/11 동일 11 node**를 기존 B 252/12와 대응시켜 B-only Commander frozen inventory 1건을 분리하고, **원래 RF-015 C3의 충족 범위만** 판정·HANDOFF_B에 SHA/NOT_RUN을 남겨라. 같은 pytest 반복 금지·frozen oracle 수정 금지. A C1/C2는 별도 Owner 책임.
- **RF-050 C4 (B Peer):** A run146 `b7da8bab`의 8-owner blob·caller/cache 계약을 받아 기존 fake 10/10에서 **빠진 원래 필수 caller/State·실패/캐시 경계만** isolated fake normal/-O로 검증하라. 전체 PASS/SCOPED_PASS를 정확히 구분한다.
- **RF-067 C4 (B Owner 인계):** A run138 delegated target scoped CLI 기존 증거를 `B-20261027-RF067-C4-SCOPE-MAP`과 먼저 매칭하고 **실제 누락 경계 1개**만 A peer에게 요청하라. 14 fake wrapper/기존 target 재실행·UEF/real preflight 승인 없는 실행 금지.
- **RF-052/046/047:** B `B-20261027-RF052-FULL-PEER` 및 `RF046-047-KEEP`의 원래 범위 peer 결과를 **재실행하지 말고** A 최종 C1 ACTION이 오면 C05가 판단하도록 증거만 인계하라. C01/B는 RF 체크·LEAD 이동·STATUS를 변경하지 않는다.
- **RunLab #32:** `B-20261027-RL32-ORDER-GUARD-SOURCE-TRACE`는 read-only **가능 경로** 증거로 인수. 실제 SELL 원인·RUN_SOURCE_SHA 확정 금지. 보호 fake 실행은 승인/격리 조건 확인 전 NOT_RUN, 일반 RF는 계속 진행.
