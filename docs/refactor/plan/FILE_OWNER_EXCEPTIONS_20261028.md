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

**C05 신규 exact-path 보강 (2026-10-28 20:52 KST):** A 원격 `3afbb9c6`의 RF-051 신규 테스트 2개 blob 확인, CSV 단일 Owner RF-051 귀속. RF-074 frozen 75 및 기존 10개 예외 불변. 혼합 `tests/test_rf054_058_040_final_residual_contract.py`은 C03 Owner 결정 전 미귀속, validator NOT_RUN.

| 신규 exact path | 단일 Owner |
|---|---|
| `tests/test_rf051_libs_market_global_sentiment_signal_branches.py` | RF-051 / Claude A |
| `tests/test_rf051_libs_market_q10_collector_residual_contract.py` | RF-051 / Claude A |

**검증 경계:** C05가 위 원격 A 10개 blob·CSV 경로 유일성·RF 원본을 대조했다. 기존 75 frozen test/regex rename·rewrite 0. 별도의 정규식 기반 자동 검사기가 CSV 우선순위를 실제로 구현/준수하는지 실행 검증은 **NOT_RUN**이다. 해당 검증기가 exact-path 예외를 무시하면 소유권 검사 적용은 **BLOCKED**, 지팀장 승인 하에 validator 예외 처리를 별도 작업해야 한다. 이 예외 자체는 RF-031/040/074 C5 MET, full opposite peer, CI 또는 DONE을 승인하지 않는다.
