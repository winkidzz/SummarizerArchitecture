#!/usr/bin/env python3
"""
Quick test of Gemini-based Ragas evaluation.

Tests the GeminiEvaluator with a simple query to verify:
1. Gemini API key is working
2. Evaluation metrics are being computed
3. Score parsing is working correctly

Usage:
    python scripts/test_gemini_eval.py
"""

import os
import sys
import time
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded .env from: {env_path}")
except ImportError:
    print("Warning: python-dotenv not installed, environment variables won't be loaded from .env")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from document_store.evaluation.gemini_evaluator import GeminiEvaluator, RagasMetrics

def main():
    print("=" * 70)
    print("GEMINI EVALUATOR TEST")
    print("=" * 70)

    # Test data
    query = "What is Basic RAG?"
    response = "Basic RAG is a foundational pattern that combines retrieval with generation. It retrieves relevant documents from a vector database and passes them to an LLM to generate a grounded response."
    contexts = [
        "Basic RAG Pattern: Retrieves documents from vector store using semantic search.",
        "RAG combines retrieval-augmented generation by finding relevant docs and using them as context for LLM responses.",
        "Vector databases enable semantic search for document retrieval in RAG systems."
    ]
    reference = "Basic RAG is a pattern that retrieves relevant documents and uses them as context for LLM generation."

    # Initialize evaluator
    print("\n🔧 Initializing Gemini evaluator...")
    try:
        evaluator = GeminiEvaluator(model="gemini-2.0-flash-exp")
        print(f"✓ Evaluator ready (model: gemini-2.0-flash-exp)")
    except Exception as e:
        print(f"✗ Failed to initialize evaluator: {e}")
        print("\nMake sure GEMINI_API_KEY is set in your .env file.")
        return 1

    # Run evaluation
    print("\n🔍 Running evaluation...")
    print(f"Query: {query}")
    print(f"Response: {response[:100]}...")

    start = time.time()
    try:
        result = evaluator.evaluate(
            query=query,
            response=response,
            retrieved_contexts=contexts,
            reference_answer=reference,
            metrics=[
                RagasMetrics.FAITHFULNESS,
                RagasMetrics.ANSWER_RELEVANCY,
                RagasMetrics.CONTEXT_PRECISION,
                RagasMetrics.CONTEXT_RECALL
            ]
        )
        elapsed = time.time() - start

        # Display results
        print(f"\n✓ Evaluation completed in {elapsed:.2f}s")
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"\nOverall Score: {result['overall_score']:.3f}")
        print("\nMetric Scores:")
        for metric, score in result['scores'].items():
            if score is not None:
                print(f"  {metric:20s}: {score:.3f}")
            else:
                print(f"  {metric:20s}: N/A")

        print("\n" + "=" * 70)

        # Check if scores are meaningful (not all 0.5)
        scores_list = [s for s in result['scores'].values() if s is not None]
        if all(s == 0.5 for s in scores_list):
            print("\n⚠️  WARNING: All scores are 0.5 (default fallback)")
            print("   This suggests score parsing might be failing.")
            return 1
        else:
            print("\n✓ SUCCESS: Gemini evaluation is working correctly!")
            print("   Scores vary, indicating proper evaluation.")
            return 0

    except Exception as e:
        print(f"\n✗ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
