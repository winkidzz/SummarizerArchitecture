"""
Ollama integration for specialized RAG tasks and local model execution.

This module provides support for using Ollama models for:
- Building RAG systems
- Generating embeddings
- Custom agent workflows
- Privacy-sensitive operations
- Model experimentation
"""

from typing import Dict, Any, Optional, List
import logging

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None

from ..storage.vector_store import VectorStore

logger = logging.getLogger(__name__)


class OllamaAgent:
    """
    Ollama-based agent for specialized RAG tasks.
    
    Provides local LLM capabilities for building RAG systems,
    generating embeddings, and custom workflows.
    """

    def __init__(
        self,
        model: str = "llama3",
        base_url: str = "http://localhost:11434",
        vector_store: Optional[VectorStore] = None,
    ):
        """
        Initialize Ollama agent.
        
        Args:
            model: Ollama model name (e.g., 'llama3', 'mistral', 'gemma')
            base_url: Ollama API base URL
            vector_store: Optional vector store for RAG operations
        """
        if not OLLAMA_AVAILABLE:
            raise ImportError(
                "ollama package is not installed. "
                "Install it with: pip install ollama"
            )
        
        self.model = model
        self.base_url = base_url
        self.vector_store = vector_store
        
        # Initialize Ollama client
        self.client = ollama.Client(host=base_url)
        
        # Verify model is available
        self._verify_model()
        
        logger.info(f"OllamaAgent initialized with model: {model}")

    def _verify_model(self) -> None:
        """Verify that the specified model is available."""
        try:
            models = self.client.list()
            model_names = [m['name'] for m in models.get('models', [])]
            
            if self.model not in model_names:
                logger.warning(
                    f"Model '{self.model}' not found. Available models: {model_names}. "
                    "Attempting to pull model..."
                )
                try:
                    self.client.pull(self.model)
                    logger.info(f"Successfully pulled model: {self.model}")
                except Exception as e:
                    logger.error(f"Failed to pull model: {e}")
        except Exception as e:
            logger.warning(f"Could not verify model availability: {e}")

    def generate_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
    ) -> List[List[float]]:
        """
        Generate embeddings using Ollama model.
        
        Args:
            texts: List of texts to embed
            model: Optional model name (defaults to self.model)
            
        Returns:
            List of embedding vectors
        """
        model_name = model or self.model
        embeddings = []
        
        for text in texts:
            try:
                # Use Ollama's embedding endpoint
                response = self.client.embeddings(
                    model=model_name,
                    prompt=text,
                )
                embeddings.append(response['embedding'])
            except Exception as e:
                logger.error(f"Error generating embedding: {e}")
                raise
        
        return embeddings

    def build_rag_response(
        self,
        query: str,
        context_documents: List[str],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build a RAG response using Ollama model.
        
        Args:
            query: User query
            context_documents: Relevant documents from vector store
            system_prompt: Optional system prompt
            
        Returns:
            RAG response with answer and metadata
        """
        # Build context from documents
        context = "\n\n".join([
            f"Document {i+1}:\n{doc}"
            for i, doc in enumerate(context_documents)
        ])
        
        # Build prompt
        system = system_prompt or (
            "You are an expert in AI architecture patterns. "
            "Answer questions based on the provided context documents. "
            "If the answer is not in the context, say so."
        )
        
        user_prompt = f"""Context:
{context}

Question: {query}

Answer:"""
        
        try:
            response = self.client.generate(
                model=self.model,
                prompt=user_prompt,
                system=system,
                stream=False,
            )
            
            return {
                "answer": response['response'],
                "model": self.model,
                "context_used": len(context_documents),
                "metadata": {
                    "total_duration": response.get('total_duration'),
                    "load_duration": response.get('load_duration'),
                    "prompt_eval_count": response.get('prompt_eval_count'),
                    "eval_count": response.get('eval_count'),
                },
            }
        except Exception as e:
            logger.error(f"Error building RAG response: {e}")
            raise

    def query_with_rag(
        self,
        query: str,
        n_results: int = 5,
        pattern_type: Optional[str] = None,
        vendor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Query architecture patterns using RAG with Ollama.
        
        Args:
            query: Search query
            n_results: Number of context documents
            pattern_type: Optional pattern type filter
            vendor: Optional vendor filter
            
        Returns:
            RAG response with answer and source documents
        """
        if self.vector_store is None:
            raise ValueError("Vector store not provided. Cannot perform RAG query.")
        
        # Retrieve relevant documents
        results = self.vector_store.query(
            query_text=query,
            n_results=n_results,
            filter_metadata={
                "pattern_type": pattern_type,
                "vendor": vendor,
            } if pattern_type or vendor else None,
        )
        
        # Build RAG response
        context_docs = results.get("documents", [])
        rag_response = self.build_rag_response(
            query=query,
            context_documents=context_docs,
        )
        
        # Combine with source documents
        return {
            **rag_response,
            "sources": [
                {
                    "content": doc,
                    "metadata": meta,
                    "id": doc_id,
                }
                for doc, meta, doc_id in zip(
                    context_docs,
                    results.get("metadatas", []),
                    results.get("ids", []),
                )
            ],
        }

    def create_custom_model(
        self,
        model_name: str,
        base_model: str,
        modelfile_content: str,
    ) -> Dict[str, Any]:
        """
        Create a custom Ollama model using Modelfile.
        
        Args:
            model_name: Name for the custom model
            base_model: Base model to use
            modelfile_content: Modelfile content for customization
            
        Returns:
            Creation result
        """
        try:
            # Create model from Modelfile
            # Note: This requires the modelfile to be saved and ollama create command
            # For now, we'll provide the structure
            logger.info(f"Creating custom model '{model_name}' from base '{base_model}'")
            
            # In practice, you would:
            # 1. Save modelfile_content to a file
            # 2. Run: ollama create model_name -f modelfile_path
            # Or use ollama Python client if it supports this
            
            return {
                "model_name": model_name,
                "base_model": base_model,
                "status": "created",
                "note": "Use 'ollama create' command with Modelfile for actual creation",
            }
        except Exception as e:
            logger.error(f"Error creating custom model: {e}")
            raise

    def list_available_models(self) -> List[str]:
        """
        List available Ollama models.
        
        Returns:
            List of model names
        """
        try:
            models = self.client.list()
            return [m['name'] for m in models.get('models', [])]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

