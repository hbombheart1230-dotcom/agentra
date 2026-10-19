> **HISTORICAL WORK ORDER — NOT CURRENT AUTHORIZATION.** ACTIVE/READY/pending statuses, role assignments, branch/worktree cleanup commands, and next steps below describe the original pinned historical task only. Do **not** restart implementation or audit, create/delete branches/worktrees, or run operational checks from this page. Current authority: [D00](../../ENGINEERING_DELIVERY_POLICY.md) + [CURRENT](CURRENT.md) + [GitHub Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20). Original safety restrictions and recorded SHA/PASS/FAIL/SKIP evidence remain intact.

# P15 HYBRID-7 V3 — V3-055 Scanner Read-Only Projection Migration

**ONE ACTIVE IMPLEMENTATION ORDER.** This is code migration, NOT architecture planning. Do not redraw target trees or repeat repository-wide AST inventories.
**Current starting SHA:** 4c6cddedcfab910181e2fa8a9f7642b628f4f164, or this work-order publication commit descending from it.
**Branch:** integration/p15-t4-pr5-convergence-20261015 only. No new branch, main merge, deployment, live Broker/LLM calls or production writes.
**Decision:** V2 accepted structurally WITH findings. Read docs/refactor/evidence/P15-V2-053-054-GPT-SCOPED-ACCEPTANCE.md; historical broad-run origin remains BLOCKED and the 37 observed failures are not fixed.
**Roles:** Claude implements in isolated clone; Codex independently audits pushed pinned-SHA delta; GPT/user final acceptance.

## Fixed V3-055 real relocation candidates — exact five

Move implementation bodies byte-for-byte to libs/agents/scanner/projections/ only after targeted consumer and behavior proof:

| Old path under libs/runtime/scanner/ | Canonical new path under libs/agents/scanner/projections/ | Expected owner |
|---|---|---|
| candidate_context_projection.py | candidate_context_projection.py | Candidate source/context/policy projection |
| control_eligibility.py | control_eligibility.py | Observation-only control eligibility |
| output_payloads.py | output_payloads.py | Candidate ranking/selection reason payload projection |
| output_snapshots.py | output_snapshots.py | Candidate/feature/ranking snapshot read model |
| selection_evidence_projection.py | selection_evidence_projection.py | Selection evidence and reasons projection |

These are **candidates**, not permission to force 5/5 success. Keep other modules including selection_output_projection.py (NamedTuple), score_feature_projection.py, score_policy_projection.py, theme_filter.py, practical_filters.py, candidate_risk.py and the V2 context/ modules unchanged. Never add six decorative empty role packages.

## Explicit implementation algorithm

1. Before touching files, verify origin branch/head, worktree status, exact five old-path blobs and **only their real callers**, frozen test references, Wave B ownership ledger entries, dynamic references, import/monkeypatch and pickle/serialization/relative import seams. Check circular imports and mutation of input arguments. Do not rerun the earlier full 2,226-file inventory.
2. For each safe candidate: Git-move its implementation body without edits; compare old(BASE) vs new(FINAL) Git Blob SHA. Keep original import path as a three-statement sys.modules identity shim with one canonical owner. Check fresh-process import old-first/new-first, package attribute, private/public function object identity, monkeypatch visibility, callable signatures and exception identity. No star-import copy or duplicated implementation.
3. Preserve exact output fields/order, snapshot bytes, candidate ranking table payloads and projection provenance. No behavior/score/rank/top1/selected symbol or State-mutation changes. Confirm no new events, logging, file writes or broker/LLM calls. If __module__, __file__, pickle ABI, external CLI, package cycles or dynamic consumer makes identity insufficient, **SAFETY_BLOCKED** only that module with exact evidence; do not patch operational code to hide it.
4. Create deterministic pinned-BASE offline inputs for real public/caller functions of each moved owner (including empty/malformed values, dictionaries and errors), replay on FINAL for exact outcomes, exception names, JSON key order and bytes. Do not fabricate BASE results after moving files. Scanner T4-A rank and selected symbol oracle must pass unchanged.
5. Critical Wave B: tests/test_p154_wave_b_moved_bodies.py now uses a **fail-closed versioned AST allowlist** for V2 moved owner paths. Inspect Wave B ledger for these new five; if any selected old owner is referenced, explicitly extend the hard-coded mapping by the exact approved old/new pair(s), retain AST exact shape and add wrong-target/extra-statement/-O negative checks. Do not permit arbitrary import targets; do not remove old assertions or relax 768 cases.
6. Run focused V1-052/V2-053 and V2-054 contract suites, strict negative suite normal AND python -O, Wave B 768, T4-A rank, relevant output/snapshot/projection tests, API patch-note sync and write-isolation tests. No broad suite rerun unless a new code regression specifically warrants it; the 37 reported failures are managed as distinct debt. No test deselect or threshold weakening.
7. Keep all frozen operational paths unchanged: graphs/nodes/scanner_node.py, graphs/nodes/execute_from_packet.py, graphs/commander_runtime.py; libs/{execution,supervisor,risk,approval,kiwoom,llm}/; libs/runtime/commander/; Scanner actual ranking/selection; Step5C CAS, UEF, UNKNOWN, Q10/Q12, scheduler, Docker, live DB, apps/, config/, deploy/. Never place real orders, restart containers or write production artifacts.
8. Commit only on existing integration branch from non-operational isolated clone. Confirm remote fast-forward and original Q12 dirty worktrees preservation. Update CURRENT status, existing gap matrix with only V3 actual moved/blocked rows, one concise evidence and daily patch, and BOTH UI-connected JSON/Markdown patch notes. Existing patch note JSON entry_count must equal len(entries). No ZIP workflow in CI; user delivery is ZIP with **only actually modified/created paths**, outside the repo. Session scratch successes auto-clean; bounded failures only, report denied deletions without force.
9. Ensure the required hosted CI workflows on the pushed FINAL SHA include new focused V3 tests where appropriate and complete required Windows/Linux jobs. If a CI failure or source ambiguity arises, stop and report the exact gate; do not advance to V4. The module move remains IMPLEMENTED/PENDING_CODEX_AUDIT until independent Codex verdict.

## Required final report
BASE_SHA:
IMPLEMENTED_SHA:
FINAL_SHA:
BRANCH:
ATTEMPTED_5:
MOVED:
SAFETY_BLOCKED_AND_REASONS:
OLD_NEW_GIT_BLOB_PARITY:
MODULE_IDENTITY_AND_PATCH_SEAMS:
BASE_FROZEN_PROJECTION_CASES:
RANK_TOP1_PARITY:
WAVE_B_768_AND_-O_NEGATIVES:
HOSTED_CI_REQUIRED_JOBS:
BROKER_LLM_WRITE_GUARDS:
UI_PATCHNOTES_SYNC:
CHANGED_FILES_ONLY_ZIP:
CODEX_AUDIT: PENDING
NEXT: pinned-SHA Codex delta audit; no V4 or main merge.
