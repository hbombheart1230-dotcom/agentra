# P1.5.2 Reporting service owner split 07

Baseline 3f3a32185c1e5cea555e888dc50def0a3b6cbd23
One AI-generation service 347 LOC, one deterministic summary service 232 LOC, both within hard 350 cap.
Original service source 573 -> import compatibility 4 LOC; source function bodies copied verbatim.
No LLM model routing, call count, JSON schema, fallback semantics or broker/UEF changes. GitHub reporting CI to validate; local real artifact/LLM-equivalence acceptance not asserted.
