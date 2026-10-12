# P15-R3-FACADE-DECOMPOSITION-001 — Claude implementation report

Task baseline / pinned code SHA: `ba6618d483e6d617f4ee56b2cb5647392c777071` (`origin/refactor/p1.5`).
Feature branch: `feature/p152-facades-r3` (isolated worktree `C:\AgentraWorktrees\p152-facades-r3`; upstream unset; nothing pushed to `refactor/p1.5` or `main`).
Outcome: **R3-A STOPPED — BLOCKER. R3-B and R3-C NOT STARTED (blocked by A, and independently infeasible).** No runtime Python was changed; code SHA == baseline. This commit is evidence/docs only.

## Why stop (exact blocker)
`tests/test_p152_facade_abi_and_authority_boundary.py` requires every one of the 436 original public names to remain a top-level `def` **in the façade file** with an AST-identical signature/returns/decorators. Therefore each façade has an unavoidable physical-line floor of (signature lines + at least one body line) per callable, before any imports.

| Façade | LOC now | `def`s | signature lines | import lines | floor: imports+sigs+1-line bodies+PEP8 blanks | absolute floor (no imports, no blanks) |
|---|---:|---:|---:|---:|---:|---:|
| `trade_story_pipeline.py` | 636 | 45 | 142 | 140 | **417** | 187 |
| `trade_report_markdown_clean.py` | 2658 | 209 | 248 | 147 | **1024** | 457 |
| `trade_report_ai.py` | 2761 | 182 | 361 | 171 | **1100** | 543 |

- Markdown and AI cannot reach <=350 even in the impossible case of zero imports and zero blank lines (457 / 543 > 350). They would require either moving the `def`s out of the façade (violates the ABI guard and patch-global semantics: function globals would become the Owner's, so patching `façade.X` stops affecting the code) or hidden dynamic exposure (`__getattr__`, `exec` into façade globals), which the work order forbids.
- Story's floor is 417 with the current import/signature formatting. Reaching 350 would need only cosmetic changes (grid-wrapping 113 imported names, collapsing multi-line signatures/calls, dropping PEP8 blank lines) which do not reduce responsibility and are LOC gaming under COMMON_RULES. Real behaviour-neutral moves available (render_* functions, `build_trade_story_input_from_bundle` body, deps-dict builders via a call-time resolver) would bring Story to roughly 450-480, still above target.
- Imported names must stay as façade globals: tests patch façade attributes (`_headline_text`, `_collect_top_headlines`, `_top_numeric_drivers`, `_derive_evidence_provenance`, `_is_present`, `_build_news_scanner_contribution_trace`, `_scanner_chart_fit_payload`) that the deps builders read at call time.

## Baseline facts recorded (no change)
- LOC 636 / 2658 / 2761; callables 45 / 209 / 182 = 436.
- Focused offline tests, project venv (`C:\Agentra\venv`, Python 3.14.2) from the isolated worktree (no live `reports/`; `data/` here is tracked eval fixtures only): `32 p152 test files + tests/test_patch_notes_sync.py` = **297 passed, 1 skipped**, 0 failures, no production-path write banner. Skip = Windows symlink privilege (same as Codex).
- Command: `python -m pytest -q -p no:cacheprovider tests/*p152*.py tests/test_patch_notes_sync.py`.
- Full-suite pytest, real-data snapshot parity and LLM parity: NOT RUN (inputs absent / out of scope; not marked PASS).

## Options for GPT/user decision (Claude does not choose)
1. Redefine the façade size gate as "no implementation bodies in façade; only signature + delegation + patch-global deps" (and record 417 / 1024 / 1100 as accepted floor), keep ABI guard. Further real moves then target body lines only (render_*, from_bundle, deps builders).
2. Amend the ABI guard to allow re-export of pure (no patchable-global) callables from Owners, accepting that `__module__`/globals identity changes; needs consumer proof for all 436.
3. Accept cosmetic compaction to hit 350 (not recommended: no responsibility reduction, E704/format churn).
4. DEFER façade size (SIZE_DEFERRED) until genuine historical report/LLM snapshots exist.

## Side effects / protection notes
- `git fetch` + `git merge --ff-only` was applied to live `C:\Agentra` (`341cedc` -> `ba6618d`; docs/tests/scripts only, no runtime source). Untracked `docs/refactor/work_orders/evidence/P15-R2-CLAUDE-FINAL-AUDIT.md` left untouched. Q12 worktrees untouched (both detached at `342060f`). No orders, LLM calls, Docker or process restarts.
- P1.5.2 remains OPEN; P1.5.3 NOT authorized.
