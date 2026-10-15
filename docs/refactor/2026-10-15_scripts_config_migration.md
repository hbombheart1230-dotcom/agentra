# Scripts / Config Inventory and Example Migration — 2026-10-15

## Scope and summary

- Branch: `refactor/agentra-target-tree`; base `57405608514c23d68f64b46e0e769467d5216cc5`; PR #5.
- T4 comparison: `4e242e5b1fc609b0ec012e0c6faed37b202e4aa0` from `refactor/p1.5`; merge base `2f95bba429636ee15ae9a399cc4ff7c4e6dcd5cb`.
- Scripts tracked baseline: **212 files**; after relocation: **216 files**, including legacy wrappers and two package markers. Three canonical files + one package marker are added; no existing CLI is removed.
- Reporting Batch 3 remains paused. No Reporting, operational launchers, Windows task definitions, Docker/CI commands, strategy parameters or config files changed.
- Evidence: `2026-10-15_scripts_config_inventory.json` contains every script, outgoing imports, incoming import/subprocess/test/CI/deploy/scheduler/docs references and line numbers. A static match is evidence of reference, not proof of deployed use.
- Baseline classification: OPERATIONS 48, DIAGNOSTICS 77, RESEARCH 60, MAINTENANCE 20, EXAMPLES 5, LEGACY_CANDIDATE 0, T4_OWNED 2.
- Post-move classification below includes 3 new canonical examples and their package marker.

| Category | Files |
| --- | --- |
| OPERATIONS | 48 |
| DIAGNOSTICS | 77 |
| RESEARCH | 60 |
| MAINTENANCE | 20 |
| EXAMPLES | 9 |
| LEGACY_CANDIDATE | 0 |
| T4_OWNED | 2 |

## Safety and compatibility

| Old CLI/module path (retained wrapper) | New canonical implementation |
| --- | --- |
| `scripts/demo_m22_skill_flow.py` | `scripts/examples/demo_m22_skill_flow.py` |
| `scripts/demo_m22_graph_with_hydration.py` | `scripts/examples/demo_m22_graph_with_hydration.py` |
| `scripts/demo_m7_dry_run_pipeline.py` | `scripts/examples/demo_m7_dry_run_pipeline.py` |

- Both M22 demos have test imports; graph hydration is also imported by `scripts/smoke_m22_hydration.py`, including private `_build_state`, `_strategist_passthrough`, `_to_summary`. Wrapper aliases the canonical module object, so private exports and monkeypatch targets remain identical. No caller rewrites.
- All three old paths have documentation references; no direct subprocess, tracked CI, Docker/deploy or Windows scheduler references were found for these three. External/manual use cannot be excluded, so retain wrappers anyway.
- M22 skill flow calls only Scanner/Monitor. M22 graph uses `graphs/nodes/executor_node.py`, a stub that sets `execution_pending=True` without order submission. M7 calls `OrderClient.dry_run_order(..., dry_run_token=True)`; no order send occurs.
- M14 order/quote-then-order and M15 approval demos may enter HTTP execution and are held as OPERATIONS, despite demo filenames. They are not moved or executed.
- Canonical M22 root discovery changes `parents[1]` → `parents[2]`. M7 gains the same root/sys.path bootstrap for direct-script invocation outside the repository. No chdir; existing M7 `./data/specs/api_catalog.demo.jsonl` remains relative to caller CWD.
- Source verification reverses ONLY the bootstrap edits and compares bytes against the original Git blob: all three match. Functions, CLI parsing, order gates, defaults and business logic are unchanged.
- Legacy wrappers: 15 lines each (45 total); new package marker: 1 line. Implementation bootstrap delta **+7 / -2 lines** (two replacements plus five M7 bootstrap additions); business logic changes **0 lines**. Raw Git code diff is +372/-321 because implementations are copied to canonical paths while old files remain wrappers; this is not a logic rewrite.

| Implementation | Original blob SHA | Original → canonical lines | Bootstrap +/- |
| --- | --- | --- | --- |
| `demo_m22_skill_flow` | `d5d1231e8f8b8fddf194524a1cf566d699cddb75` | 125 → 125 | +1/-1 |
| `demo_m22_graph_with_hydration` | `870c996c338bce513c81a062585a3a0e55e396eb` | 110 → 110 | +1/-1 |
| `demo_m7_dry_run_pipeline` | `4706758478a034215f1898d373ee7dc89b601603` | 98 → 103 | +5/-0 |

### Commands

```bash
# From repository root, both old and new commands remain supported:
.venv/bin/python scripts/demo_m22_skill_flow.py --json
.venv/bin/python scripts/examples/demo_m22_skill_flow.py --json
.venv/bin/python -m scripts.demo_m22_graph_with_hydration --json --simulate-timeout
.venv/bin/python -m scripts.examples.demo_m22_graph_with_hydration --json --simulate-timeout
# M7 writes a catalog relative to CWD: run validation from an isolated directory.
cd /tmp/agentra-script-migration/cwd
/workspace/agentra/.venv/bin/python /workspace/agentra/scripts/demo_m7_dry_run_pipeline.py
/workspace/agentra/.venv/bin/python /workspace/agentra/scripts/examples/demo_m7_dry_run_pipeline.py
```

These are compatibility commands, not authorization to run production schedules. Offline acceptance sets `SCANNER_FEATURE_SEED_WITH_YF=false`, `EXECUTION_ENABLED=false`, `ALLOW_REAL_EXECUTION=false`, `KIWOOM_MODE=mock`; those settings exist only in test subprocess environments. No saved operational policy changes.

## Validation

- Existing related pytest before and after: **20 passed** each (`test_m7_demo_catalog`, `test_m22_skill_native_scanner_monitor`, `test_m22_graph_hydration_wiring`, `test_m22_7_hydration_smoke_script`). Pytest cache and artifacts are under OS temp.
- Original CLI source retrieved byte-for-byte from base into `/tmp/agentra-script-migration/baseline`; baseline uses read-only links to the same config and API-spec inputs. No Git branch/worktree created.
- Original offline matrix: **34/34 exit 0**. Relocated legacy/canonical matrix: **68/68 exit 0 and equivalent** to original outputs after explicit clock-only normalization. Direct script and `-m` modes, repository and temporary CWD, M22 text/JSON/help/timeout cases, and M7 temporary-CWD execution are covered.
- Six clock-only fields below are normalized; all other stdout JSON/text, return codes and stderr must match. No semantic differences hidden.
  - `/monitor/exit_expected_exit_quote_age_sec`
  - `/monitor/exit_price_freshness/quote_age_sec`
  - `/monitor/exit_price_freshness/quote_observed_epoch`
  - `/monitor/minutes_to_close`
  - `/monitor/threshold_snapshot/expected_exit_quote_age_sec`
  - `/skill_fetch/ts_utc`
- Four additional M7 repository-CWD negative checks intentionally reject writes outside temp. They are isolation checks, not successful functional CLI runs. M7 functional runs use a temporary CWD and generated demo catalog.
- Initial exploratory runs exposed optional Yahoo fetch attempts and time-varying output; they are excluded from acceptance. Existing seed-disable override prevents Yahoo fetch in the final matrix. Python socket audit guard and temp-write guard remain active; no successful order or broker submission occurred.
- All three legacy module identities/private callable exports match canonical modules. Six additional direct-script checks (old/new × three scripts) passed from temp CWD with only the audit-guard directory on PYTHONPATH: repository sys.path bootstrap works without a repository PYTHONPATH binding.
- All 5 config skills load through `SkillRegistry().load()` without network. No config contents changed. Baseline snapshot and patch-note targeted pytest: **6 passed**, one dependency deprecation warning.
- No full repository suite, live execution, Windows Task Scheduler execution, Docker build, or full web build is required/run for these path-only changes. Static deployment references are retained; live Windows/CI state is not visible.

## Config inventory (8 files; no changes/deletions)

| Path | Decision | Role and evidence |
| --- | --- | --- |
| `config/.env.example` | KEEP | Operator template referenced by setup docs and env-contract tests; not automatically loaded as runtime `.env`. |
| `config/exam_strategy_baseline.yaml` | KEEP | Operator snapshot; required by `tests/test_m31_strategy_baseline_snapshot_yaml.py`; historical M31 baseline doc. |
| `config/strategy_v1_exam_baseline.json` | KEEP | Documented `regime_momentum_v1` exam manifest; `m31_operational_readiness_audit_2026-03-08.md` explicitly records that runtime does not auto-bind the manifest. |
| `config/skills/account.orders.yaml` | KEEP | Dynamic registry glob; account order DTO; skill docs and skill callers. |
| `config/skills/market.minute_ohlcv.yaml` | KEEP | Dynamic registry glob; monitor minute OHLCV; Kiwoom source inventory. |
| `config/skills/market.quote.yaml` | KEEP | Dynamic registry glob; quote DTO; Scanner/Monitor consumers. |
| `config/skills/order.place.yaml` | KEEP | Dynamic registry glob; order skill maps kt10000/kt10001. No direct filename reference is NOT evidence of unused config. |
| `config/skills/order.status.yaml` | KEEP | Dynamic registry glob; status/partial-fill DTO; skill docs and callers. |

- Dynamic path evidence: `libs/skills/registry.py` default `config/skills` and `glob("*.yaml")`; `libs/skills/runner.py` supports `SKILLS_DIR`. Relocation would require supported runtime overrides and deployment review, so none is proposed now.
- YAML and JSON share schema/baseline `m31.exam.baseline.2026-03-08` and primary strategy `regime_momentum_v1`. They differ in `reproducibility.locked_env_keys` (YAML also locks AI_STRATEGIST_MODEL) and the first three required report paths. They are NOT identical duplicates. No synchronization/value changes in this batch.
- Runtime strategy default is also `regime_momentum_v1` in `libs/strategies/v1/registry.py`, selected by policy/environment, with configuration from `libs/strategies/v1/config.py`. No live host environment was inspected or claimed to match the historical exam snapshot.
- Historical exam/test evidence is not a deletion criterion. KEEP 8, MOVE_CANDIDATE 0, DELETE_CANDIDATE 0, UNKNOWN 0 for config decisions. Runtime deployment-specific use beyond these static traces remains unverified.

## Legacy/deletion investigation

- **Safe-to-delete candidates: 0.** No files deleted. LEGACY_CANDIDATE category stays 0: lack of static refs alone does not establish that a manual CLI is obsolete.
- Files with no incoming tracked reference after relocation are listed below for operator/manual-schedule review only. Their deletion status is **UNKNOWN**, not unused. Metadata JSON retains outgoing imports even when incoming refs are empty.
- Keep `run_pytest.cmd/.ps1` and cleanup wrappers for Windows users; static absence does not permit deletion. Keep documented baseline manifests. Keep dangerous M14/M15 demos in place until a separate execution-safety review.

No-incoming-reference review list: 40 files. New `examples/__init__.py` is a package marker and is not a legacy executable.
- `scripts/__init__.py` — OPERATIONS, deletion UNKNOWN.
- `scripts/benchmark_operator_visibility_memory.py` — DIAGNOSTICS, deletion UNKNOWN.
- `scripts/cleanup_pytest_artifacts.cmd` — MAINTENANCE, deletion UNKNOWN.
- `scripts/cleanup_pytest_artifacts.ps1` — MAINTENANCE, deletion UNKNOWN.
- `scripts/collect_opening_rank1_symbol_metadata.py` — OPERATIONS, deletion UNKNOWN.
- `scripts/compact_q9_decision_windows.py` — MAINTENANCE, deletion UNKNOWN.
- `scripts/demo_m14_quote_then_order.py` — OPERATIONS, deletion UNKNOWN.
- `scripts/generate_operator_summary_report.py` — OPERATIONS, deletion UNKNOWN.
- `scripts/generate_symbol_trade_report.py` — OPERATIONS, deletion UNKNOWN.
- `scripts/repair_q9_day_artifacts.py` — MAINTENANCE, deletion UNKNOWN.
- `scripts/repair_trade_symbol_context.py` — MAINTENANCE, deletion UNKNOWN.
- `scripts/run_agent_effectiveness_scorecard.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_alpha_hypothesis_competition.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_attribution_score_range.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_conditional_alpha_diagnosis.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_evaluation_lens_report.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_existing_evidence_mining.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_full_chain_component_review.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_historical_q9_prior.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_horizon_alignment_review.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_integrated_trade_diagnosis.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_loss_decomposition.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_m15_matrix.py` — DIAGNOSTICS, deletion UNKNOWN.
- `scripts/run_market_regime_rail_review.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_monitor_noop_attribution.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_opening_rank1_deep_dive.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_opening_rank1_shadow.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_operator_summary_mining.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_pytest.cmd` — OPERATIONS, deletion UNKNOWN.
- `scripts/run_pytest.ps1` — OPERATIONS, deletion UNKNOWN.
- `scripts/run_q8_historical_review.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_q8_lane_decision_table.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_q8_shadow_blocker_review.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_same_symbol_sequence.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_scanner_alignment_root_cause_range.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_stage2_authority_review.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_structural_alpha_batch1.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_structural_alpha_batch2.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_uef6_dedup_detection.py` — RESEARCH, deletion UNKNOWN.
- `scripts/run_uef6_historical_validation.py` — RESEARCH, deletion UNKNOWN.

## T4 exclusion and shared-document constraint

- Current-tree T4_OWNED: `scripts/restart_live_session.py`, `scripts/run_session.py`. Both unchanged. T4 also adds scripts absent from this PR5 checkout; none are imported, copied or edited. Their exact paths are in the inventory JSON.
- All moved sources and new `scripts/examples/` destinations are outside T4 changed paths from the common merge base. Changed code/T4 intersection is **0**. Reporting files are not changed.
- Required UI patch-note JSON/Markdown are T4-changed paths; the user explicitly approved only these two shared documents as append-only exceptions. Existing JSON entries and order, and the complete Markdown prefix, remain unchanged. Changed code/T4 overlap stays zero; total shared-document overlap is two. Future integration must preserve both histories and check duplicate entries.
- No new branch, merge, auto-merge, rebase or T4 code overwrite. PR #5 Draft/manual-review workflow remains; GitHub API access is still unavailable, so isDraft is not independently revalidated.

## Per-file scripts classification

Counts below are conservative static reference counts. `I/S/C/D/W/M/T/O` = incoming imports / subprocess / tracked CI / Docker-deploy / Windows scheduler-launch template / Markdown-docs / tests / other code. Zero means no match found in the scanned checkout, not proof of no external caller. Outgoing imports and full `path:line` references are in the JSON.

| Script | Category | I/S/C/D/W/M/T/O |
| --- | --- | --- |
| `scripts/__init__.py` | OPERATIONS | 0/0/0/0/0/0/0/0 |
| `scripts/analyze_entry_blockers.py` | DIAGNOSTICS | 0/0/0/0/0/4/0/0 |
| `scripts/approval_cli.py` | OPERATIONS | 0/0/0/0/0/6/2/2 |
| `scripts/benchmark_operator_visibility_memory.py` | DIAGNOSTICS | 0/0/0/0/0/0/0/0 |
| `scripts/build_api_catalog.py` | OPERATIONS | 2/0/0/0/0/6/0/2 |
| `scripts/build_default_rules.py` | OPERATIONS | 0/0/0/0/0/3/0/0 |
| `scripts/build_uef5_clean_evidence_coverage.py` | RESEARCH | 0/1/0/0/0/1/1/0 |
| `scripts/capture_preopen_macro_snapshot.py` | OPERATIONS | 0/0/0/0/0/0/0/1 |
| `scripts/capture_q10_preopen_snapshot.py` | OPERATIONS | 1/0/0/0/0/1/0/1 |
| `scripts/capture_q12_btc_0855_snapshot.py` | OPERATIONS | 1/0/0/0/0/0/0/1 |
| `scripts/check_alert_policy_v1.py` | DIAGNOSTICS | 5/0/0/0/0/7/3/2 |
| `scripts/check_audit_trail_completeness.py` | DIAGNOSTICS | 1/0/0/0/0/1/0/1 |
| `scripts/check_daily_uef_run_status.py` | DIAGNOSTICS | 3/0/0/0/0/0/4/1 |
| `scripts/check_log_archive_integrity.py` | DIAGNOSTICS | 2/0/0/0/0/2/0/2 |
| `scripts/check_metrics_schema_v1.py` | DIAGNOSTICS | 2/0/0/0/0/3/1/1 |
| `scripts/check_monitor_gate_patterns.py` | DIAGNOSTICS | 1/0/0/0/0/0/1/0 |
| `scripts/check_phase_5_2_5_3_runtime_health.py` | DIAGNOSTICS | 1/0/0/0/0/3/1/0 |
| `scripts/check_profitability_recovery_day1.py` | DIAGNOSTICS | 1/0/0/0/0/1/1/0 |
| `scripts/check_q9_q12_readiness.py` | DIAGNOSTICS | 1/0/0/0/0/3/1/0 |
| `scripts/check_real_execution_preflight.py` | DIAGNOSTICS | 1/0/0/0/0/3/1/0 |
| `scripts/check_reporter_upgrade_regression.py` | DIAGNOSTICS | 1/0/0/0/0/3/1/0 |
| `scripts/check_reports_trades_health.py` | DIAGNOSTICS | 2/0/0/0/0/4/1/1 |
| `scripts/check_runtime_profile.py` | DIAGNOSTICS | 0/0/0/0/0/9/0/0 |
| `scripts/check_trade_report_runtime_regression.py` | DIAGNOSTICS | 1/0/0/0/0/2/1/0 |
| `scripts/clean_evaluation_test_contamination.py` | MAINTENANCE | 0/0/0/0/0/0/0/1 |
| `scripts/cleanup_pytest_artifacts.cmd` | MAINTENANCE | 0/0/0/0/0/0/0/0 |
| `scripts/cleanup_pytest_artifacts.ps1` | MAINTENANCE | 0/0/0/0/0/0/0/0 |
| `scripts/cleanup_pytest_artifacts.py` | MAINTENANCE | 0/0/0/0/0/1/0/2 |
| `scripts/collect_opening_rank1_symbol_metadata.py` | OPERATIONS | 0/0/0/0/0/0/0/0 |
| `scripts/compact_q9_decision_windows.py` | MAINTENANCE | 0/0/0/0/0/0/0/0 |
| `scripts/daily_profitability_scorecard.py` | RESEARCH | 1/0/0/0/0/1/1/0 |
| `scripts/demo_m14_mock_order.py` | OPERATIONS | 0/0/0/0/0/3/0/0 |
| `scripts/demo_m14_order_status.py` | EXAMPLES | 0/0/0/0/0/1/0/0 |
| `scripts/demo_m14_quote_then_order.py` | OPERATIONS | 0/0/0/0/0/0/0/0 |
| `scripts/demo_m15_smoke.py` | OPERATIONS | 0/0/0/0/0/0/0/2 |
| `scripts/demo_m22_graph_with_hydration.py` | EXAMPLES | 2/0/0/0/0/2/1/1 |
| `scripts/demo_m22_skill_flow.py` | EXAMPLES | 1/0/0/0/0/5/1/0 |
| `scripts/demo_m22_skill_hydration.py` | EXAMPLES | 1/0/0/0/0/2/1/0 |
| `scripts/demo_m7_dry_run_pipeline.py` | EXAMPLES | 0/0/0/0/0/3/0/0 |
| `scripts/docker_healthcheck.py` | OPERATIONS | 1/0/0/6/0/3/2/14 |
| `scripts/examples/__init__.py` | EXAMPLES | 0/1/0/0/0/14/2/5 |
| `scripts/examples/demo_m22_graph_with_hydration.py` | EXAMPLES | 0/0/0/0/0/0/0/2 |
| `scripts/examples/demo_m22_skill_flow.py` | EXAMPLES | 0/0/0/0/0/0/0/2 |
| `scripts/examples/demo_m7_dry_run_pipeline.py` | EXAMPLES | 0/0/0/0/0/0/0/2 |
| `scripts/generate_daily_report.py` | OPERATIONS | 5/0/0/0/0/23/3/3 |
| `scripts/generate_m28_launch_templates.py` | DIAGNOSTICS | 0/0/0/0/0/1/0/0 |
| `scripts/generate_m28_registration_helpers.py` | DIAGNOSTICS | 0/0/0/0/0/1/0/0 |
| `scripts/generate_metrics_report.py` | OPERATIONS | 10/0/0/0/0/23/5/6 |
| `scripts/generate_operator_summary_report.py` | OPERATIONS | 0/0/0/0/0/0/0/0 |
| `scripts/generate_ops_diagnostic_report.py` | DIAGNOSTICS | 1/0/0/0/0/0/1/0 |
| `scripts/generate_strategist_llm_summary.py` | OPERATIONS | 0/0/0/0/0/1/0/0 |
| `scripts/generate_symbol_trade_report.py` | OPERATIONS | 0/0/0/0/0/0/0/0 |
| `scripts/launch_with_preflight.py` | OPERATIONS | 0/0/0/4/4/6/0/4 |
| `scripts/organize_llm_reports.py` | MAINTENANCE | 0/0/0/0/0/2/0/0 |
| `scripts/query_commander_resilience_events.py` | DIAGNOSTICS | 2/0/0/0/0/6/1/1 |
| `scripts/query_intent_state_store.py` | DIAGNOSTICS | 2/0/0/0/0/3/1/2 |
| `scripts/query_m25_notification_events.py` | DIAGNOSTICS | 2/0/0/0/0/7/1/1 |
| `scripts/query_strategist_llm_events.py` | DIAGNOSTICS | 1/0/0/0/0/7/1/0 |
| `scripts/query_trade_reason_chain.py` | DIAGNOSTICS | 1/0/0/0/0/2/1/1 |
| `scripts/reconcile_intent_state_store.py` | MAINTENANCE | 1/0/0/0/0/5/1/0 |
| `scripts/reconstruct_incident_timeline.py` | DIAGNOSTICS | 1/0/0/0/0/1/0/1 |
| `scripts/register_mock_exam_tasks_example.bat` | OPERATIONS | 0/0/0/0/0/3/1/0 |
| `scripts/repair_q9_day_artifacts.py` | MAINTENANCE | 0/0/0/0/0/0/0/0 |
| `scripts/repair_trade_symbol_context.py` | MAINTENANCE | 0/0/0/0/0/0/0/0 |
| `scripts/restart_live_session.bat` | MAINTENANCE | 0/0/0/0/0/9/0/0 |
| `scripts/restart_live_session.ps1` | MAINTENANCE | 0/0/0/0/0/2/0/0 |
| `scripts/restart_live_session.py` | T4_OWNED | 2/0/0/5/0/8/6/10 |
| `scripts/run_agent_effectiveness_scorecard.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_agent_pipeline_trace_report.py` | DIAGNOSTICS | 1/0/0/0/0/4/1/1 |
| `scripts/run_ai_trade_report_batch.py` | OPERATIONS | 2/0/0/0/0/23/3/1 |
| `scripts/run_alpha_hypothesis_competition.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_alpha_research_board.py` | RESEARCH | 0/2/0/0/0/6/2/1 |
| `scripts/run_attribution_score_range.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_attribution_score_window.py` | RESEARCH | 0/0/0/0/0/1/0/0 |
| `scripts/run_baseline_btc_woori_tech.py` | RESEARCH | 0/0/0/2/0/1/2/7 |
| `scripts/run_baseline_samsung_hynix.py` | RESEARCH | 0/0/0/2/0/3/4/5 |
| `scripts/run_broker_trade_reconciliation.py` | MAINTENANCE | 1/0/0/0/0/4/1/0 |
| `scripts/run_closeout_maintenance.bat` | MAINTENANCE | 0/0/0/0/0/0/0/2 |
| `scripts/run_closeout_maintenance.py` | MAINTENANCE | 7/0/0/0/0/7/14/6 |
| `scripts/run_commander_runtime_once.py` | OPERATIONS | 0/0/0/4/4/9/0/4 |
| `scripts/run_conditional_alpha_diagnosis.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_cumulative_improvement_review.py` | RESEARCH | 0/0/0/0/0/1/0/0 |
| `scripts/run_daily_uef_evaluation.py` | RESEARCH | 0/0/0/0/0/8/1/5 |
| `scripts/run_decision_story_report.py` | RESEARCH | 2/0/0/0/0/7/2/1 |
| `scripts/run_evaluation_lens_report.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_existing_evidence_mining.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_frozen_q9_baseline_closeout.py` | RESEARCH | 0/0/0/0/0/3/0/0 |
| `scripts/run_full_chain_component_review.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_historical_q9_prior.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_horizon_alignment_review.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_horizon_revision_backtest.py` | RESEARCH | 0/0/0/0/0/1/0/0 |
| `scripts/run_integrated_trade_diagnosis.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_integrated_trade_validation.py` | RESEARCH | 0/0/0/0/0/1/0/0 |
| `scripts/run_live_execution_bundle_report.py` | OPERATIONS | 4/0/0/0/0/59/14/14 |
| `scripts/run_live_session_summary.py` | OPERATIONS | 1/0/0/0/0/5/1/0 |
| `scripts/run_live_session_watch.bat` | OPERATIONS | 0/0/0/0/0/2/0/0 |
| `scripts/run_live_session_watch.py` | OPERATIONS | 0/0/0/0/0/4/1/0 |
| `scripts/run_log_maintenance.py` | MAINTENANCE | 0/0/0/0/0/2/0/0 |
| `scripts/run_loss_decomposition.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_m13_live_loop.py` | OPERATIONS | 0/0/0/5/0/44/1/5 |
| `scripts/run_m15_matrix.py` | DIAGNOSTICS | 0/0/0/0/0/0/0/0 |
| `scripts/run_m22_closeout_check.py` | DIAGNOSTICS | 1/0/0/0/0/2/1/0 |
| `scripts/run_m23_closeout_check.py` | DIAGNOSTICS | 2/0/0/0/0/3/2/1 |
| `scripts/run_m23_resilience_closeout_check.py` | DIAGNOSTICS | 2/0/0/0/0/3/1/1 |
| `scripts/run_m24_closeout_check.py` | DIAGNOSTICS | 2/0/0/0/0/3/2/1 |
| `scripts/run_m24_guard_precedence_check.py` | DIAGNOSTICS | 3/0/0/0/0/5/3/2 |
| `scripts/run_m25_closeout_check.py` | DIAGNOSTICS | 3/0/0/0/0/6/1/2 |
| `scripts/run_m25_ops_batch.py` | OPERATIONS | 2/0/0/0/0/13/3/0 |
| `scripts/run_m26_ab_evaluation.py` | DIAGNOSTICS | 3/0/0/0/0/4/1/2 |
| `scripts/run_m26_closeout_check.py` | DIAGNOSTICS | 2/0/0/0/0/3/2/1 |
| `scripts/run_m26_dataset_manifest_check.py` | DIAGNOSTICS | 6/0/0/0/0/3/5/1 |
| `scripts/run_m26_promotion_gate_check.py` | DIAGNOSTICS | 2/0/0/0/0/3/1/1 |
| `scripts/run_m26_replay_runner.py` | DIAGNOSTICS | 3/0/0/0/0/3/1/2 |
| `scripts/run_m26_scorecard.py` | DIAGNOSTICS | 3/0/0/0/0/4/1/2 |
| `scripts/run_m27_allocation_policy_check.py` | DIAGNOSTICS | 2/0/0/0/0/3/2/1 |
| `scripts/run_m27_closeout_check.py` | DIAGNOSTICS | 2/0/0/0/0/3/2/1 |
| `scripts/run_m27_conflict_resolution_check.py` | DIAGNOSTICS | 2/0/0/0/0/3/2/1 |
| `scripts/run_m27_portfolio_budget_boundary_check.py` | DIAGNOSTICS | 2/0/0/0/0/3/2/1 |
| `scripts/run_m27_portfolio_guard_alert_policy_check.py` | DIAGNOSTICS | 2/0/0/0/0/3/2/1 |
| `scripts/run_m27_portfolio_guard_metrics_check.py` | DIAGNOSTICS | 2/0/0/0/0/3/2/1 |
| `scripts/run_m27_portfolio_guard_notify_check.py` | DIAGNOSTICS | 2/0/0/0/0/5/2/1 |
| `scripts/run_m27_portfolio_guard_notify_query_check.py` | DIAGNOSTICS | 2/0/0/0/0/4/2/1 |
| `scripts/run_m27_portfolio_guard_notify_routing_check.py` | DIAGNOSTICS | 2/0/0/0/0/5/2/1 |
| `scripts/run_m27_runtime_portfolio_guard_check.py` | DIAGNOSTICS | 2/0/0/0/0/3/2/1 |
| `scripts/run_m28_closeout_check.py` | DIAGNOSTICS | 0/0/0/0/0/1/1/0 |
| `scripts/run_m28_deploy_launch_template_check.py` | DIAGNOSTICS | 0/0/0/0/1/3/1/0 |
| `scripts/run_m28_launch_hook_integration_check.py` | DIAGNOSTICS | 0/0/0/0/0/4/1/0 |
| `scripts/run_m28_registration_helper_check.py` | DIAGNOSTICS | 0/0/0/0/1/3/1/0 |
| `scripts/run_m28_rollout_rollback_check.py` | DIAGNOSTICS | 0/0/0/0/0/3/1/0 |
| `scripts/run_m28_runtime_lifecycle_hooks_check.py` | DIAGNOSTICS | 0/0/0/0/0/7/1/0 |
| `scripts/run_m28_runtime_profile_scaffold_check.py` | DIAGNOSTICS | 0/0/0/0/0/6/1/0 |
| `scripts/run_m28_scheduler_worker_launch_wrapper_check.py` | DIAGNOSTICS | 0/0/0/0/1/4/1/0 |
| `scripts/run_m28_startup_preflight_check.py` | DIAGNOSTICS | 0/0/0/0/0/7/1/0 |
| `scripts/run_m29_audit_trail_check.py` | DIAGNOSTICS | 2/0/0/0/0/3/2/1 |
| `scripts/run_m29_closeout_check.py` | DIAGNOSTICS | 2/0/0/0/0/5/2/1 |
| `scripts/run_m29_disaster_recovery_drill.py` | DIAGNOSTICS | 2/0/0/0/0/2/2/1 |
| `scripts/run_m29_incident_timeline_check.py` | DIAGNOSTICS | 2/0/0/0/0/2/2/1 |
| `scripts/run_m29_log_archive_integrity_check.py` | DIAGNOSTICS | 2/0/0/0/0/2/2/1 |
| `scripts/run_m30_final_golive_signoff.py` | DIAGNOSTICS | 2/0/0/0/0/5/2/2 |
| `scripts/run_m30_post_golive_monitoring_policy.py` | DIAGNOSTICS | 3/0/0/0/0/6/2/3 |
| `scripts/run_m30_quality_gates_bundle.py` | DIAGNOSTICS | 3/0/0/0/0/3/2/2 |
| `scripts/run_m30_release_signoff_checklist.py` | DIAGNOSTICS | 3/0/0/0/0/3/2/2 |
| `scripts/run_m31_agent_chain_probe.py` | DIAGNOSTICS | 0/0/0/0/0/11/1/0 |
| `scripts/run_m31_mock_exam_readiness_check.py` | DIAGNOSTICS | 0/0/0/0/0/1/0/2 |
| `scripts/run_m31_mock_investor_exam_check.py` | DIAGNOSTICS | 2/0/0/0/0/10/2/1 |
| `scripts/run_m31_slo_incident_review_check.py` | DIAGNOSTICS | 2/0/0/0/0/7/2/2 |
| `scripts/run_m31_weekly_health_summary.py` | DIAGNOSTICS | 1/0/0/0/0/4/2/0 |
| `scripts/run_market_regime_rail_review.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_memory_contamination_review.py` | RESEARCH | 0/0/0/0/0/1/0/0 |
| `scripts/run_mock_exam_closeout.bat` | OPERATIONS | 0/0/0/0/1/2/0/2 |
| `scripts/run_mock_exam_day.py` | OPERATIONS | 0/0/0/0/0/14/1/0 |
| `scripts/run_mock_exam_preopen.bat` | OPERATIONS | 0/0/0/0/1/2/0/1 |
| `scripts/run_mock_exam_session.bat` | OPERATIONS | 0/0/0/0/1/5/0/2 |
| `scripts/run_mock_exam_session_probe.bat` | OPERATIONS | 0/0/0/0/0/2/0/0 |
| `scripts/run_mock_exam_session_simulated.bat` | OPERATIONS | 0/0/0/0/0/1/0/0 |
| `scripts/run_mock_exam_session_watchdog.bat` | OPERATIONS | 0/0/0/0/1/1/0/1 |
| `scripts/run_monitor_noop_attribution.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_offhours_full_trace_bundle.py` | DIAGNOSTICS | 1/0/0/0/0/4/1/0 |
| `scripts/run_offhours_validation_loop.py` | RESEARCH | 0/0/0/0/0/7/1/0 |
| `scripts/run_opening_macro_snapshot_collector.py` | OPERATIONS | 0/0/0/0/0/1/1/2 |
| `scripts/run_opening_rank1_deep_dive.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_opening_rank1_longitudinal.py` | RESEARCH | 0/0/0/0/0/1/0/0 |
| `scripts/run_opening_rank1_shadow.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_operator_brief_batch.py` | OPERATIONS | 1/0/0/0/0/1/1/0 |
| `scripts/run_operator_daily_summary.py` | OPERATIONS | 2/0/0/0/0/7/2/1 |
| `scripts/run_operator_summary_mining.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_operator_ui.py` | OPERATIONS | 0/0/0/0/0/2/0/3 |
| `scripts/run_opportunity_engine_shadow.py` | RESEARCH | 0/0/0/2/0/2/1/5 |
| `scripts/run_phase5_validation_bundle.py` | RESEARCH | 1/0/0/0/0/0/1/0 |
| `scripts/run_post_exit_shadow_recap.py` | RESEARCH | 0/0/0/0/0/2/0/1 |
| `scripts/run_post_reclaim_offline_research.py` | RESEARCH | 0/0/0/0/0/2/0/0 |
| `scripts/run_pytest.cmd` | OPERATIONS | 0/0/0/0/0/0/0/0 |
| `scripts/run_pytest.ps1` | OPERATIONS | 0/0/0/0/0/0/0/0 |
| `scripts/run_pytest.py` | DIAGNOSTICS | 0/0/0/0/0/1/0/1 |
| `scripts/run_q10_index_observation_collector.py` | OPERATIONS | 1/0/0/0/0/1/8/2 |
| `scripts/run_q12_btc_0855_capture.bat` | OPERATIONS | 0/0/0/0/1/1/0/1 |
| `scripts/run_q12_historical_policy_review.py` | RESEARCH | 0/0/0/0/0/1/0/0 |
| `scripts/run_q13_q14_validation.py` | RESEARCH | 0/0/0/0/0/2/0/0 |
| `scripts/run_q8_historical_review.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_q8_lane_decision_table.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_q8_shadow_blocker_review.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_q9_baseline_comparison.py` | RESEARCH | 0/0/0/0/0/1/0/0 |
| `scripts/run_q9_evaluation.py` | RESEARCH | 0/0/0/0/0/4/0/0 |
| `scripts/run_quant_trade_diagnosis.py` | RESEARCH | 0/0/0/0/0/2/0/0 |
| `scripts/run_rank1_feature_mart.py` | RESEARCH | 0/0/0/0/0/2/0/0 |
| `scripts/run_rank1_prospective_shadow.py` | RESEARCH | 0/0/0/0/0/1/0/0 |
| `scripts/run_report_maintenance.py` | MAINTENANCE | 0/0/0/0/0/6/0/1 |
| `scripts/run_reporter_analysis_report.py` | OPERATIONS | 1/0/0/0/0/4/1/1 |
| `scripts/run_run_card_report.py` | RESEARCH | 2/0/0/0/0/7/2/1 |
| `scripts/run_same_symbol_sequence.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_scanner_alignment_root_cause_range.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_scheduled_intelligence.py` | OPERATIONS | 0/0/0/0/0/0/0/1 |
| `scripts/run_session.py` | T4_OWNED | 1/0/0/4/0/108/13/12 |
| `scripts/run_short_alpha_discriminator.py` | RESEARCH | 0/0/0/0/0/1/0/0 |
| `scripts/run_stage2_authority_review.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_structural_alpha_batch1.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_structural_alpha_batch2.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_trade_explain_report.py` | RESEARCH | 3/0/0/0/0/3/3/0 |
| `scripts/run_uef5_3_dual_run.py` | RESEARCH | 0/0/0/0/0/1/0/0 |
| `scripts/run_uef5_historical_recompute.py` | RESEARCH | 0/0/0/0/0/3/0/1 |
| `scripts/run_uef6_dedup_detection.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_uef6_historical_validation.py` | RESEARCH | 0/0/0/0/0/0/0/0 |
| `scripts/run_uef7_alpha_board_normalization.py` | RESEARCH | 0/0/0/0/0/1/0/0 |
| `scripts/run_uef8_fair_comparison_validation.py` | RESEARCH | 0/0/0/0/0/1/0/0 |
| `scripts/run_uef9_formal_authority.py` | RESEARCH | 0/0/0/0/0/1/0/0 |
| `scripts/smoke_m20_llm.py` | DIAGNOSTICS | 2/0/0/0/0/8/2/0 |
| `scripts/smoke_m22_hydration.py` | DIAGNOSTICS | 1/0/0/0/0/2/1/0 |
| `scripts/start_operator_ui.ps1` | OPERATIONS | 0/0/0/0/0/5/0/0 |
| `scripts/start_q12_preopen.ps1` | OPERATIONS | 0/0/0/0/1/1/1/1 |
| `scripts/start_trading_day.py` | OPERATIONS | 2/0/0/0/0/7/8/5 |
| `scripts/step5d_crash_reconciliation.py` | MAINTENANCE | 2/0/0/0/0/1/2/1 |
| `scripts/stop_operator_ui.ps1` | MAINTENANCE | 0/0/0/0/0/5/0/0 |
| `scripts/sync_legacy_brief_llm.py` | MAINTENANCE | 0/0/0/0/0/1/0/0 |
| `scripts/sync_openrouter_model_catalog.py` | MAINTENANCE | 0/0/0/0/0/3/0/0 |
| `scripts/unregister_mock_exam_tasks_example.bat` | OPERATIONS | 0/0/0/0/0/2/0/0 |
| `scripts/verify_uef_freeze_manifest.py` | DIAGNOSTICS | 0/2/0/0/0/9/2/2 |

## Completion state

The user approved append-only updates to exactly the two shared UI patch-note files.
Remote target branch and PR #5 head were both rechecked immediately before edits
and still equal `57405608514c23d68f64b46e0e769467d5216cc5`;
T4 remains `4e242e5b1fc609b0ec012e0c6faed37b202e4aa0`.
No remote changes needed incorporation. No T4 files were checked out or copied.
Existing JSON entries and ordering and the full Markdown prefix are preserved;
only one new history entry and the exact entry_count update are added.
Only the target branch will be pushed; no Ready/merge/auto-merge operation.

Final combined targeted pytest before commit: **26 passed**, one dependency deprecation warning. Changed paths: 12; T4 code overlap: 0; approved shared changelog overlap: 2.
