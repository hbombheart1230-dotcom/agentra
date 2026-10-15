# CI transition for main (integration branch -> main)

Base: `integration/p15-t4-pr5-convergence-20261015` @ `faad5439d7a3721c815ff0ca71c8d56b845fa68f`. Goal: keep every existing verification ability while making the required regression executable on `main` pushes and on pull requests targeting `main`, so that deleting the `refactor/*` branches later does not leave the gates dead. No assertion was deleted or loosened to manufacture a PASS; branch-history-only checks are classified explicitly.

## 1. Workflow trigger matrix (after this change)

| Workflow file | push | pull_request | workflow_dispatch | Notes |
|---|---|---|---|---|
| `p15-integration-t4-regression.yml` (T4 Linux + Windows regression, T4-A..D frozen contracts, Windows smoke) | integration branch, **main** | **-> main** | yes | checkout `fetch-depth: 0`; ancestry fetch no longer names `refactor/p1.5`; concurrency per ref/PR |
| `p15-integration-crossbranch-compat.yml` (Reporting + Web + Windows LF byte contract) | integration branch, **main** | **-> main** | yes | unchanged steps |
| `p15-integration-scripts-contract.yml` (141 wrappers, Linux + Windows) | integration branch, **main** | **-> main** | yes | unchanged steps |
| `p15-integration-consumer-inventory.yml` (read-only consumer inventory) | integration branch, **main** (path filtered) | **-> main** (same path filter) | yes | unchanged steps |
| `scripts-target-tree-contract.yml` (PR #5 original) | `refactor/agentra-target-tree`, **main** (path filtered) | any base (path filtered, unchanged) | - | kept for PR #5 history |
| `p152-r2c-residual-regression.yml` (legacy P1.5 regression) | `refactor/p1.5` only | - | yes | **unchanged**; read by existing tests as a file artifact; becomes inert when `refactor/p1.5` is deleted — its job set is superseded by the integration T4 regression workflow |

The integration branch trigger is kept in all four integration workflows until final approval.

## 2. Branch-bound items found and their classification

| Item | Where | Classification / action |
|---|---|---|
| `on.push.branches` pinned to `integration/*` / `refactor/*` | 4 integration workflows, `scripts-target-tree-contract.yml` | **converted**: `main` push + `pull_request` -> `main` added; integration trigger retained |
| `git fetch --unshallow origin refactor/p1.5` (ancestry robustness) | t4 regression | **converted**: generic `git fetch --unshallow origin`; job checkout is now `fetch-depth: 0` |
| `assert "refactor/p1.5" in CURRENT.md and MAIN_FROZEN` | t4 regression, contract guard | **historical-branch-only on main**: still strictly asserted on the integration branch; on `main` push / PR-to-main it is printed as classified-not-applied. All other contract assertions (single work order link, State line, no FINAL_ACCEPTED, No ZIP, roles, patch-note sources) apply everywhere |
| CI-ZIP prohibition read only `p152-r2c-...yml` | t4 regression | **strengthened**: now scans every `.github/workflows/*.yml` |
| Pinned stage SHAs (`merge-base --is-ancestor`, `git fetch origin <sha>`) | t4 regression | **kept strict**. They hold on a merge commit into `main`. A squash or rebase merge would drop them: that case is reported as BLOCKED (see section 4), not waived |
| `tests/test_p15x_*` scope/ABI gates reading the legacy workflow path | tests | untouched; legacy workflow file stays |
| T4 stage pins (T4-A..D scope gates to stage-end SHAs) | tests | unchanged (already stage-pinned) |

## 3. Preserved verification abilities

T4-A/B/C/D AST + BASE-frozen contract replays (Linux portable oracle, Windows native accounting), owner parity/ABI/authority gates, Windows harness isolation, 141-wrapper and launcher compatibility, Reporting relocation/baseline owners incl. Windows LF byte contract, Operator UI/API patch-note sync, Web `npm test` + build, read-only consumer inventory. Real Broker/LLM/trading execution is never invoked; heavy/docker/benchmark sweeps stay manual (`workflow_dispatch`).

## 4. Local verification and what remains BLOCKED

* All six workflow files parse (YAML); the Fast Track contract guard step was executed locally in three contexts (integration push, `main` push, PR-to-main) and passes in each.
* Hosted `push` runs on the integration branch exercise the modified workflows after this commit (see the CI results in the report).
* **BLOCKED**: a hosted `pull_request -> main` run cannot be produced from this environment (no PR creation tooling/credentials; main must not be touched). It needs a Draft PR from the integration branch to `main`; until it is observed green, the PR path is *configured and locally simulated*, not hosted-verified.
* **Merge-method constraint**: pinned stage SHAs must stay ancestors of `main`; use a true merge commit (no squash/rebase) or the T4 gates will fail by design.
