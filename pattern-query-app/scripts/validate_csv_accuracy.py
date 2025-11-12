#!/usr/bin/env python3
"""Validate CSV accuracy against source markdown table."""

import csv
import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "src"))


def read_markdown_table(file_path):
    """Read markdown table and convert to list of dicts."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Find the table
    lines = content.split('\n')
    table_lines = []
    in_table = False

    for line in lines:
        if '| Phase |' in line:
            in_table = True

        if in_table and line.strip().startswith('|'):
            if not line.strip().startswith('|---'):
                table_lines.append(line)
        elif in_table and not line.strip():
            break

    # Parse table
    if not table_lines:
        return []

    # Extract header
    header_line = table_lines[0]
    headers = [h.strip() for h in header_line.split('|')[1:-1]]

    # Extract data rows
    rows = []
    for line in table_lines[1:]:
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if len(cells) == len(headers):
            row_dict = dict(zip(headers, cells))
            rows.append(row_dict)

    return rows


def read_csv_response(file_path):
    """Read CSV response file."""
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)


def validate_accuracy(markdown_rows, csv_rows):
    """Validate CSV accuracy against markdown source."""
    issues = []

    # Check row count
    if len(markdown_rows) != len(csv_rows):
        issues.append(f"Row count mismatch: markdown has {len(markdown_rows)}, CSV has {len(csv_rows)}")

    # Check each row
    min_rows = min(len(markdown_rows), len(csv_rows))

    for i in range(min_rows):
        md_row = markdown_rows[i]
        csv_row = csv_rows[i]

        # Check each field
        for key in md_row.keys():
            md_value = md_row[key].strip()
            csv_value = csv_row.get(key, '').strip()

            # Normalize for comparison (CSV may have quotes)
            csv_value = csv_value.strip('"')

            if md_value != csv_value:
                issues.append(
                    f"Row {i+1}, Column '{key}': "
                    f"Expected '{md_value[:50]}...', Got '{csv_value[:50]}...'"
                )

    return issues


def main():
    markdown_path = Path("/Users/sanantha/SummarizerArchitecture/pattern-library/framework/ai-development-techniques.md")
    csv_path = Path("/Users/sanantha/SummarizerArchitecture/test/llm_response.txt")

    print("=" * 80)
    print("CSV ACCURACY VALIDATION")
    print("=" * 80)

    # Read files
    print("\nReading source markdown table...")
    markdown_rows = read_markdown_table(markdown_path)
    print(f"Found {len(markdown_rows)} rows in markdown")

    print("\nReading CSV response...")
    csv_rows = read_csv_response(csv_path)
    print(f"Found {len(csv_rows)} rows in CSV")

    # Validate
    print("\nValidating accuracy...")
    issues = validate_accuracy(markdown_rows, csv_rows)

    if not issues:
        print("\n✓ SUCCESS: CSV matches source markdown perfectly!")
        print(f"  - All {len(csv_rows)} data rows present")
        print(f"  - All 7 columns match")
        print(f"  - All cell values match")
    else:
        print(f"\n✗ ISSUES FOUND: {len(issues)} problems detected")
        print("\nFirst 10 issues:")
        for issue in issues[:10]:
            print(f"  - {issue}")

        if len(issues) > 10:
            print(f"\n  ... and {len(issues) - 10} more issues")

    # Sample validation - check first and last rows
    print("\n" + "=" * 80)
    print("SAMPLE VALIDATION")
    print("=" * 80)

    if markdown_rows and csv_rows:
        print("\nFirst Row Comparison:")
        print(f"  Markdown Phase: {markdown_rows[0]['Phase']}")
        print(f"  CSV Phase:      {csv_rows[0]['Phase']}")
        print(f"  Match: {'✓' if markdown_rows[0]['Phase'] == csv_rows[0]['Phase'] else '✗'}")

        print(f"\nLast Row Comparison:")
        print(f"  Markdown Phase: {markdown_rows[-1]['Phase']}")
        print(f"  CSV Phase:      {csv_rows[-1]['Phase']}")
        print(f"  Match: {'✓' if markdown_rows[-1]['Phase'] == csv_rows[-1]['Phase'] else '✗'}")

    return 0 if not issues else 1


if __name__ == '__main__':
    sys.exit(main())
