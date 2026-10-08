# P1.5 Documentation Refactor Plan

Status: DESIGN AUTHORITY  
Date: 2026-10-07

## 1. Goal

Refactor Agentra documentation so that a reader can distinguish:

1. what is authoritative **now**
2. what is supporting design/reference material
3. what is immutable historical evidence

without rewriting history or breaking patch-note provenance.

This is part of P1.5 and follows the same behavior-preserving philosophy as the code refactor.

## 2. Non-goals

Documentation refactoring must not:
- rewrite historical incidents to match current understanding
- erase milestone/protocol names from historical records
- move files without checking inbound links and patch-note source references
- change runtime behavior merely to make documentation prettier
- rename the UI patch-note source path without an explicit adapter/code migration
- collapse technical audit evidence into short human-facing release notes

## 3. Target Documentation Model

```text
docs/
  00_HOME.md                 canonical navigation
  architecture/              current architecture authority
  ground_rules/              non-negotiable authority/rules
  runtime/                   current runtime behavior
  operations/                current operational/runbook authority
  evaluation/                current evaluation contracts
  research/                  research/UEF/evidence authority
  refactor/                  P1.5/P1.6 design authority

  daily_patch/               immutable technical change/audit history
  trading_agent_patch_notes_detailed_update/
                             UI/API changelog authority; path preserved during P1.5

  archive/                   only for safely movable superseded material
  plan/ and other legacy dirs
                             remain in place until reference-safe migration
```

The target is an authority model first, not immediate folder movement.

## 4. Four P1.5 Tracks

P1.5 now has four coordinated tracks:

```text
A. Architecture
N. Naming
T. Tests
D. Documentation
```

Every subsystem batch should update its canonical documentation and patch-note references together with code and tests.

## 5. Documentation Phases

### D0 — Inventory and authority map

- count/document current surface
- map patch-note authorities
- identify stale indexes
- identify milestone-heavy historical areas
- no bulk movement

Status: STARTED.

### D1 — Navigation and canonical-current map

- update `docs/00_HOME.md`
- create/refresh canonical owner indexes
- clearly label current vs historical material
- remove stale hand-maintained "latest" lists where freshness cannot be guaranteed

### D2 — Patch-note normalization

Preserve the two-layer model:

```text
daily_patch
  = detailed technical audit history

patch_notes.json + patch_notes.md
  = UI/API human-facing changelog
```

Required future improvement:
- one deterministic helper/validator for appending a changelog entry
- schema validation
- source-path existence check
- date/freshness check
- duplicate-version/title detection

This helper is code and therefore belongs to an implementation batch after baseline freeze.

### D3 — Historical milestone classification

Historical M/Step/Phase documents are classified, not blindly renamed.

Rules:
- historical truth keeps historical names
- current canonical documentation uses responsibility/domain names
- new documents must not introduce obsolete milestone naming as architecture vocabulary
- historical aliases may be exposed through indexes

### D4 — Duplicate/current-authority consolidation

Candidate overlapping families include:
- `dev` vs `development`
- report-plan families
- execution-plan/current runtime docs
- scattered architecture summaries
- Q-family validation docs vs evaluation indexes

For each family:
1. identify canonical owner
2. identify unique historical evidence
3. merge only current duplicate semantics
4. leave compatibility pointers when path stability matters

### D5 — Reference-safe archive

Only move a document when:
- inbound Markdown references are mapped
- code references are mapped
- patch-note `sources[]` references are mapped
- replacement links/pointers are prepared

Historical evidence may remain in place permanently if movement creates more provenance risk than maintenance value.

### D6 — Documentation quality gates

Add/strengthen automated checks for:
- broken relative links
- patch-note source existence
- UI patch-note schema
- UI patch-note freshness vs daily patch
- stale canonical index targets
- duplicate canonical authority declarations

### D7 — P1.5 documentation freeze

Acceptance:
- canonical current docs are findable from `00_HOME.md`
- patch-note authority is unambiguous
- historical audit records are preserved
- no known broken references introduced by P1.5
- code/test/doc naming agree on current responsibilities
- P1.5/P1.6 roadmap is reflected in current navigation

## 6. Patch-Note Refactor Policy

Do not rewrite old patch-note entries.

For new changes:
- detailed technical record goes to `docs/daily_patch/` when the change meets the daily-patch threshold
- UI/API summary is appended to both canonical patch-note files in the same batch
- sources point to real repository-relative evidence
- UI patch notes remain read-only / non-execution-callable

The current long folder name `trading_agent_patch_notes_detailed_update` is a naming-cleanup candidate, but **not** a documentation-only rename because application code and tests depend on it.

## 7. Relation to Code Refactor

When a subsystem is refactored:

```text
code owner changes
  -> test owner changes
  -> canonical documentation owner changes
  -> patch note records the change
```

This prevents P1.5 from producing clean code with stale architecture documents.

## 8. Cloud / GPT Workflow

Default:
- GPT performs inventory, design, GitHub documentation updates, link/reference analysis, and low-risk documentation cleanup.
- Codex Cloud is optional for large mechanical moves/link rewrites.
- Claude Cloud is reserved for high-risk/final independent audits where its credit cost is justified.

## 9. Immediate Next Steps

1. keep the current patch-note paths stable
2. update stale navigation/readme pages
3. build the full documentation reference map
4. continue Strategist detailed decomposition
5. update Strategist canonical docs in the same batch as its future implementation
