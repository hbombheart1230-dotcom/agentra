> **HISTORICAL WORK ORDER — NOT CURRENT AUTHORIZATION.** ACTIVE/READY/pending statuses, role assignments, branch/worktree cleanup commands, and next steps below describe the original pinned historical task only. Do **not** restart implementation or audit, create/delete branches/worktrees, or run operational checks from this page. Current authority: [D00](../../../ENGINEERING_DELIVERY_POLICY.md) + [CURRENT](../CURRENT.md) + [GitHub Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20). Original safety restrictions and recorded SHA/PASS/FAIL/SKIP evidence remain intact.

# ACTIVE — Agentra P1.5 T4 + PR #5 isolated convergence and integrated CI

**State:** integration/p15-t4-pr5-convergence-20261015 (baseline refactor/p1.5) — INTEGRATION_VERIFYING / T4-D STRUCTURAL_GATE_CLOSED / MAIN_FROZEN / No ZIP (CI packaging forbidden; user patch archive external only).
**Stage markers (CI guard):** P1.5.2 OPEN (final acceptance); P1.5.3-P1.5.6 FIRST_PASS_WITH_DEBT; Wave D/P1.5.11 NOT STARTED.
**CI main transition (2026-10-15):** required regression/contract workflows now also run on `main` pushes and PRs to `main` (integration trigger kept); branch-history-only checks classified, none deleted; hosted PR-to-main run BLOCKED until a Draft PR is observed. See [ci_main_transition_2026_10_15.md](../../ci_main_transition_2026_10_15.md).

**Current 2026-10-15:** T4-A/B/C accepted. T4-D independently audited (15 structural+contract PASS, 93 focused PASS, 189 records/6,456 variants/0 mismatch), originally BLOCKED solely awaiting final CI. GitHub FINAL CI 38702590672 now SUCCESS including required Windows native accounting 5/5. GPT closes T4-D structural gate for integration; this does NOT declare P1.5 final acceptance or a new Codex final audit submission. Evidence: [T4-D Codex+CI closure](../evidence/P15-T4-D-CODEX-CI-CLOSURE-046.md). Source branches frozen: refactor/p1.5 ad365913 and PR5 fe627978. Isolated merge 496d495 with 264 existing patch notes; integration CI pending.

**Codex REWORK disposition (2026-10-15):** P1 CI-ZIP policy conflict corrected by deleting `.github/workflows/p15-integration-changed-files-bundle.yml`; `No ZIP / CI packaging forbidden` remains binding. P2 Windows baseline CRLF mismatch addressed with explicit LF in `libs/reporting/baseline_artifact_io.py` and new Windows-native two-case CI. Required Q10/Q12 Windows byte assertions now 2/2 PASS on 8405ed8, but that native-Windows job still failed the fast-tier production-write audit for directory-only mtime changes. New full-tier production FILE audit is required to avoid directory-mtime-only false positives, without disabling write checks. Scope guard now checks original T4-D slice and separately guards merged HEAD T4 source/authority paths. Final ACCEPT remains blocked until CI and independent review. [Fix/evidence](../evidence/P15-INTEGRATION-CODEX-REWORK-048.md).

**Consumer dependency evidence:** [P1.5 tracked-source inventory](../../architecture/consumer_inventory_findings_20261015.md); Codex independent review [task](../P15-INTEGRATION-CODEX-CONSUMER-AUDIT-047.md). `ARCH_CONVERGENCE_NOT_APPROVED` until signed review.

**One active work order:** T4+PR5 integrated validation and SHA-pinned architecture inventory on integration/p15-t4-pr5-convergence-20261015; not T4-D implementation. Main and original branches untouched.

**Open/deferred:** T4-C BASE×2/FEATURE×2 session differential P2 NOT RUN; REAL_LLM_PARITY_NOT_RUN, REAL_REPORT_PARITY_BLOCKED, NTFS mtime P2, Scanner cross-seed telemetry P2, freeze CLI PYTHONPATH P2, and the Reporter-feedback fallback fixture-coverage P2. Historical unrelated UEF results replicated on pristine BASE (86 PASS, 20 FAIL, 2 ERROR); do not relabel as new Strategist regression. T5 / P1.5.10 / Wave D / P1.6 NOT STARTED or authorized; main and operational worktrees protected.

**Mandatory architecture convergence:** integration must first pass Linux/Windows combined gates; then SHA-pinned current overview/modules/dependency SVG, editable target draw.io, gap matrix, and user/GPT approval. ARCH_CONVERGENCE_DRAFT_WRITTEN_NOT_APPROVED; no folder moves or P1.5.10.

**CI compatibility anchor:** [historical Fast Track authority](../P15_FAST_TRACK_WAVE_S_020.md) remains exactly one legacy link required by preexisting T4 CI. This is not an active work order and confers no Wave D permission.

**Read minimal context:** this CURRENT + integration daily patch and evidence + touched files only. Do not reread completed T0–T4 archives. Integration Owner: GPT design/integration; Claude implementation on request; Codex independent validation.

**Branch policy (user 2026-10-15):** ONE active development branch only (`integration/p15-t4-pr5-convergence-20261015`). Do not create new branches. `main` remains protected as default until independent acceptance; legacy design/feature branches are retirement candidates after preservation of unique work. Final state must be `main` only, not an unverified direct merge.

**One-branch design preservation:** 23 unique P1.6/P2+ historical Markdown documents carried verbatim into integration; [SHA/paths](../../branch_convergence/2026-10-15_preserved_design_branch_materials.md). Not an approval to implement those designs. Two design branch refs retained pending integration acceptance and main assimilation.
