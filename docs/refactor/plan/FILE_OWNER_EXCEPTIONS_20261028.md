# P1.5 신규 테스트 exact-path 단일 Owner 예외 (2026-10-28 C03→C05)

**결정:** [C03 #36 댓글 6465609676](https://github.com/hbombheart1230-dotcom/agentra/issues/36#issuecomment-6465609676). **확인 소스:** Claude A 원격 `39eaa4a0df1ec3c6148960d0aa8c0a58720d6bae` (10개 신규 테스트 blob). RF-074 원래 BASE `63182ab27ecf889768003f637a40577ba1277f86`의 75개 TEST_ORACLE 및 정규식은 변경하지 않는다.

**소유권 우선순위:** (1) 아래 신규 exact path 10개는 RF-031/RF-040에 단일 귀속, (2) 기존 BASE FILE_COVERAGE CSV의 75개 RF-074 파일은 그대로 RF-074, (3) 그 외 RF-074 broad regex는 후보 매칭일 뿐 다른 RF exact-path 소유권을 덮어쓰지 않는다. 이 규칙은 [FILE_COVERAGE CSV](FILE_COVERAGE_63182ab2.csv) 10개 신규 행과 함께 적용한다. 새 파일의 CSV `baseline_sha` 열은 기존 BASE 매핑 기준을 표시하며 **그 파일이 BASE에 존재했다는 뜻이 아니다**. 신규 행의 `UNVERIFIED`는 전체 C5/CI 검증 완료를 뜻하지 않는다.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf031_reporter_ai_review_contract.py` | RF-031 / Claude A |
| `tests/test_rf031_reporter_analysis_callers.py` | RF-031 / Claude A |
| `tests/test_rf031_reporter_analysis_writers.py` | RF-031 / Claude A |
| `tests/test_rf031_trade_report_runtime_generation_plan.py` | RF-031 / Claude A |
| `tests/test_rf031_trade_report_runtime_policy_contract.py` | RF-031 / Claude A |
| `tests/test_rf031_trade_story_human_payloads_contract.py` | RF-031 / Claude A |
| `tests/test_rf040_libs_agent_reporter_agent.py` | RF-040 / Claude A |
| `tests/test_rf040_libs_agent_reporter_dtos.py` | RF-040 / Claude A |
| `tests/test_rf040_libs_agent_reporter_hooks.py` | RF-040 / Claude A |
| `tests/test_rf040_libs_agent_reporter_result.py` | RF-040 / Claude A |

**C05 신규 exact-path 보강 (2026-10-28 20:52 KST):** A 원격 `3afbb9c6`의 RF-051 신규 테스트 2개 blob 확인, CSV 단일 Owner RF-051 귀속. RF-074 frozen 75 및 기존 10개 예외 불변. C03 [#36 `6468496083`](https://github.com/hbombheart1230-dotcom/agentra/issues/36#issuecomment-6468496083)에서 혼합 신규 테스트 2개 exact-path 단일 Owner 확정. 원격 A `3afbb9c6` blob `29a07609`/`b5d455e0` 확인, CSV 반영. validator NOT_RUN.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf051_libs_market_global_sentiment_signal_branches.py` | RF-051 / Claude A |
| `tests/test_rf051_libs_market_q10_collector_residual_contract.py` | RF-051 / Claude A |
| `tests/test_rf040_058_054_residual_gaps_contract.py` | RF-040 / Claude A |
| `tests/test_rf054_058_040_final_residual_contract.py` | RF-054 / Claude A |

**C05 신규 exact-path 3개 보강 (2026-10-28 23:50 KST):** A #11 `6471660140` 원격 `2445dbd5`의 3개 blob 확인. 기존 RF-031 exact-path 우선순위에 따라 RF-031 단일 Owner, RF-074 frozen 75개 불변. 정규식 validator 실제 실행은 NOT_RUN; 이 결정은 C5 전체 MET가 아니다.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf031_reporter_analysis_helpers_contract.py` | RF-031 / Claude A |
| `tests/test_rf031_reporter_analysis_optional_writers_contract.py` | RF-031 / Claude A |
| `tests/test_rf031_reporter_feedback_helpers_contract.py` | RF-031 / Claude A |

**C05 2026-10-29 00:50 KST 신규 exact-path 소유권:** A #11 `6473163851` 원격 `b203ad0108bc9f60b84c7f788a26b0c16ce83846` 신규 RF-031 3개와 B #12 `6472816538` 원격 `031de036ad826c92bb2c525012c22afe49b28c0c` 신규 RF-044 1개를 blob 조회 후 CSV 단일 소유로 확정. RF-031 세 경로는 RF-074 broad regex보다 exact-path가 우선하며 기존 frozen 75개 불변. RF-044 경로는 별도 owner로 귀속. 정규식 validator NOT_RUN, C5 전체 MET 아님.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf031_trade_report_deterministic_seed_contract.py` | RF-031 / Claude A |
| `tests/test_rf031_trade_report_compact_input_contract.py` | RF-031 / Claude A |
| `tests/test_rf031_trade_report_strategy_memory_labels_contract.py` | RF-031 / Claude A |
| `tests/test_rf044_executor_error_serialization.py` | RF-044 / Codex B |

**C05 2026-10-29 01:50 KST 추가 exact-path 판정:** A #11 `6474598614`·`6474606575` exact `a17be883681b1bfeb7dcc9f8632b833d3cf4b5b5`에서 이전 `b203ad01` 대비 신규 **3파일**(보고의 '4파일'은 commit diff 기준 정정), B #12 `6474340889` exact `daf50d88d1086844e7d20a75e75e9d3beaf07ce6` 신규 1파일. 4개 GitHub blob 검증, CSV 단일 Owner 4행 추가. RF-074 기존 75개 frozen test·regex 변경 없음. 정규식 validator 실행 NOT_RUN; 전체 C5 MET 아님.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf031_trade_report_ai_helpers_contract.py` | RF-031 / Claude A |
| `tests/test_rf031_trade_report_alias_modules_contract.py` | RF-031 / Claude A |
| `tests/test_rf031_trade_report_markdown_clean_wrappers_contract.py` | RF-031 / Claude A |
| `tests/test_rf066_temp_contamination_cleanup.py` | RF-066 / Codex B |

**C05 2026-10-29 02:50 KST 신규 exact-path 소유권:** B #12 `6475690024` 정확 `4b926c2e0544d6055356f78159d4c92b6f63f412`의 신규 테스트 1개(blob `5c15e24ccec16e9fcdf873328a225e92b7e10edc`)를 RF-066 단일 Owner로 확정. RF-074 frozen 75·기존 regex 불변, validator NOT_RUN, C5 전체 MET 아님.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf066_q9_compaction_exception.py` | RF-066 / Codex B |

**검증 경계:** C05가 위 원격 A 10개 blob·CSV 경로 유일성·RF 원본을 대조했다. 기존 75 frozen test/regex rename·rewrite 0. 별도의 정규식 기반 자동 검사기가 CSV 우선순위를 실제로 구현/준수하는지 실행 검증은 **NOT_RUN**이다. 해당 검증기가 exact-path 예외를 무시하면 소유권 검사 적용은 **BLOCKED**, 지팀장 승인 하에 validator 예외 처리를 별도 작업해야 한다. 이 예외 자체는 RF-031/040/054/058/074 C5 MET, full opposite peer, CI 또는 DONE을 승인하지 않는다.
