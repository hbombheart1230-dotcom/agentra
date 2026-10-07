# Agentra P1.5 / P1.6 Refactor Design

Status: DESIGN / PRE-IMPLEMENTATION  
Branch: `design/p1.5-p1.6-modernization`  
Base at creation: `b67934a5baa95f4d329ccf345c14ed591a126a0f`

This directory is the design authority for the Agentra structural refactor and orchestration modernization work.

## Documents

1. `p1_5_p1_6_master_plan.md`
   - overall roadmap
   - P1.2/P1.3 gates
   - P1.5/P1.6 scope
   - relation to 2.E6, Safety 5D/5E/6, Q100, Reporter v2, memory, self-improvement, paper experiments

2. `p1_5_refactor_constitution.md`
   - non-negotiable invariants
   - agent modularity
   - LLM boundaries
   - naming policy
   - test architecture
   - Codex Cloud / Claude Cloud workflow
   - compatibility and migration policy

3. `p1_5_strategist_decomposition.md`
   - Strategist detailed-design seed
   - current known hotspots
   - target responsibilities
   - required analysis before implementation
   - implementation-packet format

## Critical Gate

This branch is for design and preparation only.

Do **not** begin P1.5 runtime implementation until:
- P1.2 cross-day acceptance is frozen,
- P1.3 Docker/operational acceptance is frozen,
- required regression suite is green,
- production-write leakage is NONE,
- trading-authority leakage is NONE,
- a baseline SHA/tag is recorded.

The implementation branch must be cut from that frozen baseline, not automatically from this design branch.
