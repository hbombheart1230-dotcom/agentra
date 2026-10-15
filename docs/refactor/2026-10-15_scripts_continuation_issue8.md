# Issue #8 — Scripts continuation (not final cleanup acceptance)

**Status: SCRIPTS_CONTINUATION_IN_PROGRESS**

Base `c0e3211920f7d3c90aca692f31b27765062622ed` on `refactor/agentra-target-tree`; T4 observed `6f68b74aa65b082799acae86ec986ad2d9ed2b22`. PR #5 stays Draft. No branch creation, T4 checkout/merge, wrapper deletion, runtime/Config/strategy or deployment changes.

## Implemented now

- Reproduced two genuine static-auditor false accepts: replacing the module alias assignment with a disconnected variable, and changing run_module run_name away from __main__. Target strings alone still passed. The auditor now checks exact top-level main-guard dispatch and ABI alias AST statements. Commented example main calls no longer count as executable dispatch.
- Added three fail-closed fixture regressions; all 141 real wrappers still pass. The wrappers themselves are untouched.
- Added a read-only Windows launcher auditor: 20 files, reference graph including bound-variable dispatch/sibling paths, CWD/env-policy text and task registration/deletion contracts. Unknown shell evaluation and external callers remain unknown; it is explicitly not a shell interpreter.
- Added five isolated graph/safety fixtures, including missing-target failure, sibling/CWD dispatch, count mismatch and never-executed launcher source.
- Extended the existing Linux/Windows Scripts CI only: actual-checkout launcher audit, six native PowerShell ParseFile syntax checks on Windows, and the 12 source-only fixture tests staged outside the checkout. No launcher is invoked, no task registered/deleted, no live broker/market/LLM called.
- Local validation: 141/141 ABI audit, 20/20 launcher static audit, 12/12 fixture tests; the exact CI staging/test shell commands also passed locally. Native Windows parse is validated by the new Windows CI job after push, not claimed from this Linux host.

## Root responsibility accounting

- Historical inventory reused; only the 42 implementations, 8 existing delegates and 20 launcher sources plus bounded deployment-template references were supplemented. No repeat of the completed 828 CLI matrix or the full repository suite.
- Root counts unchanged: 42 implementations / 8 existing delegates / 141 migration wrappers / 1 package marker / 20 Windows-shell files. Categories overlap with the 19 holds and must not be added together.
- Dynamic/manual external use remains UNKNOWN. Existing tracked refs are preserved as evidence; generated/untracked deployment templates are explicitly labeled in the JSON. No absence-of-grep deletion conclusion.

| Root implementation responsibility | Count |
| --- | --- |
| PRODUCTION_ENTRYPOINT | 4 |
| MAINTENANCE | 2 |
| TEST_DIAGNOSTIC | 7 |
| OPERATIONAL_REQUIRED | 23 |
| RESEARCH | 2 |
| DEMO_POTENTIALLY_ORDER_CAPABLE | 3 |
| UI_LAUNCHER | 1 |

### All 42 implementations and 8 delegates

| Path | Kind / responsibility | Risk | Decision | Reason |
| --- | --- | --- | --- | --- |
| `scripts/approval_cli.py` | implementation / PRODUCTION_ENTRYPOINT | CRITICAL | KEEP | Explicit approval/tool facade can mutate execution workflow; preserve public approval boundary. |
| `scripts/build_api_catalog.py` | existing_forwarder / MAINTENANCE | MEDIUM_WITH_IO_REVIEW | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/build_default_rules.py` | implementation / MAINTENANCE | MEDIUM_WITH_IO_REVIEW | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/build_uef5_clean_evidence_coverage.py` | implementation / TEST_DIAGNOSTIC | MEDIUM_WITH_IO_REVIEW | RELOCATION_CANDIDATE_AFTER_GATE | Source coverage CLI itself passed; broader UEF historical evidence is a separate integration gate. |
| `scripts/capture_preopen_macro_snapshot.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/capture_q10_preopen_snapshot.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/capture_q12_btc_0855_snapshot.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/cleanup_pytest_artifacts.py` | implementation / MAINTENANCE | MEDIUM_WITH_IO_REVIEW | KEEP | No parser help gate; main deletes matching trees. Never run for an audit. |
| `scripts/collect_opening_rank1_symbol_metadata.py` | implementation / RESEARCH | MEDIUM_WITH_IO_REVIEW | RELOCATION_CANDIDATE_AFTER_GATE | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/demo_m14_mock_order.py` | implementation / DEMO_POTENTIALLY_ORDER_CAPABLE | HIGH | KEEP | May call actual executor/order/approval flow despite demo or mock naming; preserve and never execute for cleanup. |
| `scripts/demo_m14_order_status.py` | implementation / TEST_DIAGNOSTIC | MEDIUM_WITH_IO_REVIEW | KEEP | Status/fill lookup intent, but credentials/executor transport used; network smoke not safe here. |
| `scripts/demo_m14_quote_then_order.py` | implementation / DEMO_POTENTIALLY_ORDER_CAPABLE | HIGH | KEEP | May call actual executor/order/approval flow despite demo or mock naming; preserve and never execute for cleanup. |
| `scripts/demo_m15_smoke.py` | implementation / DEMO_POTENTIALLY_ORDER_CAPABLE | HIGH | KEEP | May call actual executor/order/approval flow despite demo or mock naming; preserve and never execute for cleanup. |
| `scripts/demo_m22_skill_hydration.py` | implementation / TEST_DIAGNOSTIC | MEDIUM_WITH_IO_REVIEW | RELOCATION_CANDIDATE_AFTER_GATE | Injected demo skill runner; candidate only after architecture approval, no move now. |
| `scripts/docker_healthcheck.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Docker runtime liveness/readiness boundary; preserve command and semantics. |
| `scripts/generate_daily_report.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Report/materialization entrypoint or compatibility facade; output/LLM consumers and manual use must remain stable. |
| `scripts/generate_metrics_report.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Report/materialization entrypoint or compatibility facade; output/LLM consumers and manual use must remain stable. |
| `scripts/generate_operator_summary_report.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Report/materialization entrypoint or compatibility facade; output/LLM consumers and manual use must remain stable. |
| `scripts/generate_strategist_llm_summary.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/generate_symbol_trade_report.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Report/materialization entrypoint or compatibility facade; output/LLM consumers and manual use must remain stable. |
| `scripts/launch_with_preflight.py` | existing_forwarder / PRODUCTION_ENTRYPOINT | CRITICAL | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/restart_live_session.py` | implementation / PRODUCTION_ENTRYPOINT | CRITICAL | KEEP | T4-owned live-session stop/start path; never execute or relocate in PR5. |
| `scripts/run_ai_trade_report_batch.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Report/materialization entrypoint or compatibility facade; output/LLM consumers and manual use must remain stable. |
| `scripts/run_baseline_btc_woori_tech.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/run_baseline_samsung_hynix.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/run_closeout_maintenance.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/run_commander_runtime_once.py` | existing_forwarder / PRODUCTION_ENTRYPOINT | CRITICAL | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/run_daily_uef_evaluation.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Production scheduled daily evaluation, not an unused research tool. |
| `scripts/run_live_execution_bundle_report.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Report/materialization entrypoint or compatibility facade; output/LLM consumers and manual use must remain stable. |
| `scripts/run_live_session_summary.py` | existing_forwarder / OPERATIONAL_REQUIRED | HIGH | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/run_live_session_watch.py` | existing_forwarder / PRODUCTION_ENTRYPOINT | CRITICAL | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/run_m13_live_loop.py` | existing_forwarder / PRODUCTION_ENTRYPOINT | CRITICAL | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/run_m15_matrix.py` | implementation / TEST_DIAGNOSTIC | MEDIUM_WITH_IO_REVIEW | KEEP | --help is not a dry run; scenario runner spawns subprocesses with execution/approval env. |
| `scripts/run_m25_closeout_check.py` | implementation / TEST_DIAGNOSTIC | MEDIUM_WITH_IO_REVIEW | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/run_m25_ops_batch.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/run_mock_exam_day.py` | existing_forwarder / PRODUCTION_ENTRYPOINT | CRITICAL | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/run_opening_macro_snapshot_collector.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/run_opening_rank1_deep_dive.py` | existing_forwarder / RESEARCH | MEDIUM_WITH_IO_REVIEW | TEST_BLOCKED | Existing empty-input IndexError; no safe --help contract. Underlying research fix and fixtures required. |
| `scripts/run_operator_brief_batch.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/run_operator_daily_summary.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/run_operator_ui.py` | implementation / UI_LAUNCHER | HIGH | KEEP | Soft-deprecated manual operator UI entrypoint; deprecation is not external-usage proof. |
| `scripts/run_opportunity_engine_shadow.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/run_pytest.py` | implementation / TEST_DIAGNOSTIC | MEDIUM_WITH_IO_REVIEW | TEST_BLOCKED | Public Windows venv/Scripts/python.exe contract; Linux missing executable is not proof of disuse. |
| `scripts/run_q10_index_observation_collector.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/run_reporter_analysis_report.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Report/materialization entrypoint or compatibility facade; output/LLM consumers and manual use must remain stable. |
| `scripts/run_scheduled_intelligence.py` | implementation / OPERATIONAL_REQUIRED | HIGH | KEEP | Public source/tool contract with operational or potential manual consumers; no removal/relocation proof. |
| `scripts/run_session.py` | implementation / PRODUCTION_ENTRYPOINT | CRITICAL | KEEP | T4-owned canonical session dispatch with live/preopen/watch contracts; must remain stable. |
| `scripts/run_uef5_historical_recompute.py` | implementation / RESEARCH | MEDIUM_WITH_IO_REVIEW | TEST_BLOCKED | Historical UEF job requires admissible artifacts; no fabricated production history. |
| `scripts/start_trading_day.py` | implementation / PRODUCTION_ENTRYPOINT | CRITICAL | KEEP | Top-level scheduler/start/watchdog launcher chain; must remain stable. |
| `scripts/verify_uef_freeze_manifest.py` | implementation / TEST_DIAGNOSTIC | MEDIUM_WITH_IO_REVIEW | KEEP | Active read-only freeze gate is useful and passed earlier; retain stable check command. |

### Windows/shell invocation graph (20; sources unchanged)

References below include direct literal targets and command binding dispatch. Process-match literals are evidence of lifecycle coupling, not assertions that those lines execute a target. Full line numbers, binding kinds, CWD, policy and dispatch source are in the JSON.

| Launcher | Referenced Scripts targets | CWD contract lines |
| --- | --- | --- |
| `scripts/cleanup_pytest_artifacts.cmd` | `scripts/cleanup_pytest_artifacts.py` | No chdir; inspect absolute/sibling target and caller CWD |
| `scripts/cleanup_pytest_artifacts.ps1` | No Scripts target; inline maintenance/task operations or python -m pytest | 16, 32 |
| `scripts/register_mock_exam_tasks_example.bat` | `scripts/run_mock_exam_closeout.bat`, `scripts/run_mock_exam_preopen.bat`, `scripts/run_mock_exam_session.bat`, `scripts/run_mock_exam_session_watchdog.bat`, `scripts/run_q12_btc_0855_capture.bat`, `scripts/start_q12_preopen.ps1` | No chdir; inspect absolute/sibling target and caller CWD |
| `scripts/restart_live_session.bat` | `scripts/restart_live_session.py` | No chdir; inspect absolute/sibling target and caller CWD |
| `scripts/restart_live_session.ps1` | `scripts/restart_live_session.py` | No chdir; inspect absolute/sibling target and caller CWD |
| `scripts/run_closeout_maintenance.bat` | `scripts/run_closeout_maintenance.py` | 3 |
| `scripts/run_live_session_watch.bat` | `scripts/run_session.py` | No chdir; inspect absolute/sibling target and caller CWD |
| `scripts/run_mock_exam_closeout.bat` | `scripts/run_closeout_maintenance.bat` | No chdir; inspect absolute/sibling target and caller CWD |
| `scripts/run_mock_exam_preopen.bat` | `scripts/capture_preopen_macro_snapshot.py`, `scripts/capture_q10_preopen_snapshot.py`, `scripts/run_scheduled_intelligence.py`, `scripts/run_session.py` | 12, 42 |
| `scripts/run_mock_exam_session.bat` | `scripts/start_trading_day.py` | No chdir; inspect absolute/sibling target and caller CWD |
| `scripts/run_mock_exam_session_probe.bat` | `scripts/run_mock_exam_session.bat` | No chdir; inspect absolute/sibling target and caller CWD |
| `scripts/run_mock_exam_session_simulated.bat` | `scripts/run_mock_exam_session.bat` | No chdir; inspect absolute/sibling target and caller CWD |
| `scripts/run_mock_exam_session_watchdog.bat` | `scripts/start_trading_day.py` | No chdir; inspect absolute/sibling target and caller CWD |
| `scripts/run_pytest.cmd` | `scripts/run_pytest.py` | No chdir; inspect absolute/sibling target and caller CWD |
| `scripts/run_pytest.ps1` | No Scripts target; inline maintenance/task operations or python -m pytest | 16, 22 |
| `scripts/run_q12_btc_0855_capture.bat` | `scripts/capture_q12_btc_0855_snapshot.py` | 12, 17 |
| `scripts/start_operator_ui.ps1` | `scripts/run_operator_ui.py` | 46 |
| `scripts/start_q12_preopen.ps1` | `scripts/run_baseline_btc_woori_tech.py` | 17 |
| `scripts/stop_operator_ui.ps1` | `scripts/run_operator_ui.py` | No chdir; inspect absolute/sibling target and caller CWD |
| `scripts/unregister_mock_exam_tasks_example.bat` | No Scripts target; inline maintenance/task operations or python -m pytest | No chdir; inspect absolute/sibling target and caller CWD |

**Operational review, not an automatic cleanup fix:** register_mock_exam_tasks_example.bat creates six task suffixes but unregister_mock_exam_tasks_example.bat removes four; Q12-Preopen and Q12-BTC-0855 are unmatched creates. This existing asymmetry is recorded for the operational owner. Changing/removing scheduled tasks is outside this issue and no launcher policy was changed.

- PowerShell/Windows platform-only syntax blockers now have a native Windows CI path. Parse/source success does not validate starting/stopping production processes, task scheduler state or installed host venv. Those commands remain KEEP/TEST_BLOCKED as appropriate.
- UI start/stop launchers are soft-deprecated manual paths; no removal is justified until Issue #9 validates route/view consumers and external/manual use.

## Individual held-file resolution (19)

| File | New disposition | Concrete reason |
| --- | --- | --- |
| `scripts/build_uef5_clean_evidence_coverage.py` | RELOCATION_CANDIDATE_AFTER_GATE | Coverage CLI passed; broader historical UEF suite/data gate does not prove the CLI is broken. Source ownership/architecture approval still blocks a move. |
| `scripts/cleanup_pytest_artifacts.cmd` | KEEP | Active cleanup or UI stop capability; parse/reference validation is safe, execution is not. Preserve manual command. |
| `scripts/cleanup_pytest_artifacts.ps1` | KEEP | Active cleanup or UI stop capability; parse/reference validation is safe, execution is not. Preserve manual command. |
| `scripts/cleanup_pytest_artifacts.py` | KEEP | Unsafe main: deletions or subprocess scenarios can run even with --help. Keep; only source-only/mock checks permitted. |
| `scripts/restart_live_session.bat` | KEEP | Actual scheduled/live/operational producer, wrapper chain or operational dependency. Platform parse success does not authorize movement. |
| `scripts/restart_live_session.ps1` | KEEP | Actual scheduled/live/operational producer, wrapper chain or operational dependency. Platform parse success does not authorize movement. |
| `scripts/run_baseline_btc_woori_tech.py` | KEEP | Actual scheduled/live/operational producer, wrapper chain or operational dependency. Platform parse success does not authorize movement. |
| `scripts/run_baseline_samsung_hynix.py` | KEEP | Actual scheduled/live/operational producer, wrapper chain or operational dependency. Platform parse success does not authorize movement. |
| `scripts/run_closeout_maintenance.bat` | KEEP | Actual scheduled/live/operational producer, wrapper chain or operational dependency. Platform parse success does not authorize movement. |
| `scripts/run_closeout_maintenance.py` | KEEP | Actual scheduled/live/operational producer, wrapper chain or operational dependency. Platform parse success does not authorize movement. |
| `scripts/run_daily_uef_evaluation.py` | KEEP | Actual scheduled/live/operational producer, wrapper chain or operational dependency. Platform parse success does not authorize movement. |
| `scripts/run_m15_matrix.py` | KEEP | Unsafe main: deletions or subprocess scenarios can run even with --help. Keep; only source-only/mock checks permitted. |
| `scripts/run_m25_closeout_check.py` | KEEP | Actual scheduled/live/operational producer, wrapper chain or operational dependency. Platform parse success does not authorize movement. |
| `scripts/run_opening_rank1_deep_dive.py` | TEST_BLOCKED | Windows runtime executable contract, empty-data research failure, or missing admissible UEF history respectively. No silent portability or data fabrication fix. |
| `scripts/run_opportunity_engine_shadow.py` | KEEP | Actual scheduled/live/operational producer, wrapper chain or operational dependency. Platform parse success does not authorize movement. |
| `scripts/run_pytest.py` | TEST_BLOCKED | Windows runtime executable contract, empty-data research failure, or missing admissible UEF history respectively. No silent portability or data fabrication fix. |
| `scripts/run_uef5_historical_recompute.py` | TEST_BLOCKED | Windows runtime executable contract, empty-data research failure, or missing admissible UEF history respectively. No silent portability or data fabrication fix. |
| `scripts/stop_operator_ui.ps1` | KEEP | Active cleanup or UI stop capability; parse/reference validation is safe, execution is not. Preserve manual command. |
| `scripts/verify_uef_freeze_manifest.py` | KEEP | Reclassified from a broad UEF suite hold: actual freeze CLI is read-only and passed. Keep active check; no need to move it. |

Counts: RELOCATION_CANDIDATE_AFTER_GATE 1, KEEP 15, TEST_BLOCKED 3. No retirement authorized. The prior broad UEF hold is not blindly retained: the active freeze command is KEEP; coverage CLI is a candidate only after architecture approval; historical recompute remains TEST_BLOCKED on real evidence.

## 141-wrapper maintenance/retirement plan

- 112 PRESERVE, 29 REVIEW_AFTER_ARCH_GATE; all 141 retained with current mappings. The full map and incoming evidence for each wrapper are in the JSON.
- No usage observation is not proof of no manual CLI. The 29 have usage UNKNOWN; do not label them unused.
- Required sequence before retirement: ARCH_CONVERGENCE_APPROVED after T4 diagrams → source/dynamic/scheduler/manual consumer proof and owner attestation → explicit external CLI transition/deprecation policy → old/new CLI and public/private import parity → approved cutover. Maintain aliasing and argument contracts until then.
- No extra migration compatibility wrappers, renames or removals in this issue. Newly added audits are source-only diagnostics under the existing diagnostics package.

| Unobserved wrapper (review only; preserve now) | Canonical mapping |
| --- | --- |
| `scripts/benchmark_operator_visibility_memory.py` | `scripts/diagnostics/benchmark_operator_visibility_memory.py` |
| `scripts/compact_q9_decision_windows.py` | `scripts/maintenance/compact_q9_decision_windows.py` |
| `scripts/repair_q9_day_artifacts.py` | `scripts/maintenance/repair_q9_day_artifacts.py` |
| `scripts/repair_trade_symbol_context.py` | `scripts/maintenance/repair_trade_symbol_context.py` |
| `scripts/run_agent_effectiveness_scorecard.py` | `scripts/research/run_agent_effectiveness_scorecard.py` |
| `scripts/run_alpha_hypothesis_competition.py` | `scripts/research/run_alpha_hypothesis_competition.py` |
| `scripts/run_attribution_score_range.py` | `scripts/research/run_attribution_score_range.py` |
| `scripts/run_conditional_alpha_diagnosis.py` | `scripts/research/run_conditional_alpha_diagnosis.py` |
| `scripts/run_evaluation_lens_report.py` | `scripts/research/run_evaluation_lens_report.py` |
| `scripts/run_existing_evidence_mining.py` | `scripts/research/run_existing_evidence_mining.py` |
| `scripts/run_full_chain_component_review.py` | `scripts/research/run_full_chain_component_review.py` |
| `scripts/run_historical_q9_prior.py` | `scripts/research/run_historical_q9_prior.py` |
| `scripts/run_horizon_alignment_review.py` | `scripts/research/run_horizon_alignment_review.py` |
| `scripts/run_integrated_trade_diagnosis.py` | `scripts/research/run_integrated_trade_diagnosis.py` |
| `scripts/run_loss_decomposition.py` | `scripts/research/run_loss_decomposition.py` |
| `scripts/run_market_regime_rail_review.py` | `scripts/research/run_market_regime_rail_review.py` |
| `scripts/run_monitor_noop_attribution.py` | `scripts/research/run_monitor_noop_attribution.py` |
| `scripts/run_opening_rank1_shadow.py` | `scripts/research/run_opening_rank1_shadow.py` |
| `scripts/run_operator_summary_mining.py` | `scripts/research/run_operator_summary_mining.py` |
| `scripts/run_q8_historical_review.py` | `scripts/research/run_q8_historical_review.py` |
| `scripts/run_q8_lane_decision_table.py` | `scripts/research/run_q8_lane_decision_table.py` |
| `scripts/run_q8_shadow_blocker_review.py` | `scripts/research/run_q8_shadow_blocker_review.py` |
| `scripts/run_same_symbol_sequence.py` | `scripts/research/run_same_symbol_sequence.py` |
| `scripts/run_scanner_alignment_root_cause_range.py` | `scripts/research/run_scanner_alignment_root_cause_range.py` |
| `scripts/run_stage2_authority_review.py` | `scripts/research/run_stage2_authority_review.py` |
| `scripts/run_structural_alpha_batch1.py` | `scripts/research/run_structural_alpha_batch1.py` |
| `scripts/run_structural_alpha_batch2.py` | `scripts/research/run_structural_alpha_batch2.py` |
| `scripts/run_uef6_dedup_detection.py` | `scripts/research/run_uef6_dedup_detection.py` |
| `scripts/run_uef6_historical_validation.py` | `scripts/research/run_uef6_historical_validation.py` |

## Remaining gates and Issue #9 handoff

- Scripts cleanup is NOT DONE: physical moves/renames/retirements require ARCH_CONVERGENCE_APPROVED, operational task asymmetry needs owner review, TEST_BLOCKED fixtures/platform contracts need separate evidence, and public manual CLI retirement policy is unresolved.
- User/architecture review of these root/launcher/held/wrapper dispositions is required before claiming the Scripts scope accepted. No unsupported UNUSED_CANDIDATE or DELETE decision was manufactured.
- Issue #9 checklist, not executed here: trace apps/web and apps/operator_ui routes/navigation/dynamic loaders/API consumers; preserve live operator and patch-note surfaces; inspect T4 operator UI ownership; run targeted UI smoke; delete only with consumer/dynamic-route and retirement evidence. No apps/ edits or UI build reruns in this issue.

Evidence JSON: `docs/refactor/2026-10-15_scripts_remaining_dispositions.json`. Existing Scripts acceptance evidence remains valid for the unchanged 138 migrated implementations only.


## Follow-up iteration 2 — baseline fcc0944d

Status: **SCRIPTS_CONTINUATION_IN_PROGRESS**. Scope is only the GPT follow-up at
https://github.com/hbombheart1230-dotcom/agentra/issues/8#issuecomment-6184128399.
The accepted inventory and prior 141/20 audits were reused, not repeated.
Observed T4 HEAD: ac4642dc265811bf7ff56e32adbadf8203fed771; no T4 source edits.

### Three TEST_BLOCKED deltas (original disposition JSON remains baseline evidence)

- `run_opening_rank1_deep_dive.py`: empty `episodes` reproduced IndexError in
  `outlier_sensitivity` at `descending[0]`. One-line offline research fix returns
  `top1_return_pct: null` when no return is available, preserving nonempty results.
  Full pipeline with an explicitly empty research fixture writes JSON/CSV/Markdown
  only under pytest OS temp. This empty-data test block is resolved; entrypoint stays KEEP.
- `run_pytest.py`: retained Windows `venv/Scripts/python.exe` contract (caller:
  `scripts/run_pytest.cmd`, original inventory evidence). Mocked existence/dispatch
  verifies argv boundaries, repo CWD, child exit code, both prohibited --basetemp
  forms and missing-venv fail-closed behavior. Contract test block resolved; KEEP.
  This does not claim execution of a real Windows venv from this Linux host.
- `run_uef5_historical_recompute.py`: real CLI runs against an empty OS-temp root
  from an unrelated CWD with --no-write. Existing engine returns COMPLETE for an
  empty workload: discovered/considered/recomputed=0; every family admissible_units=0;
  no output files. This is not historical evidence acceptance. An existing focused
  authority test confirms missing receipt/archive/normalized roots remain NOT_PROVEN
  and emit no admitted candles. CLI test block resolved, but real historical
  recomputation remains TEST_BLOCKED until genuine admissible evidence is supplied.
  No production evidence was synthesized, no Reporting implementation changed.

### Redundant helper review (no consolidation authorized)

AST exact-body comparison of existing root top-level private functions (at least
20 AST nodes, excluding trivial delegates) found five duplicate groups only:
`_env_path` in demo_m14_mock_order.py / demo_m14_order_status.py;
`_write_jsonl`, `_clear_file`, `_env_bool`, `_env_int` in
 demo_m14_quote_then_order.py / demo_m15_smoke.py.
Direct callers use these for catalog paths, EXECUTION_ENABLED, quantities/prices,
intent/event deletion and order/approval logging. A private name is not proof of a
non-runtime helper: these are order-capable paths. Consolidation is BLOCKED by
protected trading-path scope and absent offline broker-parity/ownership approval.
No qualifying safe non-runtime duplicate was proven in this bounded exact-body
check; this is not a claim of no semantic duplication elsewhere.
Physical moves/renames/wrapper retirement remain BLOCKED pending explicit
ARCH_CONVERGENCE_APPROVED and external/manual usage proof. All141 wrappers stay.

### Separate Q12 operational review — no scheduler edit

Source confirmation: `register_mock_exam_tasks_example.bat` lines37/43 create
`%TASK_PREFIX%-Q12-Preopen` and `%TASK_PREFIX%-Q12-BTC-0855` with prefix
`TradingAgent-MockExamDay`; `unregister_mock_exam_tasks_example.bat` deletes only
Preopen, Session, SessionWatchdog, Closeout. Thus the two fully expanded names are
`TradingAgent-MockExamDay-Q12-Preopen` and `TradingAgent-MockExamDay-Q12-BTC-0855`.
Proposed future tests for owner review only: capture schtasks arguments with a stub,
compare exact expanded create/delete sets and task scope, verify unrelated names
are untouched and capture failure/exit semantics without invoking Task Scheduler.
Do not fix the asymmetric policy automatically. Live launchers were not executed.

### Focused evidence

- New follow-up tests7 PASS plus existing research tests5 PASS (12 total).
- Existing missing-authority test1 PASS, isolated fixture only.
- Pytest temporary outputs are outside repo; successful run directories cleaned.
- One nonfatal pytest warning: cache_dir option with cacheprovider disabled.
- No full CI/828 CLI replay or inventory reclassification.
- UI notes append-only; Issue #9 not started; PR #5 remains Draft.
