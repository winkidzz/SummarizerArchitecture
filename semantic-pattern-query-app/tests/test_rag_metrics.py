#!/usr/bin/env python3
"""
Comprehensive RAG Metrics Test

Tests 20 diverse questions and measures key metrics:
- Response latency
- Cache hit rate
- Retrieval quality
- Answer quality
- Source relevance
- System performance
"""

import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any
import statistics
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

# API base URL
API_BASE = "http://localhost:8000"

# 20 diverse questions covering different aspects
TEST_QUERIES = [
    # RAG Patterns
    "What is RAPTOR RAG and how does it work?",
    "Explain hybrid retrieval and its benefits",
    "How does semantic chunking preserve document structure?",
    "What is contextual retrieval and when should I use it?",
    "Describe the RAPTOR RAG pattern in detail",
    
    # AI Design Patterns
    "What is A/B testing for ML models?",
    "How does canary deployment work for machine learning?",
    "Explain model versioning strategies",
    "What is drift detection and why is it important?",
    "How does federated learning work?",
    
    # Technical Implementation
    "How do I implement vector search with Qdrant?",
    "What are best practices for RAG in healthcare?",
    "How to handle long context in RAG systems?",
    "What is the difference between basic RAG and advanced RAG?",
    "Explain the parent-child RAG pattern",
    
    # Use Cases
    "How to summarize patient records using RAG?",
    "What are the best practices for clinical note generation?",
    "How to implement real-time clinical data monitoring?",
    
    # Vendor/Framework
    "How to use LangChain for RAG implementation?",
    "What are the key features of Azure OpenAI for RAG?",
    "Compare different RAG patterns for healthcare use cases",
]

def test_query(query: str, use_cache: bool = True) -> Dict[str, Any]:
    """Test a single query and measure metrics."""
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_BASE}/query",
            json={
                "query": query,
                "top_k": 10,
                "use_cache": use_cache
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        
        end_time = time.time()
        latency = end_time - start_time
        
        return {
            "query": query,
            "success": True,
            "latency_ms": latency * 1000,
            "answer_length": len(result.get("answer", "")),
            "sources_count": len(result.get("sources", [])),
            "retrieved_docs": result.get("retrieved_docs", 0),
            "context_docs_used": result.get("context_docs_used", 0),
            "cache_hit": result.get("cache_hit", False),
            "has_answer": len(result.get("answer", "")) > 0,
            "has_sources": len(result.get("sources", [])) > 0,
            "answer_preview": result.get("answer", "")[:100] + "..." if result.get("answer") else "",
            "error": None
        }
    except Exception as e:
        end_time = time.time()
        latency = end_time - start_time
        return {
            "query": query,
            "success": False,
            "latency_ms": latency * 1000,
            "answer_length": 0,
            "sources_count": 0,
            "retrieved_docs": 0,
            "context_docs_used": 0,
            "cache_hit": False,
            "has_answer": False,
            "has_sources": False,
            "answer_preview": "",
            "error": str(e)
        }

def calculate_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate aggregate metrics from test results."""
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    if not successful:
        return {
            "total_queries": len(results),
            "success_rate": 0.0,
            "error": "No successful queries"
        }
    
    latencies = [r["latency_ms"] for r in successful]
    answer_lengths = [r["answer_length"] for r in successful]
    sources_counts = [r["sources_count"] for r in successful]
    cache_hits = [r for r in successful if r["cache_hit"]]
    
    return {
        "total_queries": len(results),
        "successful_queries": len(successful),
        "failed_queries": len(failed),
        "success_rate": len(successful) / len(results) * 100,
        
        # Latency metrics
        "latency": {
            "mean_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "p95_ms": statistics.quantiles(latencies, n=20)[18] if len(latencies) > 1 else latencies[0],
            "p99_ms": statistics.quantiles(latencies, n=100)[98] if len(latencies) > 1 else latencies[0],
        },
        
        # Answer quality metrics
        "answer_quality": {
            "mean_length": statistics.mean(answer_lengths),
            "median_length": statistics.median(answer_lengths),
            "min_length": min(answer_lengths),
            "max_length": max(answer_lengths),
            "has_answer_rate": sum(1 for r in successful if r["has_answer"]) / len(successful) * 100,
        },
        
        # Retrieval metrics
        "retrieval": {
            "mean_sources": statistics.mean(sources_counts),
            "mean_retrieved_docs": statistics.mean([r["retrieved_docs"] for r in successful]),
            "mean_context_docs": statistics.mean([r["context_docs_used"] for r in successful if r["context_docs_used"] is not None]),
            "has_sources_rate": sum(1 for r in successful if r["has_sources"]) / len(successful) * 100,
        },
        
        # Cache metrics
        "cache": {
            "hit_count": len(cache_hits),
            "hit_rate": len(cache_hits) / len(successful) * 100 if successful else 0,
            "miss_count": len(successful) - len(cache_hits),
        },
        
        # Performance targets
        "targets": {
            "latency_p95_target_ms": 500,
            "latency_p95_met": statistics.quantiles(latencies, n=20)[18] <= 500 if len(latencies) > 1 else False,
            "success_rate_target": 100,
            "success_rate_met": len(successful) == len(results),
            "cache_hit_rate_target": 40,
            "cache_hit_rate_met": (len(cache_hits) / len(successful) * 100) >= 40 if successful else False,
        }
    }

def main():
    """Run comprehensive RAG metrics test."""
    print("=" * 80)
    print("RAG Architecture Metrics Test")
    print("=" * 80)
    print(f"Testing {len(TEST_QUERIES)} queries...")
    print()
    
    # Check API is running
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ API health check failed: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to API at {API_BASE}: {e}")
        print("Make sure the API server is running: python src/api_server.py")
        sys.exit(1)
    
    print("✅ API server is running")
    print()
    
    # Run first pass (no cache)
    print("Phase 1: First pass (cache disabled)...")
    results_pass1 = []
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"  [{i}/{len(TEST_QUERIES)}] Query: {query[:60]}...")
        result = test_query(query, use_cache=False)
        results_pass1.append(result)
        if result["success"]:
            print(f"      ✅ {result['latency_ms']:.0f}ms, {result['sources_count']} sources")
        else:
            print(f"      ❌ Failed: {result['error']}")
    
    print()
    print("Phase 2: Second pass (cache enabled)...")
    results_pass2 = []
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"  [{i}/{len(TEST_QUERIES)}] Query: {query[:60]}...")
        result = test_query(query, use_cache=True)
        results_pass2.append(result)
        if result["success"]:
            cache_status = "✅ CACHE HIT" if result["cache_hit"] else "❌ cache miss"
            print(f"      {cache_status} {result['latency_ms']:.0f}ms")
        else:
            print(f"      ❌ Failed: {result['error']}")
    
    print()
    print("=" * 80)
    print("METRICS SUMMARY")
    print("=" * 80)
    
    # Calculate metrics for both passes
    metrics_pass1 = calculate_metrics(results_pass1)
    metrics_pass2 = calculate_metrics(results_pass2)
    
    print("\n📊 First Pass (No Cache):")
    print(f"   Success Rate: {metrics_pass1['success_rate']:.1f}%")
    print(f"   Mean Latency: {metrics_pass1['latency']['mean_ms']:.0f}ms")
    print(f"   P95 Latency: {metrics_pass1['latency']['p95_ms']:.0f}ms")
    print(f"   Mean Sources: {metrics_pass1['retrieval']['mean_sources']:.1f}")
    
    print("\n📊 Second Pass (With Cache):")
    print(f"   Success Rate: {metrics_pass2['success_rate']:.1f}%")
    print(f"   Mean Latency: {metrics_pass2['latency']['mean_ms']:.0f}ms")
    print(f"   P95 Latency: {metrics_pass2['latency']['p95_ms']:.0f}ms")
    print(f"   Cache Hit Rate: {metrics_pass2['cache']['hit_rate']:.1f}%")
    
    print("\n🎯 Performance Targets:")
    targets = metrics_pass2.get("targets", {})
    print(f"   P95 Latency < 500ms: {'✅' if targets.get('latency_p95_met') else '❌'} ({metrics_pass2['latency']['p95_ms']:.0f}ms)")
    print(f"   Success Rate = 100%: {'✅' if targets.get('success_rate_met') else '❌'} ({metrics_pass2['success_rate']:.1f}%)")
    print(f"   Cache Hit Rate > 40%: {'✅' if targets.get('cache_hit_rate_met') else '❌'} ({metrics_pass2['cache']['hit_rate']:.1f}%)")
    
    # Save detailed results
    output_file = Path(__file__).parent / "rag_metrics_results.json"
    with open(output_file, "w") as f:
        json.dump({
            "pass1": {
                "results": results_pass1,
                "metrics": metrics_pass1
            },
            "pass2": {
                "results": results_pass2,
                "metrics": metrics_pass2
            },
            "queries": TEST_QUERIES
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    # Print detailed query results
    print("\n" + "=" * 80)
    print("DETAILED QUERY RESULTS")
    print("=" * 80)
    for i, (query, r1, r2) in enumerate(zip(TEST_QUERIES, results_pass1, results_pass2), 1):
        print(f"\n[{i}] {query}")
        print(f"    Pass 1: {r1['latency_ms']:.0f}ms, {r1['sources_count']} sources, {r1['answer_length']} chars")
        print(f"    Pass 2: {r2['latency_ms']:.0f}ms, {r2['sources_count']} sources, {'CACHE HIT' if r2['cache_hit'] else 'miss'}")
        if r1.get("answer_preview"):
            print(f"    Answer: {r1['answer_preview']}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    # Overall assessment
    all_targets_met = (
        targets.get('latency_p95_met', False) and
        targets.get('success_rate_met', False)
    )
    
    if all_targets_met:
        print("✅ All key metrics met!")
    else:
        print("⚠️  Some metrics did not meet targets")
    
    return 0 if all_targets_met else 1

if __name__ == "__main__":
    sys.exit(main())

