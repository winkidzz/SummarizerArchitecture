"""
Structured output service using LLM with schema-based generation.

Provides LLM-driven structured output generation with support for:
- Google Gemini (native structured output)
- Ollama (JSON mode)
- Dynamic schema selection
- Validation and format conversion
"""

import os
import json
from typing import Dict, Any, Optional, Literal, Type
from pydantic import BaseModel

from .schemas import SchemaRegistry, TableSchema, ListSchema, ComparisonSchema
from .converters import FormatConverter
from .validators import OutputValidator, ValidationResult


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
        api_key: Optional[str] = None
    ):
        """
        Initialize the structured output service.

        Args:
            model_name: LLM model to use (if None, uses env vars)
            use_ollama: Whether to use Ollama instead of Gemini
            api_key: API key for Gemini (if None, uses env vars)
        """
        self.use_ollama = use_ollama

        if use_ollama:
            # Ollama configuration
            self.model_name = model_name or os.getenv("OLLAMA_MODEL", "qwen3:14b")
            self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            self._init_ollama()
        else:
            # Gemini configuration
            self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
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

            # Validate the data with Pydantic
            validated_data = schema_class.model_validate(structured_json)
            validated_dict = validated_data.model_dump()

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

    def _generate_with_gemini(
        self,
        content: str,
        query: str,
        schema_class: Type[BaseModel],
        schema_name: str
    ) -> Dict[str, Any]:
        """
        Generate structured output using Google Gemini with native schema support.

        Args:
            content: Source content
            query: User query
            schema_class: Pydantic model class
            schema_name: Schema name for context

        Returns:
            Structured JSON data
        """
        # Create model with response schema
        model = self.genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=schema_class
            )
        )

        # Create prompt
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
        Generate structured output using Ollama with JSON mode.

        Args:
            content: Source content
            query: User query
            schema_class: Pydantic model class
            schema_name: Schema name for context

        Returns:
            Structured JSON data
        """
        # Get JSON schema from Pydantic model
        json_schema = schema_class.model_json_schema()

        # Create prompt with schema instructions
        prompt = self._build_extraction_prompt(content, query, schema_name)
        prompt += f"\n\nYou MUST respond with valid JSON matching this schema:\n{json.dumps(json_schema, indent=2)}"

        # Generate response with JSON mode
        response = self.ollama_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a data extraction assistant. Extract structured data from documents and return it as valid JSON matching the provided schema. Do not add any explanatory text, only return the JSON."
                },
                {
                    "role": "user",
                    "content": prompt
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
