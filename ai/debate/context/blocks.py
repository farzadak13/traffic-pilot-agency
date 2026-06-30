"""
ContextBlock protocol — the extension seam for future context sources.

Today: brand fields. Tomorrow: drop in `RetrievedDocsBlock` (RAG),
`ConversationMemoryBlock` (Memory), or `SerpAnalysisBlock` (tools) without
changing BrandContext or the orchestrator. Anything with `.title()` + `.render()`
can be appended to `BrandContext.extra_blocks`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@runtime_checkable
class ContextBlock(Protocol):
    def title(self) -> str: ...
    def render(self) -> str: ...


@dataclass
class TextBlock:
    """Generic ready-made block; handy for RAG/Memory injection."""
    _title: str
    body: str

    def title(self) -> str:
        return self._title

    def render(self) -> str:
        return self.body.strip()
