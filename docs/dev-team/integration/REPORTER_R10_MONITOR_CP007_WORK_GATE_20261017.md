# P1.5 Work integration gate — Reporter R10 / Monitor CP-007

**Date:** 2026-10-17 KST
**STATE:** REVIEWED_INPUTS / PROPOSAL_ONLY, not assembled, no CI pass and no merge permission.
**Architect/reviewer:** Work. **Writer lanes:** Claude=Reporter, Codex=Monitor. Work owns shared T3/T4/agent-package/CI/UI coordination.
**Reporter exact SHA:** de99c8f0fa66bfc3e6be9a229f04fc6aad5ca06e (313 moved bodies / 23 facade paths / 41 owners)
**Monitor exact SHA:** efdab64f33b34be6ab26fd8edb9aba9ec4ebd479; last runtime 800841f229606c419dae67b0d6f794b9238676e9 (14 module moves /20 named transfers)
**Historical BASE:** d773709ba2f70471fad9badba4f92400f7818319

## 1. Independent evidence boundary

Work inspected Reporter R10 five-commit / 11-path diff; no production facade/owner move since R9, only contracts, tests, ledgers and evidence. R10 fixes original P15-WORK-004 over-broad timestamp masking, provides populated day success and timestamp negative, and adds 47 retained contracts with 3 generic parametrizations intentionally skipped but run by dedicated fixtures; it does not authorize retained I/O relocation. Synthetic artifact/API reader parity is NOT a full FastAPI router or actual LLM/persisted-report run. Windows 3.13 PASS values are developer-reported; Work has NOT rerun R10 final SHA tests. Work issue #11 review: https://github.com/hbombheart1230-dotcom/agentra/issues/11#issuecomment-6232719588 .

Work reviewed Monitor CP-007 SHA, actual selected M004/M005/M008 source/test paths and the 5 RED old shared gate assertions; 560 PASS is the developer's prior multi-command Windows 3.14 evidence, not a fresh Work test. Work issue #12 review: https://github.com/hbombheart1230-dotcom/agentra/issues/12#issuecomment-6232543190 .

## 2. Branch / concurrency invariants

Use ONLY a new isolated integration candidate (not role branches, not main). Record two exact input SHAs and compare their changes against shared historical ancestors. For each path changed by both owners, stop for explicit human-readable reconciliation; do not silently choose one. Shared files are Work-owned and added after both trees are assembled. Do not treat any prior PR #13 document merge as a source-code acceptance. Avoid new branch clutter if an existing isolation branch is suitable and safe; no forced ref updates.

The visible GitHub Actions reporting workflow runs on pushes to integration/p15-t4-pr5-convergence-20261015 and main, and PRs to main, plus manual workflow_dispatch. A new integration candidate name will **not automatically trigger that push workflow** until a safe candidate-specific trigger/manual dispatch is configured. A green old integration run is NOT evidence for the new SHA.

## 3. Shared P1 T3 closure — all allowed transformations must be proved

Existing proposed guard: docs/dev-team/proposals/reporter_facade_guard.py and test_reporter_facade_guard.py. It reconstructs all original facade module ASTs (including all UNMOVED functions, imports/statements/order) against BASE after replacing each approved wrapper by its exact BASE function and removing only strict approved owner imports/injection. Also run the existing moved-owner/lazy-global/body proof; neither check alone covers the other.

The guard's reviewed-ledger allowlist now includes Reporter de99c8f SHA with 313 moves because the R9→R10 diff contains no moved facade/owner/ledger changes; **the new SHA case has not been executed during this authoring turn**. Run 13 designed guard cases normal and python -O with the R10 checked-out candidate; add an explicit mutation on an unmoved function in trade_report_ai.py, module-level executable statement, wrong import target, wrapper arg or extra statement, extra numbered-owner file and Broker authority path. Reject every mutation. Keep original historical T3 stage-end constraints untouched and do not accept the prior path-only v4 allowlist.

## 4. Shared P1 Monitor T3/T4 closure

Source of truth: docs/refactor/work_projects/evidence/monitor/continuous/shared_contract_proposal.json at Monitor efdab64f.

Fourteen exact legacy whole-module paths now point via strict module identity shim to canonical Owner modules. Follow ONLY these exact pairs after strict identity-shim AST verification; never assume all libs/runtime/monitor modules may be followed and never permit extra arbitrary import/statement. Eight facades contain twenty named body moves: reconstruct ENTIRE original module AST and exactly prove selected owner bodies + forwarding wrappers, while protecting unselected definitions/module statements. Keep use-time facades/aliases/tuple shapes/ordering/exceptions.

Original current-head T3 observed two FAIL, T4-B three FAIL on earlier Monitor code SHA; fail-fast lookup may hide more. Run full suites after fixing first mappings, enumerate newly surfaced failures and fix only legitimate relocated-path conflict. Keep negative authority/guard checks and original historical stage-end tests.

## 5. CI required after assembly (mock-only)

- Reporter: tests/test_work_reporter_seed_migration.py; tests/test_work_reporter_r4_facade_bodies.py; tests/test_work_reporter_r8_read_contracts.py; tests/test_work_reporter_r8_read_via_callback_parity.py; tests/test_work_reporter_renderer_bytes.py; tests/test_work_reporter_r10_retained_io_contracts.py; tests/test_work_reporter_r10_artifact_parity.py; tests/test_p152_facade_symbol_ledger.py; reporter facade AST restoration guard + negative tests.
- Monitor: tests/test_work_monitor_role_contracts.py; test_work_monitor_continuous.py; test_work_monitor_body_views.py; test_work_monitor_observation_views.py; test_work_monitor_exit_labels.py; test_work_monitor_policy_trace_views.py; test_work_monitor_annotation_views.py; test_work_monitor_scope_accounting.py; original T3/T4 and native T4-B/intent-only/guard/cascade/cooldown/sizing/price/source tests.
- Shared authority: P1.5 T1/T2/UEF and scanner compatibility tests; exact agent-package allowlists reporter:{narrative,read_models}, monitor:{events,projections}; negative Broker/Executor/Supervisor leakage, no CI skip/xfail/re-pin/wildcard.
- Environment: Linux Python3.12 with git fetch-depth0 and dependency venv, native Windows Python3.12/3.13 where supported, normal and python -O, isolated TEMP/TMP/TMPDIR pytest artifacts outside repo. Do not treat pre-existing UEF environment failures as passed or waived; record same-env baseline evidence.
- Synthetic Reporter JSON/Markdown/API output-byte parity, Monitor full-mod1 native replay if budget permits (previous Monitor proof sampled mod4); hosted CI exact candidate SHA and rollback rehearsal. Real persisted/LLM nonproduction-only after separate access/evidence approvals. No live brokerage/production writes.

## 6. UI patch note and Git history hygiene

Verified UI reader: apps/api/adapters/patch_notes.py -> docs/trading_agent_patch_notes_detailed_update/patch_notes.json. Its schema needs entry_count == len(entries), required entry fields including status=current|historical, and corresponding Markdown + technical daily patch notes. Verify tests/test_patch_notes_sync.py and tests/apps/api/test_patch_notes.py. Publish actual truthful refactor milestone only after integration candidate is accepted for that milestone, never label proposed notes as deployed. Correct Reporter proposal's misleading controlled_mock_lane_report BLOCKED to the Work decision: Reporter presentation/read adapter, intentionally retained; 313 moved bodies include READ_VIA_CALLBACK (not all pure).

Reporter commit c5d004b accidentally included 4 binary Windows cache objects under literal %SystemDrive%. They are removed from HEAD de99c8f (GitHub comparison verified), but **remain reachable in Git history**. Treat binary contents as unverified until offline confidential-data triage by authorized owner. If sensitive, escalate and coordinate explicit approved history clean-up; don't force rewrite role refs or erase evidence on your own.

## 7. Acceptance / next actions

P1 shared gates close only when original full current T3/T4 tests are actually GREEN on exact assembled candidate, historical checks preserved, all negative mutation tests reject corruption normal/-O, and Work records commands/platform/run SHA. Until then Reporter=LOCAL_READY_CANDIDATE / ROLE_PARTIAL, Monitor=LOCAL_SAFE_SCOPE_SUBMITTED / ROLE_PARTIAL; main merge forbidden.

Immediate Work next action: assemble exact role trees on isolated machine or supported Work computer, reconcile overlaps, implement shared strict T3/T4 + package/CI changes, execute. No mere document is a substitute for running these tests. If this session cannot execute private repo/test environment, leave integration implementation status NOT_RUN with exact SHA/blocker, not 'green'.

Other roles Strategist/Scanner are not silently activated; define separate whole-role programs after Reporter/Monitor gates and review acceptances. Full P1.5 main merge requires all roles and explicit operator go-ahead.
