"""
Text chunking utilities for splitting large documents into smaller chunks
for better RAG retrieval and processing.
"""

from typing import List, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


class TextChunker:
    """Utility for chunking text documents into smaller pieces."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None,
    ):
        """
        Initialize the chunker.
        
        Args:
            chunk_size: Target size for chunks (in characters)
            chunk_overlap: Overlap between chunks (in characters)
            separators: List of separators to use for splitting (in order of preference)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or [
            "\n\n## ",  # Major sections
            "\n\n### ",  # Subsections
            "\n\n",  # Paragraphs
            "\n",  # Lines
            ". ",  # Sentences
            " ",  # Words
        ]
    
    def chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Split text into chunks.
        
        Args:
            text: Text to chunk
            metadata: Base metadata to attach to all chunks
            
        Returns:
            List of chunk dictionaries with 'content' and 'metadata' keys
        """
        if len(text) <= self.chunk_size:
            # Text is small enough, return as single chunk
            return [{
                "content": text,
                "metadata": (metadata or {}).copy(),
            }]
        
        chunks = []
        base_metadata = (metadata or {}).copy()
        
        # Try to split by separators in order of preference
        remaining_text = text
        chunk_index = 0
        
        while remaining_text:
            # Try each separator
            chunk = None
            for separator in self.separators:
                if separator in remaining_text:
                    # Find the best split point
                    split_point = self._find_split_point(
                        remaining_text,
                        separator,
                        self.chunk_size,
                    )
                    if split_point > 0:
                        chunk = remaining_text[:split_point].strip()
                        remaining_text = remaining_text[split_point:].strip()
                        break
            
            # If no separator worked, force split at chunk_size
            if chunk is None:
                if len(remaining_text) <= self.chunk_size:
                    chunk = remaining_text
                    remaining_text = ""
                else:
                    # Force split, but try to break at word boundary
                    split_point = self.chunk_size
                    if remaining_text[split_point:split_point+1] != " ":
                        # Find last space before split point
                        last_space = remaining_text.rfind(" ", 0, split_point)
                        if last_space > self.chunk_size // 2:
                            split_point = last_space
                    
                    chunk = remaining_text[:split_point].strip()
                    remaining_text = remaining_text[split_point:].strip()
            
            if chunk:
                chunk_metadata = base_metadata.copy()
                chunk_metadata["chunk_index"] = chunk_index
                chunk_metadata["total_chunks"] = None  # Will be updated later
                
                chunks.append({
                    "content": chunk,
                    "metadata": chunk_metadata,
                })
                chunk_index += 1
                
                # Add overlap from previous chunk if not first chunk
                if chunks and chunk_index > 1 and self.chunk_overlap > 0:
                    overlap_text = chunks[-2]["content"][-self.chunk_overlap:]
                    chunks[-1]["content"] = overlap_text + "\n" + chunks[-1]["content"]
        
        # Update total_chunks in all metadata
        for chunk in chunks:
            chunk["metadata"]["total_chunks"] = len(chunks)
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def _find_split_point(
        self,
        text: str,
        separator: str,
        max_size: int,
    ) -> int:
        """Find the best split point using the given separator."""
        # Find all occurrences of the separator
        positions = [m.start() for m in re.finditer(re.escape(separator), text)]
        
        # Find the last position before max_size
        split_point = 0
        for pos in positions:
            if pos <= max_size:
                split_point = pos
            else:
                break
        
        # If we found a good split point, include the separator
        if split_point > 0:
            return split_point + len(separator)
        
        return 0
    
    def chunk_markdown_table(
        self,
        text: str,
        metadata: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Special chunking for markdown tables - splits by rows while preserving table structure.

        Args:
            text: Markdown text containing tables
            metadata: Base metadata to attach to all chunks

        Returns:
            List of chunk dictionaries
        """
        # Detect if text contains a table
        if "|" not in text or "\n|" not in text:
            # No table, use regular chunking
            return self.chunk_text(text, metadata)

        chunks = []
        base_metadata = (metadata or {}).copy()

        # Split by table boundaries or sections
        # Look for table start (line starting with |)
        lines = text.split("\n")
        current_chunk_lines = []
        chunk_index = 0
        in_table = False
        table_header = None
        table_separator = None

        # FIX: Detect table header ONCE at the beginning by scanning first 100 lines
        # This ensures the header is preserved for ALL table chunks, not just the first one
        for i, line in enumerate(lines[:100]):
            stripped = line.strip()
            # Look for common table header patterns
            if (stripped.startswith("|") and
                "|" in stripped[1:] and
                not stripped.startswith("|---")):
                # Check if next line is separator (|---|---|)
                if i+1 < len(lines) and lines[i+1].strip().startswith("|---"):
                    table_header = line
                    table_separator = lines[i+1]
                    logger.info(f"Detected table header: {table_header[:60]}...")
                    break

        for i, line in enumerate(lines):
            # Check if this is a table row
            is_table_row = line.strip().startswith("|") and "|" in line[1:]
            is_table_separator = line.strip().startswith("|---")

            if is_table_row and not is_table_separator:
                if not in_table:
                    # Start of a new table
                    in_table = True
                
                current_chunk_lines.append(line)

                # If chunk is getting large, split it
                current_size = len("\n".join(current_chunk_lines))
                if current_size > self.chunk_size and len(current_chunk_lines) > 10:
                    # FIX: ALWAYS prepend header and separator to table chunks
                    chunk_content = "\n".join(current_chunk_lines)
                    if table_header and table_header not in chunk_content:
                        # Prepend header and separator
                        header_block = table_header
                        if table_separator:
                            header_block = table_header + "\n" + table_separator
                        chunk_content = header_block + "\n" + chunk_content

                    chunk_metadata = base_metadata.copy()
                    chunk_metadata["chunk_index"] = chunk_index
                    chunk_metadata["is_table_chunk"] = True

                    chunks.append({
                        "content": chunk_content,
                        "metadata": chunk_metadata,
                    })
                    chunk_index += 1

                    # Keep last few lines for overlap
                    overlap_lines = current_chunk_lines[-5:] if len(current_chunk_lines) > 5 else current_chunk_lines
                    current_chunk_lines = overlap_lines
            else:
                # Not a table row
                if in_table and current_chunk_lines:
                    # End of table, finalize chunk
                    # FIX: ALWAYS prepend header and separator to table chunks
                    chunk_content = "\n".join(current_chunk_lines)
                    if table_header and table_header not in chunk_content:
                        # Prepend header and separator
                        header_block = table_header
                        if table_separator:
                            header_block = table_header + "\n" + table_separator
                        chunk_content = header_block + "\n" + chunk_content

                    chunk_metadata = base_metadata.copy()
                    chunk_metadata["chunk_index"] = chunk_index
                    chunk_metadata["is_table_chunk"] = True

                    chunks.append({
                        "content": chunk_content,
                        "metadata": chunk_metadata,
                    })
                    chunk_index += 1
                    current_chunk_lines = []
                    in_table = False
                    # NOTE: Keep table_header and table_separator for potential next table
                
                # Add non-table lines
                current_chunk_lines.append(line)
                
                # If chunk is getting large, split it
                current_size = len("\n".join(current_chunk_lines))
                if current_size > self.chunk_size:
                    chunk_content = "\n".join(current_chunk_lines)
                    chunk_metadata = base_metadata.copy()
                    chunk_metadata["chunk_index"] = chunk_index
                    
                    chunks.append({
                        "content": chunk_content,
                        "metadata": chunk_metadata,
                    })
                    chunk_index += 1
                    
                    # Keep last few lines for overlap
                    overlap_lines = current_chunk_lines[-10:] if len(current_chunk_lines) > 10 else current_chunk_lines
                    current_chunk_lines = overlap_lines
        
        # Add remaining lines
        if current_chunk_lines:
            chunk_content = "\n".join(current_chunk_lines)
            chunk_metadata = base_metadata.copy()
            chunk_metadata["chunk_index"] = chunk_index
            if in_table:
                chunk_metadata["is_table_chunk"] = True
                # FIX: ALWAYS prepend header and separator to table chunks
                if table_header and table_header not in chunk_content:
                    # Prepend header and separator
                    header_block = table_header
                    if table_separator:
                        header_block = table_header + "\n" + table_separator
                    chunk_content = header_block + "\n" + chunk_content

            chunks.append({
                "content": chunk_content,
                "metadata": chunk_metadata,
            })
        
        # Update total_chunks
        for chunk in chunks:
            chunk["metadata"]["total_chunks"] = len(chunks)
        
        logger.info(f"Split markdown with tables into {len(chunks)} chunks")
        return chunks

