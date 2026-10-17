# Reporter R11 checkpoints

## R11-001 — Work review follow-up: hygiene prevention, no-skip contracts, patch-note accuracy, interpreter matrix (START_SHA de99c8f0fa66bfc3e6be9a229f04fc6aad5ca06e)

ROLE: REPORTER · CHECKPOINT: R11-001 · MOVES: none (313 / 23 facade paths / 41 owners unchanged; no production file touched)
REVIEW_ACK: Issue #11 WORK_CHECKPOINT 10:16 KST (REVIEWED_SHA de99c8f) — P15-WORK-005, P15-WORK-006, "53 PASS / 3 SKIP" remark.

### P15-WORK-005 — prevention (history NOT rewritten)
- New `scripts/refactor/work_reporter_hygiene_check.py`: rejects unexpanded env-var path components (`%X%`, `$X`, `$env:`),
  OS/tool cache dirs (ProgramData, AppData, `__pycache__`, `.pytest_cache`, ...), OS/editor files (Thumbs.db, desktop.ini,
  .DS_Store, `~$*`) and binary/cache suffixes (.pyc, .db, .sqlite*, .lnk, .tmp, ...). Modes: `--staged` (pre-commit),
  `--range A..B` (every commit, added/copied/renamed paths), `--worktree` (untracked, non-ignored). The R10-002 incident is
  tolerated ONLY for commit c5d004b and its exact four paths (commit-bound allowance; the same paths in any other commit fail).
- New `tests/test_work_reporter_r11_repo_hygiene.py` (34 cases): every Reporter-lane commit eeb742a..HEAD clean; HEAD tree clean;
  incident paths absent from HEAD and exactly equal to c5d004b's flagged additions; 16 rejected variants / 5 accepted normal
  paths; end-to-end `--staged`/`--worktree` on a scratch git repo with a literal `%SystemDrive%` cache file; AST check that
  EVERY interpreter launch in every `tests/test_work_reporter_*.py` passes a non-repository `cwd` and an env built from
  `os.environ` (the incident's root cause). This check found one more launch with `cwd=ROOT`
  (`test_work_reporter_seed_migration._run`) -> changed to a temp cwd (PYTHONPATH already explicit).
- Local `.git/hooks/pre-commit` (not versioned) runs `--staged` in this clone. CI wiring is Work's (proposal below).
- Historical blobs (reachable only via c5d004b; metadata only, contents NOT inspected by this lane):
  `e7d8a95a` 16384 B cversions.2.db; `407302e2` 1240 B; `878a932c` 309072 B; `64349e87` 662488 B
  (`{GUID}.2.ver0x0000000000000001.db`). Offline confidential-data triage and any history rewrite remain an owner decision
  (Work P15-WORK-005); nothing was force-pushed.

### "53 PASS / 3 SKIP" -> no skipped cases
- `tests/test_work_reporter_r10_retained_io_contracts.py`: the 3 callable-argument readers are no longer generated into the
  generic parametrisations (previously generated, then `pytest.skip`). New `test_callback_exclusions_are_exactly_the_callable_argument_readers`
  proves the excluded set equals exactly the retained rows whose signature needs a callable, equals the hand-written fixtures,
  and that READ_ONLY + observed rows are 47 unique pairs. Result: 54 PASS / 0 SKIP (previously 53 PASS / 3 SKIP; the 3 callback
  readers still run in their 3 dedicated fixture tests, plus the new exclusion proof).

### P15-WORK-006 — proposal wording (Reporter proposal only; official note is Work's)
- `proposed_patch_note.json/.md` -> R-11: `controlled_mock_lane_report` = "retained intentionally as a Reporter presentation/read
  adapter (Work decision); no Q10/Q12 change" (was "BLOCKED"); "313 pure function bodies" -> "313 function bodies ... not all
  pure: R-8 includes READ_VIA_CALLBACK readers"; c5d004b incident disclosed. Still `proposal_NOT_PUBLISHED`.

### Python compatibility
- Explicit `tarfile.extractall(..., filter="data")` in the three Reporter tests that unpack the pinned BASE archive
  (identical behaviour on 3.12-3.14; removes the 3.12/3.13 DeprecationWarning and the 3.14 default-filter ambiguity).
  The R10/R11/seed set passes with `-W error::DeprecationWarning`.
- `test_recorded_base_cases_are_reproduced_exactly_through_both_paths` failed on 3.14 only: 22 TypeError messages are
  reworded by CPython 3.14 (`argument of type 'X' is not iterable` -> `... is not a container or iterable`) and 4 unpack
  ValueErrors gained `, got N`. Exception types and every other field are equal, and the authoritative same-interpreter
  BASE-vs-HEAD replay (`test_same_interpreter_base_archive_replay_equals_final`) passed on 3.14. Allowance is narrowed to an
  exact regex with the SAME operand type; `test_cpython_message_rewording_allowance_is_exact` rejects other types,
  exception classes and messages. The recorded-interpreter path stays byte-exact.

### TESTS (Windows 11, this session; pytest 9.1.1; temp basetemp outside repo; PYTHONDONTWRITEBYTECODE=1)
Full Reporter + P1.5.2 set = `tests/test_work_reporter_*.py` (8 files) + `tests/test_p152_*.py` (34 files):

| Interpreter | normal | `-O` |
|---|---|---|
| CPython 3.13.14 (user site pytest) | 2953 PASS / 1 SKIP / 1 FAIL* | 2953 PASS / 1 SKIP / 1 FAIL* |
| CPython 3.14.2 (isolated venv, requirements.txt) | 2952 PASS / 1 SKIP / 2 FAIL* + ** | same |

\* `tests/test_p152_integration_acceptance_inventory.py::test_offline_inventory_is_read_only_and_retains_436_abi` — NOT a
Reporter regression: reproduced in clean detached worktrees, PASS at BASE d773709, FAIL at Work activation commit eeb742a
(its `docs/refactor/work_orders/CURRENT.md` rewrite removed the `P1.5.2 OPEN` marker that `stage_frozen` requires). Shared,
Work-owned -> finding R11-F1 below. Not modified, not skipped.
\** the 3.14 message rewording above; after the fix the seed + hygiene files are 107 PASS on 3.13 and 3.14, normal and `-O`.
The SKIP is the pre-existing p152 symlink-privilege skip. Full-set numbers were taken on the pre-fix tree (only the seed test
and its helper changed afterwards; those were re-run on both interpreters).

FastAPI router tests (`tests/apps/api` + `tests/test_patch_notes_sync.py`), previously NOT_RUN:
- 3.13.14 venv (fastapi 0.143.0) and 3.14.2 venv (fastapi 0.143.3): 73 PASS / 1 SKIP (symlink) / 1 FAIL —
  `tests/apps/api/test_isolation.py::test_api_routes_are_get_only`. Identical at BASE d773709 (git archive tree, same venv).
  Cause: FastAPI 0.143 exposes included routers as `fastapi.routing._IncludedRouter` objects in `app.routes`, so the test's
  `isinstance(route, APIRoute)` filter finds 0 routes. Library-version issue, `requirements.txt` pins only `fastapi>=0.116.0`.
  apps/api is not Reporter-owned -> finding R11-F2. Reporter's API path consumer (`safe_reports.py`) tests pass.
- Linux Python 3.12 / hosted CI: NOT_RUN (no Linux or 3.12 interpreter on this machine; WSL has only docker-desktop).

### Findings for Work (shared; no shared file modified)
- **R11-F1 (P2, shared docs/T-gate):** eeb742a removed `P1.5.2 OPEN` from `docs/refactor/work_orders/CURRENT.md`; this makes
  `test_p152_integration_acceptance_inventory.py` fail on every branch descending from the activation commit (Reporter and,
  by ancestry, Monitor). Fix options: restore the marker line in CURRENT.md, or update the historical inventory's stage check.
- **R11-F2 (P2, API test/library pin):** `test_api_routes_are_get_only` fails with fastapi 0.143.x (pre-existing at BASE).
  Fix options: walk routes through included routers, or pin a FastAPI upper bound in requirements.txt.
- **CI proposal addition:** run `python scripts/refactor/work_reporter_hygiene_check.py --range <merge-base>..HEAD` (fetch-depth 0)
  and `tests/test_work_reporter_r11_repo_hygiene.py` in the Reporter job.

### STATUS
CURRENT_ROLE: REPORTER · LOCAL_STATE: REPORTER_LOCAL_READY_FOR_INTEGRATION (role PARTIAL_WITH_BLOCKERS until Work acceptance)
WAITING_ON_WORK_ID: P15-WORK-001 (shared T3), P15-WORK-005 (blob triage decision), R11-F1, R11-F2, CI wiring
NEXT_APPROVED_ROLE: Strategist READ-ONLY ownership/consumer/test design on a separate evidence branch (relay doc 10)
PATCH_NOTES: NOT_PUBLISHED (proposal only) · BUDGET: UNKNOWN
PUSHED_SHA: recorded in the next checkpoint (a file cannot contain its own commit SHA).

## R11-002 — pushed SHA, pre-audit evidence, Strategist read-only handoff (START_SHA d0a32c29)

- R11-001 PUSHED_SHA: `d0a32c29` (work/reporter-role-20261017, fast-forward from de99c8f). Post-push: hygiene + scope tests
  36 PASS at d0a32c29.
- Issue #11 polled 11:44Z: new canonical policy `11_P15_TWO_WORKER_ARCHITECT_ON_DEMAND_20261017.md` (GPT architect on
  demand; Codex builds shared T3/T4/CI candidate; Claude audits it independently). No new SHA-bound Reporter defect.
- **Codex shared integration candidate: NOT_RUN / not found.** No candidate branch exists on origin at 2026-10-17 ~12:00Z
  (latest refs: monitor 4bc42508, integration d269c906). Audit starts when Codex posts an exact SHA on Issue #14.
- **Pre-audit evidence (design proposal, run unmodified from design ea3b6c8d):** `docs/dev-team/proposals/test_reporter_facade_guard.py`
  13 cases with `AGENTRA_REVIEW_SHA=de99c8f`: checkout de99c8f -> 13 PASS normal, 13 PASS `-O` (CPython 3.13.14);
  checkout d0a32c29 -> 13 PASS normal / `-O` (3.13.14) and 13 PASS (3.14.2). `git diff 3b549d7 d0a32c29 -- libs <R4 ledger>
  <v2 ledger>` = 0 paths, so the R10 pin is valid for R11. This closes the "R10 13-case suite NOT rerun" note in the Work gate
  doc for the Reporter side; shared T3 wiring remains Codex's.
- **Strategist READ-ONLY:** branch `evidence/p15-strategist-readonly-20261017` @ `d8b34e66` (from integration d269c906; docs only):
  `docs/refactor/work_projects/evidence/strategist/{STRATEGIST_WHOLE_ROLE_ORDER_DRAFT.md, strategist_readonly_inventory.json,
  strategist_readonly_inventory.py}` — inventory byte-reproduced from a fresh `git archive d773709`. No Strategist source edits;
  implementation waits for a GPT whole-role charter.
- Local prevention: the clone-wide pre-commit hook now resolves the repository top level, so it also guards other worktrees;
  negative probe (staged `%SystemDrive%/ProgramData/c.db`) -> commit rejected, exit 1.
- Housekeeping: an earlier push of the evidence branch went out before its commit (hook failure) and briefly pointed at
  d269c906 (identical to integration); the next push fast-forwarded it to d8b34e66. No force push.

### Issue-ready text (#11 / #14; this lane has no GitHub write credential, so it is versioned here)
```
REPORTER R11 — exact SHA d0a32c29 (+ this checkpoint commit)
P15-WORK-005: prevention added (per-commit/staged/worktree hygiene checker + 34-case test; c5d004b allowed only for its
  4 exact paths; temp-cwd/os.environ AST guard on every Reporter test interpreter launch). History NOT rewritten; blob
  triage remains an owner decision.
P15-WORK-006: proposal wording fixed (controlled_mock_lane_report = retained Reporter presentation/read adapter;
  313 bodies incl. READ_VIA_CALLBACK). NOT_PUBLISHED.
R10 retained contracts: 54 PASS / 0 SKIP (was 53/3).
Full Reporter+p152 set: 3.13 2953 PASS/1 SKIP/1 FAIL normal and -O; 3.14 same after a narrow CPython-message allowance.
  The FAIL is shared R11-F1 (eeb742a CURRENT.md lost "P1.5.2 OPEN"; PASS at d773709, FAIL at eeb742a).
FastAPI tests: 73 PASS/1 SKIP/1 FAIL on fastapi 0.143 (3.13 + 3.14); FAIL pre-existing at BASE = R11-F2.
Facade guard proposal 13/13 PASS normal/-O at de99c8f and d0a32c29.
Codex integration candidate audit: NOT_RUN (no candidate SHA yet).
Strategist read-only: evidence/p15-strategist-readonly-20261017 @ d8b34e66 (draft order for GPT).
Linux Py3.12 / hosted CI: NOT_RUN.
```

### STATUS
CURRENT_ROLE: REPORTER (local frozen) -> STRATEGIST read-only (draft delivered) · LOCAL_STATE: REPORTER_LOCAL_READY_FOR_INTEGRATION
WAITING_ON: Codex shared candidate SHA (audit), GPT Strategist charter, owner decision on c5d004b blobs, R11-F1/F2 owner
NEXT_READY: (1) audit Codex candidate from a clean checkout when posted (T3/T4, R8/R10, Monitor intent-only, negatives normal/-O);
(2) on GPT charter: Strategist S-1/S-2 (triage rows + owner contract tests) on the designated branch.
TESTS: see R11-001; BUDGET: UNKNOWN. PUSHED_SHA of this checkpoint: next checkpoint / issue.
