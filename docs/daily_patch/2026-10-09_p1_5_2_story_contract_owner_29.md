# P1.5.2 — Story Report Contract Owner 29 (2026-10-09)

- Baseline `df57b57acf6380174189ed4b69b3f9f92c638d02`, only `refactor/p1.5`.
- Eight original Story report metadata helpers moved behind original exact-name public wrappers: slug, feature_coverage, normalized_feature_coverage, confidence_label, execution_mode_label, classify_story_type, build_story_id, build_story_contract.
- libs/reporting/trade_story_facade_parts/story_contracts.py 162 physical LOC; public `trade_story_pipeline.py` 753->636 LOC. All 45 original top-level functions retained. Ledger updated for all 436 entries without DEAD declaration.
- Original eight AST bodies preserved, pinned in CI and matched against representative outputs. Call-time dependency injection preserves monkeypatches of `re`, `slug`, `feature_coverage`, `safe_int`, `safe_float`, `classify_story_type`, `execution_mode_label`.
- Expanded 25 bounded new Reporting Owners size/reverse-import/dependency DAG guard to **29**.
- This changes report-only execution mode display/classification, not Broker mode or execution authority. No UEF, R6.2, Step5C/D, Docker, Q12, production writes; Windows real report/LLM/full repo audit NOT RUN. P1.5.2 OPEN.
