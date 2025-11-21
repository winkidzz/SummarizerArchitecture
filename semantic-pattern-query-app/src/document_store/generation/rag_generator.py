"""
Layer 6: Context Window Management and RAG Generation

Intelligent context packing with citations.
Generates responses using Ollama Qwen with proper citation tracking.
"""

from typing import List, Dict, Any, Optional
import re
import logging
import os

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None

logger = logging.getLogger(__name__)


class HealthcareRAGGenerator:
    """
    Generates responses with proper citations and context management.
    
    Features:
    - Intelligent context packing (respects token limits)
    - Citation tracking and extraction
    - Structured prompt building
    - Ollama Qwen integration
    """
    
    def __init__(
        self,
        model: str = "qwen3:14b",
        base_url: str = "http://localhost:11434",
        max_context_tokens: int = 8000,
        max_response_tokens: int = 2000,
        temperature: float = 0.1
    ):
        """
        Initialize RAG generator.
        
        Args:
            model: Ollama model name
            base_url: Ollama API base URL
            max_context_tokens: Maximum context tokens
            max_response_tokens: Maximum response tokens
            temperature: LLM temperature
        """
        if not OLLAMA_AVAILABLE:
            raise ImportError(
                "ollama package is not installed. "
                "Install it with: pip install ollama"
            )
        
        self.model = model
        self.base_url = base_url
        self.max_context_tokens = max_context_tokens
        self.max_response_tokens = max_response_tokens
        self.temperature = temperature
        
        self.client = ollama.Client(host=base_url)
        
        logger.info(
            f"HealthcareRAGGenerator initialized with model: {model}"
        )
    
    def generate(
        self,
        query: str,
        docs: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate response with citations.
        
        Args:
            query: User query
            docs: Retrieved documents
            user_context: Optional user context
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        # Pack docs intelligently (respect token limits)
        context = self._pack_context(
            docs,
            max_tokens=self.max_context_tokens
        )
        
        # Build structured prompt with citations
        prompt = self._build_prompt_with_citations(query, context)
        
        # Generate with citations
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_response_tokens
                }
            )
            
            answer = response.get("response", "")
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            answer = "I apologize, but I encountered an error generating a response."
        
        # Extract citations
        citations = self._extract_citations(answer, context)
        
        return {
            "answer": answer,
            "sources": citations,
            "context_docs_used": len(context),
            "total_docs_retrieved": len(docs)
        }
    
    def _pack_context(
        self,
        docs: List[Dict[str, Any]],
        max_tokens: int
    ) -> List[Dict[str, Any]]:
        """
        Pack documents intelligently within token limit.
        
        Args:
            docs: List of document dictionaries
            max_tokens: Maximum tokens allowed
            
        Returns:
            List of packed documents
        """
        packed = []
        current_tokens = 0
        
        # Sort by score (best first)
        sorted_docs = sorted(
            docs,
            key=lambda d: d.get("score", d.get("similarity_score", d.get("rrf_score", 0))),
            reverse=True
        )
        
        for doc in sorted_docs:
            text = doc.get("text", "")
            doc_tokens = self._count_tokens(text)
            
            if current_tokens + doc_tokens <= max_tokens:
                packed.append(doc)
                current_tokens += doc_tokens
            else:
                # Try to fit partial document
                remaining_tokens = max_tokens - current_tokens
                if remaining_tokens > 100:  # Minimum viable chunk
                    partial_text = self._truncate_to_tokens(text, remaining_tokens)
                    packed.append({
                        **doc,
                        "text": partial_text,
                        "truncated": True
                    })
                break
        
        logger.debug(
            f"Packed {len(packed)} documents ({current_tokens} tokens) "
            f"from {len(docs)} retrieved"
        )
        
        return packed
    
    def _build_prompt_with_citations(
        self,
        query: str,
        docs: List[Dict[str, Any]]
    ) -> str:
        """
        Build prompt with proper citations.
        
        Args:
            query: User query
            docs: Context documents
            
        Returns:
            Formatted prompt string
        """
        context_parts = []
        
        for i, doc in enumerate(docs):
            doc_text = doc.get("text", "")
            metadata = doc.get("metadata", {})
            source = metadata.get("source_path", metadata.get("document_id", "Unknown"))
            
            context_parts.append(
                f"[Doc {i+1}] Source: {source}\n"
                f"Type: {metadata.get('document_type', 'unknown')}\n"
                f"Content:\n{doc_text}"
            )
        
        context = "\n\n---\n\n".join(context_parts)
        
        prompt = f"""You are a helpful assistant that answers questions using the provided context.

Context (from pattern library):
{context}

Question: {query}

Instructions:
- Answer using ONLY the provided context
- Cite sources as [Doc X] for each claim
- Do not infer information not in context
- If information is missing, state that clearly
- Be precise and accurate

Answer:"""
        
        return prompt
    
    def _extract_citations(
        self,
        answer: str,
        context: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract citation references from answer.
        
        Args:
            answer: Generated answer text
            context: Context documents used
            
        Returns:
            List of citation dictionaries
        """
        citations = []
        
        # Find [Doc X] references
        doc_refs = re.findall(r'\[Doc (\d+)\]', answer)
        
        for doc_num in set(doc_refs):
            try:
                doc_index = int(doc_num) - 1
                if 0 <= doc_index < len(context):
                    doc = context[doc_index]
                    metadata = doc.get("metadata", {})
                    # Extract source_type for tier identification
                    source_type = metadata.get("source_type") or metadata.get("layer", "pattern_library")

                    # Get score from any available field
                    score = doc.get("score") or doc.get("similarity_score") or doc.get("rrf_score")

                    citation = {
                        "doc_index": doc_index,
                        "document_id": metadata.get("document_id", ""),
                        "source_path": metadata.get("source_path", ""),
                        "document_type": metadata.get("document_type", "unknown"),
                        "source_type": source_type,  # Add tier metadata
                        "relevance": "cited"
                    }

                    # Add score if available
                    if score is not None:
                        citation["score"] = score

                    citations.append(citation)
            except ValueError:
                continue
        
        return citations
    
    def _count_tokens(self, text: str) -> int:
        """
        Estimate token count (approximate).
        
        Args:
            text: Text to count
            
        Returns:
            Estimated token count
        """
        # Simple approximation: ~4 characters per token
        # For more accuracy, use tiktoken or similar
        return len(text) // 4
    
    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to approximately max_tokens.
        
        Args:
            text: Text to truncate
            max_tokens: Maximum tokens
            
        Returns:
            Truncated text
        """
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        
        # Truncate at sentence boundary if possible
        truncated = text[:max_chars]
        last_period = truncated.rfind(".")
        last_newline = truncated.rfind("\n")
        
        cut_point = max(last_period, last_newline)
        if cut_point > max_chars * 0.8:  # Only if we keep most of the text
            return text[:cut_point + 1]
        
        return truncated + "..."

