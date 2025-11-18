#!/usr/bin/env python3
"""
Check Prerequisites for Testing

Verifies that all required dependencies and services are available.
"""

import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_python_package(package_name: str, import_name: str = None) -> bool:
    """Check if a Python package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        logger.info(f"✅ {package_name} is installed")
        return True
    except ImportError:
        logger.warning(f"❌ {package_name} is NOT installed")
        return False


def check_service(url: str, name: str) -> bool:
    """Check if a service is running."""
    try:
        import urllib.request
        urllib.request.urlopen(url, timeout=2)
        logger.info(f"✅ {name} is running at {url}")
        return True
    except Exception:
        logger.warning(f"❌ {name} is NOT running at {url}")
        return False


def check_ollama() -> bool:
    """Check if Ollama is running."""
    try:
        import ollama
        client = ollama.Client(host="http://localhost:11434")
        models = client.list()
        logger.info(f"✅ Ollama is running")
        logger.info(f"   Available models: {[m['name'] for m in models.get('models', [])]}")
        return True
    except Exception as e:
        logger.warning(f"❌ Ollama is NOT running: {e}")
        return False


def main():
    """Check all prerequisites."""
    logger.info("=" * 80)
    logger.info("Checking Prerequisites for Semantic Pattern Query App")
    logger.info("=" * 80)
    
    results = {}
    
    # Python packages
    logger.info("\n📦 Python Packages:")
    results["pypdf"] = check_python_package("pypdf")
    results["pdfplumber"] = check_python_package("pdfplumber")
    results["sentence_transformers"] = check_python_package("sentence-transformers", "sentence_transformers")
    results["qdrant_client"] = check_python_package("qdrant-client", "qdrant_client")
    results["elasticsearch"] = check_python_package("elasticsearch")
    results["redis"] = check_python_package("redis")
    results["ollama"] = check_python_package("ollama")
    results["fastapi"] = check_python_package("fastapi")
    results["numpy"] = check_python_package("numpy")
    results["scipy"] = check_python_package("scipy")
    
    # Services
    logger.info("\n🔧 Services:")
    results["qdrant"] = check_service("http://localhost:6333/health", "Qdrant")
    results["elasticsearch"] = check_service("http://localhost:9200/_cluster/health", "Elasticsearch")
    results["redis"] = check_service("http://localhost:6379", "Redis")  # This won't work, need redis-cli
    results["ollama_service"] = check_ollama()
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("Summary")
    logger.info("=" * 80)
    
    packages_ok = sum(1 for k, v in results.items() if k not in ["qdrant", "elasticsearch", "redis", "ollama_service"] and v)
    services_ok = sum(1 for k in ["qdrant", "elasticsearch", "redis", "ollama_service"] if results.get(k))
    
    logger.info(f"Python packages: {packages_ok}/{len(results) - 4} installed")
    logger.info(f"Services: {services_ok}/4 running")
    
    if packages_ok < len(results) - 4:
        logger.info("\n💡 To install missing packages:")
        logger.info("   pip install -r requirements.txt")
    
    if services_ok < 4:
        logger.info("\n💡 To start services:")
        logger.info("   docker-compose up -d")
        logger.info("   ollama serve")
    
    all_ok = all(results.values())
    
    if all_ok:
        logger.info("\n✅ All prerequisites are met!")
        return 0
    else:
        logger.warning("\n⚠️  Some prerequisites are missing. Install them to run full tests.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

