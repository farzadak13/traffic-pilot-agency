"""DEPRECATED — kept for back-compat. Use ai.debate.context.BrandContext instead."""
from __future__ import annotations
from typing import Any, Dict
from ai.debate.context.brand import BrandContext


def build_brand_context(data: Dict[str, Any]) -> str:
    return BrandContext.from_form(data).render()
