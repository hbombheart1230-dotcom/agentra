> **HISTORICAL WORK ORDER — NOT CURRENT AUTHORIZATION.** ACTIVE/READY/pending statuses, role assignments, branch/worktree cleanup commands, and next steps below describe the original pinned historical task only. Do **not** restart implementation or audit, create/delete branches/worktrees, or run operational checks from this page. Current authority: [D00](../../ENGINEERING_DELIVERY_POLICY.md) + [CURRENT](CURRENT.md) + [GitHub Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20). Original safety restrictions and recorded SHA/PASS/FAIL/SKIP evidence remain intact.

# Agentra P1.5 — V4-056 Scanner Pure Policy Helper Batch

**IMPLEMENTATION WORK ORDER.** V4 means fourth physical migration batch, not target-tree V4. HYBRID-7 V3 remains USER-FROZEN; do not redesign or do repository-wide inventory.
**Source base:** 6bf7112abc8facaf868916c1d4e7ba0504030b22 or the work-order publication commit descending from it.
**Branch:** integration/p15-t4-pr5-convergence-20261015 (single writable branch). Never merge main or start a new branch.
**Sequence:** Claude implement / validate / commit / push → Codex independent delta audit → GPT+user accept. No subsequent wave until audited.
**Scope acceptance:** V3 is GPT scoped-accepted at docs/refactor/evidence/P15-V3-055-GPT-SCOPED-ACCEPTANCE.md; all P2 debts retained.

## Five EXACT potential Scanner R3 helpers

For individually proven safe modules, relocate original implementation **byte-identically** under libs/agents/scanner/policy/ with a single sys.modules identity compatibility shim at the legacy path.

| Legacy path under libs/runtime/scanner/ | Canonical owner under libs/agents/scanner/policy/ | Note |
|---|---|---|
| symbol_prior.py | symbol_prior.py | Facade-injected symbol prior adjustments |
| blocker_family_overlay.py | blocker_family_overlay.py | Blocker family concentration soft overlay |
| repeat_guard.py | repeat_guard.py | Recent selection/blocker cooldown history calculation; facade.getenv and fake clocks must be scrutinized |
| guidance.py | guidance.py | Strategist guidance extraction and soft bias calculations; cross-agent contract remains unchanged |
| compatibility.py | compatibility.py | Monitor-compatible signal projection; evaluate_intraday_entry_signal and callbacks require side-effect validation |

These are **candidates**, NOT permission to bypass safety and claim 5/5. If any function writes state, calls live IO, changes Broker/monitor/trading effects, captures mutable names incorrectly, or has unsafe reflective/pickle consumers, keep only that module unmoved and label SAFETY_BLOCKED with exact evidence. No partial copying of function bodies, no changes to computation rules or call count. NamedTuple/rank owner, real selection/ranking/market representative guard and protected effect modules are OUT OF SCOPE.

## Mandatory guarded algorithm

1. Fetch branch and pinned BASE; use isolated non-operational clone/worktree with clean status; protect dirty Q12 trees. Inspect ONLY five named source modules, their true direct consumers, and their references in Wave B, T3 current Owner and frozen safety tests. Check static/dynamic import consumers, __module__/__file__/pickle/reflection and package cycles. Do not redo complete AST/inventory or V1-V3 evidence.
2. Before each move, capture BASE module Git Blob SHA and representative inputs through actual public wrappers in scanner_node or direct valid use-time facade seams. Verify injected dependencies, fake clock/env, exceptions and exact policy outputs. For repeat_guard, ensure getenv/clock/history are controlled by offline facade only. For compatibility, confirm monitor signal evaluation is a pure mock and never invokes a real monitor/broker.
3. Move entire body unchanged; old file becomes docstring plus exactly three executable statements: import sys as _sys; from libs.agents.scanner.policy import basename as _canonical; _sys.modules[__name__] = _canonical. Create policy package marker ONLY when actual owner moved. BASE source blob == new canonical blob at final commit. Test fresh interpreter old-first/new-first, from-package, private/public objects, function __module__, monkeypatch, signatures, facade late binding and exception behaviors.
4. If a test-ledger requires reading source from an old path, extend hard-coded **exact mapping** to only verified V4 owner(s) and check source-only AST exactly as existing strict Wave B verifier. No regex substring fallback, wrong canonical import or extra statement accepted even under Python -O. Do not modify old assertion families, move owner/selection authority, or relax test skip/deselect.
5. Develop deterministic BASE-vs-FINAL offline frozen comparisons per moved public wrapper/function, including abnormal inputs, object mutation/aliasing, key order, exceptions, soft bias/penalty, symbol normalization, exact Rank-1 and selected candidate. Ensure tests compare pinned actual BASE—not a regenerated fixture from FINAL. Keep fixture small and deduplicated (do not add another multi-MB generated output without a documented necessity); temp success artifacts outside repo with auto-clean and bounded failures.
6. Run Wave B 768, T3 current Owner, T4-A frozen Scanner, V1/V2/V3 focused migrations, negative AST/-O suite, patch-note sync and safety guards. Do not re-run the broad suite merely to relabel the inherited 37 failures. New failures block this batch, cannot be attributed to unverified historic provenance.
7. Ensure hosted T4 Linux/Windows, Reporting/Web/Windows-LF and Scripts Linux/Windows required workflows PASS with final SHA. If a test requires history, use adequate checkout depth, never delete/assert weaken. Report skipped jobs separately.
8. Keep these immutable: graphs/nodes/scanner_node.py, graphs/nodes/execute_from_packet.py, graphs/commander_runtime.py, libs/{execution,supervisor,risk,approval,kiwoom,llm}/, libs/runtime/commander/, Q10/Q12/UEF/Step5C/UNKNOWN, protected operational app/API/UI/config/deploy/Docker, production DB, live orders, actual LLM calls. NO ranking/selected-symbol semantic change.
9. Update CURRENT.md implementation status, append actual (not hypothetical) V4 moved/blocked dispositions to the existing gap matrix, one evidence record + daily patch, BOTH UI patch notes JSON and Markdown in their original schema. Do not change P2 V3 findings to fixed without real evidence: unknown 1-SKIP ID, 82 capture label mappings and source hash, 6.2MB fixture/one duplicate. They may be supplemented from available artifacts only; NOT a condition for structural V4 migration.
10. Push fast-forward only on the existing integration branch; no V5 work prior to Codex audit. User ZIP outside repo contains ONLY actual changed files, complete diff inventory with SHA hashes and no secrets/raw operational logs. No GitHub CI ZIP workflow. Do not force-delete an in-use scratch directory.

## Reporting format
WORK_ORDER: V4-056
BASE_SHA:
IMPLEMENTED_SHA:
FINAL_SHA:
MOVED_5_AND_BLOBS:
SAFETY_BLOCKED:
ORIGINAL_OWNER_CONSUMERS:
IMPORT_MONKEYPATCH_FACADE_SEAMS:
BASE_FROZEN_CASES:
T3_WAVE_B_-O_NEGATIVE_GATES:
SCANNER_RANK_TOP1_STATE_PARITY:
REQUIRED_CI_ALL_JOBS:
NO_PROTECTED_PATH_CHANGES:
V3_P2_DEBT_STATUS:
UI_PATCHNOTES_JSON_MD:
CHANGED_PATHS_ONLY_ZIP:
CODEX_AUDIT: PENDING
NEXT: GPT V4 acceptance decision after Codex; no main merge.
