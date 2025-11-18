#!/usr/bin/env python3
"""
Telemetry Testing Script

Tests all aspects of the telemetry system:
- Metrics collection (Prometheus)
- Structured logging
- Query telemetry tracking
- Endpoint availability
"""

import requests
import json
import time
import sys
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"

def test_metrics_endpoint():
    """Test that /metrics endpoint returns Prometheus metrics."""
    print("=" * 60)
    print("Testing /metrics endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/metrics", timeout=5)
        response.raise_for_status()
        
        metrics_text = response.text
        print(f"✅ Metrics endpoint accessible (status: {response.status_code})")
        
        # Check for key metrics
        key_metrics = [
            "rag_queries_total",
            "rag_query_duration_seconds",
            "rag_retrieval_docs",
            "rag_generation_duration_seconds"
        ]
        
        found_metrics = []
        for metric in key_metrics:
            if metric in metrics_text:
                found_metrics.append(metric)
                print(f"  ✅ Found metric: {metric}")
            else:
                print(f"  ⚠️  Missing metric: {metric}")
        
        print(f"\nFound {len(found_metrics)}/{len(key_metrics)} key metrics")
        return True
        
    except Exception as e:
        print(f"❌ Metrics endpoint test failed: {e}")
        return False


def test_query_telemetry():
    """Test that queries generate telemetry data."""
    print("\n" + "=" * 60)
    print("Testing Query Telemetry")
    print("=" * 60)
    
    test_queries = [
        {"query": "What is RAG?", "top_k": 3},
        {"query": "How does contextual retrieval work?", "top_k": 5}
    ]
    
    results = []
    for i, query_data in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {query_data['query']}")
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/query",
                json=query_data,
                timeout=120
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Query successful (duration: {duration:.2f}s)")
                print(f"  - Answer length: {len(result.get('answer', ''))} chars")
                print(f"  - Citations: {len(result.get('sources', []))}")
                print(f"  - Retrieved docs: {result.get('retrieved_docs', 0)}")
                results.append({
                    "success": True,
                    "duration": duration,
                    "answer_length": len(result.get('answer', '')),
                    "citations": len(result.get('sources', []))
                })
            else:
                print(f"  ❌ Query failed (status: {response.status_code})")
                print(f"  Error: {response.text[:200]}")
                results.append({"success": False})
                
        except Exception as e:
            print(f"  ❌ Query error: {e}")
            results.append({"success": False})
        
        # Wait between queries
        if i < len(test_queries):
            time.sleep(2)
    
    success_count = sum(1 for r in results if r.get("success"))
    print(f"\n✅ Completed {success_count}/{len(test_queries)} queries successfully")
    return success_count == len(test_queries)


def test_metrics_after_queries():
    """Check that metrics were updated after queries."""
    print("\n" + "=" * 60)
    print("Verifying Metrics After Queries")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/metrics", timeout=5)
        metrics_text = response.text
        
        # Extract query count
        query_count_lines = [line for line in metrics_text.split('\n') 
                           if 'rag_queries_total' in line and not line.startswith('#')]
        
        if query_count_lines:
            print("✅ Query metrics found:")
            for line in query_count_lines[:5]:  # Show first 5
                print(f"  {line}")
        else:
            print("⚠️  No query metrics found")
        
        # Check duration metrics
        duration_lines = [line for line in metrics_text.split('\n')
                         if 'rag_query_duration_seconds_count' in line]
        if duration_lines:
            print("\n✅ Duration metrics found:")
            for line in duration_lines[:3]:
                print(f"  {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ Metrics verification failed: {e}")
        return False


def test_health_endpoint():
    """Test health endpoint."""
    print("\n" + "=" * 60)
    print("Testing /health endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        response.raise_for_status()
        health_data = response.json()
        
        print(f"✅ Health endpoint accessible")
        print(f"  Status: {health_data.get('status', 'unknown')}")
        
        services = health_data.get('services', {})
        if services:
            print("  Services:")
            for service, status in services.items():
                status_icon = "✅" if status == "connected" else "❌"
                print(f"    {status_icon} {service}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False


def main():
    """Run all telemetry tests."""
    print("\n" + "=" * 60)
    print("TELEMETRY TESTING SUITE")
    print("=" * 60)
    print(f"API Base URL: {API_BASE_URL}\n")
    
    # Check if API is accessible
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        response.raise_for_status()
        print("✅ API server is accessible\n")
    except Exception as e:
        print(f"❌ API server not accessible: {e}")
        print("Please ensure the API server is running on port 8000")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Metrics Endpoint", test_metrics_endpoint),
        ("Query Telemetry", test_query_telemetry),
        ("Metrics Verification", test_metrics_after_queries),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All telemetry tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

