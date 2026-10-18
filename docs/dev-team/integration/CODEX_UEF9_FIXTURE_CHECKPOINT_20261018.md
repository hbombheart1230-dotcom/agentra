# UEF9 fixture candidate — Issue16

Input branch work/codex-p15-20261018 @0c6d72d8bdd8940f9920504ca4927f688d1fb7c9.
SANDBOX_ROOT / only writable registered worktree C:/AgentraEvidence/dev-codex; ignored scratch .agentra-worktmp. Effective host danger-full-access/approval-never; operational confinement, not an OS-enforced workspace-write claim. Other worktrees untouched. Existing C:/Agentra/venv interpreter/dependencies read-only; no operational data accessed.

## Cause and repair

The old test read ROOT/reports, which is gitignored and absent from clean CI. Existing production logic correctly generates0 CONDITIONAL/91 NOT_COMPARABLE without evidence. No semantics or expected-value defect was changed.
New tests/fixtures/uef9_synthetic/reports_inputs.json contains four newly hand-authored raw artifacts (no authority result labels). Four A/+30m prospective candidate inputs create six pairs; two B/+30m historical inputs create one. The unchanged pipeline computes14 candidates,91pairs,0COMPARABLE/7CONDITIONAL/84NOT_COMPARABLE.
Package SHA2563073b0b1e8b5bcdcdc5e444b1cade06946c84c6fa50e9fc0848aec0f2f413ed0. The test-only loader pins package bytes, validates paths before writes, requires a fresh root, and verifies exact input file set/content. reports_root is explicit. Missing/corrupt inputs fail rather than falling back to ambient reports.
All existing authority, binding, digest, order/nonsemantic and prohibition assertions remain. Added12 tests cover damaged/extra/missing data, missing/modified fixture, permission denial, traversal/absolute/Windows path, preexisting root, actual production evidence dependency and fresh-process clock/hash-seed stability.

## Actual verification at implementation checkpoint

- Raw production discovery: original0/7/84 reproduced with no policy change.
- Initial Windows path validator incorrectly rejected valid names after native Path converted separators:5FAIL/7PASS/20ERROR. Corrected validator to PurePosixPath. This was an implementation defect, not waived.
- Corrected first Windows Python3.14 focused run:32PASS, exit0, full production-write audit, cacheprovider config warning. Subsequent final normal/-O, Windows3.13 and hosted exact-SHA outcomes are recorded in GitHub Issue16/18 after execution, not preclaimed here.
- Windows Python3.13.14 final UEF9 normal32PASS /-O32PASS, exit0 each; original eight test function bodies (20 expanded cases) AST-identical. Added12 negatives/determinism cases run in both modes.
- Windows Python3.14 final UEF9/shared negative scope/UI notes+API selection86PASS normal, full write audit. Previous85PASS/1FAIL came from adding the LF attribute after that process had loaded its scope set; the final fresh process passes all86. Final optimized selection and hosted clean-checkout outcomes are pending at commit time and will be reported with exact SHA.
- Original baseline failure evidence remains historical; this is synthetic contract input coverage, not replacement genuine real-artifact evidence.

## Limits / handoff

No Commander/decide static analyzer edits or probes. No trading runtime source, existing golden, UEF expectation, skip/xfail/waiver, integration/main change. CI already requires the UEF9 test file, so all new negatives execute in the existing four matrix jobs. Closed scope adds six exact authorized paths and retains unapproved policy/test-path rejection. Fixture-local .gitattributes pins only the new JSON to LF for identical Windows/Linux package bytes.
Real-data24SKIP, full-repository pytest, UI build/visual smoke remain NOT_RUN unless separately evidenced. Independent Claude review pending exact pushed SHA. No automatic integration promotion or self-approval.
Own successful scratch cleanup is bounded by evidence capture and permission; no recursive deletion or bypass. Failed pre-fix evidence retained as one bounded session group; other sessions untouched.
