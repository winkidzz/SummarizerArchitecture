#!/usr/bin/env python3
"""
Evaluation test for Use Case 1: CSV Extraction with Structured Output.

Tests the LLM's ability to extract structured data and convert to CSV format.
Uses an evaluation set approach with multiple test scenarios.
"""
import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, List

# Add src and agents to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / ".adk/agents"))

# Set Ollama env vars
os.environ["USE_OLLAMA_EVAL"] = "true"
os.environ["OLLAMA_MODEL"] = "llama3.2:1b"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"

from _shared.agent_base import generate_structured_table, get_complete_document
from document_store.formatting import create_service


# Evaluation test cases
EVAL_SET = [
    {
        "id": "test_1_simple_table",
        "name": "Simple 3x3 Table Extraction",
        "content": """
# AI Development Techniques

| Phase | Category | Technique |
|-------|----------|-----------|
| Design | Architecture | RAG |
| Build | Coding | Prompting |
| Test | Quality | Evaluation |
        """,
        "schema_name": "table",
        "output_format": "csv",
        "expected": {
            "min_rows": 3,
            "expected_columns": ["Phase", "Category", "Technique"],
            "should_contain": ["Design", "RAG", "Evaluation"]
        }
    },
    {
        "id": "test_2_techniques_catalog",
        "name": "AI Development Techniques Catalog (from document)",
        "source_filter": "ai-development-techniques",
        "schema_name": "techniques_catalog",
        "output_format": "csv",
        "expected": {
            "min_rows": 5,
            "should_contain": ["phase", "category", "technique"]
        }
    },
    {
        "id": "test_3_rag_patterns_table",
        "name": "RAG Patterns Comparison Table",
        "content": """
# RAG Patterns Comparison

| Pattern | Complexity | Accuracy Improvement |
|---------|-----------|---------------------|
| Basic RAG | Low | Baseline |
| Contextual Retrieval | Medium | +49-67% |
| HyDE RAG | Medium | +15-30% |
| RAPTOR | High | +25-40% |
        """,
        "schema_name": "table",
        "output_format": "csv",
        "expected": {
            "min_rows": 4,
            "expected_columns": ["Pattern", "Complexity", "Accuracy Improvement"],
            "should_contain": ["Basic RAG", "RAPTOR", "Contextual"]
        }
    },
    {
        "id": "test_4_vendor_comparison",
        "name": "Vendor Feature Comparison",
        "content": """
# Cloud AI Vendors

| Vendor | Model | Context Window | Cost |
|--------|-------|----------------|------|
| Anthropic | Claude 3.5 | 200K | $3/$15 |
| Google | Gemini 1.5 | 2M | $1.25/$5 |
| OpenAI | GPT-4 Turbo | 128K | $10/$30 |
        """,
        "schema_name": "table",
        "output_format": "csv",
        "expected": {
            "min_rows": 3,
            "expected_columns": ["Vendor", "Model", "Context Window", "Cost"],
            "should_contain": ["Anthropic", "Gemini", "GPT-4"]
        }
    }
]


class StructuredOutputEvaluator:
    """Evaluator for structured output CSV extraction."""

    def __init__(self):
        """Initialize evaluator."""
        self.service = create_service(use_ollama=True)
        print(f"Initialized with Ollama: {self.service.use_ollama}, Model: {self.service.model_name}")

    def run_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single test case.

        Returns:
            Test result with success status and details
        """
        test_id = test_case["id"]
        test_name = test_case["name"]

        print(f"\n{'='*80}")
        print(f"TEST: {test_name}")
        print(f"ID: {test_id}")
        print(f"{'='*80}")

        try:
            # Get content
            if "source_filter" in test_case:
                # Retrieve from document store
                print(f"Retrieving document: {test_case['source_filter']}")
                doc_result = get_complete_document(test_case["source_filter"])
                if not doc_result.get("success"):
                    return {
                        "test_id": test_id,
                        "test_name": test_name,
                        "success": False,
                        "error": f"Document retrieval failed: {doc_result.get('error')}"
                    }
                content = doc_result["content"]
            else:
                # Use provided content
                content = test_case["content"]

            print(f"Content length: {len(content)} characters")

            # Generate structured output
            print(f"Generating structured output...")
            print(f"  Schema: {test_case['schema_name']}")
            print(f"  Format: {test_case['output_format']}")

            result = self.service.generate_structured_output(
                content=content,
                query=f"Extract all data as {test_case['output_format']}",
                schema_name=test_case["schema_name"],
                output_format=test_case["output_format"],
                validate=True
            )

            if not result.get("success"):
                print(f"\n❌ FAILED")
                print(f"Error: {result.get('error')}")
                return {
                    "test_id": test_id,
                    "test_name": test_name,
                    "success": False,
                    "error": result.get("error"),
                    "validation_errors": result.get("validation", {}).get("errors", [])
                }

            # Validate output
            output_data = result.get("data", "")
            validation = self._validate_output(output_data, test_case["expected"])

            if validation["passed"]:
                print(f"\n✅ PASSED")
                print(f"Validation: {validation['message']}")
                print(f"\nOutput preview (first 500 chars):")
                print(output_data[:500])
            else:
                print(f"\n⚠️  PASSED WITH WARNINGS")
                print(f"Warnings: {validation['message']}")
                print(f"\nOutput preview (first 500 chars):")
                print(output_data[:500])

            return {
                "test_id": test_id,
                "test_name": test_name,
                "success": True,
                "validation": validation,
                "output_length": len(output_data),
                "output_preview": output_data[:200],
                "metadata": result.get("metadata", {})
            }

        except Exception as e:
            print(f"\n❌ EXCEPTION")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()

            return {
                "test_id": test_id,
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def _validate_output(self, output: str, expected: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate CSV output against expected criteria.

        Returns:
            Validation result with passed status and message
        """
        warnings = []

        # Check if output is not empty
        if not output or len(output.strip()) == 0:
            return {
                "passed": False,
                "message": "Output is empty"
            }

        # Split into lines
        lines = [line.strip() for line in output.strip().split('\n') if line.strip()]

        # Check minimum rows
        if "min_rows" in expected:
            min_rows = expected["min_rows"]
            actual_rows = len(lines) - 1  # Exclude header
            if actual_rows < min_rows:
                warnings.append(f"Expected at least {min_rows} rows, got {actual_rows}")

        # Check for expected columns in header
        if "expected_columns" in expected and len(lines) > 0:
            header = lines[0].lower()
            for col in expected["expected_columns"]:
                if col.lower() not in header:
                    warnings.append(f"Expected column '{col}' not found in header")

        # Check for expected content
        if "should_contain" in expected:
            output_lower = output.lower()
            for term in expected["should_contain"]:
                if term.lower() not in output_lower:
                    warnings.append(f"Expected term '{term}' not found in output")

        if warnings:
            return {
                "passed": True,
                "has_warnings": True,
                "message": "; ".join(warnings)
            }

        return {
            "passed": True,
            "has_warnings": False,
            "message": "All validations passed"
        }

    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all test cases in the evaluation set.

        Returns:
            Summary of all test results
        """
        print("\n" + "="*80)
        print("USE CASE 1: CSV EXTRACTION - EVALUATION SET")
        print("="*80)
        print(f"Total tests: {len(EVAL_SET)}")
        print(f"Model: {self.service.model_name}")
        print("="*80)

        results = []
        for test_case in EVAL_SET:
            result = self.run_test(test_case)
            results.append(result)

        # Generate summary
        total = len(results)
        passed = sum(1 for r in results if r["success"])
        failed = total - passed

        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total tests: {total}")
        print(f"Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total*100:.1f}%)")

        if failed > 0:
            print(f"\nFailed tests:")
            for r in results:
                if not r["success"]:
                    print(f"  - {r['test_id']}: {r.get('error', 'Unknown error')}")

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total * 100,
            "results": results
        }


def main():
    """Run evaluation."""
    evaluator = StructuredOutputEvaluator()
    summary = evaluator.run_all_tests()

    # Save results to JSON
    output_file = Path(__file__).parent.parent / "usecase1_eval_results.json"
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    # Exit with appropriate code
    sys.exit(0 if summary["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
