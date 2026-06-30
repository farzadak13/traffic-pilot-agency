"""
Rich, extensible brand/SEO context.

Only populated fields are rendered, so callers can fill in as much or as
little as they have. `extra_blocks` is the forward-compat hook for RAG,
Memory, SERP tools, etc. (see context/blocks.py).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ai.debate.context.blocks import ContextBlock, TextBlock


@dataclass
class BrandContext:
    # ── core identity ───────────────────────────────────────────────
    brand_name: str = "نامشخص"
    site_url: Optional[str] = None
    niche: Optional[str] = None
    cms_platform: Optional[str] = None
    domain_authority: Optional[Any] = None
    monthly_traffic: Optional[Any] = None
    # ── strategic enrichment (all optional, all extensible) ─────────
    search_intent: Optional[str] = None
    target_persona: Optional[str] = None
    business_goals: Optional[str] = None
    conversion_goals: Optional[str] = None
    competitor_context: Optional[str] = None
    internal_linking_context: Optional[str] = None
    existing_content_summary: Optional[str] = None
    # ── future sources (RAG / Memory / tools) ───────────────────────
    extra_blocks: List[ContextBlock] = field(default_factory=list)

    # ordered (label, value) for deterministic rendering
    _CORE = [
        ("برند", "brand_name"), ("دامنه/سایت", "site_url"),
        ("حوزه فعالیت", "niche"), ("CMS", "cms_platform"),
        ("Domain Authority", "domain_authority"), ("ترافیک ماهانه فعلی", "monthly_traffic"),
    ]
    _STRATEGIC = [
        ("Search Intent", "search_intent"), ("پرسونای هدف", "target_persona"),
        ("اهداف کسب‌وکار", "business_goals"), ("اهداف تبدیل (Conversion)", "conversion_goals"),
        ("زمینه رقبا", "competitor_context"),
        ("ساختار لینک‌سازی داخلی", "internal_linking_context"),
        ("خلاصه محتوای موجود", "existing_content_summary"),
    ]

    def add_block(self, block: ContextBlock) -> "BrandContext":
        self.extra_blocks.append(block)
        return self

    def add_text(self, title: str, body: str) -> "BrandContext":
        return self.add_block(TextBlock(title, body))

    def _emit(self, pairs) -> List[str]:
        lines = []
        for label, attr in pairs:
            val = getattr(self, attr)
            if val not in (None, "", "-"):
                lines.append(f"- {label}: {val}")
        return lines

    def render(self) -> str:
        sections: List[str] = []
        core = self._emit(self._CORE)
        if core:
            sections.append("## اطلاعات برند\n" + "\n".join(core))
        strat = self._emit(self._STRATEGIC)
        if strat:
            sections.append("## زمینه استراتژیک\n" + "\n".join(strat))
        for blk in self.extra_blocks:
            body = (blk.render() or "").strip()
            if body:
                sections.append(f"## {blk.title()}\n{body}")
        return "\n\n".join(sections) if sections else f"- برند: {self.brand_name}"

    @classmethod
    def from_form(cls, data: Dict[str, Any]) -> "BrandContext":
        """Build from app.py form dict; unknown keys are ignored."""
        known = {f for f in cls.__dataclass_fields__ if f != "extra_blocks"}
        return cls(**{k: v for k, v in (data or {}).items() if k in known})
