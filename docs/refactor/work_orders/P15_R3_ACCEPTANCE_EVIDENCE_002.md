> **HISTORICAL WORK ORDER — NOT CURRENT AUTHORIZATION.** ACTIVE/READY/pending statuses, role assignments, branch/worktree cleanup commands, and next steps below describe the original pinned historical task only. Do **not** restart implementation or audit, create/delete branches/worktrees, or run operational checks from this page. Current authority: [D00](../../ENGINEERING_DELIVERY_POLICY.md) + [CURRENT](CURRENT.md) + [GitHub Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20). Original safety restrictions and recorded SHA/PASS/FAIL/SKIP evidence remain intact.

# P15-R3-ACCEPTANCE-EVIDENCE-002 — bounded evidence follow-up

**Owner:** Claude (test/evidence work) → Codex (independent audit) → GPT/user (decision).
**Scope:** Only P1.5.2 R3 evidence, focused Reporting tests/fixtures and documentation. No runtime code refactor or rule relaxation authorized.
**Source reviewed:** `e41d42d754dba9d538fba0fa2dda969d6ea83f02`; before baseline `ba6618d483e6d617f4ee56b2cb5647392c777071`.
**Single development branch:** `refactor/p1.5` only; the existing feature commit ancestry has already been fast-forwarded there as WIP (not accepted). Do not merge to main, touch live `C:\Agentra`/Q12, call real LLM/broker, restart Docker or generate production reports. Use separate isolated clone tracking `refactor/p1.5`; do not create any feature branch.

## Mandatory branch cleanup before evidence work
Verify `origin/feature/p152-facades-r3` is ancestor of `origin/refactor/p1.5`; inspect only `C:\AgentraWorktrees\p152-facades-r3` for uncommitted AND untracked changes; remove that worktree/local feature branch without force only when clean, then delete the obsolete remote feature ref with `git push origin --delete feature/p152-facades-r3`. If the workspace is dirty or a commit is not on `refactor/p1.5`, STOP and preserve it. Never touch the two Q12 worktrees.

## Smallest ordered steps
1. **Evidence reconciliation:** capture exact Codex audit commands/log provenance (197 PASS/1 SKIP, zero writes), static/dynamic hazards, whether synthetic differential, global-binding, domain-owner naming and Story Owner LOC discrepancy were checked. Do not claim unrun checks PASS.
2. **Synthetic differential (isolated):** use identical deterministic fixtures on frozen baseline and pinned feature; compare byte-exact Markdown and JSON/JSONL when applicable, stable ordering/Unicode, schema, truth precedence; mock Reporter/LLM and record prompt/method/call/retry/fallback/timeout routing without real provider calls. Synthetic parity is separate from real-data parity.
3. **Call-time seam challenge:** test monkeypatch changes occurring before and *within* a call, nested callback and recursion; classify any behavior difference explicitly (FAIL/BLOCKED), rather than silently accepting call-entry capture.
4. **LOC/responsibility review:** reconcile Story Owner claimed 271 vs actual 102 physical lines; classify `bodies_01..05` domain-responsibility and recommend focused next slice only if necessary. Do not rename/refactor as part of evidence collection.
5. **Full native pytest one safe diagnostic run only** in isolated clone with correct venv, production-path write audit and bounded artifacts. Record exit/last test/resource failure; classify pre-existing API/Scanner/UEF/Step5B issues separately from Reporting. No blind reruns.
6. **Real-data provenance gate:** search only existing *immutable, authorized* historical pre/post files and captured LLM traces. If missing, declare **BLOCKED / NOT RUN**; never fabricate baselines, read live operational reports as goldens, or weaken test gates.
7. Write concise command/count/evidence delta; both UI patch notes must be updated for any tracked change; make changed-files-only ZIP. Codex independently audits any *new* test/evidence work.

## Stop rules
- Preserve 436 ABI, 57 moved-body semantics, no new Owner >350 LOC, no authority/LLM behavior drift or production writes.
- Any regression or unsafe behavior ⇒ stop, report exact reproduction; Claude runtime code changes need a *new expressly authorized* implementation task.
- **R3 PASS_WITH_FINDINGS is not P1.5.2 final PASS.** No main integration/live deployment/P1.5.3 until GPT/user authorizes after missing gates are characterized.
