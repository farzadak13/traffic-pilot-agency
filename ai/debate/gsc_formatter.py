"""DEPRECATED — kept for back-compat. Use ai.debate.gsc.GSCAnalyzer instead."""
from __future__ import annotations
from typing import Any, Dict, List
from ai.debate.gsc.analyzer import GSCAnalyzer


def format_gsc_context(rows: List[Dict[str, Any]], limit: int = 30) -> str:
    return GSCAnalyzer(table_limit=limit).render(rows)
