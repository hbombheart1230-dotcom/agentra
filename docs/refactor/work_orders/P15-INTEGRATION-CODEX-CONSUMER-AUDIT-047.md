> **HISTORICAL WORK ORDER — NOT CURRENT AUTHORIZATION.** ACTIVE/READY/pending statuses, role assignments, branch/worktree cleanup commands, and next steps below describe the original pinned historical task only. Do **not** restart implementation or audit, create/delete branches/worktrees, or run operational checks from this page. Current authority: [D00](../../ENGINEERING_DELIVERY_POLICY.md) + [CURRENT](CURRENT.md) + [GitHub Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20). Original safety restrictions and recorded SHA/PASS/FAIL/SKIP evidence remain intact.

# P1.5 T4+PR5 — local Codex independent integration/consumer audit

**Role:** Codex (independent checker; do not implement Claude's code). **Branch:** `integration/p15-t4-pr5-convergence-20261015`.
**Evidence pin:** inventory code `b05b36a`, GitHub Actions [38715884053](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38715884053), root audit [38716302208](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38716302208).

## Read minimum
1. `docs/refactor/work_orders/CURRENT.md`
2. `docs/refactor/architecture/consumer_inventory_findings_20261015.md`
3. `docs/refactor/architecture/architecture_gap_matrix.md`
4. Direct touched source/CI, staged source-to-target proposal and static consumer evidence. Don't reread closed T0–T4 historical reports.

## Audit sequence
1. Fetch origin and verify HEAD, merge parents T4 `ad365913` and PR5 `fe627978`, no main/source-branch changes.
2. Verify unique historic UI patch versions 264 preserved after append-only new integration entries, corresponding Markdown and sources.
3. Verify current **SHA-specific** required T4 Linux + Windows gates SUCCESS (Windows replay accounting not just job name), Scripts Linux/Windows, Reporting/API and Web build. Any pending => BLOCKED. Do not inherit prior run as current SHA result.
4. Review `inventory_p15_consumers.py` for no imported user code, no operational file reads/writes, no production environment secrets, correct relative AST imports and bounded output. Rerun 1 fixture + collect JSON from a clean detached checkout.
5. Inspect static and dynamic consumers around Commander/Strategist/Scanner/Monitor/Reporter, especially `libs/agent` compatibility classes, `graphs/nodes/execute_from_packet.py`, aliases/monkeypatch.
6. Independently verify `libs/reporting/evaluation/` inbound coupling before proposing a bulk move. Existing consumer snapshot reports 133 imported modules and 327 cross-boundary static edges, NOT runtime execution.
7. Check that `b.jsonl` and `_health.json` remain intact and are not auto-deleted. Confirm 141 public script wrappers and deployment/Windows paths remain callable.
8. Inspect UEF-7/8/9, Broker, Supervisor/Executor/Step5C CAS/UNKNOWN authority for unchanged route, launch and write permissions. Do not execute a real Broker call/LLM, trading, closeout/Drill workflow or production write.
9. Confirm T4-C missing Reporter-feedback fallback 29-variant P2 still OPEN, `REAL_REPORT_PARITY_BLOCKED`, `REAL_BRIEF_PARITY_NOT_RUN`, 16-baseline failures evidence-quality P2, cross-seed/NTFS issues not mislabeled PASS.
10. Report exact verified candidate table: KEEP, SAFE_MOVE with consumers and original/target paths, MERGE with duplicate proof, REVIEW, SAFETY_LOCK. Do not invent unused files from zero static consumers.

## Final output
- SHA, Linux/Windows CI by run id, focused contract counts, new P0/P1/P2, verified optional cleanup candidates.
- `INTEGRATION_ACCEPT_RECOMMENDED` / `REWORK` / `BLOCKED`.
- Separately `ARCH_CONVERGENCE_READY_FOR_USER_REVIEW` or `BLOCKED`. This is not the user's explicit `ARCH_CONVERGENCE_APPROVED`.
- **STOP** before moving folders/deleting scripts, main merge, T5/Wave D/P1.6.

No changes unless a factual audit correction is necessary; any corrections only in integration branch with daily patch and UI JSON/Markdown append-only updated. Successful test temp cleaned, failure evidence bounded.
