# ACTIVE — P1.5 HYBRID-7 V3 tree migration, first implementation V1-052

**State:** `integration/p15-t4-pr5-convergence-20261015` — V3_USER_TARGET_FROZEN / V1_IMPLEMENTATION_AUTHORIZED / FIRST_PASS_WITH_DEBT / MAIN_FROZEN / No ZIP in CI (user-facing changed-files-only ZIP allowed outside CI). Not FINAL_ACCEPTED.
**ACTIVE ONE WORK ORDER:** [P15-TREE-MIGRATION-V1-052.md](P15-TREE-MIGRATION-V1-052.md). Read it and [COMMON_RULES.md](COMMON_RULES.md) only; no historical reread.
**Architecture authority:** [TREE_V3_FROZEN.md](../architecture/TREE_V3_FROZEN.md). No further new target design; focus on actual safe physical module relocation and tests.

**Roles:** GPT architecture/decisions; Claude implementation; Codex independent pinned-SHA audit; GPT+user acceptance. Single development branch: `integration/p15-t4-pr5-convergence-20261015`, no other new task branch. Keep `main` unchanged. The historical source `refactor/p1.5` is an ancestor/retired branch, **not a writable target**.

**Stage markers:** P1.5.2 OPEN for final acceptance; P1.5.3–P1.5.6 FIRST_PASS_WITH_DEBT; T4-D structural gate closed; P1.5.10 wrapper cleanup, Wave D/P1.5.11 and P1.6 runtime migration NOT AUTHORIZED. Current V1-052 is one strictly bounded pure-helper pilot and does not waive the broader architecture safety gate.
**CI guard compatibility:** Preserve the legacy historical link [P15_FAST_TRACK_WAVE_S_020.md](P15_FAST_TRACK_WAVE_S_020.md) once for historical T4 frozen-contract assertions. This is NOT an active order. Keep `refactor/p1.5` and `MAIN_FROZEN` textual provenance for existing frozen CI; remove stale active-branch directives from actual execution logic.

**Known deferred:** real report and LLM parity, T4-C session differential and Reporter-feedback fallback fixture, NTFS mtime causality, Scanner cross-seed telemetry. None automatically resolved by V1 tree movement.
**Protected authority:** `graphs/nodes/execute_from_packet.py`, Supervisor/Executor/Broker, Step5C, UEF, Q10/Q12, operational Docker/write paths, UI LLM brief and Reporter queue/lock/artifact effects.

**Branch event:** old feature branches are integrated, design refs retained, and closed draft PR #10 is NOT a main merge approval. This branch remains the ongoing workspace, not a release candidate.
**Artifacts:** update BOTH `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` and `patch_notes.md` for substantive changes, daily evidence, and changed-files-only user ZIP (NO ZIP CI workflow). No live trading/LLM/production writes.

Historical current and completed T4/PR5 acceptance records archived in `archive/CURRENT_2026-10-15_INTEGRATION.md`; do not reread them except when investigating a specific dependency or failed gate.
