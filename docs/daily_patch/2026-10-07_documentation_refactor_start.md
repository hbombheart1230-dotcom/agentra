# 2026-10-07 Documentation Refactor Start

## Summary

Started the documentation-architecture track of P1.5.

This is documentation/navigation work only. No runtime, strategy, execution, broker, LLM, Supervisor, Executor, UEF or trading semantics changed.

## Inventory Snapshot

At the pre-batch snapshot:
- 748 files under `docs/`
- 740 Markdown files
- 39 top-level documentation directories
- 137 dated `docs/daily_patch/` entries
- 170 Markdown files in `docs/plan/`
- approximately 207 Markdown paths carrying M/Step/Phase-style milestone naming

## Patch-Note Authority Clarified

Three patch-note surfaces were identified:

1. `docs/daily_patch/`
   - canonical detailed technical/audit history

2. `docs/trading_agent_patch_notes_detailed_update/patch_notes.json`
   and `patch_notes.md`
   - actual UI/API changelog authority
   - consumed by `apps/api/adapters/patch_notes.py`
   - guarded by patch-note API/freshness tests

3. `docs/PATCH_NOTES.md`
   - legacy phase-oriented summary
   - not the Patch Notes UI source

The P1.5/P1.6 2026-10-07 design entry was therefore added to the actual UI/API changelog pair.

## Documentation Refactor Policy

- preserve historical evidence
- do not bulk-rename milestone documents
- current canonical docs use responsibility/domain naming
- map inbound references and patch-note `sources[]` before moving historical files
- clean navigation/indexes before physical movement
- patch-note paths remain stable until a separately tested code migration is approved

## Added Design Documents

- `docs/refactor/documentation_inventory.md`
- `docs/refactor/p1_5_documentation_refactor_plan.md`

## Runtime Impact

None.
