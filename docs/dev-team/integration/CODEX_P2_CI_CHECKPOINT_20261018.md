# Codex P2 / CI checkpoint — 2026-10-18

ROLE: CODEX_DEV
BRANCH: work/codex-p15-20261018
START_SHA: 5cb90b39d00cee483be292272b893d8e8a4c6e78
CODE_SHA / EVIDENCE_SHA: recorded after commit in Issue #14; this file cannot contain its own hash.
TASK_COMPLETED: Reporter P2 narrowed; Monitor evidence serialization portability fix implemented (hosted verification pending); required CI development trigger and inherited -O added.
NEXT_READY: focused normal/-O verification, push exact SHA, observe hosted CI, request Claude AUDITOR. No integration promotion before independent PASS.
INDEPENDENT_VERDICT: NOT_RUN / NOT_SELF_APPROVED

SANDBOX_ROOT: C:/AgentraEvidence/dev-codex
ALLOWED_WRITE_WORKTREE: C:/AgentraEvidence/dev-codex only
WORKTREE_GIT_COMMON_DIR: C:/Agentra/.git
SCRATCH_ROOT: C:/AgentraEvidence/dev-codex/.agentra-worktmp (verified ignored)
PERMISSION_MODE_EFFECTIVE: host danger-full-access / approval never; self-imposed verified worktree write boundary. No claim of enforced workspace-write OS sandbox.
SCRATCH_REMOVED: pending own-successful-run summary capture
FAILURE_EVIDENCE_RETAINED: .agentra-worktmp/p2-repro/repro.xml (28 expected regression-test failures before fix)
RETENTION_MISMATCH: none observed for this session
REMOTE_BRANCH_RETIREMENT: NO
RUNNER_ACTUALLY_DEPLOYED: NO
PRODUCTION_OR_MAIN_CHANGED: NO

## Input evidence and unresolved gates

Hosted [run 39088517687](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39088517687) at exact START_SHA executed all four jobs. Linux 3.12.15 normal/optimized: each 2893 PASS / 3 FAIL / 24 SKIP. Windows 3.13.16 normal/optimized: each 2895 PASS / 1 FAIL / 24 SKIP. FastAPI 0.142.2 and 0.143.0 endpoint jobs succeeded. These observations supersede historical hosted NOT_RUN statements, without rewriting their historical evidence.

Linux-only failures: test_m007_recorded_symbol_ast_is_the_current_source_not_a_fabricated_inventory and test_retained_exclusions_are_complete_and_match_actual_sources. The recorded _to_int AST hash is 94efa63caa5101014baf53a710dfe0faace2600360d18d83ac2e8d66413c60ce; Python 3.12 empty-field dump yields 4b5cb88459010f2691d987d220b640837afe846741aabaf9a7f2df0768242d66. Local 3.14 show_empty=True reproduces the exact latter hash. Frozen inventories and inventory-producer pin remain unchanged.

UEF9 test_a_valid_current_authority: expected CONDITIONAL=7/NOT_COMPARABLE=84, actual 0/91. Prior same-environment immutable BASE d773709ba2f70471fad9badba4f92400f7818319 reproduced 19 PASS / 1 FAIL; see CODEX_SHARED_EXECUTION_20261018.json -> runs.uef9_same_env_base. This is known BASE behavior, not evidence of a new runtime regression or permission to waive the failure. New source changes are confined to test/evidence/CI; runtime and UEF files remain unchanged.

24 historical-artifact SKIP remain unresolved. Genuine real-artifact parity, whole-repository pytest and final integrated acceptance: NOT_RUN. Main frozen. No live orders, live LLM, Docker restart, production-data write or policy change.

## Focused P2 reproduction

Before fix: 28 FAIL / 4 PASS / 73 deselected. After fix: cpython selection 33 PASS / 72 deselected. Corpus inspection: 2565 fixed cases, eight too-many-unpack cases at expected=2; fixture bytes unchanged. Both directions of optional got detail accepted; malformed, opposite-direction and count-changing messages rejected.

## Current execution

Focused normal/-O and patch-note results are appended after actual completion. These are development verification results, not independent acceptance.

Normal Windows Python 3.14.2 / FastAPI 0.142.2: focused 330 PASS / 0 FAIL / 0 SKIP; paired patch-note schema/API and GET-only endpoint checks 14 PASS / 0 FAIL / 0 SKIP. Full production-path manifest audit enabled, no violation reported; both processes exit 0. Exact per-module counts and JUnit hashes: CODEX_P2_LOCAL_EXECUTION_20261018.json. Optimized execution is in progress at this checkpoint; actual final -O and hosted results will be recorded on Issue #14 for the pushed SHA. No synthetic PASS.

Modified helper/producer/runner LOC: monitor_evidence_ast.py 102; work_monitor_retained_boundary.py 57; shared_candidate_tests.py 100. New evidence tests 39 LOC; Reporter seed test file 462 LOC (test file, not a runtime Owner). Runtime Owner maximum remains 337 LOC from unchanged prior verified inventory.
