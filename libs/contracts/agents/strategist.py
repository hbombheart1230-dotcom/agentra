"""Stable Strategist contract namespace for an incremental ownership migration.

The definitions remain owned by libs.strategies.contracts until the runtime
callers can migrate independently of in-flight T4 work. Re-export the *same*
objects; do not duplicate dataclasses, schemas, or normalization behavior.

Existing imports remain supported. This module does not call an agent, broker,
Supervisor, or execution path.
"""

from libs.strategies.contracts import (
    StrategyAction,
    StrategyDecision,
    StrategyEvidence,
    StrategyInput,
    StrategyInvalidation,
    StrategistAggressiveness,
    StrategistMarketRegime,
    StrategistMarketSentiment,
    StrategistMonitorGuidance,
    StrategistOutput,
    StrategistPlaybook,
    StrategistRiskTone,
    StrategistScannerBias,
    coerce_strategist_output,
)

__all__ = [
    "StrategyAction",
    "StrategyDecision",
    "StrategyEvidence",
    "StrategyInput",
    "StrategyInvalidation",
    "StrategistAggressiveness",
    "StrategistMarketRegime",
    "StrategistMarketSentiment",
    "StrategistMonitorGuidance",
    "StrategistOutput",
    "StrategistPlaybook",
    "StrategistRiskTone",
    "StrategistScannerBias",
    "coerce_strategist_output",
]
