"""
Layer 5: Hybrid Retrieval

Hybrid retrieval optimized for pattern queries with 3-tier architecture:
- Step 1: Two-step vector search (local model approximate + Qwen re-embedding)
- Step 2: Sparse BM25 search (keyword/exact match)
- Step 2.5: Web Knowledge Base search (Tier 2 - cached web results, Phase 2)
- Step 3: Live Web search (Tier 3 - optional, conditional, Phase 1)
- Step 4: Multi-tier Reciprocal Rank Fusion (with weights: 1.0, 0.9, 0.7)
- Step 5: Cross-encoder reranking

3-Tier Architecture:
- 🏠 Tier 1: Pattern Library (Weight 1.0) - Curated patterns
- 📚 Tier 2: Web Knowledge Base (Weight 0.9) - Cached web results with audit trail
- 🌐 Tier 3: Live Web Search (Weight 0.7) - Only if Tier 1+2 insufficient
"""

from typing import List, Dict, Any, Optional, Set, TYPE_CHECKING
import logging

from .two_step_retrieval import TwoStepRetrieval
from .bm25_search import BM25Search
from ..monitoring.metrics import MetricsCollector
from ..evaluation.ir_metrics import evaluate_retrieval_quality

if TYPE_CHECKING:
    from ..web.providers import WebSearchProvider, WebSearchResult

logger = logging.getLogger(__name__)


class HealthcareHybridRetriever:
    """
    Hybrid retrieval orchestration with 3-tier architecture.

    Combines:
    - Two-step vector search (semantic)
    - BM25 search (keyword)
    - Web Knowledge Base (Tier 2 - cached web results with audit trail)
    - Live Web search (Tier 3 - optional, conditional)
    - Multi-tier Reciprocal Rank Fusion (weighted: 1.0, 0.9, 0.7)
    - Cross-encoder reranking
    """

    def __init__(
        self,
        two_step_retriever: TwoStepRetrieval,
        bm25_search: BM25Search,
        web_search_provider: Optional['WebSearchProvider'] = None,
        web_kb_manager: Optional[Any] = None,
        rrf_constant: int = 60
    ):
        """
        Initialize hybrid retriever.

        Args:
            two_step_retriever: Two-step vector retriever
            bm25_search: BM25 search instance
            web_search_provider: Optional web search provider (Tier 3: Live Web)
            web_kb_manager: Optional Web Knowledge Base manager (Tier 2: Cached Web)
            rrf_constant: Reciprocal Rank Fusion constant
        """
        self.two_step_retriever = two_step_retriever
        self.bm25_search = bm25_search
        self.web_search_provider = web_search_provider
        self.web_kb_manager = web_kb_manager
        self.rrf_constant = rrf_constant

        if web_kb_manager:
            logger.info("Web Knowledge Base (Tier 2) enabled in hybrid retriever")
        if web_search_provider:
            logger.info("Live Web search (Tier 3) enabled in hybrid retriever")
        if not web_kb_manager and not web_search_provider:
            logger.info("Web search disabled (no providers configured)")
    
    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        embedder_type: Optional[str] = None,
        relevant_doc_ids: Optional[Set[str]] = None,
        relevance_scores: Optional[Dict[str, float]] = None,
        # Web search parameters (Phase 1)
        enable_web_search: bool = False,
        web_mode: str = "on_low_confidence"  # "parallel" or "on_low_confidence"
    ) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval with optional web search.

        Args:
            query: Query text
            top_k: Number of final results
            filters: Optional metadata filters
            embedder_type: Which premium embedder to use ("ollama" or "gemini")
                          If None, uses the embedder's default
            relevant_doc_ids: Optional ground truth relevant document IDs for IR metrics evaluation
            relevance_scores: Optional graded relevance scores for NDCG calculation
            enable_web_search: Enable live web search (default: False)
            web_mode: Web search mode - "parallel" (always) or "on_low_confidence" (conditional)

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

        # Stage 2.5: Web Knowledge Base search (Tier 2 - Phase 2)
        web_kb_results = []
        if enable_web_search and self.web_kb_manager:
            try:
                import time
                start_time = time.time()

                # Search cached web knowledge base
                web_kb_results = self.web_kb_manager.search(
                    query,
                    top_k=top_k * 3
                )

                duration = time.time() - start_time

                logger.info(
                    f"Web KB (Tier 2) search returned {len(web_kb_results)} cached results "
                    f"(duration: {duration:.2f}s)"
                )

                # Record metrics
                MetricsCollector.web_search_queries.labels(
                    mode="web_kb",
                    status="success"
                ).inc()
                MetricsCollector.web_search_results.observe(len(web_kb_results))

            except Exception as e:
                logger.error(f"Web KB search failed: {e}")
                MetricsCollector.web_search_queries.labels(
                    mode="web_kb",
                    status="error"
                ).inc()

        # Stage 3: Live Web search (Tier 3 - Phase 1)
        # Only trigger if Web KB results insufficient
        web_results = []
        logger.info(f"Web search check - enable_web_search={enable_web_search}, has_provider={self.web_search_provider is not None}, mode={web_mode}")
        if enable_web_search and self.web_search_provider:
            should_search_web = self._should_trigger_web_search(
                query,
                vector_results,
                sparse_results,
                web_kb_results,  # Consider Web KB results
                mode=web_mode
            )
            logger.info(f"Web search trigger decision: {should_search_web} (mode={web_mode})")

            if should_search_web:
                try:
                    import time
                    start_time = time.time()

                    web_search_results = self.web_search_provider.search(
                        query,
                        max_results=top_k
                    )

                    # Convert WebSearchResult to retrieval format
                    web_results = self._normalize_web_results(web_search_results)

                    duration = time.time() - start_time

                    logger.info(
                        f"Web search returned {len(web_results)} results "
                        f"(mode: {web_mode}, duration: {duration:.2f}s)"
                    )

                    # Record metrics
                    MetricsCollector.web_search_queries.labels(
                        mode=web_mode,
                        status="success"
                    ).inc()

                    MetricsCollector.web_search_results.observe(len(web_results))
                    MetricsCollector.web_search_duration.labels(
                        provider="duckduckgo"
                    ).observe(duration)

                    # Record trust scores
                    for result in web_results:
                        trust_score = result.get("metadata", {}).get("trust_score", 0.5)
                        MetricsCollector.web_search_trust_scores.observe(trust_score)

                    # Phase 2: Auto-ingest live web results into Web KB for future queries
                    if self.web_kb_manager and web_search_results:
                        try:
                            ingest_start = time.time()
                            ingested_count = self.web_kb_manager.ingest_web_results(
                                web_search_results,
                                query=query
                            )
                            ingest_duration = time.time() - ingest_start

                            logger.info(
                                f"Auto-ingested {ingested_count} live web results into Web KB "
                                f"(duration: {ingest_duration:.2f}s)"
                            )
                        except Exception as e:
                            logger.error(f"Auto-ingestion to Web KB failed: {e}")

                except Exception as e:
                    logger.error(f"Web search failed: {e}")
                    MetricsCollector.web_search_queries.labels(
                        mode=web_mode,
                        status="error"
                    ).inc()

        # Stage 4: Multi-tier Reciprocal Rank Fusion (Phase 2: 3-tier architecture)
        sources = {
            "vector": (vector_results, 1.0),   # Tier 1: Pattern Library (vector)
            "sparse": (sparse_results, 1.0),   # Tier 1: Pattern Library (BM25)
        }

        # Add Web KB results (Tier 2) with weight 0.9
        if web_kb_results:
            sources["web_kb"] = (web_kb_results, 0.9)

        # Add live web results (Tier 3) with weight 0.7
        if web_results:
            sources["web_live"] = (web_results, 0.7)

        fused = self._rrf_fusion_multi(sources)

        # Stage 5: Cross-encoder rerank (top 20 only)
        reranked = self._cross_encode_rerank(query, fused[:20])

        # Return top-k
        final_results = reranked[:top_k]

        # Calculate and record web source ratio
        if web_results:
            web_count = sum(1 for r in final_results
                          if r.get("metadata", {}).get("source_type") == "web_search")
            web_ratio = web_count / len(final_results) if final_results else 0
            MetricsCollector.web_source_ratio.observe(web_ratio)

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

    def _should_trigger_web_search(
        self,
        query: str,
        vector_results: List[Dict[str, Any]],
        sparse_results: List[Dict[str, Any]],
        web_kb_results: List[Dict[str, Any]],
        mode: str
    ) -> bool:
        """
        Determine if web search should be triggered.

        Phase 2: Also considers Web KB results - only trigger live web if
        Pattern Library (Tier 1) AND Web KB (Tier 2) are insufficient.

        Args:
            query: Query text
            vector_results: Vector search results (Tier 1)
            sparse_results: BM25 search results (Tier 1)
            web_kb_results: Web Knowledge Base results (Tier 2)
            mode: "parallel" (always) or "on_low_confidence" (conditional)

        Returns:
            True if web search should be triggered
        """
        if mode == "parallel":
            return True

        elif mode == "on_low_confidence":
            # Phase 2: If Web KB has good results, skip live web search
            if web_kb_results and len(web_kb_results) >= 3:
                avg_kb_score = sum(
                    r.get("similarity_score", r.get("score", 0))
                    for r in web_kb_results[:5]
                ) / min(5, len(web_kb_results))

                if avg_kb_score >= 0.5:
                    logger.info(
                        f"Web KB (Tier 2) has good results ({avg_kb_score:.3f}), "
                        "skipping live web search (Tier 3)"
                    )
                    return False

            # Check for low confidence indicators

            # 1. Check vector search scores
            if vector_results:
                avg_vector_score = sum(
                    r.get("similarity_score", r.get("score", 0))
                    for r in vector_results[:5]
                ) / min(5, len(vector_results))

                if avg_vector_score < 0.5:
                    logger.info(
                        f"Low vector confidence ({avg_vector_score:.3f}), "
                        "triggering live web search (Tier 3)"
                    )
                    return True

            # 2. Check for temporal keywords
            temporal_keywords = [
                "latest", "recent", "current", "2025", "2024",
                "new", "updated", "now", "today"
            ]
            if any(keyword in query.lower() for keyword in temporal_keywords):
                logger.info(
                    "Temporal keyword detected, triggering live web search (Tier 3)"
                )
                return True

            # 3. Check for few results across ALL tiers
            total_results = len(vector_results) + len(sparse_results) + len(web_kb_results)
            if total_results < 3:
                logger.info(
                    f"Few results across all tiers ({total_results}), "
                    "triggering live web search (Tier 3)"
                )
                return True

            return False

        return False

    def _normalize_web_results(
        self,
        web_results: List['WebSearchResult']
    ) -> List[Dict[str, Any]]:
        """
        Convert WebSearchResult to retrieval format.

        Matches the format used by vector and BM25 retrievers for RRF fusion.

        Args:
            web_results: List of WebSearchResult objects

        Returns:
            List of normalized result dictionaries
        """
        normalized = []

        for result in web_results:
            # Format content as title + snippet
            content = f"{result.title}\n\n{result.snippet}\n\nSource: {result.url}"

            normalized.append({
                "id": f"web_{hash(result.url)}",  # Unique ID based on URL
                "text": content,
                "score": result.trust_score,  # Use trust score as relevance
                "similarity_score": result.trust_score,
                "metadata": {
                    "source_type": "web_search",
                    "title": result.title,
                    "url": result.url,
                    "domain": result.domain,
                    "provider": result.provider,
                    "trust_score": result.trust_score,
                    "rank": result.rank,
                    "retrieved_at": result.retrieved_at.isoformat() if result.retrieved_at else None,
                    **result.metadata
                }
            })

        return normalized

    def _rrf_fusion_multi(
        self,
        sources: Dict[str, tuple[List[Dict[str, Any]], float]]
    ) -> List[Dict[str, Any]]:
        """
        Multi-source Reciprocal Rank Fusion with weights.

        Extends the existing RRF implementation to handle 3+ sources with different weights.

        Args:
            sources: Dict of {source_name: (results, weight)}
                    Example: {"vector": (results, 1.0), "web_live": (results, 0.7)}

        Returns:
            Fused and ranked results
        """
        scores = {}
        k = self.rrf_constant

        for source_name, (results, weight) in sources.items():
            for rank, result in enumerate(results, 1):
                doc_id = result.get("id") or result.get("metadata", {}).get("document_id")

                if doc_id not in scores:
                    scores[doc_id] = {
                        "result": result,
                        "rrf_score": 0,
                        "sources": []
                    }

                # Weighted RRF: weight / (k + rank)
                rrf_contribution = weight / (k + rank)
                scores[doc_id]["rrf_score"] += rrf_contribution
                scores[doc_id]["sources"].append({
                    "name": source_name,
                    "rank": rank,
                    "weight": weight,
                    "contribution": rrf_contribution
                })

        # Sort by RRF score
        fused = sorted(
            scores.values(),
            key=lambda x: x["rrf_score"],
            reverse=True
        )

        # Add RRF metadata to results
        results = []
        for item in fused:
            result = item["result"].copy()
            result["rrf_score"] = item["rrf_score"]
            result["ranking_method"] = "hybrid_rrf_multi"
            result["rrf_sources"] = item["sources"]
            results.append(result)

        return results

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

