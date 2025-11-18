"""
Ollama Qwen Embedding Wrapper

Provides embeddings using Ollama Qwen models.
"""

from typing import List, Optional
import numpy as np
import logging
import os

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None

logger = logging.getLogger(__name__)


class QwenEmbedder:
    """
    Embedding generator using Ollama Qwen models.
    
    Note: Ollama embedding support may vary by model.
    This wrapper handles both embedding-capable models and fallbacks.
    """
    
    def __init__(
        self,
        model: str = "qwen3:14b",
        base_url: str = "http://localhost:11434"
    ):
        """
        Initialize Qwen embedder.
        
        Args:
            model: Ollama model name
            base_url: Ollama API base URL
        """
        if not OLLAMA_AVAILABLE:
            raise ImportError(
                "ollama package is not installed. "
                "Install it with: pip install ollama"
            )
        
        self.model = model
        self.base_url = base_url
        self.client = ollama.Client(host=base_url)
        
        # Check if model supports embeddings
        self._verify_embedding_support()
    
    def _verify_embedding_support(self):
        """Verify that the model supports embeddings."""
        try:
            # Try a test embedding
            test_response = self.client.embeddings(
                model=self.model,
                prompt="test"
            )
            if "embedding" in test_response:
                self.embedding_dimension = len(test_response["embedding"])
                logger.info(
                    f"QwenEmbedder initialized with model {self.model}, "
                    f"dimension: {self.embedding_dimension}"
                )
            else:
                raise ValueError(f"Model {self.model} does not support embeddings")
        except Exception as e:
            logger.warning(
                f"Could not verify embedding support for {self.model}: {e}. "
                "Will attempt to use anyway."
            )
            # Default dimension (will be updated on first successful embedding)
            self.embedding_dimension = 4096  # Common for Qwen models
    
    def embed(
        self,
        texts: List[str],
        batch_size: int = 10
    ) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            numpy array of embeddings (n_texts, dimension)
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = []
            
            for text in batch:
                try:
                    response = self.client.embeddings(
                        model=self.model,
                        prompt=text
                    )
                    
                    if "embedding" in response:
                        embedding = response["embedding"]
                        batch_embeddings.append(embedding)
                        
                        # Update dimension if first embedding
                        if self.embedding_dimension == 4096 and len(embedding) != 4096:
                            self.embedding_dimension = len(embedding)
                    else:
                        raise ValueError(f"No embedding in response: {response}")
                        
                except Exception as e:
                    logger.error(f"Error embedding text: {e}")
                    # Use zero vector as fallback
                    if embeddings:
                        batch_embeddings.append(np.zeros(self.embedding_dimension).tolist())
                    else:
                        raise
            
            embeddings.extend(batch_embeddings)
        
        return np.array(embeddings)
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query.
        
        Args:
            query: Query text
            
        Returns:
            numpy array of embedding (1, dimension)
        """
        embeddings = self.embed([query], batch_size=1)
        return embeddings[0] if len(embeddings) > 0 else np.zeros(self.embedding_dimension)

