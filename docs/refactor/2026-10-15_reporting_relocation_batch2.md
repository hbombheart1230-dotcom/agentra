# 2026-10-15 - Reporting Target-Tree Relocation Batch 2

- Move six implementation bodies byte-for-byte, retaining legacy module-object aliases.
- `trade_report_ai_deterministic` -> `trade_report/deterministic`
- `trade_report_ai_merge_policy` -> `trade_report/merge_policy`
- `trade_report_ai_prompting` -> `trade_report/prompting`
- `trade_report_ai_shared_facts` -> `trade_report/shared_facts`
- `trade_report_markdown_monitor` -> `trade_report_markdown/monitor`
- `trade_report_markdown_scanner` -> `trade_report_markdown/scanner`
- Existing call sites, top-level Reporting owners and all agent/runtime/execution paths remain untouched.
- Batch 1 prerequisite: 14 import checks and 185 related tests passed.
- Validation results are recorded in the Batch 2 refactor document.

## Compatibility and review

All six canonical implementations have the same bytes as their source in
`a7c4897`. Old module paths alias the canonical module object through
`sys.modules`, as in Batch 1. No consumer import rewrites are needed.
The existing top-level trade_report_ai, trade_report_markdown_clean and
trade_story_pipeline owners remain unchanged. No agent nodes or runtime,
risk, broker, approval or CAS files are changed. Claude T4 overlap cannot
be independently checked without its file list or commit; merge remains manual.

Revert this Batch 2 commit to roll back; no schema migration is involved.
PR #4 status and PR #5 metadata could not be read because GitHub API returns
Forbidden. The old GPT branch must not be deleted until CLOSED/unmerged is verified.

## Validation

- Batch 1: import regression 14 passed; related reporting/patch-note checks 185 passed.
- Batch 2: 273 passed, 1 dependency deprecation warning (no failures/skips):
  `tests/test_reporting_relocation_imports.py`,
  `tests/test_trade_story_pipeline_enrichment.py`, `tests/test_trade_report_ai.py`,
  `tests/test_trade_summary_symbol_metadata.py`,
  `tests/test_trade_report_ai_separated_adapter.py`,
  `tests/test_single_trade_report.py`, `tests/test_symbol_trade_report.py`,
  `tests/test_intraday_trade_reports.py`, `tests/test_run_ai_trade_report_batch.py`,
  `tests/test_check_trade_report_runtime_regression.py`,
  `tests/test_patch_notes_sync.py`, `tests/apps/api/test_patch_notes.py`,
  `tests/apps/api/test_trade_reports.py` via `.venv/bin/python -m pytest ... -q`.
- Fresh-process canonical-first imports: all six modules and callable/private
  export identities passed. Legacy-first imports are covered by pytest.
- Byte equality against `a7c4897`: all six canonical implementations passed.
- `npm run build`: passed; `npm test`: 7 files / 16 tests passed.
- `git diff --check`: passed. Full repository suite and live trading not run.
- Read-only Git access succeeds. `refs/pull/5/head` equals Batch 1 commit
  `a7c4897986741b0f8c378f41bbc3d99cf784de6c` before this update.

## Changed files

Six old alias files and six new implementation files are listed above.
Additional files:
- `tests/test_reporting_relocation_imports.py`
- `docs/daily_patch/2026-10-15_reporting_relocation_batch2.md`
- `docs/refactor/2026-10-15_reporting_relocation_batch2.md`
- `docs/trading_agent_patch_notes_detailed_update/patch_notes.json`
- `docs/trading_agent_patch_notes_detailed_update/patch_notes.md`

Only the requested target branch is used; no merge or auto-merge is performed.
