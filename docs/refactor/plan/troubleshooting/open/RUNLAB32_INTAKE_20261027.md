# RUNLAB32 — RunLab #32 신규 증상 접수·개발 인계 (2026-10-27)

**CASE:** `RUNLAB32-20261027` · **상태:** `OPEN / SAFETY_HOLD`(영향받는 주문·운영 경계만) · **지팀장:** TRIAGE_OWNER · **정본 규칙:** [D04](../../../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md) ↔ [D00](../../../work_orders/D00_ENGINEERING_DELIVERY_POLICY.md) ↔ [C03 배정](../../../work_orders/C03_LEAD_TRIAGE_CURRENT.md).

**증거 범위:** [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32)에서 2026-10-26 EOD [Codex 결과](https://github.com/hbombheart1230-dotcom/agentra/issues/32#issuecomment-6411226322) · [추가 소스 조사](https://github.com/hbombheart1230-dotcom/agentra/issues/32#issuecomment-6411909991) · 2026-10-27 [07시](https://github.com/hbombheart1230-dotcom/agentra/issues/32#issuecomment-6428473788) · [09:38 독립 관측](https://github.com/hbombheart1230-dotcom/agentra/issues/32#issuecomment-6430800415) · [20:09 FINAL 독립 관측](https://github.com/hbombheart1230-dotcom/agentra/issues/32#issuecomment-6440428084). **원본 증거는 `C:\AgentraRunLab`의 RunLab 보존 경로**, 이 문서는 공개 가능한 요약/작업 배정만 유지. 실행 중 이미지 digest는 `sha256:f3d1a4a3…`로 보고됐으나 **RUN_SOURCE_SHA=UNKNOWN**; 현재 integration 코드와 런타임 동일 버전임을 주장하지 않는다.

## 실제 접수·배정 — 신규 RF 생성/큐 이동 전

| 항목/분류(현시점) | 증거·정확한 미해결 범위 | 임시 조사 담당 | 지팀장 차기 판정/해제 조건 |
|---|---|---|---|
| `RL32-ORDER` / `SAFETY+UNKNOWN` | 10/26 보존 mock broker BUY `0019354`, SELL `0020349` 양쪽 **체결**, local 이벤트는 BUY만; SELL 제출 owner·account-wide exclusivity 미상. 10/27 SELL `0045749` **체결 확정**, broker BUY `0017713`도 체결됐으나 **local event 0건**(제출 owner UNKNOWN) | **Dev Codex B:** `execute_from_packet` 주문 이벤트→`kiwoom_order_fill_reader`→reconciliation 경로의 **읽기 전용 소스/격리 fake 재현**. **RunLab 17시 담당:** 기존 증거/승인된 모의 브로커 snapshot의 신규 차이 관측 | 지팀장이 실제 독점 owner RF 확인 후 **해당 원 Owner에만 코드 작업 배정**. 제출자/로컬 불일치/체결 미확인을 사후 추정으로 메우지 않음. 새 주문·취소·복구 없음 |
| `RL32-GUARD` / `SAFETY+UNKNOWN` | 10/26 BUY guard `filled_qty=-1/remaining_qty=-1` TTL 뒤 잔류. **10/27 09:38에는 buy_guard.orders={}로 해소된 상태 관측**(정리 원인·시각 UNKNOWN). 10/27 SELL `0045749` guard `filled_qty=-1`, `remaining_qty=-1`, `fill_truth_confirmed=false`가 체결 이후에도 잔류(09:38 TTL 만료 후 약 10.5h, 20:09 관측) | **Dev Codex B:** Guard 업데이트/만료/브로커 truth 반영 및 `build_execution_readiness` mismatch 처리 read-only/fake 분석. **RunLab:** 새 BUY/SELL guard 상태만 read-only 관측 | 기존 BUY guard가 여전히 잔류한다고 주장 금지. 새 SELL fill/TTL·readiness 불일치 재현과 코드 owner 확정, 안전 변경 전 사용자 승인 |
| `RL32-REPORT` / `PRODUCER_INPUT_MISSING + VISIBILITY_DESIGN_GAP` (scoped source) | A run143 integration/BASE × normal/-O 4/4 exit0: `trade_index`는 local lifecycle artifact만 소비하므로 SELL local producer 부재 시 `[]`가 코드상 일관됨. `performance/summary.json` 부재 시 trading health `UNKNOWN`, Operator 집계는 RED/YELLOW만 승격하여 **GREEN 유지 가능**. broker reconciliation 입력은 해당 health 집계에 없음. 20:09 broker diary 청산 1건 대비 local `trade_rows=[]`/`total_trades=0` 재관측; 실제 RunLab 버전/근본 원인은 미확정 | **Dev Codex B:** ORDER producer provenance/누락 원인(read-only fake). **Dev Claude A:** RF-030 visibility gap의 안전한 입력/표시 계약 후보만 제시(코드 변경 금지). **RunLab 17/19시:** 적용 이미지 실제 local lifecycle/SELL/health 대조 | **원인 분리:** `RL32-REPORT` trade_index 소비 결함은 현재 소스에서 미재현, ORDER producer 누락 우선; GREEN misleading visibility는 **RF-030 후보 설계 결함**(frozen oracle/보호 변경 승인 전 HOLD). `RUN_SOURCE_SHA` 입증 및 적용 런 증거 전 DEV_RESOLVED/RUNTIME_VERIFIED 금지 |
| `RL32-IMAGE` / `ENV+PROVENANCE_BLOCKED` | 실행 이미지에 OCI revision/빌드 증명 부족: `RUN_SOURCE_SHA=UNKNOWN`. RUN 이미지와 새로운 integration HEAD 불일치만으로 코드 FAIL 아님 | **RunLab Codex(07/17시):** 이미지 digest·기존 빌드 provenance 읽기 전용 조사, **지팀장:** 소유/승인 경로 결정 | 현 이미지 무승인 재빌드/교체 금지. **차기 승인 빌드에서** revision label·digest↔SHA 증명 도입 후 해당 런 검증 가능 |
| `RL32-OPS` / `ENV_PENDING` | 07시 예약 등록/활성의 독립 증명 부족. 10/27 17시 Codex EOD 결과는 20:09 FINAL 기준 `NOT_RUN / UPSTREAM_NOT_RUN`(보고 부재; 실제 실행 여부 단정 금지). 장중 market listener reconnecting, 복사본 `C:\AgentraRunLab\logs\events.jsonl` stale 대비 실제 `src/data/logs/events.jsonl` 갱신 | **RunLab 운영 담당:** 기존 예약 등록 여부·활성 상태·로그 경로를 읽기 전용 구분. **지팀장:** 승인 필요한 일정/설정 변경 판정 | 예약 미확정≠07시 보고/런 ID 전체 부재; 실제 설정 변경은 사용자 별도 승인 후만 |

## 2026-10-27 20:09 FINAL 신규 관측 인수 — 기존 OPEN delta (21시 C03 배정)

- **원본:** [Issue #32 FINAL #6440428084](https://github.com/hbombheart1230-dotcom/agentra/issues/32#issuecomment-6440428084). 실행 이미지 digest `sha256:f3d1a4a354c2244af714f8e8564aba9164fc3efa5c98163040ecf402e372b6b8`, **RUN_SOURCE_SHA=UNKNOWN**. 로컬 RunLab DB/로그/브로커 보존 증거를 C03이 직접 열람하거나 운영 런을 재실행하지 않음.
- **ORDER 신규:** 229200 mock BUY `0017713` 09:05:21 체결, mock SELL `0045749` 체결. 브로커 2건 vs local 1건(SELL만), **BUY local event 0건**. 기존 10/26 SELL `0020349` 누락과 비슷한 패턴이지만 동일 원인/제출자라는 증거는 없음. **B**는 `RF-012/055`의 submit→event logger 실패/누락·order-id 매핑을 **read-only/fake**로 분리, 신규 주문·취소·복구 금지.
- **GUARD 신규:** SELL `0045749` `filled_qty=-1/remaining_qty=-1`, `fill_truth_confirmed=false`, TTL 09:38:02 이후 약 10.5h 잔류. **B**는 `RF-048` 및 `RF-012` guard persist/prune와 fill-truth 소비 경계만 read-only/fake로 조사. 10/27 오전 BUY guard는 이미 비워졌으며 정리 원인은 여전히 UNKNOWN.
- **REPORT 재확인:** broker diary 청산 1건(실현손익 +75원, 비용 80원 보고)인데 `performance/summary.json`은 `total_trades=0/trade_rows=[]`, 10/27 reports/trades 없음. **A**는 `RF-030/035/001`의 producer 누락과 UNKNOWN→GREEN visibility 후보를 read-only/temp-fake로 분리. 적용 이미지의 Reporter 소비자 결함 확정이나 보호 코드 변경은 금지.
- **IMAGE/OPS:** 17시 Codex EOD 보고 없음(`UPSTREAM_NOT_RUN`), 20:09 FINAL이 보존된 자료로 독립 관측. **RunLab**은 이미지 digest↔source provenance, EOD/예약 상태를 읽기 전용으로 확인; 무승인 예약 수정·재배포 금지.
- **분류/종결:** `FILE_OWNER_MAPPED / DEFECT_OWNER_PENDING / DEV_RESOLVED=NO / RUNTIME_VERIFIED=NO / OPEN / SAFETY_HOLD`. mock 환경의 Docker 건강·LLM 부분 PASS는 주문-로컬 정합 FAIL이나 버전별 PASS를 대체하지 않음. 사용자 별도 승인 없는 주문·보호 실행·운영 파일/이미지/설정 변경 금지. 새로운 RF 생성·RF 큐 이동·코드 변경·CI 실행 없음.

## 2026-10-28 07:00 START 신규 관측 인수 — 기존 OPEN 사건 delta (C03 08시)

- **출처:** [Issue #32 07시 START](https://github.com/hbombheart1230-dotcom/agentra/issues/32#issuecomment-6454782573), RUN_ID `start_20261028_070423`. REMOTE_HEAD `48b47e102bbd557de3a8b06ffc0740c8f11f2aa0`, 로컬 체크아웃/source 표시 `a4083434522f1ad0e8d4762f3c8eb02b16641a52`, image digest `sha256:f3d1a4a354c2244af714f8e8564aba9164fc3efa5c98163040ecf402e372b6b8`. **image→source revision 증명 없음: RUN_SOURCE_SHA=UNKNOWN / TESTED_SHA=UNPROVEN.** 로컬 SHA나 REMOTE_HEAD를 실행 이미지 SHA로 승격 금지.
- **운영 관측 범위:** 10/25 기존 런타임 보존·재시작 없음, Docker 3/3 healthy, API/UI HTTP 200, mock 및 `ALLOW_REAL_EXECUTION=false` 플래그 확인. `REBUILD/REDEPLOY=BLOCKED`; 이것은 **버전별 RUNTIME_VERIFIED나 주문 정합 PASS가 아님**. 10/28 장전 market/LLM 신규 실검증 NOT_RUN(전일 저장 메타만 확인), fresh broker 조회·주문·취소 없음.
- **ORDER/GUARD delta:** 10/26 BUY `0019354` 체결·SELL `0020349` local 누락, 10/27 BUY `0017713` local 누락·SELL `0045749` local 대응이라는 **기존 보존 snapshot 불일치 지속**. 이전 BUY guard는 현재 empty이나 정리 원인/시각 UNKNOWN. SELL `0045749` guard `filled_qty=-1/remaining_qty=-1`, fill truth 미확정 상태 지속. 보존 snapshot의 과거 open-orders empty를 현재 계좌 전체 소유권/브로커 상태 PASS로 사용 금지(`CURRENT_BROKER_STATE/ACCOUNT_WIDE_OWNERSHIP=UNKNOWN`).
- **REPORT/IMAGE/OPS delta:** 10/27 broker round trip 대비 local `trade_index=[]/trade_count=0` 불일치 지속. OCI revision·이미지 출처 미증명, 기존 `--allow-offhours` 기동 기록으로 세션 동등성도 UNPROVEN. 07시 START 보고는 있으므로 이전의 07시 예약 미확정 기록을 **오늘 SLOT NOT_RUN**으로 확대하지 않는다. 실제 예약 등록/소유권은 별도 증명 대기.
- **기존 담당 유지(새 RF/CLAIM 없음):** **B** `RL32-ORDER/GUARD` RF-012/055/048의 submit→local event·fill/TTL 경계 read-only/fake 조사, **A** `RL32-REPORT` RF-030/035/001 producer 누락·UNKNOWN→GREEN 후보 read-only/temp-fake 조사, **RunLab** image digest↔source·lease/account ownership·적용 증거 읽기 전용 확인. `FILE_OWNER_MAPPED ≠ DEFECT_OWNER`. 승인 전 보호 코드·주문·운영 DB/State·이미지·예약·재배포 변경 금지.
- **판정:** `DEFECT_OWNER_PENDING / DEV_RESOLVED=NO / RUNTIME_VERIFIED=NO / OPEN / SAFETY_HOLD`. RunLab 원본 PC DB/로그/이미지를 C03이 직접 열람·재실행한 것은 아님. RF 체크·물리 큐·STATUS·CI·DONE 변경 없음.

## 2026-10-27 A run143 독립 read-only 조사 인수 — REPORT producer/visibility 분리

- **A source 기준:** integration `179a6f50` 및 BASE `63182ab2`, `rl32_report_trace.py` temp-only × normal/`python -O` **4/4 exit0**(A 실행 보고, 지팀장 직접 재실행 NOT_RUN). 현재 integration `libs/reporting/operator_visibility.py` blob `26c71139e363...`, `symbol_trade_report.py` blob `099cdbd0...`, `intraday_trade_reports.py` blob `819ce8b8...`를 지팀장이 별도 원격 read-only 조회.
- **입력→소비자 경계:** `build_daily_trade_index`는 local lifecycle 산출물에 의존. BUY `generate_intraday_trade_artifacts`는 `generate_on_open=false`이면 `trade_report_generate_on_open_disabled`로 skip할 수 있고, SELL local producer가 없으면 closed lifecycle가 없어 `trade_index=[]`가 된다. **실제 10/26 누락 원인은 B의 ORDER provenance 조사가 필요**하며, 이 소스 관찰만으로 broker 체결 여부·런타임 버전·데이터 누락 시점을 확정하지 않는다.
- **GREEN 원인 소스 확인:** `operator_visibility.py` `_build_trading_health_status`는 summary 부재 또는 realised sample=0에서 `UNKNOWN`을 반환. `build_operator_daily_summary_payload`의 집계(`~L804-861`)는 `RED`/`YELLOW`만 `_raise_health`로 승격하며 `UNKNOWN`은 무시해 기본 `GREEN`이 남는다. 집계 입력에 broker↔local reconciliation signal 없음. **이건 source-level visibility gap(후보 RF-030)**이지 RunLab 적용 이미지에서 수정 검증된 결함이 아니다.
- **판정/Owner:** `RL32-ORDER` producer 원인 B read-only/fake 우선(후보 RF-012/055), `RL32-REPORT` 표시/health gap A가 RF-030 원소유로 **안전한 개선안만 설계**. RF-030 frozen-oracle/운영 안전 경계는 사용자 승인 없이 수정하지 않는다. 원래 `OPEN / SAFETY_HOLD`, `DEFECT_OWNER_PENDING`(런 소스) 유지. **코드 수정·주문·배포·운영 쓰기 0**.

## FILE_COVERAGE 실제 경로→RF 소유 매핑 (지팀장 읽기 전용 인수)

기준: `docs/refactor/plan/FILE_COVERAGE_63182ab2.csv` blob `32fecc1bf00d261eacbd9a027e6d02be83893366`, BASE `63182ab2`. integration의 다음 경로 source를 직접 조회했으나 **운영 이미지 RUN_SOURCE_SHA는 여전히 UNKNOWN**. CSV의 RF는 **파일 책임 소유자**이지 런타임 증상의 원인/수정 RF 확정이 아니다. CSV verification은 아래 경로 대부분 `UNVERIFIED`; 실제 root-cause는 B/A의 읽기 전용 조사 결과 전까지 `DEFECT_OWNER_PENDING`.

| 사건 | 소스 경로 → 파일 RF | 소스 연결 관찰 / 다음 확인 |
|---|---|---|
| RL32-ORDER | `graphs/nodes/execute_from_packet.py` → **RF-012**; `libs/read/kiwoom_order_fill_reader.py`, `kiwoom_broker_truth_common.py` → **RF-055** | `kiwoom_order_fill_reader.load_local_execution_rows`는 `stage=execute_from_packet`, `event=execution` JSONL을 소비. SELL `0020349`의 실제 제출 경로와 로컬 이벤트 누락 지점을 B가 read-only/fake로 분리. RF-012 보호 실행 경계는 수정 금지 |
| RL32-GUARD | `graphs/nodes/build_execution_readiness.py` → **RF-012**; `libs/execution/recent_order_guard.py`, `order_lifecycle_policy.py`, `execution_readiness.py` → **RF-048** | readiness 노드 주석상 `execute_from_packet`가 `state.execution_readiness.ready`를 소비. SELL fill-truth/TTL과 reconciliation 입력 생성 vs 소비 구간을 B가 분리, 보호 계약 수정 금지 |
| RL32-REPORT | `libs/reporting/operator_visibility.py` → **RF-030**; `libs/reporting/metrics_report_generator.py`, `reporter_bundle_runtime_parts/closed_sell_reconciliation.py` → **RF-035**; `apps/operator_ui/data_access_trade_index_projection.py` → **RF-001** | `trade_index=[]`의 producer 입력 누락 vs Reporter/Operator 소비 결함은 아직 미분류. A가 fake/temp로 비교, RF-030 동결 오라클/보호 HOLD 유지 |
| RL32-IMAGE/OPS | 소스 경로 미확정(OCI revision label·런이미지/운영 예약 메타) | RunLab이 read-only provenance 확보, 이미지 교체/재배포/예약 변경은 승인 전 금지 |

**판정:** `FILE_OWNER_MAPPED`(위 경로만) / `DEFECT_OWNER_PENDING` / `DEV_RESOLVED=NO` / `RUNTIME_VERIFIED=NO`. 원래 RF의 개발 owner를 임의 교체하거나 이 매핑만으로 RF를 REWORK/DONE 처리하지 않는다.

### 지팀장에게 부여된 공통 작업

- **현재 C03이 접수·배정 관리할 대상:** `RL32-ORDER/GUARD`의 개발 B 읽기 전용 조사, `RL32-REPORT`의 개발 A 읽기 전용 조사, `RL32-IMAGE/OPS`의 RunLab 환경 관측과 지팀장 소유자 분류.
- **최초 미해결 계약만 분류:** Source bug 재현 시 `FILE_COVERAGE`와 원 Owner를 확인해 기존 RF로 연결; RF 소유 미확정·보호 영역인 동안 `OWNER_MAPPING_PENDING / SAFETY_HOLD`. 사용자가 승인하지 않은 Executor/Broker/Supervisor/Step5C/UEF 수정·frozen CI/오라클 변경 금지. A/B는 **이 인수 자체로 보호 코드 수정 권한을 얻지 않는다**.
- **개발 정상 종결과 운영 종결 분리:** Developer `PEER_PASS → integration/CI`는 `DEV_RESOLVED`일 뿐, RunLab 적용 image/source SHA가 검증되고 해당 증상을 재확인하기 전까지 `RUNTIME_PENDING / OPEN`. 무승인 컨테이너 재배포/주문을 요구하지 않는다.
- **새 사실만 추적:** 같은 현상이 RunLab #32에 다시 올라오면 기존 CASE 표의 **delta와 원본 댓글 링크만** 갱신. 수용 증거/테스트 재실행과 별개 문서 체크포인트 반복 금지.

**현재 실제 수행:** Issue #32 근거 확인 및 문서상 OPEN·담당 배정. RunLab PC 직접 실행·Dev A/B 신규 진단·코드 fix·통합 CI·운영 재검증 **NOT_RUN**. 현재 상태는 `OPEN`, `DEV_RESOLVED=NO`, `RUNTIME_VERIFIED=NO`. 별도 RF 큐 이동·DONE 발생 없음.

## 2026-10-27 B 신규 read-only ORDER/GUARD 소스 trace 접수 (런검증 아님)

- **출처:** `work/p15-b-operator-structure-20261022@7af57e8e`, [HANDOFF_B](https://github.com/hbombheart1230-dotcom/agentra/blob/work/p15-b-operator-structure-20261022/docs/refactor/work_orders/HANDOFF_B.md), `B-20261027-RL32-ORDER-GUARD-SOURCE-TRACE`. **소스 정적 추적만**, fake/CLI/브로커/운영 런 **NOT_RUN**.
- **ORDER 가능 경로:** 정상 흐름에서 `execute_from_packet`는 `execute_owned_order` → recent guard 갱신 → `stage=execute_from_packet, event=execution` JSONL 기록 순서. `kiwoom_order_fill_reader.load_local_execution_rows`는 그 이벤트와 주문 ID·심볼·모드·broker message/order-id 조건을 요구한다. 따라서 **주문 제출 후 로그 기록 전 실패**는 broker truth가 존재해도 local reconciliation row가 없을 수 있는 **가설 경계**다. SELL `0020349`의 실제 원인 입증은 아님.
- **GUARD/READINESS:** unknown fill은 `-1`로 보존, `expires_epoch` 만료 평가는 있지만 persisted pruning은 이후 정상 갱신 경로에 의존. `build_execution_readiness`는 fresh portfolio/open-order/ownership/Step5C 입력 소비자이며 local execution event를 생성·broker/local reconciliation하지 않는다. 10/27 오전 BUY guard 비움 원인은 여전히 UNKNOWN.
- **판정 유지:** `FILE_OWNER_MAPPED`(ORDER RF-012/055, GUARD RF-012/048) / `DEFECT_OWNER_PENDING` / `RUN_SOURCE_SHA=UNKNOWN` / `OPEN/SAFETY_HOLD` / `DEV_RESOLVED=NO` / `RUNTIME_VERIFIED=NO`. 차기 증거는 **승인된 격리 fake에서 post-submit logger-failure 경계** 또는 RunLab의 이미지 SHA provenance. 실제 주문/취소/재배포·보호 코드 변경·운영 파일 쓰기 금지.

## 2026-10-28 09:38 MORNING 신규 장중 관측 (C03 10시 접수)

- **새 입력:** [RunLab #32 댓글 `6457499824`](https://github.com/hbombheart1230-dotcom/agentra/issues/32#issuecomment-6457499824). 기존 07:00 START와 **동일 이미지 digest**, `RUN_SOURCE_SHA=UNKNOWN`; RunLab 보고상 Docker 3/3 healthy, mock/`ALLOW_REAL_EXECUTION=false`. 오늘 09:02–09:38 Agent Chain/LLM 결과 27건, `execute_from_packet` 7건 모두 noop, **당일 신규 주문 0**. 이는 **장중 일부 가동 관측**이지 적용 버전 검증이나 주문·Reporter 종단 PASS가 아님.
- **변경 없는 미해결:** 10/26 SELL `0020349`·10/27 BUY `0017713`의 local 미기록, 10/27 SELL `0045749` fill-truth `-1` guard 잔류, 10/27 `trade_index=[]/trade_count=0`. 오늘 거래 0이므로 **10/28 Reporter 거래 정합은 NOT_RUN**. 브로커 현재 상태·account-wide owner·이미지 source SHA는 UNKNOWN. 새 개발 SOURCE SHA/독립 peer/수정 재현 없음.
- **기존 안전 배정 유지(재배정/새 RF 아님):** **B** RF-012/055/048 ORDER→logger·fill/TTL read-only/temp-fake 조사, **A** RF-030/035/001 local producer·UNKNOWN→GREEN 표시 계약 read-only 설계, **RunLab** OCI revision·주문 출처·적용 버전 관측. 원 RF 소유와 런 결함 owner는 구분. `DEFECT_OWNER_PENDING / DEV_RESOLVED=NO / RUNTIME_VERIFIED=NO / OPEN / SAFETY_HOLD` 유지. 주문·취소·운영 쓰기·배포·예약·보호 코드 변경 없음.
