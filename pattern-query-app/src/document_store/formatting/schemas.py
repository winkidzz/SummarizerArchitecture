"""
Pydantic schema definitions for structured output.

Simplified schemas compatible with Google Gemini's structured output.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


# ============================================================================
# Base Schemas
# ============================================================================

class TableSchema(BaseModel):
    """Schema for tabular data extracted from documents."""
    table_name: str = Field(description="Name/title of the table")
    description: Optional[str] = Field(description="Brief description of table content")
    columns: List[str] = Field(description="Column names in order")
    rows: List[Dict[str, Any]] = Field(description="Table rows as list of dictionaries")
    total_rows: int = Field(description="Total number of rows")
    source_document: Optional[str] = Field(description="Source document identifier")


class ListSchema(BaseModel):
    """Schema for list/catalog data."""
    list_name: str = Field(description="Name of the list")
    description: Optional[str] = Field(description="Brief description")
    items: List[Dict[str, Any]] = Field(description="List items with attributes")
    total_items: int = Field(description="Total number of items")
    categories: Optional[List[str]] = Field(description="Categories present in the list")


class ComparisonSchema(BaseModel):
    """Schema for comparison matrices."""
    comparison_name: str = Field(description="Name of the comparison")
    description: Optional[str] = Field(description="What is being compared")
    entities: List[str] = Field(description="Entities being compared (e.g., vendors, techniques)")
    dimensions: List[str] = Field(description="Comparison dimensions/criteria")
    matrix: List[Dict[str, Any]] = Field(description="Comparison matrix data")
    summary: Optional[str] = Field(description="Brief summary of key differences")


# ============================================================================
# Specialized Schemas
# ============================================================================

class TechniqueRow(BaseModel):
    """Specific schema for AI development techniques."""
    phase: str = Field(description="Development phase")
    category: str = Field(description="Technique category")
    technique: str = Field(description="Technique name")
    description: str = Field(description="Technique description")
    process_framework: Optional[str] = Field(description="Process framework")
    usage: Optional[str] = Field(description="Usage in architecture")
    lifecycle_steps: Optional[str] = Field(description="Lifecycle steps")


class TechniquesCatalog(BaseModel):
    """Complete catalog of AI development techniques."""
    catalog_name: str = Field(description="Catalog name")
    total_techniques: int = Field(description="Total number of techniques")
    techniques: List[TechniqueRow] = Field(description="List of techniques")
    phases: List[str] = Field(description="Unique phases present")
    categories: List[str] = Field(description="Unique categories present")


class PatternSummary(BaseModel):
    """Summary of a RAG pattern."""
    pattern_name: str = Field(description="Name of the pattern")
    complexity: Literal["Low", "Medium", "High"] = Field(description="Implementation complexity")
    use_cases: List[str] = Field(description="Recommended use cases")
    benefits: List[str] = Field(description="Key benefits")
    limitations: List[str] = Field(description="Known limitations")
    vendors_supported: List[str] = Field(description="Vendors that support this pattern")
    estimated_improvement: Optional[str] = Field(description="Performance improvement estimate")


class VendorComparison(BaseModel):
    """Vendor feature comparison."""
    vendor_name: str = Field(description="Vendor name")
    features: Dict[str, Any] = Field(description="Feature availability and details")
    pricing_model: Optional[str] = Field(description="Pricing model")
    best_for: List[str] = Field(description="Best use cases")
    limitations: List[str] = Field(description="Known limitations")


# ============================================================================
# Schema Registry
# ============================================================================

class SchemaRegistry:
    """
    Registry of available schemas for structured output.

    The LLM can query this registry to find appropriate schemas
    based on the type of data being extracted.
    """

    # Map schema names to Pydantic models
    SCHEMAS = {
        # Generic schemas
        "table": TableSchema,
        "list": ListSchema,
        "comparison": ComparisonSchema,

        # Specialized schemas
        "techniques_catalog": TechniquesCatalog,
        "pattern_summary": PatternSummary,
        "vendor_comparison": VendorComparison,
    }

    # Schema descriptions for LLM to understand when to use each
    SCHEMA_DESCRIPTIONS = {
        "table": "Generic table with rows and columns. Use for any tabular data.",
        "list": "Generic list/catalog. Use for collections of items with attributes.",
        "comparison": "Comparison matrix. Use when comparing multiple entities across dimensions.",
        "techniques_catalog": "Specialized schema for AI development techniques catalog.",
        "pattern_summary": "Specialized schema for RAG pattern summaries.",
        "vendor_comparison": "Specialized schema for comparing cloud AI vendors.",
    }

    @classmethod
    def get_schema(cls, schema_name: str) -> Optional[type[BaseModel]]:
        """Get a schema by name."""
        return cls.SCHEMAS.get(schema_name)

    @classmethod
    def get_schema_description(cls, schema_name: str) -> Optional[str]:
        """Get description of when to use a schema."""
        return cls.SCHEMA_DESCRIPTIONS.get(schema_name)

    @classmethod
    def list_schemas(cls) -> Dict[str, str]:
        """List all available schemas with descriptions."""
        return cls.SCHEMA_DESCRIPTIONS

    @classmethod
    def infer_schema(cls, content_type: str, query: str) -> str:
        """
        Infer the most appropriate schema based on content type and query.

        Args:
            content_type: Type of content (e.g., "techniques", "patterns", "vendors")
            query: User's query string

        Returns:
            Schema name to use
        """
        # Check for specialized schemas first
        if "technique" in content_type.lower() or "technique" in query.lower():
            return "techniques_catalog"
        elif "pattern" in content_type.lower() and ("summary" in query.lower() or "describe" in query.lower()):
            return "pattern_summary"
        elif "vendor" in content_type.lower() or "compare" in query.lower():
            if "compare" in query.lower():
                return "comparison"
            return "vendor_comparison"

        # Fall back to generic schemas based on query intent
        if "compare" in query.lower() or "vs" in query.lower():
            return "comparison"
        elif "list" in query.lower() or "catalog" in query.lower():
            return "list"
        else:
            return "table"  # Default to table for most structured data

    @classmethod
    def get_schema_json_schema(cls, schema_name: str) -> Optional[Dict[str, Any]]:
        """Get JSON schema for a given schema name (for LLM structured output)."""
        schema_class = cls.get_schema(schema_name)
        if schema_class:
            return schema_class.model_json_schema()
        return None
