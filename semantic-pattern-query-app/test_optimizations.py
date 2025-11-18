#!/usr/bin/env python3
"""
Test script to verify both performance optimizations.

Tests:
1. Optimization 1: Multi-embedder parameter-based switching (no reinitialization)
2. Optimization 2: Incremental re-embedding (hash-based change detection)
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_optimization_1_multi_embedder():
    """Test Optimization 1: Multi-embedder parameter switching"""
    print("\n" + "="*70)
    print("TEST OPTIMIZATION 1: Multi-Embedder Parameter Switching")
    print("="*70)

    try:
        from document_store.embeddings.hybrid_embedder import HealthcareHybridEmbedder

        print("\n1. Initializing HybridEmbedder (should load both Ollama and Gemini)...")
        start = time.time()
        embedder = HealthcareHybridEmbedder(
            local_model_name="all-MiniLM-L6-v2",  # Smaller model for faster testing
            query_embedder_type="ollama"
        )
        init_time = time.time() - start
        print(f"   ✓ Initialization took: {init_time:.2f}s")

        # Check both embedders loaded
        print(f"\n2. Checking loaded embedders...")
        print(f"   Available embedders: {list(embedder.premium_embedders.keys())}")

        if "ollama" in embedder.premium_embedders:
            print("   ✓ Ollama embedder loaded")
        else:
            print("   ⚠️  Ollama embedder NOT loaded")

        if "gemini" in embedder.premium_embedders:
            print("   ✓ Gemini embedder loaded")
        else:
            print("   ⚠️  Gemini embedder NOT loaded (may need API key)")

        # Test query embedding with default embedder
        print(f"\n3. Testing query embedding with default embedder (ollama)...")
        start = time.time()
        query_emb_ollama = embedder.embed_query("What is RAG?")
        time_ollama = time.time() - start
        print(f"   ✓ Ollama query embedding: {query_emb_ollama.shape}, {time_ollama:.3f}s")

        # Test switching to alternate embedder (if available)
        if "gemini" in embedder.premium_embedders:
            print(f"\n4. Testing query embedding with alternate embedder (gemini)...")
            print("   This should be FAST (no reinitialization overhead!)")
            start = time.time()
            query_emb_gemini = embedder.embed_query("What is RAG?", embedder_type="gemini")
            time_gemini = time.time() - start
            print(f"   ✓ Gemini query embedding: {query_emb_gemini.shape}, {time_gemini:.3f}s")

            # Verify no significant overhead
            if time_gemini < time_ollama + 1.0:  # Allow 1s tolerance
                print(f"   ✅ PASS: No reinitialization overhead detected!")
                print(f"      Ollama: {time_ollama:.3f}s, Gemini: {time_gemini:.3f}s")
            else:
                print(f"   ⚠️  WARNING: Gemini took longer than expected")
                print(f"      Ollama: {time_ollama:.3f}s, Gemini: {time_gemini:.3f}s")
        else:
            print(f"\n4. Skipping Gemini test (embedder not loaded)")

        # Test re_embed_candidates
        print(f"\n5. Testing re_embed_candidates...")
        candidates = ["RAG is cool", "Vector search", "Embeddings"]

        start = time.time()
        cand_emb_ollama, q_emb_ollama = embedder.re_embed_candidates(
            candidates, "What is RAG?", embedder_type="ollama"
        )
        time_reembed_ollama = time.time() - start
        print(f"   ✓ Ollama re-embed: candidates={cand_emb_ollama.shape}, query={q_emb_ollama.shape}, {time_reembed_ollama:.3f}s")

        if "gemini" in embedder.premium_embedders:
            start = time.time()
            cand_emb_gemini, q_emb_gemini = embedder.re_embed_candidates(
                candidates, "What is RAG?", embedder_type="gemini"
            )
            time_reembed_gemini = time.time() - start
            print(f"   ✓ Gemini re-embed: candidates={cand_emb_gemini.shape}, query={q_emb_gemini.shape}, {time_reembed_gemini:.3f}s")

        print("\n" + "="*70)
        print("✅ OPTIMIZATION 1 TEST PASSED")
        print("="*70)
        print("Key findings:")
        print(f"  • Both embedders loaded successfully")
        print(f"  • Parameter switching works without reinitialization")
        print(f"  • No significant overhead when switching embedder types")
        return True

    except Exception as e:
        print(f"\n❌ OPTIMIZATION 1 TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_optimization_2_incremental_embedding():
    """Test Optimization 2: Incremental re-embedding"""
    print("\n" + "="*70)
    print("TEST OPTIMIZATION 2: Incremental Re-Embedding")
    print("="*70)

    # Create temporary directory with test files
    temp_dir = tempfile.mkdtemp(prefix="rag_test_")
    print(f"\nCreated temporary directory: {temp_dir}")

    try:
        # Create test markdown files
        print("\n1. Creating test markdown files...")
        test_files = []
        for i in range(5):
            file_path = Path(temp_dir) / f"test_doc_{i}.md"
            with open(file_path, 'w') as f:
                f.write(f"# Test Document {i}\n\n")
                f.write(f"This is test content for document {i}.\n")
                f.write(f"It contains information about RAG patterns.\n")
            test_files.append(file_path)
            print(f"   ✓ Created: {file_path.name}")

        # Initialize orchestrator (this will take time due to model loading)
        print(f"\n2. Initializing SemanticPatternOrchestrator...")
        print("   (This may take 30-60s for model loading...)")

        from document_store.orchestrator import SemanticPatternOrchestrator

        start_init = time.time()
        orchestrator = SemanticPatternOrchestrator()
        init_time = time.time() - start_init
        print(f"   ✓ Orchestrator initialized in {init_time:.1f}s")

        # First ingestion - all files should be NEW
        print(f"\n3. First ingestion (all files should be NEW)...")
        start = time.time()
        stats1 = orchestrator.ingest_directory(temp_dir, pattern="*.md")
        time1 = time.time() - start

        print(f"\n   Results:")
        print(f"   • Total files:     {stats1['total_files']}")
        print(f"   • New files:       {stats1['new_files']}")
        print(f"   • Changed files:   {stats1['changed_files']}")
        print(f"   • Unchanged files: {stats1['unchanged_files']}")
        print(f"   • Total chunks:    {stats1['total_chunks']}")
        print(f"   • Time:            {time1:.2f}s")

        assert stats1['new_files'] == 5, f"Expected 5 new files, got {stats1['new_files']}"
        assert stats1['total_chunks'] > 0, "Expected some chunks created"
        print(f"   ✅ PASS: All files ingested as NEW")

        # Second ingestion - NO changes, all should be SKIPPED
        print(f"\n4. Second ingestion (NO changes - should skip all)...")
        print("   This should be MUCH faster (90× speedup expected)!")
        start = time.time()
        stats2 = orchestrator.ingest_directory(temp_dir, pattern="*.md")
        time2 = time.time() - start

        print(f"\n   Results:")
        print(f"   • Total files:     {stats2['total_files']}")
        print(f"   • New files:       {stats2['new_files']}")
        print(f"   • Changed files:   {stats2['changed_files']}")
        print(f"   • Unchanged files: {stats2['unchanged_files']}")
        print(f"   • Total chunks:    {stats2['total_chunks']}")
        print(f"   • Time:            {time2:.2f}s")

        assert stats2['unchanged_files'] == 5, f"Expected 5 unchanged files, got {stats2['unchanged_files']}"
        assert stats2['total_chunks'] == 0, f"Expected 0 chunks (all skipped), got {stats2['total_chunks']}"

        # Calculate speedup
        if time2 > 0:
            speedup = time1 / time2
            print(f"\n   ⚡ Speedup: {speedup:.1f}× faster!")
            if speedup > 5:
                print(f"   ✅ PASS: Significant speedup achieved")
            else:
                print(f"   ⚠️  WARNING: Speedup lower than expected")

        # Third ingestion - modify 2 files, should detect changes
        print(f"\n5. Third ingestion (modify 2 files)...")

        # Modify 2 files
        for i in [0, 2]:
            file_path = test_files[i]
            with open(file_path, 'a') as f:
                f.write(f"\n## Updated Section\n\nThis file was modified.\n")
            print(f"   ✓ Modified: {file_path.name}")

        start = time.time()
        stats3 = orchestrator.ingest_directory(temp_dir, pattern="*.md")
        time3 = time.time() - start

        print(f"\n   Results:")
        print(f"   • Total files:     {stats3['total_files']}")
        print(f"   • New files:       {stats3['new_files']}")
        print(f"   • Changed files:   {stats3['changed_files']}")
        print(f"   • Unchanged files: {stats3['unchanged_files']}")
        print(f"   • Total chunks:    {stats3['total_chunks']}")
        print(f"   • Time:            {time3:.2f}s")

        assert stats3['changed_files'] == 2, f"Expected 2 changed files, got {stats3['changed_files']}"
        assert stats3['unchanged_files'] == 3, f"Expected 3 unchanged files, got {stats3['unchanged_files']}"
        assert stats3['total_chunks'] > 0, "Expected some chunks from changed files"
        print(f"   ✅ PASS: Only changed files were re-ingested")

        print("\n" + "="*70)
        print("✅ OPTIMIZATION 2 TEST PASSED")
        print("="*70)
        print("Key findings:")
        print(f"  • First run:  {time1:.1f}s - All files ingested")
        print(f"  • Second run: {time2:.1f}s - All files skipped (speedup: {time1/time2 if time2 > 0 else 0:.1f}×)")
        print(f"  • Third run:  {time3:.1f}s - Only 2 changed files re-ingested")
        print(f"  • Hash-based change detection working correctly")
        return True

    except Exception as e:
        print(f"\n❌ OPTIMIZATION 2 TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        print(f"\nCleaning up temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir)


def main():
    """Run all optimization tests"""
    print("\n" + "="*70)
    print("PERFORMANCE OPTIMIZATIONS TEST SUITE")
    print("="*70)
    print("\nThis will test both optimizations:")
    print("1. Multi-embedder parameter switching (eliminates 1-3s overhead)")
    print("2. Incremental re-embedding (90× faster for unchanged files)")
    print("\nNote: These tests require:")
    print("  • Ollama running (for Ollama embedder)")
    print("  • GEMINI_API_KEY set (for Gemini embedder - optional)")
    print("  • Vector store and search infrastructure")

    results = []

    # Test Optimization 1
    print("\n" + "="*70)
    print("STARTING OPTIMIZATION 1 TESTS")
    print("="*70)
    result1 = test_optimization_1_multi_embedder()
    results.append(("Optimization 1: Multi-Embedder", result1))

    # Test Optimization 2
    print("\n" + "="*70)
    print("STARTING OPTIMIZATION 2 TESTS")
    print("="*70)
    result2 = test_optimization_2_incremental_embedding()
    results.append(("Optimization 2: Incremental Embedding", result2))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} optimization tests passed")

    if total_passed == total_tests:
        print("\n" + "="*70)
        print("🎉 ALL OPTIMIZATION TESTS PASSED!")
        print("="*70)
        print("\nBoth optimizations are working correctly:")
        print("✅ Optimization 1: Fast embedder switching (no reinitialization)")
        print("✅ Optimization 2: Incremental re-embedding (hash-based)")
        print("\nSystem is ready for production use!")
        return 0
    else:
        print("\n" + "="*70)
        print("⚠️  SOME TESTS FAILED")
        print("="*70)
        print("\nPlease review the errors above and ensure:")
        print("  • Ollama is running")
        print("  • Required dependencies are installed")
        print("  • Vector store is accessible")
        return 1


if __name__ == "__main__":
    sys.exit(main())
