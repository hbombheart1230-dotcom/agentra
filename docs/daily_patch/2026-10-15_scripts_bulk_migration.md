# 2026-10-15 - Scripts Bulk Migration

- Reuse prior Scripts inventory: 157 candidates processed; 138 moved, 19 held with per-file evidence.
- Move 53 Research, 73 Diagnostics and 12 Maintenance implementations into category packages; preserve old CLI/import contracts with 138 thin wrappers.
- 42 local-implementation Python files, 8 existing forwarders, 141 compatibility wrappers and one package marker remain at root; 20 Windows/non-Python files remain unchanged.
- Original implementation blobs are recovered byte-for-byte by reversing only bootstrap changes. Business logic, trading policy and Config 8 changes: zero.
- Import/signature/root checks: 276 passed; CLI parity: 828 passed; 74 existing test files: 300 passed.
- Preserve 48 Operations and 2 original T4-owned Scripts paths. New T4 code overlap: zero. Only the two approved shared UI changelog paths are append-only exceptions.
- Reporting Batch 3 remains paused. Same branch / PR #5 Draft workflow; no merge or auto-merge.
- Details: docs/refactor/2026-10-15_scripts_bulk_migration.md.
- Full 157-candidate ledger: docs/refactor/2026-10-15_scripts_bulk_manifest.json.
- Final UI patch-note checks: 5 passed; append-only integrity verified. Successful pytest scratch/cache and validation runtime artifacts cleaned outside the repository.
