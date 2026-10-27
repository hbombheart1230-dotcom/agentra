# RUNLAB32 — RunLab #32 신규 증상 접수·개발 인계 (2026-10-27)

**CASE:** `RUNLAB32-20261027` · **상태:** `OPEN / SAFETY_HOLD`(영향받는 주문·운영 경계만) · **지팀장:** TRIAGE_OWNER · **정본 규칙:** [D04](../../../../runtime/validation/D04_RUNTIME_VALIDATION_RULES.md) ↔ [D00](../../../work_orders/D00_ENGINEERING_DELIVERY_POLICY.md) ↔ [C00](../../../work_orders/CURRENT.md).

**증거 범위:** [Issue #32](https://github.com/hbombheart1230-dotcom/agentra/issues/32)에서 2026-10-26 EOD [Codex 결과](https://github.com/hbombheart1230-dotcom/agentra/issues/32#issuecomment-6411226322) · [추가 소스 조사](https://github.com/hbombheart1230-dotcom/agentra/issues/32#issuecomment-6411909991) · 2026-10-27 [07시](https://github.com/hbombheart1230-dotcom/agentra/issues/32#issuecomment-6428473788) · [09:38 독립 관측](https://github.com/hbombheart1230-dotcom/agentra/issues/32#issuecomment-6430800415). **원본 증거는 `C:\AgentraRunLab`의 RunLab 보존 경로**, 이 문서는 공개 가능한 요약/작업 배정만 유지. 실행 중 이미지 digest는 `sha256:f3d1a4a3…`로 보고됐으나 **RUN_SOURCE_SHA=UNKNOWN**; 현재 integration 코드와 런타임 동일 버전임을 주장하지 않는다.

## 실제 접수·배정 — 신규 RF 생성/큐 이동 전

| 항목/분류(현시점) | 증거·정확한 미해결 범위 | 임시 조사 담당 | 지팀장 차기 판정/해제 조건 |
|---|---|---|---|
| `RL32-ORDER` / `SAFETY+UNKNOWN` | 10/26 보존 mock broker BUY `0019354`, SELL `0020349` 양쪽 **체결**, local 이벤트는 BUY만; SELL 제출 owner·account-wide exclusivity 미상. 10/27 SELL `0045749` **접수**, 체결/보유 출처 UNKNOWN | **Dev Codex B:** `execute_from_packet` 주문 이벤트→`kiwoom_order_fill_reader`→reconciliation 경로의 **읽기 전용 소스/격리 fake 재현**. **RunLab 17시 담당:** 기존 증거/승인된 모의 브로커 snapshot의 신규 차이 관측 | 지팀장이 실제 독점 owner RF 확인 후 **해당 원 Owner에만 코드 작업 배정**. 제출자/로컬 불일치/체결 미확인을 사후 추정으로 메우지 않음. 새 주문·취소·복구 없음 |
| `RL32-GUARD` / `SAFETY+UNKNOWN` | 10/26 BUY guard `filled_qty=-1/remaining_qty=-1` TTL 뒤 잔류. **10/27 09:38에는 buy_guard.orders={}로 해소된 상태 관측**(정리 원인·시각 UNKNOWN). 10/27 SELL guard도 fill-truth 불명 `-1` | **Dev Codex B:** Guard 업데이트/만료/브로커 truth 반영 및 `build_execution_readiness` mismatch 처리 read-only/fake 분석. **RunLab:** 새 BUY/SELL guard 상태만 read-only 관측 | 기존 BUY guard가 여전히 잔류한다고 주장 금지. 새 SELL fill/TTL·readiness 불일치 재현과 코드 owner 확정, 안전 변경 전 사용자 승인 |
| `RL32-REPORT` / `OBSERVED_CONSISTENCY_FAIL / ROOT_CAUSE_UNKNOWN` | 10/26 EOD broker round trip 대비 local `trade_index=[]`, realised sample 누락, operator GREEN, 09시 metrics stale. 10/27 Reporter 산출은 갱신됐으나 SELL 포함 여부 **NOT_VERIFIED** | **Dev Claude A:** `libs/reporting/operator_visibility.py` 등 Reporter/metrics 소비자 경로의 **read-only + temp fake 조사**, 외부 효과 0. **RunLab 17/19시:** 기존 기록과 오늘 결과 증분 독립 대조 | 이벤트 입력 누락/보고서 소비 결함/환경을 구별한 뒤 실제 owner RF(후보만, 미확정) 지정. 보호 guard·readiness 편집 금지 |
| `RL32-IMAGE` / `ENV+PROVENANCE_BLOCKED` | 실행 이미지에 OCI revision/빌드 증명 부족: `RUN_SOURCE_SHA=UNKNOWN`. RUN 이미지와 새로운 integration HEAD 불일치만으로 코드 FAIL 아님 | **RunLab Codex(07/17시):** 이미지 digest·기존 빌드 provenance 읽기 전용 조사, **지팀장:** 소유/승인 경로 결정 | 현 이미지 무승인 재빌드/교체 금지. **차기 승인 빌드에서** revision label·digest↔SHA 증명 도입 후 해당 런 검증 가능 |
| `RL32-OPS` / `ENV_PENDING` | 07시 예약 등록/활성의 독립 증명 부족. 장중 market listener reconnecting, 복사본 `C:\AgentraRunLab\logs\events.jsonl` stale 대비 실제 `src/data/logs/events.jsonl` 갱신 | **RunLab 운영 담당:** 기존 예약 등록 여부·활성 상태·로그 경로를 읽기 전용 구분. **지팀장:** 승인 필요한 일정/설정 변경 판정 | 예약 미확정≠07시 보고/런 ID 전체 부재; 실제 설정 변경은 사용자 별도 승인 후만 |

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

- **현재 C00에 등록/배정 완료 대상:** `RL32-ORDER/GUARD`의 개발 B 읽기 전용 조사, `RL32-REPORT`의 개발 A 읽기 전용 조사, `RL32-IMAGE/OPS`의 RunLab 환경 관측과 지팀장 소유자 분류.
- **최초 미해결 계약만 분류:** Source bug 재현 시 `FILE_COVERAGE`와 원 Owner를 확인해 기존 RF로 연결; RF 소유 미확정·보호 영역인 동안 `OWNER_MAPPING_PENDING / SAFETY_HOLD`. 사용자가 승인하지 않은 Executor/Broker/Supervisor/Step5C/UEF 수정·frozen CI/오라클 변경 금지. A/B는 **이 인수 자체로 보호 코드 수정 권한을 얻지 않는다**.
- **개발 정상 종결과 운영 종결 분리:** Developer `PEER_PASS → integration/CI`는 `DEV_RESOLVED`일 뿐, RunLab 적용 image/source SHA가 검증되고 해당 증상을 재확인하기 전까지 `RUNTIME_PENDING / OPEN`. 무승인 컨테이너 재배포/주문을 요구하지 않는다.
- **새 사실만 추적:** 같은 현상이 RunLab #32에 다시 올라오면 기존 CASE 표의 **delta와 원본 댓글 링크만** 갱신. 수용 증거/테스트 재실행과 별개 문서 체크포인트 반복 금지.

**현재 실제 수행:** Issue #32 근거 확인 및 문서상 OPEN·담당 배정. RunLab PC 직접 실행·Dev A/B 신규 진단·코드 fix·통합 CI·운영 재검증 **NOT_RUN**. 현재 상태는 `OPEN`, `DEV_RESOLVED=NO`, `RUNTIME_VERIFIED=NO`. 별도 RF 큐 이동·DONE 발생 없음.
