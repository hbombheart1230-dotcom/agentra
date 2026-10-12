# P15-R3-FACADE-LOC-NEXT-CANDIDATES-012 — QUEUED, NOT AUTHORIZED

**Only after independent LOC 010 audit and GPT/user decision.** Current submitted façade LOC: AI **1958**, Markdown **1527**, Story **562**, total **4047** (original 18743). Preserved 436 façade defs; 86 relocated bodies under acceptance review. `SIZE_DEFERRED` is unpaid work, **not** a blanket waiver.

## Next measured candidates (from Claude LOC 010 inventory; remeasure before acting)
- AI dependency maps `_section_builder_deps` + `_context_builder_deps`: **−69 façade LOC** estimated, Owner ~89. Their call-time references must behave like original module globals, and LLM/truth dependencies must not change.
- Story dependency maps (3): **−64 façade LOC** estimated, Owner ~89. Careful about state, assembler and human payload patch surfaces.
- Markdown memory/policy phase lines (12): **−65 façade LOC** estimated, Owner ~136. **Higher risk:** truth-source order/provenance and presentation decisions; require broader deterministic fixture parity before selecting.
- Markdown numeric/format helpers (17): **−55**, Owner ~150, high-call-rate and many consumers.
- Time/duration helpers (7): **−38**, lower priority.
All numbers are *estimates*. Each successive slice needs a positive measured net façade reduction, one coherent domain Owner ≤350, 436 ABI/use-time patch preserved, deterministic goldens/LLM mock parity, isolated write-audit zero, source ledger and dual UI patch-note updates. Do not create `bodies_06`, move business truth ownership, or delete public wrappers by static absence alone. Wrapper removal normally belongs to P1.5.10 after consumer proof.

**No runtime implementation authorized by this queued page.** `refactor/p1.5` sole branch, live Windows/Q12 protected, P1.5.2 OPEN, P1.5.3 not authorized; real frozen report/LLM parity and controlled_mock_lanes isolation remain separate open gates.
