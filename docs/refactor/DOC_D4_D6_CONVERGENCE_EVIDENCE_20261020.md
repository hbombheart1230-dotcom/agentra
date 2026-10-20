# P1.5 DOC D4–D6 bounded convergence — 2026-10-20

**Status: PARTIAL / EVIDENCE ONLY / DOC_FREEZE NOT ACCEPTED.** Work performed at `integration/p1.5@75a79da7a0b837a9b757896b8781d0c400e3dc90` before this documentation commit. The tree and GitHub Issue [#20](https://github.com/hbombheart1230-dotcom/agentra/issues/20) determine the live SHA and CI. This document is a **bounded D4/D5/D6 acceptance receipt**, not an alternate work-order queue or executable authorization. D0–D7 are documentation phases; DOC-A–DOC-E denote a different historic audit/remediation sequence.

## 1. Evidence actually checked

- GitHub recursive tree `a58fdfee02c770f82199657f10f87d1ecf99af56` at exact base `75a79da7`: **4,232 tree entries**, including **1,288 docs/ tracked blobs**. Git registry `DOC_REGISTRY.csv`: **339 original records / 339 paths present** in the current tree; **292 original blob SHA values unchanged, 47 changed**. A changed blob may reflect a later historical quarantine header or other update; it is **not** proof of corrupted evidence or a semantic PASS.
- Original 339 class counts: `HISTORICAL_EVIDENCE=200`, `HISTORICAL_WORK_ORDER=34`, `DATED_HISTORY=21`, `LEDGER_DATA=21`, `PINNED_ARCH_SNAPSHOT=16`, `STAGE_PACKET=14`, `HISTORICAL_PROJECT=9`, `SUPPORTING_REFERENCE=9`, `FUTURE_DESIGN=7`; other nine original class labels total eight? **Use the registry itself for full authoritative per-class counts.** No file was moved/deleted.
- Markdown relative target check on **19 explicitly selected navigation, architecture, refactor, historical and evaluation pages** yielded **86 conventional `[label](relative)` occurrences, 0 missing resolved current-tree targets**. This is a targeted, path-existence scan, not a whole-repository Markdown/HTML/Wiki/case-sensitivity/anchor/dynamic-link audit and not a semantic-content check.
- Paired Patch Notes source at base: `patch_notes.json` **entry_count=315, entries=315, unique version identifiers=315**. A current-tree-only `sources[]` check finds **14 distinct missing local repository paths cited 16 times** (as separately recorded in [historical provenance](DOC_PATCHNOTE_SOURCE_PROVENANCE_20261019.md)). **Four additional references are GitHub HTTPS URLs**, not local-path missing files: Issues #18/#19/#20 and an Actions run. Do not count those four as missing tracked paths. A true HTTP URL-availability check was not performed.
- Latest **base** `75a79da7` Actions observed at the time of assessment: Integration Scripts, Reporting/Web, T4 Regression, Reporter Regression **SUCCESS**; Shared Candidate **IN_PROGRESS**; Target Tree workflow absent among base-triggered runs. These observations are not a post-change CI claim. Prior `4c90b031` six-workflow PASS does not transfer automatically to a new SHA.

## 2. D4 canonical versus overlapping document families

| Family / live ambiguity | Canonical **current** responsibility | Safe disposition at this batch | Acceptance gap |
|---|---|---|---|
| Engineering loop: `docs/dev/workflow.md`, `docs/dev/codex_rules.md`, `docs/development/*` | **D00** `docs/ENGINEERING_DELIVERY_POLICY.md`; **D01** `AGENTS.md`; **D02** `CLAUDE.md` | Old `docs/dev/workflow.md` marked historical; `docs/development/evidence_index.md` remains evidence provenance | All old inline references/other developer guides not fully content-classified |
| P1.5 program and dated orders | `docs/refactor/README.md` for navigation, `docs/refactor/work_orders/CURRENT.md` -> **Issue #20** for live state; frozen `TREE_V3_FROZEN.md` for target | Keep all original `work_orders/` and `work_projects/` at path; no reenabling old sessions | Cross-reader review of all imperative legacy clauses pending |
| Patch Notes: `docs/PATCH_NOTES.md`, `docs/daily_patch/`, UI JSON/MD | **UI/API**: `trading_agent_patch_notes_detailed_update/patch_notes.json` with paired `patch_notes.md`; technical history: `daily_patch/` | Label old `docs/PATCH_NOTES.md` as historical phase narrative; preserve original content | Full generated/legacy citation resolver and automated validators pending |
| Q9-era evaluation `docs/evaluation/README.md` and UEF research | Frozen UEF authority: `docs/research/` and its explicit UEF freeze records; historic Q-program-specific scopes remain in `docs/evaluation/` | Add dated historical-status clarification without rewriting evaluation proof | Current Q-family overlap, program-specific exceptions require domain review |
| Current role overview vs V2 design and frozen V3 | `docs/ground_rules/AGENT_RULES.md` safety; `docs/refactor/architecture/TREE_V3_FROZEN.md` target; `docs/architecture/architecture.md` supporting overview | `architecture_v2.md` already says DESIGN ONLY; no attempt to replace frozen owner tree | Latest role callable/source parity still P1.5 release gate |
| `report_plan/`, `report_upgrade_plan/`, `trade_report_plan/`, `execution_plan/` | No unambiguous single per-file current owner established by this pass; D00 authority controls any new assignments | **DEFER / KEEP_AT_PATH** rather than invent a replacement canonical doc | Whole-family inbound/code consumers and semantic owner matrix missing |
| `docs/plan/`, retired milestone/runbooks | Historical milestone truth with current navigation through `docs/00_HOME.md` | **KEEP_AT_PATH**; no historical body rewriting | Source-specific retirement coverage and every inbound reference not fully proved |

**Authority discipline:** this table assigns the **current decision/navigation precedence**, not ownership of every historical fact. An unchanged historical document can remain valuable even where its work instructions are inert. D00/D01/D02 and trading safety rules are not replaced by this receipt.

## 3. D5 conservative reference-safe disposition

- **All 339 original registry paths remain `KEEP_AT_PATH`**; **no files relocated or deleted**. This is a positive preservation decision, not completion of every `inbound_refs` field.
- Current `DOC_REGISTRY.csv` still truthfully records `content_check=PROVEN_FOR_ENTRYPOINTS_ELSE_NOT_VERIFIED` and `inbound_refs=NOT_FULLY_CHECKED` for all 339. Do **not** mass-change these labels after a path-only test.
- Preserve all historical `sources[]` verbatim. Of 14 known absent local paths, historic secrets, logs and untracked/generated evidence are **UNAVAILABLE**; do not read secrets, synthesize logs, or fabricate UEF outputs. Five flat legacy docs and `libs/event_logger.py` remain exact-revision provenance candidates, not automatic redirects.
- A safe physical archive requires proof of **incoming Markdown/Wiki/HTML links, Python imports/path literals, workflow/CI usages and UI sources** on the exact modified SHA, followed by independently reviewed pointers. Nothing qualifies for an automatic mass move in this batch.

## 4. D6 narrow quality-gate receipt

**Completed read-only checks:** exact Git tree versus 339 registry paths/blob ids; selected 19-page Markdown relative target existence (86/86); paired JSON declared/actual/unique version count (315/315/315) at base; classification of 14/16 missing tracked local sources versus four external URLs. These are *not* newly added CI gates.

**Not completed:** full 339-file semantic authority and inbound census; case-sensitive/anchor-aware Markdown and HTML/Wiki backlinks; embedded code-reference/path check across whole repository; full patchnote schema/date/provenance validator; new-commit hosted matrix; fresh peer reviewer receipt; real operator-host `claude -p` ↔ `codex exec` test. Do not convert NOT_RUN to PASS or weaken historic CI/UEF/Step5C golden assertions to show green.

## 5. D7 operator decision boundary

**Decision: DOC_FREEZE HOLD.** Remaining signoff blockers: (1) source-specific/representative risk-class **content and inbound review**, with a documented acceptance/defer matrix rather than 339 invented checkmarks; (2) unresolved report-plan/Q-family canonical ownership and exact references as material; (3) latest SHA CI and independently reviewed D00/D01/D02+this batch; (4) operator explicit freeze SHA/exceptions acceptance. The DOC_FREEZE gate is distinct from later P1.5 code release gates and is **not** authorization for local developer CLI launch, worktree creation, main promotion or real trading.

**Other release risks kept visible:** `main` GitHub branch read back as `protected:false`, although D00 policy forbids unapproved main modification; the 24 real-data test SKIPs are not production parity. Runtime/approval/guard code, production data and developer CLI were not touched in this documentation batch.
