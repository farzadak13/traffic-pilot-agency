"""
Judge selection + bias-reduction strategy.

Policy (DefaultJudgeStrategy):
1. NEUTRAL THIRD PARTY — if a provider exists that did NOT debate
   (e.g. Claude judging a Gemini-vs-OpenAI debate), it judges. Lowest bias.
2. ANONYMIZED PEER — if every provider debated, one of them judges, but
   authorship is stripped (پلن A/B/C…) and the order is shuffled, so the
   judge cannot systematically favor its own output (self-enhancement bias).

Swappable: pass any object implementing `plan(...)` to the orchestrator
(e.g. an EnsembleJudge that polls all providers and majority-votes later).
"""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import Dict, List

from ai.debate import prompts as P
from ai.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)


@dataclass
class JudgePlan:
    judge_key: str
    system: str
    prompt: str
    bias_mode: str                     # "neutral_third_party" | "anonymized_peer"
    label_map: Dict[str, str] = field(default_factory=dict)  # label -> provider


class JudgeStrategy:
    def plan(self, registry: ProviderRegistry, debaters: List[str],
             gsc_context: str, brand_context: str,
             drafts: Dict[str, str], critiques: Dict[str, str]) -> JudgePlan:
        raise NotImplementedError


class DefaultJudgeStrategy(JudgeStrategy):
    def __init__(self, preferred_judge: str = "claude", seed: int | None = None):
        self.preferred_judge = preferred_judge
        self._rng = random.Random(seed)

    def plan(self, registry, debaters, gsc_context, brand_context, drafts, critiques):
        available = registry.available()
        neutral = [k for k in available if k not in debaters]

        if neutral:
            judge_key = self.preferred_judge if self.preferred_judge in neutral else neutral[0]
            labeled_drafts = {f"استراتژیست {k}": v for k, v in drafts.items()}
            labeled_crit = {f"نقد {k}": v for k, v in critiques.items()}
            label_map = {f"استراتژیست {k}": k for k in drafts}
            bias = "neutral_third_party"
        else:
            judge_key = debaters[0]
            items = list(drafts.items())
            self._rng.shuffle(items)                          # de-bias ordering
            labels = [f"پلن {chr(65 + i)}" for i in range(len(items))]
            label_map = {labels[i]: items[i][0] for i in range(len(items))}
            prov_to_label = {p: lbl for lbl, p in label_map.items()}
            labeled_drafts = {labels[i]: items[i][1] for i in range(len(items))}
            labeled_crit = {f"نقد روی {prov_to_label[p]}": c
                            for p, c in critiques.items() if p in prov_to_label}
            bias = "anonymized_peer"

        logger.info("judge=%s bias_mode=%s (debaters=%s)", judge_key, bias, debaters)
        prompt = P.build_judge_prompt(gsc_context, brand_context, labeled_drafts, labeled_crit)
        return JudgePlan(judge_key, P.JUDGE_SYSTEM_INSTRUCTION, prompt, bias, label_map)
