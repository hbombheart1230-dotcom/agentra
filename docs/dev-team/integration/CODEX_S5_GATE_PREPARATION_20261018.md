# Codex S5 shared candidate — preparation and audited-source activation, 2026-10-18

ROLE: CODEX_DEV
BRANCH: work/codex-p15-20261018
START / INTEGRATION_SCOPE_BASE: 1e1e78a9061f9a56c3ce1410202ce5193c6af679
CODE_SHA / EVIDENCE_SHA: exact pushed SHA to be posted in Issue #14 (self-hash excluded)
REVIEWED_INPUT_SHA: candidate c4960c5312945c8dac9b141df222f54ecc28beda; developer evidence 318c952ed9838202c9de0e9a182b15d38ec0d635
INDEPENDENT_VERDICT: S5_IMPLEMENTATION PASS for c4960c53 at Issue #14 comment 6245517822. Shared/combined candidate still requires Claude AUDITOR; no self-approval. Historical preparation f78bd907 preceded this source verdict.
TASK_COMPLETED: exact four audited S5 commits selectively applied with --no-commit, source admission pin activated; prepared scope patch applied; required S5 runtime/frozen T4-C CI connected. Combined verification is recorded below.
NEXT_READY: finish combined normal/-O checks, commit/push exact joint SHA and request Claude AUDITOR. Only independently accepted changes may be proposed for separately authorized single-writer integration promotion.

SANDBOX_ROOT / ONLY_ALLOWED_WRITE_WORKTREE: C:/AgentraEvidence/dev-codex
WORKTREE_GIT_COMMON_DIR: C:/Agentra/.git
SCRATCH_ROOT: worktree/.agentra-worktmp/s5-joint-normal and s5-joint-optimized; owned artifact directory s5-prep-delivery (verified ignored)
PERMISSION_MODE_EFFECTIVE: host danger-full-access / approval never; self-bound verified worktree, not an enforced workspace-write claim
SCRATCH_REMOVED: twelve own successful roots (six preparation + six joint/fixed-CLI) removed nonrecursively after bounded XML/patch capture in s5-prep-delivery / s5-joint-delivery; exact literal paths, no force
FAILURE_EVIDENCE_RETAINED: s5-api-order-repro and s5-api-cli-before (two bounded pre-fix diagnostic groups, max7days); prior session evidence untouched
RETENTION_MISMATCH: NO for this session; prior session retained roots untouched
REMOTE_BRANCH_RETIREMENT: NO
RUNNER_ACTUALLY_DEPLOYED: NO
PRODUCTION_OR_MAIN_CHANGED: NO

## Exact five mappings

1. p164 non-moved definitions: verify each complete thin wrapper including original ABI, facade argument, and body; validate exact pinned two Owners, unqualify bodies and restore exactly eight original defs. Entire restored node equals source d269c906 AST. Other defs/statements remain exact.
2. p164 import names: add only the eight (module, name_r3_impl) pairs after the full contract passes. Alias, duplicate, missing, relative and extra imports fail.
3. p172: retain all 16 canonical object-identity checks; compare precisely restored module AST against its existing pinned BASE. Current pre-S5 node is still byte-protected by the helper.
4. Monitor/shared runtime: add only candidate node + value_helpers.py + text_fragment_helpers.py as an exact disjoint set, pinned to c4960c53, AND require ADMITTED_CODE == CANDIDATE_CODE. ADMITTED_CODE was None in preparation f78bd907, so unreviewed installation failed. It is now the exact c4960c53 pin following independent source PASS; partial/wrong-source installation still fails. Broker/Executor/Supervisor/other Strategist paths stay rejected. Future admission is exercised only with an isolated monkeypatch/in-memory source overlay in tests, never persisted.
5. S5 source branch gate: prepared S5_SCOPE_POST_AUDIT_20261018.patch replaces only its scope function with the integrated-base exact-path verifier. It was not applied at preparation. It is now applied only after source PASS to the selectively installed S5 test. Current preparation has its own real changed/staged/untracked scope check. No generic docs/ or tests/ exemption.

## Selective application — executed only after independent source PASS

Exact commits, oldest first:
- 4e48268dc0dcfca7f837c1742670d0f538134dae
- 446eb4adeb0364ac452a497823dbb458febcd812
- 21ec7fe438f48dfb7d98b5d7bded15aadd89ad8b
- c4960c5312945c8dac9b141df222f54ecc28beda

`git diff d269c906 c4960c53` contains exactly six source/test paths. A source/test-only patch first passed `git apply --check` without applying. After the independent source PASS, the explicit four commits above were applied with --no-commit (no branch merge); shared gate and paired UI evidence changes join the same candidate commit. Do not merge Claude ancestry or cherry-pick evidence 318c952e as source. Old d269c906 UI patch-note conflicts are avoided. Source pin/audit provenance must be rechecked before applying; no HEAD-based moving target.

## Results and limitations

Initial normal focused run: 194 PASS / 0 FAIL / 0 SKIP, exit 0; full production-path manifest audit clean. Includes new static virtual-candidate negatives, p164, p172, shared role guard and Monitor's protected-runtime test. Optimized and final companion checks are recorded below after completion.

This is preparation, not S5 runtime parity or integration acceptance. At preparation S5 runtime claims awaited independent review; the later exact-SHA source auditor now confirms them (see activation below). Our combined results are recorded separately. Existing UEF9 BASE failure, 24 real-artifact SKIPs, and prior CI results at 1e1e78a9 remain unchanged historical facts. New-SHA hosted CI, whole repository pytest, real data and UI build are NOT_RUN at this checkpoint. Main/integration untouched.

## Completed focused executions (developer verification only)

Windows Python 3.14.2 / pytest 9.1.1 / FastAPI 0.142.2. TEMP/TMP/TMPDIR are per-run ignored scratch; PYTHONDONTWRITEBYTECODE=1, PYTEST_DISABLE_PLUGIN_AUTOLOAD=1, PRODUCTION_WRITE_AUDIT_MODE=full. Optimized runs use python -O and inherited PYTHONOPTIMIZE=1. All runs exited 0 with no production write-audit violation.

| Execution | PASS | FAIL | SKIP | JUnit SHA256 |
| --- | ---: | ---: | ---: | --- |
| normal | 194 | 0 | 0 | 21e6d1b646802186b9be6ec287e9507f1c02f93f5f27e8a3368b1fc90fb2c933 |
| optimized | 194 | 0 | 0 | 4ffa7e9c5f03462149f1c90faaf22677601e95f050d023a2f55db95c85e652bb |
| companion_normal | 68 | 0 | 0 | af40cdc766a5274638f07ec65463ac39f4fcebaabb8bcdc5496421570bb32839 |
| companion_optimized | 68 | 0 | 0 | d50d9bceec2735b308882449d9616f48ea646ffc164991abed42cf9a9ee665bd |
| updated_negative_normal | 3 | 0 | 0 | 7717b02a1b4cab7cf2886e41e6f040a19c96b41ac0b0ad9b6107a74b520e730b |
| updated_negative_optimized | 3 | 0 | 0 | f4b5a0eee65ac3cf1421712887eee60c0799ae24945f15d76f4976cebbbaf10e |

Core command: python [-O] -m pytest -q -p no:cacheprovider tests/test_shared_strategist_contracts.py tests/test_p164_t4c_extraction_gates.py tests/test_p172_strategist_s1_057_migration.py tests/test_shared_role_contracts.py tests/test_work_monitor_role_contracts.py::test_all_retained_role_owners_and_protected_runtime_stay_byte_identical --junitxml=<owned-scratch>/result.xml.

Companion: same interpreter/options, tests/test_p159_current_owner_contract_gates.py, test_p161_t35_extraction_gates.py, test_p162_t4a_extraction_gates.py, test_p163_t4b_extraction_gates.py, test_p165_t4d_extraction_gates.py, test_patch_notes_sync.py, apps/api/test_patch_notes.py, apps/api/test_isolation.py and the new actual integrated-scope test. Core+companion have one intentional scope-test overlap; do not present their sum as unique tests. After explicitly isolating the child unreviewed-admission scenario, its three affected tests were rerun normal/-O (3 PASS each, 45 deselected).

No runtime, frozen-fixture or historical inventory change. New contract helper 150 LOC; new tests 136 LOC. Changed-files-only ZIP and final SHA-bound Issue #14 request follow after commit. New-SHA CI remains NOT_RUN at commit time; real data/full-repo/UI build and independent acceptance remain NOT_RUN. No approval is inferred from these local PASS results.

## Independent source admission — implementation PASS, integration not approved

Authoritative exact-SHA result: https://github.com/hbombheart1230-dotcom/agentra/issues/14#issuecomment-6245517822 (separate Codex Auditor session).
S5_IMPLEMENTATION_VERDICT PASS for c4960c5312945c8dac9b141df222f54ecc28beda. INTEGRATION_COMPATIBILITY FAIL / NOT_WAIVED; P1.5 overall NOT_RUN/NOT_ACCEPTED. Source PASS authorizes the user's selective developer-branch adoption condition, not integration/main promotion.

Auditor executed CRLF S5+T4-C 53 PASS normal/-O, LF S5 48 PASS normal/-O, all 19 owner mutants and four out-of-scope mutants, full State 50 records/1141 variants with zero mismatches in both modes. These are auditor results, not our claimed execution. Its evidence range correction is satisfied by the four explicit SHA list above, including S5-A.

Selective adoption preserved exact reviewed bytes (normalized only for checkout CRLF) for node, both Owners, runner and cases. S5 test differs only in the prepared branch-scope function: original pinned SRC is preserved for all BASE behavioral comparisons. No skip/xfail or expectation edits. The static helper's admission literal now points to c4960c53 with the audit URL. CI explicitly adds S5 runtime test and frozen T4-C test, not optional file discovery.

The original f78bd907 CI is historical preparation-only; do not confuse it with this later joint candidate. Whole-repository pytest, real-data parity and UI build remain NOT_RUN. UEF9 BASE failure is neither waived nor modified. Claude must independently audit this combined SHA before promotion is proposed.

## Joint developer verification after source admission

Actual Windows Python 3.14.2 / FastAPI0.142.2 joint execution: core+S5+frozen native T4-C normal **247 PASS**, inherited -O **247 PASS**; companion T3/T3.5/T4-A/B/D+UI/API+scope **68 PASS** in each mode. Full production-path audit clean; exit0 throughout. One scope test overlaps across groups. Frozen T4-C uses its original sample_mod=4 pytest replay; auditor's independent whole 50/1141 proof is separately attributed above. Do not call this new joint full-variant replay or real-data parity.

Hosted preparation f78bd907 run39095810359 actually completed all four jobs: each **3076 PASS /1 FAIL /24 SKIP /1 ERROR**. The FAIL remains known UEF9. New ERROR: tests/apps/api/test_isolation.py::test_api_routes_are_get_only lacks api_settings when CLI paths enter API, return to root tests, then re-enter API under pytest9.1. Dedicated API jobs each 9 PASS. This was introduced by our runner's new root tests between the two API files; it is a test-collection setup defect, not demonstrated S5 runtime behavior.

Reproduced locally with interleaved API/p172/API CLI: 97 PASS /1 ERROR. New configured-CLI regression failed before fix (child2 PASS/1 ERROR). Restoring the original contiguous API block preserves every test/endpoint negative; no fixture, assertion, skip or expected-value edits. The new regression now passes normal/-O, its child actually runs the API GET-only, canonical identity and scope checks (3 PASS). Both fixed regression processes exit0 with clean full write audit.

Joint normal JUnit SHA256: 13c7f5c2d3a91d287eba11384f6919411a08baf7144b44e0959723fbdbfcbccd; optimized: 3fdde5281c2750f4ca5aeb5cd4e62640d45289ef5983e7432af009c97428ad52. Bounded XML/count/hash artifacts: .agentra-worktmp/s5-joint-delivery. Failure reproduction groups s5-api-order-repro and s5-api-cli-before retained (two groups, max7days). New-SHA hosted matrix and Claude audit must confirm the complete candidate; do not carry f78 counts forward as latest results.

Latest helper LOC152; shared contract tests148; adapted S5 test306. Runtime Owners remain43/42, node4026; no new move/authority scope. All successful owned test basetemps were auto-cleaned by existing hook, remaining known XML/empty folders removed nonrecursively after evidence capture. No recursive deletion attempt or permission bypass in this session.
