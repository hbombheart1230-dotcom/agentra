# Current-to-target architecture gap matrix

Source SHA: f555165b1abcf64b03e9c370844611dabe40c949
State: GPT ARCHITECTURE_DRAFT / ARCH_CONVERGENCE_NOT_APPROVED
Scope: merged T4 + PR #5, no source changes or physical module relocation.

## Editable target proposal (not a relocation order)
```text
agentra/
  graphs/                          # Keep graph adapter and stable runtime entry
  libs/agents/                     # PROPOSED, no files moved
    commander/ strategist/ scanner/ monitor/
    reporter/ supervisor/ executor/
  libs/contracts/                 # Shared DTO and versioned adapters
  libs/runtime/                   # Cross-agent primitives after approved moves
  libs/reporting/                 # Report read models / renderer, exclude research owners
  libs/research/                  # Q10/Q12/Evaluation, no order authority
  libs/execution/ libs/supervisor/ libs/risk/ # SAFETY_LOCK, keep original paths
  apps/api/ apps/web/ apps/operator_ui/
  scripts/{diagnostics,research,maintenance,examples}/ # Old wrappers retained
  tests/ docs/ deploy/ config/ data/
```

Prefer one real callable Agent core per role, with graphs/nodes acting as stable adapters. libs/agents/<role>/ is only a provisional logical packaging name; reuse existing libs/runtime/<role>/ owners rather than making duplicate implementations. No cosmetic service.py creation.

| Priority | Current path | Proposed owner / action | Status | Safety/consumer proof |
|---|---|---|---|---|
| P0 | graphs/nodes/scanner_node.py + libs/runtime/scanner/ | Scanner callable core + adapter | MOVE_WITH_ADAPTER | rank/top1 parity, consumers |
| P0 | graphs/nodes/monitor_node.py + libs/runtime/monitor/ + monitor_exit/ | Monitor callable core | MOVE_WITH_ADAPTER | intent/exit State/effect order |
| P0 | graphs/nodes/strategist_node.py + libs/runtime/strategist/ | Strategist core | MOVE_WITH_ADAPTER | LLM/news/prompt/memory parity |
| P0 | graphs/commander_runtime.py + libs/runtime/commander/ | Commander policy core | MOVE_WITH_ADAPTER | runtime mode/env/state order |
| P0 | libs/reporting/ 500 files | separate Reporter/Evaluation/Research | UNPROVEN_BLOCKED | Q10/Q12 + artifact consumers |
| P0 | libs/reporting/trade_report and original flat facade modules | preserve nine safe PR5 identity pairs | KEEP_CANONICAL | import/monkeypatch identity |
| P0 | libs/reporting/live_execution_bundle_runner.py | Reporter effect owner retained | SAFETY_LOCK | locks/queue/writes/real parity |
| P0 | graphs/nodes/execute_from_packet.py | operational order authority retained | SAFETY_LOCK | Broker/Step5C/UNKNOWN |
| P0 | libs/supervisor/ + libs/risk/ + libs/approval/ | Supervisor authority retained | SAFETY_LOCK | approval/intent/CAS |
| P1 | libs/agent/monitor.py | legacy consumer proof then thin adapter | LEGACY_COMPAT_KEEP | old callers and tests |
| P1 | libs/agent/commander.py and strategist.py | keep legacy APIs | LEGACY_COMPAT_KEEP | constructor/alias consumers |
| P1 | libs/agent/scanner.py | compare old ranking to canonical | UNPROVEN_BLOCKED | avoid duplicate rank source |
| P1 | libs/agent/reporter.py | keep real Reporter entry | KEEP_CANONICAL | feedback + report contract |
| P1 | scripts/ 141 public wrappers | retain shims; categorize by scheduled role | LEGACY_COMPAT_KEEP | Windows/task scheduler refs |
| P1 | scripts/diagnostics and libs/diagnostics | PR5 work orders pure owner consolidation | KEEP_CANONICAL | CLI help/exit/outputs |
| P1 | graphs/trading_graph.py | separate M17 graph stub from operational flow | UNPROVEN_BLOCKED | runtime selector and LangGraph evidence |
| P2 | apps/operator_ui data_access_core.py | preserve render/LLM paths | KEEP_CANONICAL | exact brief bytes, REAL_PARITY_NOT_RUN |
| P2 | docs/ and tests/ | archive/index after stable source | MOVE_SAFE_PENDING_TEST | CI globs, discovery, source links |
| P2 | PR5 19 held script cases | defer until consumer authority evidence | LEGACY_COMPAT_KEEP | operational / launch paths |

## Three execution batches after approval
1. Simple no-authority consolidation and docs/script classification. Preserve public wrappers until every consumer is known.
2. Reporter/Research/Evaluation canonical ownership and nine PR5 safe alias pairs; protect artifact byte formats and LLM-bound effects.
3. Scanner, Monitor, Strategist, Commander callable boundaries with explicit State adapters; stop before Executor/Supervisor/CAS safety routes unless separately authorized.

## Unclosed acceptance items
- T4-C replaced Reporter-feedback fallback 29-variant scenario with a different 23-variant max-token scenario: restore the lost independent BASE case before final P1.5 approval.
- Synthetic UI renderer parity is not actual persisted Operator Brief parity; real report and LLM parity are not proven.
- Legacy 16-test BASE/FEATURE IDs and exact replay commands absent; NTFS mtime and cross-seed telemetry P2 remain.
- T5, Wave D, P1.5.10, P1.6 and main merge remain NO-GO.

Approval sequence: GPT architecture evidence → user edits target_architecture.drawio → Codex dependency/consumer audit → explicit ARCH_CONVERGENCE_APPROVED → Claude batch implementation → Codex audit → GPT/user acceptance.

Current decision: ARCH_CONVERGENCE_NOT_APPROVED; no paths have been moved.
