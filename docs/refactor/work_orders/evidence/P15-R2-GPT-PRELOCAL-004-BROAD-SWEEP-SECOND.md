# P1.5.2 Remote Prelocal Broad Test Sweep — second Linux pass/fail inventory

Date 2026-10-10
Branch refactor/p1.5
Code SHA `9303aacd19a7cab6ac49916901b1ff6607805d36`
GitHub Actions https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38035913347

## Actual outcomes
- Focused Reporting/Owner/UI integration job: **SUCCESS** (709 previously accepted selected tests and 3 new conservative consumer tests).
- Separate repo-wide Linux `pytest -q tests -m "not heavy and not docker and not benchmark" --maxfail=25`: **4,607 PASSED / 25 FAILED / 25 SKIPPED / 9 DESELECTED**, stopped at maximum 25 failures after ~203 seconds.
- Isolated API route check independently FAILED: FastAPI app produced zero objects recognized by test's `fastapi.routing.APIRoute` on hosted Linux.
- JUnit: https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38035913347/artifacts/11664172537
- Previous first sweep `38035524693`: 2,114 PASS / 12 FAIL after maxfail 12 under inherited `DRY_RUN=1` and missing history. Those harness-induced mock-LLM and missing-AST cases are ABSENT from the second sweep.

## Second-sweep failure buckets
1. Linux path / Windows strict lock expectations / API route: 7 (API 1, closeout lock 3, archive absolute Windows path 1, Operator UI Windows path 1, runtime path 1).
2. Scanner rank plumbing: 1. Test and `graphs/nodes/scanner_node.py` and `libs/runtime/opening_rank1_controlled_probe.py` blob-identical to before-P1.5.2 source SHA `2fb4b8fcbaa68c34e80fbdbeb8e009c66d0cbc7c`. Still a real FAILED test; not waived.
3. Step5B recovery tests expecting simulated RealExecutor calls: 8; execution remained DISABLED in hosted mock CI. Never enable real orders merely to clear CI.
4. UEF-2A real historical contract fixture files absent from ephemeral GitHub checkout: 8; **NOT evidence of local UEF failure/pass**.
5. UEF5 clean-evidence registry has an assertion failure due observed UEF6 validation replay module import: 1. Source/test existed pre-P1.5.2; freeze preserved, do not alter UEF core without separate authorization.

## Proven source identity and interpretation limits
- Source and test blobs checked for API main/isolation, closeout lock/test, market-data receipts/test, Operator UI data/test, two LLM test files, strategist node/test, Scanner node/opening probe/test, Step5B tests, UEF5 test/replay: identical in pinned before and current refactor branch. This is direct Git blob identity only, not proof that all cross-module runtime interactions are equal.
- Do not classify all failures as expected or pre-existing behavior without pinned old-suite execution. No source modifications to these safety/authority modules.
- Full Windows native suite, local real output/prompt parity and two independent auditors remain NOT RUN. **P1.5.2 OPEN.**
- Next broadened Linux sweep runs without `--maxfail` to inventory all eligible tests; this is still NOT the entire local repository suite.
