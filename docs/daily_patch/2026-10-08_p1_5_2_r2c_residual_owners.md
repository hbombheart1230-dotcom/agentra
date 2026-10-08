# 2026-10-08 — P1.5.2 R2-C residual news, scanner and provenance extraction

## Scope
Continue the R2-C trade-story structural refactor from `codex/p1.5.2-reporting-r2c-20261007` (baseline `602d935`). This change only moves owner code and preserves import/function names on `libs/reporting/trade_story_pipeline.py`.

## Ownership
- `trade_story_pipeline_news.py`: 15 existing helpers for headline cleanup, ticker matching, ranked news headline selection and news-to-scanner contribution calculations.
- `trade_story_pipeline_scanner.py`: 8 existing helpers for Korean index bullets, score breakdown, candidate evidence rows, scanner rank/fit selection traces.
- `trade_story_pipeline_provenance.py`: 13 existing helpers for evidence completeness, commander source refs, section provenance and report section provenance seeds.
- `trade_story_pipeline.py`: retains same imported compatibility names and call-time dependencies for extracted owners.

## Façade reduction
```text
R2-C baseline    4,527 LOC
Previous tranche 1,873 LOC
This tranche     1,200 LOC
Residual drop      673 LOC (35.9% of prior façade)
Total drop       3,327 LOC (73.5% of R2-C baseline)
```

## Compatibility and safety
- Owner functions refer back to callable helpers on the façade **at call time**, so monkeypatch seams are not bound to stale module globals.
- No changes to output schemas, classification rules, news/scanner score arithmetic, evidence truth precedence, LLM calls, Supervisor/Executor authority, UEF semantics, broker paths, or execution toggles.
- All work performed on a separate feature branch; no merge to `main`, runtime restart, Docker deployment or production orders.

## Verification
- Existing Python 3.12 broad Reporting + trade-story regression: **337 passed, 1 pre-existing warning**.
- Extracted-owner compilation: PASS.
- New helper patch compatibility tests plus Patch Notes API/sync checks: enforced on GitHub Actions for this branch (final result recorded on the run).
- Tests run in ephemeral CI runners with cacheprovider disabled; no historical repository test output is committed.

## Status
```text
P1.5.2 R2-C           ACTIVE / PARTIAL PASS
NEWS / SCANNER OWNER   EXTRACTED
PROVENANCE OWNER       EXTRACTED
PUBLIC HELPER NAMES    PRESERVED
NEXT                   final façade seam audit and residual-function sizing
```
