> **HISTORICAL COMMANDER CONFIGURATION DESIGN PRINCIPLE — NOT AN APPROVAL/GUARD BYPASS.** The text below records the direction toward Commander-owned runtime configuration; it is not evidence that existing broker mode, max-notional, allowlist or supervisor gates may be removed. Frozen [trading safety](../ground_rules/AGENT_RULES.md), [D00](../ENGINEERING_DELIVERY_POLICY.md) and [Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20) retain priority. No runtime config is modified by this document.

# Env Rules

## Principle
Commander owns configuration choice and policy authority.

We minimize env-driven toggles over time. If a setting is needed, it should be
selected by Commander and injected through commander-applied policy or runtime
state, rather than owned independently by downstream agents.

## Rules
- do not add new env toggles when Commander can make the decision
- do not create agent-local ownership for runtime behavior flags
- prefer `state["applied_policy"]` or other Commander-owned runtime state
- Strategist, Reporter, Scanner, and Monitor are consumers, not owners

## Practical direction
- env should shrink over time
- Commander-applied policy is the preferred source of truth
- runtime state may be used as a transitional fallback
- downstream agents may read configuration, but should not own final choice
