"""
Multi-Agent SEO Debate engine — async, truly parallel.

Data Flow:
  raw GSC ─► GSCAnalyzer.render ──┐
  BrandContext.render ────────────┤
                                  ▼
  Round 1 Draft     : asyncio.gather over all debaters         [parallel]
  Round 2 Critique  : asyncio.gather, each critiques the rest  [parallel]
  Round 3 Judge     : JudgeStrategy picks a (neutral) judge -> final plan
                                  ▼
                            DebateResult

Injected collaborators (all swappable -> testable, extensible):
  registry        : which models are alive
  gsc_analyzer    : which GSC lenses to apply (no orchestrator change to add one)
  judge_strategy  : how the judge is chosen + de-biased

Forward-compat: to add RAG/Memory, enrich BrandContext.extra_blocks or pass a
richer analyzer — the orchestrator stays as-is.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from ai.providers.base import LLMResponse
from ai.providers.registry import ProviderRegistry
from ai.debate import prompts as P
from ai.debate.gsc.analyzer import GSCAnalyzer
from ai.debate.context.brand import BrandContext
from ai.debate.judge import DefaultJudgeStrategy, JudgeStrategy

logger = logging.getLogger(__name__)

BrandLike = Union[BrandContext, str]


@dataclass
class DebateRounds:
    drafts: Dict[str, LLMResponse] = field(default_factory=dict)
    critiques: Dict[str, LLMResponse] = field(default_factory=dict)


@dataclass
class DebateResult:
    final_plan: str
    judge: Optional[LLMResponse]
    rounds: DebateRounds
    participants: List[str]
    judge_key: Optional[str] = None
    bias_mode: Optional[str] = None
    label_map: Dict[str, str] = field(default_factory=dict)
    degraded: bool = False
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return bool(self.final_plan and self.final_plan.strip())


class DebateOrchestrator:
    def __init__(
        self,
        registry: ProviderRegistry,
        *,
        gsc_analyzer: Optional[GSCAnalyzer] = None,
        judge_strategy: Optional[JudgeStrategy] = None,
        min_participants: int = 1,
        judge_temperature: float = 0.3,  # low temp -> deterministic verdict
    ) -> None:
        self.registry = registry
        self.gsc_analyzer = gsc_analyzer or GSCAnalyzer()
        self.judge_strategy = judge_strategy or DefaultJudgeStrategy()
        self.min_participants = min_participants
        self.judge_temperature = judge_temperature

    @staticmethod
    def _render_brand(brand: BrandLike) -> str:
        return brand.render() if isinstance(brand, BrandContext) else str(brand)

    # ── async core ──────────────────────────────────────────────────────
    async def arun(
        self,
        gsc_rows: List[Dict[str, Any]],
        brand_context: BrandLike,
        *,
        debater_keys: Optional[List[str]] = None,
        previous_gsc_rows: Optional[List[Dict[str, Any]]] = None,
    ) -> DebateResult:
        debaters = debater_keys or self.registry.available()
        debaters = [k for k in debaters if k in self.registry.available()]
        if not debaters:
            return DebateResult("", None, DebateRounds(), [],
                                error="no providers available (check API keys)")

        gsc_context = self.gsc_analyzer.render(gsc_rows, previous_gsc_rows)
        brand_str = self._render_brand(brand_context)

        # ── Round 1: independent drafts (parallel) ──────────────────────
        draft_prompt = P.build_draft_prompt(gsc_context, brand_str)
        draft_list = await asyncio.gather(*[
            self.registry.get(k).agenerate(P.DRAFT_SYSTEM_INSTRUCTION, draft_prompt, role="draft")
            for k in debaters
        ])
        drafts = dict(zip(debaters, draft_list))
        usable = [k for k in debaters if drafts[k].is_usable]
        if len(usable) < self.min_participants:
            return DebateResult("", None, DebateRounds(drafts=drafts), debaters, degraded=True,
                                error=f"only {len(usable)} usable draft(s); need {self.min_participants}")

        # ── Round 2: cross-critique (parallel) ──────────────────────────
        async def critique(key: str) -> LLMResponse:
            rivals = {k: drafts[k].text for k in usable if k != key} or {key: drafts[key].text}
            prompt = P.build_critique_prompt(drafts[key].text, rivals)
            return await self.registry.get(key).agenerate(
                P.CRITIQUE_SYSTEM_INSTRUCTION, prompt, role="critique")

        crit_list = await asyncio.gather(*[critique(k) for k in usable])
        critiques = dict(zip(usable, crit_list))

        # ── Round 3: judge synthesis (neutral / de-biased) ──────────────
        plan = self.judge_strategy.plan(
            self.registry, usable, gsc_context, brand_str,
            drafts={k: drafts[k].text for k in usable},
            critiques={k: critiques[k].text for k in usable if critiques[k].is_usable},
        )
        judge = await self.registry.get(plan.judge_key).agenerate(
            plan.system, plan.prompt, role="judge", temperature=self.judge_temperature)

        rounds = DebateRounds(drafts=drafts, critiques=critiques)
        degraded = len(usable) < len(debaters)

        if not judge.is_usable:  # graceful fallback -> strongest surviving draft
            return DebateResult(drafts[usable[0]].text, judge, rounds, debaters,
                                judge_key=plan.judge_key, bias_mode=plan.bias_mode,
                                label_map=plan.label_map, degraded=True,
                                error="judge failed; returned strongest draft")

        return DebateResult(judge.text, judge, rounds, debaters,
                            judge_key=plan.judge_key, bias_mode=plan.bias_mode,
                            label_map=plan.label_map, degraded=degraded)

    # ── sync convenience wrapper ────────────────────────────────────────
    def run(self, gsc_rows, brand_context, *, debater_keys=None, previous_gsc_rows=None) -> DebateResult:
        return asyncio.run(self.arun(
            gsc_rows, brand_context,
            debater_keys=debater_keys, previous_gsc_rows=previous_gsc_rows))
