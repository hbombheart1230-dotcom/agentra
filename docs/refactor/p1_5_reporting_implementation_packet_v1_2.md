# P1.5.2 Reporting v1.2 — Small-Owner Continuation Packet

Date: 2026-10-09
Branch: refactor/p1.5
Overrides future residual R2 implementation/size acceptance of v1.1; retains original Reporting v1.0 and v1.1 history.
Policy: p1_5_small_owner_policy_and_rollback_decision_v1_2.md.

## Audit-backed size debt
Observed current physical LOC on refactor/p1.5:
- Public façades trade_report_ai.py 3,039; trade_report_markdown_clean.py 3,043; trade_story_pipeline.py 948.
- Existing extracted Owners: trade_report/sections.py **2,233**; trade_story_pipeline_story_assembly.py **1,356**; trade_story_pipeline_human_payloads.py **1,337**; trade_report/markdown_summary.py **1,275**; trade_report/markdown_signals.py **812**; trade_report/operator_text.py **804**; trade_story_pipeline_evidence_hydration.py **661**; trade_report/service.py **575**.

**All NEW/moved/extracted implementation-owner files MUST be <=350 physical LOC at tranche PASS.** 150–300 preferred. Existing overlimit owners block final Reporting Owner-size acceptance until distinct responsibilities are split, or their unmodified legacy exceptions are explicitly recorded as OPEN (never marked fulfilled). Preserve v1.0 public façade guidance (AI 300–600, Markdown 300–500, Story 250–450); prefer <=350 where consumer parity permits; a wrapper size exception cannot be mislabeled PASS.

## Coherent candidate owner tree — create only after actual source/caller graph
libs/reporting/trade_report/section_parts/
  market.py 150–300; strategist.py 150–300; scanner.py 150–300;
  entry.py 150–300; exit.py 150–300; lifecycle.py 150–300;
  execution.py 150–300; reporter.py 150–300
libs/reporting/trade_report/summary_parts/
  input.py 150–300; render.py 150–300; diagnostics.py 150–300
libs/reporting/trade_report/signal_parts/
  entry.py 150–300; exit.py 150–300
libs/reporting/trade_report/operator_parts/
  labels.py 150–300; text.py 150–300; sections.py 150–300
libs/reporting/trade_story_human_parts/
  market.py 150–300; scanner.py 150–300; monitor.py 150–300; filters.py 150–300
libs/reporting/trade_story_assembly_parts/
  lifecycle.py 150–300; section_seeds.py 150–300; composition.py 150–300
libs/reporting/trade_story_evidence_parts/
  hydration.py 150–300; candidate_evidence.py 150–300

The above modules are **candidates, not a bulk file-creation checklist**. First prove an existing Owner cannot retain the cohesive concern under the cap. Preserve existing stable façades and private monkeypatch call-time seams; avoid ambiguous Python module/package same-name collisions. No parallel Reporting framework or duplicate Scanner/Monitor/truth ownership.

## Implementation sequence
R0 — LOCAL FIRST. Claude checks C:\Agentra SHA/status and preserves dirty Q12 worktrees. Read-only BEFORE snapshots: representative AI/Markdown/trade-story JSON outputs, prompts/retry/LLM counts, artifact paths, truth-source precedence, lifecycle/provenance, outputs from real local report fixtures. Characterize historical tests on the CURRENT local baseline.

R1 — Complete a file/function Owner ledger: KEEP/MOVE/WRAPPER/DEAD/SAFETY-LOCK, source LOC, production/test callers, import cycles, monkeypatch names, IO/state/LLM, exact target owner, expected unchanged goldens.

R2 — Start with ONE read-only coherent slice from a large existing owner (recommend sections.py). Extract into a <=350-line distinct owner, keep compatibility wrapper, run targeted parity tests. Do not move several large packages in the first batch.

R3 — Repeat one slice at a time across sections/story assembly/human payload/summary then signals/operator text/hydration/service. The existing oversized intermediate files are NOT called final refactor success. Stop if a newly created owner exceeds 350.

R4 — Direct unit/integration/regression tests by responsibility, retain all historical scenario coverage and hidden import/monkeypatch expectations. Remove obsolete wrappers only with actual consumer-proof via P1.5.10.

R5 — Full Reporting targeted and broad suite, byte/semantic report parity, LLM call/retry/fallback/timeout, no UEF/Step5/trading authority changes and Codex independent audit. Record unresolved debt explicitly. Only then declare P1.5.2 program PASS.

## Rollback verdict
**CONTINUE existing R2-A/B/C**, never reset all code merely because current owners are large. Selective revert only for a demonstrated newly introduced regression. All implementation must use the two-branch model main/refactor/p1.5; no remote CI/artifact/per-tranche branches.
