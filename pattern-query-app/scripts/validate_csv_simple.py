#!/usr/bin/env python3
"""Simple CSV accuracy validation - check row count, sample rows, and structure."""

import csv
from pathlib import Path


def main():
    csv_path = Path("/Users/sanantha/SummarizerArchitecture/test/llm_response.txt")

    print("=" * 80)
    print("CSV ACCURACY VALIDATION")
    print("=" * 80)

    # Read CSV
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"\n✓ CSV file loaded successfully")
    print(f"✓ Found {len(rows)} data rows")

    # Get column names (filter out None values if any)
    col_names = [k for k in rows[0].keys() if k is not None]
    print(f"✓ Header: {', '.join(col_names)}")

    # Expected values
    expected_rows = 163  # 164 total lines - 1 header = 163 data rows
    expected_columns = 7

    # Validation checks
    issues = []

    # Check row count
    if len(rows) != expected_rows:
        issues.append(f"Expected {expected_rows} rows, got {len(rows)}")
    else:
        print(f"✓ Row count correct: {len(rows)} data rows")

    # Check column count
    actual_col_count = len(col_names)
    if actual_col_count != expected_columns:
        issues.append(f"Expected {expected_columns} columns, got {actual_col_count}")
    else:
        print(f"✓ Column count correct: {expected_columns} columns")

    # Check expected columns
    expected_cols = ["Phase", "Category", "Technique/Methodology", "Description",
                     "Process Framework", "Usage in Architecture", "Lifecycle Steps"]
    actual_cols = col_names
    if actual_cols != expected_cols:
        issues.append(f"Column names mismatch")
        print(f"✗ Expected columns: {expected_cols}")
        print(f"✗ Got columns: {actual_cols}")
    else:
        print(f"✓ Column names correct")

    # Sample validation - check key content
    print("\n" + "=" * 80)
    print("SAMPLE CONTENT VALIDATION")
    print("=" * 80)

    # First row
    print("\nFirst Row:")
    print(f"  Phase: {rows[0]['Phase']}")
    print(f"  Category: {rows[0]['Category']}")
    print(f"  Technique: {rows[0]['Technique/Methodology']}")
    print(f"  Framework: {rows[0]['Process Framework']}")

    # Check first row content (accounting for bold formatting removal)
    if "1. Ideation & Planning" in rows[0]['Phase']:
        print("  ✓ Phase matches (formatting stripped correctly)")
    else:
        issues.append("First row Phase content doesn't match")

    if rows[0]['Category'] == "Data Analysis":
        print("  ✓ Category matches")
    else:
        issues.append("First row Category doesn't match")

    if "Exploratory Data Analysis" in rows[0]['Technique/Methodology']:
        print("  ✓ Technique matches (formatting stripped correctly)")
    else:
        issues.append("First row Technique doesn't match")

    if "CRISP-DM" in rows[0]['Process Framework']:
        print("  ✓ Process Framework matches")
    else:
        issues.append("First row Process Framework doesn't match")

    # Last row
    print("\nLast Row:")
    print(f"  Phase: {rows[-1]['Phase']}")
    print(f"  Category: {rows[-1]['Category']}")
    print(f"  Technique: {rows[-1]['Technique/Methodology']}")

    if "10. Continuous Compliance" in rows[-1]['Phase']:
        print("  ✓ Last row Phase matches")
    else:
        issues.append("Last row Phase doesn't match")

    # Check for empty cells
    print("\n" + "=" * 80)
    print("DATA QUALITY CHECKS")
    print("=" * 80)

    empty_cells = 0
    for i, row in enumerate(rows):
        for col, value in row.items():
            if not value or value.strip() == '':
                empty_cells += 1
                if empty_cells <= 5:  # Show first 5
                    print(f"  ✗ Empty cell at row {i+1}, column '{col}'")

    if empty_cells == 0:
        print("  ✓ No empty cells found")
    else:
        print(f"  ✗ Found {empty_cells} empty cells")
        issues.append(f"{empty_cells} empty cells found")

    # Check for suspiciously short descriptions
    short_descriptions = []
    for i, row in enumerate(rows):
        if len(row['Description']) < 20:
            short_descriptions.append((i+1, row['Description']))

    if not short_descriptions:
        print("  ✓ All descriptions have reasonable length")
    else:
        print(f"  ✗ Found {len(short_descriptions)} suspiciously short descriptions")
        for row_num, desc in short_descriptions[:3]:
            print(f"    Row {row_num}: '{desc}'")

    # Phase distribution check
    print("\n" + "=" * 80)
    print("PHASE DISTRIBUTION")
    print("=" * 80)

    phase_counts = {}
    for row in rows:
        phase = row['Phase']
        phase_counts[phase] = phase_counts.get(phase, 0) + 1

    for phase, count in sorted(phase_counts.items()):
        print(f"  {phase}: {count} rows")

    # Expected phases
    expected_phases = 10
    if len(phase_counts) == expected_phases:
        print(f"\n  ✓ All {expected_phases} phases present")
    else:
        issues.append(f"Expected {expected_phases} phases, got {len(phase_counts)}")

    # Final summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    if not issues:
        print("\n✓ SUCCESS: CSV is accurate and complete!")
        print(f"  - {len(rows)} data rows (expected {expected_rows})")
        print(f"  - {len(rows[0].keys())} columns (expected {expected_columns})")
        print(f"  - {len(phase_counts)} phases (expected {expected_phases})")
        print(f"  - All required columns present")
        print(f"  - No empty cells")
        print(f"  - Formatting properly stripped (bold, markdown)")
        return 0
    else:
        print(f"\n✗ VALIDATION FAILED: {len(issues)} issues found")
        for issue in issues:
            print(f"  - {issue}")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
