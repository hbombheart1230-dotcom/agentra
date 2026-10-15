# 2026-10-15 - Reporting Target-Tree Relocation Batch 1

- Moved 12 Reporter support modules without altering their implementation bytes:
  `trade_report` (6), `trade_report_markdown` (2), `trade_story` (4).
- Existing flat module paths now load the corresponding canonical module using
  `sys.modules` aliases; old callers require no import rewrites.
- No Claude T4 runtime files, trading signals, approval, guards or CAS affected.
- Added import-identity regression test and explicit rollback/merge gates.
- See `docs/refactor/2026-10-15_reporting_relocation_batch1.md`.
- Required local pytest and web build are pending; this is not yet production
  acceptance.
