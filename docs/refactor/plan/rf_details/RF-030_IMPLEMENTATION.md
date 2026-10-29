# RF-030 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@a9568fbbc6007b9eafc6cb1c85363f406255774a`, RF 원본 `docs/refactor/plan/queue/01_PENDING/CLAUDE_A/RF-030.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Claude A 구현 / Codex B read-only. 소유 16개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/reporting/operator_visibility.py` blob `26c71139e363632e914dff16e690ef2d209277c6` (1521 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 이유/증거 |
|---|---|---|---|
| `libs/reporting/operator_visibility.py::_build_run_contexts` L357-680 | MOVE_BODY | `libs/reporting/operator_visibility_build_run_contexts.py::_build_run_contexts` | 324행 · 순수 후보 |
| `libs/reporting/operator_visibility.py::_build_trading_health_status` L181-223 | MOVE_BODY | `libs/reporting/operator_visibility_build_trading_health_status.py::_build_trading_health_status` | 43행 · 순수 후보 |
| `libs/reporting/operator_visibility.py::_iter_jsonl` L94-113 | KEEP_EFFECT_SPLIT_PURE | `libs/reporting/operator_visibility.py::_iter_jsonl` | 20행 · IO |

### _build_run_contexts — 원본 324행
- **확인된 책임:** `libs/reporting/operator_visibility.py` L357–680; 직접 호출 helper `_run_context_default`, `_safe_int`, `_reason_text`, `_humanize_reason`, `_compact_kv_text`, `_decision_trace_inner`, `_broker_code_success`, `_normalize_reason_code`. 감지된 효과: 없음.
- **목표:** `libs/reporting/operator_visibility_build_run_contexts.py::_build_run_contexts` (Owner Claude A, RF-030). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _build_trading_health_status — 원본 43행
- **확인된 책임:** `libs/reporting/operator_visibility.py` L181–223; 직접 호출 helper `_read_json`, `_safe_int`, `_safe_float`. 감지된 효과: 없음.
- **목표:** `libs/reporting/operator_visibility_build_trading_health_status.py::_build_trading_health_status` (Owner Claude A, RF-030). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _iter_jsonl — 원본 20행
- **확인된 책임:** `libs/reporting/operator_visibility.py` L94–113; 직접 호출 helper `_gen`. 감지된 효과: IO.
- **목표:** `libs/reporting/operator_visibility.py::_iter_jsonl` (Owner Claude A, RF-030). IO·State·class context가 있는 부분은 원위치 효과 Owner로 KEEP. 실제 부작용과 무관한 계산 블록만 확인된 경우에 한해 새 pure helper로 분리, 아니면 KEEP_JUSTIFIED 한 줄로 승인.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/reporting/operator_candidate_decisions.py` | `libs/reporting/operator_candidate_decisions.py` | `f381c6cf1b57` / 2446B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/operator_period_summary.py` | `libs/reporting/operator_period_summary.py` | `d6d1dd1ceb95` / 44813B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/operator_period_summary_parts/closeout_reconciliation.py` | `libs/reporting/operator_period_summary_parts/closeout_reconciliation.py` | `f365ed88d29b` / 8239B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/operator_period_summary_parts/markdown_daily_summary.py` | `libs/reporting/operator_period_summary_parts/markdown_daily_summary.py` | `1fccf10264dc` / 17273B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/operator_period_summary_parts/markdown_period_symbol_summary.py` | `libs/reporting/operator_period_summary_parts/markdown_period_symbol_summary.py` | `79c904a04a64` / 8382B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/operator_period_summary_parts/operator_readouts.py` | `libs/reporting/operator_period_summary_parts/operator_readouts.py` | `fffbf8e497b3` / 4246B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/operator_period_summary_parts/pattern_buckets_and_performance.py` | `libs/reporting/operator_period_summary_parts/pattern_buckets_and_performance.py` | `3a2b652091e8` / 14920B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/operator_period_summary_parts/pattern_naming.py` | `libs/reporting/operator_period_summary_parts/pattern_naming.py` | `ee5924070a0b` / 10513B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/operator_period_summary_parts/period_payloads.py` | `libs/reporting/operator_period_summary_parts/period_payloads.py` | `6f10f994521d` / 10463B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/operator_period_summary_parts/residual_positions.py` | `libs/reporting/operator_period_summary_parts/residual_positions.py` | `3e5454d9b36d` / 13887B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/operator_period_summary_parts/trade_decision_fields.py` | `libs/reporting/operator_period_summary_parts/trade_decision_fields.py` | `27edc86c7772` / 18339B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/operator_period_summary_parts/trade_rows_and_metrics.py` | `libs/reporting/operator_period_summary_parts/trade_rows_and_metrics.py` | `5ff83b766bd7` / 14473B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/operator_summary_refresh.py` | `libs/reporting/operator_summary_refresh.py` | `91b2549c307f` / 4667B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/operator_visibility.py` | `libs/reporting/operator_visibility.py` | `26c71139e363` / 77321B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/reporting/operator_visibility_parts/reason_text_and_time.py` | `libs/reporting/operator_visibility_parts/reason_text_and_time.py` | `e111f89416e8` / 7638B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/operator_visibility_parts/summary_snapshot_and_bundle.py` | `libs/reporting/operator_visibility_parts/summary_snapshot_and_bundle.py` | `fea5094b7a91` / 12679B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Claude A 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #11에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-030|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
