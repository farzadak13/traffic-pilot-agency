"""
Pluggable GSC analysis strategies (Strategy pattern + registry).

Add a new lens (e.g. "cannibalization") by subclassing `GSCStrategy` and
decorating with `@register_strategy`. The analyzer and orchestrator are
untouched — pure OCP.

Strategies that need period-over-period data (Declining, NewOpportunities)
receive an optional `previous` map {term -> GSCRow}; they no-op without it.
"""
from __future__ import annotations

import abc
import logging
from typing import Dict, List, Optional, Type

from ai.debate.gsc.models import GSCRow, Insight

logger = logging.getLogger(__name__)

_STRATEGIES: Dict[str, Type["GSCStrategy"]] = {}


def register_strategy(cls: Type["GSCStrategy"]) -> Type["GSCStrategy"]:
    _STRATEGIES[cls.key] = cls
    return cls


def get_strategy(key: str) -> "GSCStrategy":
    if key not in _STRATEGIES:
        raise KeyError(f"unknown GSC strategy '{key}'. registered: {list(_STRATEGIES)}")
    return _STRATEGIES[key]()


def all_strategy_keys() -> List[str]:
    return list(_STRATEGIES.keys())


class GSCStrategy(abc.ABC):
    key: str = "base"
    title: str = "Base"
    needs_previous: bool = False
    max_items: int = 10

    @abc.abstractmethod
    def find(self, rows: List[GSCRow], previous: Optional[Dict[str, GSCRow]] = None) -> List[Insight]:
        raise NotImplementedError


@register_strategy
class QuickWins(GSCStrategy):
    key = "quick_wins"
    title = "فرصت‌های Quick-win (پوزیشن ۴ تا ۲۰)"

    def find(self, rows, previous=None):
        cand = sorted((r for r in rows if 4 <= r.position <= 20),
                      key=lambda r: r.impressions, reverse=True)[: self.max_items]
        return [Insight(self.key, r.term,
                        f"پوزیشن {r.position} با {r.impressions} نمایش — با بهینه‌سازی به صفحه ۱ برسد",
                        {"position": r.position, "impressions": r.impressions, "ctr": round(r.ctr*100, 2)})
                for r in cand]


@register_strategy
class LowCTR(GSCStrategy):
    key = "low_ctr"
    title = "CTR پایین با نمایش بالا (بهینه‌سازی Title/Meta)"
    min_impressions = 200
    ctr_threshold = 0.02  # 2%

    def find(self, rows, previous=None):
        cand = sorted((r for r in rows if r.impressions >= self.min_impressions and r.ctr < self.ctr_threshold),
                      key=lambda r: r.impressions, reverse=True)[: self.max_items]
        return [Insight(self.key, r.term,
                        f"CTR فقط {round(r.ctr*100,2)}% با {r.impressions} نمایش — Title/Meta بازنویسی شود",
                        {"ctr": round(r.ctr*100, 2), "impressions": r.impressions, "position": r.position})
                for r in cand]


@register_strategy
class HighImpressions(GSCStrategy):
    key = "high_impressions"
    title = "بیشترین نمایش (تقاضای بالا)"

    def find(self, rows, previous=None):
        cand = sorted(rows, key=lambda r: r.impressions, reverse=True)[: self.max_items]
        return [Insight(self.key, r.term,
                        f"{r.impressions} نمایش، پوزیشن {r.position} — پتانسیل ترافیک بالا",
                        {"impressions": r.impressions, "position": r.position})
                for r in cand]


@register_strategy
class DecliningQueries(GSCStrategy):
    key = "declining"
    title = "کوئری‌های در حال افت (نیازمند به‌روزرسانی)"
    needs_previous = True
    pos_drop = 1.5          # position worsened by >= 1.5
    clicks_drop_pct = 0.25  # or clicks fell >= 25%

    def find(self, rows, previous=None):
        if not previous:
            return []
        out: List[Insight] = []
        for r in rows:
            prev = previous.get(r.term)
            if not prev:
                continue
            pos_worse = r.position - prev.position >= self.pos_drop
            clicks_worse = prev.clicks > 0 and (prev.clicks - r.clicks) / prev.clicks >= self.clicks_drop_pct
            if pos_worse or clicks_worse:
                out.append(Insight(self.key, r.term,
                    f"افت: پوزیشن {prev.position}→{r.position}، کلیک {prev.clicks}→{r.clicks}",
                    {"position_from": prev.position, "position_to": r.position,
                     "clicks_from": prev.clicks, "clicks_to": r.clicks}))
        out.sort(key=lambda i: i.metrics.get("clicks_from", 0), reverse=True)
        return out[: self.max_items]


@register_strategy
class NewOpportunities(GSCStrategy):
    key = "new_opportunities"
    title = "کوئری‌های نوظهور (در دوره قبل نبودند)"
    needs_previous = True
    min_impressions = 50

    def find(self, rows, previous=None):
        if not previous:
            return []
        cand = sorted((r for r in rows
                       if r.term not in previous and r.impressions >= self.min_impressions),
                      key=lambda r: r.impressions, reverse=True)[: self.max_items]
        return [Insight(self.key, r.term,
                        f"جدید: {r.impressions} نمایش، پوزیشن {r.position} — محتوای اختصاصی بسازید",
                        {"impressions": r.impressions, "position": r.position})
                for r in cand]
