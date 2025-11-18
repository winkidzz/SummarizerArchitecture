#!/usr/bin/env python3
"""
Test API quality metrics collection.
Sends test queries and verifies metrics are collected.
"""

import requests
import json
import time

API_URL = "http://localhost:8000"

def test_query(query_text: str, num: int):
    """Send a test query and print quality metrics."""
    print(f"\n{'='*80}")
    print(f"Test Query #{num}: {query_text}")
    print('='*80)

    try:
        response = requests.post(
            f"{API_URL}/query",
            json={"query": query_text, "top_k": 5},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()

            print(f"\n✅ Query successful!")
            print(f"Answer length: {len(result.get('answer', ''))} chars")
            print(f"Sources retrieved: {result.get('retrieved_docs', 0)}")

            # Check quality metrics
            quality_metrics = result.get('quality_metrics')
            if quality_metrics:
                print(f"\n📊 Quality Metrics:")

                # Answer quality
                answer_metrics = quality_metrics.get('answer', {})
                print(f"\n  Answer Quality:")
                print(f"    Faithfulness:    {answer_metrics.get('faithfulness', 0):.2%}")
                print(f"    Relevancy:       {answer_metrics.get('relevancy', 0):.2%}")
                print(f"    Completeness:    {answer_metrics.get('completeness', 0):.2%}")
                print(f"    Hallucination:   {answer_metrics.get('has_hallucination', False)}")
                print(f"    Severity:        {answer_metrics.get('hallucination_severity', 'N/A')}")

                # Context quality
                context_metrics = quality_metrics.get('context', {})
                print(f"\n  Context Quality:")
                print(f"    Relevancy:       {context_metrics.get('relevancy', 0):.2%}")
                print(f"    Utilization:     {context_metrics.get('utilization', 0):.2%}")

                return True
            else:
                print(f"\n⚠️  No quality metrics in response!")
                print(f"Response keys: {list(result.keys())}")
                return False
        else:
            print(f"\n❌ Query failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def check_prometheus_metrics():
    """Check if metrics are exposed in Prometheus endpoint."""
    print(f"\n{'='*80}")
    print("Checking Prometheus Metrics Endpoint")
    print('='*80)

    try:
        response = requests.get(f"{API_URL}/metrics", timeout=5)

        if response.status_code == 200:
            metrics_text = response.text

            # Check for quality metrics
            quality_metrics_found = []

            if 'rag_answer_faithfulness_score' in metrics_text:
                quality_metrics_found.append('✅ rag_answer_faithfulness_score')
            else:
                quality_metrics_found.append('❌ rag_answer_faithfulness_score')

            if 'rag_hallucination_detected' in metrics_text:
                quality_metrics_found.append('✅ rag_hallucination_detected')
            else:
                quality_metrics_found.append('❌ rag_hallucination_detected')

            if 'rag_context_relevancy' in metrics_text:
                quality_metrics_found.append('✅ rag_context_relevancy')
            else:
                quality_metrics_found.append('❌ rag_context_relevancy')

            if 'rag_answer_relevancy_score' in metrics_text:
                quality_metrics_found.append('✅ rag_answer_relevancy_score')
            else:
                quality_metrics_found.append('❌ rag_answer_relevancy_score')

            print("\nQuality Metrics in Prometheus:")
            for metric in quality_metrics_found:
                print(f"  {metric}")

            # Count total metrics
            all_metrics = [line for line in metrics_text.split('\n') if line.startswith('rag_')]
            print(f"\nTotal RAG metrics exposed: {len(all_metrics)}")

            return all(m.startswith('✅') for m in quality_metrics_found)
        else:
            print(f"❌ Metrics endpoint failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error checking metrics: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("API Quality Metrics Test Suite")
    print("="*80)

    # Test queries
    test_queries = [
        "What is RAPTOR RAG and how does it work?",
        "Explain contextual retrieval techniques",
        "What are the benefits of hybrid search?"
    ]

    success_count = 0
    for i, query in enumerate(test_queries, 1):
        if test_query(query, i):
            success_count += 1
        time.sleep(2)  # Small delay between queries

    print(f"\n{'='*80}")
    print(f"Test Results: {success_count}/{len(test_queries)} queries successful")
    print('='*80)

    # Check Prometheus
    prometheus_ok = check_prometheus_metrics()

    # Final summary
    print(f"\n{'='*80}")
    print("Summary")
    print('='*80)
    print(f"  API Queries:         {success_count}/{len(test_queries)} ✅" if success_count == len(test_queries) else f"  API Queries:         {success_count}/{len(test_queries)} ⚠️")
    print(f"  Prometheus Metrics:  {'✅' if prometheus_ok else '⚠️'}")

    if success_count == len(test_queries) and prometheus_ok:
        print(f"\n🎉 All tests passed! Quality metrics are being collected.")
        print(f"\n📊 View metrics in Grafana:")
        print(f"   http://localhost:3333/d/4facbed2-cca8-4582-a2cc-c0e4b934a497/rag-quality-metrics")
    else:
        print(f"\n⚠️  Some tests failed. Check the API server logs.")

    print()


if __name__ == "__main__":
    main()
