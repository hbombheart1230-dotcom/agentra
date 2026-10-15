# P7 — Agentra V2 Formal System Freeze & Operational Acceptance

Status: ACCEPTANCE ARCHITECTURE ONLY. P7 freeze cannot be declared until real P2–P6 releases and all gates exist.

## Objective and candidate manifest

Define one coherent, auditable V2 system baseline with immutable source/engine/deployment/config/fixture/UEF hashes and verified invariants. "Unit tests pass" alone never freezes a trading system; production promotion and trade authority need independent approval.

```text
V2FreezeCandidate
  candidate_sha / parent_main_sha / tag_candidate
  P1.5_freeze_sha / P1.6_ADR / accepted_engine_version
  P2_program_registry_digest / context_contract_version
  Step6_safety_baseline_digest
  UEF_freeze_manifest_digest + daily UEF VALID binding references
  Q100_registry/attribution_versions
  memory/retrieval_schema_versions + memory_disabled_fallback_proof
  Level4/5 review_approval_policy_digest
  replay_dataset_manifest / environment_versions
  artifact_lineage / test_inventory_hash / ci_logs
  deployment_profile / ownership/guard states
  independent_audit_verdict / human_approval / rollback_reference
```
Conceptual schema only; do not pretend this exists.

## Acceptance domains (all mandatory)

| Gate | Proof | Non-waivable failure |
|---|---|---|
| G0 baseline | exact commit/tag and no unmerged unreviewed source | drift or ambiguous candidate SHA |
| G1 role/contract | 7-role ownership, standalone input/output, compatibility and state adapters | new LLM trade authority |
| G2 strategy | program/time/source quality, Q10/Q12/rank reasoning, no silent policy change | look-ahead/missing source passed as reliable |
| G3 broker safety | Step5B/C/D/E/6 guards/CAS/UNKNOWN/recovery authority | retry after unknown, unapproved mutation |
| G4 execution topology | Docker single owner/heartbeat/restarts/shutdown, host gate, preopen/closeout | dual owner, stale takeover, unsafe drain |
| G5 evaluation | UEF frozen manifest match, 7/8 conservation, 9 VALID, replay/source freshness | missing pair/id mismatch/canonical diagnostic write |
| G6 Reporter/Q100 | correct source IDs, derived vs authority, reports preserve canonical truth | parallel UEF scoring / metric substitution |
| G7 memory | provenance, TTL, memory-off identical safety, no LLM-induced broker path | vault controls approval or execution |
| G8 improvement | Levels 1–5 only, human review, no production auto-mutation | self-tuned live risk/strategy without separate release |
| G9 operability | traces, incident recovery, alert, evidence access, rollback/drill | unreproducible incident or inability to halt |
| G10 release quality | full suitable pytest, contamination and artifact retention policy, Windows/host/Docker supported | unrun critical suite claimed PASS |
| G11 independent review | Codex pinned-SHA independent audit, GPT/user explicit acceptance | unresolved CRITICAL/HIGH |

UEF daily validation remains recurring, not a one-time P7 green screenshot. Every day check UEF-7 candidate conservation and coverage, UEF-8 pair count/unique IDs/status counts/COMPARABLE, UEF-9 binding and authority, replay determinism and leakage.

## Fail-closed incident response

A failed guard/owner/UEF binding gate prevents release. Do not "unblock" by changing frozen authority, ignoring failed tests, rewriting fixture outputs or promoting conditional evidence. Evidence is append-only and linked by SHA. Tests must not create long-lived repo artifact explosions: isolated roots per run, successes auto-cleaned and bounded failure evidence retention.

## Release decision and rollback

1. Candidate SHA freeze, agreed scenario manifest and full regression; quantify any existing unrelated failures explicitly.
2. Codex independently inspects effective diff and active runtime against baseline; reruns focused high-risk tests and validates false-green risks.
3. GPT summarizes material change/defect/risk; human operator accepts PASS, PASS_WITH_FINDINGS only where explicitly safe and policy allows, or FAIL.
4. On acceptance, reviewed integration into `main`, immutable tag/manifest, post-merge verification. No implicit live deployment.
5. Separately authorized deployment window: prepare last-known-good image/config, rollback procedure, operator pause, broker exposure state, Step5D/5E pending-incident handling and ownership lease; confirm safe reversion.
6. If error after rollout, stop new mutation safely, preserve UNKNOWN quarantine, withdraw feature route and restore known baseline without manipulating unconfirmed broker outcomes.

## Operational deliverables

Versioned architecture + contract map; incident runbooks; UI patch history; recorded implementation SHA/version; final validated UEF evidence; fault-injection and mock/real safe-authorization proofs; formal step-by-step recovery/rollback drills; issue/risk disposition and independent signoff.

**P7 accepted ≠ Paper scientifically valid.** P8 still needs prospective experimental design, source data quality, statistical uncertainty and replication to substantiate claims.
