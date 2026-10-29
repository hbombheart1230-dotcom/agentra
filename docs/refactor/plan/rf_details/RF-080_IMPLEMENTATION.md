# RF-080 — 코드 구조/함수 재배치 설계 (T06)

## T06 patch history OWNER 최종 판정
- docs/daily_patch/ and docs/trading_agent_patch_notes_detailed_update/: historical release/patch provenance; keep names and dates, do not rewrite history.
- Other owned docs retain domain directory and consumers. Existing file per-path SOURCE/TARGET table below is the authoritative scope.
- One-line KEEP_OK when link/owner correct, no code/tests or cosmetic relocation. No A/B doc edits.


**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-080.md` blob `01f667d24df300e516599b35162b163c93c87d54`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 313개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `docs/daily_patch/2026-04-29_strategy-conservatism-runtime-guards.md` → `docs/daily_patch/2026-04-29_strategy-conservatism-runtime-guards.md` | 3966 | `6bae8bf25044` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-04-30_entry-gate-reporting-memory-defaults.md` → `docs/daily_patch/2026-04-30_entry-gate-reporting-memory-defaults.md` | 19721 | `05551053bba3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-04_intraday-cash-truth-ai-report-check.md` → `docs/daily_patch/2026-05-04_intraday-cash-truth-ai-report-check.md` | 16062 | `575d89da3a74` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-05_truth-surface-summary-alignment.md` → `docs/daily_patch/2026-05-05_truth-surface-summary-alignment.md` | 4035 | `06888c18a54d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-06_today-run-gap-review.md` → `docs/daily_patch/2026-05-06_today-run-gap-review.md` | 14594 | `18b7df46fc0c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-06_trade-price-truth-refresh.md` → `docs/daily_patch/2026-05-06_trade-price-truth-refresh.md` | 17394 | `ffb6d72ce599` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-07_live-open-patch-verification.md` → `docs/daily_patch/2026-05-07_live-open-patch-verification.md` | 34450 | `34cfc8b6ba7e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-08_post-scanner-refresh-latency-fix.md` → `docs/daily_patch/2026-05-08_post-scanner-refresh-latency-fix.md` | 38216 | `eb29d32b0307` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-09_weekend-validation-report-regeneration-review.md` → `docs/daily_patch/2026-05-09_weekend-validation-report-regeneration-review.md` | 7397 | `fe8ef8a740c8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-11_pending-order-stale-guard.md` → `docs/daily_patch/2026-05-11_pending-order-stale-guard.md` | 35775 | `56d562430f6d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_candidate-cascade-expansion-hotfix.md` → `docs/daily_patch/2026-05-12_candidate-cascade-expansion-hotfix.md` | 2297 | `f3b70990da00` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_closeout-preflight-fallback.md` → `docs/daily_patch/2026-05-12_closeout-preflight-fallback.md` | 1974 | `844d41cb18d9` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_cost-floor-and-truth-surface-hotfix.md` → `docs/daily_patch/2026-05-12_cost-floor-and-truth-surface-hotfix.md` | 2596 | `3b3a9d4caebd` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_defensive-top3-and-repeat-loss-guard.md` → `docs/daily_patch/2026-05-12_defensive-top3-and-repeat-loss-guard.md` | 1582 | `7a71b431a20a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_etf-universe-and-deviation-signal.md` → `docs/daily_patch/2026-05-12_etf-universe-and-deviation-signal.md` | 2434 | `9c1d7e104c71` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_full-close-trade-report-gate.md` → `docs/daily_patch/2026-05-12_full-close-trade-report-gate.md` | 2966 | `d8f8c39c4ea3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_human-chart-guard-chartfit-horizon-alignment.md` → `docs/daily_patch/2026-05-12_human-chart-guard-chartfit-horizon-alignment.md` | 4061 | `23bd9e22a79b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_live-monitor-crash-hotfix.md` → `docs/daily_patch/2026-05-12_live-monitor-crash-hotfix.md` | 2039 | `2ac218cca6cd` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_llm-report-folder-dedup-and-trade-summary-copy.md` → `docs/daily_patch/2026-05-12_llm-report-folder-dedup-and-trade-summary-copy.md` | 2768 | `cf9cd80ce235` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_monitor-human-chart-positive-entry-setup.md` → `docs/daily_patch/2026-05-12_monitor-human-chart-positive-entry-setup.md` | 2005 | `89666f675a86` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_overnight-decision-report-clarity.md` → `docs/daily_patch/2026-05-12_overnight-decision-report-clarity.md` | 1653 | `59705d51b045` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_pending-exit-sell-guard.md` → `docs/daily_patch/2026-05-12_pending-exit-sell-guard.md` | 1859 | `365c3d388a8d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_recent-buy-fill-settle-sell-guard.md` → `docs/daily_patch/2026-05-12_recent-buy-fill-settle-sell-guard.md` | 1834 | `3c5b71799ffb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_same-day-summary-pnl-unknown-fix.md` → `docs/daily_patch/2026-05-12_same-day-summary-pnl-unknown-fix.md` | 1632 | `a616bf7a5919` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_scanner-macro-chartfit-monitor-quality.md` → `docs/daily_patch/2026-05-12_scanner-macro-chartfit-monitor-quality.md` | 4218 | `97bc60304d36` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_scanner-monitor-chart-fit-verification.md` → `docs/daily_patch/2026-05-12_scanner-monitor-chart-fit-verification.md` | 2759 | `07c3926d244f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_trade-summary-entry-vwap-volume-exit-distance.md` → `docs/daily_patch/2026-05-12_trade-summary-entry-vwap-volume-exit-distance.md` | 1166 | `2c95766fcfc8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-12_vwap-exit-fresh-minute-source-hotfix.md` → `docs/daily_patch/2026-05-12_vwap-exit-fresh-minute-source-hotfix.md` | 2209 | `fd19d4204cf2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-13_chart-positive-entry-and-cooldown-scope.md` → `docs/daily_patch/2026-05-13_chart-positive-entry-and-cooldown-scope.md` | 2825 | `0b37101cf3d3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-13_clean-live-session-restart-wrapper.md` → `docs/daily_patch/2026-05-13_clean-live-session-restart-wrapper.md` | 2330 | `75c69cf28f5b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-13_exit-trigger-execution-status-separation.md` → `docs/daily_patch/2026-05-13_exit-trigger-execution-status-separation.md` | 2167 | `ee2c25311e47` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-13_monitor-exit-theme-report-alignment.md` → `docs/daily_patch/2026-05-13_monitor-exit-theme-report-alignment.md` | 1680 | `893fe4cb6be3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-13_operator-summary-pattern-performance.md` → `docs/daily_patch/2026-05-13_operator-summary-pattern-performance.md` | 2681 | `3caccc96d2b8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-13_peak-profit-protection-report-evidence.md` → `docs/daily_patch/2026-05-13_peak-profit-protection-report-evidence.md` | 2962 | `9a3dfe373edd` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-13_pending-buy-human-chart-hard-guard.md` → `docs/daily_patch/2026-05-13_pending-buy-human-chart-hard-guard.md` | 2554 | `25370f256498` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-13_strategist-risk-tone-reporting-fix.md` → `docs/daily_patch/2026-05-13_strategist-risk-tone-reporting-fix.md` | 2665 | `0d227bc4b6c6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-13_strategist-summary-stage-meta-rendering-fix.md` → `docs/daily_patch/2026-05-13_strategist-summary-stage-meta-rendering-fix.md` | 2279 | `72ec8d6149a8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-13_time-limit-cost-floor-reassessment.md` → `docs/daily_patch/2026-05-13_time-limit-cost-floor-reassessment.md` | 2633 | `b7b0485879ea` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-13_trade-summary-entry-exit-evidence-lines.md` → `docs/daily_patch/2026-05-13_trade-summary-entry-exit-evidence-lines.md` | 1627 | `937cb14d6ee9` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-14_peak-drawdown-profit-protection-floor.md` → `docs/daily_patch/2026-05-14_peak-drawdown-profit-protection-floor.md` | 1188 | `e2723e87c9db` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-14_strategist-input-fingerprint-cache-gate.md` → `docs/daily_patch/2026-05-14_strategist-input-fingerprint-cache-gate.md` | 1322 | `2cca0e3eabe0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-14_strategist-llm-token-budget.md` → `docs/daily_patch/2026-05-14_strategist-llm-token-budget.md` | 1893 | `057d11753c87` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-14_vwap-reclaim-strategy-and-human-chart-entry-relaxation.md` → `docs/daily_patch/2026-05-14_vwap-reclaim-strategy-and-human-chart-entry-relaxation.md` | 5254 | `f4b6cad58bec` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-15_incremental-refactor-plan-start.md` → `docs/daily_patch/2026-05-15_incremental-refactor-plan-start.md` | 77465 | `d19f33d70f1d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-16_incremental-refactor-continuation.md` → `docs/daily_patch/2026-05-16_incremental-refactor-continuation.md` | 79776 | `660829c7a391` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-18_entry-cascade-hardblock-and-summary-average.md` → `docs/daily_patch/2026-05-18_entry-cascade-hardblock-and-summary-average.md` | 1453 | `bd85c787514b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-18_live-execution-reporting-boundary.md` → `docs/daily_patch/2026-05-18_live-execution-reporting-boundary.md` | 14669 | `6657b282312b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-18_reporting-hotspot-phase11-14.md` → `docs/daily_patch/2026-05-18_reporting-hotspot-phase11-14.md` | 27276 | `afcbf4b7a7d1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-20_quant-tactic-engine-q1.md` → `docs/daily_patch/2026-05-20_quant-tactic-engine-q1.md` | 1687 | `4b0d5f71b4a1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-20_quant-tactic-engine-q2.md` → `docs/daily_patch/2026-05-20_quant-tactic-engine-q2.md` | 2393 | `26162125159e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-20_quant-tactic-engine-q3.md` → `docs/daily_patch/2026-05-20_quant-tactic-engine-q3.md` | 1386 | `09f737b3f880` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-20_quant-tactic-engine-q4.md` → `docs/daily_patch/2026-05-20_quant-tactic-engine-q4.md` | 2199 | `4a0972574d39` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-20_quant-tactic-engine-q5.md` → `docs/daily_patch/2026-05-20_quant-tactic-engine-q5.md` | 2195 | `f3f8d99be193` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-20_quant-tactic-engine-q6.md` → `docs/daily_patch/2026-05-20_quant-tactic-engine-q6.md` | 2650 | `cc85d4707f29` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-20_quant-tactic-engine-q7-slice1.md` → `docs/daily_patch/2026-05-20_quant-tactic-engine-q7-slice1.md` | 1988 | `3b4cd06b7b43` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-20_quant-tactic-engine-q7-slice2.md` → `docs/daily_patch/2026-05-20_quant-tactic-engine-q7-slice2.md` | 2093 | `6479b1e9bd9c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-20_quant-tactic-engine-q7-slice3.md` → `docs/daily_patch/2026-05-20_quant-tactic-engine-q7-slice3.md` | 2060 | `525f388d1eb7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-21_close_review_and_q8_findings.md` → `docs/daily_patch/2026-05-21_close_review_and_q8_findings.md` | 6207 | `2c0ab4e33d14` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-21_post-exit-shadow-recap-closeout-fix.md` → `docs/daily_patch/2026-05-21_post-exit-shadow-recap-closeout-fix.md` | 2080 | `6ff0bcd93c93` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-21_quant-entry-enforcement.md` → `docs/daily_patch/2026-05-21_quant-entry-enforcement.md` | 1555 | `9c492ecfdd36` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-21_quant-tactic-engine-q7-residual-strategist-context.md` → `docs/daily_patch/2026-05-21_quant-tactic-engine-q7-residual-strategist-context.md` | 1829 | `65254dd69095` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-22_q8_report_integrity_and_bundle_latency.md` → `docs/daily_patch/2026-05-22_q8_report_integrity_and_bundle_latency.md` | 8877 | `ee20aab2f97b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-24_broker_alignment_at_report_generation.md` → `docs/daily_patch/2026-05-24_broker_alignment_at_report_generation.md` | 1716 | `301a77471b6c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-24_kiwoom_account_snapshot_archive.md` → `docs/daily_patch/2026-05-24_kiwoom_account_snapshot_archive.md` | 1094 | `c2d7df98ec07` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-24_preopen_carry_guard.md` → `docs/daily_patch/2026-05-24_preopen_carry_guard.md` | 1234 | `a600308ccad2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-24_q8_candidate_shadow_dataset.md` → `docs/daily_patch/2026-05-24_q8_candidate_shadow_dataset.md` | 2280 | `9f896614c6df` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-24_q8_truth_first_ka10170.md` → `docs/daily_patch/2026-05-24_q8_truth_first_ka10170.md` | 1813 | `96560934301c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-26_opening_momentum_probe_shadow.md` → `docs/daily_patch/2026-05-26_opening_momentum_probe_shadow.md` | 2803 | `8fdb9ef5431e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-26_q8_shadow_guard_count_fix.md` → `docs/daily_patch/2026-05-26_q8_shadow_guard_count_fix.md` | 1624 | `df13b92dca70` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-05-29_weekend_preparation.md` → `docs/daily_patch/2026-05-29_weekend_preparation.md` | 5796 | `cc1e8be82f1b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-06-01_q8_active_behavior_patch.md` → `docs/daily_patch/2026-06-01_q8_active_behavior_patch.md` | 1799 | `9b960f424b80` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-06-01_q8_cost_edge_promotion_state.md` → `docs/daily_patch/2026-06-01_q8_cost_edge_promotion_state.md` | 1399 | `37536302e45f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-07-31_scanner_market_candidates_and_q11_index_sanity.md` → `docs/daily_patch/2026-07-31_scanner_market_candidates_and_q11_index_sanity.md` | 3109 | `d69a464e024a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-21_q10_q11_q13_measurement_integrity.md` → `docs/daily_patch/2026-08-21_q10_q11_q13_measurement_integrity.md` | 2934 | `c16c8084c0e4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-21_q14_q18_measurement_integrity.md` → `docs/daily_patch/2026-08-21_q14_q18_measurement_integrity.md` | 4811 | `ef4fba546c00` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-24_preopen_and_baseline_observability.md` → `docs/daily_patch/2026-08-24_preopen_and_baseline_observability.md` | 2304 | `b6edebe3cba2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-25_q12_trend_and_rank1_observability.md` → `docs/daily_patch/2026-08-25_q12_trend_and_rank1_observability.md` | 1720 | `4fb51c35cad0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-26_ai_effectiveness_provenance.md` → `docs/daily_patch/2026-08-26_ai_effectiveness_provenance.md` | 2159 | `2bc58796bf3f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-26_closeout_review.md` → `docs/daily_patch/2026-08-26_closeout_review.md` | 5201 | `824305b004ed` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-26_opening_overshoot_snapshot_and_casebook.md` → `docs/daily_patch/2026-08-26_opening_overshoot_snapshot_and_casebook.md` | 3194 | `e6c6a207c47f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-27_alpha_research_board_v2.md` → `docs/daily_patch/2026-08-27_alpha_research_board_v2.md` | 1084 | `bebafb752b92` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-27_scheduled_intelligence_and_supervisor.md` → `docs/daily_patch/2026-08-27_scheduled_intelligence_and_supervisor.md` | 1112 | `0f8365993944` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-27_stage2_candidate_authority_review.md` → `docs/daily_patch/2026-08-27_stage2_candidate_authority_review.md` | 2960 | `1b4cdf7c2236` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-27_stage3_horizon_lineage.md` → `docs/daily_patch/2026-08-27_stage3_horizon_lineage.md` | 2504 | `6723c57532c8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-28_controlled_mock_four_lane_execution.md` → `docs/daily_patch/2026-08-28_controlled_mock_four_lane_execution.md` | 1213 | `61a2c44187eb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-28_q10_korea_lead_market_forward_validation.md` → `docs/daily_patch/2026-08-28_q10_korea_lead_market_forward_validation.md` | 1210 | `39a24e6e3744` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-28_q12_five_variable_hypothesis_validation.md` → `docs/daily_patch/2026-08-28_q12_five_variable_hypothesis_validation.md` | 1777 | `3e20125caed6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-28_scheduled_intelligence_detail_ui.md` → `docs/daily_patch/2026-08-28_scheduled_intelligence_detail_ui.md` | 1175 | `d25f9183dfcf` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-29_cloudflare_private_ingress.md` → `docs/daily_patch/2026-08-29_cloudflare_private_ingress.md` | 941 | `738620a529ad` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-30_operations_command_center.md` → `docs/daily_patch/2026-08-30_operations_command_center.md` | 589 | `90ad901a94c3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-30_scheduled_artifact_json_viewer.md` → `docs/daily_patch/2026-08-30_scheduled_artifact_json_viewer.md` | 996 | `8d83c653ec22` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-31_controlled_lane_observability_integrity.md` → `docs/daily_patch/2026-08-31_controlled_lane_observability_integrity.md` | 1777 | `52981e26a2c0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-31_opening_q10_q12_capture_alignment.md` → `docs/daily_patch/2026-08-31_opening_q10_q12_capture_alignment.md` | 3271 | `696953f325be` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-08-31_supervisor_modify_contract_gap.md` → `docs/daily_patch/2026-08-31_supervisor_modify_contract_gap.md` | 3116 | `99dcf688d846` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-01_opening_alpha_price_integrity.md` → `docs/daily_patch/2026-09-01_opening_alpha_price_integrity.md` | 3059 | `8b295fca73db` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-07_q10_vwap_and_opening_alpha_integrity.md` → `docs/daily_patch/2026-09-07_q10_vwap_and_opening_alpha_integrity.md` | 3731 | `80b9bc5a2bdc` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-08_opening_alpha_observation_integrity.md` → `docs/daily_patch/2026-09-08_opening_alpha_observation_integrity.md` | 3405 | `1007eb129618` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-09_evaluation_observability_and_opening_matrix.md` → `docs/daily_patch/2026-09-09_evaluation_observability_and_opening_matrix.md` | 3023 | `4a973180b800` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-09_exit_threshold_and_horizon_integrity.md` → `docs/daily_patch/2026-09-09_exit_threshold_and_horizon_integrity.md` | 1485 | `e832cf3bfbec` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-10_evaluation_closeout_integrity.md` → `docs/daily_patch/2026-09-10_evaluation_closeout_integrity.md` | 1598 | `149b28614f44` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-10_stale_expected_exit_quote_integrity.md` → `docs/daily_patch/2026-09-10_stale_expected_exit_quote_integrity.md` | 1628 | `8148db588e20` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-28_uef5_3_formal_freeze.md` → `docs/daily_patch/2026-09-28_uef5_3_formal_freeze.md` | 3715 | `e0d8a46efd48` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-28_uef5_formal_freeze_and_patch_backfill.md` → `docs/daily_patch/2026-09-28_uef5_formal_freeze_and_patch_backfill.md` | 5522 | `ea4728918cb2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-28_uef6_formal_freeze.md` → `docs/daily_patch/2026-09-28_uef6_formal_freeze.md` | 4560 | `51168c52b890` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-29_daily_uef_authority_closure.md` → `docs/daily_patch/2026-09-29_daily_uef_authority_closure.md` | 6433 | `cfc93544cb6a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-29_daily_uef_eod_wiring.md` → `docs/daily_patch/2026-09-29_daily_uef_eod_wiring.md` | 8416 | `5f6c8405a334` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-29_daily_uef_eod_wiring_fix2.md` → `docs/daily_patch/2026-09-29_daily_uef_eod_wiring_fix2.md` | 8010 | `6835459970ef` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-29_p1_3_pytest_harness_and_shutdown_safety_fixes.md` → `docs/daily_patch/2026-09-29_p1_3_pytest_harness_and_shutdown_safety_fixes.md` | 7805 | `1048fe6a4868` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-29_pytest_artifact_hygiene.md` → `docs/daily_patch/2026-09-29_pytest_artifact_hygiene.md` | 2104 | `2e5ebe254f09` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-29_uef7_formal_freeze.md` → `docs/daily_patch/2026-09-29_uef7_formal_freeze.md` | 3125 | `ebd81fae1471` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-29_uef8_formal_freeze.md` → `docs/daily_patch/2026-09-29_uef8_formal_freeze.md` | 3386 | `1ab6614fd943` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-29_uef9_uef_complete.md` → `docs/daily_patch/2026-09-29_uef9_uef_complete.md` | 3592 | `4b61cad1fbe5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-29_uef_p1_1_real_run_acceptance.md` → `docs/daily_patch/2026-09-29_uef_p1_1_real_run_acceptance.md` | 1495 | `3408dddcca9f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-30_closeout_diagnostic_hardening.md` → `docs/daily_patch/2026-09-30_closeout_diagnostic_hardening.md` | 8109 | `584b2322edc5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-30_closeout_single_owner_guard.md` → `docs/daily_patch/2026-09-30_closeout_single_owner_guard.md` | 5537 | `3abdfd1a3fc8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-30_closeout_strict_owner_lock_fix.md` → `docs/daily_patch/2026-09-30_closeout_strict_owner_lock_fix.md` | 5033 | `061ae22afbb4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-30_closeout_strict_release_identity_fix2.md` → `docs/daily_patch/2026-09-30_closeout_strict_release_identity_fix2.md` | 2219 | `bdc1608ffede` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-30_p1_2_daily_automation_integration.md` → `docs/daily_patch/2026-09-30_p1_2_daily_automation_integration.md` | 1558 | `a6c6050f3f3f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-30_p1_3_closed_read_write_gate_fix.md` → `docs/daily_patch/2026-09-30_p1_3_closed_read_write_gate_fix.md` | 6971 | `ef4d23549502` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-30_p1_3_docker_operational_acceptance.md` → `docs/daily_patch/2026-09-30_p1_3_docker_operational_acceptance.md` | 5146 | `163bd9d60d82` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-30_p1_3_docker_post_eod_final_acceptance.md` → `docs/daily_patch/2026-09-30_p1_3_docker_post_eod_final_acceptance.md` | 6221 | `ab8cc2a9f848` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-30_p1_3_eod_cascade_attempt_and_paper_pending.md` → `docs/daily_patch/2026-09-30_p1_3_eod_cascade_attempt_and_paper_pending.md` | 4727 | `1134ac416ca1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-30_p1_3_eod_cascade_confirmed_reachable_correction.md` → `docs/daily_patch/2026-09-30_p1_3_eod_cascade_confirmed_reachable_correction.md` | 5579 | `73e53c728502` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-09-30_p1_3_final_closure_paper_and_resource_benchmark.md` → `docs/daily_patch/2026-09-30_p1_3_final_closure_paper_and_resource_benchmark.md` | 7040 | `41385d400ac1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-01_host_runtime_pivot_final_ops_cleanup.md` → `docs/daily_patch/2026-10-01_host_runtime_pivot_final_ops_cleanup.md` | 13472 | `970ca78d45d0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-01_p1_2_idempotency_determinism_integration.md` → `docs/daily_patch/2026-10-01_p1_2_idempotency_determinism_integration.md` | 8462 | `0106a1b714f3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-01_storage_temp_artifact_hygiene.md` → `docs/daily_patch/2026-10-01_storage_temp_artifact_hygiene.md` | 1526 | `96349cacdd84` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-02_p1_3_production_docker_cutover.md` → `docs/daily_patch/2026-10-02_p1_3_production_docker_cutover.md` | 4986 | `ebff35e5754c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-02_p1_3_r1_r4_docker_restart_safety.md` → `docs/daily_patch/2026-10-02_p1_3_r1_r4_docker_restart_safety.md` | 8050 | `f81dee3d994e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-02_p1_3_r5_healthcheck_shutdown_recovery_matrix.md` → `docs/daily_patch/2026-10-02_p1_3_r5_healthcheck_shutdown_recovery_matrix.md` | 5874 | `84b2a8401b8b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-03_agentra_root_migration.md` → `docs/daily_patch/2026-10-03_agentra_root_migration.md` | 1104 | `d2268f48eac9` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-06_docker_live_open_and_daily_uef_freshness_incident.md` → `docs/daily_patch/2026-10-06_docker_live_open_and_daily_uef_freshness_incident.md` | 2503 | `d67612263a6e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-06_r6_1_scope_fix.md` → `docs/daily_patch/2026-10-06_r6_1_scope_fix.md` | 5573 | `13ffdf6bb40c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-06_r6_2_attempt_binding_and_lock_identity.md` → `docs/daily_patch/2026-10-06_r6_2_attempt_binding_and_lock_identity.md` | 4237 | `1235b1feb47b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-06_r6_immutable_readiness_evidence.md` → `docs/daily_patch/2026-10-06_r6_immutable_readiness_evidence.md` | 4923 | `dc34f49b12a6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-06_yfinance_dependency_restore.md` → `docs/daily_patch/2026-10-06_yfinance_dependency_restore.md` | 3677 | `f85eb5bd08ba` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_commander_runtime_p1_5_design_complete.md` → `docs/daily_patch/2026-10-07_commander_runtime_p1_5_design_complete.md` | 3483 | `de8d32d64cfb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_compatibility_wrapper_p1_5_design_complete.md` → `docs/daily_patch/2026-10-07_compatibility_wrapper_p1_5_design_complete.md` | 3432 | `efd275ef8307` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_documentation_refactor_start.md` → `docs/daily_patch/2026-10-07_documentation_refactor_start.md` | 1666 | `bdb3a018a5d7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_executor_p1_5_low_risk_design_complete.md` → `docs/daily_patch/2026-10-07_executor_p1_5_low_risk_design_complete.md` | 2862 | `957ee2335975` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_monitor_p1_5_design_complete.md` → `docs/daily_patch/2026-10-07_monitor_p1_5_design_complete.md` | 3689 | `5b76d33c5dd0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_operator_ui_brief_p1_5_design_complete.md` → `docs/daily_patch/2026-10-07_operator_ui_brief_p1_5_design_complete.md` | 2618 | `4e36671e6181` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_p1_3_closeout_memory_fix_and_production_deployment.md` → `docs/daily_patch/2026-10-07_p1_3_closeout_memory_fix_and_production_deployment.md` | 7907 | `e3e27adbf52a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_p1_5_1_reporting_dead_code_cleanup.md` → `docs/daily_patch/2026-10-07_p1_5_1_reporting_dead_code_cleanup.md` | 2246 | `b007c6aa7e45` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_p1_5_2_r2a_reporting_service_extraction.md` → `docs/daily_patch/2026-10-07_p1_5_2_r2a_reporting_service_extraction.md` | 8891 | `10be40b54ce2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_p1_5_2_r2b_markdown_decomposition.md` → `docs/daily_patch/2026-10-07_p1_5_2_r2b_markdown_decomposition.md` | 8113 | `cd7c70327957` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_p1_5_2_r2c_trade_story_decomposition.md` → `docs/daily_patch/2026-10-07_p1_5_2_r2c_trade_story_decomposition.md` | 3414 | `4847eba72bc7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_p1_5_full_regression_freeze_design_complete.md` → `docs/daily_patch/2026-10-07_p1_5_full_regression_freeze_design_complete.md` | 3618 | `6868d53f250b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_p1_5_p1_6_refactor_design_start.md` → `docs/daily_patch/2026-10-07_p1_5_p1_6_refactor_design_start.md` | 2120 | `197a21402eaf` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_p1_5_prep_closed.md` → `docs/daily_patch/2026-10-07_p1_5_prep_closed.md` | 4050 | `fb8531cf2b5b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_p1_5_strategist_deep_design.md` → `docs/daily_patch/2026-10-07_p1_5_strategist_deep_design.md` | 2151 | `0dabe98081b4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_reporting_p1_5_design_complete.md` → `docs/daily_patch/2026-10-07_reporting_p1_5_design_complete.md` | 1310 | `3651960069e7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_runtime_naming_p1_5_design_complete.md` → `docs/daily_patch/2026-10-07_runtime_naming_p1_5_design_complete.md` | 3489 | `2c8ee1fc95de` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_scanner_p1_5_design_complete.md` → `docs/daily_patch/2026-10-07_scanner_p1_5_design_complete.md` | 3187 | `cb87088b6ea5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_strategist_p1_5_design_complete.md` → `docs/daily_patch/2026-10-07_strategist_p1_5_design_complete.md` | 2010 | `2b7f2dd1ff85` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-07_strategist_p1_5_design_freeze.md` → `docs/daily_patch/2026-10-07_strategist_p1_5_design_freeze.md` | 1463 | `a70dce30c7ca` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-08_p1_2_p1_3_final_closure.md` → `docs/daily_patch/2026-10-08_p1_2_p1_3_final_closure.md` | 7170 | `46f1b82b6516` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-08_p1_5_1_to_11_responsibility_review.md` → `docs/daily_patch/2026-10-08_p1_5_1_to_11_responsibility_review.md` | 2317 | `3bea929927e8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-08_p1_5_2_r2c_residual_owners.md` → `docs/daily_patch/2026-10-08_p1_5_2_r2c_residual_owners.md` | 3885 | `026f4f0c3532` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-08_p1_5_2_reporting_design_v11.md` → `docs/daily_patch/2026-10-08_p1_5_2_reporting_design_v11.md` | 2157 | `a833e27eb4a4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-08_p1_5_reporting_branch_consolidation.md` → `docs/daily_patch/2026-10-08_p1_5_reporting_branch_consolidation.md` | 2317 | `5bc8a18f18bf` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_ai_facade_labels_35_36.md` → `docs/daily_patch/2026-10-09_p1_5_2_ai_facade_labels_35_36.md` | 1007 | `023ca3d9e3f1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_ai_facade_text_helpers_31.md` → `docs/daily_patch/2026-10-09_p1_5_2_ai_facade_text_helpers_31.md` | 905 | `7db07d43cf2c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_ai_service_loc_cap_fix.md` → `docs/daily_patch/2026-10-09_p1_5_2_ai_service_loc_cap_fix.md` | 409 | `70598e0bed02` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_evidence_owner_split_06.md` → `docs/daily_patch/2026-10-09_p1_5_2_evidence_owner_split_06.md` | 619 | `3f1758882316` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_facade_abi_authority_guard_34.md` → `docs/daily_patch/2026-10-09_p1_5_2_facade_abi_authority_guard_34.md` | 1003 | `f2ab03eac421` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_facade_static_consumer_evidence_26.md` → `docs/daily_patch/2026-10-09_p1_5_2_facade_static_consumer_evidence_26.md` | 1172 | `882cda39359e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_gpt_continuation_08_to_18_ci_accepted.md` → `docs/daily_patch/2026-10-09_p1_5_2_gpt_continuation_08_to_18_ci_accepted.md` | 1213 | `676ec19b8b9e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_gpt_direct_story_owner_10.md` → `docs/daily_patch/2026-10-09_p1_5_2_gpt_direct_story_owner_10.md` | 1021 | `106faed28252` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_gpt_facade_symbol_inventory_12.md` → `docs/daily_patch/2026-10-09_p1_5_2_gpt_facade_symbol_inventory_12.md` | 848 | `53870db5c597` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_gpt_implementation_verification_handoff.md` → `docs/daily_patch/2026-10-09_p1_5_2_gpt_implementation_verification_handoff.md` | 1000 | `c093762e96f5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_gpt_lifecycle_evidence_owner_11.md` → `docs/daily_patch/2026-10-09_p1_5_2_gpt_lifecycle_evidence_owner_11.md` | 1160 | `9c0f25ba7290` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_gpt_lifecycle_human_small_owner_08.md` → `docs/daily_patch/2026-10-09_p1_5_2_gpt_lifecycle_human_small_owner_08.md` | 1046 | `a07f2e383606` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_gpt_monitor_diagnostics_owner_13.md` → `docs/daily_patch/2026-10-09_p1_5_2_gpt_monitor_diagnostics_owner_13.md` | 896 | `26cdb7263667` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_gpt_monitor_entry_review_owner_18.md` → `docs/daily_patch/2026-10-09_p1_5_2_gpt_monitor_entry_review_owner_18.md` | 854 | `3ed13ba46c5d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_gpt_monitor_policy_bullets_17.md` → `docs/daily_patch/2026-10-09_p1_5_2_gpt_monitor_policy_bullets_17.md` | 782 | `067c4f9f5673` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_gpt_operator_language_owner_15.md` → `docs/daily_patch/2026-10-09_p1_5_2_gpt_operator_language_owner_15.md` | 973 | `470cf1b82c81` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_gpt_operator_phrase_owners_14.md` → `docs/daily_patch/2026-10-09_p1_5_2_gpt_operator_phrase_owners_14.md` | 1159 | `6abfc3a23fd6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_gpt_remote_source_audit.md` → `docs/daily_patch/2026-10-09_p1_5_2_gpt_remote_source_audit.md` | 937 | `6c164dcb3f0e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_gpt_story_provenance_owner_09.md` → `docs/daily_patch/2026-10-09_p1_5_2_gpt_story_provenance_owner_09.md` | 1076 | `7911a8c24dc5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_gpt_summary_findings_owner_16.md` → `docs/daily_patch/2026-10-09_p1_5_2_gpt_summary_findings_owner_16.md` | 849 | `94a3f60e0dfe` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_human_market_scanner_split_04.md` → `docs/daily_patch/2026-10-09_p1_5_2_human_market_scanner_split_04.md` | 576 | `34317f46dc74` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_input_main_builder_owner_24.md` → `docs/daily_patch/2026-10-09_p1_5_2_input_main_builder_owner_24.md` | 936 | `998dbaee005d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_markdown_clean_label_owner_32_33.md` → `docs/daily_patch/2026-10-09_p1_5_2_markdown_clean_label_owner_32_33.md` | 885 | `aa56c3e8356b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_markdown_clean_summary_language_30.md` → `docs/daily_patch/2026-10-09_p1_5_2_markdown_clean_summary_language_30.md` | 905 | `dab783ff55be` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_markdown_facade_main_renderer_25.md` → `docs/daily_patch/2026-10-09_p1_5_2_markdown_facade_main_renderer_25.md` | 1169 | `ce7760feb4e6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_markdown_render_section_owners_22.md` → `docs/daily_patch/2026-10-09_p1_5_2_markdown_render_section_owners_22.md` | 986 | `01ec50e192b7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_markdown_signals_split_05.md` → `docs/daily_patch/2026-10-09_p1_5_2_markdown_signals_split_05.md` | 639 | `2238d6017a8a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_monitor_context_split_19.md` → `docs/daily_patch/2026-10-09_p1_5_2_monitor_context_split_19.md` | 1096 | `c62c4f8cbbe1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_monitor_trace_wrapper_owner_21.md` → `docs/daily_patch/2026-10-09_p1_5_2_monitor_trace_wrapper_owner_21.md` | 1126 | `fb3a3d7cfaaa` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_owner_19_21_dependency_gate.md` → `docs/daily_patch/2026-10-09_p1_5_2_owner_19_21_dependency_gate.md` | 1262 | `c1d2cac7f15f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_owner_parity_guard.md` → `docs/daily_patch/2026-10-09_p1_5_2_owner_parity_guard.md` | 479 | `1068baea3a87` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_owner_parity_module_invocation_fix.md` → `docs/daily_patch/2026-10-09_p1_5_2_owner_parity_module_invocation_fix.md` | 460 | `8e7eea14f4bd` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_render_diagnostics_owner_20.md` → `docs/daily_patch/2026-10-09_p1_5_2_render_diagnostics_owner_20.md` | 1129 | `3033cf9224bd` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_sections_owner_split_01.md` → `docs/daily_patch/2026-10-09_p1_5_2_sections_owner_split_01.md` | 2446 | `1a126a5f8954` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_seed_import_repair.md` → `docs/daily_patch/2026-10-09_p1_5_2_seed_import_repair.md` | 617 | `8d202c7c549e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_seed_owner_split_02.md` → `docs/daily_patch/2026-10-09_p1_5_2_seed_owner_split_02.md` | 985 | `825813d6b023` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_service_owner_split_07.md` → `docs/daily_patch/2026-10-09_p1_5_2_service_owner_split_07.md` | 479 | `222b91457bf3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_story_assembly_owner_split_03.md` → `docs/daily_patch/2026-10-09_p1_5_2_story_assembly_owner_split_03.md` | 922 | `de012882d8cb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_story_contract_owner_29.md` → `docs/daily_patch/2026-10-09_p1_5_2_story_contract_owner_29.md` | 1197 | `b589b685732d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_story_facade_compatible_owners_27.md` → `docs/daily_patch/2026-10-09_p1_5_2_story_facade_compatible_owners_27.md` | 1328 | `f8505b8e3251` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_story_facade_human_judgments_28.md` → `docs/daily_patch/2026-10-09_p1_5_2_story_facade_human_judgments_28.md` | 1007 | `7f582c5a3a46` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_summary_input_contract_owners_23.md` → `docs/daily_patch/2026-10-09_p1_5_2_summary_input_contract_owners_23.md` | 988 | `241743aab8fb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_2_zip_upload_path_fix.md` → `docs/daily_patch/2026-10-09_p1_5_2_zip_upload_path_fix.md` | 500 | `288837b0fa0f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_git_driven_work_order_protocol.md` → `docs/daily_patch/2026-10-09_p1_5_git_driven_work_order_protocol.md` | 1937 | `d8685c55871e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-09_p1_5_small_owner_executor_design.md` → `docs/daily_patch/2026-10-09_p1_5_small_owner_executor_design.md` | 1925 | `48bf3b148556` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-10_p152_fast_parity_kit_005.md` → `docs/daily_patch/2026-10-10_p152_fast_parity_kit_005.md` | 959 | `0cc02ba86908` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-10_p152_integration_closeout_003.md` → `docs/daily_patch/2026-10-10_p152_integration_closeout_003.md` | 2479 | `0c1d5c5777c8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-10_p152_prelocal_remote_exhaustive_004.md` → `docs/daily_patch/2026-10-10_p152_prelocal_remote_exhaustive_004.md` | 5040 | `7ac450123ba1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-10_p1_5_2_ai_duration_language_owner_37.md` → `docs/daily_patch/2026-10-10_p1_5_2_ai_duration_language_owner_37.md` | 2159 | `01b4161849f7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-10_p1_5_2_markdown_news_headlines_owner_38.md` → `docs/daily_patch/2026-10-10_p1_5_2_markdown_news_headlines_owner_38.md` | 1926 | `999125806f9d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p152_guard007_pass_loc008_activation.md` → `docs/daily_patch/2026-10-12_p152_guard007_pass_loc008_activation.md` | 1026 | `1526f532898d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p152_loc008_audit_accepted_loc010_activated.md` → `docs/daily_patch/2026-10-12_p152_loc008_audit_accepted_loc010_activated.md` | 991 | `26f5686c5f00` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p152_loc008_codex_handoff.md` → `docs/daily_patch/2026-10-12_p152_loc008_codex_handoff.md` | 967 | `ad9044210106` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p152_loc010_codex_handoff.md` → `docs/daily_patch/2026-10-12_p152_loc010_codex_handoff.md` | 3932 | `d178adbcaf0d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p152_r3_audit_closeout.md` → `docs/daily_patch/2026-10-12_p152_r3_audit_closeout.md` | 433 | `2ac152d81a78` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p152_r3_claude_codex_git_first.md` → `docs/daily_patch/2026-10-12_p152_r3_claude_codex_git_first.md` | 2010 | `63d13860de26` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p152_r3_codex_audit_handoff.md` → `docs/daily_patch/2026-10-12_p152_r3_codex_audit_handoff.md` | 501 | `673afd893723` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p152_r3_codex_pass_with_findings.md` → `docs/daily_patch/2026-10-12_p152_r3_codex_pass_with_findings.md` | 492 | `11845271a2da` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p152_r3_codex_seam_audit_handoff.md` → `docs/daily_patch/2026-10-12_p152_r3_codex_seam_audit_handoff.md` | 669 | `81d5695ec128` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p152_r3_guard_audit_and_loc_reduction_queue.md` → `docs/daily_patch/2026-10-12_p152_r3_guard_audit_and_loc_reduction_queue.md` | 960 | `71a14f9af6fa` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p152_r3_harness_guard_task_activation.md` → `docs/daily_patch/2026-10-12_p152_r3_harness_guard_task_activation.md` | 470 | `6679a54b4158` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p152_r3_seam_restoration_decision.md` → `docs/daily_patch/2026-10-12_p152_r3_seam_restoration_decision.md` | 843 | `9b9c5b4f147c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p152_single_refactor_branch_policy.md` → `docs/daily_patch/2026-10-12_p152_single_refactor_branch_policy.md` | 711 | `d79a899d3d5e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p15_fast_track_first_pass_approved.md` → `docs/daily_patch/2026-10-12_p15_fast_track_first_pass_approved.md` | 1182 | `2674cd70dbe8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p1_5_2_codex_local_acceptance.md` → `docs/daily_patch/2026-10-12_p1_5_2_codex_local_acceptance.md` | 773 | `7e52b526de26` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p1_5_2_r3_acceptance_evidence_002.md` → `docs/daily_patch/2026-10-12_p1_5_2_r3_acceptance_evidence_002.md` | 395 | `13e1d1709ddb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p1_5_2_r3_compat_first_decomposition.md` → `docs/daily_patch/2026-10-12_p1_5_2_r3_compat_first_decomposition.md` | 482 | `c0fe5ac92b58` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p1_5_2_r3_facade_blocker.md` → `docs/daily_patch/2026-10-12_p1_5_2_r3_facade_blocker.md` | 417 | `c8e671f39f68` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p1_5_2_r3_facade_loc_008.md` → `docs/daily_patch/2026-10-12_p1_5_2_r3_facade_loc_008.md` | 367 | `67eb1c79a826` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p1_5_2_r3_facade_loc_010.md` → `docs/daily_patch/2026-10-12_p1_5_2_r3_facade_loc_010.md` | 370 | `723eecea6b9b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p1_5_2_r3_harness_guards_006.md` → `docs/daily_patch/2026-10-12_p1_5_2_r3_harness_guards_006.md` | 407 | `0326de150c58` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p1_5_2_r3_live_run_triage_005.md` → `docs/daily_patch/2026-10-12_p1_5_2_r3_live_run_triage_005.md` | 335 | `7c9ca0256c72` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p1_5_2_r3_use_time_seam_restoration.md` → `docs/daily_patch/2026-10-12_p1_5_2_r3_use_time_seam_restoration.md` | 392 | `996969ca421a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p1_5_fast_track_wave_a.md` → `docs/daily_patch/2026-10-12_p1_5_fast_track_wave_a.md` | 463 | `0fb0fd249e24` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p1_5_fast_track_wave_b.md` → `docs/daily_patch/2026-10-12_p1_5_fast_track_wave_b.md` | 498 | `4c2526985831` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p1_5_fast_track_wave_c.md` → `docs/daily_patch/2026-10-12_p1_5_fast_track_wave_c.md` | 368 | `8cf0da326b24` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p1_5_wave_a_closeout.md` → `docs/daily_patch/2026-10-12_p1_5_wave_a_closeout.md` | 329 | `2cea53598bbe` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p1_6_design_branch_prepared.md` → `docs/daily_patch/2026-10-12_p1_6_design_branch_prepared.md` | 890 | `02acbf3ecbd2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p1_6_detailed_design_completed.md` → `docs/daily_patch/2026-10-12_p1_6_detailed_design_completed.md` | 678 | `74e28c3eb415` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-12_p2_p8_architecture_branch_prepared.md` → `docs/daily_patch/2026-10-12_p2_p8_architecture_branch_prepared.md` | 1021 | `ed808fe36c06` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-13_p15_canonical_tree_reporter_as_is.md` → `docs/daily_patch/2026-10-13_p15_canonical_tree_reporter_as_is.md` | 659 | `e658c32697c6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-13_p15_third_pass_reporter_architecture.md` → `docs/daily_patch/2026-10-13_p15_third_pass_reporter_architecture.md` | 762 | `2f7465a8bd2b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-13_p15_tree_big_files_delete_audit.md` → `docs/daily_patch/2026-10-13_p15_tree_big_files_delete_audit.md` | 946 | `0639c23e27cc` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-13_p15_wave_d_after_full_modularization.md` → `docs/daily_patch/2026-10-13_p15_wave_d_after_full_modularization.md` | 714 | `6692908b9505` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-13_p1_5_parity_comparator_p1_fix.md` → `docs/daily_patch/2026-10-13_p1_5_parity_comparator_p1_fix.md` | 380 | `9b4d413297d4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-13_p1_5_parity_evidence_closure.md` → `docs/daily_patch/2026-10-13_p1_5_parity_evidence_closure.md` | 371 | `fcc92c7c4b3c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-13_p1_5_second_pass.md` → `docs/daily_patch/2026-10-13_p1_5_second_pass.md` | 336 | `c2a7afb65237` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-13_p1_5_third_pass_t0_t1.md` → `docs/daily_patch/2026-10-13_p1_5_third_pass_t0_t1.md` | 359 | `da6f650cd97d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-13_p1_5_third_pass_t1_evidence_closure.md` → `docs/daily_patch/2026-10-13_p1_5_third_pass_t1_evidence_closure.md` | 413 | `da644fd57f76` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-13_p1_5_third_pass_t2.md` → `docs/daily_patch/2026-10-13_p1_5_third_pass_t2.md` | 426 | `2cb704bdb961` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-13_p1_5_third_pass_t3.md` → `docs/daily_patch/2026-10-13_p1_5_third_pass_t3.md` | 424 | `7ae57ec7d838` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-13_p1_5_third_pass_t3_0_1.md` → `docs/daily_patch/2026-10-13_p1_5_third_pass_t3_0_1.md` | 422 | `f86ca9a05254` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-13_p1_5_third_pass_t3_0_2.md` → `docs/daily_patch/2026-10-13_p1_5_third_pass_t3_0_2.md` | 743 | `b5ac650af3cd` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-14_p1_5_t3_5_1.md` → `docs/daily_patch/2026-10-14_p1_5_t3_5_1.md` | 402 | `02a9c0b0dff3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-14_p1_5_t4_a.md` → `docs/daily_patch/2026-10-14_p1_5_t4_a.md` | 430 | `96a5f11bd509` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-14_p1_5_third_pass_t3_0_3.md` → `docs/daily_patch/2026-10-14_p1_5_third_pass_t3_0_3.md` | 468 | `9a994fe6599b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-14_p1_5_third_pass_t3_1.md` → `docs/daily_patch/2026-10-14_p1_5_third_pass_t3_1.md` | 553 | `bacf5110c7c6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-14_p1_5_third_pass_t3_2.md` → `docs/daily_patch/2026-10-14_p1_5_third_pass_t3_2.md` | 516 | `adae57cb1de9` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-14_p1_5_third_pass_t3_2_1.md` → `docs/daily_patch/2026-10-14_p1_5_third_pass_t3_2_1.md` | 492 | `a8382c1390a4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-14_p1_5_third_pass_t3_2_2.md` → `docs/daily_patch/2026-10-14_p1_5_third_pass_t3_2_2.md` | 437 | `a7a5dd2ff946` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-14_p1_5_third_pass_t3_5.md` → `docs/daily_patch/2026-10-14_p1_5_third_pass_t3_5.md` | 548 | `845a293893b2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_p15_codex_rework_p1_p2_fix.md` → `docs/daily_patch/2026-10-15_p15_codex_rework_p1_p2_fix.md` | 2470 | `714101e3a058` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_p15_consumer_inventory.md` → `docs/daily_patch/2026-10-15_p15_consumer_inventory.md` | 1057 | `dcc2c88beeb3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_p15_integrated_architecture_draft.md` → `docs/daily_patch/2026-10-15_p15_integrated_architecture_draft.md` | 740 | `ce87220a287f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_p15_integration_ci_preexisting_scope.md` → `docs/daily_patch/2026-10-15_p15_integration_ci_preexisting_scope.md` | 979 | `e60089e2360f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_p15_single_working_branch_scope_win_guard.md` → `docs/daily_patch/2026-10-15_p15_single_working_branch_scope_win_guard.md` | 1314 | `4105ad4d21cd` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_p15_t4_pr5_integration_start.md` → `docs/daily_patch/2026-10-15_p15_t4_pr5_integration_start.md` | 1202 | `b5344405b69c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_p1_5_architecture_visualization_gate.md` → `docs/daily_patch/2026-10-15_p1_5_architecture_visualization_gate.md` | 604 | `11c35ba53bf8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_p1_5_ci_main_transition.md` → `docs/daily_patch/2026-10-15_p1_5_ci_main_transition.md` | 322 | `18425da92965` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_p1_5_t4_a_1.md` → `docs/daily_patch/2026-10-15_p1_5_t4_a_1.md` | 451 | `8a4430160299` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_p1_5_t4_a_1_codex_accept.md` → `docs/daily_patch/2026-10-15_p1_5_t4_a_1_codex_accept.md` | 731 | `4a27f14d5ad7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_p1_5_t4_b.md` → `docs/daily_patch/2026-10-15_p1_5_t4_b.md` | 440 | `a27ed25d6fae` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_p1_5_t4_b_codex_accept_t4_c_go.md` → `docs/daily_patch/2026-10-15_p1_5_t4_b_codex_accept_t4_c_go.md` | 1013 | `1afbe7489d62` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_p1_5_t4_c.md` → `docs/daily_patch/2026-10-15_p1_5_t4_c.md` | 384 | `1396139d47e7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_p1_5_t4_c_codex_accept_t4_d_go.md` → `docs/daily_patch/2026-10-15_p1_5_t4_c_codex_accept_t4_d_go.md` | 1073 | `d89a42e51342` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_p1_5_t4_d.md` → `docs/daily_patch/2026-10-15_p1_5_t4_d.md` | 357 | `77fa2c637362` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_preserve_branch_unique_design_materials.md` → `docs/daily_patch/2026-10-15_preserve_branch_unique_design_materials.md` | 971 | `dea4fd870ea8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_reporting_relocation_batch1.md` → `docs/daily_patch/2026-10-15_reporting_relocation_batch1.md` | 665 | `532c3a31e946` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_reporting_relocation_batch2.md` → `docs/daily_patch/2026-10-15_reporting_relocation_batch2.md` | 934 | `5684cc4692e4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_reporting_t4_pr5_cleanup.md` → `docs/daily_patch/2026-10-15_reporting_t4_pr5_cleanup.md` | 703 | `d2f3913704a4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_scripts_bulk_migration.md` → `docs/daily_patch/2026-10-15_scripts_bulk_migration.md` | 1305 | `c64e4f46d5a2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_scripts_continuation_issue8.md` → `docs/daily_patch/2026-10-15_scripts_continuation_issue8.md` | 1505 | `b684efd4439c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_scripts_contract_ci_handoff.md` → `docs/daily_patch/2026-10-15_scripts_contract_ci_handoff.md` | 1255 | `5f4a1afc4bf7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_scripts_examples_migration.md` → `docs/daily_patch/2026-10-15_scripts_examples_migration.md` | 1434 | `1228a6597713` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_scripts_issue8_followup.md` → `docs/daily_patch/2026-10-15_scripts_issue8_followup.md` | 4227 | `f3e839d9359e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_scripts_issue8_iteration3.md` → `docs/daily_patch/2026-10-15_scripts_issue8_iteration3.md` | 2367 | `081cd8c757cd` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_scripts_wrapper_contract_audit.md` → `docs/daily_patch/2026-10-15_scripts_wrapper_contract_audit.md` | 742 | `51b5413daadb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_source_work_order01.md` → `docs/daily_patch/2026-10-15_source_work_order01.md` | 4203 | `5cf60d5e5663` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_source_work_order02.md` → `docs/daily_patch/2026-10-15_source_work_order02.md` | 5430 | `035eae9e349d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-15_source_work_order03.md` → `docs/daily_patch/2026-10-15_source_work_order03.md` | 5473 | `e4de5881d590` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-16_p15_058_v4_s1_integration.md` → `docs/daily_patch/2026-10-16_p15_058_v4_s1_integration.md` | 453 | `36808a51bcde` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-16_p15_test_harness_performance.md` → `docs/daily_patch/2026-10-16_p15_test_harness_performance.md` | 8773 | `6c5c234f5ec9` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-16_p15_tree_migration_v1_052.md` → `docs/daily_patch/2026-10-16_p15_tree_migration_v1_052.md` | 385 | `d479ccb6f09f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-16_p15_tree_migration_v2_053.md` → `docs/daily_patch/2026-10-16_p15_tree_migration_v2_053.md` | 454 | `30a1a2b62545` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-16_p15_tree_migration_v3_055.md` → `docs/daily_patch/2026-10-16_p15_tree_migration_v3_055.md` | 456 | `b9fce7321d13` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-16_p15_tree_migration_v4_056.md` → `docs/daily_patch/2026-10-16_p15_tree_migration_v4_056.md` | 455 | `2a2136ff5fb9` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-16_p15_tree_v3_freeze_and_v1_kickoff.md` → `docs/daily_patch/2026-10-16_p15_tree_v3_freeze_and_v1_kickoff.md` | 963 | `b88ff1bbf4c3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-16_p15_v2_053_order_published.md` → `docs/daily_patch/2026-10-16_p15_v2_053_order_published.md` | 1145 | `5e31a0d0cce0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-16_p15_v2_053_rework_054.md` → `docs/daily_patch/2026-10-16_p15_v2_053_rework_054.md` | 1046 | `e426291627f5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-16_p15_v2_codex_fail_rework_054.md` → `docs/daily_patch/2026-10-16_p15_v2_codex_fail_rework_054.md` | 847 | `c87d3f9aee25` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-16_v2_scoped_acceptance_v3_055_authorized.md` → `docs/daily_patch/2026-10-16_v2_scoped_acceptance_v3_055_authorized.md` | 666 | `b2b7e0331f79` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-16_v3_scoped_acceptance_v4_056_authorized.md` → `docs/daily_patch/2026-10-16_v3_scoped_acceptance_v4_056_authorized.md` | 963 | `da5061aeafe8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-17_p15_perf2a.md` → `docs/daily_patch/2026-10-17_p15_perf2a.md` | 6275 | `e89a11a8a7b3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-17_work_role_activation.md` → `docs/daily_patch/2026-10-17_work_role_activation.md` | 473 | `1ddb261d71c0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-18_codex_p15_p2_ci_portability.md` → `docs/daily_patch/2026-10-18_codex_p15_p2_ci_portability.md` | 1911 | `73091f7f6ffa` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-18_monitor_shared_candidate.md` → `docs/daily_patch/2026-10-18_monitor_shared_candidate.md` | 1844 | `edb6e72ce470` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-18_s5_shared_gate_preparation.md` → `docs/daily_patch/2026-10-18_s5_shared_gate_preparation.md` | 3008 | `f3511267e760` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/2026-10-18_uef9_synthetic_fixture.md` → `docs/daily_patch/2026-10-18_uef9_synthetic_fixture.md` | 1299 | `8f369c27560c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/daily_patch/README.md` → `docs/daily_patch/README.md` | 2306 | `3924bbbf923c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trading_agent_patch_notes_detailed_update/README.md` → `docs/trading_agent_patch_notes_detailed_update/README.md` | 2854 | `7ac045470dcf` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` → `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` | 653417 | `f035370b7f5d` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `docs/trading_agent_patch_notes_detailed_update/patch_notes.md` → `docs/trading_agent_patch_notes_detailed_update/patch_notes.md` | 392396 | `068f26a5c5d3` | KEEP_IF: 문서 참조·경로·내용 정본 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
