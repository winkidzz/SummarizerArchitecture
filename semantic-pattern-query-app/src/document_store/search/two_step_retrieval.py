"""
Two-Step Retrieval Process

Two-step retrieval with model alignment:
1. Approximate search with local model (fast, cost-effective)
2. Re-embed and rank with premium model (Ollama or Gemini) (precise, low volume)
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

from ..embeddings.hybrid_embedder import HealthcareHybridEmbedder
from ..storage.qdrant_store import HealthcareVectorStore

logger = logging.getLogger(__name__)


class TwoStepRetrieval:
    """
    Two-step retrieval process with model alignment.
    
    Process:
    1. Approximate search with local model (fast, cost-effective)
    2. Re-embed top candidates with premium model (Ollama or Gemini) for final ranking (precise)
    """
    
    def __init__(
        self,
        embedder: HealthcareHybridEmbedder,
        vector_store: HealthcareVectorStore
    ):
        """
        Initialize two-step retriever.
        
        Args:
            embedder: Hybrid embedder instance
            vector_store: Qdrant vector store instance
        """
        self.embedder = embedder
        self.vector_store = vector_store
    
    def retrieve(
        self,
        query: str,
        top_k_approximate: int = 50,
        top_k_final: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        embedder_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Two-step retrieval with model alignment.

        Args:
            query: Query text
            top_k_approximate: Number of candidates from approximate search
            top_k_final: Number of final results after re-embedding
            filters: Optional metadata filters
            embedder_type: Which premium embedder to use ("ollama" or "gemini")
                          If None, uses the embedder's default

        Returns:
            List of result dictionaries with text, score, and metadata
        """
        # Step 1: Approximate search with local model
        # Query is mapped to local model space for comparison
        query_embedding_local = self.embedder.embed_query(query, embedder_type=embedder_type)

        # Retrieve candidates using local model embeddings
        candidates = self.vector_store.search(
            query_embedding_local,
            top_k=top_k_approximate,
            filters=filters
        )

        if not candidates:
            logger.warning("No candidates found in approximate search")
            return []

        # Step 2: Re-embed top candidates with premium model for final ranking
        # If premium embeddings fail, fall back to local model similarity
        candidate_texts = [c["text"] for c in candidates]
        try:
            candidate_embeddings_premium, query_embedding_premium = \
                self.embedder.re_embed_candidates(candidate_texts, query, embedder_type=embedder_type)

            # Calculate final similarity scores in premium model space
            similarities = cosine_similarity(
                query_embedding_premium.reshape(1, -1),
                candidate_embeddings_premium
            )[0]

            # Rank by premium model similarity scores
            ranked_indices = np.argsort(similarities)[::-1]
            used_embedder_type = embedder_type or self.embedder.query_embedder_type
            ranking_method = f"{used_embedder_type}_re_embedding"
        except Exception as e:
            used_embedder_type = embedder_type or self.embedder.query_embedder_type
            logger.warning(
                f"Premium ({used_embedder_type}) re-embedding failed ({e}), "
                "using local model scores"
            )
            # Fall back to using existing scores from approximate search
            similarities = np.array([c.get("score", 0.0) for c in candidates])
            ranked_indices = np.argsort(similarities)[::-1]
            ranking_method = "local_approximate"
        
        # Return top-k results
        final_results = []
        for idx in ranked_indices[:top_k_final]:
            result = candidates[idx].copy()
            result["similarity_score"] = float(similarities[idx])
            result["ranking_method"] = ranking_method
            final_results.append(result)
        
        logger.info(
            f"Two-step retrieval: {len(candidates)} candidates -> "
            f"{len(final_results)} final results"
        )
        
        return final_results

