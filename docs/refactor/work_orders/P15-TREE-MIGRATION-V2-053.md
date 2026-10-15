# P15 HYBRID-7 V3 — V2-053 Scanner Context & Scoring Inputs Bulk Migration

**Task:** IMPLEMENTATION. No redesign, no full-source reinventory. GPT decision after Codex PASS_WITH_FINDINGS on V1-052.

**Branch:** `integration/p15-t4-pr5-convergence-20261015` (single active development branch).
**Required base:** `1eb5fa1fd8dc6154743ef3855305663e34a83281` or an explicitly inspected fast-forward descendant. No new branches, no `main` merge.
**Roles:** Claude implements → Codex audits pinned pushed SHA → GPT/user accepts. All changes on isolated non-operational clone, never live `C:\Agentra` or Q12 worktrees.
**Architecture:** HYBRID-7 V3 is frozen (see `docs/refactor/architecture/TREE_V3_FROZEN.md`). Code migration is the goal, not another diagram or proposal.

## Step 0: Close V1 independently accepted work

Record V1-052 `GPT_ACCEPTED_WITH_P2_DOC_FINDINGS` at `1eb5fa1...`: Codex independently verified exact BASE vs canonical Git Blob SHA `8dea30a...`, true old/new module identity, use-time `_clamp` monkeypatch, 115/115 frozen BASE-vs-final cases, 13/13 focused, and 3 hosted green CI workflows. The only P2 finding is documentation.

Correct `docs/refactor/architecture/architecture_gap_matrix.md`:
- The older blanket phrase “no paths have been moved” must become “the architectural proposal itself does not authorize additional moves; V1-052 has already moved one approved module.”
- Clarify `8` V1 migration tests + `5` existing candidate-risk tests = **13 combined**, rather than implying the one test file contains 13.
- Do not alter frozen history; only mark the current state and append a short factual V1 acceptance note.

## Step 1: Real, coherent V2 relocation (five candidates)

Inspect the *five named modules and their exact consumers only*. Provided their module object, imports and patch seams can be preserved with no behavior change, move these pure/helper bodies byte-for-byte:

| Existing compatibility path | Proposed sole canonical path | Responsibility |
|---|---|---|
| `libs/runtime/scanner/feature_coverage.py` | `libs/agents/scanner/context/feature_coverage.py` | Candidate quote-metric coverage and refresh policy read-model |
| `libs/runtime/scanner/sentiment_inputs.py` | `libs/agents/scanner/context/sentiment_inputs.py` | News/global sentiment input projection |
| `libs/runtime/scanner/scoring_inputs.py` | `libs/agents/scanner/context/scoring_inputs.py` | Scanner score/context policy normalization |
| `libs/runtime/scanner/macro_focus.py` | `libs/agents/scanner/context/macro_focus.py` | Macro focus weights projection |
| `libs/runtime/scanner/macro_chart_fit.py` | `libs/agents/scanner/context/macro_chart_fit.py` | Macro chart-fit soft-bias projection |

Design freeze note: `context/` is simply the stable ownership grouping for these existing pure Scanner inputs, not a new Agent or ranking policy authority. Keep `libs/agents/scanner/candidate_risk.py` in its V1 location. Don't fabricate package stubs for the other six agents. The canonical ownership rule is **exactly one body** per migrated module.

For each migrated file:
1. Compare source bytes / blob against the pinned base; preserve body exactly. Do not change runtime logic, exceptions, signatures, value ordering, thresholds, names or import-side effects.
2. Keep the old module path as a `sys.modules`-level **identity** compatibility alias to the single new owner, not `from new import *` or a duplicate class/function copy.
3. Check old-first/new-first fresh-process imports, package attribute `is` identity, private/public objects, callable signatures, and use-time monkeypatch of the old path. Use the original caller signature and injected `facade` use-time resolution.
4. Build frozen BASE-body replay inputs where possible; compare exact outputs/key order and exception behavior, using real pinned source rather than fabricated historical baselines.
5. Assess dynamic import strings, scheduler/CLI consumers, injected callbacks and any `__module__`, `__file__`, package resolution, pickle or introspection dependencies. Do not infer safe moves solely from static import absence.
6. If any of the five moves proves unsafe, **leave just that module untouched** with a concrete `SAFETY_BLOCKED` reason; continue independent safe siblings. No false 5/5 claim.

## Immutable boundaries and regression gates

- No modification of `graphs/nodes/scanner_node.py` or any selected/rank-1 logic, ranking score semantics, order intent/admission, Commander routing, Strategist prompt/call count, Supervisor, Executor, Broker/Step5C/UNKNOWN/UEF, Q10/Q12 runtime, Docker, API/Web or UI output writers.
- Tests must be mock/offline, no network, no live orders/LLM, no production writes. Isolated temporary roots; successful scratch auto-clean, bounded failure evidence.
- Run a single focused test batch for all five modules with import identity, monkeypatch, AST/blob parity, selected/rank replay, the existing V1-052 contract, and relevant frozen T4 Scanner tests. Do not weaken or deselect safety assertions to force PASS.
- Preserve V1-052 tests; if a new test relies on `git diff BASE..HEAD`, ensure all applicable hosted CI checkouts have history (do not alter tests to conceal missing history).
- Run available required CI on the pushed implementation SHA; report full job status, not only the step subset. Independent Codex audit before V2 acceptance.
- Keep `docs/refactor/work_orders/CURRENT.md` pointing to **one active** V2-053 task; retain historical `P15_FAST_TRACK_WAVE_S_020.md` link required by CI. `FINAL_ACCEPTED` must not appear inside `CURRENT.md` `**State:**` line.
- Update existing Gap Matrix with all five actual dispositions, today's short daily evidence, UI-linked `patch_notes.json` AND `patch_notes.md` (correct entry_count and source links). No ZIP workflows in CI. For user delivery create a **changed-files-only** ZIP outside the repo; exclude secrets, operational data and historical archives.

## Completion report

```
BASE_SHA:
IMPLEMENTED_SHA:
FINAL_SHA:
BRANCH:
MODULES_ATTEMPTED:
MODULES_MOVED:
MODULES_BLOCKED_AND_REASONS:
ORIGINAL_TO_CANONICAL_BLOB_SHA:
OLD_NEW_MODULE_IDENTITIES:
FOCUSED_TESTS:
SCANNER_RANK_ORACLE:
CI_REQUIRED_RUNS_AND_JOBS:
PRODUCTION_WRITE_AND_BROKER_LLM_GUARD:
V1_DOC_P2_FINDING_FIXED:
UI_PATCH_NOTE_JSON_MD_COUNT:
CHANGED_PATHS:
CHANGED_ONLY_ZIP:
CODEX_AUDIT: PENDING
```

**Do not start V3** until Codex independently verifies this pushed SHA. No further tree-target iteration, and no `main` merge.
