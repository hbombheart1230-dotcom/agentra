# ACTIVE — P1.5 V2-053 Codex FAIL, corrective rework 054

**State:** `integration/p15-t4-pr5-convergence-20261015` — V3_USER_TARGET_FROZEN / V1_ACCEPTED_WITH_P2_DOC_FINDINGS / V2_CODEX_FAIL_REWORK_REQUIRED / V3_BLOCKED / FIRST_PASS_WITH_DEBT / MAIN_FROZEN / No ZIP in CI (user-facing changed-files-only ZIP allowed outside CI). Final acceptance NOT granted.
**ACTIVE ONE WORK ORDER:** [P15-V2-053-REWORK-054.md](P15-V2-053-REWORK-054.md). Read it and [COMMON_RULES.md](COMMON_RULES.md) only; no historical reread.
**Architecture authority:** [TREE_V3_FROZEN.md](../architecture/TREE_V3_FROZEN.md). No further new target design; focus on actual safe physical module relocation and tests.

**Roles:** GPT architecture/decisions; Claude implementation; Codex independent pinned-SHA audit; GPT+user acceptance. Single development branch: `integration/p15-t4-pr5-convergence-20261015`, no other new task branch. Keep `main` unchanged. The historical source `refactor/p1.5` is an ancestor/retired branch, **not a writable target**.

**Stage markers:** P1.5.2 OPEN for final acceptance; P1.5.3–P1.5.6 FIRST_PASS_WITH_DEBT; T4-D structural gate closed; P1.5.10 wrapper cleanup, Wave D/P1.5.11 and P1.6 runtime migration NOT AUTHORIZED. Current rework 054 only repairs the fail-open Wave B shim oracle, proves/disproves the 37-failure BASE comparison, and fixes the V1/V2 status contradiction. No new physical moves authorized.
**CI guard compatibility:** Preserve the legacy historical link [P15_FAST_TRACK_WAVE_S_020.md](P15_FAST_TRACK_WAVE_S_020.md) once for historical T4 frozen-contract assertions. This is NOT an active order. Keep `refactor/p1.5` and `MAIN_FROZEN` textual provenance for existing frozen CI; remove stale active-branch directives from actual execution logic.

**V1-052 status (2026-10-16):** GPT_ACCEPTED_WITH_P2_DOC_FINDINGS, 13 focused PASS and hosted CI 3/3 SUCCESS — `candidate_risk` moved to `libs/agents/scanner/` with a module-identity shim; evidence [P15-TREE-MIGRATION-V1-052-CLAUDE.md](../evidence/P15-TREE-MIGRATION-V1-052-CLAUDE.md). V1 itself moved only candidate_risk; V2 later moved five additional Scanner context modules.
**V1 independent acceptance:** [Codex findings and V1 acceptance](../evidence/V1-052_GPT_ACCEPTANCE_2026-10-16.md); first action of V2-053 must fix the P2 Gap Matrix text and the 8+5=13 test count. No source change was made in the present work-order activation commit.
**V2-053 status:** IMPLEMENTED / CODEX FAIL — REWORK 054 ACTIVE — 5/5 Scanner context/scoring modules moved to `libs/agents/scanner/context/` with identity shims; V1 P2 matrix wording fixed; evidence [P15-TREE-MIGRATION-V2-053-CLAUDE.md](../evidence/P15-TREE-MIGRATION-V2-053-CLAUDE.md). Codex found P1 fail-open shim test and P1 missing 37-failure equivalence evidence; V3 BLOCKED.
**Rework 054 status:** IMPLEMENTED / PENDING CODEX DELTA AUDIT — strict allowlisted AST shim verifier (22/22 mutations rejected, Wave B 768/768) and BASE-vs-FINAL broad manifest (FINAL_ONLY 0, different-cause 0, identical 37, BASE-only 1 timing flake); evidence [P15-V2-053-REWORK-054-CLAUDE.md](../evidence/P15-V2-053-REWORK-054-CLAUDE.md). V2 acceptance and V3 remain BLOCKED until the delta audit.
**Codex audit finding:** [P15-V2-053-CODEX-FAIL-2026-10-16.md](../evidence/P15-V2-053-CODEX-FAIL-2026-10-16.md). 5/5 bodies and 136/136 replay PASS, but gate fail-open and broad BASE comparison BLOCKED. The 37 alleged pre-existing failures are NOT accepted as established facts. V2 not yet GPT accepted.
**Known deferred:** real report and LLM parity, T4-C session differential and Reporter-feedback fallback fixture, NTFS mtime causality, Scanner cross-seed telemetry. None automatically resolved by V1 tree movement.
**Protected authority:** `graphs/nodes/execute_from_packet.py`, Supervisor/Executor/Broker, Step5C, UEF, Q10/Q12, operational Docker/write paths, UI LLM brief and Reporter queue/lock/artifact effects.

**Branch event:** old feature branches are integrated, design refs retained, and closed draft PR #10 is NOT a main merge approval. This branch remains the ongoing workspace, not a release candidate.
**Artifacts:** update BOTH `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` and `patch_notes.md` for substantive changes, daily evidence, and changed-files-only user ZIP (NO ZIP CI workflow). No live trading/LLM/production writes.

Historical current and completed T4/PR5 acceptance records archived in `archive/CURRENT_2026-10-15_INTEGRATION.md`; do not reread them except when investigating a specific dependency or failed gate.
