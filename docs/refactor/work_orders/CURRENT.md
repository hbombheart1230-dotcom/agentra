# Agentra P1.5 — CURRENT

**정본:** `hbombheart1230-dotcom/agentra` / `integration/p1.5`
**운영:** [D00](D00_ENGINEERING_DELIVERY_POLICY.md) · **RF:** [물리 큐](../plan/queue/) · **집계:** [STATUS](../plan/STATUS.md)

**이 브랜치의 CURRENT만 지시 정본이다.** A/B는 자신의 브랜치 CURRENT·구 HANDOFF의 지시를 사용하지 않는다. D00 및 아래 배정 RF만 필요 시 읽어라. 같은 SHA·같은 경계 반복 검증·ACK 문서로 종료하지 마라.


## 상시 실행·작성 규칙 — 지팀장/A/B 공통

**지팀장은 앞으로도 CURRENT를 매번 구체적인 명령문으로 작성하라.** 각 작업에 반드시 담당자, 우선순위, 지금 실행할 RF, 정확한 대상 파일/함수, 검증할 신규 경계, 정상/-O 명령과 exit, 제출 산출물, 막혔을 때 다음 RF를 명시하라. '검토 필요'·'진행 예정'·'결정 대기'만 써 놓고 작업 지시라고 하지 마라. **'확인하라 → 분류하라 → 수정하거나 KEEP하라 → 검증하라 → SHA·exit를 제출하라 → 다음 RF를 실행하라'**로 써라.

**A/B는 지시를 받으면 실제 실행하라.** 매번 integration/p1.5의 최신 CURRENT·HEAD를 읽고 자기 배정 RF만 수행하라. 기존 유효 SHA·동일 테스트는 재실행하지 마라. 앞 작업이 BASELINE/ENV/SAFETY/동결 오라클 때문에 막히면 그 원인과 해제 조건을 적고 즉시 다음 안전한 RF를 수행하라. 소스 수정이 가능하면 실제 commit+normal/-O 증거를, KEEP이면 파일별 소비자·IO/State·예외 근거를, peer면 처음 보는 경계의 독립 증거를 제출하라. ACK·HANDOFF 문서만 수정하고 종료하지 마라.

**지팀장은 이미 나온 증거의 RF 판정·큐 이동·소스 통합을 개발자에게 되돌리지 마라.** 직접 ACCEPT/HOLD/KEEP/FIX/PEER/REWORK/INTEGRATE를 결정하고 물리 큐를 갱신하라. 다음 배정을 확정한 뒤 CURRENT를 마지막에 고쳐라. 이 상시 지시형 운영 규칙을 이후 CURRENT 개정에서도 반드시 유지하라.

## Claude A — `work/p15-a-reporter-pure-20261021`

**이번 회차 실제 실행 1순위 RF-033 원개발** [02_DEVELOPING/CLAUDE_A](../plan/queue/02_DEVELOPING/CLAUDE_A/RF-033.md). 45 owner 중 `libs/reporting/baseline_btc_woori_tech/{contracts.py,comparison.py,forward_returns.py}`를 먼저 BASE `63182ab2`/integration/A SHA별로 확인하고 공개 소비자, 입력 누락·잘못된 값·예외, read-only State/IO를 분류하라. 원본 frozen 경계 `python -m pytest -q -p no:cacheprovider tests/test_work_reporter_seed_migration.py::test_target_tree_discipline_and_no_forbidden_surface` 및 `python -O -m pytest -q -p no:cacheprovider tests/test_work_reporter_seed_migration.py::test_target_tree_discipline_and_no_forbidden_surface`를 새 수정 후보에서 **처음** 확인하라. 안전 격리 fake market input을 `/tmp/rf033_offline_boundary.py`에 생성하여 `python /tmp/rf033_offline_boundary.py` / `python -O /tmp/rf033_offline_boundary.py`로 normal/-O 실제 exit·assertion marker 제출. 소켓·broker·주문·운영 경로 쓰기 금지, frozen 13 owner/RF-030 금지 후보 우회 금지. 의미 있는 owner-local FIX가 가능하면 코드 SHA·정확한 patch·consumer 동등성·normal/-O exit와 필요한 UI patchnotes JSON/MD 제출. FIX 불가면 45개 파일별 KEEP/FIX/HOLD 근거를 제출하고 아래 RF-065로 이동하라. Issue #11은 증거 제출용, 배정 경로가 아니다.

**차선 RF-065 신규 안전 독립 peer** [03_PEER_REVIEW/CLAUDE_A](../plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-065.md). 기존 130/130 import-only와 RF-063 감사 CLI 2개 재검증 금지. `scripts/research/daily_profitability_scorecard.py`의 읽기 중심 `main(argv)` 소비자 경계를 임시 synthetic inputs와 network/sqlite/subprocess/운영 파일 쓰기 차단 후 `/tmp/rf065_offline_peer.py` 정상/-O 최초 실행. 실제 실행/쓰기 차단 불가 시 SAFETY_HOLD 후 다음 안전 RF로 이동, 위험 `__main__` 강행 금지. B 소스 SHA·exit·미검증 효과를 HANDOFF_A와 Issue #11에 제출.

**기존 RF-031** [03_PEER_REVIEW/CODEX_B](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-031.md): A 22 owner KEEP/13 frozen HOLD·9 FIX 미입증 및 BASE 동일 실패 수용, 원개발 종료. 동일 85 test-file 반복 금지, B 신규 peer 대기. **RF-030** [01_PENDING/CLAUDE_A](../plan/queue/01_PENDING/CLAUDE_A/RF-030.md) RF-074 동결 오라클 HOLD, 미승인 source `03b255e5` 통합·재검증 금지. RF-063 감사 CLI scoped PASS 재사용; RF-007 fastapi ENV 차단, RF-008·067 scoped peer 재사용.

**A 제출 필수:** RF | 신규 source SHA 또는 KEEP 파일별 근거 | 최초 명령과 normal/-O exit | frozen oracle 결과 | read-only 효과 차단 | 다음 실행 가능 RF. 코드/테스트/CI/거래 안전 무승인 변경 금지. 자기 브랜치 CURRENT·큐 수정 금지.

## Codex B — `work/p15-b-operator-structure-20261022`

**RF-001** [04_LEAD_ACCEPTANCE/FROM_CODEX_B](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CODEX_B/RF-001.md): integration exact SHA `b5fe3dd9` 3 test-file normal/-O 각각 706+28+53 PASS, exit 0, owner blob `0666538f`/`4f73570f` **수용 완료**. 같은 SHA·경계 재실행 금지. 지팀장 잔여 33 owner/hosted CI 판정 전 NOT_DONE. 코드 SHA 바뀌거나 신규 위험 발생 시에만 최초 새 테스트.

**1순위 RF-028 최초 신규 peer** [03_PEER_REVIEW/CODEX_B](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-028.md). A 85 owner BASE 동일·fake LLM 11케이스 재사용. `libs/reporting/trade_report`의 아직 미검증된 동적 consumer 1~2개를 실제 파일에서 선정하여 use-time monkeypatch, IO/State 불변, 예외 전파를 `/tmp/rf028_peer_boundary.py` 합성 입력으로 `python /tmp/rf028_peer_boundary.py` 및 `python -O /tmp/rf028_peer_boundary.py` **처음** 검증, exit/marker/차단 경계 제출. 실제 broker/운영 파일/LLM 호출 금지.

**2순위 RF-031 신규 독립 peer** [03_PEER_REVIEW/CODEX_B](../plan/queue/03_PEER_REVIEW/CODEX_B/RF-031.md). A 22 owner KEEP/13 frozen HOLD/9 FIX 미입증 증거 재사용. `libs/reporting/reporter_analysis.py`의 read_text→summary write/feedback State·예외 순서 또는 `libs/reporting/trade_report_ai.py`의 fake LLM timeout/exception 소비자 중 최초 안전 경계 한 개를 `/tmp/rf031_peer_boundary.py`로 격리, normal/-O 명령과 exit 제출. 임시 파일만 쓰기, 실제 네트워크·운영 데이터 금지; 재현된 원개발 코드 결함만 지팀장에게 CODE 분류 보고.

**3순위 RF-066** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-066.md): 기존 build_demo_catalog normal marker/-O exit-only 반복 금지. `/tmp/rf066_fake_orderclient.py`에 fake `OrderClient` 요청/실패 assertion 및 network/broker 차단을 구축하여 `python /tmp/rf066_fake_orderclient.py` / `python -O /tmp/rf066_fake_orderclient.py` exit와 **양쪽 성공 marker** 제출. 실제 `main()`/주문 금지. 격리 실패 시 NOT_RUN/HOLD 후 RF-070으로 이동.

**4순위 RF-070** [02_DEVELOPING/CODEX_B](../plan/queue/02_DEVELOPING/CODEX_B/RF-070.md): 기존 85/142 wrapper scoped PASS 재사용, 남은 25 launcher AST 소비자·argv/subprocess/IO/State·부작용 분류를 파일별 완료, 32 위험 launcher 실행 금지. **RF-029** [04_LEAD_ACCEPTANCE/FROM_CLAUDE_A](../plan/queue/04_LEAD_ACCEPTANCE/FROM_CLAUDE_A/RF-029.md): B 최초 precedence/fail-soft offline peer normal/-O exit 0 인수 완료, 반복 금지. RF-018 BASE fallback 반복 금지, RF-069 UEF5 snapshot ENV HOLD.

**B 제출 필수:** RF | 테스트 대상 정확 SHA | 최초 명령·normal/-O exit | fake 입력·효과 차단 | CODE/BASELINE/ENV/UNKNOWN 분류 | 다음 RF. HANDOFF_B와 Issue #12는 결과 기록용; 큐·CURRENT 수정 금지.

## 지팀장 — `integration/p1.5`

**이번 인수 (2026-10-26):** A `992acf6e` RF-031 22 owner KEEP, RF-063 2 read-only CLI 최초 peer PASS; B `9f39745c` RF-001 `integration@b5fe3dd9` 3파일 정상/-O 각 787 PASS exit 0, RF-029 신규 offline fake-artifact peer PASS. A/B 신규 source SHA 0. **지팀장 직접 판정·큐:** RF-029 PEER→LEAD(KEEP_NOOP_SCOPED/NOT_DONE), RF-031 DEVELOPING→PEER(KEEP/독립 peer 필요), RF-033 PENDING→DEVELOPING A 신규 배정. RF-001 exact b5fe 표적 게이트 PASS이나 33 owner/hosted CI/새 HEAD 전체 검증 미완료로 LEAD/NOT_DONE. 신규 소스 선별 통합 0, 신규 DONE 0.

**런검증 [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32) EOD:** broker BUY/SELL filled 증거 수용, broker 2 vs local 1 mismatch·SELL origin UNKNOWN·BUY guard stale·Reporter trade_index empty·metrics stale·running image SHA 미입증. RUNTIME_ENV/UNKNOWN 관측으로 보존, 소유 코드 재현 전 REWORK 금지. RUNLAB 환경·예약은 RunLab 담당, 지팀장 무승인 변경 금지.

**troubleshooting:** [open](../plan/troubleshooting/open/) 4건 / [closed](../plan/troubleshooting/closed/) 0건 확인, 해결조건 증명 없음→이동 0. STATUS는 이번 RF 이동에 맞춰 갱신. A/B 기존 normal/-O·peer 반복 금지. 새로운 owner source SHA·독립 peer·frozen 오라클·patchnotes·exact integration SHA/CI가 모두 충족되는 최소 코드만 지팀장이 직접 선별 통합. RF-001/029/031 부분 PASS를 DONE으로 승격하지 마라.

**다음 지팀장 실행:** ① 이 integration CURRENT만 읽고 A/B 새 HANDOFF·source diff·Issue #32 확인 ② 신규 CODE/BASELINE/ENV/SAFETY/UNKNOWN 분류 ③ 이미 충족된 RF는 직접 KEEP/FIX/PEER/INTEGRATE/HOLD 판정·원자 큐 이동 ④ 허용 owner blob만 선별 통합 및 exact-SHA normal/-O 증거 인수 ⑤ troubleshooting open/closed 종료조건 확인, STATUS 정합화 ⑥ A/B 구체적 다음 RF 배정 ⑦ **CURRENT를 마지막에 갱신**. 실행 가능한 지팀장 RF가 있으면 보고만 하고 종료하지 마라. main·실거래·Broker/Supervisor/Executor/Step5C/UEF·동결 테스트/CI·예약 무승인 변경 금지.

**물리 큐 기준 (이번 조치 후):** PENDING **65** (UNASSIGNED 64, CLAUDE_A RF-030 HOLD 1) / DEVELOPING **3** (A RF-033, B RF-066/070) / PEER **10** (B RF-028/031 등) / LEAD **4** (RF-001/008/029/069) / REWORK **0** / DONE **11** = **93 RF**, 단일 경로. 정확한 원격 tree 확인 후 확정.
