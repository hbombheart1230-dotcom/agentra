# Daily Patch Log — Technical Audit History

`docs/daily_patch/` is Agentra's canonical dated technical patch/audit history.

It is intentionally different from the Patch Notes UI source.

## Authority Split

```text
docs/daily_patch/
  = detailed technical evidence and audit history

docs/trading_agent_patch_notes_detailed_update/patch_notes.json
docs/trading_agent_patch_notes_detailed_update/patch_notes.md
  = human-facing Patch Notes UI/API changelog
```

The UI/API pair must not fall behind this directory.  
`tests/test_patch_notes_sync.py` enforces date freshness.

## Naming

Use:

```text
YYYY-MM-DD_short-main-title.md
```

Multiple major entries on the same day are allowed when they represent distinct auditable changes.

## Add an Entry For

- formal freeze or acceptance milestone
- architecture/authority decision
- production/runtime safety fix
- major operational incident
- research lifecycle promotion/deprecation
- major roadmap change
- significant documentation-authority change

Do not add a daily patch for every helper rename, formatting-only edit, ordinary test run or trivial refactor.

## Required Content

Record, as applicable:
- reason/context
- exact behavior or authority change
- runtime/report/operator impact
- validation commands and results
- deployment/restart status
- known limitations
- remaining follow-up
- links to canonical source/design evidence

## Historical Integrity

Old entries are audit evidence.

Do not rewrite an old incident/freeze note merely because architecture or naming later changed.  
If a historical statement requires correction, add a new dated correction/clarification record.

Historical milestone identifiers such as M13 or Step5C may remain when they accurately describe the original phase.

## Navigation

Do not maintain a hand-written "latest hotfix" list in this README; it becomes stale.

Use filename dates, Git history, the Patch Notes UI, or repository search for current entries.

## P1.5 Documentation Refactor

See:
- `docs/refactor/documentation_inventory.md`
- `docs/refactor/p1_5_documentation_refactor_plan.md`

P1.5 may reorganize navigation and current canonical documentation, but this directory remains an append-only audit-history surface unless an explicit, reference-safe migration is separately approved.
