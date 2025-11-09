"""
Docling-based document processor for converting various document formats
into structured data suitable for RAG systems.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
except ImportError:
    raise ImportError(
        "docling is not installed. Install it with: pip install docling"
    )

logger = logging.getLogger(__name__)


class DoclingProcessor:
    """
    Processor for converting documents using Docling.
    
    Supports various formats: PDF, DOCX, PPTX, HTML, and more.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Docling processor.
        
        Args:
            config: Optional configuration dictionary for DocumentConverter
        """
        self.config = config or {}
        self.converter = DocumentConverter(**self.config)
        logger.info("DoclingProcessor initialized")

    def process_document(
        self,
        source: str | Path,
        output_format: str = "markdown",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a document and convert it to structured format.
        
        Args:
            source: Path to document file or URL
            output_format: Output format ('markdown', 'json', 'text')
            metadata: Optional metadata to attach to the document
            
        Returns:
            Dictionary containing:
                - content: Processed document content
                - format: Output format used
                - metadata: Document metadata
                - source: Source path/URL
        """
        try:
            logger.info(f"Processing document: {source}")
            
            # Convert document
            result = self.converter.convert(str(source))
            
            # Extract content based on format
            if output_format == "markdown":
                content = result.document.export_to_markdown()
            elif output_format == "json":
                content = result.document.export_to_dict()
            elif output_format == "text":
                content = result.document.export_to_text()
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
            
            # Prepare result
            processed_doc = {
                "content": content if isinstance(content, str) else str(content),
                "format": output_format,
                "metadata": metadata or {},
                "source": str(source),
            }
            
            # Add document metadata if available
            if hasattr(result.document, "metadata"):
                processed_doc["metadata"].update(result.document.metadata)
            
            logger.info(f"Successfully processed document: {source}")
            return processed_doc
            
        except Exception as e:
            logger.error(f"Error processing document {source}: {str(e)}")
            raise

    def process_directory(
        self,
        directory: str | Path,
        output_format: str = "markdown",
        file_extensions: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Process all supported documents in a directory.
        
        Args:
            directory: Path to directory containing documents
            output_format: Output format for processed documents
            file_extensions: Optional list of file extensions to process
                           (default: PDF, DOCX, PPTX, HTML)
        
        Returns:
            List of processed documents
        """
        if file_extensions is None:
            file_extensions = [".pdf", ".docx", ".pptx", ".html", ".htm"]
        
        directory_path = Path(directory)
        if not directory_path.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        
        processed_docs = []
        
        for file_path in directory_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in file_extensions:
                try:
                    doc = self.process_document(
                        file_path,
                        output_format=output_format,
                        metadata={"file_path": str(file_path)},
                    )
                    processed_docs.append(doc)
                except Exception as e:
                    logger.warning(f"Failed to process {file_path}: {str(e)}")
                    continue
        
        logger.info(f"Processed {len(processed_docs)} documents from {directory}")
        return processed_docs

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported document formats.
        
        Returns:
            List of supported file extensions
        """
        return [
            ".pdf",
            ".docx",
            ".pptx",
            ".html",
            ".htm",
            ".md",
            ".txt",
        ]

