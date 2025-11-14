"""
Output validators for quality assurance of structured output.

Validates that LLM-generated structured output meets quality standards
including completeness, consistency, and format correctness.
"""

import csv
import io
import json
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, ValidationError
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    message: str
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


class OutputValidator:
    """Validator for structured output quality."""

    @staticmethod
    def validate_csv(
        csv_text: str,
        expected_columns: Optional[List[str]] = None,
        min_rows: int = 0,
        check_consistency: bool = True
    ) -> ValidationResult:
        """
        Validate CSV output format and content.

        Args:
            csv_text: CSV formatted text
            expected_columns: Expected column names (if known)
            min_rows: Minimum expected number of rows
            check_consistency: Check for consistent column counts

        Returns:
            ValidationResult with validation details
        """
        errors = []
        warnings = []
        metadata = {}

        try:
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(csv_text))
            rows = list(csv_reader)

            # Get actual columns
            if not rows:
                errors.append("CSV is empty (no rows)")
                return ValidationResult(
                    is_valid=False,
                    message="CSV validation failed: empty",
                    errors=errors,
                    warnings=warnings,
                    metadata=metadata
                )

            actual_columns = list(rows[0].keys())
            metadata["column_count"] = len(actual_columns)
            metadata["row_count"] = len(rows)
            metadata["columns"] = actual_columns

            # Check expected columns
            if expected_columns:
                if set(actual_columns) != set(expected_columns):
                    missing = set(expected_columns) - set(actual_columns)
                    extra = set(actual_columns) - set(expected_columns)
                    if missing:
                        errors.append(f"Missing expected columns: {missing}")
                    if extra:
                        warnings.append(f"Extra columns found: {extra}")

            # Check minimum rows
            if len(rows) < min_rows:
                errors.append(f"Expected at least {min_rows} rows, got {len(rows)}")

            # Check consistency
            if check_consistency:
                for i, row in enumerate(rows, start=1):
                    if len(row) != len(actual_columns):
                        errors.append(f"Row {i} has inconsistent column count")

                    # Check for empty/None values
                    empty_cells = [k for k, v in row.items() if not v or v.strip() == ""]
                    if empty_cells:
                        warnings.append(f"Row {i} has empty cells: {empty_cells}")

            is_valid = len(errors) == 0
            message = "CSV validation passed" if is_valid else "CSV validation failed"

            return ValidationResult(
                is_valid=is_valid,
                message=message,
                errors=errors,
                warnings=warnings,
                metadata=metadata
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"CSV validation error: {str(e)}",
                errors=[str(e)],
                warnings=warnings,
                metadata=metadata
            )

    @staticmethod
    def validate_json(
        json_data: Any,
        pydantic_model: Optional[Type[BaseModel]] = None,
        check_completeness: bool = True
    ) -> ValidationResult:
        """
        Validate JSON output against schema.

        Args:
            json_data: JSON data (dict, list, etc.)
            pydantic_model: Pydantic model to validate against
            check_completeness: Check for null/empty values

        Returns:
            ValidationResult with validation details
        """
        errors = []
        warnings = []
        metadata = {}

        try:
            # If string, parse it
            if isinstance(json_data, str):
                json_data = json.loads(json_data)

            # Validate against Pydantic model if provided
            if pydantic_model:
                try:
                    validated = pydantic_model.model_validate(json_data)
                    metadata["model_validated"] = True
                    metadata["model_name"] = pydantic_model.__name__

                    # Convert back to dict for further checks
                    json_data = validated.model_dump()

                except ValidationError as e:
                    errors.extend([f"{err['loc']}: {err['msg']}" for err in e.errors()])
                    return ValidationResult(
                        is_valid=False,
                        message="Pydantic validation failed",
                        errors=errors,
                        warnings=warnings,
                        metadata=metadata
                    )

            # Check completeness
            if check_completeness:
                OutputValidator._check_json_completeness(json_data, "", warnings)

            # Add metadata about structure
            metadata["type"] = type(json_data).__name__
            if isinstance(json_data, dict):
                metadata["key_count"] = len(json_data.keys())
                metadata["keys"] = list(json_data.keys())
            elif isinstance(json_data, list):
                metadata["item_count"] = len(json_data)

            is_valid = len(errors) == 0
            message = "JSON validation passed" if is_valid else "JSON validation failed"

            return ValidationResult(
                is_valid=is_valid,
                message=message,
                errors=errors,
                warnings=warnings,
                metadata=metadata
            )

        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid JSON: {str(e)}",
                errors=[str(e)],
                warnings=warnings,
                metadata=metadata
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"JSON validation error: {str(e)}",
                errors=[str(e)],
                warnings=warnings,
                metadata=metadata
            )

    @staticmethod
    def _check_json_completeness(data: Any, path: str, warnings: List[str]) -> None:
        """
        Recursively check JSON structure for null/empty values.

        Args:
            data: Data to check
            path: Current path in the structure
            warnings: List to append warnings to
        """
        if data is None:
            warnings.append(f"Null value at {path or 'root'}")
        elif isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                if value is None or (isinstance(value, str) and value.strip() == ""):
                    warnings.append(f"Empty/null value at {new_path}")
                else:
                    OutputValidator._check_json_completeness(value, new_path, warnings)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_path = f"{path}[{i}]"
                OutputValidator._check_json_completeness(item, new_path, warnings)

    @staticmethod
    def validate_content_completeness(
        source_content: str,
        structured_output: Dict[str, Any],
        expected_items: Optional[List[str]] = None,
        sample_checks: int = 5
    ) -> ValidationResult:
        """
        Validate that structured output contains complete content from source.

        Args:
            source_content: Original source document content
            structured_output: Structured output to validate
            expected_items: List of expected items/keywords
            sample_checks: Number of random samples to verify

        Returns:
            ValidationResult with completeness details
        """
        errors = []
        warnings = []
        metadata = {}

        # Check if expected items are present in output
        if expected_items:
            output_str = json.dumps(structured_output).lower()
            missing_items = []
            for item in expected_items:
                if item.lower() not in output_str:
                    missing_items.append(item)

            if missing_items:
                errors.append(f"Missing expected items: {missing_items}")
            metadata["expected_items_found"] = len(expected_items) - len(missing_items)
            metadata["expected_items_missing"] = len(missing_items)

        # Extract data rows/items from structured output
        rows = []
        if "rows" in structured_output:
            rows = structured_output["rows"]
        elif "items" in structured_output:
            rows = structured_output["items"]
        elif "matrix" in structured_output:
            rows = structured_output["matrix"]
        elif "techniques" in structured_output:
            rows = structured_output["techniques"]

        metadata["extracted_row_count"] = len(rows)

        # Check if rows are substantive (not truncated/summarized)
        if rows:
            # Sample first few rows
            sample_size = min(sample_checks, len(rows))
            for i in range(sample_size):
                row = rows[i]
                # Check if values are suspiciously short (might be summarized)
                for key, value in row.items():
                    if isinstance(value, str) and value:
                        if len(value) < 10 and "..." in value:
                            warnings.append(f"Row {i}, field '{key}' appears truncated: {value}")
                        # Check if value exists in source
                        if len(value) > 5 and value.lower() not in source_content.lower():
                            warnings.append(f"Row {i}, field '{key}' value not found in source: {value[:50]}")

        is_valid = len(errors) == 0
        message = "Content completeness validated" if is_valid else "Content validation failed"

        return ValidationResult(
            is_valid=is_valid,
            message=message,
            errors=errors,
            warnings=warnings,
            metadata=metadata
        )

    @staticmethod
    def validate_table_structure(
        table_data: Dict[str, Any],
        min_rows: int = 0,
        min_columns: int = 0,
        required_columns: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Validate table structure requirements.

        Args:
            table_data: Table data (from TableSchema)
            min_rows: Minimum expected rows
            min_columns: Minimum expected columns
            required_columns: Required column names

        Returns:
            ValidationResult with structure validation
        """
        errors = []
        warnings = []
        metadata = {}

        # Check required fields
        if "columns" not in table_data:
            errors.append("Missing 'columns' field in table data")
        if "rows" not in table_data:
            errors.append("Missing 'rows' field in table data")

        if errors:
            return ValidationResult(
                is_valid=False,
                message="Invalid table structure",
                errors=errors,
                warnings=warnings,
                metadata=metadata
            )

        columns = table_data.get("columns", [])
        rows = table_data.get("rows", [])

        metadata["column_count"] = len(columns)
        metadata["row_count"] = len(rows)
        metadata["columns"] = columns

        # Check minimum requirements
        if len(rows) < min_rows:
            errors.append(f"Expected at least {min_rows} rows, got {len(rows)}")

        if len(columns) < min_columns:
            errors.append(f"Expected at least {min_columns} columns, got {len(columns)}")

        # Check required columns
        if required_columns:
            missing = set(required_columns) - set(columns)
            if missing:
                errors.append(f"Missing required columns: {missing}")

        # Check row consistency
        for i, row in enumerate(rows):
            row_keys = set(row.keys())
            expected_keys = set(columns)
            if row_keys != expected_keys:
                missing = expected_keys - row_keys
                extra = row_keys - expected_keys
                if missing:
                    warnings.append(f"Row {i} missing columns: {missing}")
                if extra:
                    warnings.append(f"Row {i} has extra columns: {extra}")

        is_valid = len(errors) == 0
        message = "Table structure validated" if is_valid else "Table validation failed"

        return ValidationResult(
            is_valid=is_valid,
            message=message,
            errors=errors,
            warnings=warnings,
            metadata=metadata
        )

    @staticmethod
    def validate_format_conversion(
        original_json: Dict[str, Any],
        converted_text: str,
        target_format: str
    ) -> ValidationResult:
        """
        Validate that format conversion preserved data integrity.

        Args:
            original_json: Original JSON data
            converted_text: Converted output text
            target_format: Target format (csv, markdown, etc.)

        Returns:
            ValidationResult with conversion validation
        """
        errors = []
        warnings = []
        metadata = {"target_format": target_format}

        try:
            if target_format.lower() == "csv":
                # Parse CSV and check row count
                csv_reader = csv.DictReader(io.StringIO(converted_text))
                converted_rows = list(csv_reader)

                original_rows = original_json.get("rows", [])
                metadata["original_row_count"] = len(original_rows)
                metadata["converted_row_count"] = len(converted_rows)

                if len(converted_rows) != len(original_rows):
                    errors.append(
                        f"Row count mismatch: original={len(original_rows)}, "
                        f"converted={len(converted_rows)}"
                    )

            elif target_format.lower() == "markdown":
                # Check for table structure
                lines = converted_text.strip().split("\n")
                if len(lines) < 2:
                    errors.append("Markdown table too short (missing header or separator)")
                elif not lines[1].startswith("|"):
                    errors.append("Markdown table missing separator row")

                # Count data rows
                data_rows = [line for line in lines[2:] if line.strip().startswith("|")]
                original_rows = original_json.get("rows", [])
                metadata["original_row_count"] = len(original_rows)
                metadata["converted_row_count"] = len(data_rows)

                if len(data_rows) != len(original_rows):
                    warnings.append(
                        f"Row count mismatch: original={len(original_rows)}, "
                        f"converted={len(data_rows)}"
                    )

            is_valid = len(errors) == 0
            message = f"Format conversion to {target_format} validated" if is_valid else "Conversion validation failed"

            return ValidationResult(
                is_valid=is_valid,
                message=message,
                errors=errors,
                warnings=warnings,
                metadata=metadata
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Conversion validation error: {str(e)}",
                errors=[str(e)],
                warnings=warnings,
                metadata=metadata
            )
