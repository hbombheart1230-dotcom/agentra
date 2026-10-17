# Agentra P1.5 continuity runner — source delivery manifest (NOT DEPLOYED)

**Status:** LOCAL_PROTOTYPE_TESTED / NOT_INSTALLED / NOT_RUNNING. Infrastructure branch only, branched from frozen main without changes to main, Reporter or Monitor.

A local source ZIP for this conversation contains exactly four source and test files:
- tools/devteam/continuity_runner.py (SHA-256 75b68de64480e6cd28be38549c0462716e3f46cd01447e0bc31c148caee2e1fc)
- tools/devteam/continuity_config.example.json (SHA-256 e0c117fb64f244813c36a981c9453cb6ab95726290845c3a81cd6a7d32a5e552)
- tools/devteam/README.md (SHA-256 108b4c2fb72389b6e86c9d5a9967a7e2cfd91f489e3d5c3ed77432e5438fa8bd)
- tests/test_continuity_runner.py (SHA-256 aebaf941646794d768d66a99f459f11097d3eadc2c96450722cd7a334c9ebddb)

Changed-only ZIP SHA-256: `b13ae37fa3e5e432dc64b9811c40dd2fd34bf1241e19c435fa47a9b571fa3f73`.
The four code files were exercised by local `python -m unittest discover -s tests -v`: **11 PASS** including a fake Claude CLI, explicit no-progress deduplication, config validation, branch spoof rejection, stop defaults, separate per-role states, origin check. This is test evidence on a local mock environment, NOT the user's Windows box. GitHub manifest is documentation only: the four runnable files **are not present on this Git branch yet** and must be applied from the ZIP or pushed from the verified local source. Never claim this manifest is a deployed runner.

**Runtime design:** Separate Windows dev host, isolated Reporter and Monitor checkouts; strict origin+branch/clean working-tree validation; only two allowlisted CLI adapters, Git pushed SHA check after commit, single-writer lock, local durable state, per-day invocation count and wall-time cap, STOP file, no git reset/force and no live brokerage. Does not inspect actual token/dollar spend: requires provider-level spend controls. `enabled=false` and `provider_spend_limit_acknowledged=false` in the example config, requiring explicit operator opt-in. Running the source requires installed authenticated Claude/Codex CLI with approved, permission-scoped developer credentials and explicit `--activate`; never pass danger-full-access flags or secrets.

**Limitations:** Stops WAITING_WORK when a CLI produces no verified new commit, to avoid loops; automatic Issue-comment reactivation and cross-role Strategist/Scanner switching are future features. Power-off/sleep means no process. Work's hourly GitHub automation is separate and does not start CLI processes.

**Next host actions:** validate exact checkout paths, auth and permissions, provider budget cap; smoke one worker at a time, inspect branch SHA and state; then activate two runners on a persistent host after verifying STOP/sandbox. Do not start the infrastructure on a broker production host or merge into main without the full P1.5 gate.
