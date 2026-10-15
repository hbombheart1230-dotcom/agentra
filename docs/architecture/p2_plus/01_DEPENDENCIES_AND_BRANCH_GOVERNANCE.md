# Architecture Dependencies, Four Managed Branches & Merge Contract

Status: DESIGN PROCESS POLICY / PROPOSED in `design/p2plus-architecture`.

## 1. Four branch model

```text
                         main (ONLY accepted/runtime baseline)
                          | 2f95bba… as of architecture branch creation
        ┌─────────────────┼───────────────────────────────┐
        v                 v                               v
 refactor/p1.5  design/p1.6-orchestration       design/p2plus-architecture
 implement      detailed conditional blueprint  P2–P8 conceptual designs
 & freeze       + offline later                  NO implementation
        |
        | formal P1.5.11 release PASS + user acceptance
        v
 main (+P1.5)  ← P1.6 branch RECONCILED against this accepted SHA
        |         (don't blindly merge P1.5 WIP ancestry!)
        | only if P1.6 comparison/decision/freeze accepted
        v
 main (+P1.6 decision/accepted changes) ← P2+ architecture reconciled here
        |                                   (docs-only design may be
        |                                    cherry-picked or re-based after review)
        v
 P2 implementation authorized → separate controlled change/review windows
        v
 P2 freeze → main → P3 freeze → main → … → P7 freeze → main
```

**Important:** P1.6 is currently a design branch descended from a **P1.5 work-in-progress** snapshot, not from final P1.5 freeze. Do not merge it directly into `main` just because P1.5 merged; that risks bringing stale/unaccepted source history. Choose one:
- **Preferred for a shared-history design branch**: after P1.5 freeze, create a *reviewed, clean PR/cherry-pick of only intended design/document deltas* against frozen `main`; repair UI patch note conflicts and preserve original branch for provenance.
- **Alternative**: explicit rebase (requires reviewed tree/diff/conflict list and agreed history rewrite) only after human approval.
No automatic force-push, no blind rebasing and no implicit merge. Same caution applies if P2+ design is based on older main: reconcile normative docs/patch notes before incorporation.

## 2. Branch-specific authority, isolation and check-in

| Branch | Mutable by | Scope | Merging gate |
|---|---|---|---|
| `main` | accepted release process only | baseline/source of production truth | never push unreviewed implementation |
| `refactor/p1.5` | assigned P1.5 implementer/reviewer | current P1.5 work order only; safety-locked areas | P1.5.11 full regression/UEF/Docker/write/authority+user acceptance |
| `design/p1.6-orchestration` | architecture documentation owners | candidate framework design, future sandbox work only after P1.5 freeze | pin freeze SHA, parity/bench/independent ADR; no forced library adoption |
| `design/p2plus-architecture` | architecture documentation owners | P2–P8 requirements, invariant/contract sketches, dependency plan | doc review first; stage implementation packet only on accepted predecessors |

P1.5 existing `docs/refactor/work_orders/CURRENT.md` remains active. P2 architecture does NOT create/replace P1.5 work orders. `design/*` branches cannot be deployed, set execution flags, run production reconciliation or change running Docker state.

## 3. Define the milestone words precisely

- `ARCHITECTURE_PREPARED`: stable design docs exist; **no** implementation, tests or live change.
- `IMPLEMENTATION_DESIGN_READY`: actual frozen predecessor SHA examined; file/function/ABI test plan complete.
- `IMPLEMENTED`: changes authored, focused tests run; **not** release.
- `CANDIDATE_FROZEN`: full candidate SHA+environment+evidence locked; no hidden blocker.
- `ACCEPTED`: independent audit + GPT/user signoff on verified candidate; only then eligible to merge main.
- `RELEASED`: deployment/operational rollout separately accepted; merge alone not live deployment.
- `BLOCKED`: a required proof/gate missing or failed; never substitute verbal PASS.

No phase is called 'done' purely because its design branch has a commit. `P1.6` may terminate `KEEP_CUSTOM`, `DEFER` or `ADOPT` based on proof. KEEP_CUSTOM can be an accepted decision without switching runtime.

## 4. Predecessor dependency DAG

```text
P1.5.11 formal freeze --------> P1.6 design revalidation + offline graph comparison
                                             |
                                     P1.6 architecture decision
                                             |
                                      P2 implementable blueprint
                                             |
                      P2 strategy integration (not live promotion)
                                             |
                            P3 Step5D → Step5E → Step6 Safety Freeze
                                             |
                       P4 Q100-1/2/3 + Reporter V2 (UEF reads)
                                             |
                              P5 Q100-4/5 Memory & Retrieval
                                             |
                             P6 Q100-6 feedback Level 1–5
                                             |
                                       P7 V2 Full Freeze
                                             |
                            P8 formal paper result / final dataset
```

Parallel **DESIGN/READ-ONLY** activities now allowed: architecture P2–P8, paper hypotheses and pre-registration, immutable prospective market/evidence capture where pre-existing/approved, analysis of missing source contracts. No new live runtime features or framework shadow executable before gates.

**Conditional early read-only work:** independent P2 data freshness inventory / safety risk register may be advanced without modifying production, but this is not P2 implementation acceptance.

## 5. Gate by phase / immutable evidence

| To start | Must have | Can prepare ahead |
|---|---|---|
| P1.6 executable comparison | accepted P1.5 SHA/DTO/mode map, no authority/write leaks | docs/fixtures schema and benchmarks |
| P2 code | P1.6 decision + reconciled source snapshot, agent contract registry | ProgramEntry/context design |
| P3 broker recovery | existing Step5B/C frozen obligations, P2 changes isolated, operational reconciler design/safety review | state machine/incident manual scenarios |
| P4 reporting / Q100 | Step6 accepted and authoritative UEF-9 read availability | registry/evidence schema as drafts |
| P5 memory activation | UEF provenance, P4 attribution and Step6, accepted memory privacy/growth policy | YAML/frontmatter/Obsidian model |
| P6 promotion suggestion | OOS matched evaluation and P5 lineage, governance approval | causal control design and stop rules |
| P7 V2 freeze | integration all gates green, full rollback restore | acceptance matrix |
| P8 final empirical claims | P7 tagged, immutable datasets/experiment scripts / leakage checks | study preregistration and fixed fixtures |

## 6. Freeze merge protocol — applicable to each phase

1. Pin candidate commit, compare to currently accepted `main`, capture tree and change manifest.
2. Lock the **actual** tests and source version, including Docker/mock and UEF checks for impacted layers; run proper independent audit. No false-green tests due to reused artifacts.
3. Verify zero unsafe broker/LLM/production writes during offline tests and prove guard/authority invariants; if relevant prove real operational acceptance on separately approved window.
4. GPT + user explicitly accept candidate; if blocked, DO NOT merge.
5. Update UI-linked patch notes `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` and `patch_notes.md`, plus a concise `docs/daily_patch/` entry on the **actual target branch**, resolving older design-branch version differences.
6. Integrate via reviewed PR/merge/cherry-pick against latest main, CI/gate verified at integrated SHA. Avoid merging the full old design ancestry if it includes unaccepted WIP.
7. Tag released/frozen source with unique milestone tag and freeze manifest (never reuse incorrect prior evidence).
8. Re-audit next phase's implementation locations and contracts; only then build code-level packets.

## 7. Context and credits policy

Each agent reads a **short stable index and only directly affected source/contract files**. Do not reread completed P1.5 history, archived work orders or full patch timeline every time. Codex/Claude report diffs, candidate SHA, tests executed, outstanding limitations and next gate. Prefer one integrated low-risk wave over repeated microreviews, without collapsing mandatory high-risk safety checks.

## 8. Forbidden today

No P2–P8 Python/config/runtime/test implementation on this design branch; no branch merges; no live account operations; no real LLM calls; no UEF freeze changes; no new strategy auto-promotion; no ZIP (user said pre-design GitHub-only).
