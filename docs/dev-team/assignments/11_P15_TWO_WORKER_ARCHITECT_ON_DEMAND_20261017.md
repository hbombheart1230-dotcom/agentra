# Agentra P1.5 — GPT Architect on Demand + Claude/Codex Two-Worker Delivery

> **R11 architecture delta (2026-10-17):** Reporter `443f90362ad5970a4731685311a45e8e0f6b55e4` and Strategist read-only draft `d8b34e669e1c43342eadd80b13ea43aac4bc255b` were inspected. GPT approved only [Strategist S1/S2 evidence and bounded offline tests](13_STRATEGIST_S1_S2_SCOPED_CHARTER_20261017.md), not S3-S6 source refactors. Reporter R11 shared F1/F2 owned by Codex on isolated integration as [architect-designated](../integration/R11_SHARED_FAILURES_F1_F2_ARCHITECT_DECISION.md), Claude independently audits. Reporter full suite still has reported historical/shared 1 FAIL; Linux CI NOT_RUN. Hourly Work automation remains DISABLED.


**Effective:** 2026-10-17 KST. **Authority:** supersedes contradictory Work-as-always-on / Work-shared-implementer clauses in older `00`, `01`, `02`, `03`, `05`, `10`, and docs/dev-team/DEVELOPMENT_LOOP.md. Old records remain historical evidence, not active instructions.
**Repo:** hbombheart1230-dotcom/agentra. **Design reference:** design/agentra-dev-team-loop-20261017.
**Operating premise:** ChatGPT Work's hourly monitoring automation was explicitly disabled on operator request; do NOT recreate/schedule it or treat Work as a live process. GPT in **ordinary chat on demand** remains architect, technical lead, design owner and final architecture judge. This does not mean that a ChatGPT chat continues working between user requests.

## 1. Who does what, right now

| Function | Responsibility | Permission & proof |
|---|---|---|
| **GPT (ordinary chat, on demand)** | P1.5 target architecture, role contracts, disputed design decisions, high-risk adjudication, planning next whole roles, accepting final evidence/ordering | Publish SHA-bound decisions to design branch or issues when explicitly invoked; no automatic recurring review, no direct trading authority, no main merge |
| **Claude (worker 1)** | Reporter on `work/reporter-role-20261017`; independent code review and test of **Codex-authored shared integration candidate** after Reporter local freeze; then Strategist read-only mapping | Do not edit Codex's integration branch; produce SHA-bound audit/repro in separate reviewer branch or Issue #14. Fix Reporter defects on Reporter branch only |
| **Codex (worker 2)** | Monitor on `work/monitor-role-20261017`; **after Monitor-local safe packets are complete or truly blocked**, implement shared Reporter+Monitor **T3/T4/agent-package/CI/UI integration** on a separate integration candidate; then Scanner read-only mapping | Codex owns shared integration changes, but **cannot self-approve** them; Claude must independently test/review. No Reporter/Monitor active-branch cross-write |
| **Operator (user)** | Direction, any new live-trade/policy/authority approval, budget/host/credential activation, full P1.5 main-merge approval | No per-batch relay or routine approval needed for proven scope-preserving tests/refactors |

**Important separation:** Codex finishes or parks genuine Monitor-local safe work first; it does **not abandon Monitor mid-batch** to become full-time Reporter reviewer. Once at local acceptance candidate, Codex can work on isolated integration. Claude similarly can independently review integrations after Reporter local freeze without redoing the entire Reporter source tree. Work in ChatGPT is OPTIONAL when the operator explicitly launches it, never required for the normal two-worker code path.

## 2. Exact current handoff SHAs (refresh before work)

- Reporter `de99c8f0fa66bfc3e6be9a229f04fc6aad5ca06e`: R10 local-ready candidate, **313** migrated bodies /23 facade paths /41 owner files; 47 retained functions offline-characterized; 22 excluded authority/name-related items; no shared T3/CI closure. Issue #11.
- Monitor `4bc4250844093050438d8a9c29f5842991ad1c3a`: M9 CP-008 full native mod1 replay and persisted/safety negative evidence added to runtime `800841f229606c419dae67b0d6f794b9238676e9` (14 whole-module moves +20 named functions). M9 retained-symbol review may still be ongoing; refresh Issue #12.
- Shared five T3/T4 failures (2 T3 and 3 T4-B) are **known RED** on an earlier exact combined-contract Monitor SHA. They are path/AST integration contract problems until a full new candidate rerun proves otherwise. Treat later hidden failures as possible, not waived. Shared queue Issue #14.
- Existing design proposal `docs/dev-team/proposals/reporter_facade_guard.py` and test file have a proven R9 path-based same-facade unmoved-body negative; R10 pin was proposed but NOT run at R10 in the last review. Read `docs/dev-team/integration/REPORTER_R10_MONITOR_CP007_WORK_GATE_20261017.md` for precise acceptance.
- `main` baseline `2f95bba429636ee15ae9a399cc4ff7c4e6dcd5cb` was unchanged at this handoff. **Absolutely no early main merge.**

## 3. Continuous task queue and role switch — without routine GPT/Work approval

**Claude Reporter lane:** keep Reporter frozen as local-ready candidate unless new SHA-bound Reporter defect appears. If there is a relevant new integration defect, fix it on the Reporter branch with tests and post issue evidence. Meanwhile independently review Codex's integration PR/branch from a clean checkout or its own reviewer branch. Read-only Strategist consumer/owner/test mapping is allowed during integration waiting, but do not write Strategist runtime source until GPT publishes a bounded whole-role source charter.

**Codex Monitor lane:** finish the M9 retained 359-symbol classification (or record exact exclusions) and any safe independent Monitor regression tests still READY, without make-work. Post local freeze with test matrix and open shared-contract blockers, then automatically select **shared integration** as the next approved work packet. No need to wait for hourly Work or a new routine user message.

**Codex shared integration lane (the immediate critical path):**
1. On a new isolated candidate branch assemble **exact** Reporter and Monitor HEADs, recording both SHAs and merge overlap/conflicts; do not overwrite active branches. If tree overlap is ambiguous, issue GPT decision request and continue safe independent work.
2. Replace legacy T3/T4 current-head resolver assumptions with **strict exact mappings**: 14 Monitor legacy whole-module identity shims → canonical modules and 20 named moves across 8 facades, with full BASE AST reconstruction covering all unmoved functions/constants/statements; preserve historical stage-end tests. Reporter 313 wrapper facades require exact whole-module BASE restoration, strict approved imports and owner body/use-time proofs. Forbid blanket path allowlists; same-path unmoved-function mutation must fail.
3. Run original full T3/T4 suites after each mapping repair to expose further failures, and retain negative normal/`python -O` probes: illegal import or raise, redirect, duplicate or changed shim, unselected body change, fake Broker capability, changed owner body, missing facade alias. Zero suppression, no skip/xfail, no CI re-pin, no historical weakening.
4. Wire BOTH Reporter seed and moved-body tests and R8/R10 parity tests, Monitor role-native/intent/cascade and current gates, exact agent package allowlists, Linux Py3.12 and supported Windows/`-O` jobs. Runner/test temporary output must be session-isolated; bounded failure retention. If a dependency is unavailable, `NOT_RUN` with command, never green.
5. Reconcile actual UI-linked patch note store `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` and Markdown + `docs/daily_patch/` archive only for verified integration milestone, keep exact `entry_count` and tests green. No premature deployed claim. Distinguish intentionally retained Reporter `controlled_mock_lane_report` from unresolved and do not describe all 313 migrated bodies as pure.
6. Prepare exact diff, commit SHA, deterministic commands/results, rollback, conflict resolution and independent-review request on Issue #14. **Do not merge main.**

**Claude independent review lane:** review Codex integration diff and pinned inputs from scratch, not merely the issue summary. Reproduce core T3/T4, R8/R10 Reporter, Monitor intent-only safety, negative mutation and CI evidence in the accessible environment. Post `AUDIT_PASS`, `AUDIT_REWORK`, or `NOT_RUN` against exact candidate SHA with repro. Codex fixes shared candidate; Claude does not write its implementation. If a Reporter-specific bug is proven, Claude repairs own branch and Codex reassembles/pins new SHA.

**GPT architecture loop:** user invokes ordinary chat when a P0/P1 dispute, scope disagreement, trading-policy authority question, new role charter, or final milestone decision merits it. GPT reads Issues #11/#12/#14 and actual commit SHAs, records a concise SHA-specific ruling in GitHub, and avoids rereading every completed historical task. GPT designs Strategist/Scanner next whole-role packets when requested, using developer read-only inventories; no recurring automatic call or invisible background promise.

## 4. Role relay after this joint milestone

Once Reporter+Monitor combined T3/T4/CI passes with independent Claude verification, keep the integration candidate separate and keep the final main merge deferred until ALL P1.5 roles are done.

- Claude may transition to **Strategist** full-role refactor after GPT creates an exact architecture/ownership/acceptance charter and designates a separate source branch; before that, read-only mapping only.
- Codex may transition to **Scanner** on the same condition, with a separate branch; before that, read-only mapping only.
- Work of Commander, Supervisor, Executor is high authority: begin only with role-specific plan and clear forbidden trading/guard semantics. No auto transfer of execution permissions.
- The user authorizes the **one final main merge** after P1.5 combined testing, rollback plan, UI notes and a SHA-pinned independent audit.

## 5. Stop, safety and cost

- No actual trading, position/state write, live broker/Executor/Supervisor changes, Step5C or UEF authority edits, Q10/Q12 strategy changes, source-of-truth priority, LLM routing/retries/cost, secrets, or production report writes.
- P0 stops unsafe lane and alerts operator. P1 prevents approval/merge and is repaired before full acceptance; other safe work may continue. A completed checkpoint/role does not necessarily end the *whole* program. A truly exhausted safe queue DOES justify parking; do not invent meaningless tasks to keep a model running.
- Each model session has only its actual lifetime. GitHub Issues, a prompt, and ChatGPT chats do not relaunch CLIs. The existing opt-in `infra/p15-continuity-runner-20261017` prototype is NOT activated and has not demonstrated role auto-switch. No unattended runner without operator's explicit host/budget/credential approval.
- **Hourly ChatGPT Work/GitHub monitoring stays DISABLED** at the user's request. Never enable or recreate a scheduled automation without a new explicit request. Report on-demand only; no surprise recurring credit usage.

## 6. Cut-and-paste small bootstraps

**Codex (after Monitor local completion):**
`Read docs/dev-team/assignments/11_P15_TWO_WORKER_ARCHITECT_ON_DEMAND_20261017.md on origin/design/agentra-dev-team-loop-20261017 and Issue #12/#14. Finish safe Monitor-local M9 first, then implement shared Reporter+Monitor T3/T4/agent-package/CI/UI on a NEW isolated integration candidate at actual two role SHAs. Do not touch role branches or main. Post exact SHA/tests/negative mutations. Request independent Claude review and repair feedback continuously. No Work approval wait per batch; GPT is architect on demand.`

**Claude (after Reporter local completion):**
`Read docs/dev-team/assignments/11_P15_TWO_WORKER_ARCHITECT_ON_DEMAND_20261017.md on origin/design/agentra-dev-team-loop-20261017 and Issues #11/#14. Maintain Reporter fixes on its own branch only. Independently audit Codex's latest shared integration candidate from a clean checkout, run precise normal/-O and negative T3/T4/Reporter/Monitor tests, post SHA-bound findings on Issue #14. Do not edit Codex's candidate. In parallel prepare read-only Strategist mapping; source edits only after GPT charter. No Work-auto-monitoring or main merge.`

**GPT (ordinary chat, on demand):**
`Act as Agentra P1.5 chief architect, NOT an always-on Work runner. Read 11_P15_TWO_WORKER_ARCHITECT_ON_DEMAND_20261017.md, fresh role SHAs and issues. Decide precise disputed scope and next-role design; give SHA-bound acceptance, prevent trading-authority drift, and hold final main approval for the user. Do not schedule recurring review.`

## 7. Supersession / documents

Use **this doc first**. Older instructions that say `Work solely implements T3/T4`, `Codex must never work on shared tests`, `Work hourly automation is active`, or `no role transition until Work starts a separate Work session` are **obsolete**. Historical issue comments are preserved but no longer active assignments. GitHub is the durable source of truth; every worker should load this doc from the design ref explicitly because it is not automatically present in its role branch.
