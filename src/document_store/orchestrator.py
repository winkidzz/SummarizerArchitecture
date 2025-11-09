"""
Orchestrator for document store operations.

Provides a high-level interface for ingesting documents,
updating the knowledge base, and querying patterns.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from .processors.docling_processor import DoclingProcessor
from .storage.vector_store import VectorStore
from .search.rag_query import RAGQueryInterface
from .search.web_search import WebSearchTool
from .agents.adk_agent import ADKAgentQuery
from .agents.ollama_agent import OllamaAgent

logger = logging.getLogger(__name__)


class DocumentStoreOrchestrator:
    """
    High-level orchestrator for document store operations.
    
    Combines document processing, storage, and querying capabilities.
    """

    def __init__(
        self,
        persist_directory: str | Path = "./data/chroma_db",
        collection_name: str = "architecture_patterns",
        embedding_model: Optional[str] = None,
        use_adk_agent: bool = True,
        ollama_model: Optional[str] = None,
    ):
        """
        Initialize the orchestrator.
        
        Args:
            persist_directory: Directory for ChromaDB storage
            collection_name: Collection name for patterns
            embedding_model: Embedding model name
            use_adk_agent: Whether to use Google ADK agent for querying (primary)
            ollama_model: Optional Ollama model name for specialized tasks
        """
        # Initialize components
        self.processor = DoclingProcessor()
        self.vector_store = VectorStore(
            persist_directory=persist_directory,
            collection_name=collection_name,
            embedding_model=embedding_model,
        )
        self.rag_interface = RAGQueryInterface(self.vector_store)
        self.web_search = WebSearchTool()
        
        # Initialize agents
        self.adk_agent = None
        if use_adk_agent:
            try:
                self.adk_agent = ADKAgentQuery(self.vector_store)
            except Exception as e:
                logger.warning(f"Could not initialize ADK agent: {e}")
        
        self.ollama_agent = None
        if ollama_model:
            try:
                self.ollama_agent = OllamaAgent(
                    model=ollama_model,
                    vector_store=self.vector_store,
                )
            except Exception as e:
                logger.warning(f"Could not initialize Ollama agent: {e}")
        
        logger.info("DocumentStoreOrchestrator initialized")

    def ingest_documents(
        self,
        sources: List[str | Path],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Ingest documents into the knowledge base.
        
        Args:
            sources: List of document paths or URLs
            metadata: Optional metadata to attach to all documents
            
        Returns:
            Number of documents successfully ingested
        """
        processed_docs = []
        
        for source in sources:
            try:
                source_path = Path(source)
                
                if source_path.is_file():
                    # Process single file
                    file_metadata = metadata.copy() if metadata else {}
                    file_metadata.setdefault("source", str(source))
                    file_metadata.setdefault("file_path", str(source))
                    doc = self.processor.process_document(
                        source,
                        metadata=file_metadata,
                    )
                    processed_docs.append(doc)
                elif source_path.is_dir():
                    # Process directory
                    docs = self.processor.process_directory(
                        source_path,
                    )
                    processed_docs.extend(docs)
                else:
                    logger.warning(f"Source not found: {source}")
                    continue
                    
            except Exception as e:
                logger.error(f"Error processing {source}: {str(e)}")
                continue
        
        if processed_docs:
            # Add to vector store
            self.vector_store.add_documents(processed_docs)
            logger.info(f"Ingested {len(processed_docs)} documents")
        
        return len(processed_docs)

    def query_patterns(
        self,
        query: str,
        n_results: int = 5,
        pattern_type: Optional[str] = None,
        vendor: Optional[str] = None,
        use_agent: bool = True,
        use_ollama_rag: bool = False,
    ) -> Dict[str, Any]:
        """
        Query for architecture patterns.
        
        Uses Google ADK agent as primary querying method, with fallback
        to direct RAG query. Can use Ollama for specialized RAG tasks.
        
        Args:
            query: Search query
            n_results: Number of results
            pattern_type: Optional pattern type filter
            vendor: Optional vendor filter
            use_agent: Whether to use ADK agent (primary method)
            use_ollama_rag: Whether to use Ollama for RAG response generation
            
        Returns:
            Query results
        """
        # Primary: Use ADK agent if available
        if use_agent and self.adk_agent is not None:
            try:
                return self.adk_agent.query(
                    query=query,
                    pattern_type=pattern_type,
                    vendor=vendor,
                    n_results=n_results,
                    use_agent=True,
                )
            except Exception as e:
                logger.warning(f"ADK agent query failed: {e}. Falling back to direct query.")
        
        # Specialized: Use Ollama for RAG if requested
        if use_ollama_rag and self.ollama_agent is not None:
            try:
                return self.ollama_agent.query_with_rag(
                    query=query,
                    n_results=n_results,
                    pattern_type=pattern_type,
                    vendor=vendor,
                )
            except Exception as e:
                logger.warning(f"Ollama RAG query failed: {e}. Falling back to direct query.")
        
        # Fallback: Direct RAG query
        return self.rag_interface.query_patterns(
            query=query,
            n_results=n_results,
            pattern_type=pattern_type,
            vendor=vendor,
        )

    def search_and_ingest(
        self,
        query: str,
        max_results: int = 10,
        auto_ingest: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Search the web for relevant content and optionally ingest.
        
        Args:
            query: Search query
            max_results: Maximum search results
            auto_ingest: Whether to automatically ingest found content
            
        Returns:
            List of search results
        """
        results = self.web_search.search_architecture_patterns(
            pattern_name=query,
            max_results=max_results,
        )
        
        if auto_ingest and results:
            # Note: In a real implementation, you would download and process
            # the content from the URLs. This is a placeholder.
            logger.info(f"Found {len(results)} search results (auto-ingest not fully implemented)")
        
        return results

    def get_store_info(self) -> Dict[str, Any]:
        """Get information about the document store."""
        return self.vector_store.get_collection_info()

