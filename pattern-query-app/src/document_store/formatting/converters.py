"""
Format converters for transforming validated JSON to various output formats.

Converts structured JSON output (from LLM) to CSV, Markdown, Excel, etc.
"""

import csv
import io
import json
from typing import List, Dict, Any, Optional


class FormatConverter:
    """Convert validated JSON structures to various output formats."""

    @staticmethod
    def to_csv(
        data: List[Dict[str, Any]],
        include_header: bool = True,
        quoting: int = csv.QUOTE_MINIMAL,
        delimiter: str = ","
    ) -> str:
        """
        Convert list of dictionaries to CSV format.

        Args:
            data: List of dictionaries with consistent keys
            include_header: Whether to include header row
            quoting: CSV quoting style (see csv module)
            delimiter: Field delimiter

        Returns:
            CSV formatted string

        Example:
            >>> data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
            >>> csv_text = FormatConverter.to_csv(data)
            >>> print(csv_text)
            name,age
            Alice,30
            Bob,25
        """
        if not data:
            return ""

        output = io.StringIO()

        # Get all unique keys across all dictionaries (in case of inconsistent keys)
        all_keys = []
        seen_keys = set()
        for item in data:
            for key in item.keys():
                if key not in seen_keys:
                    all_keys.append(key)
                    seen_keys.add(key)

        writer = csv.DictWriter(
            output,
            fieldnames=all_keys,
            quoting=quoting,
            delimiter=delimiter,
            extrasaction='ignore'
        )

        if include_header:
            writer.writeheader()

        writer.writerows(data)

        return output.getvalue()

    @staticmethod
    def to_markdown_table(data: List[Dict[str, Any]], alignment: Optional[List[str]] = None) -> str:
        """
        Convert list of dictionaries to Markdown table format.

        Args:
            data: List of dictionaries with consistent keys
            alignment: List of alignments ('left', 'center', 'right') per column

        Returns:
            Markdown table formatted string

        Example:
            >>> data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
            >>> md = FormatConverter.to_markdown_table(data)
            >>> print(md)
            | name | age |
            |------|-----|
            | Alice | 30 |
            | Bob | 25 |
        """
        if not data:
            return ""

        # Get all unique keys
        all_keys = []
        seen_keys = set()
        for item in data:
            for key in item.keys():
                if key not in seen_keys:
                    all_keys.append(key)
                    seen_keys.add(key)

        # Create header row
        header_row = "| " + " | ".join(str(k) for k in all_keys) + " |"

        # Create separator row with alignment
        separators = []
        for i, key in enumerate(all_keys):
            if alignment and i < len(alignment):
                align = alignment[i]
                if align == "center":
                    separators.append(":---:")
                elif align == "right":
                    separators.append("---:")
                else:
                    separators.append("---")
            else:
                separators.append("---")

        separator_row = "| " + " | ".join(separators) + " |"

        # Create data rows
        rows = []
        for item in data:
            row_values = []
            for key in all_keys:
                value = item.get(key, "")
                # Escape pipes in cell content
                value_str = str(value).replace("|", "\\|")
                row_values.append(value_str)
            row = "| " + " | ".join(row_values) + " |"
            rows.append(row)

        return "\n".join([header_row, separator_row] + rows)

    @staticmethod
    def to_json(
        data: Any,
        indent: int = 2,
        sort_keys: bool = False,
        ensure_ascii: bool = False
    ) -> str:
        """
        Convert data to formatted JSON string.

        Args:
            data: Data to convert (dict, list, etc.)
            indent: Number of spaces for indentation
            sort_keys: Whether to sort dictionary keys
            ensure_ascii: Whether to escape non-ASCII characters

        Returns:
            JSON formatted string
        """
        return json.dumps(
            data,
            indent=indent,
            sort_keys=sort_keys,
            ensure_ascii=ensure_ascii
        )

    @staticmethod
    def to_tsv(data: List[Dict[str, Any]], include_header: bool = True) -> str:
        """
        Convert list of dictionaries to TSV (Tab-Separated Values) format.

        Args:
            data: List of dictionaries with consistent keys
            include_header: Whether to include header row

        Returns:
            TSV formatted string
        """
        return FormatConverter.to_csv(
            data=data,
            include_header=include_header,
            quoting=csv.QUOTE_MINIMAL,
            delimiter="\t"
        )

    @staticmethod
    def to_html_table(
        data: List[Dict[str, Any]],
        table_class: Optional[str] = None,
        include_header: bool = True
    ) -> str:
        """
        Convert list of dictionaries to HTML table format.

        Args:
            data: List of dictionaries with consistent keys
            table_class: CSS class for the table element
            include_header: Whether to include header row

        Returns:
            HTML table string
        """
        if not data:
            return ""

        # Get all unique keys
        all_keys = []
        seen_keys = set()
        for item in data:
            for key in item.keys():
                if key not in seen_keys:
                    all_keys.append(key)
                    seen_keys.add(key)

        # Start table
        table_tag = f'<table class="{table_class}">' if table_class else '<table>'
        lines = [table_tag]

        # Header
        if include_header:
            lines.append("  <thead>")
            lines.append("    <tr>")
            for key in all_keys:
                lines.append(f"      <th>{FormatConverter._html_escape(str(key))}</th>")
            lines.append("    </tr>")
            lines.append("  </thead>")

        # Body
        lines.append("  <tbody>")
        for item in data:
            lines.append("    <tr>")
            for key in all_keys:
                value = item.get(key, "")
                lines.append(f"      <td>{FormatConverter._html_escape(str(value))}</td>")
            lines.append("    </tr>")
        lines.append("  </tbody>")

        lines.append("</table>")

        return "\n".join(lines)

    @staticmethod
    def _html_escape(text: str) -> str:
        """Escape HTML special characters."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )

    @staticmethod
    def to_yaml(data: Any, default_flow_style: bool = False) -> str:
        """
        Convert data to YAML format.

        Args:
            data: Data to convert
            default_flow_style: Use flow style (inline) for collections

        Returns:
            YAML formatted string
        """
        try:
            import yaml
            return yaml.dump(
                data,
                default_flow_style=default_flow_style,
                allow_unicode=True,
                sort_keys=False
            )
        except ImportError:
            # Fallback to JSON if PyYAML not available
            return FormatConverter.to_json(data)

    @staticmethod
    def table_schema_to_format(
        table_data: Dict[str, Any],
        output_format: str = "csv"
    ) -> str:
        """
        Convert TableSchema validated data to requested format.

        Args:
            table_data: Dictionary from validated TableSchema
            output_format: Target format (csv, markdown, json, tsv, html, yaml)

        Returns:
            Formatted output string
        """
        rows = table_data.get("rows", [])

        format_map = {
            "csv": lambda: FormatConverter.to_csv(rows),
            "tsv": lambda: FormatConverter.to_tsv(rows),
            "markdown": lambda: FormatConverter.to_markdown_table(rows),
            "json": lambda: FormatConverter.to_json(table_data),
            "html": lambda: FormatConverter.to_html_table(rows),
            "yaml": lambda: FormatConverter.to_yaml(table_data),
        }

        converter = format_map.get(output_format.lower())
        if converter:
            return converter()
        else:
            # Default to JSON for unknown formats
            return FormatConverter.to_json(table_data)

    @staticmethod
    def list_schema_to_format(
        list_data: Dict[str, Any],
        output_format: str = "json"
    ) -> str:
        """
        Convert ListSchema validated data to requested format.

        Args:
            list_data: Dictionary from validated ListSchema
            output_format: Target format (csv, markdown, json, yaml)

        Returns:
            Formatted output string
        """
        items = list_data.get("items", [])

        if output_format.lower() in ["csv", "tsv", "markdown", "html"]:
            # Convert list items to table format
            return FormatConverter.table_schema_to_format(
                {"rows": items},
                output_format
            )
        elif output_format.lower() == "yaml":
            return FormatConverter.to_yaml(list_data)
        else:
            # Default to JSON
            return FormatConverter.to_json(list_data)

    @staticmethod
    def comparison_schema_to_format(
        comparison_data: Dict[str, Any],
        output_format: str = "markdown"
    ) -> str:
        """
        Convert ComparisonSchema validated data to requested format.

        Args:
            comparison_data: Dictionary from validated ComparisonSchema
            output_format: Target format (csv, markdown, json, html, yaml)

        Returns:
            Formatted output string
        """
        matrix = comparison_data.get("matrix", [])

        if output_format.lower() in ["csv", "tsv", "markdown", "html"]:
            return FormatConverter.table_schema_to_format(
                {"rows": matrix},
                output_format
            )
        elif output_format.lower() == "yaml":
            return FormatConverter.to_yaml(comparison_data)
        else:
            # Default to JSON
            return FormatConverter.to_json(comparison_data)
