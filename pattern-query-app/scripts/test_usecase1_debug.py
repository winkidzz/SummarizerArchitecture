#!/usr/bin/env python3
"""
Debug test for Use Case 1 - shows actual LLM output.
"""
import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set Ollama env vars
os.environ["USE_OLLAMA_EVAL"] = "true"
os.environ["OLLAMA_MODEL"] = "llama3.2:1b"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"

from document_store.formatting import create_service


def test_simple_table():
    """Test simple table extraction with debug output."""
    print("="*80)
    print("DEBUG TEST: Simple Table Extraction")
    print("="*80)

    service = create_service(use_ollama=True)
    print(f"\nService: Ollama={service.use_ollama}, Model={service.model_name}")

    content = """
# AI Development Techniques

| Phase | Category | Technique |
|-------|----------|-----------|
| Design | Architecture | RAG |
| Build | Coding | Prompting |
| Test | Quality | Evaluation |
    """

    print(f"\nInput content:")
    print(content)

    print(f"\n{'='*80}")
    print("Calling LLM with TableSchema...")
    print(f"{'='*80}")

    # Call the internal method to see raw LLM output
    try:
        from document_store.formatting.schemas import SchemaRegistry, TableSchema

        schema_class = SchemaRegistry.get_schema("table")
        print(f"\nSchema: {schema_class.__name__}")
        print(f"Schema fields: {list(schema_class.model_fields.keys())}")

        # Generate with Ollama
        raw_output = service._generate_with_ollama(
            content=content,
            query="Extract the table as structured data",
            schema_class=schema_class,
            schema_name="table"
        )

        print(f"\n{'='*80}")
        print("RAW LLM OUTPUT:")
        print(f"{'='*80}")
        print(json.dumps(raw_output, indent=2))

        # Try to validate
        print(f"\n{'='*80}")
        print("Attempting Pydantic validation...")
        print(f"{'='*80}")

        try:
            validated = TableSchema(**raw_output)
            print("✅ Validation PASSED")
            print(f"\nValidated data:")
            print(validated.model_dump_json(indent=2))
        except Exception as e:
            print(f"❌ Validation FAILED")
            print(f"Error: {e}")

    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_simple_table()
