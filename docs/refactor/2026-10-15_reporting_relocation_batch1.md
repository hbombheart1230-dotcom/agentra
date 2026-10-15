# Reporting Target-Tree Relocation — Batch 1

Date: 2026-10-15
Branch: `refactor/agentra-target-tree`
Base main: `2f95bba429636ee15ae9a399cc4ff7c4e6dcd5cb`

## Scope

This is a **file relocation**, not a business-logic refactor. The following 12
Reporting helper modules are copied byte-for-byte to target subpackages.
Original import locations are retained as small `sys.modules` alias modules
so legacy imports, including imports of private helpers and monkeypatch-based
tests, still reference the exact same module object.

| Previous module | New canonical module |
| --- | --- |
| `libs/reporting/trade_report_common.py` | `libs/reporting/trade_report/normalization.py` |
| `libs/reporting/trade_reporter_status_text.py` | `libs/reporting/trade_report/operator_text.py` |
| `libs/reporting/trade_report_ai_summary_adapter.py` | `libs/reporting/trade_report/summary_adapter.py` |
| `libs/reporting/trade_report_ai_compact_helpers.py` | `libs/reporting/trade_report/compact_helpers.py` |
| `libs/reporting/trade_report_ai_compact_input.py` | `libs/reporting/trade_report/compact_input.py` |
| `libs/reporting/trade_report_ai_llm.py` | `libs/reporting/trade_report/llm.py` |
| `libs/reporting/trade_report_markdown_strategy_memory.py` | `libs/reporting/trade_report_markdown/memory.py` |
| `libs/reporting/trade_report_markdown_truth.py` | `libs/reporting/trade_report_markdown/truth.py` |
| `libs/reporting/trade_story_evidence.py` | `libs/reporting/trade_story/evidence.py` |
| `libs/reporting/trade_story_pipeline_evidence_hydration.py` | `libs/reporting/trade_story/evidence_hydration.py` |
| `libs/reporting/trade_story_pipeline_human_payloads.py` | `libs/reporting/trade_story/human_payloads.py` |
| `libs/reporting/trade_story_pipeline_story_assembly.py` | `libs/reporting/trade_story/assembly.py` |

## Invariants and exclusions

- No agent node, Commander, Strategist, Scanner, Monitor, Supervisor, Executor,
  risk/guard, broker, Step5C/Step5D or trading configuration was modified.
- No changes to the *contents* of the relocated module bodies; Git blob hashes
  are reused rather than rewriting code.
- No runtime application import call sites changed in this batch.
- Existing import paths stay importable; no duplicate executable implementation.
- `libs/reporting/trade_report_ai.py`,
  `libs/reporting/trade_report_markdown_clean.py` and
  `libs/reporting/trade_story_pipeline.py` are intentionally left untouched:
  those high-impact owners require separate verification.
- The three new package `__init__.py` files carry no imports or side effects.

## Verification

Run locally against a full checkout:

```bash
python -m pytest tests/test_reporting_relocation_imports.py -q
python -m pytest tests/test_trade_story_pipeline_enrichment.py tests/test_trade_report_ai.py tests/test_trade_summary_symbol_metadata.py -q
python -m pytest tests/test_patch_notes_sync.py tests/apps/api/test_patch_notes.py -q
```

Connector-side checks: GitHub blob identity, only intended paths changed, JSON
append-only patch-note validation, import-free package inits.

**Not yet verified here:** Python project imports, pytest results, UI production
build, and real-run integration. These are merge gates, not implied PASS.

## Rollback

Revert this commit or drop the draft PR. The modules are byte-for-byte copies
of the original code and the unchanged call sites can be restored with no
schema/behavior migration. Preserve the T4 branch independently.

## Next batches

1. More low-dependency Reporter leaf helpers, maintaining module aliases.
2. Trade Report / Trade Story top-level entrypoints (after targeted test parity).
3. Operator UI read models and larger ownership changes later, with an explicit
   overlap check against Claude's T4 code at merge time.
