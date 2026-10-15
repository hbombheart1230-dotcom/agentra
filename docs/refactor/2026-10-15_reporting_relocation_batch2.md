# 2026-10-15 - Reporting Target-Tree Relocation Batch 2

- Move five implementation bodies byte-for-byte, retaining legacy module-object aliases.
- `trade_report_ai_merge_policy` -> `trade_report/merge_policy`
- `trade_report_ai_prompting` -> `trade_report/prompting`
- `trade_report_ai_shared_facts` -> `trade_report/shared_facts`
- `trade_report_markdown_monitor` -> `trade_report_markdown/monitor`
- `trade_report_markdown_scanner` -> `trade_report_markdown/scanner`
- Existing call sites, top-level Reporting owners and all agent/runtime/execution paths remain untouched.
- Batch 1 prerequisite: 14 import checks and 185 related tests passed.
- Validation results are recorded in the Batch 2 refactor document.

## Compatibility and review

All five canonical implementations have the same bytes as their source in
`a7c4897`. Old module paths alias the canonical module object through
`sys.modules`, as in Batch 1. No consumer import rewrites are needed.
The existing top-level trade_report_ai, trade_report_markdown_clean and
trade_story_pipeline owners remain unchanged. No agent nodes or runtime,
risk, broker, approval or CAS files are changed. Claude T4 was checked against `refactor/p1.5` at
`5c8001c35fb623b8f1a19cfa1b3a1bd9d2e5dca0`. The deterministic helper
was excluded after discovering overlap; its flat implementation remains exactly
as in Batch 1. Remaining Batch 2 code paths have no T4 overlap. Shared UI
patch-note JSON/Markdown are updated as required; merge remains manual.

Revert this Batch 2 commit to roll back; no schema migration is involved.
PR #4 status and PR #5 metadata could not be read because GitHub API returns
Forbidden. The old GPT branch must not be deleted until CLOSED/unmerged is verified.

## Validation

- Batch 1: import regression 14 passed; related reporting/patch-note checks 185 passed.
- Batch 2: 272 passed, 1 dependency deprecation warning (no failures/skips):
  `tests/test_reporting_relocation_imports.py`,
  `tests/test_trade_story_pipeline_enrichment.py`, `tests/test_trade_report_ai.py`,
  `tests/test_trade_summary_symbol_metadata.py`,
  `tests/test_trade_report_ai_separated_adapter.py`,
  `tests/test_single_trade_report.py`, `tests/test_symbol_trade_report.py`,
  `tests/test_intraday_trade_reports.py`, `tests/test_run_ai_trade_report_batch.py`,
  `tests/test_check_trade_report_runtime_regression.py`,
  `tests/test_patch_notes_sync.py`, `tests/apps/api/test_patch_notes.py`,
  `tests/apps/api/test_trade_reports.py` via `.venv/bin/python -m pytest ... -q`.
- Fresh-process canonical-first imports: all five modules and callable/private
  export identities passed. Legacy-first imports are covered by pytest.
- Byte equality against `a7c4897`: all five canonical implementations passed.
- `npm run build`: passed; `npm test`: 7 files / 16 tests passed.
- `git diff --check`: passed. Full repository suite and live trading not run.
- Read-only Git access succeeds. `refs/pull/5/head` equals Batch 1 commit
  `a7c4897986741b0f8c378f41bbc3d99cf784de6c` before this update.

## Changed files

Five old alias files and five new implementation files are listed above.
Additional files:
- `tests/test_reporting_relocation_imports.py`
- `docs/daily_patch/2026-10-15_reporting_relocation_batch2.md`
- `docs/refactor/2026-10-15_reporting_relocation_batch2.md`
- `docs/trading_agent_patch_notes_detailed_update/patch_notes.json`
- `docs/trading_agent_patch_notes_detailed_update/patch_notes.md`

Only the requested target branch is used; no merge or auto-merge is performed.


## T4 overlap correction

T4 branch: `refactor/p1.5`, commit `5c8001c35fb623b8f1a19cfa1b3a1bd9d2e5dca0`.
Comparison base: `2f95bba429636ee15ae9a399cc4ff7c4e6dcd5cb`; 719 T4 paths.
The initial Batch 2 commit included deterministic.py; a follow-up removes that
move and restores the legacy deterministic file byte-for-byte from Batch 1.
Final Batch 2 changes no T4 implementation files. Required UI changelog updates
share two documentation paths with T4 and need normal integration review.

Inherited Batch 1 code overlaps with T4 (not changed by Batch 2):
- `libs/reporting/trade_report/__init__.py`
- `libs/reporting/trade_report/normalization.py`
- `libs/reporting/trade_report/operator_text.py`
- `libs/reporting/trade_report_ai_compact_input.py`
- `libs/reporting/trade_report_markdown_strategy_memory.py`
- `libs/reporting/trade_report_markdown_truth.py`
- `libs/reporting/trade_story_pipeline_evidence_hydration.py`
- `libs/reporting/trade_story_pipeline_human_payloads.py`
- `libs/reporting/trade_story_pipeline_story_assembly.py`

These inherited overlaps require manual integration before any merge.
