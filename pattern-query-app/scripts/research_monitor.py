"""
Research Monitor - Automated arXiv and Research Source Monitoring

This script implements the research-monitor Claude Skill, automatically searching
for and ingesting the latest AI/RAG research papers from arXiv and other reputable sources.

Usage:
    python scripts/research_monitor.py --mode monitor
    python scripts/research_monitor.py --mode ingest --arxiv-id 2401.12345
    python scripts/research_monitor.py --mode search --query "contextual retrieval"
"""

import os
import sys
import json
import time
import argparse
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import xml.etree.ElementTree as ET

import chromadb
from chromadb.utils import embedding_functions


@dataclass
class ResearchPaper:
    """Research paper metadata."""
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    publish_date: str
    url: str
    categories: List[str]
    citations: int = 0  # Can be populated from external API
    relevance_score: float = 0.0


class ArxivClient:
    """Client for arXiv API."""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self):
        self.session = requests.Session()

    def search_papers(
        self,
        query: str,
        max_results: int = 50,
        start_date: Optional[str] = None
    ) -> List[ResearchPaper]:
        """
        Search arXiv for papers matching query.

        Args:
            query: Search query (e.g., "retrieval augmented generation")
            max_results: Maximum number of results to return
            start_date: Filter papers published after this date (YYYY-MM-DD)

        Returns:
            List of ResearchPaper objects
        """

        # Build search query
        search_query = f'all:"{query}"'

        # Add date filter if provided
        if start_date:
            search_query += f' AND submittedDate:[{start_date}0000 TO {datetime.now().strftime("%Y%m%d")}2359]'

        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }

        print(f"Searching arXiv for: {query}")
        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()

        # Parse XML response
        papers = self._parse_arxiv_response(response.text)
        print(f"Found {len(papers)} papers")

        return papers

    def _parse_arxiv_response(self, xml_text: str) -> List[ResearchPaper]:
        """Parse arXiv API XML response."""

        papers = []
        root = ET.fromstring(xml_text)

        # Namespace for arXiv API
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }

        for entry in root.findall('atom:entry', ns):
            # Extract arXiv ID from URL
            id_url = entry.find('atom:id', ns).text
            arxiv_id = id_url.split('/abs/')[-1]

            # Extract metadata
            title = entry.find('atom:title', ns).text.strip()
            abstract = entry.find('atom:summary', ns).text.strip()
            publish_date = entry.find('atom:published', ns).text[:10]

            # Extract authors
            authors = [
                author.find('atom:name', ns).text
                for author in entry.findall('atom:author', ns)
            ]

            # Extract categories
            categories = [
                cat.attrib['term']
                for cat in entry.findall('atom:category', ns)
            ]

            paper = ResearchPaper(
                arxiv_id=arxiv_id,
                title=title,
                authors=authors,
                abstract=abstract,
                publish_date=publish_date,
                url=id_url,
                categories=categories
            )

            papers.append(paper)

        return papers


class WebSourceMonitor:
    """Monitor web sources for AI research updates."""

    SOURCES = {
        'anthropic': {
            'name': 'Anthropic Blog',
            'url': 'https://www.anthropic.com/research',
            'topics': ['Claude', 'Constitutional AI', 'RAG', 'Prompt Caching']
        },
        'google_ai': {
            'name': 'Google AI Blog',
            'url': 'https://blog.research.google/search/label/Gemini',
            'topics': ['Gemini', 'Vertex AI', 'Long Context']
        },
        'microsoft': {
            'name': 'Microsoft Research AI',
            'url': 'https://www.microsoft.com/en-us/research/blog/category/artificial-intelligence/',
            'topics': ['Azure OpenAI', 'GPT-4', 'RAG']
        },
        'aws': {
            'name': 'AWS Machine Learning Blog',
            'url': 'https://aws.amazon.com/blogs/machine-learning/',
            'topics': ['Bedrock', 'Healthcare AI', 'RAG']
        }
    }

    def check_source(self, source_key: str) -> Dict:
        """
        Check a web source for updates.

        Note: This is a placeholder implementation.
        In production, implement proper web scraping with:
        - BeautifulSoup4 or Playwright for dynamic content
        - RSS feed parsing if available
        - Respect robots.txt and rate limits

        Args:
            source_key: Key from SOURCES dict

        Returns:
            Dictionary with update information
        """

        source = self.SOURCES.get(source_key)
        if not source:
            raise ValueError(f"Unknown source: {source_key}")

        print(f"Checking {source['name']}...")

        # Placeholder - in production, implement actual web scraping
        return {
            'source': source['name'],
            'url': source['url'],
            'checked_at': datetime.now().isoformat(),
            'status': 'placeholder - implement web scraping',
            'updates': []
        }


class ResearchQualityEvaluator:
    """Evaluate research paper quality and relevance."""

    # High-quality venues for AI/ML research
    TOP_VENUES = [
        'cs.CL',  # Computation and Language
        'cs.AI',  # Artificial Intelligence
        'cs.LG',  # Machine Learning
        'cs.IR',  # Information Retrieval
    ]

    # Healthcare AI categories
    HEALTHCARE_CATEGORIES = [
        'cs.CY',  # Computers and Society
        'q-bio',  # Quantitative Biology
    ]

    def evaluate_paper(self, paper: ResearchPaper, query: str) -> float:
        """
        Evaluate paper quality and relevance.

        Args:
            paper: ResearchPaper to evaluate
            query: Original search query

        Returns:
            Relevance score (0.0 to 1.0)
        """

        score = 0.0

        # Category relevance (0-0.3)
        if any(cat in self.TOP_VENUES for cat in paper.categories):
            score += 0.3
        elif any(cat.startswith('cs.') for cat in paper.categories):
            score += 0.15

        # Healthcare relevance (0-0.2)
        healthcare_keywords = ['medical', 'clinical', 'healthcare', 'patient', 'diagnosis']
        if any(kw in paper.title.lower() or kw in paper.abstract.lower() for kw in healthcare_keywords):
            score += 0.2

        # Title/abstract relevance to query (0-0.3)
        query_terms = query.lower().split()
        title_abstract = (paper.title + ' ' + paper.abstract).lower()

        matching_terms = sum(1 for term in query_terms if term in title_abstract)
        score += 0.3 * (matching_terms / len(query_terms))

        # Recency (0-0.2) - prefer papers from last 6 months
        pub_date = datetime.strptime(paper.publish_date, '%Y-%m-%d')
        days_old = (datetime.now() - pub_date).days

        if days_old < 180:  # 6 months
            score += 0.2 * (1 - days_old / 180)

        paper.relevance_score = score
        return score


class ChromaDBManager:
    """Manage research papers in ChromaDB."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB client.

        Args:
            persist_directory: Directory to persist ChromaDB data
        """

        self.client = chromadb.PersistentClient(path=persist_directory)

        # Use sentence-transformers for embeddings
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # Get or create research papers collection
        self.collection = self.client.get_or_create_collection(
            name="research_papers",
            embedding_function=self.embedding_function,
            metadata={"description": "AI/RAG research papers from arXiv and other sources"}
        )

    def ingest_paper(self, paper: ResearchPaper) -> None:
        """
        Ingest research paper into ChromaDB.

        Args:
            paper: ResearchPaper to ingest
        """

        # Check if paper already exists
        existing = self.collection.get(ids=[paper.arxiv_id])
        if existing['ids']:
            print(f"Paper {paper.arxiv_id} already in database, skipping")
            return

        # Prepare document text (title + abstract)
        document = f"{paper.title}\n\n{paper.abstract}"

        # Prepare metadata
        metadata = {
            'arxiv_id': paper.arxiv_id,
            'title': paper.title,
            'authors': ', '.join(paper.authors),
            'publish_date': paper.publish_date,
            'url': paper.url,
            'categories': ', '.join(paper.categories),
            'relevance_score': paper.relevance_score,
            'ingested_at': datetime.now().isoformat()
        }

        # Add to collection
        self.collection.add(
            ids=[paper.arxiv_id],
            documents=[document],
            metadatas=[metadata]
        )

        print(f"Ingested: {paper.title[:60]}... (arXiv:{paper.arxiv_id})")

    def search_papers(self, query: str, n_results: int = 10) -> Dict:
        """
        Search ingested papers.

        Args:
            query: Search query
            n_results: Number of results to return

        Returns:
            Search results from ChromaDB
        """

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        return results

    def get_recent_papers(self, days: int = 30) -> List[Dict]:
        """
        Get papers ingested in last N days.

        Args:
            days: Number of days to look back

        Returns:
            List of paper metadata
        """

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Get all papers (ChromaDB doesn't support date range queries directly)
        all_papers = self.collection.get()

        recent = []
        for i, metadata in enumerate(all_papers['metadatas']):
            if metadata.get('ingested_at', '') >= cutoff_date:
                recent.append({
                    'id': all_papers['ids'][i],
                    'document': all_papers['documents'][i],
                    'metadata': metadata
                })

        return recent


class PatternUpdater:
    """Update pattern documentation based on new research."""

    def __init__(self, patterns_dir: str = "./docs/patterns"):
        """
        Initialize pattern updater.

        Args:
            patterns_dir: Directory containing pattern documentation
        """
        self.patterns_dir = patterns_dir

    def analyze_research_for_updates(self, paper: ResearchPaper) -> Dict:
        """
        Analyze research paper to determine if patterns need updating.

        Args:
            paper: ResearchPaper to analyze

        Returns:
            Dictionary with update recommendations
        """

        # Extract key insights from paper
        insights = self._extract_insights(paper)

        # Determine which patterns are affected
        affected_patterns = self._identify_affected_patterns(paper, insights)

        return {
            'paper': paper.arxiv_id,
            'title': paper.title,
            'insights': insights,
            'affected_patterns': affected_patterns,
            'recommended_actions': self._generate_recommendations(affected_patterns)
        }

    def _extract_insights(self, paper: ResearchPaper) -> List[str]:
        """Extract key insights from paper abstract."""

        # Placeholder - in production, use LLM to extract insights
        insights = []

        # Simple keyword-based extraction
        if 'improve' in paper.abstract.lower():
            insights.append("Performance improvement technique")

        if 'reduce' in paper.abstract.lower():
            insights.append("Error reduction approach")

        if 'novel' in paper.abstract.lower() or 'new' in paper.abstract.lower():
            insights.append("Novel approach or architecture")

        return insights

    def _identify_affected_patterns(self, paper: ResearchPaper, insights: List[str]) -> List[str]:
        """Identify which patterns might be affected by this research."""

        affected = []

        # Map keywords to patterns
        pattern_keywords = {
            'basic-rag.md': ['retrieval', 'generation', 'baseline'],
            'contextual-retrieval.md': ['context', 'chunk', 'embedding'],
            'hyde-rag.md': ['hypothesis', 'hypothetical'],
            'raptor-rag.md': ['hierarchical', 'tree', 'clustering'],
            'query-routing.md': ['routing', 'adaptive', 'selection'],
            'reranking-rag.md': ['rerank', 'cross-encoder', 'scoring']
        }

        paper_text = (paper.title + ' ' + paper.abstract).lower()

        for pattern, keywords in pattern_keywords.items():
            if any(kw in paper_text for kw in keywords):
                affected.append(pattern)

        return affected

    def _generate_recommendations(self, affected_patterns: List[str]) -> List[str]:
        """Generate update recommendations."""

        recommendations = []

        for pattern in affected_patterns:
            recommendations.append(
                f"Review {pattern} for potential updates based on new research"
            )

        return recommendations


class ResearchMonitor:
    """Main research monitoring orchestrator."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize research monitor.

        Args:
            persist_directory: Directory for ChromaDB persistence
        """

        self.arxiv_client = ArxivClient()
        self.web_monitor = WebSourceMonitor()
        self.evaluator = ResearchQualityEvaluator()
        self.db_manager = ChromaDBManager(persist_directory)
        self.pattern_updater = PatternUpdater()

    def monitor_arxiv(
        self,
        topics: List[str] = None,
        days_back: int = 7,
        min_relevance: float = 0.5
    ) -> Dict:
        """
        Monitor arXiv for new papers.

        Args:
            topics: List of topics to search (default: RAG-related)
            days_back: How many days back to search
            min_relevance: Minimum relevance score to ingest

        Returns:
            Summary of monitoring run
        """

        if topics is None:
            topics = [
                "retrieval augmented generation",
                "RAG",
                "contextual retrieval",
                "medical NLP",
                "healthcare AI summarization",
                "clinical note generation",
                "long context window"
            ]

        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        all_papers = []
        ingested_count = 0

        print(f"\n{'='*80}")
        print(f"Research Monitor - arXiv Scan")
        print(f"Date Range: {start_date} to {datetime.now().strftime('%Y-%m-%d')}")
        print(f"{'='*80}\n")

        for topic in topics:
            papers = self.arxiv_client.search_papers(
                query=topic,
                max_results=20,
                start_date=start_date
            )

            # Evaluate and filter papers
            for paper in papers:
                score = self.evaluator.evaluate_paper(paper, topic)

                if score >= min_relevance:
                    all_papers.append(paper)
                    self.db_manager.ingest_paper(paper)
                    ingested_count += 1

                    # Analyze for pattern updates
                    update_analysis = self.pattern_updater.analyze_research_for_updates(paper)

                    if update_analysis['affected_patterns']:
                        print(f"\n⚠️  Pattern Update Recommended:")
                        print(f"   Paper: {paper.title[:60]}...")
                        print(f"   Affects: {', '.join(update_analysis['affected_patterns'])}")

            # Rate limiting
            time.sleep(3)

        # Generate summary
        summary = {
            'run_date': datetime.now().isoformat(),
            'topics_searched': topics,
            'papers_found': len(all_papers),
            'papers_ingested': ingested_count,
            'date_range': f"{start_date} to {datetime.now().strftime('%Y-%m-%d')}"
        }

        print(f"\n{'='*80}")
        print(f"Summary: Found {len(all_papers)} papers, ingested {ingested_count}")
        print(f"{'='*80}\n")

        return summary

    def monitor_web_sources(self) -> Dict:
        """Monitor web sources for updates."""

        print(f"\n{'='*80}")
        print(f"Research Monitor - Web Sources Scan")
        print(f"{'='*80}\n")

        results = {}

        for source_key in self.web_monitor.SOURCES.keys():
            results[source_key] = self.web_monitor.check_source(source_key)

        return results

    def run_full_monitoring(self) -> Dict:
        """Run complete monitoring cycle."""

        print("\n🔍 Starting Research Monitoring Cycle...\n")

        # Monitor arXiv
        arxiv_summary = self.monitor_arxiv()

        # Monitor web sources
        web_summary = self.monitor_web_sources()

        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'arxiv': arxiv_summary,
            'web_sources': web_summary
        }

        # Save report
        report_path = f"reports/research-monitor-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        os.makedirs('reports', exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✅ Monitoring complete. Report saved to: {report_path}\n")

        return report


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description="Research Monitor - Automated arXiv and research source monitoring"
    )

    parser.add_argument(
        '--mode',
        choices=['monitor', 'search', 'ingest'],
        default='monitor',
        help='Operation mode'
    )

    parser.add_argument(
        '--query',
        type=str,
        help='Search query (for search mode)'
    )

    parser.add_argument(
        '--arxiv-id',
        type=str,
        help='arXiv ID to ingest (for ingest mode)'
    )

    parser.add_argument(
        '--days-back',
        type=int,
        default=7,
        help='Days to look back for papers (default: 7)'
    )

    args = parser.parse_args()

    monitor = ResearchMonitor()

    if args.mode == 'monitor':
        # Run full monitoring cycle
        monitor.run_full_monitoring()

    elif args.mode == 'search':
        if not args.query:
            print("Error: --query required for search mode")
            sys.exit(1)

        # Search ChromaDB
        results = monitor.db_manager.search_papers(args.query)

        print(f"\nSearch Results for: {args.query}")
        print(f"{'='*80}")

        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"\n{i+1}. {metadata['title']}")
            print(f"   arXiv: {metadata['arxiv_id']}")
            print(f"   Date: {metadata['publish_date']}")
            print(f"   URL: {metadata['url']}")

    elif args.mode == 'ingest':
        if not args.arxiv_id:
            print("Error: --arxiv-id required for ingest mode")
            sys.exit(1)

        # Fetch and ingest specific paper
        papers = monitor.arxiv_client.search_papers(query=args.arxiv_id, max_results=1)

        if papers:
            paper = papers[0]
            monitor.evaluator.evaluate_paper(paper, args.arxiv_id)
            monitor.db_manager.ingest_paper(paper)
            print(f"✅ Ingested paper: {paper.title}")
        else:
            print(f"❌ Paper not found: {args.arxiv_id}")


if __name__ == '__main__':
    main()
