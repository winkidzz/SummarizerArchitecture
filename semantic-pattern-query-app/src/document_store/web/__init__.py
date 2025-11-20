"""
Web search integration module.

Provides web search capabilities with multiple providers:
- DuckDuckGo (free, privacy-focused)
- Tavily (future: specialized for RAG)

This module follows the same provider pattern as the embedders,
allowing multiple providers to be loaded simultaneously and
selected at runtime.
"""

from .providers import (
    WebSearchProvider,
    WebSearchResult,
    DuckDuckGoProvider,
    TrafilaturaProvider,
    WebSearchConfig
)

__all__ = [
    'WebSearchProvider',
    'WebSearchResult',
    'DuckDuckGoProvider',
    'TrafilaturaProvider',
    'WebSearchConfig'
]
