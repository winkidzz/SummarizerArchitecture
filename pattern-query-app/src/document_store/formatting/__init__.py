"""
Formatting module for structured output generation.

This module provides tools for LLM-driven structured output generation,
allowing the LLM to decide when to generate structured data (JSON, CSV, tables)
vs free-form text responses.

Features:
- Two-step schema generation and data extraction
- Schema caching for performance optimization
- Batch processing for multiple documents
- Multiple output formats (JSON, CSV, Markdown, etc.)
"""

from .structured_output import StructuredOutputService, create_service
from .schemas import SchemaRegistry, TableSchema, ListSchema, ComparisonSchema
from .converters import FormatConverter
from .validators import OutputValidator
from .schema_cache import SchemaCache

__all__ = [
    'StructuredOutputService',
    'create_service',
    'SchemaRegistry',
    'TableSchema',
    'ListSchema',
    'ComparisonSchema',
    'FormatConverter',
    'OutputValidator',
    'SchemaCache',
]
