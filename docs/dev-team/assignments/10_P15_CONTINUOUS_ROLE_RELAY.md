# Agentra P1.5 — Continuous Role Relay, Not Per-Checkpoint Chat Stopping

> **OVERRIDE / WORK DISABLED (2026-10-17):** This earlier relay document includes obsolete claims that hourly Work monitoring is active and Work exclusively owns T3/T4 code. Those claims are NOW FALSE. Read [11_P15_TWO_WORKER_ARCHITECT_ON_DEMAND_20261017.md](11_P15_TWO_WORKER_ARCHITECT_ON_DEMAND_20261017.md) as authoritative: GPT chat on-demand remains architect; Codex implements shared integration AFTER Monitor-local completion; Claude independently audits it; hourly automation remains DISABLED. Existing runner prototype is not activated.


**Active from 2026-10-17 KST.** Overall target is the P1.5 structural refactor and safe integration across the seven LangGraph roles. A role-local freeze is NOT project completion. **Owner routing remains** Claude=Reporter, Codex=Monitor, Work=architect/reviewer/shared T3/T4/integration. After local closure, a next role requires a separately approved whole-role scope and isolated writer branch.

## Actual checkpoints; refresh every session

- Reporter remote de99c8f0fa66bfc3e6be9a229f04fc6aad5ca06e — Reporter R10 local evidence ready for independent integration, 313 body moves, no main merge. Work independently reviewed static files but final Linux/CI/real persisted parity NOT_RUN.
- Monitor remote 4bc4250844093050438d8a9c29f5842991ad1c3a — M9 CP-008, 14 whole module +20 named body moves unchanged, full native mod1 replay attempted/passed on developer Windows, offline proof expanding retained 359 functions. **Codex currently reports ACTIVE, NOT parked.** Work shared five T3/T4 failures remain unclosed.
- Work shared queue Issue #14 — precise path/AST guards, strict current-head negative tests, cross-role integration candidate, required CI and UI-connected patch notes. An issue alone is not executing this work.

## The source of the early-stop failure

Prior orders treated SAFE_EXTRACTION_EXHAUSTED as if the entire work program were exhausted. This is now invalid: neither a moved-function count nor a single-role PARITAL_WITH_BLOCKERS is a completion criterion. However, repeating unneeded moves/tests merely to keep a process alive is also invalid. Correct continuation is **work transfer**: safe new proof, ready next-role architecture/implementation, or shared integration on a different authorized writer lane.

## Explicit cross-role next-lane plan

| Worker | Primary active lane | When local role is truly done | Next lane that is immediately authorized without a further user message |
|---|---|---|---|
| Claude | Reporter until Work ACK of R10 + any new findings | Issue #11 receives REPORTER_LOCAL_READY_FOR_INTEGRATION confirmation | **Strategist READ-ONLY ownership/consumer/test design** on an isolated evidence branch, not source migration |
| Codex | Monitor M9 until role tests/retained classification and Work ACK | Issue #12 receives MONITOR_LOCAL_READY_FOR_INTEGRATION confirmation | **Scanner READ-ONLY ownership/consumer/test design** on an isolated evidence branch, not source migration |
| Work | parallel Reporter/Monitor reviews + shared T3/T4 + combined CI/UI | Roles accepted for local integration and shared tests green | Prepare narrow Strategist/Scanner whole-role source change charters, approve disjoint branches for implementers, continue dual-role candidate; not main merge |

**Transition criteria:** Work must record an exact `NEXT_ROLE_SOURCE_APPROVED` charter on GitHub before either implementer starts changing Strategist or Scanner runtime. Until then their additional role work is bounded to read-only Git study, architecture, fixtures that do not import live brokerage, and candidate acceptance tests on isolated docs/evidence branches. No automatic transfer of trade policy or authority. Later roles Commander, Supervisor and Executor require separately reviewed authority-preserving program packets; no automatic mechanical refactor of execution/guards without narrow human consent. Work can prepare safety-only plans while other roles progress.

**No role handoff that edits another writer's branch.** Separate branch/worktree per new role, from a verified canonical base chosen by Work after checking existing P1.5 historic refactors/ledgers. Do not merge active Reporter/Monitor/other role branches into each other to get code. Final main merge only when the full P1.5 integration has mock-only CI green and human expressly approves.

## Restart/readiness protocol

At EACH CLI completion, write status in branch checkpoint and issue when authorized:
`CURRENT_ROLE`, `EXACT_PUSHED_SHA`, `LOCAL_STATE`, `NEXT_READY`, `WAITING_ON_WORK_ID`, `NEXT_APPROVED_ROLE`, `TESTS_PASS_FAIL_NOT_RUN`, `CREDITS_OBSERVED_OR_UNKNOWN`.

A session that completed one batch MUST proceed to the next ready task. A session that completed all role-local tasks must switch to the approved **next safe lane** instead of asking the operator for another chat prompt. A session without a safe approved next lane must honestly park `WAITING_ON_WORK` and not burn tokens. **No text instruction can restart a killed process:** this requires an installed/scheduled runner on a powered-on, authenticated machine.

A separate opt-in Python prototype (infrastructure branch `infra/p15-continuity-runner-20261017`, delivery pending local activation) is available as a changed-files ZIP. It provides bounded session relaunch, same-role git/dirty validation, process single-writer lock, real pushed-SHA verification, daily invocation/time ceilings, STOP file, no-repeat on zero commits and mock-only tool permissions. It does NOT currently automatically switch to another role or wake from `WAITING_WORK` on GitHub Issue updates; those are future runner extensions and must not be claimed as active. Provider dollar spend is NOT metered by the runner, so an external provider spend cap is required before activation.

## Work hourly review vs CLI worker execution

An hourly **ChatGPT automation** has been configured on 2026-10-17 to check GitHub P1.5 status, review SHA deltas and surface blockers as tools permit. It does NOT launch Work's cloud computer, Claude Code CLI, or Codex CLI on the user's PC. Do not confuse a scheduled GitHub review with running implementation processes.

## Priority and budget controls

P0 actual live-execution/secret/guard incident: STOP affected lanes and escalate immediately. P1 hidden behavior change/shared negative gate: prevent final role PASS/merge while unaffected proof tasks continue. P2 hygiene/docs: repair in the next coherent batch. Never automatically merge main, modify real brokerage state, or extract private credentials. Model expense must be bounded by user-chosen daily session cap, max runtime and official provider budget control; if absent, unattended runners remain disabled.

## Operator daily digest only

Work posts one concise digest with real latest SHAs, run/idle state, latest independent tests and unresolved common contracts. Do not make the human copy Claude/Codex output between chats. Notify early only for P0, genuinely unavoidable authorization/host/credential/budget decisions, or P1.5 final merge request.
