# P1.5.2 — Guard 006 review and façade size continuation (2026-10-12)

Git confirmed Guard 006 SHA `f6cc71b` with nine changed paths, only `main` and `refactor/p1.5`. Claude reports 61 guard PASS and 656 regression PASS/1 SKIP, offline seam 357 cases/57 functions, 0 focused writes. Codex review is now active per `docs/refactor/work_orders/P15_R3_CODEX_GUARD_AUDIT_007.md`.

Measured three façade files at this SHA: AI 1958 LOC (182 defs), Markdown 1891 (209 defs), Story 562 (45 defs), total 4411 vs original 18743. The large public-function and dependency-wiring surfaces still contain further extraction opportunities. `SIZE_DEFERRED` remains OPEN, not waived; the queued `P15_R3_FACADE_LOC_MAX_REDUCTION_008.md` mandates maximum safe domain/consumer-based reduction after the guard audit. No production code was changed in this task. Real report/LLM parity BLOCKED/NOT RUN; controlled-mock-lane write-isolation OPEN. P1.5.2 OPEN, P1.5.3 unauthorized.
