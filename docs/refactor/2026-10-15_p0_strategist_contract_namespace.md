# P0: Isolated Strategist Contract Namespace

Date: 2026-10-15
Base commit: `2f95bba429636ee15ae9a399cc4ff7c4e6dcd5cb`
Branch: `refactor/gpt-p0-strategist-contract-20261015`

## Why this is the first slice

The target tree has `libs/contracts/agents/strategist.py`; the current
Strategist DTOs and normalization already live in `libs/strategies/contracts.py`.
Duplicating those types would risk identity drift and a silent schema change.
The first migration creates an optional import location for the existing,
identical objects without changing any runtime call sites.

## T4 exclusion / ownership

- No modifications to Commander, Strategist, Scanner, Monitor, Supervisor,
  Executor, Reporter, graph entrypoints, broker code, or existing contract files.
- No import rewiring in `graphs/nodes/strategist_node.py` during Claude's T4.
- The current `libs/strategies/contracts.py` remains the implementation
  authority; the new namespace is an alias only, not a second source of truth.
- This branch is independently reviewable; do not merge/rebase over T4 without
  checking for concurrent edits to shared UI patch notes.

## Invariants

- Exact Python object identity is preserved for exported classes, type aliases,
  and `coerce_strategist_output`.
- DTO fields, defaults, normalization, additive extra keys and existing imports
  remain unchanged.
- No change to trading signal evaluation, supervisor approval, guards, CAS,
  execution flags, or broker routing.

## Targeted verification

Run from the repository root:

```bash
python -m pytest tests/test_strategist_contract_namespace.py tests/test_strategist_output_schema.py -q
python -m pytest tests/test_patch_notes_sync.py -q
```

This slice deliberately does not claim end-to-end execution or production build
verification. These must be performed against a full checkout before merging.

## Next low-risk independent slices (after T4 overlap check)

1. Map existing Scanner helpers to the requested `scoring`, `evidence`,
   and `contracts` responsibilities, first with no runtime rewiring.
2. Extract one small pure helper at a time and verify parity with tests.
3. Keep `graphs/nodes/*` as compatible entrypoint shims; migrate hot paths
   only after T4 lands and regression evidence is available.
4. Defer all Supervisor, Step5C CAS and Execution Guard migrations to a
   dedicated safety-reviewed phase.
