# P1.5 Documentation Inventory

Status: BASELINE INVENTORY  
Snapshot date: 2026-10-07  
Snapshot branch: `design/p1.5-p1.6-modernization`  
Snapshot head before this documentation batch: `7171736d31536d32e771f826615960cd24a70fdc`

## 1. Size

At the inventory snapshot:

| Item | Count |
|---|---:|
| files under `docs/` | 748 |
| Markdown files under `docs/` | 740 |
| top-level documentation directories | 39 |
| dated `docs/daily_patch/` entries | 137 |
| Markdown files under `docs/plan/` | 170 |
| milestone/step/phase-named Markdown files | ~207 |

The documentation surface has reached the same maintainability threshold as the large runtime modules: history, current authority, plans, experiments and operator-facing change logs coexist in the same namespace.

## 2. Current Patch-Note Authority

There are three different patch-note surfaces and they are not interchangeable.

### A. Technical audit history — canonical detailed evidence

`docs/daily_patch/`

Purpose:
- dated technical evidence
- formal freezes
- production/safety fixes
- major incidents
- research lifecycle promotions/deprecations
- major roadmap/architecture changes

Policy:
- append-only historical record
- old incident/freeze notes are not rewritten to match current architecture
- source paths used by historical evidence should remain valid where practical

### B. UI/API patch-note authority

`docs/trading_agent_patch_notes_detailed_update/patch_notes.json`  
`docs/trading_agent_patch_notes_detailed_update/patch_notes.md`

Consumers:
- `apps/api/adapters/patch_notes.py`
- `/api/v1/patch-notes`
- web Patch Notes UI

Guards:
- `tests/apps/api/test_patch_notes.py`
- `tests/test_patch_notes_sync.py`

Important:
- the JSON is the structured runtime/UI source
- the Markdown is the paired human-readable changelog
- both are append-only
- UI freshness is checked against the latest dated `docs/daily_patch/` entry

### C. Legacy phase summary

`docs/PATCH_NOTES.md`

This is not the current Patch Notes UI source. It is retained as a historical/phase summary until P1.5 documentation cleanup decides whether to archive, merge or replace it with a pointer.

## 3. Main Documentation Families

Current top-level families include:

- architecture / runtime / operations / ground_rules
- research / evaluation / offline_alpha
- daily_patch / patch-note UI source
- plan / milestones
- dev / development / execution_plan
- report_plan / report_upgrade_plan / trade_report_plan
- strategy_horizon_feedback / strategist_output / tactics
- q13 / q14 / q13_q14_validation
- refactor
- language indexes (ko/en)

Several of these overlap semantically and need an authority map before any physical moves.

## 4. Historical Milestone Names

Milestone names such as M8, M10, M13, M31 are valid historical identifiers in old design and audit records.

P1.5 naming cleanup therefore distinguishes:

- **runtime/current canonical names**: remove historical milestone naming when it no longer conveys domain meaning
- **historical documents**: keep milestone names when they describe the actual historical phase
- **indexes/navigation**: expose canonical responsibility names first, with historical milestone aliases second

This avoids falsifying history while preventing new code/docs from inheriting obsolete milestone vocabulary.

## 5. Immediate Findings

1. `docs/daily_patch/README.md` contains a manually maintained "Latest" section that stopped around May 2026 and is therefore stale.
2. `docs/PATCH_NOTES.md` can be mistaken for the UI source, but the UI actually reads the structured patch-note folder.
3. The UI patch-note path is hard-coded in `apps/api/adapters/patch_notes.py`; renaming it is a code migration, not a documentation-only move.
4. Historical patch-note entries contain repository-relative source paths, so bulk-moving old documents can break audit provenance.
5. `docs/plan/` contains a large historical milestone corpus and should not be bulk-renamed merely for cosmetic consistency.

## 6. Classification Required Before Movement

Each documentation item or family should receive one classification:

- CANONICAL_CURRENT
- CURRENT_SUPPORTING
- HISTORICAL_AUDIT
- HISTORICAL_PLAN
- SUPERSEDED
- DUPLICATE
- GENERATED/DERIVED
- COMPATIBILITY_POINTER
- CANDIDATE_DELETE

Deletion requires proof that the file is neither an audit source nor an inbound-link target.

## 7. Next Inventory Work

Before large moves:
- build inbound/outbound Markdown link map
- map code references to documentation paths
- map patch-note `sources[]` references
- identify duplicate/superseded current docs
- identify stale navigation pages
- identify documents that can be archived without breaking provenance
