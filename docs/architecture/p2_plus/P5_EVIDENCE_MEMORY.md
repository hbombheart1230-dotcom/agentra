# P5 — Evidence Memory / Obsidian Architecture (Q100-4/5)

Status: DESIGN ONLY. No Knowledge Vault directory, database, index, embedding service or skill is created.

## Hard truth hierarchy — inherited Architecture V2

```text
Tier 1  Operational Truth  | SQLite, EventLog, broker/intent history | execution owner ONLY
Tier 2  Evaluation Truth   | UEF canonical + verified reports        | UEF owner ONLY
Tier 3  Knowledge          | validated/advisory ExperienceRecord    | Reporter curator + review
Tier 4  Knowledge UI       | Markdown/Obsidian view/export          | UI ONLY
```

The memory store is **not an eighth agent**; Reporter curates, Strategist retrieves. It cannot directly create/approve an `OrderIntent` or set broker guards. A corrupt vault or slow retrieval is advisory unavailable, never license to relax safe defaults.

## Knowledge schema and promotion

```text
Raw Event
 → Daily Observation
 → Repeated Evidence
 → Finding
 → Lesson
 → Strategy Knowledge
```

A candidate record includes:
- `source_program_id`
- `source_evaluation_record_id` (set; nonempty to promote beyond Daily Observation)
- `source_class`: CANONICAL_EVALUATION / LEGACY_EVALUATION / OPERATOR_OBSERVATION / DERIVED_AGGREGATE
- `promotion_stage`, `promoted_by`, `promoted_at`, `confidence_basis`, caveats
- `observation_window`, market regime/symbol/sector, valid-from/expiry/review timestamp
- `superseded_by` and provenance/record digest
- `memory_version`, schema version, responsible review/algorithm version.

Proposed **promotion gate**: evidence must be repeated across independent data where appropriate, no critical contamination, UEF-9 VALID and source IDs verified, OOS validation before a Finding becomes Lesson. Draft thresholds must not be marketed as statistically proven until evaluated.

## Reporter curation → Strategist read

```text
P4 structured finding
    ↓ provenance + quality checks
Candidate Lesson queue  → review / evidence audit → versioned promoted Lesson
    ↓                                        ↓
Indexed queryable record                     Obsidian Markdown export
    ↓
Context-specific retrieval, quality filtering, budget/TTL limits
    ↓
Strategist compact context pack, advisory-only
    ↓
Existing reasoning workflow; log which memory_id/version affected context
```

Retrieval priority from Q100 source:
1. Verified CANONICAL_EVALUATION Lessons for exact symbol and regime.
2. Verified canonical Lessons from related symbol/sector.
3. Stable Strategy Knowledge matching regime.
4. LEGACY_EVALUATION (explicitly lower trust).
5. Findings (provisional) with limitations.
Derived aggregate/operator notes never outrank a canonical exact-match lesson at equal specificity.

**Negative behavior:** if no credible match, emit empty context + `NO_TRUSTED_MEMORY`; never backfill with unrelated confidence, stale legacy information or a model's hallucinated prior.

## Portable vault and logical storage

Markdown is a **read/export and human review surface**, not canonical execution ledger. Conceptual folders, following `architecture_v2.md` and Q100 roadmap:

```text
knowledge/Programs/
knowledge/Markets/
knowledge/Strategies/
knowledge/Symbols/
knowledge/Experiments/
knowledge/Incidents/
knowledge/Decisions/
knowledge/Findings/
knowledge/Lessons/
knowledge/Reports/{Daily,Weekly,Monthly}/
```

Path above is an **illustration**, not an approval to add this directory to the repository or store private broker/account artifacts in Git. Keep canonical content versioned in bounded authorized memory storage; export derived, redacted Markdown notes with immutable IDs/backlinks. No bidirectional UI edits that silently rewrite evidence. Edits go through a reviewed curator transaction.

## Design trade-offs and open decisions

- Source of authoritative *knowledge metadata*: append-only JSONL/SQLite vs versioned object store — evaluate retention, search, revisions and single-owner constraints after P4; Obsidian is never the authority.
- Search: deterministic tags/symbol/time/regime first, optional embeddings **only when privacy/cost/versioning validated**. No external data upload implied.
- Retention: program-specific TTL/review, maximum lesson/context budget, revocation/supersedes; bound archive/test artifacts.
- Context packaging: redacted summary, source IDs, confidence limitations, regime and expiry, token budget and model cost; no credentials or private account data.
- Conflict resolution: newer validated findings do not silently erase an old lesson; supersession points both directions with reason and validation evidence.

## Proof before activation

1. Quality/lineage: unmatched source ID, invalid UEF binding, duplicate promotion, contaminated source or legacy-only claim → BLOCKED/downgraded.
2. Retrieval: exact-match precedence, adversarial contradictory lessons, stale TTL, absent vault, memory poisoning tests, prompt injection controls.
3. Causality: memory-on/off matched replay with same market inputs and LLM budget; no success claim from anecdote.
4. Safety: after vault failure/timeout, same Supervisor/Executor policy and trading authority; **zero dependency on memory for safety correctness**.
5. Operational: bounded storage, redaction, isolated writes, no persistence into production SQLite, reproducible index rebuild, deterministic retrieval for deterministic inputs.

**Exit:** provenance-preserving advisory knowledge/retrieval with independent acceptance. It must not produce live policy self-tuning or broker actions; that is explicitly prohibited in P6 as well.
