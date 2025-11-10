"""
Comprehensive initialization and testing script for the AI Summarization Reference Architecture.

This script:
1. Initializes the document store
2. Tests all components
3. Demonstrates usage patterns
4. Validates the architecture

Extends existing components rather than creating isolated tests.
"""

import sys
from pathlib import Path
import logging
import json
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from document_store.orchestrator import DocumentStoreOrchestrator
from document_store.processors.docling_processor import DoclingProcessor
from document_store.storage.vector_store import VectorStore
from document_store.search.rag_query import RAGQueryInterface
from document_store.search.web_search import WebSearchTool

# Try to import agents (may not be available)
try:
    from document_store.agents.adk_agent import ADKAgentQuery
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    ADKAgentQuery = None

try:
    from document_store.agents.ollama_agent import OllamaAgent
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    OllamaAgent = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArchitectureTester:
    """Comprehensive tester that extends existing components."""
    
    def __init__(self, test_data_dir: Path = None):
        """Initialize the tester."""
        self.test_data_dir = test_data_dir or Path(__file__).parent.parent / "data" / "test"
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        self.results = {
            "initialization": {},
            "component_tests": {},
            "integration_tests": {},
            "summary": {}
        }
        logger.info("ArchitectureTester initialized")

    def test_initialization(self) -> Dict[str, Any]:
        """Test 1: Initialize all components."""
        logger.info("\n" + "="*60)
        logger.info("TEST 1: Component Initialization")
        logger.info("="*60)
        
        results = {}
        
        # Test Docling Processor
        try:
            processor = DoclingProcessor()
            results["docling_processor"] = {
                "status": "success",
                "supported_formats": processor.get_supported_formats()
            }
            logger.info("✓ Docling Processor initialized")
        except Exception as e:
            results["docling_processor"] = {"status": "error", "error": str(e)}
            logger.error(f"✗ Docling Processor failed: {e}")
        
        # Test Vector Store
        try:
            vector_store = VectorStore(
                persist_directory=str(self.test_data_dir / "chroma_test"),
                collection_name="test_patterns"
            )
            info = vector_store.get_collection_info()
            results["vector_store"] = {
                "status": "success",
                "info": info
            }
            logger.info(f"✓ Vector Store initialized: {info}")
        except Exception as e:
            results["vector_store"] = {"status": "error", "error": str(e)}
            logger.error(f"✗ Vector Store failed: {e}")
        
        # Test RAG Query Interface
        try:
            if "vector_store" in results and results["vector_store"]["status"] == "success":
                rag_interface = RAGQueryInterface(vector_store)
                results["rag_interface"] = {"status": "success"}
                logger.info("✓ RAG Query Interface initialized")
            else:
                results["rag_interface"] = {"status": "skipped", "reason": "Vector store not available"}
        except Exception as e:
            results["rag_interface"] = {"status": "error", "error": str(e)}
            logger.error(f"✗ RAG Query Interface failed: {e}")
        
        # Test Web Search
        try:
            web_search = WebSearchTool()
            results["web_search"] = {"status": "success"}
            logger.info("✓ Web Search Tool initialized")
        except Exception as e:
            results["web_search"] = {"status": "error", "error": str(e)}
            logger.error(f"✗ Web Search Tool failed: {e}")
        
        # Test ADK Agent (if available)
        if ADK_AVAILABLE:
            try:
                if "vector_store" in results and results["vector_store"]["status"] == "success":
                    adk_agent = ADKAgentQuery(vector_store)
                    results["adk_agent"] = {
                        "status": "success",
                        "info": adk_agent.get_agent_info()
                    }
                    logger.info("✓ ADK Agent initialized")
                else:
                    results["adk_agent"] = {"status": "skipped", "reason": "Vector store not available"}
            except Exception as e:
                results["adk_agent"] = {"status": "warning", "error": str(e)}
                logger.warning(f"⚠ ADK Agent not fully available: {e}")
        else:
            results["adk_agent"] = {"status": "not_installed"}
            logger.info("⚠ ADK Agent not installed (expected)")
        
        # Test Ollama Agent (if available)
        if OLLAMA_AVAILABLE:
            try:
                if "vector_store" in results and results["vector_store"]["status"] == "success":
                    ollama_agent = OllamaAgent(
                        model="llama3",
                        vector_store=vector_store
                    )
                    models = ollama_agent.list_available_models()
                    results["ollama_agent"] = {
                        "status": "success",
                        "model": "llama3",
                        "available_models": models
                    }
                    logger.info(f"✓ Ollama Agent initialized with model: llama3")
                else:
                    results["ollama_agent"] = {"status": "skipped", "reason": "Vector store not available"}
            except Exception as e:
                results["ollama_agent"] = {"status": "warning", "error": str(e)}
                logger.warning(f"⚠ Ollama Agent not fully available: {e}")
        else:
            results["ollama_agent"] = {"status": "not_installed"}
            logger.info("⚠ Ollama Agent not installed (install ollama package and run 'ollama serve')")
        
        # Test Orchestrator
        try:
            orchestrator = DocumentStoreOrchestrator(
                persist_directory=str(self.test_data_dir / "chroma_test"),
                collection_name="test_patterns",
                use_adk_agent=ADK_AVAILABLE,
                ollama_model="llama3" if OLLAMA_AVAILABLE else None
            )
            info = orchestrator.get_store_info()
            results["orchestrator"] = {
                "status": "success",
                "info": info
            }
            logger.info(f"✓ Orchestrator initialized: {info}")
        except Exception as e:
            results["orchestrator"] = {"status": "error", "error": str(e)}
            logger.error(f"✗ Orchestrator failed: {e}")
        
        self.results["initialization"] = results
        return results

    def test_document_processing(self) -> Dict[str, Any]:
        """Test 2: Document processing capabilities."""
        logger.info("\n" + "="*60)
        logger.info("TEST 2: Document Processing")
        logger.info("="*60)
        
        results = {}
        processor = DoclingProcessor()
        
        # Create a test markdown document
        test_doc_path = self.test_data_dir / "test_pattern.md"
        test_content = """# Basic RAG Pattern

## Overview
Basic RAG (Retrieval-Augmented Generation) is a pattern that combines retrieval and generation.

## When to Use
- Simple document Q&A
- Single-step retrieval needed
- Straightforward queries

## Architecture
1. Query processing
2. Document retrieval
3. Context assembly
4. LLM generation
"""
        test_doc_path.write_text(test_content)
        
        try:
            # Test processing markdown (as text)
            processed = processor.process_document(
                test_doc_path,
                output_format="text",
                metadata={"pattern_type": "basic-rag", "vendor": "general"}
            )
            results["document_processing"] = {
                "status": "success",
                "content_length": len(processed["content"]),
                "metadata": processed["metadata"]
            }
            logger.info(f"✓ Document processed: {len(processed['content'])} characters")
            
            # Store processed document for later tests
            self.test_document = processed
            
        except Exception as e:
            results["document_processing"] = {"status": "error", "error": str(e)}
            logger.error(f"✗ Document processing failed: {e}")
            self.test_document = None
        
        self.results["component_tests"]["document_processing"] = results
        return results

    def test_vector_store_operations(self) -> Dict[str, Any]:
        """Test 3: Vector store operations."""
        logger.info("\n" + "="*60)
        logger.info("TEST 3: Vector Store Operations")
        logger.info("="*60)
        
        results = {}
        
        try:
            vector_store = VectorStore(
                persist_directory=str(self.test_data_dir / "chroma_test"),
                collection_name="test_patterns"
            )
            
            # Add test documents if we have them
            if hasattr(self, 'test_document') and self.test_document:
                vector_store.add_documents([self.test_document])
                logger.info("✓ Test document added to vector store")
            
            # Test query
            query_result = vector_store.query(
                query_text="What is basic RAG?",
                n_results=3
            )
            
            results["vector_store_operations"] = {
                "status": "success",
                "query_results_count": len(query_result.get("documents", [])),
                "collection_info": vector_store.get_collection_info()
            }
            logger.info(f"✓ Vector store query successful: {len(query_result.get('documents', []))} results")
            
        except Exception as e:
            results["vector_store_operations"] = {"status": "error", "error": str(e)}
            logger.error(f"✗ Vector store operations failed: {e}")
        
        self.results["component_tests"]["vector_store"] = results
        return results

    def test_rag_query_interface(self) -> Dict[str, Any]:
        """Test 4: RAG query interface."""
        logger.info("\n" + "="*60)
        logger.info("TEST 4: RAG Query Interface")
        logger.info("="*60)
        
        results = {}
        
        try:
            vector_store = VectorStore(
                persist_directory=str(self.test_data_dir / "chroma_test"),
                collection_name="test_patterns"
            )
            
            # Add test document if available
            if hasattr(self, 'test_document') and self.test_document:
                vector_store.add_documents([self.test_document])
            
            rag_interface = RAGQueryInterface(vector_store)
            
            # Test query
            query_result = rag_interface.query_patterns(
                query="What is basic RAG pattern?",
                n_results=3
            )
            
            results["rag_query"] = {
                "status": "success",
                "query": query_result.get("query"),
                "results_count": query_result.get("count", 0)
            }
            logger.info(f"✓ RAG query successful: {query_result.get('count', 0)} results")
            
        except Exception as e:
            results["rag_query"] = {"status": "error", "error": str(e)}
            logger.error(f"✗ RAG query failed: {e}")
        
        self.results["component_tests"]["rag_query"] = results
        return results

    def test_web_search(self) -> Dict[str, Any]:
        """Test 5: Web search functionality."""
        logger.info("\n" + "="*60)
        logger.info("TEST 5: Web Search")
        logger.info("="*60)
        
        results = {}
        
        try:
            web_search = WebSearchTool(backend="duckduckgo")
            
            # Test search
            search_results = web_search.search(
                query="RAG patterns AI",
                max_results=3
            )
            
            results["web_search"] = {
                "status": "success",
                "results_count": len(search_results),
                "sample_results": search_results[:2] if search_results else []
            }
            logger.info(f"✓ Web search successful: {len(search_results)} results")
            
        except Exception as e:
            results["web_search"] = {"status": "error", "error": str(e)}
            logger.error(f"✗ Web search failed: {e}")
        
        self.results["component_tests"]["web_search"] = results
        return results

    def test_orchestrator_integration(self) -> Dict[str, Any]:
        """Test 6: Full orchestrator integration."""
        logger.info("\n" + "="*60)
        logger.info("TEST 6: Orchestrator Integration")
        logger.info("="*60)
        
        results = {}
        
        try:
            orchestrator = DocumentStoreOrchestrator(
                persist_directory=str(self.test_data_dir / "chroma_test"),
                collection_name="test_patterns",
                use_adk_agent=ADK_AVAILABLE,
                ollama_model="llama3" if OLLAMA_AVAILABLE else None
            )
            
            # Test document ingestion
            test_doc_path = self.test_data_dir / "test_pattern.md"
            if test_doc_path.exists():
                ingested = orchestrator.ingest_documents([test_doc_path])
                logger.info(f"✓ Document ingestion: {ingested} documents")
            
            # Test querying (extend existing query_patterns method)
            query_result = orchestrator.query_patterns(
                query="What is basic RAG?",
                n_results=3,
                use_agent=False,  # Use direct query for testing
            )
            
            results["orchestrator"] = {
                "status": "success",
                "query_results": query_result.get("count", 0),
                "store_info": orchestrator.get_store_info()
            }
            logger.info(f"✓ Orchestrator integration successful: {query_result.get('count', 0)} results")
            
        except Exception as e:
            results["orchestrator"] = {"status": "error", "error": str(e)}
            logger.error(f"✗ Orchestrator integration failed: {e}")
        
        self.results["integration_tests"]["orchestrator"] = results
        return results

    def test_agent_integrations(self) -> Dict[str, Any]:
        """Test 7: Agent integrations (if available)."""
        logger.info("\n" + "="*60)
        logger.info("TEST 7: Agent Integrations")
        logger.info("="*60)
        
        results = {}
        
        # Test ADK Agent
        if ADK_AVAILABLE:
            try:
                vector_store = VectorStore(
                    persist_directory=str(self.test_data_dir / "chroma_test"),
                    collection_name="test_patterns"
                )
                adk_agent = ADKAgentQuery(vector_store)
                agent_info = adk_agent.get_agent_info()
                results["adk_agent"] = {
                    "status": "success",
                    "info": agent_info
                }
                logger.info("✓ ADK Agent integration successful")
            except Exception as e:
                results["adk_agent"] = {"status": "warning", "error": str(e)}
                logger.warning(f"⚠ ADK Agent integration: {e}")
        else:
            results["adk_agent"] = {"status": "not_installed"}
            logger.info("⚠ ADK Agent not installed (expected)")
        
        # Test Ollama Agent
        if OLLAMA_AVAILABLE:
            try:
                vector_store = VectorStore(
                    persist_directory=str(self.test_data_dir / "chroma_test"),
                    collection_name="test_patterns"
                )
                ollama_agent = OllamaAgent(
                    model="llama3",
                    vector_store=vector_store
                )
                models = ollama_agent.list_available_models()
                results["ollama_agent"] = {
                    "status": "success",
                    "available_models": models
                }
                logger.info(f"✓ Ollama Agent integration successful: {len(models)} models")
            except Exception as e:
                results["ollama_agent"] = {"status": "warning", "error": str(e)}
                logger.warning(f"⚠ Ollama Agent integration: {e}")
        else:
            results["ollama_agent"] = {"status": "not_installed"}
            logger.info("⚠ Ollama Agent not installed (install ollama and run 'ollama serve')")
        
        self.results["integration_tests"]["agents"] = results
        return results

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests in sequence."""
        logger.info("\n" + "="*60)
        logger.info("COMPREHENSIVE ARCHITECTURE TESTING")
        logger.info("="*60)
        
        # Run all tests
        self.test_initialization()
        self.test_document_processing()
        self.test_vector_store_operations()
        self.test_rag_query_interface()
        self.test_web_search()
        self.test_orchestrator_integration()
        self.test_agent_integrations()
        
        # Generate summary
        self._generate_summary()
        
        return self.results

    def _generate_summary(self):
        """Generate test summary."""
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        warnings = 0
        
        def count_status(d, status_key="status"):
            nonlocal total_tests, passed_tests, failed_tests, warnings
            if isinstance(d, dict):
                if status_key in d:
                    total_tests += 1
                    status = d[status_key]
                    if status == "success":
                        passed_tests += 1
                    elif status == "error":
                        failed_tests += 1
                    elif status in ["warning", "not_installed", "skipped"]:
                        warnings += 1
                for v in d.values():
                    if isinstance(v, (dict, list)):
                        count_status(v, status_key)
            elif isinstance(d, list):
                for item in d:
                    count_status(item, status_key)
        
        count_status(self.results)
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "warnings": warnings,
            "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
        }
        
        self.results["summary"] = summary
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Warnings/Skipped: {warnings}")
        logger.info(f"Success Rate: {summary['success_rate']}")
        
        # Save results
        results_file = self.test_data_dir.parent / "test_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info(f"\n✓ Test results saved to: {results_file}")


def main():
    """Main entry point - extends existing scripts pattern."""
    logger.info("Starting comprehensive architecture initialization and testing...")
    
    tester = ArchitectureTester()
    results = tester.run_all_tests()
    
    logger.info("\n" + "="*60)
    logger.info("INITIALIZATION AND TESTING COMPLETE")
    logger.info("="*60)
    
    return results


if __name__ == "__main__":
    main()

