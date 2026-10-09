# P1.5.2 Reporting Public Façade Symbol Ledger — Conservative Remote Inventory

Date: 2026-10-09
Reference source SHA: `73e374acd3b06fb94bca12631067860b024e01aa`, branch `refactor/p1.5`
JSON ledger: `docs/refactor/p1_5_2_facade_symbol_ledger_2026-10-09.json`

**Source inspection only.** No local user-data, runtime/monkeypatch tracing or production-write evidence was available. The inventory therefore preserves ALL symbols and marks consumer compatibility as NOT_RUN_LOCAL. It must not be mistaken for proof that any wrapper can be safely deleted.

## Quantified façade audit

| Public facade | Physical LOC | Top-level defs/classes | Imports |
|---|---:|---:|---:|
| `libs/reporting/trade_report_ai.py` | 3039 | 182 | 29 import statements |
| `libs/reporting/trade_report_markdown_clean.py` | 3043 | 209 | 17 import statements |
| `libs/reporting/trade_story_pipeline.py` | 948 | 45 | 19 import statements |

Total indexed top-level definitions/classes: **436**. Name-heuristic truth/fallback/model/provenance/order risk markers: **51** (review cues, NOT proven defects).

All symbols include original exact file and line ranges, provisional KEEP or WRAPPER classification, formatting/evidence/LLM/composition responsibility tags, and a mandatory P1.5.10 consumer-proof retirement constraint. No DEAD conclusion is inferred from apparent private naming; no public API deletion is authorized. Imported aliases have a separate `imports` map.

## Required outstanding proofs

- Canonical `C:\Agentra` imports and real report corpus; hidden monkeypatch callers and by-name dynamic consumers; exact output byte/schema/golden comparisons; prompt counts/fallback/retry timeouts; full pytest baseline.
- Review flagged symbols and produce true KEEP/MOVE/WRAPPER/DEAD/SAFETY-LOCK decisions with verified caller evidence rather than guessing from names.
- Zero tolerance for report truth-source changes, side effects, UEF/Step5C/D/R6.2, Supervisor/Executor and production order modifications.

## Next source action

Prioritize existing legacy oversized `trade_report/markdown_summary.py`, `trade_report/operator_text.py` and `trade_story_pipeline_human_payloads.py` for one coherent small-owner extraction at a time, without deleting external facade seams. P1.5.2 stays OPEN; P1.5.3 cannot start based on this inventory.
