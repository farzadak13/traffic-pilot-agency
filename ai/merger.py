"""
ai/merger.py — thin facade over the debate engine.

The legacy single-pass merge is gone; callers use one of:
    run_seo_debate(...)   sync, one call
    arun_seo_debate(...)  async, for async apps
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Mapping, Optional, Union

from ai.providers.registry import build_registry
from ai.debate.orchestrator import DebateOrchestrator, DebateResult
from ai.debate.gsc.analyzer import GSCAnalyzer
from ai.debate.context.brand import BrandContext
from ai.debate.judge import DefaultJudgeStrategy

logger = logging.getLogger(__name__)

BrandLike = Union[BrandContext, str]


def _build_orchestrator(secrets, model_overrides, strategy_keys, preferred_judge):
    registry = build_registry(secrets, model_overrides=model_overrides)
    return DebateOrchestrator(
        registry,
        gsc_analyzer=GSCAnalyzer(strategy_keys=strategy_keys),
        judge_strategy=DefaultJudgeStrategy(preferred_judge=preferred_judge),
    )


def run_seo_debate(
    gsc_rows: List[Dict[str, Any]],
    brand_context: BrandLike,
    secrets: Mapping[str, str],
    *,
    debater_keys: Optional[List[str]] = None,
    previous_gsc_rows: Optional[List[Dict[str, Any]]] = None,
    strategy_keys: Optional[List[str]] = None,
    model_overrides: Optional[Mapping[str, str]] = None,
    preferred_judge: str = "claude",
) -> DebateResult:
    """Build providers from `secrets` and run the full async debate (sync wrapper)."""
    orch = _build_orchestrator(secrets, model_overrides, strategy_keys, preferred_judge)
    return orch.run(gsc_rows, brand_context,
                    debater_keys=debater_keys, previous_gsc_rows=previous_gsc_rows)


async def arun_seo_debate(
    gsc_rows: List[Dict[str, Any]],
    brand_context: BrandLike,
    secrets: Mapping[str, str],
    *,
    debater_keys: Optional[List[str]] = None,
    previous_gsc_rows: Optional[List[Dict[str, Any]]] = None,
    strategy_keys: Optional[List[str]] = None,
    model_overrides: Optional[Mapping[str, str]] = None,
    preferred_judge: str = "claude",
) -> DebateResult:
    orch = _build_orchestrator(secrets, model_overrides, strategy_keys, preferred_judge)
    return await orch.arun(gsc_rows, brand_context,
                           debater_keys=debater_keys, previous_gsc_rows=previous_gsc_rows)


def validate_output(text: str) -> bool:  # legacy shim
    return bool(text and text.strip() and len(text.strip()) >= 200)
