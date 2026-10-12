# P1.5.2 Codex local acceptance and Windows parity-tool fix

## Scope

The P1.5.2 local acceptance tool now decodes `git show` source as UTF-8 explicitly, avoiding Windows cp949 failures on Korean Reporting source. No runtime Reporting or trade-execution code changed.

## Evidence

- Owner parity: 38 AST-preserved functions in 26 bounded Owners — PASS.
- P1.5.2 selected tests: 295 passed, 1 skipped; production-path write audit fired, so acceptance remains OPEN.
- Full pytest: NOT PASS; FastAPI missing during collection and production-path writes were detected.
- Real report/LLM snapshot parity: NOT RUN because no independently frozen before/after copies were available.

Evidence: `docs/refactor/work_orders/evidence/P15-R2-CODEX-LOCAL-ACCEPTANCE-2026-10-12.md`.
