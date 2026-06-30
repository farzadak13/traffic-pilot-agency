"""
GSCAnalyzer — composes selected strategies into a single model-ready context.

The orchestrator depends only on `render()`. Choosing/adding strategies never
touches the orchestrator (OCP). Strategies that need period-over-period data
are skipped automatically when `previous_rows` is absent.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ai.debate.gsc.models import GSCRow, Insight, to_rows
from ai.debate.gsc.strategies import GSCStrategy, all_strategy_keys, get_strategy

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    rows: List[GSCRow]
    insights: Dict[str, List[Insight]] = field(default_factory=dict)


class GSCAnalyzer:
    def __init__(self, strategy_keys: Optional[List[str]] = None,
                 table_limit: int = 30) -> None:
        keys = strategy_keys if strategy_keys is not None else all_strategy_keys()
        self.strategies: List[GSCStrategy] = [get_strategy(k) for k in keys]
        self.table_limit = table_limit

    def analyze(self, raw_rows: List[Dict[str, Any]],
                previous_raw: Optional[List[Dict[str, Any]]] = None) -> AnalysisResult:
        rows = to_rows(raw_rows)
        previous = {r.term: r for r in to_rows(previous_raw)} if previous_raw else None
        insights: Dict[str, List[Insight]] = {}
        for strat in self.strategies:
            try:
                found = strat.find(rows, previous)
            except Exception as exc:  # one bad strategy must not break analysis
                logger.error("GSC strategy '%s' failed: %s", strat.key, exc)
                found = []
            if found:
                insights[strat.title] = found
        return AnalysisResult(rows=rows, insights=insights)

    def render(self, raw_rows: List[Dict[str, Any]],
               previous_raw: Optional[List[Dict[str, Any]]] = None) -> str:
        if not raw_rows:
            return ("داده‌های Search Console در دسترس نیست. "
                    "تحلیل را بر اساس دانش حوزه و نام برند انجام بده.")
        res = self.analyze(raw_rows, previous_raw)
        out: List[str] = ["داده‌های Google Search Console (Top queries):",
                          "| کوئری | کلیک | نمایش | CTR% | پوزیشن |",
                          "|---|---|---|---|---|"]
        for r in res.rows[: self.table_limit]:
            out.append(f"| {r.term} | {r.clicks} | {r.impressions} | {round(r.ctr*100,2)} | {r.position} |")
        for title, items in res.insights.items():
            out.append(f"\n{title}:")
            out += [f"- «{i.term}» — {i.detail}" for i in items]
        return "\n".join(out)
