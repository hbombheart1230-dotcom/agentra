# RF-032 — 코드 구조/함수 재배치 설계 (T00/V3)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-032.md` blob `8dc5408d66313431450dd03b0ae5a9f4eec3aa86`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 135개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `libs/reporting/evaluation/uef5/historical_recompute.py` | 78065 | `719101c37fcac1fe83dd5461b906e42dd5cdf24e` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/uef5/historical_recompute_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/canonical/metrics/policy.py` | 60287 | `37a213c5f470927abaaced261efe0ec1b26137b3` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/canonical/metrics/policy_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/canonical/record.py` | 52066 | `85f32c16914fa1edb9d9c41ee94438a89fc0db48` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/canonical/record_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/daily_uef_pipeline.py` | 45711 | `8909111a9844173789319b723c666f8a6b73933a` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/daily_uef_pipeline_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/full_chain_component_review.py` | 43029 | `dc1e6c5017e537057864be84b659f0803efa0a8c` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/full_chain_component_review_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/canonical/forward/profiles.py` | 42498 | `4fbb1216e24b9cad5f16684558335b661b1bf9fe` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/canonical/forward/profiles_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/uef5/clean_evidence_rules.py` | 41630 | `e378ea883f1c7814d87a06d7501092ae9d92c9ad` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/uef5/clean_evidence_rules_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/uef5_3/divergence_classifier.py` | 39105 | `5f2d84cb5646fd22f8899d349069968759b2941d` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/uef5_3/divergence_classifier_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/canonical/forward/engine.py` | 38904 | `102831ee19f9627f37af359f70230c5de9c61086` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/canonical/forward/engine_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/canonical/forward/policy.py` | 34008 | `893409c731fae0ee05618f9294c786c512592372` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/canonical/forward/policy_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/trade_read_model.py` | 32723 | `2f4217f3a19bafaef1cc8bc07009e9aa34f22c34` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/trade_read_model_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/canonical/identity.py` | 32323 | `222d72730fe3d71fd417badc874e605409c63181` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/canonical/identity_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/uef5/clean_evidence_registry.py` | 31249 | `fa66ec2eeda483415a9f000ec0727339e7bc476d` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/uef5/clean_evidence_registry_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/canonical/adapters/virtual_probe_adapter.py` | 28973 | `4a10fa771d0eda353e152d01b3407ab1bb577a56` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/canonical/adapters/virtual_probe_adapter_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/canonical/adapters/opening_rank1_shadow.py` | 28727 | `2ac0c06728b5b9d6344ef2f2373e01c2bfb3e7d4` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/canonical/adapters/opening_rank1_shadow_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/evaluation_lens_report.py` | 27561 | `cade83e2c18aecbde557acad9a0e26ca2fbe3938` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/evaluation_lens_report_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/canonical/adapters/already_net_shadow_adapter.py` | 26125 | `be23986b0fb9b111e290357a81b356c521c1d4cf` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/canonical/adapters/already_net_shadow_adapter_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/canonical/adapters/q10_index_reaction_adapter.py` | 25912 | `ccf89a1f4842e48e2f76119cc47e6887d9ecbbab` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/canonical/adapters/q10_index_reaction_adapter_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/canonical/adapters/q10_semiconductor.py` | 25813 | `03b8c7b7c3ea699085f2c3ac30084ac71c29749a` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/canonical/adapters/q10_semiconductor_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/q16_proxy_rejection_review.py` | 25234 | `09467b4d9f48aff4acdd0ed31b20357c56786e61` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/q16_proxy_rejection_review_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/canonical/adapters/q9_horizon_exit_adapter.py` | 23642 | `5f4ee0e2a4000763ab1072db099de5ce03e3afa2` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/canonical/adapters/q9_horizon_exit_adapter_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/canonical/metrics/engine.py` | 23416 | `2518b92374b85529c5feb4cece9af48f9c111e44` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/canonical/metrics/engine_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/uef5/candle_authority.py` | 23153 | `1f6a5a8aa4b7c67c542c3a6cd50cb5ebed0fab3f` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/uef5/candle_authority_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/loss_decomposition.py` | 22780 | `87544f1ad77e164389fce354c02680d70b98f7f7` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/loss_decomposition_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/canonical/adapters/q10_index_directional_shadow_adapter.py` | 22673 | `c11ee9d9aa124da08cca1778ad3c225b9c7cedfb` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/canonical/adapters/q10_index_directional_shadow_adapter_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/uef5_3/dual_run.py` | 22159 | `1a179f78c73a71b68156c9c5208b965197f60427` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/uef5_3/dual_run_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/canonical/metrics/aggregation.py` | 21410 | `23d98818996caee86fee33b9f7b4e9bd6cd145e4` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/canonical/metrics/aggregation_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/scanner_alignment_root_cause.py` | 20444 | `8774bea29dd8ebd83283b28c5109e5fc6210fd1a` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/scanner_alignment_root_cause_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/evaluation/entry_timing_attribution.py` | 20050 | `a7559c358b7ff8e6048586ba1d42a97480ad3c79` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/evaluation/entry_timing_attribution_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/reporting/evaluation/__init__.py` → `libs/reporting/evaluation/__init__.py` | 200 | `fb691f9863bc` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/agent_effectiveness_scorecard.py` → `libs/reporting/evaluation/agent_effectiveness_scorecard.py` | 12747 | `16b501782427` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/artifact_inventory.py` → `libs/reporting/evaluation/artifact_inventory.py` | 18239 | `e2ec5c448448` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/attribution_score_range.py` → `libs/reporting/evaluation/attribution_score_range.py` | 10502 | `ea17c616ea00` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/attribution_score_v0.py` → `libs/reporting/evaluation/attribution_score_v0.py` | 13158 | `a7a47252a2b7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/attribution_score_window.py` → `libs/reporting/evaluation/attribution_score_window.py` | 9823 | `7deb1f069b47` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/__init__.py` → `libs/reporting/evaluation/canonical/__init__.py` | 3994 | `23a6c6e06d09` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/adapters/__init__.py` → `libs/reporting/evaluation/canonical/adapters/__init__.py` | 1072 | `8b76b9f33aa4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/adapters/already_net_shadow_adapter.py` → `libs/reporting/evaluation/canonical/adapters/already_net_shadow_adapter.py` | 26125 | `be23986b0fb9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/adapters/forward_measurement_adapter.py` → `libs/reporting/evaluation/canonical/adapters/forward_measurement_adapter.py` | 11597 | `67b6e4ea51b4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/adapters/hypothesis_forward_adapter.py` → `libs/reporting/evaluation/canonical/adapters/hypothesis_forward_adapter.py` | 16245 | `555315f0523b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/adapters/opening_rank1_shadow.py` → `libs/reporting/evaluation/canonical/adapters/opening_rank1_shadow.py` | 28727 | `2ac0c06728b5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/adapters/q10_index_directional_shadow_adapter.py` → `libs/reporting/evaluation/canonical/adapters/q10_index_directional_shadow_adapter.py` | 22673 | `c11ee9d9aa12` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/adapters/q10_index_reaction_adapter.py` → `libs/reporting/evaluation/canonical/adapters/q10_index_reaction_adapter.py` | 25912 | `ccf89a1f4842` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/adapters/q10_semiconductor.py` → `libs/reporting/evaluation/canonical/adapters/q10_semiconductor.py` | 25813 | `03b8c7b7c3ea` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/adapters/q12_baseline_btc_woori.py` → `libs/reporting/evaluation/canonical/adapters/q12_baseline_btc_woori.py` | 14815 | `adb90f4eb082` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/adapters/q9_horizon_exit_adapter.py` → `libs/reporting/evaluation/canonical/adapters/q9_horizon_exit_adapter.py` | 23642 | `5f4ee0e2a400` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/adapters/virtual_probe_adapter.py` → `libs/reporting/evaluation/canonical/adapters/virtual_probe_adapter.py` | 28973 | `4a10fa771d0e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/adapters/vnext_completeness_adapter.py` → `libs/reporting/evaluation/canonical/adapters/vnext_completeness_adapter.py` | 18714 | `d522a2b7c57e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/contracts.py` → `libs/reporting/evaluation/canonical/contracts.py` | 9254 | `8bfc83b06ff5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/forward/__init__.py` → `libs/reporting/evaluation/canonical/forward/__init__.py` | 2965 | `2317c4c4130a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/forward/contracts.py` → `libs/reporting/evaluation/canonical/forward/contracts.py` | 14293 | `8cb533549651` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/forward/engine.py` → `libs/reporting/evaluation/canonical/forward/engine.py` | 38904 | `102831ee19f9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/forward/policy.py` → `libs/reporting/evaluation/canonical/forward/policy.py` | 34008 | `893409c731fa` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/forward/profiles.py` → `libs/reporting/evaluation/canonical/forward/profiles.py` | 42498 | `4fbb1216e24b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/identity.py` → `libs/reporting/evaluation/canonical/identity.py` | 32323 | `222d72730fe3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/metrics/__init__.py` → `libs/reporting/evaluation/canonical/metrics/__init__.py` | 2682 | `3e32a67d68b9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/metrics/aggregation.py` → `libs/reporting/evaluation/canonical/metrics/aggregation.py` | 21410 | `23d98818996c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/metrics/contracts.py` → `libs/reporting/evaluation/canonical/metrics/contracts.py` | 18155 | `96fa8436d6f1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/metrics/engine.py` → `libs/reporting/evaluation/canonical/metrics/engine.py` | 23416 | `2518b92374b8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/metrics/policy.py` → `libs/reporting/evaluation/canonical/metrics/policy.py` | 60287 | `37a213c5f470` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/record.py` → `libs/reporting/evaluation/canonical/record.py` | 52066 | `85f32c16914f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/canonical/relations.py` → `libs/reporting/evaluation/canonical/relations.py` | 10752 | `e1df08643d6e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/contracts.py` → `libs/reporting/evaluation/contracts.py` | 1892 | `de66fd1209d8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/cost_basis_comparison.py` → `libs/reporting/evaluation/cost_basis_comparison.py` | 9481 | `d6ceae367fea` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/counterfactuals.py` → `libs/reporting/evaluation/counterfactuals.py` | 2909 | `8429cf73588f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/cumulative_improvement_review.py` → `libs/reporting/evaluation/cumulative_improvement_review.py` | 17404 | `a2f64696546c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/daily_scorecard.py` → `libs/reporting/evaluation/daily_scorecard.py` | 4948 | `9c09b97144ce` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/daily_uef_pipeline.py` → `libs/reporting/evaluation/daily_uef_pipeline.py` | 45711 | `8909111a9844` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/day_validity.py` → `libs/reporting/evaluation/day_validity.py` | 8867 | `67923fe98c0d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/entry_timing_attribution.py` → `libs/reporting/evaluation/entry_timing_attribution.py` | 20050 | `a7559c358b7f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/episode_scanner_review.py` → `libs/reporting/evaluation/episode_scanner_review.py` | 13204 | `5bd42ffafd07` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/evaluation_lens_report.py` → `libs/reporting/evaluation/evaluation_lens_report.py` | 27561 | `cade83e2c18a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/feedback_effectiveness.py` → `libs/reporting/evaluation/feedback_effectiveness.py` | 3085 | `f12cec33f28a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/five_day_freeze.py` → `libs/reporting/evaluation/five_day_freeze.py` | 2113 | `824318af6d03` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/frozen_window_closeout.py` → `libs/reporting/evaluation/frozen_window_closeout.py` | 14016 | `0da35b93945e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/full_chain_component_review.py` → `libs/reporting/evaluation/full_chain_component_review.py` | 43029 | `dc1e6c5017e5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/historical_prior.py` → `libs/reporting/evaluation/historical_prior.py` | 12105 | `6adbc1e96e1f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/horizon_alignment.py` → `libs/reporting/evaluation/horizon_alignment.py` | 14920 | `c41a0b655071` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/horizon_compliance_report.py` → `libs/reporting/evaluation/horizon_compliance_report.py` | 7655 | `e4d6325a8f7d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/horizon_contract.py` → `libs/reporting/evaluation/horizon_contract.py` | 10906 | `86e423583ab4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/loss_decomposition.py` → `libs/reporting/evaluation/loss_decomposition.py` | 22780 | `87544f1ad77e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/markdown.py` → `libs/reporting/evaluation/markdown.py` | 4110 | `18319b98d064` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/memory_review/__init__.py` → `libs/reporting/evaluation/memory_review/__init__.py` | 105 | `8d360bd02db0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/memory_review/classifier.py` → `libs/reporting/evaluation/memory_review/classifier.py` | 10940 | `5b998594c940` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/memory_review/contracts.py` → `libs/reporting/evaluation/memory_review/contracts.py` | 481 | `57d87534b19a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/memory_review/forward.py` → `libs/reporting/evaluation/memory_review/forward.py` | 9120 | `a098dcae6a71` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/memory_review/loaders.py` → `libs/reporting/evaluation/memory_review/loaders.py` | 6215 | `d480564fa533` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/memory_review/pipeline.py` → `libs/reporting/evaluation/memory_review/pipeline.py` | 4985 | `cfc3c5b4b400` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/memory_review/report.py` → `libs/reporting/evaluation/memory_review/report.py` | 8635 | `afb6fdd4fd70` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/metrics.py` → `libs/reporting/evaluation/metrics.py` | 1293 | `6427c295f42a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/monitor_noop_attribution/__init__.py` → `libs/reporting/evaluation/monitor_noop_attribution/__init__.py` | 99 | `21fde3836e94` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/monitor_noop_attribution/contracts.py` → `libs/reporting/evaluation/monitor_noop_attribution/contracts.py` | 1055 | `ac5e33a5d021` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/monitor_noop_attribution/episodes.py` → `libs/reporting/evaluation/monitor_noop_attribution/episodes.py` | 5577 | `55c85fa87f46` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/monitor_noop_attribution/pipeline.py` → `libs/reporting/evaluation/monitor_noop_attribution/pipeline.py` | 4583 | `e89be9783281` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/monitor_noop_attribution/report.py` → `libs/reporting/evaluation/monitor_noop_attribution/report.py` | 7408 | `05b685b39ff1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/no_trade_attribution.py` → `libs/reporting/evaluation/no_trade_attribution.py` | 16371 | `967aca16db29` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/operator_summary_mining.py` → `libs/reporting/evaluation/operator_summary_mining.py` | 19758 | `1c05a5a64941` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/pipeline.py` → `libs/reporting/evaluation/pipeline.py` | 15713 | `853e2bd2cf7c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/post_reclaim_shadow_review.py` → `libs/reporting/evaluation/post_reclaim_shadow_review.py` | 3708 | `99998254d8eb` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/q13_q14_validation.py` → `libs/reporting/evaluation/q13_q14_validation.py` | 13062 | `0c209fae4718` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/q16_proxy_rejection_review.py` → `libs/reporting/evaluation/q16_proxy_rejection_review.py` | 25234 | `09467b4d9f48` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/q9_artifact_repair.py` → `libs/reporting/evaluation/q9_artifact_repair.py` | 18325 | `aa02d22f1444` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/rolling_scorecard.py` → `libs/reporting/evaluation/rolling_scorecard.py` | 2626 | `eb3b03478376` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/same_symbol_sequences/__init__.py` → `libs/reporting/evaluation/same_symbol_sequences/__init__.py` | 111 | `8409f3676341` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/same_symbol_sequences/builder.py` → `libs/reporting/evaluation/same_symbol_sequences/builder.py` | 8992 | `5c49c05a4eb1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/same_symbol_sequences/pipeline.py` → `libs/reporting/evaluation/same_symbol_sequences/pipeline.py` | 4406 | `8abe6cc3a226` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/scanner_alignment_root_cause.py` → `libs/reporting/evaluation/scanner_alignment_root_cause.py` | 20444 | `8774bea29dd8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/scanner_quality.py` → `libs/reporting/evaluation/scanner_quality.py` | 7625 | `5d36b62d61fc` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/scanner_score_decomposition.py` → `libs/reporting/evaluation/scanner_score_decomposition.py` | 4087 | `52223768fde2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/selection_authority_audit.py` → `libs/reporting/evaluation/selection_authority_audit.py` | 5539 | `7f139a43a46a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/stage2_authority/__init__.py` → `libs/reporting/evaluation/stage2_authority/__init__.py` | 177 | `b9499400a390` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/stage2_authority/builder.py` → `libs/reporting/evaluation/stage2_authority/builder.py` | 16603 | `7b98409945a7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/stage2_authority/contracts.py` → `libs/reporting/evaluation/stage2_authority/contracts.py` | 3599 | `1157585b49a6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/stage2_authority/deep_dive.py` → `libs/reporting/evaluation/stage2_authority/deep_dive.py` | 18187 | `bcaaa84eea83` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/stage2_authority/deep_dive_report.py` → `libs/reporting/evaluation/stage2_authority/deep_dive_report.py` | 8337 | `e787812e1810` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/stage2_authority/loaders.py` → `libs/reporting/evaluation/stage2_authority/loaders.py` | 3355 | `a3d6e6fe20ba` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/stage2_authority/pipeline.py` → `libs/reporting/evaluation/stage2_authority/pipeline.py` | 5967 | `76939b24a54b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/stage2_authority/report.py` → `libs/reporting/evaluation/stage2_authority/report.py` | 3213 | `ff965bb0ed75` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/start_gate.py` → `libs/reporting/evaluation/start_gate.py` | 13498 | `a449b5f599da` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/strategist_effectiveness.py` → `libs/reporting/evaluation/strategist_effectiveness.py` | 4586 | `f36cc0beef1a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/trade_evaluator.py` → `libs/reporting/evaluation/trade_evaluator.py` | 5515 | `8ee553781321` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/trade_read_model.py` → `libs/reporting/evaluation/trade_read_model.py` | 32723 | `2f4217f3a19b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef5/__init__.py` → `libs/reporting/evaluation/uef5/__init__.py` | 262 | `c3a08edd7f5b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef5/candle_authority.py` → `libs/reporting/evaluation/uef5/candle_authority.py` | 23153 | `1f6a5a8aa4b7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef5/clean_evidence_coverage.py` → `libs/reporting/evaluation/uef5/clean_evidence_coverage.py` | 19618 | `9a650f545e2d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef5/clean_evidence_registry.py` → `libs/reporting/evaluation/uef5/clean_evidence_registry.py` | 31249 | `fa66ec2eeda4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef5/clean_evidence_rules.py` → `libs/reporting/evaluation/uef5/clean_evidence_rules.py` | 41630 | `e378ea883f1c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef5/historical_recompute.py` → `libs/reporting/evaluation/uef5/historical_recompute.py` | 78065 | `719101c37fca` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef5/session_policy.py` → `libs/reporting/evaluation/uef5/session_policy.py` | 4681 | `c9bd221211d9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef5_3/__init__.py` → `libs/reporting/evaluation/uef5_3/__init__.py` | 1123 | `8a68623a055d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef5_3/canonical_run.py` → `libs/reporting/evaluation/uef5_3/canonical_run.py` | 13892 | `dad204394fb9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef5_3/comparison_unit.py` → `libs/reporting/evaluation/uef5_3/comparison_unit.py` | 4689 | `3277e12b48a3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef5_3/divergence_classifier.py` → `libs/reporting/evaluation/uef5_3/divergence_classifier.py` | 39105 | `5f2d84cb5646` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef5_3/dual_run.py` → `libs/reporting/evaluation/uef5_3/dual_run.py` | 22159 | `1a179f78c73a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef5_3/legacy_forward_returns.py` → `libs/reporting/evaluation/uef5_3/legacy_forward_returns.py` | 7017 | `34a92d4d5cbf` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef5_3/legacy_opportunity_engine.py` → `libs/reporting/evaluation/uef5_3/legacy_opportunity_engine.py` | 5433 | `dc6982b7c6fd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef5_3/taxonomy.py` → `libs/reporting/evaluation/uef5_3/taxonomy.py` | 2031 | `c06f73c7b412` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef6/__init__.py` → `libs/reporting/evaluation/uef6/__init__.py` | 861 | `93fb36abc426` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef6/lineage_coverage.py` → `libs/reporting/evaluation/uef6/lineage_coverage.py` | 16645 | `6738abb8f9de` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef6/lineage_model.py` → `libs/reporting/evaluation/uef6/lineage_model.py` | 7107 | `234783d68860` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef6/lineage_verify.py` → `libs/reporting/evaluation/uef6/lineage_verify.py` | 3832 | `48429e894d05` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef6/lineage_witness.py` → `libs/reporting/evaluation/uef6/lineage_witness.py` | 10982 | `1783878893ef` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef6/loader.py` → `libs/reporting/evaluation/uef6/loader.py` | 2626 | `28a631342d51` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef6/population_dedup.py` → `libs/reporting/evaluation/uef6/population_dedup.py` | 15554 | `b4b21b714678` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef6/report_model.py` → `libs/reporting/evaluation/uef6/report_model.py` | 4312 | `8b6d9a165634` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef6/reporter.py` → `libs/reporting/evaluation/uef6/reporter.py` | 3540 | `730df2a3e777` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef6/run_identity.py` → `libs/reporting/evaluation/uef6/run_identity.py` | 2823 | `13e760c89501` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `libs/reporting/evaluation/uef6/run_uef6a.py` → `libs/reporting/evaluation/uef6/run_uef6a.py` | 3352 | `8b9283f3c37c` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `libs/reporting/evaluation/uef6/validation_replay.py` → `libs/reporting/evaluation/uef6/validation_replay.py` | 17010 | `076cedab0158` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef7/__init__.py` → `libs/reporting/evaluation/uef7/__init__.py` | 718 | `8c816182d07d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef7/alpha_board_normalization.py` → `libs/reporting/evaluation/uef7/alpha_board_normalization.py` | 16446 | `0fbb3345f74f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef7/model.py` → `libs/reporting/evaluation/uef7/model.py` | 9503 | `968ef6b9ed97` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef7/reporter.py` → `libs/reporting/evaluation/uef7/reporter.py` | 2696 | `2ddaf7f69e40` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef7/run_identity.py` → `libs/reporting/evaluation/uef7/run_identity.py` | 4128 | `ec6756229911` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `libs/reporting/evaluation/uef8/__init__.py` → `libs/reporting/evaluation/uef8/__init__.py` | 743 | `4de2e42af8c1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef8/fair_comparison.py` → `libs/reporting/evaluation/uef8/fair_comparison.py` | 14129 | `a2fab9e96fd2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef8/model.py` → `libs/reporting/evaluation/uef8/model.py` | 7156 | `eb9b784b078e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef8/reporter.py` → `libs/reporting/evaluation/uef8/reporter.py` | 2312 | `50bb3024270f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef8/run_identity.py` → `libs/reporting/evaluation/uef8/run_identity.py` | 2779 | `dcdcb7ed631a` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `libs/reporting/evaluation/uef9/__init__.py` → `libs/reporting/evaluation/uef9/__init__.py` | 161 | `57d8c18c3b79` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef9/authority.py` → `libs/reporting/evaluation/uef9/authority.py` | 11099 | `d7ba11a9c8fe` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef9/model.py` → `libs/reporting/evaluation/uef9/model.py` | 3094 | `edd084977a37` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef9/reporter.py` → `libs/reporting/evaluation/uef9/reporter.py` | 2120 | `d91b4246a752` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/evaluation/uef9/run_identity.py` → `libs/reporting/evaluation/uef9/run_identity.py` | 3147 | `199a873407ca` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
