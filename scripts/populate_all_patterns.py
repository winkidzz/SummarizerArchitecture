"""
Populate All AI Design Pattern Templates

This script reads from all_pattern_content.json and populates the first 3 sections
(Overview, When to Use, When Not to Use) for all 70 AI design pattern template files.

Usage:
    python scripts/populate_all_patterns.py
"""

import json
import os
from pathlib import Path

def load_pattern_content(json_path: Path) -> dict:
    """Load pattern content from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def populate_pattern_file(file_path: Path, content: dict):
    """Populate a single pattern file with content."""

    # Read current file content
    with open(file_path, 'r', encoding='utf-8') as f:
        current_content = f.read()

    # Build the replacement sections
    overview_section = f"""## Overview

{content['overview']}"""

    when_to_use_items = '\n'.join([f"- {item}" for item in content['when_to_use']])
    when_to_use_section = f"""## When to Use

{when_to_use_items}"""

    when_not_to_use_items = '\n'.join([f"- {item}" for item in content['when_not_to_use']])
    when_not_to_use_section = f"""## When Not to Use

{when_not_to_use_items}"""

    # Replace template placeholders
    template_text = """## Overview

[Brief description of the pattern, its purpose, and when it's commonly used]

## When to Use

- [Use case 1]
- [Use case 2]
- [Use case 3]

## When Not to Use

- [Anti-pattern or alternative scenario 1]
- [Anti-pattern or alternative scenario 2]
- [Anti-pattern or alternative scenario 3]"""

    replacement_text = f"""{overview_section}

{when_to_use_section}

{when_not_to_use_section}"""

    # Replace in file
    new_content = current_content.replace(template_text, replacement_text)

    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True

def main():
    """Main execution."""
    # Paths
    script_dir = Path(__file__).parent
    base_path = script_dir.parent / "docs" / "ai-design-patterns"
    json_path = script_dir / "all_pattern_content.json"

    # Load content
    print("Loading pattern content from JSON...")
    pattern_content = load_pattern_content(json_path)
    print(f"Loaded {len(pattern_content)} pattern definitions")

    # Process each pattern
    updated_count = 0
    not_found_count = 0
    error_count = 0

    for pattern_path, content in pattern_content.items():
        # Construct full file path
        file_path = base_path / pattern_path

        if not file_path.exists():
            print(f"[NOT FOUND] {pattern_path}")
            not_found_count += 1
            continue

        try:
            populate_pattern_file(file_path, content)
            print(f"[OK] Updated: {pattern_path}")
            updated_count += 1
        except Exception as e:
            print(f"[ERROR] updating {pattern_path}: {str(e)}")
            error_count += 1

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total patterns in JSON: {len(pattern_content)}")
    print(f"Successfully updated:   {updated_count}")
    print(f"Not found:              {not_found_count}")
    print(f"Errors:                 {error_count}")
    print("="*60)

    if updated_count == len(pattern_content):
        print("\n[SUCCESS] All patterns updated successfully!")
    elif updated_count > 0:
        print(f"\n[PARTIAL] {updated_count}/{len(pattern_content)} patterns updated")
    else:
        print("\n[FAILURE] No patterns were updated")

if __name__ == "__main__":
    main()
