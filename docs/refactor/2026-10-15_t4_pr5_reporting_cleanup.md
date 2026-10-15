# Reporting Conflict Cleanup — T4-first Integration Gate

Date: 2026-10-15
Work branch: `refactor/agentra-target-tree`
Before cleanup: `27f22f5598568e2c83f0eb3633156caa8ae1d206`
T4 snapshot used: `c61caab0a94d6e40b015709b720d0266cf0f1d9a`

## Decision and actual edits

- **No branch merge has occurred.** This change makes PR #5 conflict-compatible
  with T4, while keeping T4's code on `refactor/p1.5` authoritative.
- Restore eight conflicted PR5 flat compatibility aliases to the exact original
  `main` Git blob SHA. The original implementations remain importable, and T4
  can later apply its evolved implementation without PR5 override.
- Delete the eight PR5-only **outdated canonical copies** associated with those
  aliases. None are needed by the nine remaining independent migration pairs.
- Align `libs/reporting/trade_report/__init__.py` to T4's exact blob (package
  docstring only). This avoids an add/add content divergence.
- Reduce reporting import-identity tests from the former 17 pairs to the nine
  genuinely independent owners; retain explicit flat-helper smoke checks.
- Preserve **all 138 scripts bulk moves and 141 compatibility wrappers**.
  Removing wrappers without a CLI retirement policy could break Windows/manual
  callers. Do not "clean" by deleting them.

## Restored flat paths and removed obsolete destinations

| Flat T4-owned API restored from main | Obsolete PR5 destination deleted |
| --- | --- |
| `libs/reporting/trade_report_common.py` | `libs/reporting/trade_report/normalization.py` |
| `libs/reporting/trade_reporter_status_text.py` | `libs/reporting/trade_report/operator_text.py` |
| `libs/reporting/trade_report_ai_compact_input.py` | `libs/reporting/trade_report/compact_input.py` |
| `libs/reporting/trade_report_markdown_strategy_memory.py` | `libs/reporting/trade_report_markdown/memory.py` |
| `libs/reporting/trade_report_markdown_truth.py` | `libs/reporting/trade_report_markdown/truth.py` |
| `libs/reporting/trade_story_pipeline_evidence_hydration.py` | `libs/reporting/trade_story/evidence_hydration.py` |
| `libs/reporting/trade_story_pipeline_human_payloads.py` | `libs/reporting/trade_story/human_payloads.py` |
| `libs/reporting/trade_story_pipeline_story_assembly.py` | `libs/reporting/trade_story/assembly.py` |

## Retained independent relocations (9)

- `libs.reporting.trade_report_ai_merge_policy` → `libs.reporting.trade_report.merge_policy`
- `libs.reporting.trade_report_ai_prompting` → `libs.reporting.trade_report.prompting`
- `libs.reporting.trade_report_ai_shared_facts` → `libs.reporting.trade_report.shared_facts`
- `libs.reporting.trade_report_markdown_monitor` → `libs.reporting.trade_report_markdown.monitor`
- `libs.reporting.trade_report_markdown_scanner` → `libs.reporting.trade_report_markdown.scanner`
- `libs.reporting.trade_report_ai_summary_adapter` → `libs.reporting.trade_report.summary_adapter`
- `libs.reporting.trade_report_ai_compact_helpers` → `libs.reporting.trade_report.compact_helpers`
- `libs.reporting.trade_report_ai_llm` → `libs.reporting.trade_report.llm`
- `libs.reporting.trade_story_evidence` → `libs.reporting.trade_story.evidence`

## What remains to be integrated

- The patch-note JSON and Markdown histories from T4 and PR5 diverge. During
  integration preserve **every T4 entry** and append PR5-only entries once,
  preserving order and recounting `entry_count`. Never overwrite T4 history.
- T4 contains extensive Reporting and runtime work. This PR has not adopted or
  merged it. Do **not** merge PR #5 directly to main first or cherry-pick the
  entire PR.
- An integration must run the combined checkout through:
  1. T4-specific Reporting/API facade and monkeypatch/ABI tests.
  2. PR5 nine-owner import identity test.
  3. Scripts 138-move parity and current CLI tests.
  4. Patch-note API/UI read tests, plus web build.
  5. Trading authority leak prevention and Step5C guard regression tests.
- Live order requests, trade-policy changes, and automatic merge are forbidden.
- No local full-checkout pytest is available from the GitHub connector; this
  commit is **structural reconciliation**, not combined runtime acceptance.
- Continue future changes on the existing target-tree branch; any T4 merge
  must have owner approval and a green combined test run.

### Related records

- `docs/refactor/2026-10-15_t4_pr5_reporting_conflict_report.md`
- `docs/refactor/2026-10-15_scripts_bulk_migration.md`
- `tests/test_reporting_relocation_imports.py`
