# Monitor — whole-role refactoring project (AUTHORIZED, WORKER_NOT_STARTED)

Assigned implementation: Codex. Independent audit: Claude. Integration/technical judgment: Work. Preparation BASE: d773709ba2f70471fad9badba4f92400f7818319; runtime BASE is pinned; branch start is the common documentation activation commit. Read ACTIVATION.md before executing.

## Whole-role responsibility register
Cover Scanner/Strategist handoff, observed position/market context, signal features, entry evidence and eligibility, exit observations/decisions, cycle/output/event payloads and OrderIntent boundary. An entire Monitor responsibility is managed as one project; the ten seed modules are the first internal batch only. Physical movement of safety-sensitive decision/effect owners is not authorized by this draft.

| Current responsibility / anchor | Treatment |
|---|---|
| Ten exact seed modules in SEED_LEDGER.json | `libs/agents/monitor/events/` or `projections/`, whole blob unchanged plus strict legacy identity shim |
| Other `libs/runtime/monitor/` context/evidence/signal projections | Reuse owner matrix; register exact consumers, purity, aliases and ownership before including a pure owner in a continuous batch |
| `entry_candidate_*`, `entry_carry_guard`, `entry_cascade_selection`, eligibility and trigger owners | KEEP_WITH_REASON / SAFETY_LOCK until separately scoped; no change to entry authority or cooldown |
| `libs/runtime/monitor_exit/**`, actual entry/exit decisions | Protected boundary; record consumers and fake-contract tests, no decision or authority movement |
| `libs/runtime/intraday_monitor_signals.py`, `graphs/nodes/monitor_node.py` | Stable facade/decision seams; read-only dependency/ABI checks, no graph/facade rewrite under this draft |
| Supervisor/Executor/Broker, OrderIntent creation/effect order, position persistence/locks | SAFETY_LOCK; no write, quantity, reason, timing or authority change |
| Reporter consumption of Monitor fields | Shared DTO/output boundary; preserve schema/values/order and aliases; shared change belongs to Work |

Do not redesign V3 or create placeholder packages. Extra canonical destinations require exact integrator-recorded mappings, not a wildcard allowance. Whole-role classification must show residual scope; keeping every difficult module does not constitute full structural completion.

## Execution and proof
At worker start: refresh seed/source hashes and existing Monitor inventory rows; build responsibility/consumer/effect dispositions; implement coherent safe event/projection/context batches continuously; defer unsafe modules individually with exact reasons; submit pinned role SHA to Claude; Work performs serial integration and final combined CI.

No changes to selected symbol, score/ranking, entry/exit reason, quantity, OrderIntent fields/order/call counts, risk policy, cooldown, position state or locks. Source-mutating/side-effect helpers cannot be described as pure because their filename says projection. Preserve facade lookups at use time and actual copying/mutability.

Initial relevant tests: `tests/test_p163_t4b_extraction_gates.py`, `tests/test_p163_monitor_contract_freeze.py`, current T3 owner gates, Wave B moved-body/authority and strict mutation/-O gates. Extend focused selection from exact consumers; do not run full-repo tests per file. Work owns all existing shared gate updates; worker submits failing test IDs and necessary mappings instead of weakening them. Fake broker/clock/env/LLM only; preserve effect traces with zero production interaction. Existing native Windows replay requirements remain.

Worker-owned paths: approved Monitor legacy/canonical pairs; unique `tests/test_work_monitor_*`, `tests/fixtures/work_monitor/**`, `scripts/refactor/work_monitor_*` if needed and Monitor-specific evidence. No Reporter/scanner/strategist, protected monitor_exit/decision owners, graph, shared notes, tests or workflows edits. Use isolated run/process temp roots and bounded evidence.

Completion: all role responsibilities dispositioned, approved pure moves/decompositions finished, remaining protected/shared/blocked responsibilities explicit, compatibility and input/output/effect proof attached, independent audit P0/P1 closed, combined required CI PASS and official UI notes synchronized. A ten-file seed pass alone is PARTIAL. main/deployment/safety changes require user approval.
