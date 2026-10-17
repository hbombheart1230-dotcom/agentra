# CODEX — Independent Auditor, Contract/CI Integrator and Runner Engineer

**Mission:** Execute independent Reporter/Monitor audits, harden shared safety contracts, implement a non-trading runner candidate, and prepare multi-role integration. Don't wait for the entire Reporter role to close before beginning independent work.
**Repository:** hbombheart1230-dotcom/agentra
**Reporter SHA:** 8ce327ecc71c4c92074c1fa5fb6f00428ba9279b (re-fetch)
**Monitor SHA:** a33c28780592917481eb610a3d69c3948e4a4ead (re-fetch)
**Read-only design:** origin/design/agentra-dev-team-loop-20261017
**Audit inbox:** https://github.com/hbombheart1230-dotcom/agentra/issues/14
**Role inbox:** Reporter #11, Monitor #12
**Codex-written changes reviewer:** Work. Never self-certify your own integration patches.

## Workspace and scope

- Work in isolated clones/worktrees and branch-specific directories; inspect existing refs and dirty files before new branches. No changes to work/reporter-role-20261017, work/monitor-role-20261017 or main, no force push, no active Claude worktree modifications.
- Separate audit evidence, shared-contract integration proposal and runner implementation branches. Only create branches genuinely needed; keep branch inventory small. Existing integration branch is not approved for main merge.
- All tests mock/nonproduction. Never modify Broker/Executor/Supervisor live approvals/guards, truth-source precedence, Q10/Q12, UEF/Step5C semantics, LLM route/retry/billing, secrets or production data.
- GitHub issue write unavailable? Keep versioned handoff and ready-to-post comments in your own branch without harvesting auth credentials. Other safe packets must continue.

## D0 — Independent Reporter R7 evidence and regression audit

Read actual remote R7 HEAD, Reporter handoff, r4_facade_ledger.json, facade_symbol_ledger_v2.json, function_blockers.json, historical pinned R3 tests, seed scope and R4 body proof tests. Independently inspect:
1. unique total moved function bodies 264=14+56+66+128 over 21 modules, exact facade/owner mappings and owner size <=350 lines;
2. original signatures/decorators/docstrings, callable identity where contracted, AST after removing facade-qualification, use-time lookups, closure and module identity, import-order and before-call/callback mid-call monkeypatch;
3. exact report JSON/Markdown byte, key order, exceptions, side effects and fallback behavior with offline fixtures;
4. permission/scope test closed paths plus negative unexpected-file mutations and forbidden broker/execution/LLM surfaces;
5. reported Python 3.13 tests (R4 proof 1,351 PASS; -O 1,425 PASS; focused runs R4=1,407/R5=1,722/R6=1,845/R7=1,533) as reported only until you run them;
6. 8 UEF2A and 2 UEF5_1 reported pre-existing failures: reproduce under equivalent base and deps; otherwise mark NOT_VERIFIED.

Attempt required CI Python 3.12, the local 3.13 interpreter, -O, native Windows when available and 3.14 only if supported. Label unavailable suites NOT_RUN. Post exact-SHA audit to Issue #14 and any actionable defects to Reporter #11. AUDIT_PASS only for examined scope/SHA and actual tests, never blanket P1.5 completion.

## D1 — P1 T3 facade safety: do immediately in isolated proposal

**Known vulnerability in proposed shared patch R4_T3 v4:** file-path allowance includes whole protected facade paths trade_report_ai.py and trade_report_markdown_clean.py. A mutation in an UNMOVED function in one of these paths could pass current-head path guard while preserving the 264 moved-body proofs, original names/signatures and current ledger.

Required work:
- Preserve historical pinned T3 intent, forbidden authority checks, and historical BASE window. If historical comparison is re-pinned, guarantee a separate current-head test covers all later protected surfaces at least as strongly; no skip, xfail, fail-open, or wildcard path acceptance.
- For approved facades compare AST of every UNMOVED top-level function/class/decorator/default and executable module-level statement against BASE; whitelist only proven R4 wrapper transformations with explicit facade→owner mapping and strict import constraints.
- Add negative SAME-PATH mutation of an unmoved facade function body without changing name/signature and require failure. Add module-level change, owner-body mutation, unexpected numbered bodies file, unapproved facade, and Broker/Executor path negative tests. All must fail; actual 264-move legitimate tree must pass.
- Ensure no import-time callable snapshot, changed closure semantics, dynamic-import side effects or hidden approval bypass.
- Apply only to scratch candidate with SHA and exact-path manifest. Re-run historical T3, new T3 and focused Reporter suite. Work independently reviews your candidate before any integration adoption.
- If a safety tool blocks a proposed test edit, never bypass it. Record exact decision-needed diff, continue D2/D3 and request normal authorization.

D1 acceptance: exact same-path unmoved-body negative fails as intended, actual R7 positive passes, historical safety strength preserved, no new runtime authority. Existing T3 v4 alone does not satisfy this acceptance.

## D2 — Cross-role shared-contract and CI integration rehearsal

Reporter-proposed shared_contract_patch_R4.diff includes Monitor-specific allowlists/tests. Monitor tests aren't necessarily present on Reporter head. Assemble exact Reporter and Monitor verified SHAs only on separate integration candidate; do not add missing Monitor tests on Reporter branch.

- Gate exact role package sets reporter:narrative/read_models and monitor:events/projections only after both roles actually exist in the candidate.
- Verify Monitor T3/T4 shim pairs with strict identity AST verifier; forbid lazy wildcard following or permissive masks.
- Wire both Reporter tests into REQUIRED CI: tests/test_work_reporter_seed_migration.py and tests/test_work_reporter_r4_facade_bodies.py. Add tests/test_work_monitor_role_contracts.py only after the candidate includes it.
- Verify historical P1.5 T1/T3/T4, UEF, DTO, negative authority, UI patch notes and report consumers; Linux Python 3.12 and available Windows/Python 3.13/-O. Record exact failures and baseline comparison, never blanket waiver.
- Keep candidate unmerged while Reporter is PARTIAL_WITH_BLOCKERS or other P1.5 roles not frozen. A rehearsal is not production approval.
- Work independent review is mandatory for Codex-authored shared-contract changes; operator decides final main integration after full P1.5.

## D3 — Mock-only persistent engineering runner (separate lane)

Read 04_PERSISTENT_RUNNER_SPEC.md. Implement testable runner on a separate branch with no trading runtime integration and no production order credentials.

Deliver:
- validated config for workers (role, repository, issue ID, owner branch), explicit daily cost/token/concurrency caps and STOP flag; fail closed if caps unset;
- process supervision, session exit/crash detection, checkpoint resume from verified pushed SHA, lock/lease to prevent two workers owning same branch, backoff and bounded retries;
- GitHub issue poller with allowlisted authorized authors and monotonic comment IDs, finding ID dedupe and no arbitrary commands from comments;
- isolated logging, artifact cleanup, mock local test harness, one daily digest generator;
- tests simulating abrupt termination, repeated comment, stale SHA, network 401/429, push conflict, dirty worktree, budget exceeded, P0 stop, and no issue-write capability;
- operator runbook for Windows local deployment and manual off-switch/rollback.

Don't invent an API for starting ChatGPT Work: Work windows still require supported explicit Work invocation/configured schedule. Runner can queue SHA-bound audit packets for Work to read, but cannot claim to start Work sessions without a real integration.

**Deployment is a separate user authorization.** This order authorizes mock-only implementation and validation, not always-on launch or execution on a production trading host.

## D4 — Continuous useful audit queue

After D0–D3, continue:
- review only NEW Claude Reporter SHAs and acknowledge resolved findings with acceptance evidence, without blocking each batch;
- audit Monitor current SHA, especially Monitor intent-only and entry/exit policy parity;
- prepare Strategist then Scanner whole-role acceptance tests and dependency maps (read-only until separately approved source ownership);
- analyze persisted-report read parity, Windows LF/CRLF and Python version differences, UI-connected patch-note correctness, failure evidence retention, hermetic CI;
- maintain integration conflict map, staged mock regression suite and rollback steps. Do not repeatedly run full unchanged tests simply to consume credits.

## Repeating work and audit checkpoint format

At each coherent milestone: targeted verification -> commit/push isolated proposal -> exact SHA and tests -> issue review entry -> choose next ready audit or runner task. The presence of an audit checkpoint is not a stop signal.

    AUDIT_ID: P15-CODEX-NNN
    TARGET_SHA: <actual>
    BRANCH_AND_PROPOSAL_SHA: <if any>
    RESULT: AUDIT_PASS / AUDIT_REWORK / NOT_RUN
    CHANGED_PATHS_AND_SYMBOLS: <exact list>
    TESTS: <command, exit, PASS/FAIL/NOT_RUN>
    NEGATIVE_MUTATIONS: <old/new guard comparison>
    PREEXISTING_FAILS: <same env base evidence or UNKNOWN>
    OPEN_FINDINGS: <P0/P1/P2 + reproducer>
    NEXT_READY: <at least 2 packets if available>
    REQUESTED_WORK_REVIEW: <issue or PR link>
    MAIN_MERGE: NOT_AUTHORIZED

No mass temp files in repo, secrets in logs, or unbounded test retention. When budget/process ends, leave next SHA and restart plan; otherwise continue through D0–D4 safe queue.

## Ready-to-copy Codex CLI bootstrap

AGENTRA CODEX INDEPENDENT QA AND INTEGRATION ENGINEER. Fetch/read 00_FULL_TIME_TEAM_CHARTER_20261017.md, 03_CODEX_FULLTIME_ORDER.md, and 04_PERSISTENT_RUNNER_SPEC.md from origin/design/agentra-dev-team-loop-20261017. Inspect GitHub Audit Issue #14 and Reporter Issue #11 at exact current remote Reporter SHA (previously 8ce327e), plus Monitor #12. Work only in isolated audit/shared-contract/runner branches, never active worker branches or main. Execute D0 independent audit, D1 T3 same-path unmoved-body hardening with mutation negatives, D2 integration rehearsal after actual cross-role SHAs, D3 mock-only durable runner and D4 ongoing audits. Post exact SHA evidence, request Work review of your authored patches, pick next safe task automatically. DO NOT ask human after each checkpoint. NEVER weaken safety gates, touch trade authority, merge main or auto-activate an unattended runner.
