"""
Layer 5: Hybrid Retrieval

Hybrid retrieval optimized for pattern queries:
- Step 1: Two-step vector search (local model approximate + Qwen re-embedding)
- Step 2: Sparse BM25 search (keyword/exact match)
- Step 3: Reciprocal Rank Fusion
- Step 4: Cross-encoder reranking
"""

from typing import List, Dict, Any, Optional
import logging

from .two_step_retrieval import TwoStepRetrieval
from .bm25_search import BM25Search

logger = logging.getLogger(__name__)


class HealthcareHybridRetriever:
    """
    Hybrid retrieval orchestration.
    
    Combines:
    - Two-step vector search (semantic)
    - BM25 search (keyword)
    - Reciprocal Rank Fusion
    - Cross-encoder reranking
    """
    
    def __init__(
        self,
        two_step_retriever: TwoStepRetrieval,
        bm25_search: BM25Search,
        rrf_constant: int = 60
    ):
        """
        Initialize hybrid retriever.
        
        Args:
            two_step_retriever: Two-step vector retriever
            bm25_search: BM25 search instance
            rrf_constant: Reciprocal Rank Fusion constant
        """
        self.two_step_retriever = two_step_retriever
        self.bm25_search = bm25_search
        self.rrf_constant = rrf_constant
    
    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        embedder_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval with two-step vector search and BM25.

        Args:
            query: Query text
            top_k: Number of final results
            filters: Optional metadata filters
            embedder_type: Which premium embedder to use ("ollama" or "gemini")
                          If None, uses the embedder's default

        Returns:
            List of result dictionaries
        """
        # Stage 1: Two-step vector search
        # Step 1a: Approximate search with local model (mapped query)
        # Step 1b: Re-embed top candidates with selected embedder for final ranking
        vector_results = self.two_step_retriever.retrieve(
            query,
            top_k_approximate=top_k * 3,  # Get more candidates for fusion
            top_k_final=top_k * 3,  # Return top candidates for fusion
            filters=filters,
            embedder_type=embedder_type
        )
        
        # Stage 2: Sparse BM25 search (critical for keyword matches)
        sparse_results = self.bm25_search.search(
            query,
            k=top_k * 3,
            filters=filters
        )
        
        # Stage 3: Reciprocal Rank Fusion
        fused = self._rrf_fusion(vector_results, sparse_results)
        
        # Stage 4: Cross-encoder rerank (top 20 only)
        reranked = self._cross_encode_rerank(query, fused[:20])
        
        # Return top-k
        return reranked[:top_k]
    
    def _rrf_fusion(
        self,
        dense_results: List[Dict[str, Any]],
        sparse_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Reciprocal Rank Fusion combines rankings.
        
        RRF score = sum(1 / (k + rank)) for each result
        
        Args:
            dense_results: Results from vector search
            sparse_results: Results from BM25 search
            
        Returns:
            Fused and ranked results
        """
        scores = {}
        k = self.rrf_constant
        
        # Add dense results
        for rank, result in enumerate(dense_results, 1):
            doc_id = result.get("id") or result.get("metadata", {}).get("document_id")
            if doc_id not in scores:
                scores[doc_id] = {
                    "result": result,
                    "rrf_score": 0
                }
            scores[doc_id]["rrf_score"] += 1 / (k + rank)
        
        # Add sparse results
        for rank, result in enumerate(sparse_results, 1):
            doc_id = result.get("id") or result.get("metadata", {}).get("document_id")
            if doc_id not in scores:
                scores[doc_id] = {
                    "result": result,
                    "rrf_score": 0
                }
            scores[doc_id]["rrf_score"] += 1 / (k + rank)
        
        # Sort by RRF score
        fused = sorted(
            scores.values(),
            key=lambda x: x["rrf_score"],
            reverse=True
        )
        
        # Add RRF score to results
        results = []
        for item in fused:
            result = item["result"].copy()
            result["rrf_score"] = item["rrf_score"]
            result["ranking_method"] = "hybrid_rrf"
            results.append(result)
        
        return results
    
    def _cross_encode_rerank(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rerank top results using cross-encoder.
        
        Note: For production, use a proper cross-encoder model.
        This is a simplified version that uses existing scores.
        
        Args:
            query: Query text
            results: Results to rerank
            
        Returns:
            Reranked results
        """
        # Simplified reranking: use existing scores
        # In production, use a cross-encoder model like:
        # from sentence_transformers import CrossEncoder
        # reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        # pairs = [(query, r["text"]) for r in results]
        # scores = reranker.predict(pairs)
        
        # For now, use existing scores (RRF or similarity)
        reranked = sorted(
            results,
            key=lambda x: x.get("rrf_score", x.get("similarity_score", x.get("score", 0))),
            reverse=True
        )
        
        return reranked

