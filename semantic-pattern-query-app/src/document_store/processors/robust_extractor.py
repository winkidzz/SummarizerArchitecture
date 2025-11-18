"""
Layer 1: Robust Document Extractor

Multi-stage extraction with fallbacks for PDFs and markdown files.
Based on the production RAG architecture.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Result of document extraction."""
    text: str
    confidence: float
    method: str
    metadata: Dict[str, Any]
    has_tables: bool = False
    tables: Optional[List[Dict[str, Any]]] = None


class RobustDocumentExtractor:
    """
    Multi-stage document extractor with fallback strategy.
    
    For PDFs:
    - Stage 1: Fast extraction (pypdf)
    - Stage 2: Table-aware extraction (pdfplumber)
    
    For Markdown:
    - Direct markdown parsing
    """
    
    def __init__(self):
        """Initialize the extractor."""
        self.pypdf_available = pypdf is not None
        self.pdfplumber_available = pdfplumber is not None
        
        if not self.pypdf_available:
            logger.warning("pypdf not available. PDF extraction will be limited.")
        if not self.pdfplumber_available:
            logger.warning("pdfplumber not available. Table extraction will be limited.")
    
    def extract(
        self,
        document_path: str,
        document_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExtractionResult:
        """
        Extract document with multi-stage fallback.
        
        Args:
            document_path: Path to document
            document_type: Optional document type hint
            metadata: Optional metadata to include
            
        Returns:
            ExtractionResult with text, confidence, and metadata
        """
        path = Path(document_path)
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")
        
        # Auto-detect document type
        if document_type is None:
            document_type = self._detect_document_type(path)
        
        metadata = metadata or {}
        metadata["source_path"] = str(path)
        metadata["document_type"] = document_type
        
        # Route to appropriate extractor
        if document_type == "pdf":
            return self._extract_pdf(path, metadata)
        elif document_type == "markdown":
            return self._extract_markdown(path, metadata)
        elif document_type == "text":
            return self._extract_text(path, metadata)
        else:
            # Try PDF first, then text
            try:
                return self._extract_pdf(path, metadata)
            except Exception:
                return self._extract_text(path, metadata)
    
    def _extract_pdf(
        self,
        path: Path,
        metadata: Dict[str, Any]
    ) -> ExtractionResult:
        """
        Extract PDF with multi-stage fallback.
        
        Stage 1: Fast extraction (pypdf)
        Stage 2: Table-aware extraction (pdfplumber)
        """
        # Stage 1: Fast extraction (pypdf)
        if self.pypdf_available:
            try:
                result = self._pypdf_extract(path, metadata)
                if result.confidence > 0.85:
                    logger.info(f"Stage 1 (pypdf) succeeded for {path}")
                    return result
            except Exception as e:
                logger.debug(f"Stage 1 (pypdf) failed: {e}")
        
        # Stage 2: Table-aware extraction (pdfplumber)
        if self.pdfplumber_available:
            try:
                result = self._pdfplumber_extract(path, metadata)
                if result.confidence > 0.75:
                    logger.info(f"Stage 2 (pdfplumber) succeeded for {path}")
                    return result
            except Exception as e:
                logger.debug(f"Stage 2 (pdfplumber) failed: {e}")
        
        # Fallback: Try pypdf even if confidence was low
        if self.pypdf_available:
            try:
                result = self._pypdf_extract(path, metadata)
                result.confidence = 0.5  # Lower confidence for fallback
                logger.warning(f"Using fallback extraction for {path}")
                return result
            except Exception as e:
                logger.error(f"All PDF extraction methods failed: {e}")
        
        raise ExtractionException(f"Could not extract PDF: {path}")
    
    def _pypdf_extract(
        self,
        path: Path,
        metadata: Dict[str, Any]
    ) -> ExtractionResult:
        """Extract using pypdf (fast, basic)."""
        text_parts = []
        num_pages = 0
        
        with open(path, "rb") as f:
            pdf_reader = pypdf.PdfReader(f)
            num_pages = len(pdf_reader.pages)
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text.strip():
                    text_parts.append(text)
        
        full_text = "\n\n".join(text_parts)
        
        # Calculate confidence based on text extraction quality
        confidence = self._calculate_confidence(full_text, num_pages)
        
        metadata["num_pages"] = num_pages
        metadata["extraction_method"] = "pypdf"
        
        return ExtractionResult(
            text=full_text,
            confidence=confidence,
            method="pypdf",
            metadata=metadata,
            has_tables=False
        )
    
    def _pdfplumber_extract(
        self,
        path: Path,
        metadata: Dict[str, Any]
    ) -> ExtractionResult:
        """Extract using pdfplumber (table-aware)."""
        text_parts = []
        tables = []
        
        with pdfplumber.open(path) as pdf:
            num_pages = len(pdf.pages)
            
            for page in pdf.pages:
                # Extract text
                text = page.extract_text()
                if text and text.strip():
                    text_parts.append(text)
                
                # Extract tables
                page_tables = page.extract_tables()
                if page_tables:
                    for table in page_tables:
                        tables.append({
                            "data": table,
                            "page": page.page_number
                        })
        
        full_text = "\n\n".join(text_parts)
        
        # Calculate confidence
        confidence = self._calculate_confidence(full_text, num_pages)
        if tables:
            confidence = min(0.95, confidence + 0.1)  # Boost for tables
        
        metadata["num_pages"] = num_pages
        metadata["extraction_method"] = "pdfplumber"
        metadata["num_tables"] = len(tables)
        
        return ExtractionResult(
            text=full_text,
            confidence=confidence,
            method="pdfplumber",
            metadata=metadata,
            has_tables=len(tables) > 0,
            tables=tables if tables else None
        )
    
    def _extract_markdown(
        self,
        path: Path,
        metadata: Dict[str, Any]
    ) -> ExtractionResult:
        """Extract markdown file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            
            # Markdown extraction is high confidence
            confidence = 0.95
            
            metadata["extraction_method"] = "markdown"
            
            return ExtractionResult(
                text=text,
                confidence=confidence,
                method="markdown",
                metadata=metadata,
                has_tables=False
            )
        except Exception as e:
            logger.error(f"Error extracting markdown {path}: {e}")
            raise
    
    def _extract_text(
        self,
        path: Path,
        metadata: Dict[str, Any]
    ) -> ExtractionResult:
        """Extract plain text file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            
            confidence = 0.9
            
            metadata["extraction_method"] = "text"
            
            return ExtractionResult(
                text=text,
                confidence=confidence,
                method="text",
                metadata=metadata,
                has_tables=False
            )
        except Exception as e:
            logger.error(f"Error extracting text {path}: {e}")
            raise
    
    def _detect_document_type(self, path: Path) -> str:
        """Detect document type from extension."""
        ext = path.suffix.lower()
        
        if ext == ".pdf":
            return "pdf"
        elif ext in [".md", ".markdown"]:
            return "markdown"
        elif ext in [".txt", ".text"]:
            return "text"
        else:
            return "unknown"
    
    def _calculate_confidence(
        self,
        text: str,
        num_pages: int
    ) -> float:
        """
        Calculate extraction confidence based on text quality.
        
        Factors:
        - Text length (more is better)
        - Non-empty pages ratio
        - Text structure (paragraphs, sentences)
        """
        if not text or not text.strip():
            return 0.0
        
        # Base confidence from text length
        text_length = len(text.strip())
        words = len(text.split())
        
        # Minimum viable extraction
        if words < 10:
            return 0.3
        
        # Good extraction indicators
        confidence = 0.5
        
        # Length bonus
        if words > 100:
            confidence += 0.2
        if words > 500:
            confidence += 0.1
        
        # Structure bonus (paragraphs, sentences)
        paragraphs = text.count("\n\n")
        sentences = text.count(".") + text.count("!") + text.count("?")
        
        if paragraphs > 5:
            confidence += 0.1
        if sentences > 10:
            confidence += 0.1
        
        return min(0.95, confidence)


class ExtractionException(Exception):
    """Exception raised during document extraction."""
    pass

