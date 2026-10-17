# Monitor M9 — Verify That Scope Is Really Exhausted Before Parking

**Date:** 2026-10-17 KST. **Actor:** Codex only, Monitor role. **Code HEAD:** efdab64f33b34be6ab26fd8edb9aba9ec4ebd479; runtime frozen SHA 800841f229606c419dae67b0d6f794b9238676e9 (refresh before work).
**Branch:** work/monitor-role-20261017. **Reviewer:** Work. **Issue:** #12. **Shared T3/T4 integration:** Work #14, not Codex.

## Why CP-007 does not itself prove whole-role work exhausted

CP-007 attests that 14 whole blobs and 20 named body moves were made and that currently triaged safe extraction candidates are exhausted. It does NOT independently prove that every retained symbol lacks safe structural opportunities. Current inventory has 100 modules/428 symbols, 59 source modules retained at BASE bytes, 55 patch primitives, 302 entries labeled SAFETY_LOCK across multiple categories (including 14 orchestration, 92 exit/price/state, 38 signal policy, 45 entry signal, 109 shared policy, 4 exit precedence), and two intentionally retained small DTO helpers. These are *classification counts*, not observed defects or an independent justification for every exclusion. Do not count moved functions as role-finished percentage.

Do NOT repeat the entire historical 14+20 migrations or run old full suites without a specific new proof gap. Do NOT move a protected function solely to keep the CLI busy. Aim at useful independent Monitor work and evidence, bounded by the safety contract.

## M9-A — Challenge the retention classification with call-graph evidence (read-only first)

Generate a stable diff-scoped per-symbol review for the 59 retained BASE-byte modules, especially candidate presentation/observation/projection modules: libs/runtime/monitor/signal_score_projection.py, libs/runtime/monitor/signal_features.py, libs/runtime/monitor/entry_cascade_projection.py, libs/runtime/monitor_exit/preview.py, libs/runtime/monitor_exit/exit_policy_pnl_projection.py, and the large monitor_node/policy/exit modules. These are *inspection candidates only*, not approved move targets.

For every meaningful function, record: original path/name; callers and import/monkeypatch entry points; output consumed by decisions or presentation only; global dependencies, side effects/mutations/time/IO; authorization boundary; current tests; effect/identity parity proof; should move? SAFE_PURE_CANDIDATE, RETAIN_MATERIAL_AUTHORITY, RETAIN_COMPAT, NEEDS_WORK_DECISION, or UNKNOWN. Reference exact AST and consumer evidence, not names/tokens alone. Inspect the two small DTO helpers for whether leaving colocated is justified; do not split artificially. Surface misclassified pure helpers as a concrete next READY batch; if none found, say zero with per-symbol evidence.

## M9-B — Execute proven structural changes ONLY within existing authorization

If M9-A finds genuinely independent pure/read-only observation or formatting groups outside the protected policy/decision chain, move cohesive groups under the existing P1.5 semantic-preserving mandate. Preserve original complete module AST (unmoved functions, statements and import-time effects), facade ABI/import identity, late-bound callbacks, exception and alias/effect order. Owner <=350 LOC. Add BASE-first deterministic fixtures plus normal/-O malicious mutation negatives. Then run impacted policy/intent/guard consumers and commit/push a reversible batch. Do not touch policy thresholds, price/clock/ranking/sizing, exit priority, truth precedence, OrderIntent or broker authority even when a helper looks simple. Anything decision-consumed or needing a path exception gets a Work narrow decision request, not an implicit edit authorization.

## M9-C — High-value remaining tests, independent of any new extraction

1. Investigate the full native monitor T4-B replay inventory (previously 2,879 variants with 689 sampled mod4), decide whether an isolated full-mod1 replay is tractable within budget and record PASS/FAIL/NOT_RUN. Avoid redoing old mod4 runs.
2. Run Python 3.12 Linux compatibility in the available mock-only environment if present; otherwise prepare exact reproducible dependency and command contract for Work and mark NOT_RUN. Prior final-runtime 560 PASS are Windows Python 3.14.2 developer evidence, not Linux CI.
3. Add/complete bounded synthetic persisted Monitor artifact consumer parity: exact OrderIntent DTO/field order and identity, event/observation serialization, error handling, missing/stale/partial inputs. Use temporary fake state and reports only, never production files or actual broker/LLM calls.
4. Add safety-negative coverage for retained policy/guard surfaces where it contributes a test that fails on a realistic unauthorized mutation, including exit reason priority, rank/candidate fallback, cooldown, sizing, guard override, Broker-call leakage, before/mid-call patching. Do not alter policy to pass tests; no unnecessary duplicate suites.
5. Reconcile actual UI-linked patch-note source for Work integration via a proposal only; don't publish shared runtime UI code on Monitor branch.

## M9-D — Hand off EXACT shared-contract needs without waiting

Work already owns and must independently resolve the five RED shared T3/T4 AST owner-path failures on an isolated combined candidate. Continue M9-A/C while it does so; do not edit shared gate tests or Reporter branch. After Work produces tested T3/T4 fix, inspect pinned candidate and perform limited Monitor-local compatibility verification. If Work finds a regression in Monitor-owned source, fix it on your own branch with direct evidence and have Work re-audit. Keep current Issue #12 up to date.

## M9-E — Exit states and truthful continuation

Checkpoint after each coherent M9 batch: exact source/commit SHA; classification coverage; new proof/negatives; tested commands and platform + PASS/FAIL/NOT_RUN; current inherited shared reds; next 2 independent READY packets where possible. Issue-write failure must not stop local work: push a versioned issue-ready handoff without token harvesting.

Only after M9-A and M9-C have been executed or individually blocked with concrete environment/proof explanations, M9-B has no demonstrably safe candidates, and fresh Work Issue #12 feedback adds no Monitor-local tasks may Codex park as MONITOR_LOCAL_READY_FOR_INTEGRATION. This is not Monitor ROLE_READY, full P1.5 complete, CI green or permission to merge main. Work has the next shared-contract critical path. A new CLI process requires a real explicit launch/persistent supervisor; GitHub docs alone cannot run between sessions.

## Strict no-go

No Broker/Executor/Supervisor live authority, real trading, policy/guard/sizing/cooldown/priority/truth/Q10/Q12/Step5C semantic changes, LLM or production artifact writes, unauthorized GitHub credentials, CI skip/xfail/wildcard, arbitrary path exemptions, forced merge/main, or destructively clearing worktrees.

## Ready-to-copy bootstrap

AGENTRA CODEX MONITOR CONTINUATION. Resume work/monitor-role-20261017 at verified remote SHA (previously efdab64f33b34be6ab26fd8edb9aba9ec4ebd479). Read the design-branch docs/dev-team/assignments/08_CODEX_MONITOR_M9_CONTINUATION.md and Issue #12 latest Work review without merging design. CP-007 moved-code scope is frozen but does not independently prove all Monitor validation and reclassification work is done. Execute M9-A callgraph/symbol-level retained-boundary audit, M9-B only if a truly safe pure group is proven, M9-C targeted new parity/full native/Linux proof, and M9-D follow up Work shared contract. Push exact-SHA checkpoints and automatically take next READY Monitor packet during your active CLI session. Never move decision-authority code or change policy to keep busy. Codex ONLY Monitor; Work owns shared T3/T4 and Reporter integration; Claude ONLY Reporter. Park only after all current safe Monitor-local packets done or evidence-blocked. No main merge.