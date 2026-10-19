# P1.5 historical UI patch-note source provenance — 2026-10-19

**Scope:** Existing UI `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` **sources[]** from Git integration `6a4822fe725aa06d6d315f6fb2f7a96ca8f047f3`, before this ledger is added. `source` path means a historical citation, NOT an instruction to restore missing runtime output or to edit historical claims.

**Exact finding: 14 distinct absent Git paths / 16 citation occurrences.** Git tracked **directories** satisfy a path reference; `docs/evaluation/` and `libs/runtime/controlled_mock_lanes/` are present and are **NOT missing**. GitHub check is repo-tree only, not evidence that historically generated files never existed on operating systems. This is a SOURCE-AVAILABILITY CLASSIFICATION, not independently VERIFIED file provenance. No tracked source is silently rewritten. This registry documents the missing link rather than inventing evidence.

## Missing references (exact current-tree paths)

| Original historical `sources[]` value | Uses | Referencing version(s) | Disposition | Evidence / required follow-up |
|---|---:|---|---|---|
| `data/logs/events.jsonl` | 2 | Docker Live-Open Observation and Daily UEF Freshness Incident; P1.2 Closed and P1.3 Full Docker Frozen | **EXTERNAL_APPEND_ONLY_LOG / ORIGINAL UNAVAILABLE** | Historical runtime event/execution log not tracked; do not access live paths or regenerate |
| `data/logs/execution_readiness_evidence/2026-10-08.jsonl` | 1 | P1.2 Closed and P1.3 Full Docker Frozen | **EXTERNAL_APPEND_ONLY_LOG / ORIGINAL UNAVAILABLE** | Historical runtime event/execution log not tracked; do not access live paths or regenerate |
| `deploy/compose/.env` | 1 | Agentra Root Migration | **EXTERNAL_SECRET_CONFIG / ORIGINAL UNAVAILABLE** | Intentionally untracked secret/environment; NEVER copy, synthesize, commit or link live secret |
| `docs/01_overview.md` | 2 | M14–M16; Current | **HISTORIC_FLAT_DOC / ORIGINAL UNAVAILABLE** | Language-specific `docs/en/` and `docs/ko/` candidates exist; match canonical original revision/language before mapping |
| `docs/02_principles.md` | 1 | M14–M16 | **HISTORIC_FLAT_DOC / ORIGINAL UNAVAILABLE** | Language-specific `docs/en/` and `docs/ko/` candidates exist; match canonical original revision/language before mapping |
| `docs/05_runtime_flow.md` | 1 | M14–M16 | **HISTORIC_FLAT_DOC / ORIGINAL UNAVAILABLE** | Language-specific `docs/en/` and `docs/ko/` candidates exist; match canonical original revision/language before mapping |
| `docs/07_execution_and_guards.md` | 1 | M14–M16 | **HISTORIC_FLAT_DOC / ORIGINAL UNAVAILABLE** | Language-specific `docs/en/` and `docs/ko/` candidates exist; match canonical original revision/language before mapping |
| `docs/08_observability.md` | 1 | v0.1 | **HISTORIC_FLAT_DOC / ORIGINAL UNAVAILABLE** | Language-specific `docs/en/` and `docs/ko/` candidates exist; match canonical original revision/language before mapping |
| `libs/event_logger.py` | 1 | v0.1 | **LEGACY_MOVED_CANDIDATE / ORIGINAL UNAVAILABLE** | Current `libs/core/event_logger.py` is candidate only; prove historical file identity at referenced revision before alias |
| `reports/evaluation/alpha_research_board/2026-10-08/generations/UEF9RUN_559c27f2d0d1f62b/COMPLETE.json` | 1 | P1.2 Closed and P1.3 Full Docker Frozen | **UNTRACKED_GENERATED_EVIDENCE / ORIGINAL UNAVAILABLE** | Historical generated/ignored report or UEF COMPLETE; no proven source bytes, never fabricate or restore |
| `reports/evaluation/baseline_btc_woori` | 1 | Independent Baselines | **UNTRACKED_GENERATED_EVIDENCE / ORIGINAL UNAVAILABLE** | Historical generated/ignored report or UEF COMPLETE; no proven source bytes, never fabricate or restore |
| `reports/evaluation/baseline_samsung_hynix` | 1 | Independent Baselines | **UNTRACKED_GENERATED_EVIDENCE / ORIGINAL UNAVAILABLE** | Historical generated/ignored report or UEF COMPLETE; no proven source bytes, never fabricate or restore |
| `reports/operator_summary/daily/2026-10-06/daily_report.md` | 1 | Docker Live-Open Observation and Daily UEF Freshness Incident | **UNTRACKED_GENERATED_EVIDENCE / ORIGINAL UNAVAILABLE** | Historical generated/ignored report or UEF COMPLETE; no proven source bytes, never fabricate or restore |
| `reports/operator_summary/daily/2026-10-08/closeout_maintenance.json` | 1 | P1.2 Closed and P1.3 Full Docker Frozen | **UNTRACKED_GENERATED_EVIDENCE / ORIGINAL UNAVAILABLE** | Historical generated/ignored report or UEF COMPLETE; no proven source bytes, never fabricate or restore |

## Preservation and acceptance

1. Keep prior `patch_notes.json` entry `sources[]` values **verbatim** (and old Markdown entries) for audit reproducibility. Missing historical source ≠ authority to rewrite a passing UEF or frozen record; preserve the open evidence-availability debt.
2. To promote a historical mapping to `RESOLVED`, independently prove exact original SHA/file identity and reference URL; multilingual topic similarity or later identically named artifact is **not enough**. If unavailable, keep explicit `UNAVAILABLE_HISTORICAL_EXTERNAL` with no new object created.
3. `deploy/compose/.env`, `data/logs/**`, `reports/**` are runtime/private/generated paths. No read from production, no secret content reproduction, no fake COMPLETE.json, no code change just to satisfy a link checker.
4. This ledger is the **modern explanatory index**, not an executable patchnote or substitute for origin artifacts. The UI's existing patchnote contract and original record remain in place.
5. Fresh reviewer must compare **14 unique / 16 uses** against the exact current Git tree and verify no newly introduced absent source from this docs-only change. No DOC_FREEZE acceptance solely from this ledger.

## Other pending DOC_FREEZE gates

- `docs/refactor/DOC_REGISTRY.csv`: 339 original paths inventoried, but per-document classification/content and all inbound links not FULLY verified. Do not label path-only evidence as semantic PASS.
- Two **legacy CI workflow dispatch/main-era assertions** in `.github/workflows/p15-integration-t4-regression.yml` and `p152-r2c-residual-regression.yml` still require closed fixed-role, single-wave, `No ZIP`, obsolete `CURRENT State:` strings. Their push triggers point at old branch names; the first also covers `main` and PR-to-main. **Do not change current docs to satisfy these obsolete predicates.** The CI owner must update the assertion logic with narrow diff and preserve actual regression/security checks before any use of these workflows for main acceptance.
- Historical `P15_EXECUTION_PROTOCOL.md` and `p1_5_small_owner_policy_and_rollback_decision_v1_2.md` have imperative legacy clauses. Their original dated contract and test evidence remain historical; current operational rules exclusively D00 + #20.
- Independent DOC-E review, newest SHA checks and operator approval required before DOC_FREEZE_PASS.
