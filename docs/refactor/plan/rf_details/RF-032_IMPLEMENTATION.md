# RF-032 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@49cd60c4744c23ca556dbb633b197dbce4810d53`, RF 원본 `docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-032.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Claude A 구현 / Codex B read-only. 소유 135개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/reporting/evaluation/uef5/historical_recompute.py` blob `719101c37fcac1fe83dd5461b906e42dd5cdf24e` (1458 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 본문 행수·주의 |
|---|---|---|---|
| `libs/reporting/evaluation/uef5/historical_recompute.py::_prepare_secondary_and_cost` L1081-1151 | MOVE_BODY | `libs/reporting/evaluation/uef5/historical_recompute_prepare_secondary_and_cost.py::_prepare_secondary_and_cost` | 71행 · 순수 후보 |
| `libs/reporting/evaluation/uef5/historical_recompute.py::_pipeline_q12_calc1` L736-787 | MOVE_BODY | `libs/reporting/evaluation/uef5/historical_recompute_pipeline_q12_calc1.py::_pipeline_q12_calc1` | 52행 · 순수 후보 |
| `libs/reporting/evaluation/uef5/historical_recompute.py::_pipeline_q12_calc2` L788-834 | MOVE_BODY | `libs/reporting/evaluation/uef5/historical_recompute_pipeline_q12_calc2.py::_pipeline_q12_calc2` | 47행 · 순수 후보 |
| `libs/reporting/evaluation/uef5/historical_recompute.py::_pipeline_q10_semiconductor` L586-622 | MOVE_BODY | `libs/reporting/evaluation/uef5/historical_recompute_pipeline_q10_semiconductor.py::_pipeline_q10_semiconductor` | 37행 · 순수 후보 |
| `libs/reporting/evaluation/uef5/historical_recompute.py::_pipeline_q10_index` L653-688 | MOVE_BODY | `libs/reporting/evaluation/uef5/historical_recompute_pipeline_q10_index.py::_pipeline_q10_index` | 36행 · 순수 후보 |
| `libs/reporting/evaluation/uef5/historical_recompute.py::_q10_fg_episodes_without_cost` L623-652 | MOVE_BODY | `libs/reporting/evaluation/uef5/historical_recompute_q10_fg_episodes_without_cost.py::_q10_fg_episodes_without_cost` | 30행 · 순수 후보 |
| `libs/reporting/evaluation/uef5/historical_recompute.py::_secondary_identity` L303-327 | MOVE_BODY | `libs/reporting/evaluation/uef5/historical_recompute_secondary_identity.py::_secondary_identity` | 25행 · 순수 후보 |

### _prepare_secondary_and_cost — 원본 71행
- **확인된 책임:** `libs/reporting/evaluation/uef5/historical_recompute.py` L1081–1151; 직접 호출 helper `_verify_unchanged`, `_read_json`, `_companion`, `_calc1_candle_needs`, `_calc2_candle_needs`, `_q10_semi_candle_needs`, `_secondary_disposition`. 감지된 효과: 없음.
- **목표:** `libs/reporting/evaluation/uef5/historical_recompute_prepare_secondary_and_cost.py::_prepare_secondary_and_cost` (Owner Claude A, RF-032). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _pipeline_q12_calc1 — 원본 52행
- **확인된 책임:** `libs/reporting/evaluation/uef5/historical_recompute.py` L736–787; 직접 호출 helper `_verify_unchanged`, `_read_json`, `_companion`, `_calc1_candle_needs`, `_dedupe_episodes`, `_add_members`, `_aggregate`. 감지된 효과: 없음.
- **목표:** `libs/reporting/evaluation/uef5/historical_recompute_pipeline_q12_calc1.py::_pipeline_q12_calc1` (Owner Claude A, RF-032). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _pipeline_q12_calc2 — 원본 47행
- **확인된 책임:** `libs/reporting/evaluation/uef5/historical_recompute.py` L788–834; 직접 호출 helper `_verify_unchanged`, `_read_json`, `_calc2_candle_needs`, `_dedupe_episodes`, `_add_members`, `_aggregate`. 감지된 효과: 없음.
- **목표:** `libs/reporting/evaluation/uef5/historical_recompute_pipeline_q12_calc2.py::_pipeline_q12_calc2` (Owner Claude A, RF-032). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _pipeline_q10_semiconductor — 원본 37행
- **확인된 책임:** `libs/reporting/evaluation/uef5/historical_recompute.py` L586–622; 직접 호출 helper `_verify_unchanged`, `_read_json`, `_companion`, `_q10_semi_candle_needs`, `_dedupe_episodes`. 감지된 효과: 없음.
- **목표:** `libs/reporting/evaluation/uef5/historical_recompute_pipeline_q10_semiconductor.py::_pipeline_q10_semiconductor` (Owner Claude A, RF-032). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _pipeline_q10_index — 원본 36행
- **확인된 책임:** `libs/reporting/evaluation/uef5/historical_recompute.py` L653–688; 직접 호출 helper `_verify_unchanged`, `_q10_fg_episodes_without_cost`, `_add_members`, `_aggregate`, `_dedupe_episodes`. 감지된 효과: 없음.
- **목표:** `libs/reporting/evaluation/uef5/historical_recompute_pipeline_q10_index.py::_pipeline_q10_index` (Owner Claude A, RF-032). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _q10_fg_episodes_without_cost — 원본 30행
- **확인된 책임:** `libs/reporting/evaluation/uef5/historical_recompute.py` L623–652; 직접 호출 helper `_read_verified_json`, `_parse_reaction_target`, `_resolve_open_reference`. 감지된 효과: 없음.
- **목표:** `libs/reporting/evaluation/uef5/historical_recompute_q10_fg_episodes_without_cost.py::_q10_fg_episodes_without_cost` (Owner Claude A, RF-032). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/reporting/evaluation/__init__.py` | `libs/reporting/evaluation/__init__.py` | `fb691f9863bc` / 200B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/agent_effectiveness_scorecard.py` | `libs/reporting/evaluation/agent_effectiveness_scorecard.py` | `16b501782427` / 12747B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/artifact_inventory.py` | `libs/reporting/evaluation/artifact_inventory.py` | `e2ec5c448448` / 18239B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/attribution_score_range.py` | `libs/reporting/evaluation/attribution_score_range.py` | `ea17c616ea00` / 10502B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/attribution_score_v0.py` | `libs/reporting/evaluation/attribution_score_v0.py` | `a7a47252a2b7` / 13158B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/attribution_score_window.py` | `libs/reporting/evaluation/attribution_score_window.py` | `7deb1f069b47` / 9823B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/canonical/__init__.py` | `libs/reporting/evaluation/canonical/__init__.py` | `23a6c6e06d09` / 3994B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/canonical/adapters/__init__.py` | `libs/reporting/evaluation/canonical/adapters/__init__.py` | `8b76b9f33aa4` / 1072B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/canonical/adapters/already_net_shadow_adapter.py` | `libs/reporting/evaluation/canonical/adapters/already_net_shadow_adapter.py` | `be23986b0fb9` / 26125B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/canonical/adapters/forward_measurement_adapter.py` | `libs/reporting/evaluation/canonical/adapters/forward_measurement_adapter.py` | `67b6e4ea51b4` / 11597B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/canonical/adapters/hypothesis_forward_adapter.py` | `libs/reporting/evaluation/canonical/adapters/hypothesis_forward_adapter.py` | `555315f0523b` / 16245B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/canonical/adapters/opening_rank1_shadow.py` | `libs/reporting/evaluation/canonical/adapters/opening_rank1_shadow.py` | `2ac0c06728b5` / 28727B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/canonical/adapters/q10_index_directional_shadow_adapter.py` | `libs/reporting/evaluation/canonical/adapters/q10_index_directional_shadow_adapter.py` | `c11ee9d9aa12` / 22673B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/canonical/adapters/q10_index_reaction_adapter.py` | `libs/reporting/evaluation/canonical/adapters/q10_index_reaction_adapter.py` | `ccf89a1f4842` / 25912B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/canonical/adapters/q10_semiconductor.py` | `libs/reporting/evaluation/canonical/adapters/q10_semiconductor.py` | `03b8c7b7c3ea` / 25813B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/canonical/adapters/q12_baseline_btc_woori.py` | `libs/reporting/evaluation/canonical/adapters/q12_baseline_btc_woori.py` | `adb90f4eb082` / 14815B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/canonical/adapters/q9_horizon_exit_adapter.py` | `libs/reporting/evaluation/canonical/adapters/q9_horizon_exit_adapter.py` | `5f4ee0e2a400` / 23642B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/canonical/adapters/virtual_probe_adapter.py` | `libs/reporting/evaluation/canonical/adapters/virtual_probe_adapter.py` | `4a10fa771d0e` / 28973B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/canonical/adapters/vnext_completeness_adapter.py` | `libs/reporting/evaluation/canonical/adapters/vnext_completeness_adapter.py` | `d522a2b7c57e` / 18714B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/canonical/contracts.py` | `libs/reporting/evaluation/canonical/contracts.py` | `8bfc83b06ff5` / 9254B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/canonical/forward/__init__.py` | `libs/reporting/evaluation/canonical/forward/__init__.py` | `2317c4c4130a` / 2965B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/canonical/forward/contracts.py` | `libs/reporting/evaluation/canonical/forward/contracts.py` | `8cb533549651` / 14293B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/canonical/forward/engine.py` | `libs/reporting/evaluation/canonical/forward/engine.py` | `102831ee19f9` / 38904B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/canonical/forward/policy.py` | `libs/reporting/evaluation/canonical/forward/policy.py` | `893409c731fa` / 34008B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/canonical/forward/profiles.py` | `libs/reporting/evaluation/canonical/forward/profiles.py` | `4fbb1216e24b` / 42498B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/canonical/identity.py` | `libs/reporting/evaluation/canonical/identity.py` | `222d72730fe3` / 32323B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/canonical/metrics/__init__.py` | `libs/reporting/evaluation/canonical/metrics/__init__.py` | `3e32a67d68b9` / 2682B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/canonical/metrics/aggregation.py` | `libs/reporting/evaluation/canonical/metrics/aggregation.py` | `23d98818996c` / 21410B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/canonical/metrics/contracts.py` | `libs/reporting/evaluation/canonical/metrics/contracts.py` | `96fa8436d6f1` / 18155B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/canonical/metrics/engine.py` | `libs/reporting/evaluation/canonical/metrics/engine.py` | `2518b92374b8` / 23416B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/canonical/metrics/policy.py` | `libs/reporting/evaluation/canonical/metrics/policy.py` | `37a213c5f470` / 60287B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/canonical/record.py` | `libs/reporting/evaluation/canonical/record.py` | `85f32c16914f` / 52066B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/canonical/relations.py` | `libs/reporting/evaluation/canonical/relations.py` | `e1df08643d6e` / 10752B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/contracts.py` | `libs/reporting/evaluation/contracts.py` | `de66fd1209d8` / 1892B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/cost_basis_comparison.py` | `libs/reporting/evaluation/cost_basis_comparison.py` | `d6ceae367fea` / 9481B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/counterfactuals.py` | `libs/reporting/evaluation/counterfactuals.py` | `8429cf73588f` / 2909B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/cumulative_improvement_review.py` | `libs/reporting/evaluation/cumulative_improvement_review.py` | `a2f64696546c` / 17404B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/daily_scorecard.py` | `libs/reporting/evaluation/daily_scorecard.py` | `9c09b97144ce` / 4948B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/daily_uef_pipeline.py` | `libs/reporting/evaluation/daily_uef_pipeline.py` | `8909111a9844` / 45711B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/day_validity.py` | `libs/reporting/evaluation/day_validity.py` | `67923fe98c0d` / 8867B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/entry_timing_attribution.py` | `libs/reporting/evaluation/entry_timing_attribution.py` | `a7559c358b7f` / 20050B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/episode_scanner_review.py` | `libs/reporting/evaluation/episode_scanner_review.py` | `5bd42ffafd07` / 13204B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/evaluation_lens_report.py` | `libs/reporting/evaluation/evaluation_lens_report.py` | `cade83e2c18a` / 27561B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/feedback_effectiveness.py` | `libs/reporting/evaluation/feedback_effectiveness.py` | `f12cec33f28a` / 3085B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/five_day_freeze.py` | `libs/reporting/evaluation/five_day_freeze.py` | `824318af6d03` / 2113B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/frozen_window_closeout.py` | `libs/reporting/evaluation/frozen_window_closeout.py` | `0da35b93945e` / 14016B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/full_chain_component_review.py` | `libs/reporting/evaluation/full_chain_component_review.py` | `dc1e6c5017e5` / 43029B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/historical_prior.py` | `libs/reporting/evaluation/historical_prior.py` | `6adbc1e96e1f` / 12105B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/horizon_alignment.py` | `libs/reporting/evaluation/horizon_alignment.py` | `c41a0b655071` / 14920B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/horizon_compliance_report.py` | `libs/reporting/evaluation/horizon_compliance_report.py` | `e4d6325a8f7d` / 7655B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/horizon_contract.py` | `libs/reporting/evaluation/horizon_contract.py` | `86e423583ab4` / 10906B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/loss_decomposition.py` | `libs/reporting/evaluation/loss_decomposition.py` | `87544f1ad77e` / 22780B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/markdown.py` | `libs/reporting/evaluation/markdown.py` | `18319b98d064` / 4110B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/memory_review/__init__.py` | `libs/reporting/evaluation/memory_review/__init__.py` | `8d360bd02db0` / 105B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/memory_review/classifier.py` | `libs/reporting/evaluation/memory_review/classifier.py` | `5b998594c940` / 10940B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/memory_review/contracts.py` | `libs/reporting/evaluation/memory_review/contracts.py` | `57d87534b19a` / 481B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/memory_review/forward.py` | `libs/reporting/evaluation/memory_review/forward.py` | `a098dcae6a71` / 9120B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/memory_review/loaders.py` | `libs/reporting/evaluation/memory_review/loaders.py` | `d480564fa533` / 6215B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/memory_review/pipeline.py` | `libs/reporting/evaluation/memory_review/pipeline.py` | `cfc3c5b4b400` / 4985B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/memory_review/report.py` | `libs/reporting/evaluation/memory_review/report.py` | `afb6fdd4fd70` / 8635B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/metrics.py` | `libs/reporting/evaluation/metrics.py` | `6427c295f42a` / 1293B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/monitor_noop_attribution/__init__.py` | `libs/reporting/evaluation/monitor_noop_attribution/__init__.py` | `21fde3836e94` / 99B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/monitor_noop_attribution/contracts.py` | `libs/reporting/evaluation/monitor_noop_attribution/contracts.py` | `ac5e33a5d021` / 1055B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/monitor_noop_attribution/episodes.py` | `libs/reporting/evaluation/monitor_noop_attribution/episodes.py` | `55c85fa87f46` / 5577B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/monitor_noop_attribution/pipeline.py` | `libs/reporting/evaluation/monitor_noop_attribution/pipeline.py` | `e89be9783281` / 4583B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/monitor_noop_attribution/report.py` | `libs/reporting/evaluation/monitor_noop_attribution/report.py` | `05b685b39ff1` / 7408B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/no_trade_attribution.py` | `libs/reporting/evaluation/no_trade_attribution.py` | `967aca16db29` / 16371B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/operator_summary_mining.py` | `libs/reporting/evaluation/operator_summary_mining.py` | `1c05a5a64941` / 19758B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/pipeline.py` | `libs/reporting/evaluation/pipeline.py` | `853e2bd2cf7c` / 15713B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/post_reclaim_shadow_review.py` | `libs/reporting/evaluation/post_reclaim_shadow_review.py` | `99998254d8eb` / 3708B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/q13_q14_validation.py` | `libs/reporting/evaluation/q13_q14_validation.py` | `0c209fae4718` / 13062B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/q16_proxy_rejection_review.py` | `libs/reporting/evaluation/q16_proxy_rejection_review.py` | `09467b4d9f48` / 25234B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/q9_artifact_repair.py` | `libs/reporting/evaluation/q9_artifact_repair.py` | `aa02d22f1444` / 18325B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/rolling_scorecard.py` | `libs/reporting/evaluation/rolling_scorecard.py` | `eb3b03478376` / 2626B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/same_symbol_sequences/__init__.py` | `libs/reporting/evaluation/same_symbol_sequences/__init__.py` | `8409f3676341` / 111B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/same_symbol_sequences/builder.py` | `libs/reporting/evaluation/same_symbol_sequences/builder.py` | `5c49c05a4eb1` / 8992B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/same_symbol_sequences/pipeline.py` | `libs/reporting/evaluation/same_symbol_sequences/pipeline.py` | `8abe6cc3a226` / 4406B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/scanner_alignment_root_cause.py` | `libs/reporting/evaluation/scanner_alignment_root_cause.py` | `8774bea29dd8` / 20444B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/scanner_quality.py` | `libs/reporting/evaluation/scanner_quality.py` | `5d36b62d61fc` / 7625B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/scanner_score_decomposition.py` | `libs/reporting/evaluation/scanner_score_decomposition.py` | `52223768fde2` / 4087B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/selection_authority_audit.py` | `libs/reporting/evaluation/selection_authority_audit.py` | `7f139a43a46a` / 5539B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/stage2_authority/__init__.py` | `libs/reporting/evaluation/stage2_authority/__init__.py` | `b9499400a390` / 177B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/stage2_authority/builder.py` | `libs/reporting/evaluation/stage2_authority/builder.py` | `7b98409945a7` / 16603B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/stage2_authority/contracts.py` | `libs/reporting/evaluation/stage2_authority/contracts.py` | `1157585b49a6` / 3599B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/stage2_authority/deep_dive.py` | `libs/reporting/evaluation/stage2_authority/deep_dive.py` | `bcaaa84eea83` / 18187B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/stage2_authority/deep_dive_report.py` | `libs/reporting/evaluation/stage2_authority/deep_dive_report.py` | `e787812e1810` / 8337B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/stage2_authority/loaders.py` | `libs/reporting/evaluation/stage2_authority/loaders.py` | `a3d6e6fe20ba` / 3355B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/stage2_authority/pipeline.py` | `libs/reporting/evaluation/stage2_authority/pipeline.py` | `76939b24a54b` / 5967B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/stage2_authority/report.py` | `libs/reporting/evaluation/stage2_authority/report.py` | `ff965bb0ed75` / 3213B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/start_gate.py` | `libs/reporting/evaluation/start_gate.py` | `a449b5f599da` / 13498B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/strategist_effectiveness.py` | `libs/reporting/evaluation/strategist_effectiveness.py` | `f36cc0beef1a` / 4586B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/trade_evaluator.py` | `libs/reporting/evaluation/trade_evaluator.py` | `8ee553781321` / 5515B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/trade_read_model.py` | `libs/reporting/evaluation/trade_read_model.py` | `2f4217f3a19b` / 32723B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/uef5/__init__.py` | `libs/reporting/evaluation/uef5/__init__.py` | `c3a08edd7f5b` / 262B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef5/candle_authority.py` | `libs/reporting/evaluation/uef5/candle_authority.py` | `1f6a5a8aa4b7` / 23153B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/uef5/clean_evidence_coverage.py` | `libs/reporting/evaluation/uef5/clean_evidence_coverage.py` | `9a650f545e2d` / 19618B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef5/clean_evidence_registry.py` | `libs/reporting/evaluation/uef5/clean_evidence_registry.py` | `fa66ec2eeda4` / 31249B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/uef5/clean_evidence_rules.py` | `libs/reporting/evaluation/uef5/clean_evidence_rules.py` | `e378ea883f1c` / 41630B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/uef5/historical_recompute.py` | `libs/reporting/evaluation/uef5/historical_recompute.py` | `719101c37fca` / 78065B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/reporting/evaluation/uef5/session_policy.py` | `libs/reporting/evaluation/uef5/session_policy.py` | `c9bd221211d9` / 4681B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef5_3/__init__.py` | `libs/reporting/evaluation/uef5_3/__init__.py` | `8a68623a055d` / 1123B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef5_3/canonical_run.py` | `libs/reporting/evaluation/uef5_3/canonical_run.py` | `dad204394fb9` / 13892B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef5_3/comparison_unit.py` | `libs/reporting/evaluation/uef5_3/comparison_unit.py` | `3277e12b48a3` / 4689B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef5_3/divergence_classifier.py` | `libs/reporting/evaluation/uef5_3/divergence_classifier.py` | `5f2d84cb5646` / 39105B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/uef5_3/dual_run.py` | `libs/reporting/evaluation/uef5_3/dual_run.py` | `1a179f78c73a` / 22159B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/evaluation/uef5_3/legacy_forward_returns.py` | `libs/reporting/evaluation/uef5_3/legacy_forward_returns.py` | `34a92d4d5cbf` / 7017B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef5_3/legacy_opportunity_engine.py` | `libs/reporting/evaluation/uef5_3/legacy_opportunity_engine.py` | `dc6982b7c6fd` / 5433B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef5_3/taxonomy.py` | `libs/reporting/evaluation/uef5_3/taxonomy.py` | `c06f73c7b412` / 2031B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef6/__init__.py` | `libs/reporting/evaluation/uef6/__init__.py` | `93fb36abc426` / 861B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef6/lineage_coverage.py` | `libs/reporting/evaluation/uef6/lineage_coverage.py` | `6738abb8f9de` / 16645B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef6/lineage_model.py` | `libs/reporting/evaluation/uef6/lineage_model.py` | `234783d68860` / 7107B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef6/lineage_verify.py` | `libs/reporting/evaluation/uef6/lineage_verify.py` | `48429e894d05` / 3832B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef6/lineage_witness.py` | `libs/reporting/evaluation/uef6/lineage_witness.py` | `1783878893ef` / 10982B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef6/loader.py` | `libs/reporting/evaluation/uef6/loader.py` | `28a631342d51` / 2626B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef6/population_dedup.py` | `libs/reporting/evaluation/uef6/population_dedup.py` | `b4b21b714678` / 15554B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef6/report_model.py` | `libs/reporting/evaluation/uef6/report_model.py` | `8b6d9a165634` / 4312B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef6/reporter.py` | `libs/reporting/evaluation/uef6/reporter.py` | `730df2a3e777` / 3540B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef6/run_identity.py` | `libs/reporting/evaluation/uef6/run_identity.py` | `13e760c89501` / 2823B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef6/run_uef6a.py` | `libs/reporting/evaluation/uef6/run_uef6a.py` | `8b9283f3c37c` / 3352B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef6/validation_replay.py` | `libs/reporting/evaluation/uef6/validation_replay.py` | `076cedab0158` / 17010B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef7/__init__.py` | `libs/reporting/evaluation/uef7/__init__.py` | `8c816182d07d` / 718B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef7/alpha_board_normalization.py` | `libs/reporting/evaluation/uef7/alpha_board_normalization.py` | `0fbb3345f74f` / 16446B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef7/model.py` | `libs/reporting/evaluation/uef7/model.py` | `968ef6b9ed97` / 9503B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef7/reporter.py` | `libs/reporting/evaluation/uef7/reporter.py` | `2ddaf7f69e40` / 2696B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef7/run_identity.py` | `libs/reporting/evaluation/uef7/run_identity.py` | `ec6756229911` / 4128B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef8/__init__.py` | `libs/reporting/evaluation/uef8/__init__.py` | `4de2e42af8c1` / 743B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef8/fair_comparison.py` | `libs/reporting/evaluation/uef8/fair_comparison.py` | `a2fab9e96fd2` / 14129B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef8/model.py` | `libs/reporting/evaluation/uef8/model.py` | `eb9b784b078e` / 7156B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef8/reporter.py` | `libs/reporting/evaluation/uef8/reporter.py` | `50bb3024270f` / 2312B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef8/run_identity.py` | `libs/reporting/evaluation/uef8/run_identity.py` | `dcdcb7ed631a` / 2779B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef9/__init__.py` | `libs/reporting/evaluation/uef9/__init__.py` | `57d8c18c3b79` / 161B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef9/authority.py` | `libs/reporting/evaluation/uef9/authority.py` | `d7ba11a9c8fe` / 11099B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef9/model.py` | `libs/reporting/evaluation/uef9/model.py` | `edd084977a37` / 3094B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef9/reporter.py` | `libs/reporting/evaluation/uef9/reporter.py` | `d91b4246a752` / 2120B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/evaluation/uef9/run_identity.py` | `libs/reporting/evaluation/uef9/run_identity.py` | `199a873407ca` / 3147B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Claude A 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #11에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-032|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
