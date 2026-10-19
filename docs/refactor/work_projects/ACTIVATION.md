> **HISTORICAL RECORD ONLY:** 2026-10-17 activation text below is NOT authorization for a new CLI, Reporter/Monitor session, branch, production order, or code change. Consult [work_projects README](README.md), [CURRENT](../work_orders/CURRENT.md), and [#20](https://github.com/hbombheart1230-dotcom/agentra/issues/20). Original record follows unchanged.

# Agentra role projects — activation and worker handoff

User authority: "진행시켜", 2026-10-17 11:09 Asia/Seoul. IMPLEMENTATION AUTHORIZED for the bounded whole-role structural projects below; external workers NOT_STARTED until observed startup evidence. No user approval required per internal batch, normal test repair or normal role-scope continuation.

## Pinned baseline and branches
Runtime/evidence BASE: `d773709ba2f70471fad9badba4f92400f7818319` (T4 run 38990895599, Reporting/Web 38990895679, Scripts 38990895597 all SUCCESS). PERF-1 782 cases 157.67->49.07 sec; PERF-2A 3 cases 111.78->7.00 sec. These are local subset improvements, not CI-wide percentages. Reuse evidence, do not reproduce completed PERF work.

| Owner | Role | Write branch | Independent reviewer |
|---|---|---|---|
| Claude | Reporter whole-role structural project | `work/reporter-role-20261017` | Codex on pinned Reporter SHA |
| Codex | Monitor whole-role structural project | `work/monitor-role-20261017` | Claude on pinned Monitor SHA |
| Work | Shared contracts, docs, notes, serial integration | `integration/p15-t4-pr5-convergence-20261015` | Role changes retain the independent reviewer above |

All three start at the same activation commit: resolve the initial branch commit whose message is `docs(work): activate Reporter and Monitor whole-role projects from d773709`. Runtime BASE remains d773709; source/test/tool parity hashes are checked against it. The common docs commit adds no runtime/test/workflow code. Pin and record the exact branch-start SHA at worker startup; do not use a moving HEAD as BASE.

## Minimal startup
Use an isolated separate clone, not operational C:\Agentra and not another worker's directory. Verify origin points to hbombheart1230-dotcom/agentra, actual branch/HEAD/status/worktrees and expected activation ancestry. Preserve all unknown dirty/untracked content. Fetch and use only the assigned branch; do not force push, reset/clean others' files or modify production.

Read CURRENT -> this file -> OPERATING_RULES -> assigned project + SEED_LEDGER. No historic work-order reread/full inventory. Within own-role scope, build a responsibility disposition register and begin the approved seed batch, then extend pure role batches continuously as allowed below. Do not stop after 8/10 files or ask permission per small batch. Do not require Work to be online for routine ledger expansion.

## Exclusive worker writes
Reporter: exact eight Reporter seed pairs plus proven pure Reporter-owned legacy modules under `libs/reporting/`, excluding `evaluation/**`, Research/Q-series and all effects. New canonical bodies under `libs/agents/reporter/`; new subpackage destinations must match real ownership and the frozen tree. Actual writer/queue/lock/memory-persistence/LLM execution and `live_execution_bundle_runner.py` / `reporter_bundle_runtime_parts/**` remain protected. Additional facade decomposition and stable-call-site rewrites are NOT a free wildcard: submit as a separate named ledger batch with parity proof; do not change behavior, report generation policy or graph/service endpoints. Do not mass-move shared reporting infrastructure. Unnecessary report review is a decision ledger only: no disabling/deleting reports.

Monitor: exact ten Monitor seed pairs plus proven pure observation/context/evidence/projection owners under `libs/runtime/monitor/` into `libs/agents/monitor/`. Exclude actual entry/exit decisions, eligibility/guard/cascade selection/trigger logic, position/cooldown persistence and `libs/runtime/monitor_exit/**`; no authority movement. State mutation/aliases and callback effects must be proven, not inferred from names.

Each worker may write only own exact registered legacy/canonical paths, own `tests/test_work_reporter_*` or `test_work_monitor_*`, own `tests/fixtures/work_reporter/**` or `work_monitor/**`, own `scripts/refactor/work_reporter_*` or `work_monitor_*` if needed, and its exclusive `docs/refactor/work_projects/evidence/reporter/**` or `monitor/**` (including path ledger, proposed patch-note entry, commands, tests and handoff). No empty placeholder packages/tests. No modifications to the other lane.

Shared protected paths: graphs/**, apps/**, config/**, deploy/**, .github/workflows/**, existing shared tests, root conftest/sitecustomize/pytest/requirements, source-inventory/architecture authorities, scanner/strategist source, risk/approval/supervisor/execution/kiwoom/llm, Step5C/UNKNOWN/UEF/Q10/Q12 and operational reports/data. Shared CURRENT, AGENTS/CLAUDE/COMMON_RULES, STATUS.json, official UI notes and non-role evidence belong to Work. A shared gate mismatch is reported with exact failing ID/mapping; worker does not relax it. Continue independent safe batches.

## Execution, audit and handoff
Run blob/strict-shim/import/patch/frozen-output checks per coherent batch, impacted existing contracts locally; no full CI duplication per file. Never thread-parallelize global monkeypatch suites. Each process/run has unique TEMP/TMP/basetemp; preserve the integrated safe PID cleanup and bounded immutable caches. Do not edit PERF infrastructure. Record actual PASS/FAIL/SKIP/NOT RUN, and base/tool/fixture/env provenance. Final role handoff is an immutable commit SHA and pending independent audit, not self-certified completion. New owner LOC follows existing 350-line policy with explicit debt.

At implementation readiness, push only own role branch and record `READY_FOR_AUDIT` plus BASE/START/FINAL SHA, exact delta and responsibility register in own evidence. The other worker reviews that pinned SHA in a separate read-only clone/session; do not edit the implementation while auditing. Implementer fixes findings on its branch; reviewer records exact re-reviewed SHA and never reports own edits as independent proof. If reviewer is still implementing, queue audit; continue own authorized work without holding both roles hostage. No live trading/LLM/production writes.

Work serially imports approved role changes, reconciles shared strict tests and appends both official UI note formats. Workers supply one unique proposed note entry; no parallel official-note overwrite. Use existing required CI commands/platforms on the final integration SHA, with explicit role-test wiring. Use the EXISTING integration branch and its required hosted workflows. Integration push triggers its normal CI; do not dispatch duplicate runs, create another controller branch or change workflow triggers merely for this activation. No test weakening, ZIP CI or automatic main merge. User main/deployment/safety approvals remain mandatory.

## Inherited findings and status
Keep PERF-2A huge-int price OverflowError P3; NTFS mtime P2; historical 37 failures/provenance; V3/Q-series P2; actual LLM/persisted-report parity; P1.5 final acceptance open. Missing real parity stays NOT RUN/BLOCKED, never synthetic PASS. These are carried debts, not permission to restart PERF or silently erase them. Role acceptance must distinguish structural scope from full P1.5 approval.

The P15-058 user handoff closes that implementation cycle; historical audit-pending lines below other files are provenance, not a demand to rerun it. No new independent P15-058 audit is invented. P0/P1/safety issue: stop affected work, preserve evidence and report immediately; unrelated safe work continues. Existing reports at 00/06/12/18 KST never impose an execution pause; no new scheduler/server/merge bot.

## Minimal branch lifecycle
Exactly three active development lanes: existing integration controller plus Reporter and Monitor. main is preserved separately. No new wave/per-batch/ZIP branches. Old planning/design/performance refs are evidence or retirement candidates, not active development lanes. Before retiring a role branch: independently accepted pinned SHA, exact selective-import coverage for all approved source/evidence, no unique needed commits or dirty/untracked worker material, no active worker/PR dependence; archive valuable evidence before deletion. Do not use an ancestry-only check for selective imports. Never auto-delete other people's or unknown dirty worktrees.

A redundant empty `work/role-integration-20261017` ref was created during setup at runtime BASE before the minimal-branch steering. It is NOT an active lane, must receive no commits, and is eligible for deletion only if it still equals d773709 and has no consumer. Work will not claim it deleted without a successful GitHub deletion.
