"""
Layer 5: Hybrid Retrieval

Hybrid retrieval optimized for pattern queries:
- Step 1: Two-step vector search (local model approximate + Qwen re-embedding)
- Step 2: Sparse BM25 search (keyword/exact match)
- Step 3: Reciprocal Rank Fusion
- Step 4: Cross-encoder reranking
"""

from typing import List, Dict, Any, Optional, Set
import logging

from .two_step_retrieval import TwoStepRetrieval
from .bm25_search import BM25Search
from ..monitoring.metrics import MetricsCollector
from ..evaluation.ir_metrics import evaluate_retrieval_quality

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
        embedder_type: Optional[str] = None,
        relevant_doc_ids: Optional[Set[str]] = None,
        relevance_scores: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval with two-step vector search and BM25.

        Args:
            query: Query text
            top_k: Number of final results
            filters: Optional metadata filters
            embedder_type: Which premium embedder to use ("ollama" or "gemini")
                          If None, uses the embedder's default
            relevant_doc_ids: Optional ground truth relevant document IDs for IR metrics evaluation
            relevance_scores: Optional graded relevance scores for NDCG calculation

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
        final_results = reranked[:top_k]

        # Evaluate retrieval quality if ground truth is provided
        if relevant_doc_ids:
            self._evaluate_and_record_metrics(
                final_results,
                relevant_doc_ids,
                relevance_scores
            )

        return final_results
    
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

    def _evaluate_and_record_metrics(
        self,
        results: List[Dict[str, Any]],
        relevant_doc_ids: Set[str],
        relevance_scores: Optional[Dict[str, float]] = None
    ):
        """
        Evaluate retrieval quality and record IR metrics to Prometheus.

        This method is called when ground truth relevance judgments are provided
        (typically during testing/evaluation, not production).

        Args:
            results: Retrieved documents
            relevant_doc_ids: Ground truth relevant document IDs
            relevance_scores: Optional graded relevance scores for NDCG
        """
        # Extract retrieved document IDs in ranked order
        retrieved_doc_ids = []
        for result in results:
            doc_id = result.get("id") or result.get("metadata", {}).get("document_id")
            if doc_id:
                retrieved_doc_ids.append(doc_id)

        if not retrieved_doc_ids:
            logger.warning("No document IDs found in results for IR metrics evaluation")
            return

        # Evaluate all IR metrics
        try:
            metrics = evaluate_retrieval_quality(
                retrieved_doc_ids=retrieved_doc_ids,
                relevant_doc_ids=relevant_doc_ids,
                relevance_scores=relevance_scores,
                k_values=[1, 3, 5, 10]
            )

            # Record metrics to Prometheus
            MetricsCollector.record_ir_metrics(
                precision_at_k=metrics['precision@k'],
                recall_at_k=metrics['recall@k'],
                hit_rate_at_k=metrics['hit_rate@k'],
                mrr=metrics['mrr'],
                map_score=metrics['map'],
                ndcg_at_k=metrics['ndcg@k']
            )

            logger.info(
                f"IR Metrics - Precision@5: {metrics['precision@k'].get(5, 0):.3f}, "
                f"Recall@5: {metrics['recall@k'].get(5, 0):.3f}, "
                f"NDCG@5: {metrics['ndcg@k'].get(5, 0):.3f}, "
                f"MRR: {metrics['mrr']:.3f}, "
                f"MAP: {metrics['map']:.3f}"
            )

        except Exception as e:
            logger.error(f"Failed to evaluate IR metrics: {e}", exc_info=True)

