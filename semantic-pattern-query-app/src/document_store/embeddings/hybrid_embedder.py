"""
Layer 3: Hybrid Embedding Strategy

Two-step cost-optimized embedding strategy:
- Step 1: Local model for bulk document indexing (FREE)
- Step 2: Premium embeddings for queries and re-embedding top candidates
  - Choice between Ollama Qwen or Google Gemini (configurable via API parameter)
- Model alignment calibration for two-step retrieval
"""

from typing import List, Tuple, Optional, Literal
import numpy as np
import os
import logging

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

from .qwen_embedder import QwenEmbedder
from .gemini_embedder import GeminiEmbedder

logger = logging.getLogger(__name__)


class HealthcareHybridEmbedder:
    """
    Two-step cost-optimized embedding strategy.
    
    - Step 1: Local model for bulk document indexing and approximate search (FREE)
    - Step 2: Premium embeddings for query embedding and re-embedding top candidates
      - Supports both Ollama Qwen and Google Gemini (configurable)
    - Models are aligned through calibration tests
    """
    
    def __init__(
        self,
        local_model_name: str = "all-MiniLM-L12-v2",
        query_embedder_type: Literal["ollama", "gemini"] = "ollama",
        qwen_model: str = "qwen3:14b",
        ollama_base_url: str = "http://localhost:11434",
        gemini_model: str = "models/embedding-001",
        gemini_api_key: Optional[str] = None
    ):
        """
        Initialize hybrid embedder.
        
        Args:
            local_model_name: Local embedding model name
            query_embedder_type: Which premium embedder to use for queries ("ollama" or "gemini")
            qwen_model: Ollama Qwen model name (used if query_embedder_type="ollama")
            ollama_base_url: Ollama API base URL
            gemini_model: Gemini embedding model name (used if query_embedder_type="gemini")
            gemini_api_key: Google AI API key (default: from GEMINI_API_KEY env var)
        """
        # Fast local model for bulk indexing and approximate search
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Install it with: pip install sentence-transformers"
            )
        
        self.local_model = SentenceTransformer(local_model_name)
        self.local_dimension = self.local_model.get_sentence_embedding_dimension()

        # Premium embedders - load BOTH for fast switching
        self.query_embedder_type = query_embedder_type  # default type
        self.premium_embedders = {}  # dictionary of embedders

        # Load Ollama embedder
        try:
            self.premium_embedders["ollama"] = QwenEmbedder(
                model=qwen_model,
                base_url=ollama_base_url
            )
            logger.info(f"✓ Loaded Ollama embedder: {qwen_model}")
        except Exception as e:
            logger.warning(f"Could not load Ollama embedder: {e}")

        # Load Gemini embedder
        try:
            self.premium_embedders["gemini"] = GeminiEmbedder(
                model=gemini_model,
                api_key=gemini_api_key
            )
            logger.info(f"✓ Loaded Gemini embedder: {gemini_model}")
        except Exception as e:
            logger.warning(f"Could not load Gemini embedder: {e}")

        # Verify at least one embedder is available
        if not self.premium_embedders:
            raise ValueError("No premium embedders available - both Ollama and Gemini failed to load")

        # Set premium dimension from default embedder
        default_embedder = self.premium_embedders.get(query_embedder_type)
        if not default_embedder:
            # Fall back to first available embedder
            query_embedder_type = list(self.premium_embedders.keys())[0]
            default_embedder = self.premium_embedders[query_embedder_type]
            logger.warning(f"Requested embedder type '{self.query_embedder_type}' not available, using '{query_embedder_type}'")
            self.query_embedder_type = query_embedder_type

        self.premium_dimension = default_embedder.embedding_dimension

        # Model alignment calibration - load for ALL embedders
        self.alignment_matrices = {}
        for embedder_type in self.premium_embedders.keys():
            matrix = self._load_alignment_matrix(embedder_type)
            if matrix is not None:
                self.alignment_matrices[embedder_type] = matrix

        logger.info(
            f"HybridEmbedder initialized: "
            f"local={local_model_name} (dim={self.local_dimension}), "
            f"premium_embedders={list(self.premium_embedders.keys())}, "
            f"default={self.query_embedder_type} (dim={self.premium_dimension})"
        )
    
    def embed_documents(
        self,
        texts: List[str],
        doc_type: Optional[str] = None,
        metadata: Optional[List[dict]] = None
    ) -> np.ndarray:
        """
        Step 1: Embed documents with local model for indexing.
        All documents use local model for initial approximate search.
        
        Args:
            texts: List of texts to embed
            doc_type: Optional document type
            metadata: Optional metadata list
            
        Returns:
            numpy array of embeddings (n_texts, local_dimension)
        """
        # Normalize local model embeddings for alignment
        embeddings = self.local_model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32,
            normalize_embeddings=True  # Critical for alignment
        )
        return embeddings
    
    def embed_query(self, query: str, embedder_type: Optional[str] = None) -> np.ndarray:
        """
        Embed query with premium model, then map to local space for approximate search.
        Follows the architecture pattern: premium embedding → calibration mapping → local space.

        Args:
            query: Query text
            embedder_type: Which premium embedder to use ("ollama" or "gemini")
                          If None, uses the default (self.query_embedder_type)

        Returns:
            Query embedding mapped to local model space (for approximate search)
        """
        # Use specified embedder type or default
        embedder_type = embedder_type or self.query_embedder_type

        # Get embedder from dictionary
        premium_embedder = self.premium_embedders.get(embedder_type)
        if not premium_embedder:
            raise ValueError(
                f"Embedder type '{embedder_type}' not available. "
                f"Available types: {list(self.premium_embedders.keys())}"
            )

        # Step 1: Embed with selected premium model
        premium_embedding = premium_embedder.embed_query(query)

        # Step 2: Map to local space using calibration matrix for this embedder type
        mapped_embedding = self._map_to_local_space(
            premium_embedding,
            query,
            embedder_type=embedder_type
        )

        return mapped_embedding
    
    def _map_to_local_space(
        self,
        premium_embedding: np.ndarray,
        query: str = None,
        embedder_type: Optional[str] = None
    ) -> np.ndarray:
        """
        Map premium embedding to local model space using calibration matrix.
        This allows approximate search in the local model's vector space.

        Args:
            premium_embedding: Embedding from premium model (Ollama or Gemini)
            query: Original query text (for fallback)
            embedder_type: Which embedder type was used (for selecting calibration matrix)

        Returns:
            Embedding mapped to local model space (384 dim)
        """
        embedder_type = embedder_type or self.query_embedder_type

        # Get embedder-specific calibration matrix
        alignment_matrix = self.alignment_matrices.get(embedder_type)

        if alignment_matrix is not None:
            # Apply alignment matrix from calibration tests
            # Project premium embedding to local space
            mapped = np.dot(premium_embedding, alignment_matrix)
            # Normalize to match local model normalization
            norm = np.linalg.norm(mapped)
            if norm > 0:
                mapped = mapped / norm
            return mapped
        else:
            # Fallback: use local model for query if calibration not available
            logger.warning(
                f"Calibration matrix not available for {embedder_type}. "
                "Falling back to local model for query embedding."
            )
            if query is not None:
                return self.local_model.encode([query], normalize_embeddings=True)[0]
            else:
                # If no query provided, return zero vector (shouldn't happen)
                return np.zeros(self.local_dimension)
    
    def re_embed_candidates(
        self,
        candidate_texts: List[str],
        query: str,
        embedder_type: Optional[str] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Step 2: Re-embed top candidates with premium model for final ranking.
        This provides precision after approximate search.
        Uses the configured premium embedder (Ollama or Gemini).

        Args:
            candidate_texts: List of candidate texts to re-embed
            query: Original query text
            embedder_type: Which premium embedder to use ("ollama" or "gemini")
                          If None, uses the default (self.query_embedder_type)

        Returns:
            Tuple of (candidate_embeddings, query_embedding) in premium model space
        """
        # Use specified embedder type or default
        embedder_type = embedder_type or self.query_embedder_type

        # Get embedder from dictionary
        premium_embedder = self.premium_embedders.get(embedder_type)
        if not premium_embedder:
            raise ValueError(
                f"Embedder type '{embedder_type}' not available. "
                f"Available types: {list(self.premium_embedders.keys())}"
            )

        # Re-embed candidates with selected premium model
        candidate_embeddings = premium_embedder.embed(candidate_texts)

        # Re-embed query with selected premium model for final similarity check
        query_embedding = premium_embedder.embed_query(query)

        return candidate_embeddings, query_embedding
    
    
    def _load_alignment_matrix(self, embedder_type: str) -> Optional[np.ndarray]:
        """
        Load alignment matrix for specific embedder type.
        Calibration tests map premium embeddings (Ollama or Gemini) to local model space.

        Args:
            embedder_type: "ollama" or "gemini"

        Returns:
            Alignment matrix or None if not available
        """
        # Try embedder-specific calibration matrix
        embedder_specific_path = os.getenv(
            f"EMBEDDING_ALIGNMENT_MATRIX_PATH_{embedder_type.upper()}",
            f"alignment_matrix_{embedder_type}.npy"
        )

        if embedder_specific_path and os.path.exists(embedder_specific_path):
            try:
                matrix = np.load(embedder_specific_path)
                logger.info(
                    f"Loaded alignment matrix from {embedder_specific_path} "
                    f"for {embedder_type}"
                )
                return matrix
            except Exception as e:
                logger.warning(f"Could not load alignment matrix from {embedder_specific_path}: {e}")

        logger.info(
            f"No calibration matrix found for {embedder_type}. "
            "Will use fallback to local model for query embedding."
        )
        return None
    
    def calibrate_models(
        self,
        sample_texts: List[str],
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """
        Calibrate models by mapping premium embeddings to local model space.
        Run this once with representative sample texts to create alignment matrix.
        Creates embedder-specific calibration matrix.
        
        Args:
            sample_texts: Representative sample texts for calibration
            output_path: Optional path to save alignment matrix
                If None, uses embedder-specific default path
        
        Returns:
            Alignment matrix
        """
        logger.info(
            f"Calibrating {self.query_embedder_type} model with {len(sample_texts)} sample texts..."
        )
        
        # Embed with local model
        local_embeddings = self.local_model.encode(
            sample_texts,
            normalize_embeddings=True
        )
        
        # Embed with premium model (Ollama or Gemini)
        premium_embedder = self.premium_embedders.get(self.query_embedder_type)
        if not premium_embedder:
            raise ValueError(f"No embedder available for type: {self.query_embedder_type}")
        premium_embeddings = premium_embedder.embed(sample_texts)
        
        # Compute alignment matrix using least squares
        # Maps premium space to local model space
        if premium_embeddings.shape[1] != local_embeddings.shape[1]:
            # If dimensions don't match, use pseudo-inverse
            logger.warning(
                f"Dimension mismatch: {self.query_embedder_type}={premium_embeddings.shape[1]}, "
                f"Local={local_embeddings.shape[1]}. "
                "Using pseudo-inverse for alignment."
            )
            alignment_matrix = np.linalg.pinv(premium_embeddings) @ local_embeddings
        else:
            alignment_matrix = np.linalg.lstsq(
                premium_embeddings,
                local_embeddings,
                rcond=None
            )[0]
        
        # Save alignment matrix with embedder-specific name
        if output_path is None:
            output_path = os.getenv(
                f"EMBEDDING_ALIGNMENT_MATRIX_PATH_{self.query_embedder_type.upper()}",
                f"alignment_matrix_{self.query_embedder_type}.npy"
            )
        
        np.save(output_path, alignment_matrix)
        logger.info(
            f"Saved {self.query_embedder_type} alignment matrix to {output_path}"
        )
        
        return alignment_matrix

