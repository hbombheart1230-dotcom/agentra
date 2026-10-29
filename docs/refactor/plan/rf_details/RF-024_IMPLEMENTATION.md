# RF-024 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@a9568fbbc6007b9eafc6cb1c85363f406255774a`, RF 원본 `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-024.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Codex B 구현 / Claude A read-only. 소유 18개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/runtime/quant/shadow_candidates.py` blob `b95ce93495dd2750f9e4f474e249afe52419c200` (1079 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 이유/증거 |
|---|---|---|---|
| `libs/runtime/quant/shadow_candidates.py::_opening_largecap_watchlist_row` L609-688 | MOVE_BODY | `libs/runtime/quant/shadow_candidates_opening_largecap_watchlist_row.py::_opening_largecap_watchlist_row` | 80행 · 순수 후보 |
| `libs/runtime/quant/shadow_candidates.py::sync_q9_decision_candidates_for_state` L1027-1079 | KEEP_EFFECT_SPLIT_PURE | `libs/runtime/quant/shadow_candidates.py::sync_q9_decision_candidates_for_state` | 53행 · IO |
| `libs/runtime/quant/shadow_candidates.py::_opening_probe_payload` L403-453 | MOVE_BODY | `libs/runtime/quant/shadow_candidates_opening_probe_payload.py::_opening_probe_payload` | 51행 · 순수 후보 |
| `libs/runtime/quant/shadow_candidates.py::_runner_row` L509-556 | MOVE_BODY | `libs/runtime/quant/shadow_candidates_runner_row.py::_runner_row` | 48행 · 순수 후보 |
| `libs/runtime/quant/shadow_candidates.py::_market_context_from_state` L301-343 | MOVE_BODY | `libs/runtime/quant/shadow_candidates_market_context_from_state.py::_market_context_from_state` | 43행 · 순수 후보 |
| `libs/runtime/quant/shadow_candidates.py::_market_snapshot_for_symbol` L242-275 | MOVE_BODY | `libs/runtime/quant/shadow_candidates_market_snapshot_for_symbol.py::_market_snapshot_for_symbol` | 34행 · 순수 후보 |
| `libs/runtime/quant/shadow_candidates.py::_candidate_context` L119-151 | MOVE_BODY | `libs/runtime/quant/shadow_candidates_candidate_context.py::_candidate_context` | 33행 · 순수 후보 |

### _opening_largecap_watchlist_row — 원본 80행
- **확인된 책임:** `libs/runtime/quant/shadow_candidates.py` L609–688; 직접 호출 helper `_candidate_context`, `_symbol`, `_as_dict`, `_factor_snapshot`, `_metric_value`, `_text`, `_candidate_factor_snapshot`, `_bool`. 감지된 효과: 없음.
- **목표:** `libs/runtime/quant/shadow_candidates_opening_largecap_watchlist_row.py::_opening_largecap_watchlist_row` (Owner Codex B, RF-024). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### sync_q9_decision_candidates_for_state — 원본 53행
- **확인된 책임:** `libs/runtime/quant/shadow_candidates.py` L1027–1079; 직접 호출 helper `_as_dict`, `_text`, `_q9_decision_candidate_rows`, `_kst_datetime_from_state`, `_opening_minutes_since_open`, `_utc_now`. 감지된 효과: IO.
- **목표:** `libs/runtime/quant/shadow_candidates.py::sync_q9_decision_candidates_for_state` (Owner Codex B, RF-024). IO·State·class context가 있는 부분은 원위치 효과 Owner로 KEEP. 실제 부작용과 무관한 계산 블록만 확인된 경우에 한해 새 pure helper로 분리, 아니면 KEEP_JUSTIFIED 한 줄로 승인.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _opening_probe_payload — 원본 51행
- **확인된 책임:** `libs/runtime/quant/shadow_candidates.py` L403–453; 직접 호출 helper `_factor_snapshot`, `_float`, `_bool`, `_cost_ok_for_opening_probe`. 감지된 효과: 없음.
- **목표:** `libs/runtime/quant/shadow_candidates_opening_probe_payload.py::_opening_probe_payload` (Owner Codex B, RF-024). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _runner_row — 원본 48행
- **확인된 책임:** `libs/runtime/quant/shadow_candidates.py` L509–556; 직접 호출 helper `_symbol`, `_candidate_context`, `_bool`, `_text`, `_as_dict`. 감지된 효과: 없음.
- **목표:** `libs/runtime/quant/shadow_candidates_runner_row.py::_runner_row` (Owner Codex B, RF-024). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _market_context_from_state — 원본 43행
- **확인된 책임:** `libs/runtime/quant/shadow_candidates.py` L301–343; 직접 호출 helper `_text`, `_resolve_day`, `_as_dict`. 감지된 효과: 없음.
- **목표:** `libs/runtime/quant/shadow_candidates_market_context_from_state.py::_market_context_from_state` (Owner Codex B, RF-024). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _market_snapshot_for_symbol — 원본 34행
- **확인된 책임:** `libs/runtime/quant/shadow_candidates.py` L242–275; 직접 호출 helper `_normalize_minute_rows`, `_minute_root`, `_text`. 감지된 효과: 없음.
- **목표:** `libs/runtime/quant/shadow_candidates_market_snapshot_for_symbol.py::_market_snapshot_for_symbol` (Owner Codex B, RF-024). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/runtime/quant/__init__.py` | `libs/runtime/quant/__init__.py` | `a5f019bb85a2` / 225B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/quant/context.py` | `libs/runtime/quant/context.py` | `9403a678cd8c` / 8270B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/quant/contracts.py` | `libs/runtime/quant/contracts.py` | `76d91b5c6439` / 3195B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/quant/decision.py` | `libs/runtime/quant/decision.py` | `0157cf735ef6` / 12219B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/quant/enforcement.py` | `libs/runtime/quant/enforcement.py` | `a891f58c8409` / 2449B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/quant/entry_lane_observation.py` | `libs/runtime/quant/entry_lane_observation.py` | `90e32792ef4d` / 14459B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/quant/entry_promotion_policy.py` | `libs/runtime/quant/entry_promotion_policy.py` | `3bbf47d1b89b` / 3332B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/quant/factors.py` | `libs/runtime/quant/factors.py` | `2c4bc82473a1` / 8821B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/quant/market_rail_translation.py` | `libs/runtime/quant/market_rail_translation.py` | `7faad7623294` / 9175B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/quant/market_regime_observation.py` | `libs/runtime/quant/market_regime_observation.py` | `ca43361564d9` / 5548B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/quant/memory.py` | `libs/runtime/quant/memory.py` | `e08d6aa5c3b0` / 4626B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/quant/opening_largecap_surge_shadow.py` | `libs/runtime/quant/opening_largecap_surge_shadow.py` | `3aabb5e8f781` / 4774B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/quant/risk_off_defensive_policy.py` | `libs/runtime/quant/risk_off_defensive_policy.py` | `dbd8e427529f` / 2968B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/quant/scorecard.py` | `libs/runtime/quant/scorecard.py` | `161af1e2e18a` / 7569B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/quant/shadow_candidates.py` | `libs/runtime/quant/shadow_candidates.py` | `b95ce93495dd` / 43778B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/runtime/quant/suitability.py` | `libs/runtime/quant/suitability.py` | `440d836adb89` / 6345B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/quant/tactics.py` | `libs/runtime/quant/tactics.py` | `f8aa70a1846f` / 3311B | 짧은 단일 책임이면 KEEP_OK |
| `libs/runtime/quant/vwap_reclaim_observation.py` | `libs/runtime/quant/vwap_reclaim_observation.py` | `1c74351d990f` / 7225B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Codex B 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #12에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-024|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
