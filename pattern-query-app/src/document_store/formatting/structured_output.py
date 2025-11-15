"""
Structured output service using LLM with schema-based generation.

Provides LLM-driven structured output generation with support for:
- Google Gemini (native structured output)
- Ollama (JSON mode)
- Dynamic schema selection
- Validation and format conversion
- Schema caching for performance optimization
"""

import os
import json
from typing import Dict, Any, Optional, Literal, Type, List
from pydantic import BaseModel

from .schemas import SchemaRegistry, TableSchema, ListSchema, ComparisonSchema
from .converters import FormatConverter
from .validators import OutputValidator, ValidationResult
from .schema_cache import SchemaCache


class StructuredOutputService:
    """
    Service for generating structured output using LLM with schema validation.

    This service allows the LLM to generate structured data (JSON) that conforms
    to predefined schemas, then convert to various formats (CSV, Markdown, etc.).
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        use_ollama: bool = False,
        api_key: Optional[str] = None,
        enable_caching: bool = True,
        cache_max_size: int = 100,
        cache_ttl: int = 3600
    ):
        """
        Initialize the structured output service.

        Args:
            model_name: LLM model to use (if None, uses env vars)
            use_ollama: Whether to use Ollama instead of Gemini
            api_key: API key for Gemini (if None, uses env vars)
            enable_caching: Enable schema caching for performance
            cache_max_size: Maximum number of schemas to cache
            cache_ttl: Time-to-live for cached schemas in seconds
        """
        self.use_ollama = use_ollama

        # Initialize schema cache
        self.schema_cache = SchemaCache(
            max_size=cache_max_size,
            ttl_seconds=cache_ttl
        ) if enable_caching else None

        if use_ollama:
            # Ollama configuration
            self.model_name = model_name or os.getenv("OLLAMA_MODEL", "qwen3:14b")
            self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            self._init_ollama()
        else:
            # Gemini configuration
            self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            self.api_key = api_key or os.getenv("GEMINI_API_KEY")
            self._init_gemini()

    def _init_gemini(self):
        """Initialize Google Gemini client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.genai = genai
            self.model = None  # Will be created per request with specific schema
        except ImportError:
            raise ImportError(
                "google-generativeai package required for Gemini. "
                "Install with: pip install google-generativeai"
            )

    def _init_ollama(self):
        """Initialize Ollama client."""
        try:
            from openai import OpenAI
            self.ollama_client = OpenAI(
                base_url=self.base_url,
                api_key="ollama"  # Ollama doesn't need real API key
            )
        except ImportError:
            raise ImportError(
                "openai package required for Ollama. "
                "Install with: pip install openai"
            )

    def generate_structured_output(
        self,
        content: str,
        query: str,
        schema_name: str,
        output_format: Literal["json", "csv", "tsv", "markdown", "html", "yaml"] = "json",
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Generate structured output from content using LLM with schema.

        Args:
            content: Source content to extract structured data from
            query: User's query (helps LLM understand intent)
            schema_name: Name of schema to use (from SchemaRegistry)
            output_format: Desired output format
            validate: Whether to validate output

        Returns:
            Dictionary with:
                - success: bool
                - data: Structured data (format depends on output_format)
                - format: Output format used
                - schema_used: Schema name
                - validation: ValidationResult (if validate=True)
                - metadata: Additional metadata
        """
        # Get schema
        schema_class = SchemaRegistry.get_schema(schema_name)
        if not schema_class:
            return {
                "success": False,
                "error": f"Unknown schema: {schema_name}",
                "available_schemas": list(SchemaRegistry.list_schemas().keys())
            }

        # Generate structured output using LLM
        try:
            if self.use_ollama:
                structured_json = self._generate_with_ollama(
                    content=content,
                    query=query,
                    schema_class=schema_class,
                    schema_name=schema_name
                )
            else:
                structured_json = self._generate_with_gemini(
                    content=content,
                    query=query,
                    schema_class=schema_class,
                    schema_name=schema_name
                )

            # Validate against schema
            validation_result = None
            validated_dict = None

            if validate:
                validation_result = OutputValidator.validate_json(
                    json_data=structured_json,
                    pydantic_model=schema_class,
                    check_completeness=True
                )

                if not validation_result.is_valid:
                    return {
                        "success": False,
                        "error": "Schema validation failed",
                        "validation": validation_result.__dict__,
                        "raw_output": structured_json
                    }

                # Validate the data with Pydantic (only when validate=True)
                validated_data = schema_class.model_validate(structured_json)
                validated_dict = validated_data.model_dump()
            else:
                # Skip validation - use raw JSON from LLM
                # Handle case where LLM returns list directly instead of schema object
                if isinstance(structured_json, list):
                    # Wrap list in TableSchema-like structure
                    validated_dict = {"rows": structured_json}
                else:
                    validated_dict = structured_json

            # Convert to requested format
            if output_format != "json":
                formatted_output = self._convert_to_format(
                    validated_dict,
                    schema_name,
                    output_format
                )
            else:
                formatted_output = validated_dict

            return {
                "success": True,
                "data": formatted_output,
                "format": output_format,
                "schema_used": schema_name,
                "validation": validation_result.__dict__ if validation_result else None,
                "metadata": {
                    "model": self.model_name,
                    "use_ollama": self.use_ollama,
                    "schema_class": schema_class.__name__
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "schema_used": schema_name
            }

    def generate_schema_from_content(
        self,
        content: str,
        query: str,
        schema_type: str,
        use_cache: bool = True,
        content_preview_size: int = 2000
    ) -> Dict[str, Any]:
        """
        Generate a dynamic JSON schema by analyzing document content.

        This is Step 1 of the two-step extraction process. The generated schema
        can be reused across multiple similar documents for efficiency.

        Args:
            content: Document content to analyze
            query: User query providing context for schema design
            schema_type: Type of schema (table, list, comparison, etc.)
            use_cache: Whether to use cached schemas (default: True)
            content_preview_size: Number of characters to analyze (default: 2000)

        Returns:
            Dictionary with:
                - success: bool
                - schema: Generated JSON schema dict
                - schema_type: Type of schema generated
                - from_cache: Whether result came from cache
                - metadata: Additional info (model, content_analyzed, etc.)
        """
        # Check cache first
        if use_cache and self.schema_cache:
            cache_key = self.schema_cache.generate_key(
                content=content,
                schema_type=schema_type,
                query=query,
                sample_size=content_preview_size
            )
            cached_schema = self.schema_cache.get(cache_key)

            if cached_schema:
                return {
                    "success": True,
                    "schema": cached_schema,
                    "schema_type": schema_type,
                    "from_cache": True,
                    "metadata": {
                        "cache_key": cache_key,
                        "model": self.model_name
                    }
                }

        # Generate schema using LLM
        try:
            content_sample = content[:content_preview_size]

            if self.use_ollama:
                generated_schema = self._generate_schema_internal(
                    content_sample=content_sample,
                    query=query,
                    schema_type=schema_type,
                    fallback_schema=None
                )
            else:
                # For Gemini, use predefined schema structure
                schema_class = SchemaRegistry.get_schema(schema_type)
                if schema_class:
                    generated_schema = schema_class.model_json_schema()
                else:
                    return {
                        "success": False,
                        "error": f"Unknown schema type: {schema_type}"
                    }

            # Cache the generated schema
            if use_cache and self.schema_cache:
                cache_key = self.schema_cache.generate_key(
                    content=content,
                    schema_type=schema_type,
                    query=query,
                    sample_size=content_preview_size
                )
                self.schema_cache.set(cache_key, generated_schema)

            return {
                "success": True,
                "schema": generated_schema,
                "schema_type": schema_type,
                "from_cache": False,
                "metadata": {
                    "model": self.model_name,
                    "use_ollama": self.use_ollama,
                    "content_analyzed": len(content_sample)
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "schema_type": schema_type
            }

    def extract_data_with_schema(
        self,
        content: str,
        schema: Dict[str, Any],
        query: Optional[str] = None,
        validate: bool = True,
        output_format: Literal["json", "csv", "tsv", "markdown", "html", "yaml"] = "json"
    ) -> Dict[str, Any]:
        """
        Extract structured data from content using a provided schema.

        This is Step 2 of the two-step extraction process. Use this with a schema
        from generate_schema_from_content() or provide your own custom schema.

        Args:
            content: Document content to extract data from
            schema: JSON schema to use for extraction
            query: Optional query for context
            validate: Whether to validate extracted data
            output_format: Desired output format (default: json)

        Returns:
            Dictionary with:
                - success: bool
                - data: Extracted data (format depends on output_format)
                - format: Output format used
                - schema_used: Schema that was used
                - validation: ValidationResult (if validate=True)
                - metadata: Additional info
        """
        try:
            # Extract data using LLM
            if self.use_ollama:
                extracted_data = self._extract_data_internal(
                    content=content,
                    schema=schema,
                    query=query
                )
            else:
                # For Gemini, use the schema directly with native support
                # This requires converting dict schema back to Pydantic class
                # For now, fall back to Ollama behavior
                extracted_data = self._extract_data_internal(
                    content=content,
                    schema=schema,
                    query=query
                )

            # Validate if requested
            validation_result = None
            if validate:
                # Basic validation - check if data matches schema structure
                validation_result = OutputValidator.validate_json(
                    json_data=extracted_data,
                    pydantic_model=None,  # Can't validate without Pydantic model
                    check_completeness=False
                )

            # Convert to requested format
            if output_format != "json":
                formatted_output = FormatConverter.to_format(
                    data=extracted_data,
                    format_type=output_format
                )
            else:
                formatted_output = extracted_data

            return {
                "success": True,
                "data": formatted_output,
                "format": output_format,
                "schema_used": schema,
                "validation": validation_result.__dict__ if validation_result else None,
                "metadata": {
                    "model": self.model_name,
                    "use_ollama": self.use_ollama
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    def extract_batch(
        self,
        documents: List[str],
        query: str,
        schema_type: str,
        output_format: Literal["json", "csv", "tsv", "markdown", "html", "yaml"] = "json",
        validate: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Extract structured data from multiple documents using schema reuse.

        Generates schema once from the first document, then applies it to all
        documents. This is ~50% more efficient than calling generate_structured_output()
        for each document individually.

        Args:
            documents: List of document contents to process
            query: User query for context
            schema_type: Type of schema to use
            output_format: Desired output format
            validate: Whether to validate extracted data

        Returns:
            List of result dictionaries (one per document)
        """
        if not documents:
            return []

        # Step 1: Generate schema from first document (with caching)
        schema_result = self.generate_schema_from_content(
            content=documents[0],
            query=query,
            schema_type=schema_type,
            use_cache=True
        )

        if not schema_result["success"]:
            # If schema generation failed, return error for all documents
            return [schema_result] * len(documents)

        generated_schema = schema_result["schema"]

        # Step 2: Extract from all documents using the same schema
        results = []
        for i, doc in enumerate(documents):
            result = self.extract_data_with_schema(
                content=doc,
                schema=generated_schema,
                query=query,
                validate=validate,
                output_format=output_format
            )

            # Add batch metadata
            if result.get("metadata"):
                result["metadata"]["batch_index"] = i
                result["metadata"]["batch_size"] = len(documents)
                result["metadata"]["schema_from_cache"] = schema_result["from_cache"]

            results.append(result)

        return results

    def _generate_with_gemini(
        self,
        content: str,
        query: str,
        schema_class: Type[BaseModel],
        schema_name: str
    ) -> Dict[str, Any]:
        """
        Generate structured output using Google Gemini with JSON mode.

        Note: We use JSON mode without a fixed schema to allow Gemini to infer
        the table structure from the content (supporting dynamic columns).

        Args:
            content: Source content
            query: User query
            schema_class: Pydantic model class (for reference, not enforced)
            schema_name: Schema name for context

        Returns:
            Structured JSON data
        """
        # Use JSON mode WITHOUT fixed schema to allow dynamic structure
        # This lets Gemini infer table columns from the content
        model = self.genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )

        # Create prompt that guides Gemini to generate the right structure
        prompt = self._build_extraction_prompt(content, query, schema_name)

        # Generate response
        response = model.generate_content(prompt)

        # Parse JSON response
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # If response is not valid JSON, try to extract it
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text.strip())

    def _generate_with_ollama(
        self,
        content: str,
        query: str,
        schema_class: Type[BaseModel],
        schema_name: str
    ) -> Dict[str, Any]:
        """
        Generate structured output using Ollama with JSON mode (two-step process).

        Args:
            content: Source content
            query: User query
            schema_class: Pydantic model class
            schema_name: Schema name for context

        Returns:
            Structured JSON data
        """
        # STEP 1: Generate schema
        generated_schema = self._generate_schema_internal(
            content_sample=content[:2000],
            query=query,
            schema_type=schema_name,
            fallback_schema=schema_class.model_json_schema()
        )

        # STEP 2: Extract data using generated schema
        extracted_data = self._extract_data_internal(
            content=content,
            schema=generated_schema,
            query=query
        )

        return extracted_data

    def _generate_schema_internal(
        self,
        content_sample: str,
        query: str,
        schema_type: str,
        fallback_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Internal method to generate schema using LLM.

        Args:
            content_sample: Sample of content for analysis
            query: User query
            schema_type: Type of schema to generate
            fallback_schema: Fallback schema if generation fails

        Returns:
            Generated JSON schema
        """
        schema_generation_prompt = f"""Analyze the following document and create a JSON schema definition for extracting structured data.

User Query: {query}
Target Schema Type: {schema_type}

Document Content:
{content_sample}

Generate a JSON schema that captures the structure of the data in this document. Include:
- Field names that match the document content
- Field types (string, array, object, etc.)
- Descriptions for each field
- Required fields

Return ONLY the JSON schema definition."""

        schema_response = self.ollama_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a schema design expert. Analyze documents and create appropriate JSON schemas for data extraction."
                },
                {
                    "role": "user",
                    "content": schema_generation_prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        # Parse the generated schema
        generated_schema_text = schema_response.choices[0].message.content
        try:
            return json.loads(generated_schema_text)
        except json.JSONDecodeError:
            # Fallback to predefined schema if available
            if fallback_schema:
                return fallback_schema
            raise

    def _extract_data_internal(
        self,
        content: str,
        schema: Dict[str, Any],
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Internal method to extract data using provided schema.

        Args:
            content: Full document content
            schema: JSON schema to use for extraction
            query: Optional query for context

        Returns:
            Extracted structured data
        """
        extraction_prompt = f"""Extract structured data from the document using the provided schema.

Document Content:
{content}

Schema to follow:
{json.dumps(schema, indent=2)}

IMPORTANT:
- Extract ACTUAL DATA from the document, not the schema definition
- Fill in real values from the document content
- If the document contains a table, extract ALL rows
- Preserve exact values and structure from the document

Return the extracted data as JSON matching the schema structure."""

        # Generate response with JSON mode
        response = self.ollama_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a data extraction assistant. Extract structured data FROM documents using the provided schema. Return actual data values, not schema definitions."
                },
                {
                    "role": "user",
                    "content": extraction_prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1  # Low temperature for consistent extraction
        )

        # Parse response
        response_text = response.choices[0].message.content

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to clean up response
            text = response_text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text.strip())

    def _build_extraction_prompt(
        self,
        content: str,
        query: str,
        schema_name: str
    ) -> str:
        """
        Build prompt for structured data extraction.

        Args:
            content: Source content
            query: User query
            schema_name: Schema being used

        Returns:
            Extraction prompt
        """
        schema_desc = SchemaRegistry.get_schema_description(schema_name)

        prompt = f"""Extract structured data from the following document to answer the user's query.

User Query: {query}

Schema to use: {schema_name}
Schema description: {schema_desc}

Document Content:
{content}

Instructions:
1. Carefully read the entire document
2. Extract ALL relevant data (do not truncate or summarize)
3. Preserve exact values from the document
4. Structure the data according to the schema
5. Ensure completeness - include all rows/items found
6. If a table has multiple rows, include ALL rows
7. Maintain accuracy - do not invent data not present in the document

Return the structured data as JSON matching the schema."""

        return prompt

    def _convert_to_format(
        self,
        validated_data: Dict[str, Any],
        schema_name: str,
        output_format: str
    ) -> str:
        """
        Convert validated JSON to requested format.

        Args:
            validated_data: Validated dictionary from Pydantic
            schema_name: Schema name
            output_format: Target format

        Returns:
            Formatted string
        """
        # Determine schema type
        schema_class = SchemaRegistry.get_schema(schema_name)

        if schema_class == TableSchema or "table" in schema_name:
            return FormatConverter.table_schema_to_format(validated_data, output_format)
        elif schema_class == ListSchema or "list" in schema_name:
            return FormatConverter.list_schema_to_format(validated_data, output_format)
        elif schema_class == ComparisonSchema or "comparison" in schema_name:
            return FormatConverter.comparison_schema_to_format(validated_data, output_format)
        else:
            # Generic conversion - extract rows/items/techniques
            if "rows" in validated_data:
                return FormatConverter.table_schema_to_format(validated_data, output_format)
            elif "items" in validated_data:
                return FormatConverter.list_schema_to_format(validated_data, output_format)
            elif "techniques" in validated_data:
                # Handle TechniquesCatalog
                return FormatConverter.table_schema_to_format(
                    {"rows": validated_data["techniques"]},
                    output_format
                )
            else:
                # Fallback to JSON
                return FormatConverter.to_json(validated_data)

    def infer_and_generate(
        self,
        content: str,
        query: str,
        output_format: str = "json",
        content_type_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Automatically infer schema and generate structured output.

        Args:
            content: Source content
            query: User query
            output_format: Desired output format
            content_type_hint: Optional hint about content type

        Returns:
            Result dictionary (same as generate_structured_output)
        """
        # Infer schema
        content_type = content_type_hint or ""
        schema_name = SchemaRegistry.infer_schema(content_type, query)

        # Generate output
        return self.generate_structured_output(
            content=content,
            query=query,
            schema_name=schema_name,
            output_format=output_format,
            validate=True
        )


def create_service(use_ollama: Optional[bool] = None) -> StructuredOutputService:
    """
    Factory function to create StructuredOutputService with env-based config.

    Args:
        use_ollama: Override for Ollama usage (if None, checks USE_OLLAMA_EVAL env var)

    Returns:
        Configured StructuredOutputService
    """
    if use_ollama is None:
        use_ollama = os.getenv("USE_OLLAMA_EVAL", "false").lower() == "true"

    return StructuredOutputService(use_ollama=use_ollama)
