"""
Google Gemini Embedding Wrapper

Provides embeddings using Google Gemini models via the Generative AI SDK.
Modular design - can be used alongside Ollama for query space.
"""

from typing import List, Optional
import numpy as np
import logging
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

logger = logging.getLogger(__name__)


class GeminiEmbedder:
    """
    Embedding generator using Google Gemini models.
    
    Uses Gemini's embedding models for high-quality semantic embeddings.
    Designed to work alongside Ollama embedder - choice is made via API parameter.
    """
    
    def __init__(
        self,
        model: str = "models/embedding-001",
        api_key: Optional[str] = None
    ):
        """
        Initialize Gemini embedder.
        
        Args:
            model: Gemini embedding model name
                - "models/embedding-001" (default, 768 dimensions)
                - "models/text-embedding-004" (if available)
            api_key: Google AI API key (default: from GEMINI_API_KEY env var)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-generativeai package is not installed. "
                "Install it with: pip install google-generativeai"
            )
        
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required. "
                "Get your API key from: https://makersuite.google.com/app/apikey"
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Determine embedding dimension based on model
        if "embedding-001" in model:
            self.embedding_dimension = 768
        elif "text-embedding-004" in model:
            self.embedding_dimension = 768
        else:
            # Default, will be updated on first embedding
            self.embedding_dimension = 768
        
        # Verify embedding support
        self._verify_embedding_support()
    
    def _verify_embedding_support(self):
        """Verify that the model supports embeddings."""
        try:
            # Try a test embedding with explicit output_dimensionality
            test_embedding = genai.embed_content(
                model=self.model,
                content="test",
                task_type="retrieval_document",
                output_dimensionality=768  # Explicitly set to 768
            )
            
            if "embedding" in test_embedding:
                embedding_data = test_embedding["embedding"]
                actual_dim = len(embedding_data) if isinstance(embedding_data, list) else embedding_data.shape[0] if hasattr(embedding_data, 'shape') else len(embedding_data)
                self.embedding_dimension = actual_dim
                logger.info(
                    f"GeminiEmbedder initialized with model {self.model}, "
                    f"dimension: {self.embedding_dimension}"
                )
            else:
                raise ValueError(f"Model {self.model} does not support embeddings")
        except Exception as e:
            logger.warning(
                f"Could not verify embedding support for {self.model}: {e}. "
                "Will attempt to use anyway."
            )
            # Keep default dimension
            self.embedding_dimension = 768
    
    def embed(
        self,
        texts: List[str],
        task_type: str = "retrieval_document",
        batch_size: int = 100
    ) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            task_type: Task type for embeddings
                - "retrieval_document" for documents
                - "retrieval_query" for queries
                - "semantic_similarity" for similarity tasks
            batch_size: Batch size for processing (Gemini supports up to 100)
            
        Returns:
            numpy array of embeddings (n_texts, dimension)
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                # Gemini supports batch embedding
                # Use output_dimensionality to ensure consistent 768 dimensions
                response = genai.embed_content(
                    model=self.model,
                    content=batch,
                    task_type=task_type,
                    output_dimensionality=768  # Explicitly set to 768
                )
                
                # Handle response format
                # Note: Gemini API returns 'embedding' (singular) even for batch requests
                # The embedding is a concatenated array that needs to be split
                expected_dim = 768  # We set output_dimensionality=768
                batch_size_actual = len(batch)
                
                if "embedding" in response:
                    # Single 'embedding' field - format depends on input
                    embedding_data = response["embedding"]
                    emb_array = np.array(embedding_data) if not isinstance(embedding_data, np.ndarray) else embedding_data

                    # Check array shape to determine format
                    if emb_array.ndim == 1:
                        # 1D array - could be single embedding or concatenated batch
                        if len(emb_array) == expected_dim:
                            # Single embedding (768 dims)
                            embeddings.append(emb_array.tolist())
                        elif len(emb_array) % expected_dim == 0:
                            # Concatenated batch (e.g., 6912 = 9 * 768)
                            num_embeddings = len(emb_array) // expected_dim
                            if num_embeddings == batch_size_actual:
                                # Split concatenated embeddings correctly
                                emb_array = emb_array.reshape(num_embeddings, expected_dim)
                                for idx in range(num_embeddings):
                                    embeddings.append(emb_array[idx].tolist())
                            else:
                                logger.warning(
                                    f"Embedding count mismatch: expected {batch_size_actual}, "
                                    f"got {num_embeddings}. Attempting to split anyway."
                                )
                                emb_array = emb_array.reshape(num_embeddings, expected_dim)
                                for idx in range(min(num_embeddings, batch_size_actual)):
                                    embeddings.append(emb_array[idx].tolist())
                        else:
                            # Unexpected length - truncate/pad
                            logger.warning(
                                f"Unexpected embedding length: {len(emb_array)}, "
                                f"expected {expected_dim} or multiple thereof"
                            )
                            if len(emb_array) >= expected_dim:
                                embeddings.append(emb_array[:expected_dim].tolist())
                            else:
                                padded = np.pad(emb_array, (0, expected_dim - len(emb_array)), mode='constant')
                                embeddings.append(padded.tolist())

                    elif emb_array.ndim == 2:
                        # 2D array - batch of embeddings already in correct format!
                        # This is the actual Gemini API response format for batches
                        # Shape: (n_texts, 768)
                        if emb_array.shape[1] == expected_dim:
                            # Perfect - already in correct shape
                            for idx in range(emb_array.shape[0]):
                                embeddings.append(emb_array[idx].tolist())
                        else:
                            # Wrong dimension - truncate/pad each embedding
                            logger.warning(
                                f"Unexpected embedding dimension: {emb_array.shape[1]}, "
                                f"expected {expected_dim}"
                            )
                            for idx in range(emb_array.shape[0]):
                                emb = emb_array[idx]
                                if len(emb) == expected_dim:
                                    embeddings.append(emb.tolist())
                                elif len(emb) > expected_dim:
                                    embeddings.append(emb[:expected_dim].tolist())
                                else:
                                    padded = np.pad(emb, (0, expected_dim - len(emb)), mode='constant')
                                    embeddings.append(padded.tolist())
                    else:
                        # Unexpected ndim - log error and use fallback
                        logger.error(
                            f"Unexpected embedding array dimensions: {emb_array.ndim}D, "
                            f"shape: {emb_array.shape}"
                        )
                        # Use zero vectors as fallback
                        for _ in batch:
                            embeddings.append([0.0] * expected_dim)
                        
                elif "embeddings" in response:
                    # Multiple embeddings returned as list (preferred format)
                    batch_embeddings = response["embeddings"]
                    if isinstance(batch_embeddings, list):
                        for emb in batch_embeddings:
                            if isinstance(emb, (list, np.ndarray)):
                                emb_list = emb.tolist() if isinstance(emb, np.ndarray) else emb
                                # Ensure correct dimension
                                if len(emb_list) == expected_dim:
                                    embeddings.append(emb_list)
                                elif len(emb_list) > expected_dim:
                                    embeddings.append(emb_list[:expected_dim])
                                else:
                                    padded = emb_list + [0.0] * (expected_dim - len(emb_list))
                                    embeddings.append(padded)
                            else:
                                embeddings.append(list(emb) if hasattr(emb, '__iter__') else [0.0] * expected_dim)
                    else:
                        # Single embedding wrapped
                        if isinstance(batch_embeddings, (list, np.ndarray)):
                            emb_list = batch_embeddings.tolist() if isinstance(batch_embeddings, np.ndarray) else batch_embeddings
                            if len(emb_list) == expected_dim:
                                embeddings.append(emb_list)
                            else:
                                embeddings.append(emb_list[:expected_dim] if len(emb_list) >= expected_dim else emb_list + [0.0] * (expected_dim - len(emb_list)))
                        else:
                            embeddings.append([0.0] * expected_dim)
                else:
                    raise ValueError(f"Unexpected response format: {response}")
                    
            except Exception as e:
                logger.error(f"Error embedding batch: {e}")
                # Use zero vectors as fallback
                for _ in batch:
                    embeddings.append([0.0] * self.embedding_dimension)
        
        # Convert to numpy array and ensure 2D shape (n_texts, dimension)
        if not embeddings:
            return np.zeros((0, 768))
        
        result = np.array(embeddings)
        
        # Ensure 2D shape
        if result.ndim == 1:
            # If 1D, check if it's concatenated
            if len(result) % 768 == 0:
                num_emb = len(result) // 768
                result = result.reshape(num_emb, 768)
            else:
                result = result.reshape(1, -1)
        elif result.ndim > 2:
            # Flatten if somehow 3D
            result = result.reshape(result.shape[0], -1)
        
        # Final validation: ensure all rows have 768 dimensions
        if result.shape[1] != 768:
            if result.shape[1] > 768:
                result = result[:, :768]  # Truncate
            else:
                # Pad if smaller
                padding = np.zeros((result.shape[0], 768 - result.shape[1]))
                result = np.hstack([result, padding])
        
        return result
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query.
        
        Args:
            query: Query text
            
        Returns:
            numpy array of embedding (dimension,)
        """
        try:
            response = genai.embed_content(
                model=self.model,
                content=query,
                task_type="retrieval_query",
                output_dimensionality=768  # Explicitly set to 768
            )
            
            if "embedding" in response:
                embedding = response["embedding"]
                emb_array = np.array(embedding)
                
                # Ensure it's 1D with correct dimension
                if emb_array.ndim > 1:
                    emb_array = emb_array.flatten()
                
                # Validate dimension
                if len(emb_array) != 768:
                    if len(emb_array) > 768:
                        emb_array = emb_array[:768]
                    else:
                        emb_array = np.pad(emb_array, (0, 768 - len(emb_array)), mode='constant')
                
                return emb_array
            else:
                raise ValueError(f"No embedding in response: {response}")
                
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            return np.zeros(768)  # Return 768-dim zero vector

