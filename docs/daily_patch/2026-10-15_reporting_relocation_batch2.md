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

- Batch 2 validation: **272 pytest passed**, **16 web tests passed**, production build passed; five implementation byte comparisons and canonical-first import checks passed. Full repository suite/live trading not run.
