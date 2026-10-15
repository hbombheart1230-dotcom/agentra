# ACTIVE — Agentra P1.5 T4 + PR #5 isolated convergence and integrated CI

**State:** integration/p15-t4-pr5-convergence-20261015 (baseline refactor/p1.5) — INTEGRATION_VERIFYING / T4-D STRUCTURAL_GATE_CLOSED / MAIN_FROZEN / No ZIP (CI packaging forbidden; user patch archive external only).
**Stage markers (CI guard):** P1.5.2 OPEN (final acceptance); P1.5.3-P1.5.6 FIRST_PASS_WITH_DEBT; Wave D/P1.5.11 NOT STARTED.

**Current 2026-10-15:** T4-A/B/C accepted. T4-D independently audited (15 structural+contract PASS, 93 focused PASS, 189 records/6,456 variants/0 mismatch), originally BLOCKED solely awaiting final CI. GitHub FINAL CI 38702590672 now SUCCESS including required Windows native accounting 5/5. GPT closes T4-D structural gate for integration; this does NOT declare P1.5 final acceptance or a new Codex final audit submission. Evidence: [T4-D Codex+CI closure](evidence/P15-T4-D-CODEX-CI-CLOSURE-046.md). Source branches frozen: refactor/p1.5 ad365913 and PR5 fe627978. Isolated merge 496d495 with 264 existing patch notes; integration CI pending.

**Codex REWORK disposition (2026-10-15):** P1 CI-ZIP policy conflict corrected by deleting `.github/workflows/p15-integration-changed-files-bundle.yml`; `No ZIP / CI packaging forbidden` remains binding. P2 Windows baseline CRLF mismatch addressed with explicit LF in `libs/reporting/baseline_artifact_io.py` and new Windows-native two-case CI. Both require verification on this fix SHA; no pre-emptive ACCEPT. [Fix/evidence](evidence/P15-INTEGRATION-CODEX-REWORK-048.md).\n\n**Consumer dependency evidence:** [P1.5 tracked-source inventory](../architecture/consumer_inventory_findings_20261015.md); Codex independent review [task](P15-INTEGRATION-CODEX-CONSUMER-AUDIT-047.md). `ARCH_CONVERGENCE_NOT_APPROVED` until signed review.

**One active work order:** T4+PR5 integrated validation and SHA-pinned architecture inventory on integration/p15-t4-pr5-convergence-20261015; not T4-D implementation. Main and original branches untouched.

**Open/deferred:** T4-C BASE×2/FEATURE×2 session differential P2 NOT RUN; REAL_LLM_PARITY_NOT_RUN, REAL_REPORT_PARITY_BLOCKED, NTFS mtime P2, Scanner cross-seed telemetry P2, freeze CLI PYTHONPATH P2, and the Reporter-feedback fallback fixture-coverage P2. Historical unrelated UEF results replicated on pristine BASE (86 PASS, 20 FAIL, 2 ERROR); do not relabel as new Strategist regression. T5 / P1.5.10 / Wave D / P1.6 NOT STARTED or authorized; main and operational worktrees protected.

**Mandatory architecture convergence:** integration must first pass Linux/Windows combined gates; then SHA-pinned current overview/modules/dependency SVG, editable target draw.io, gap matrix, and user/GPT approval. ARCH_CONVERGENCE_DRAFT_WRITTEN_NOT_APPROVED; no folder moves or P1.5.10.

**CI compatibility anchor:** [historical Fast Track authority](P15_FAST_TRACK_WAVE_S_020.md) remains exactly one legacy link required by preexisting T4 CI. This is not an active work order and confers no Wave D permission.

**Read minimal context:** this CURRENT + integration daily patch and evidence + touched files only. Do not reread completed T0–T4 archives. Integration Owner: GPT design/integration; Claude implementation on request; Codex independent validation.
