# Agentra Git-hosted work orders — START HERE

**Minimal startup:** root [AGENTS.md](../../../AGENTS.md) or [CLAUDE.md](../../../CLAUDE.md) → [standing delivery-first policy](../../ENGINEERING_DELIVERY_POLICY.md) → [Issue #20 LIVE checkpoint](https://github.com/hbombheart1230-dotcom/agentra/issues/20) → [CURRENT.md](CURRENT.md) → [COMMON_RULES.md](COMMON_RULES.md). Open a role issue only when #20 assigns a new exact-SHA task.

| Location | Meaning | Active work authority |
|---|---|---|
| GitHub #20 | One current issue: verified branch SHAs, CI, PASS/HOLD, NEXT one action; new-chat handoff | YES, under user approval and safety |
| CURRENT.md | Short repo-local pointer and exact historic integrated code SHA; defer to live GitHub | NO independent queue |
| COMMON_RULES.md | Current role-neutral workflow, safety, tests, ZIP and verification method | Process only |
| ENGINEERING_DELIVERY_POLICY.md | Permanent anti-loop delivery constitution | Process only |
| Issues #16–#19 | Codex/Claude development and reciprocal audit; previous tasks closed, may be explicitly reactivated | ONLY when reactivated |
| archive/, evidence/, older P15-*.md | Historical work-order / immutable acceptance evidence | NO |
| ../work_projects/ACTIVATION.md and STATUS.json | 2026-10-17 Reporter/Monitor **historical snapshot**, not today's phase | NO |

If an older document says `ACTIVE`, `NOT_STARTED`, single `refactor/p1.5` branch, `Claude implements/Codex audits`, or `NO ZIP`, it is historical. The newer current Issue #20 and permanent policy supersede it; preserved unchanged in Git history at `c5fe8a9a`.

**Definition of delivery:** approved code implementation → independent DELTA audit → GPT selective integration → new integration-SHA required CI → accurate #20 checkpoint. Do not revive an old worker merely because an issue is still visible. No live trading, `main` merge or unsafe destructive cleanup without user permission. Both UI-linked patchnotes JSON and MD are always synchronized for tracked changes.
