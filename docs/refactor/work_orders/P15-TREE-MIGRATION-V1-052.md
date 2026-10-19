> **HISTORICAL WORK ORDER — NOT CURRENT AUTHORIZATION.** ACTIVE/READY/pending statuses, role assignments, branch/worktree cleanup commands, and next steps below describe the original pinned historical task only. Do **not** restart implementation or audit, create/delete branches/worktrees, or run operational checks from this page. Current authority: [D00](../../ENGINEERING_DELIVERY_POLICY.md) + [CURRENT](CURRENT.md) + [GitHub Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20). Original safety restrictions and recorded SHA/PASS/FAIL/SKIP evidence remain intact.

# P15 TREE MIGRATION V1 — 052 (IMPLEMENTATION, NOT DESIGN)

**ACTIVE WORK ORDER.** Target: `integration/p15-t4-pr5-convergence-20261015`. Expected starting HEAD: `e9a9a854c2696889da8af1f6f7ec02e936f7d924` (or fast-forward descendant containing this work order). Governing target: [HYBRID-7 V3 FROZEN](../architecture/TREE_V3_FROZEN.md).
**Operator directive 2026-10-16:** Stop re-designing or repeating AST inventories. **Make a real, safe source relocation** with mechanical identity compatibility and regression evidence.
**Owner:** Claude IMPLEMENTS → Codex INDEPENDENTLY AUDITS → GPT+user DECIDES.
**Scope:** one limited Scanner pure-helper migration, chosen because the original body has no Broker, LLM, DB or IO calls. Not permission to change scoring or rank behavior.

## Required code change — the one-module pilot

1. Inspect ONLY `libs/runtime/scanner/candidate_risk.py`, its callers and focused tests. Establish the exact BASE blob SHA, current real consumer imports, monkeypatch and dynamic loading seams; retain any uncertain path.
2. If proven safe, relocate its **implementation body byte-for-byte** to `libs/agents/scanner/candidate_risk.py`. Create only the necessary Python package markers: `libs/agents/__init__.py`, `libs/agents/scanner/__init__.py`; do not create empty directories for the other six roles.
3. Make `libs/runtime/scanner/candidate_risk.py` a **true module-object identity compatibility shim** to the one new canonical implementation (not duplicated code or imported function copies). Check old-first AND new-first imports, `is` identity, exported private/public symbols, signatures and use-time monkeypatch behavior. Retain prior public import paths and callable signatures. If an exact-object alias is impossible without breaking a consumer, **STOP/BLOCKED that move**, do not silently fall back to two owners.
4. Include a targeted contract test ensuring old/new imports refer to the same module object; frozen input cases produce exactly identical risk-score/source/components/missing-inputs outputs. Validate any relevant selected/rank-1 output fixture stays identical and no `Scanner` rank owner is added. Do not fabricate a frozen oracle.
5. No edits in `graphs/nodes/scanner_node.py`, `graphs/nodes/execute_from_packet.py`, Commander operational code, Broker, approval, Step5C, Q10/Q12, UEF, real LLM prompt/retry, deployed CLI/scheduler, or production write paths.
6. Update the existing `docs/refactor/architecture/architecture_gap_matrix.md` with **one row's actual disposition and SHA**, not a new target design. Keep remaining unproven paths blocked. Add one short day patch + BOTH UI patch notes. Do not rewrite historical design/ledger for cosmetic reasons.

## Operational and testing constraints

- Work on the **existing integration branch** via isolated clone/workspace; never edit the live `C:\Agentra` runtime, Q12 dirty worktrees, or `main`. Confirm `git status`, branch HEAD, remote HEAD before changes and before fast-forward push.
- No network calls from tests, no real Broker/LLM/trading, no writes outside unique temporary scratch roots. Success artifacts auto-cleaned; bounded failure evidence only.
- Existing focused Scanner import/signature/macro/selected-rank fixtures, old-first/new-first import identity, static/dynamic consumer scan for **just this module**, test collection, `git diff --check`, and available Linux/Windows CI all reported separately.
- `libs/agents/scanner/candidate_risk.py` MUST be a genuine only-owner, not a second ranking implementation; if test parity or module identity fails, revert this pilot and report BLOCKED; never weaken tests/guards.
- No broad folder rename, no research/evaluation move, no Inspector/Executor/Supervisor mutation, no P1.6 migration, no full-suite loop, no main PR/merge, no new dev branch.
- CI code and patch-note guards must remain operational; preserve legacy `P15_FAST_TRACK_WAVE_S_020.md` reference and the `No ZIP` CI policy while allowing changed-files-only user downloads outside CI.
- A user-facing deliverable ZIP must contain **only changed paths**, not the full repository; keep secrets, live reports/data out.
- Codex validates the *pushed* pinned SHA separately: true blob-body equality; one authoritative implementation; old/new module-object identity; monkeypatch contract; target tree/path discipline; rank semantics untouched; zero broker/production effects. Report PASS/FAIL/BLOCKED with exact evidence.

## Evidence / completion format

```
BASE_SHA:
IMPLEMENTED_SHA:
BRANCH: integration/p15-t4-pr5-convergence-20261015
SCOPE: V1-SCANNER-CANDIDATE-RISK
OLD_BODY_BLOB_SHA:
NEW_BODY_BLOB_SHA:
OLD_NEW_MODULE_IDENTITY:
DYNAMIC_AND_MONKEYPATCH_CONSUMERS:
TARGETED_TESTS:
CI_RUNS:
NO_RANK_SEMANTICS_CHANGE:
BROKER_LLM_WRITE_GUARDS:
UI_PATCH_NOTE_JSON_MD:
CHANGED_PATHS:
CHANGED_ONLY_ZIP:
CODEX_AUDIT: PENDING
NEXT: independent audit, then V2
```

No claim of completed physical relocation until code + tests are actually pushed. If source safety proof is uncertain, submit BLOCKED and the exact blocker rather than doing another wholesale design exercise.
