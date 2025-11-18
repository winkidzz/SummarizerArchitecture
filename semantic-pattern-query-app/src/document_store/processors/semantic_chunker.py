"""
Layer 2: Semantic Chunker

Structure-aware chunking that respects document boundaries,
preserves context, and handles markdown patterns.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
import logging
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """A document chunk with metadata."""
    text: str
    metadata: Dict[str, Any]
    chunk_index: int
    start_char: int = 0
    end_char: int = 0


class SemanticChunker:
    """
    Structure-aware chunker that respects document structure.
    
    Features:
    - Detects sections (headers, code blocks, lists)
    - Preserves atomic sections
    - Adds overlap only when needed
    - Handles markdown patterns
    """
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 100,
        min_chunk_size: int = 50
    ):
        """
        Initialize the semantic chunker.
        
        Args:
            chunk_size: Target chunk size in tokens/words
            chunk_overlap: Overlap between chunks
            min_chunk_size: Minimum chunk size to keep
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk_document(
        self,
        text: str,
        metadata: Dict[str, Any],
        doc_type: Optional[str] = None
    ) -> List[Chunk]:
        """
        Chunk document based on structure.
        
        Args:
            text: Document text
            metadata: Document metadata
            doc_type: Document type (markdown, text, etc.)
            
        Returns:
            List of Chunk objects
        """
        if doc_type is None:
            doc_type = metadata.get("document_type", "text")
        
        if doc_type == "markdown":
            return self._chunk_markdown(text, metadata)
        else:
            return self._chunk_generic(text, metadata)
    
    def _chunk_markdown(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[Chunk]:
        """
        Chunk markdown preserving structure.
        
        Detects:
        - Headers (# ## ###)
        - Code blocks (```)
        - Lists
        - Sections
        """
        # Detect sections
        sections = self._detect_markdown_sections(text)
        chunks = []
        
        for section in sections:
            if self._is_atomic_section(section):
                # Keep small sections whole
                chunk_index = len(chunks)
                chunk_id = self._generate_chunk_id(metadata.get("source_path", ""), chunk_index)
                chunks.append(Chunk(
                    text=section["text"],
                    metadata={
                        **metadata,
                        "chunk_id": chunk_id,  # Add consistent chunk_id
                        "section_type": section.get("type", "text"),
                        "section_level": section.get("level", 0),
                        "preserves_context": True
                    },
                    chunk_index=chunk_index,
                    start_char=section.get("start", 0),
                    end_char=section.get("end", len(section["text"]))
                ))
            else:
                # Split large sections with overlap
                sub_chunks = self._split_with_overlap(
                    section["text"],
                    section.get("type", "text"),
                    metadata,
                    base_index=len(chunks)
                )
                chunks.extend(sub_chunks)
        
        # Ensure all chunks have consistent chunk_ids
        for i, chunk in enumerate(chunks):
            if "chunk_id" not in chunk.metadata:
                chunk.metadata["chunk_id"] = self._generate_chunk_id(
                    metadata.get("source_path", ""),
                    chunk.chunk_index
                )
        
        return chunks
    
    def _chunk_generic(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[Chunk]:
        """
        Chunk generic text preserving paragraphs.
        """
        # Split by paragraphs first
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_size = len(para.split())
            
            if current_size + para_size > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = "\n\n".join(current_chunk)
                chunk_index = len(chunks)
                chunk_id = self._generate_chunk_id(metadata.get("source_path", ""), chunk_index)
                chunks.append(Chunk(
                    text=chunk_text,
                    metadata={
                        **metadata,
                        "chunk_id": chunk_id,  # Add consistent chunk_id
                        "chunk_overlap": self.chunk_overlap
                    },
                    chunk_index=chunk_index
                ))
                
                # Start new chunk with overlap
                overlap_paras = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk
                current_chunk = overlap_paras + [para]
                current_size = sum(len(p.split()) for p in current_chunk)
            else:
                current_chunk.append(para)
                current_size += para_size
        
        # Add final chunk
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunk_index = len(chunks)
            chunk_id = self._generate_chunk_id(metadata.get("source_path", ""), chunk_index)
            chunks.append(Chunk(
                text=chunk_text,
                metadata={
                    **metadata,
                    "chunk_id": chunk_id,  # Add consistent chunk_id
                    "chunk_overlap": self.chunk_overlap
                },
                chunk_index=chunk_index
            ))
        
        # Ensure all chunks have consistent chunk_ids
        for i, chunk in enumerate(chunks):
            if "chunk_id" not in chunk.metadata:
                chunk.metadata["chunk_id"] = self._generate_chunk_id(
                    metadata.get("source_path", ""),
                    chunk.chunk_index
                )
        
        return chunks
    
    def _generate_chunk_id(self, source_path: str, chunk_index: int) -> str:
        """
        Generate a consistent chunk ID based on source path and chunk index.
        
        Args:
            source_path: Source file path
            chunk_index: Chunk index within the document
            
        Returns:
            Consistent chunk ID (UUID format)
        """
        import uuid
        
        # Create a deterministic ID from source_path + chunk_index
        # Use hash to create a UUID-like identifier
        combined = f"{source_path}:{chunk_index}"
        hash_bytes = hashlib.md5(combined.encode()).digest()
        
        # Convert to UUID format (use bytes directly, set version to avoid validation issues)
        # Pad or truncate to 16 bytes if needed
        if len(hash_bytes) >= 16:
            uuid_bytes = hash_bytes[:16]
        else:
            uuid_bytes = hash_bytes + b'\x00' * (16 - len(hash_bytes))
        
        # Create UUID from bytes (set version=4 to avoid validation, but we control the bytes)
        chunk_uuid = uuid.UUID(bytes=uuid_bytes)
        return str(chunk_uuid)
    
    def _detect_markdown_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect markdown sections (headers, code blocks, etc.).
        
        Returns:
            List of section dictionaries with text, type, level
        """
        sections = []
        lines = text.split("\n")
        
        current_section = {
            "text": "",
            "type": "text",
            "level": 0,
            "start": 0
        }
        in_code_block = False
        code_block_start = None
        
        for i, line in enumerate(lines):
            # Detect code blocks
            if line.strip().startswith("```"):
                if not in_code_block:
                    # Start of code block
                    if current_section["text"].strip():
                        current_section["end"] = i
                        sections.append(current_section.copy())
                    
                    in_code_block = True
                    code_block_start = i
                    current_section = {
                        "text": line + "\n",
                        "type": "code_block",
                        "level": 0,
                        "start": i
                    }
                else:
                    # End of code block
                    current_section["text"] += line + "\n"
                    current_section["end"] = i
                    sections.append(current_section.copy())
                    in_code_block = False
                    current_section = {
                        "text": "",
                        "type": "text",
                        "level": 0,
                        "start": i + 1
                    }
                continue
            
            if in_code_block:
                current_section["text"] += line + "\n"
                continue
            
            # Detect headers
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if header_match:
                # Save previous section
                if current_section["text"].strip():
                    current_section["end"] = i - 1
                    sections.append(current_section.copy())
                
                # Start new section
                level = len(header_match.group(1))
                current_section = {
                    "text": line + "\n",
                    "type": "header",
                    "level": level,
                    "start": i
                }
                continue
            
            # Regular line
            current_section["text"] += line + "\n"
        
        # Add final section
        if current_section["text"].strip():
            current_section["end"] = len(lines) - 1
            sections.append(current_section)
        
        return sections
    
    def _is_atomic_section(self, section: Dict[str, Any]) -> bool:
        """
        Check if section should be kept whole (not split).
        
        Atomic sections:
        - Small sections (< chunk_size)
        - Code blocks
        - Headers with small content
        """
        text = section["text"]
        word_count = len(text.split())
        
        # Code blocks are always atomic
        if section.get("type") == "code_block":
            return True
        
        # Small sections are atomic
        if word_count <= self.chunk_size:
            return True
        
        return False
    
    def _split_with_overlap(
        self,
        text: str,
        section_type: str,
        base_metadata: Dict[str, Any],
        base_index: int = 0
    ) -> List[Chunk]:
        """
        Split large text with overlap, preserving sentence boundaries.
        """
        sentences = self._split_sentences(text)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence.split())
            
            if current_size + sentence_size > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = " ".join(current_chunk)
                chunk_index = base_index + len(chunks)
                chunk_id = self._generate_chunk_id(base_metadata.get("source_path", ""), chunk_index)
                chunks.append(Chunk(
                    text=chunk_text,
                    metadata={
                        **base_metadata,
                        "chunk_id": chunk_id,  # Add consistent chunk_id
                        "section_type": section_type,
                        "chunk_overlap": self.chunk_overlap
                    },
                    chunk_index=chunk_index
                ))
                
                # Start new chunk with overlap
                overlap_sentences = current_chunk[-self.chunk_overlap//10:] if len(current_chunk) > self.chunk_overlap//10 else current_chunk
                current_chunk = overlap_sentences + [sentence]
                current_size = sum(len(s.split()) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_size += sentence_size
        
        # Add final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            if len(chunk_text.split()) >= self.min_chunk_size:
                chunk_index = base_index + len(chunks)
                chunk_id = self._generate_chunk_id(base_metadata.get("source_path", ""), chunk_index)
                chunks.append(Chunk(
                    text=chunk_text,
                    metadata={
                        **base_metadata,
                        "chunk_id": chunk_id,  # Add consistent chunk_id
                        "section_type": section_type,
                        "chunk_overlap": self.chunk_overlap
                    },
                    chunk_index=chunk_index
                ))
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Handles:
        - Periods, exclamation, question marks
        - Code blocks (preserve)
        - URLs (don't split on periods in URLs)
        """
        # Simple sentence splitting
        # Split on sentence endings
        sentences = re.split(r'([.!?]+[\s\n]+)', text)
        
        # Recombine sentences with their punctuation
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i + 1]
            else:
                sentence = sentences[i]
            
            sentence = sentence.strip()
            if sentence:
                result.append(sentence)
        
        # Handle last sentence if odd number
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            result.append(sentences[-1].strip())
        
        return result if result else [text]

