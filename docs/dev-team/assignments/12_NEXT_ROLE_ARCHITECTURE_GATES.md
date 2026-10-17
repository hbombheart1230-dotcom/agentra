# P1.5 Remaining-Roles Architecture Backlog — GPT as On-Demand Architect

**Author:** GPT (ordinary chat, on-demand), 2026-10-17. **Stage:** design/analysis only. No new-role source migration is authorized by this file. **Current policy:** [11_P15_TWO_WORKER_ARCHITECT_ON_DEMAND_20261017.md](11_P15_TWO_WORKER_ARCHITECT_ON_DEMAND_20261017.md).

## Architecture sequence

1. **Finish shared Reporter+Monitor T3/T4/CI integration candidate** — Codex implements, Claude independently validates. Keep main untouched.
2. **Strategist whole-role charter** — Claude performs read-only ownership and contract mapping. GPT then writes an exact approved refactor scope, file-ownership map, test matrix and disallowed semantic changes. Only then Claude starts an isolated Strategist implementation branch.
3. **Scanner whole-role charter** — Codex read-only maps canonical candidate/rank/rank-provenance path and old compatibility consumers. GPT then writes narrow source-change charter; Codex uses a separate Scanner implementation branch only after approved. No fixing Scanner rank defects as an accidental side effect of P1.5 structural refactoring.
4. **Commander/Orchestrator scope** — classify LangGraph node routing/state transformation and output interfaces; preserve command priority and NOOP safety behavior. Must not shift policy execution authority.
5. **Supervisor and Executor protected scope** — first write only inventory/ABI/OrderIntent/approval/guards and replay tests. Structural refactor only after explicit separate risk/authorization decision, no new execution or order/cancel semantics.
6. **P1.5 cross-role freeze** — shared contracts, negative authority, historical pins, replay determinism, UI-linked patch notes, rollout/rollback; independent review and user final approval before a single main merge.

## Inputs GPT expects from workers

| Role | Read-only study owner | Must produce for GPT approval |
|---|---|---|
| Strategist | Claude after Reporter local handoff | source/consumer dependency DAG, schema/contract list, LangGraph state fields, precedence from commander/context, output DTO, pure formatter vs policy evaluator classification, patching points, negative fixtures |
| Scanner | Codex after Monitor local handoff | candidate lifecycle/rank identity map, rank-1 and fallback flow, timestamp/source/canonical price provenance, all callers, wrapper/Owner candidates, deterministic replay and lossless records |
| Commander | To be assigned later | policy and delegation graph, observation-only vs authorized decision responsibility, NOOP/override/test gate |
| Supervisor | To be assigned later with human scope | approval and guard precedence, enforcement boundary, immutable order authority and reject-by-default tests |
| Executor | To be assigned later with human scope | Step5C CAS/idempotency, order/cancel/status contracts, no-live mock invariants and rollback path |

**Important:** the names above describe desired responsibility mapping, not a claim that each expected field or file currently exists as described. Every actual path/symbol and module location must be cited from GitHub at the review SHA before creating its source work order. Do not use this planning document to “fix” any trading strategy or runtime defect in a refactor branch.

## Acceptance rubric for each whole-role charter

- An exact BASE/HEAD pair, single-writer branch, objective in-scope path/function inventory, explicit exclusions, reversible internal batches.
- Public signatures/import/module identities, DTO byte and exception parity, callback/use-time binding, no live networking or broker calls; negative same-path/source mutation catches unintended behavior changes.
- Historical tests untouched; new current-head guards are additive and fail closed in normal and optimized Python.
- Linux Python 3.12 and applicable native Windows tests; match representative user-facing JSON/Markdown bytes; no test fixture in tracked repo temp directories.
- UI patch note source provenance, actual counts, current-vs-proposal state, exact final SHA evidence; independent other-worker verification at role freeze.
- No accidental T3/T4 broad allowlist, source-of-truth, rank/pricing/cooldown, Q10/Q12 or Step5C/UEF authority changes.

## On-demand GPT intervention policy

Do not make GPT approval a per-file or per-commit bottleneck. The initial source-work charter defines all reversible pure structural packets within its closed scope, and developers may proceed through those. Trigger a user-directed GPT design review ONLY for:
- scope beyond closed set, ownership conflict or uncertainty over actual policy authority;
- conflict between pinned historical and new current-head safeguards;
- adverse P0/P1 security, trade semantics or unresolvable CI;
- change of whole-role implementation target or final P1.5 merge request.

A new GPT chat is not a background agent. No recurring Work scheduling or automatic CLI restarts are authorized. When GPT is invoked, inspect only current SHA deltas + relevant issue evidence and publish an exact GitHub design ruling. User retains final approval for all main/trade-authority changes.
