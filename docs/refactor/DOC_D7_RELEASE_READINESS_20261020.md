# Agentra P1.5 — D7 documentation-freeze decision packet (2026-10-20)

**State: REVIEW_READY / NOT_ACCEPTED.** This packet is a decision aid only; it is not DOC_FREEZE approval, code-development authorization, a CLI launch, or a broker operation. The authoritative live SHA and check results are tracked in [Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20). The pre-remediation baseline inspected here is `integration/p1.5@974eb9d1bd1155091282cac02162735ebaa589a0`.

## D0–D7 disposition

| Phase | Verified outcome | Decision / residual gap |
|---|---|---|
| D0 original inventory | 339 original `docs/refactor/` registry paths preserved in the 2026-10-20 pre-remediation tree; original versions frozen in `DOC_REGISTRY.csv` | KEEP_AT_PATH; not a 339-file semantic PASS |
| D1 navigation | `docs/00_HOME.md` -> `docs/refactor/README.md`, D00/D01/D02, Issue #20, frozen HYBRID-7 V3 target | Canonical P1.5 entry is findable; no replacement of dated source truth |
| D2 UI provenance | JSON/MD paired, pre-change **317/317** versions/titles unique; UI adapter reads canonical JSON at its original path | This batch strengthens two pre-existing CI inline guards; standalone append helper is still deferred as a source-development task |
| D3 historical documents | Original milestone, work orders and project sources quarantined/inert | No rename, deletion, invented evidence or archival moves |
| D4 current-vs-legacy authority | D00 + D01/D02 direct reciprocal CLI review; Issue #20 active state; 35 high-priority registry pages + 17 cross-domain pages read; 14 high-risk ambiguity banners, old bodies retained | Family-specific report/Q/architecture historical details remain and must not automatically override current owners |
| D5 reference-safe archive | Conservatively **zero moves/deletes**; 339 original paths remain | Full repo-wide inbound link/call graph not certified. No source-path migration needing link rewrites was performed |
| D6 quality | Base `974eb9d1` had **5/5 observed workflows SUCCESS**; two existing workflow inline guards upgraded to fail on *new* missing `sources[]`, duplicate versions/titles, missing direct cross-CLI policy | New commit CI and final independent review must be pinned; full global Markdown/HTML/Wiki backlink sweep not performed |
| D7 decision | **REVIEW_READY**, not freeze accepted | Requires independent doc review receipt, new SHA-matched CI, and explicit user acceptance of bounded historical exceptions |

## Machine-checkable source validation — prechange snapshot

- `patch_notes.json`: `entry_count=317`, 317 actual entries, **317 distinct versions and 317 distinct titles**.
- All entries together: **1,017 `sources[]` occurrences**: 997 paths presently found in the tracked Git tree (including tracked directory prefixes), 16 references to **14 distinct absent historical local paths**, and four exact GitHub HTTPS links. No newly unclassified missing local path was identified.
- The 14 absent path values and their dispositions are *not fabricated*: see [2026-10-19 provenance](DOC_PATCHNOTE_SOURCE_PROVENANCE_20261019.md). Includes secrets (`deploy/compose/.env`), runtime logs, generated reports, five historic flat docs, and `libs/event_logger.py`. Values are intentionally not rewritten in old UI rows. The manifest-style inline CI allowlist blocks any 15th new missing local path. It additionally asserts **exactly 16** historical missing-reference occurrences and **exactly 14** distinct allowed paths, so drift is not silently ignored.
- `tests/test_patch_notes_sync.py` already checks entry structure and date freshness vs `docs/daily_patch/`, and `tests/apps/api/test_patch_notes.py` checks read-only `/api/v1/patch-notes` behavior. Existing CI maintains those tests. The changed inline workflow checks are **additional**, not replacements.
- Only ".github/workflows/p15-integration-t4-regression.yml" and "p152-r2c-residual-regression.yml" documentation-guard *segments* were changed; their runtime/UEF/broker regressions, test suites, skip semantics and workflow branch conditions are retained. A side effect is that previously stale `No live developer implementation issue` exact-string requirement is replaced by a live Issue #20/DOC_FREEZE contract check; absence of `FINAL_ACCEPTED` remains a distinct source-release gate until formal release acceptance.

## Safety and review boundaries

- No live trading, broker credentials, permission, order, safety Step5C, UEF oracle or production-write code changed. `main` remains untouched. The `main` branch was found not technically protected; enabling branch protection is a **separate operator-admin action** before any production promotion.
- Local `claude -p` / `codex exec` cross-review on the operator's Windows PC is **NOT_RUN**. It is not validated by this GitHub documentary CI. No reviewer PASS is inferred.
- An independent **read-only** reviewer should check just the final `974eb9d1..FINAL_SHA` delta, including two altered YAML inline assertions, 14-path provenance exception list, D00/D01/D02 nonrecursive peer-review invariant, and the paired UI summary. It must return `PASS / REWORK / BLOCKED` with exact SHA and evidence. It must not start a developer batch or modify files.
- If latest hosted CI or this independent review finds a failure, **REWORK on integration, no DOC_FREEZE acceptance**. An unreviewed workflow refactor is not certified by the previous 5/5.

## Exact bounded operator decision

**Pending operator signoff:** Accept this *documentation-only* freeze at the eventually reported new integration SHA, retaining (a) 14/16 unavailable historical `sources[]` exceptions, (b) unverified inbound-only references for original 339 docs because none was moved or deleted, (c) unrun local CLI reciprocal smoke until developers are launched, and (d) deferred nonessential patchnote helper work. This decision **does not** approve P1.5 source release, all-seven public callable interfaces, Docker/Windows/production JSON/HTML parity, 24 real-data SKIPs, protected-main promotion, or live broker trading.

**No unilateral D7 flip:** until an independent reviewer receipt, new commit CI and the operator's explicit acceptance are recorded, status stays `DOC_FREEZE_HOLD` and the two primary developers do not start new source batches or worktrees. The next concrete action after PASS is to offer the operator one consolidated exact-SHA D7 acceptance, then launch the pre-agreed two developer lanes without another broad document audit.