"""
Formatting module for structured output generation.

This module provides tools for LLM-driven structured output generation,
allowing the LLM to decide when to generate structured data (JSON, CSV, tables)
vs free-form text responses.
"""

from .structured_output import StructuredOutputService, create_service
from .schemas import SchemaRegistry, TableSchema, ListSchema, ComparisonSchema
from .converters import FormatConverter
from .validators import OutputValidator

__all__ = [
    'StructuredOutputService',
    'create_service',
    'SchemaRegistry',
    'TableSchema',
    'ListSchema',
    'ComparisonSchema',
    'FormatConverter',
    'OutputValidator',
]
