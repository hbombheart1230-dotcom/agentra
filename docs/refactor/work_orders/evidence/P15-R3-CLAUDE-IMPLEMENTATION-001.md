# P15-R3-FACADE-DECOMPOSITION-001 — Claude implementation report (compatibility-first resume)

Task baseline: `ba6618d483e6d617f4ee56b2cb5647392c777071` (`origin/refactor/p1.5`). Branch `feature/p152-facades-r3`, worktree `C:\AgentraWorktrees\p152-facades-r3`. Nothing merged into `refactor/p1.5` / `main`.
History: earlier BLOCKER commit `02bbf298` (floor analysis: Story 417 / Markdown 1024 / AI 1100) -> GPT decision: compatibility-first, façade <=350 = SIZE_DEFERRED, Owner <=350 kept.

## Pinned code SHAs (per batch)
| Batch | Code SHA | Moved bodies | New Owner files (LOC) | Façade LOC |
|---|---|---:|---|---|
| R3-A Story | `33031d526e67427514d79eb110dfc89d765256b6` | 3 | `trade_story_facade_r3_parts/bodies_01.py` (271) | 636 -> 562 |
| R3-B Markdown | `e8d0f7d5857bd3c8ecad3c271bcf06b1d7f4e175` | 25 | `trade_report/markdown_clean_r3_parts/bodies_01..05.py` (261/252/262/251/63) | 2658 -> 1891 |
| R3-C AI | `321eabb5b83a6aa4eb912cadaf6436a82214a848` | 29 | `trade_report/ai_facade_r3_parts/bodies_01..05.py` (245/252/275/228/84) | 2761 -> 1958 |

The Codex audit target is the final branch HEAD reported in chat (docs, patch notes and ZIP only after batch C; runtime code equals `321eabb5`).

## What moved and how
- Moved only bodies that were real implementations (>=20 lines; Story >=15), excluding existing thin delegations and `*_deps` wiring. Façade `def` (name, signature with defaults/annotations, decorators, docstring) stays; the body becomes `return <name>_r3_impl(args..., facade=_r3_sys.modules[__name__])`.
- Owner functions keep the original body unchanged (AST-identical) after a prelude `x = facade.x` for every former façade global that body referenced (computed with `symtable`, nested scopes included). No `__getattr__`, `exec`, `globals()`, star-import or blanket re-export; Owners import only `__future__`.
- Semantics note: globals are bound at call entry rather than lazily at each use; a façade global mutated *during* one call would differ (no such pattern found; call-time patching before the call is preserved).
- AI safety lock, NOT moved: `build_ai_trade_report`, `build_separated_ai_trade_report`, `build_trade_summary_report`, `_router_chat_with_hard_timeout`, `_build_repair_messages`, `_build_concise_trade_report_messages`, `_resolve_intraday_report_execution_profile`, `_failure_report`, `_fallback_report`, `_merge_trade_report_candidate`, `_build_skipped_separated_report`, `_trade_report_parse_meta`, `_trade_report_language_meta`, `_normalize_trade_report_output`, `_compact_story_input_for_llm`. No moved function binds router/chat/retry/timeout/prompt/attempt names.

## Verification (isolated worktree, project venv `C:\Agentra\venv`, Python 3.14.2; no live reports/ or runtime processes in the worktree)
- `python -m pytest -q -p no:cacheprovider tests/*p152*.py <42 façade-consumer test files incl. LLM/report tests> tests/test_patch_notes_sync.py` -> **810 passed, 1 skipped** (Windows symlink privilege). Production-path write banner count: 0.
- New gate `tests/test_p152_r3_moved_bodies.py` (57 symbols x checks): body AST == baseline modulo prelude; prelude == exact former-global set; owner has no unresolved global; façade wrapper keeps args/returns/decorators and injects its own module; owner reads the names from the injected object at entry; Owner <=350 and never imports a façade.
- Contract vs location split: ABI test (pinned names/signatures) unchanged and passing; symbol ledger records current `start_line/end_line/physical_loc` and `r3_owner` per symbol. No check deleted or weakened.
- Independent scripts (own AST/symtable, not repo tests): 436 baseline top-level defs, 0 ABI violations; 11 new Owner files, none >350; 0 module-level import cycles in `libs.reporting`; no Owner imports a façade; changed paths limited to `libs/reporting`, `tests`, `docs`.
- Byte parity: structural (AST identity + identical binding) plus existing synthetic golden/consumer tests. A differential before/after execution on synthetic inputs was NOT added.

## Gates NOT satisfied / NOT RUN
- Façade physical LOC <=350: **SIZE_DEFERRED** (562 / 1891 / 1958); Owners all <=350.
- Real frozen Markdown/JSON/JSONL snapshots and captured LLM prompt/retry/timeout/call-count parity: **NOT RUN** (no genuine snapshots).
- Whole native pytest: **not run / incomplete** (known API GET-only, Scanner/UEF/Step5B out-of-scope failures untouched).
- Codex independent audit, GPT/user acceptance, merge: pending. P1.5.2 OPEN; P1.5.3 NOT AUTHORIZED.

## Protection
Live `C:\Agentra` and both Q12 worktrees untouched in this resume; no orders, LLM, Docker or process restarts.
