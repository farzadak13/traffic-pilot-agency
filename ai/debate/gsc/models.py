"""Typed GSC primitives shared by every strategy."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class GSCRow:
    term: str
    clicks: int
    impressions: int
    ctr: float        # 0..1
    position: float

    @classmethod
    def from_api(cls, row: Dict[str, Any]) -> "GSCRow":
        keys = row.get("keys") or []
        return cls(
            term=keys[0] if keys else "-",
            clicks=int(row.get("clicks", 0) or 0),
            impressions=int(row.get("impressions", 0) or 0),
            ctr=float(row.get("ctr", 0) or 0),
            position=round(float(row.get("position", 0) or 0), 1),
        )


@dataclass
class Insight:
    """One actionable finding produced by a strategy."""
    strategy: str
    term: str
    detail: str
    metrics: Dict[str, Any] = field(default_factory=dict)


def to_rows(raw: List[Dict[str, Any]]) -> List[GSCRow]:
    return [GSCRow.from_api(r) for r in (raw or [])]
