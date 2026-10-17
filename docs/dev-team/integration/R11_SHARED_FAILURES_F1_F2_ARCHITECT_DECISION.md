# GPT Architect R11 Shared-Failure Decision — F1 stage provenance, F2 FastAPI route isolation

**Date:** 2026-10-17 KST. **Decision owner:** GPT (ordinary ChatGPT on demand), no recurring Work.
**Evidence:** Reporter `443f90362ad5970a4731685311a45e8e0f6b55e4` (`R11_CHECKPOINTS.md`); Reporter initial R11 `d0a32c29`. Strategist evidence `d8b34e669e1c43342eadd80b13ea43aac4bc255b`. Monitor last known `4bc4250844093050438d8a9c29f5842991ad1c3a`; re-fetch before integration. 
**Change owner:** Codex isolated *shared integration candidate*, after Monitor local-safe stage, NOT Reporter or Monitor active branch. **Independent reviewer:** Claude. **Architect:** GPT on demand.
**Current status:** Scope approved for *shared doc/test repairs*, fixes NOT IMPLEMENTED here, test execution NOT_RUN by this architecture turn, `main` unchanged.

## Decision F1 — the existing inventory pin should not block all downstream role branches

**Observed source:** `scripts/refactor/p152_integration_acceptance.py` checks:
`stage_frozen = "P1.5.2 OPEN" in current and "P1.5.3" in current`
and the downstream offline inventory test expects `source_inventory.all_source_checks_pass`. Original BASE `d773709` contained an explicit **historical stage marker**; later activation `eeb742a33b16f6271ff364a904e187b470561c7e` rewrote `docs/refactor/work_orders/CURRENT.md` without those two legacy substrings. Reporter observed a reproducible FAIL, not a Reporter facade/owner semantic regression.

**Approved narrow fix choice:**
1. On integration candidate, **append a clearly labeled historical stage-state paragraph** to `docs/refactor/work_orders/CURRENT.md` containing **both** `P1.5.2 OPEN` and `P1.5.3`. Explain this is pinned acceptance provenance, not a current ACTIVE work order. Preserve current whole-role activation section and stop-state wording; never revert to the outdated active instruction.
2. Keep `tests/test_p152_integration_acceptance_inventory.py` and `scripts/refactor/p152_integration_acceptance.py` original historical guard unchanged during the first attempt. Check BASE/current outputs/immutable 436 ABI and 37 owners. Do not remove `stage_frozen` or hardcode true.
3. Negative test: remove or mutate either historical string in a temporary candidate copy and verify source inventory fails; then restore both and demonstrate the original failing `test_offline_inventory_is_read_only_and_retains_436_abi` becomes green. All existing frozen/current stages must remain documented truthfully.
4. If `CURRENT.md` is shared in more than one branch/owner, apply only to the isolated integration candidate with exact SHAs and record any conflict. Never edit Claude's Reporter branch to hide the historical failing test.

**Fallback:** If a truthful historical paragraph alone is insufficient, produce precise evidence before requesting approval for a minimal change to stage provenance parsing. Do NOT rewrite pinned historical test semantics just to reach green.

## Decision F2 — FastAPI >=0.143 included-router API test must remain fail-closed

**Observed source:** `tests/apps/api/test_isolation.py::test_api_routes_are_get_only` currently uses:
`routes = [route for route in app.routes if isinstance(route, APIRoute)]`
and asserts `routes` and exact methods `{"GET"}`. Reporter independently observed 73 PASS/1 SKIP/1 FAIL in Windows Python 3.13/3.14 with fastapi 0.143.x; same failure at pinned BASE. The installed version reportedly wraps included routers in `_IncludedRouter`. This is **test introspection compatibility**, not proof a non-GET endpoint exists or proof all endpoints are GET.

**Approved repair choice:** adapt the **test**, not `apps/api/main.py` and not a broad version cap in `requirements.txt` by default.

1. Determine actual `app.routes`, `app.router.routes` and included-router shapes at the failing FastAPI version via controlled offline inspection. Then enumerate the ACTUAL complete application endpoint set with public supported router metadata where possible; if a wrapper is encountered, recurse only through explicitly verified router `routes` members, preserving a cycle/duplicate guard.
2. Keep fail-closed semantics: require nonempty discovered endpoint set, compare to actual mounted GET endpoint paths; **verify every active endpoint allows only GET** (never silently ignore `_IncludedRouter`, generic `Route` or mounted sub-router POST endpoints). If a route type or method set is unrecognized, FAIL with diagnostic path/type rather than drop it.
3. Add a regression **negative fixture**: introduce a synthetic POST/PUT endpoint in an isolated test app/router and prove the checker FAILS, while normal read-only API routes PASS for the installed library versions supported by requirements. Include no real HTTP network/broker access.
4. Test same candidate with FastAPI 0.143.x and, if available, older supported version; avoid global dependency pin/downgrade unless the public introspection mechanism truly cannot support the currently required dependency range. A dependency pin is an explicit alternative decision, not an undocumented quick fix.
5. Do not alter production routes, route permissions, CORS, auth or read-only API behavior to get tests green.

**Acceptance:** original failing API isolation test now PASS, deliberate POST mutation FAIL, actual GET-only API invariant maintained and no side effects; record exact package version, command, exit and candidate SHA. Existing historical BASE failure remains documented as such, not labeled a new Reporter regression.

## R11 evidence and other non-blockers

- `P15-WORK-005`: Reporter R11 adds a staged/worktree/per-commit path hygiene checker and 34 negative tests; the four binary cache blobs introduced in historical `c5d004b` are absent from Reporter HEAD but present in Git reachable history. DO NOT force-rewrite repository history without owner authorization. Before deciding remediation, authorized offline owner should inspect for personal/secrets/credentials and check for forks/tags/other remote references. The current metadata says caches, but contents were not independently cleared.
- `P15-WORK-006`: Reporter R11 proposed patch-note wording corrected; proposals are NOT the UI publication. When shared integration candidate reaches a verified milestone, Codex updates actual `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` + paired human text and sync tests. UI patch note must not assert any P1.5 whole-role final acceptance or `313 pure` misleading label.
- `P15-WORK-004`: Reporter frozen-clock and populated success/negative checks were reported repaired. Reporter R11 independently reran proposed exact facade guard 13/13 in normal/`-O` on R10/R11; integrate guarded test into shared required CI, and Claude re-audits candidate. These are developer-reported until separately run by another actor.
- Python 3.14 message rewording allowance is narrow but R11 full suite was NOT rerun after fix; combined integration must execute full relevant tests on supported platform. Linux Python3.12/hosted CI NOT_RUN.

## Scheduling / ownership

1. Codex finishes true Monitor-local M9 items. On isolated integration candidate address **critical shared P1 T3/T4 first**, then F1 and F2 plus CI/UI. Do not abandon P1 strict mutation gate for low-priority doc failures.
2. Claude independently reviews Codex candidate at its exact SHA, including above F1 historical markers and F2 POST negative. Claude fixes Reporter-owned source only.
3. GPT does not block each normal batch. Escalate only architecture/scope/authority conflicts and final main merge to the user.
4. No periodic Work automation or cross-session claim of execution. No code was modified by this design decision; Codex must implement/test.

**Provenance links:** Issue #11 for Reporter, Issue #12 Monitor, Issue #14 shared integration. `main` merge forbidden.
