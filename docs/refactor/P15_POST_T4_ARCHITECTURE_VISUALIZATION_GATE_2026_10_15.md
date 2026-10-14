# Agentra P1.5 — Mandatory Post-T4 Architecture Visualization & Convergence Gate

**Authority:** User decision, 2026-10-15 KST. **Status: MANDATORY FUTURE GATE / NOT STARTED.** Branch: `refactor/p1.5`.
This supersedes older task sequencing that silently skips architecture visualization. The original P1.5 PREP responsibility-first target stays authoritative as an architectural goal, not a command to recreate exact file names.

## Mandatory sequence (do not skip)

1. Finish T4-A.1 independent Codex review. **T4-B remains BLOCKED until Codex ACCEPT.**
2. Complete and independently audit T4-B Monitor, T4-C Strategist, T4-D Commander/Operator UI and authorized remaining Reporter structural work. **Decompose first; do not prematurely reorganize folders or rename modules.**
3. **Immediately after the T4 structural closure** generate actual-source architecture views and original-plan comparison, pinned to a real Git SHA. These are FUTURE deliverables, not yet generated.
4. GPT and the user inspect current-vs-target diagrams together and edit the desired target in draw.io. Do not auto-align the tree. For each proposed move/merge/rename record the original path, proposed owner, direct/dynamic consumers, API/State/IO/LLM/authority boundaries, parity evidence, risks and acceptance decision. Codex independently checks this mapping.
5. **Before P1.5.10 wrapper cleanup or any bulk directory move/rename**, require explicit `ARCH_CONVERGENCE_APPROVED` from GPT + user with Codex consumer/safety audit. Missing/uncertain evidence = `ARCH_CONVERGENCE_BLOCKED`. SAFE scoped changes may then be separately authorized and tested.
6. Wave D/P1.5.11 final acceptance and **P1.6 runtime migration cannot use the diagram as a PASS substitute**. P1.6 still requires a separate, formal P1.5 freeze. T5 controlled-mock-lane path remediation remains a separate safety gate (no automatic authority for T5 changes).

## Five required architecture deliverables

| Proposed path (not yet present) | Source-grounded scope |
|---|---|
| `docs/refactor/architecture/current_overview.md` | Mermaid overview: seven roles, orchestration/Graph, deterministic vs LLM decision roles, Supervisor/Executor authority, Reporter vs evaluation layers. |
| `docs/refactor/architecture/current_modules.md` | Per-Agent Mermaid module drill-down with actual node, owner/service, compatibility adapters, mutable State/effects, boundaries. Not a 3,000-file hairball. |
| `docs/refactor/architecture/dependencies.svg` | Generated real Python import dependencies, source SHA, exact generation command, filtered scope and visible cycles/coupling. Mark incomplete coverage: dynamic facade, monkeypatch, runtime dispatch and State-key dependencies need separate evidence. |
| `docs/refactor/architecture/target_architecture.drawio` | Editable proposed target tree using original PREP architecture. **User-adjusted and manually approved**, not automatically applied. |
| `docs/refactor/architecture/architecture_gap_matrix.md` | Current path / desired logical owner / direct & dynamic consumers / action / safety classification / callable Agent-contract gaps / tests / acceptance evidence. |

VS Code Mermaid preview = overview; draw.io = user-editable target; pydeps/Graphviz or equivalent = generated import picture. Pin SHA, counts and known blind spots. No fabricated complete call graph. The key goal is **independently callable Agent cores** with explicit inputs/outputs and state adapters, not cosmetic folders or LOC minimization.

## Mandatory decision matrix

Every candidate module is classified:
- `KEEP_CANONICAL`: single valid owner, leave intact.
- `MOVE_SAFE_PENDING_TEST`: location-only, still requires actual consumer/import/parity proof.
- `MOVE_WITH_ADAPTER`: explicit API/State compatibility plan and proven consumers.
- `MERGE_AFTER_CONSUMER_PROOF`: genuine duplicate authority; retain exactly one implementation.
- `LEGACY_COMPAT_KEEP`: active or unresolved compatibility consumers.
- `SAFETY_LOCK`: Broker/Step5C/UNKNOWN/Supervisor/Executor mutation, LLM prompt/retry/count, production writes, State/event ordering; defer without independently authorized immutable fixtures.
- `UNPROVEN_BLOCKED`: missing evidence or unknown dynamic caller.

Never create a duplicate Scanner ranking authority, loosen golden/oracle/UEF guard, silently rehome LLM/Broker authority, change trading semantics, or delete legacy paths on import search alone. A `service.py`/contract file should only appear when actual independent ownership requires it, not because the PREP drawing has that name.

## Exit checklist and authority

- [ ] All required T4 structural slices reviewed/accepted (not just CI green).
- [ ] All five diagrams/matrix delivered and source SHA / generator / filtering recorded.
- [ ] Seven independent callable Agent surface/contract/state-adapter gaps and legacy wrappers measured against actual code.
- [ ] Import and direct/dynamic consumer DAG, duplicate owners, monkeypatch seams, cycles and SAFETY_LOCK classified.
- [ ] GPT + user have reviewed and approved the editable target; decisions recorded as `ARCH_CONVERGENCE_APPROVED` (otherwise BLOCKED).
- [ ] Codex independently audits consumer evidence; authorized renames/moves are separate behavior-parity work orders.
- [ ] `CURRENT.md`, both UI patch-note formats and daily evidence updated; no automatic Wave D/P1.6 GO.

**Owners:** GPT = design/review; User = target-tree approval; Claude = approved implementation; Codex = independent audit.
**Current:** T4-A.1 implementation pushed, Codex audit PENDING; T4-B BLOCKED. This document registers only a future mandatory gate. No actual diagrams, reorganization or CI enforcement are claimed.
