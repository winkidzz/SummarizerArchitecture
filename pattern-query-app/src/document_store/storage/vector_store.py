"""
Embedded file-based vector store using ChromaDB for storing
architecture patterns and documentation.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import logging

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
except ImportError:
    raise ImportError(
        "chromadb is not installed. Install it with: pip install chromadb"
    )

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Embedded file-based vector store for architecture patterns.
    
    Uses ChromaDB as the underlying storage engine, which stores
    data in local files.
    """

    def __init__(
        self,
        persist_directory: Union[str, Path] = "./data/chroma_db",
        collection_name: str = "architecture_patterns",
        embedding_model: Optional[str] = None,
    ):
        """
        Initialize the vector store.
        
        Args:
            persist_directory: Directory where ChromaDB will store data
            collection_name: Name of the collection to use
            embedding_model: Name of embedding model to use
                           (default: 'all-MiniLM-L6-v2' for sentence-transformers)
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model or "all-MiniLM-L6-v2"
        
        # Initialize embedding function
        if SentenceTransformer:
            try:
                self.embedding_model = SentenceTransformer(self.embedding_model_name)
                # Create a proper embedding function wrapper
                embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=self.embedding_model_name
                )
            except Exception as e:
                logger.warning(f"Failed to use SentenceTransformer embedding: {e}. Using default embedding.")
                embedding_fn = embedding_functions.DefaultEmbeddingFunction()
                self.embedding_model = None
        else:
            # Use ChromaDB's default embedding function
            embedding_fn = embedding_functions.DefaultEmbeddingFunction()
            self.embedding_model = None
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )
        
        # Check if collection exists and handle embedding function conflict
        try:
            # Try to get existing collection first
            existing_collection = self.client.get_collection(
                name=self.collection_name,
            )
            # Collection exists - use its existing embedding function
            self.collection = existing_collection
            logger.info(
                f"Using existing collection '{self.collection_name}' with its current embedding function"
            )
        except Exception:
            # Collection doesn't exist - create it with the specified embedding function
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=embedding_fn,
                metadata={"description": "Architecture patterns and documentation"},
            )
            logger.info(
                f"Created new collection '{self.collection_name}' with embedding function"
            )
        
        logger.info(
            f"VectorStore initialized: {self.persist_directory}, "
            f"collection: {self.collection_name}"
        )

    def _custom_embedding_function(self, texts: List[str]) -> List[List[float]]:
        """
        Custom embedding function using sentence-transformers.
        Note: This is kept for backward compatibility but ChromaDB's
        SentenceTransformerEmbeddingFunction should be used instead.
        """
        if self.embedding_model is None:
            # Fallback to default if model not available
            default_fn = embedding_functions.DefaultEmbeddingFunction()
            return default_fn(texts)
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
    ) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document dictionaries with 'content' and 'metadata' keys
            ids: Optional list of document IDs (auto-generated if not provided)
        """
        if not documents:
            return
        
        texts = [doc.get("content", "") for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        
        if ids is None:
            # Generate IDs based on source or index
            ids = [
                doc.get("metadata", {}).get("source", f"doc_{i}")
                for i, doc in enumerate(documents)
            ]
        
        # Add to collection
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids,
        )
        
        logger.info(f"Added {len(documents)} documents to vector store")

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Query the vector store for similar documents.
        
        Args:
            query_text: Query text to search for
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            Dictionary containing:
                - documents: List of document texts
                - metadatas: List of metadata dictionaries
                - distances: List of similarity distances
                - ids: List of document IDs
        """
        query_kwargs = {
            "query_texts": [query_text],
            "n_results": n_results,
        }
        
        if filter_metadata:
            query_kwargs["where"] = filter_metadata
        
        results = self.collection.query(**query_kwargs)
        
        # Flatten results (remove outer list since we only query one text)
        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
            "ids": results["ids"][0] if results["ids"] else [],
        }

    def delete(self, ids: Optional[List[str]] = None, where: Optional[Dict] = None) -> None:
        """
        Delete documents from the vector store.
        
        Args:
            ids: Optional list of document IDs to delete
            where: Optional metadata filter for deletion
        """
        if ids:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents by IDs")
        elif where:
            self.collection.delete(where=where)
            logger.info("Deleted documents by metadata filter")
        else:
            logger.warning("No deletion criteria provided")

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_directory": str(self.persist_directory),
        }

    def reset(self) -> None:
        """Reset the collection (delete all documents)."""
        self.client.delete_collection(name=self.collection_name)
        
        # Recreate collection with same embedding function
        if self.embedding_model:
            embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model_name
            )
        else:
            embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=embedding_fn,
        )
        logger.info("Vector store collection reset")

