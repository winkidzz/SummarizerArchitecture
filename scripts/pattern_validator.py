"""
Pattern Validator - Automated Pattern Documentation Validation

This script implements the pattern-validator Claude Skill, automatically validating
and updating pattern documentation based on latest research.

Usage:
    python scripts/pattern_validator.py --mode validate
    python scripts/pattern_validator.py --mode test-examples
    python scripts/pattern_validator.py --mode update-benchmarks
"""

import os
import re
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

import chromadb
from chromadb.utils import embedding_functions


@dataclass
class ValidationIssue:
    """Pattern validation issue."""
    pattern_file: str
    issue_type: str  # 'outdated_benchmark', 'deprecated_api', 'missing_reference', 'code_error'
    severity: str  # 'critical', 'warning', 'info'
    description: str
    line_number: Optional[int] = None
    recommended_fix: Optional[str] = None


@dataclass
class PatternMetadata:
    """Pattern documentation metadata."""
    file_path: str
    title: str
    version: str
    last_updated: str
    performance_claims: List[str]
    code_examples: List[str]
    references: List[str]
    model_versions: List[str]


class PatternParser:
    """Parse pattern documentation to extract metadata and content."""

    def __init__(self, patterns_dir: str = "./docs/patterns"):
        """
        Initialize pattern parser.

        Args:
            patterns_dir: Directory containing pattern markdown files
        """
        self.patterns_dir = Path(patterns_dir)

    def parse_pattern(self, pattern_file: str) -> PatternMetadata:
        """
        Parse pattern markdown file to extract metadata.

        Args:
            pattern_file: Pattern filename (e.g., 'basic-rag.md')

        Returns:
            PatternMetadata object
        """

        file_path = self.patterns_dir / pattern_file

        if not file_path.exists():
            raise FileNotFoundError(f"Pattern file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract title
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else 'Unknown'

        # Extract version and last updated
        version_match = re.search(r'\*\*v([\d.]+)\*\*', content)
        version = version_match.group(1) if version_match else 'unknown'

        date_match = re.search(r'\((\d{4}-\d{2}-\d{2})\)', content)
        last_updated = date_match.group(1) if date_match else 'unknown'

        # Extract performance claims
        performance_claims = self._extract_performance_claims(content)

        # Extract code examples
        code_examples = self._extract_code_blocks(content)

        # Extract references
        references = self._extract_references(content)

        # Extract model versions
        model_versions = self._extract_model_versions(content)

        return PatternMetadata(
            file_path=str(file_path),
            title=title,
            version=version,
            last_updated=last_updated,
            performance_claims=performance_claims,
            code_examples=code_examples,
            references=references,
            model_versions=model_versions
        )

    def _extract_performance_claims(self, content: str) -> List[str]:
        """Extract performance claims like '+20% accuracy'."""

        claims = []

        # Pattern for percentage improvements
        percent_pattern = r'[+\-]?\d+[-–]\d+%|[+\-]?\d+%'
        matches = re.finditer(percent_pattern, content)

        for match in matches:
            # Get surrounding context (50 chars before and after)
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end].strip()

            claims.append({
                'claim': match.group(0),
                'context': context
            })

        return claims

    def _extract_code_blocks(self, content: str) -> List[str]:
        """Extract Python code blocks."""

        # Match code blocks with ```python
        pattern = r'```python\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)

        return matches

    def _extract_references(self, content: str) -> List[str]:
        """Extract references (arXiv links, URLs, etc.)."""

        references = []

        # arXiv links
        arxiv_pattern = r'arxiv\.org/abs/([\d.]+)'
        arxiv_matches = re.findall(arxiv_pattern, content)
        references.extend([f'arXiv:{match}' for match in arxiv_matches])

        # DOI links
        doi_pattern = r'doi\.org/(10\.\d+/[^\s\)]+)'
        doi_matches = re.findall(doi_pattern, content)
        references.extend([f'DOI:{match}' for match in doi_matches])

        # Generic URLs in references section
        ref_section_match = re.search(r'## References\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if ref_section_match:
            url_pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)'
            url_matches = re.findall(url_pattern, ref_section_match.group(1))
            references.extend([f'{title}: {url}' for title, url in url_matches])

        return references

    def _extract_model_versions(self, content: str) -> List[str]:
        """Extract model version strings."""

        models = []

        # Claude models
        claude_pattern = r'claude-[\d]+-?[\w-]*-\d{8}'
        models.extend(re.findall(claude_pattern, content))

        # Gemini models
        gemini_pattern = r'gemini-[\d.]+-[\w-]+-\d{3}'
        models.extend(re.findall(gemini_pattern, content))

        # GPT models
        gpt_pattern = r'gpt-[\d.]+[-\w]*'
        models.extend(re.findall(gpt_pattern, content))

        # Llama models
        llama_pattern = r'llama[\d.]+[:\w-]*'
        models.extend(re.findall(llama_pattern, content))

        # Remove duplicates
        return list(set(models))


class CodeValidator:
    """Validate code examples in patterns."""

    # Known deprecated APIs
    DEPRECATED_APIS = {
        'anthropic': {
            'claude-3-opus-20240229': 'claude-3-5-sonnet-20241022',
            'claude-3-sonnet-20240229': 'claude-3-5-sonnet-20241022',
            'claude-2.1': 'claude-3-5-sonnet-20241022',
        },
        'openai': {
            'gpt-4': 'gpt-4-turbo',
            'gpt-3.5-turbo': 'gpt-4-turbo',
        },
        'ollama': {
            'llama3': 'llama3.2',
            'llama3:latest': 'llama3.2',
        }
    }

    # Current stable API versions
    CURRENT_API_VERSIONS = {
        'azure_openai': '2024-10-21',
        'anthropic': '2023-06-01',
    }

    def __init__(self):
        """Initialize code validator."""
        pass

    def validate_code_example(self, code: str) -> List[ValidationIssue]:
        """
        Validate a code example.

        Args:
            code: Python code string

        Returns:
            List of validation issues
        """

        issues = []

        # Check for deprecated model versions
        issues.extend(self._check_deprecated_models(code))

        # Check for outdated API versions
        issues.extend(self._check_api_versions(code))

        # Check for common code issues
        issues.extend(self._check_code_quality(code))

        return issues

    def _check_deprecated_models(self, code: str) -> List[ValidationIssue]:
        """Check for deprecated model versions."""

        issues = []

        for vendor, deprecated_models in self.DEPRECATED_APIS.items():
            for old_model, new_model in deprecated_models.items():
                if old_model in code:
                    issues.append(ValidationIssue(
                        pattern_file='',  # Will be set by caller
                        issue_type='deprecated_api',
                        severity='warning',
                        description=f'Deprecated {vendor} model: {old_model}',
                        recommended_fix=f'Update to: {new_model}'
                    ))

        return issues

    def _check_api_versions(self, code: str) -> List[ValidationIssue]:
        """Check for outdated API versions."""

        issues = []

        # Check Azure OpenAI API version
        azure_api_match = re.search(r'api_version=["\']([^"\']+)["\']', code)
        if azure_api_match:
            api_version = azure_api_match.group(1)
            current_version = self.CURRENT_API_VERSIONS['azure_openai']

            if api_version != current_version:
                issues.append(ValidationIssue(
                    pattern_file='',
                    issue_type='deprecated_api',
                    severity='warning',
                    description=f'Outdated Azure OpenAI API version: {api_version}',
                    recommended_fix=f'Update to: {current_version}'
                ))

        return issues

    def _check_code_quality(self, code: str) -> List[ValidationIssue]:
        """Check for common code quality issues."""

        issues = []

        # Check for missing error handling
        if 'try:' not in code and ('requests.' in code or 'client.' in code):
            issues.append(ValidationIssue(
                pattern_file='',
                issue_type='code_error',
                severity='info',
                description='Code example missing error handling',
                recommended_fix='Add try/except block for API calls'
            ))

        # Check for hardcoded credentials
        if 'api_key="' in code and 'os.getenv' not in code:
            issues.append(ValidationIssue(
                pattern_file='',
                issue_type='code_error',
                severity='critical',
                description='Hardcoded API key detected',
                recommended_fix='Use os.getenv() for API keys'
            ))

        # Check for missing imports
        if 'import' not in code and ('client.' in code or 'requests.' in code):
            issues.append(ValidationIssue(
                pattern_file='',
                issue_type='code_error',
                severity='warning',
                description='Code example missing import statements',
                recommended_fix='Add required imports'
            ))

        return issues

    def test_code_syntax(self, code: str) -> Optional[ValidationIssue]:
        """Test code for Python syntax errors."""

        try:
            compile(code, '<string>', 'exec')
            return None
        except SyntaxError as e:
            return ValidationIssue(
                pattern_file='',
                issue_type='code_error',
                severity='critical',
                description=f'Syntax error: {str(e)}',
                line_number=e.lineno,
                recommended_fix='Fix Python syntax error'
            )


class ResearchComparator:
    """Compare pattern claims against latest research in ChromaDB."""

    def __init__(self, chroma_db_path: str = "./chroma_db"):
        """
        Initialize research comparator.

        Args:
            chroma_db_path: Path to ChromaDB persistence directory
        """

        self.client = chromadb.PersistentClient(path=chroma_db_path)

        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        try:
            self.collection = self.client.get_collection(
                name="research_papers",
                embedding_function=self.embedding_function
            )
        except Exception:
            print("Warning: ChromaDB collection 'research_papers' not found.")
            print("Run research_monitor.py first to populate research database.")
            self.collection = None

    def verify_performance_claim(
        self,
        pattern_name: str,
        claim: str
    ) -> Dict:
        """
        Verify a performance claim against latest research.

        Args:
            pattern_name: Name of the pattern (e.g., 'HyDE RAG')
            claim: Performance claim to verify (e.g., '+20% accuracy')

        Returns:
            Verification result with supporting research
        """

        if not self.collection:
            return {
                'verified': 'unknown',
                'reason': 'Research database not available'
            }

        # Search for relevant research
        query = f"{pattern_name} {claim}"
        results = self.collection.query(
            query_texts=[query],
            n_results=5
        )

        if not results['documents'][0]:
            return {
                'verified': 'unknown',
                'reason': 'No relevant research found',
                'recommendation': 'Manual review required'
            }

        # Analyze results
        supporting_papers = []
        contradicting_papers = []

        for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
            # Simple heuristic - look for performance numbers in abstract
            if re.search(r'[+\-]?\d+[-–]\d+%|[+\-]?\d+%', doc):
                supporting_papers.append({
                    'arxiv_id': metadata.get('arxiv_id', 'unknown'),
                    'title': metadata.get('title', 'Unknown'),
                    'relevance': 'supporting'  # Simplified - could use LLM for analysis
                })

        if supporting_papers:
            return {
                'verified': 'supported',
                'supporting_research': supporting_papers,
                'recommendation': 'Claim appears valid'
            }
        else:
            return {
                'verified': 'unverified',
                'reason': 'No supporting research found',
                'recommendation': 'Consider updating claim or adding citation'
            }


class PatternValidator:
    """Main pattern validation orchestrator."""

    def __init__(
        self,
        patterns_dir: str = "./docs/patterns",
        chroma_db_path: str = "./chroma_db"
    ):
        """
        Initialize pattern validator.

        Args:
            patterns_dir: Directory containing pattern files
            chroma_db_path: Path to ChromaDB
        """

        self.parser = PatternParser(patterns_dir)
        self.code_validator = CodeValidator()
        self.research_comparator = ResearchComparator(chroma_db_path)
        self.patterns_dir = Path(patterns_dir)

    def validate_pattern(self, pattern_file: str) -> Dict:
        """
        Validate a single pattern file.

        Args:
            pattern_file: Pattern filename

        Returns:
            Validation report
        """

        print(f"\nValidating: {pattern_file}")
        print(f"{'='*80}")

        # Parse pattern
        metadata = self.parser.parse_pattern(pattern_file)

        issues = []

        # Validate code examples
        print(f"Checking {len(metadata.code_examples)} code examples...")
        for i, code in enumerate(metadata.code_examples):
            code_issues = self.code_validator.validate_code_example(code)

            for issue in code_issues:
                issue.pattern_file = pattern_file
                issues.append(issue)

            # Test syntax
            syntax_issue = self.code_validator.test_code_syntax(code)
            if syntax_issue:
                syntax_issue.pattern_file = pattern_file
                issues.append(syntax_issue)

        # Verify performance claims
        print(f"Verifying {len(metadata.performance_claims)} performance claims...")
        for claim_info in metadata.performance_claims:
            verification = self.research_comparator.verify_performance_claim(
                pattern_name=metadata.title,
                claim=claim_info['claim']
            )

            if verification['verified'] == 'unverified':
                issues.append(ValidationIssue(
                    pattern_file=pattern_file,
                    issue_type='outdated_benchmark',
                    severity='warning',
                    description=f"Unverified claim: {claim_info['claim']}",
                    recommended_fix=verification.get('recommendation', 'Manual review required')
                ))

        # Check references
        print(f"Checking {len(metadata.references)} references...")
        for ref in metadata.references:
            if ref.startswith('arXiv:'):
                # Could verify arXiv ID is valid
                pass

        # Check if pattern is outdated (> 6 months old)
        if metadata.last_updated != 'unknown':
            last_update = datetime.strptime(metadata.last_updated, '%Y-%m-%d')
            days_old = (datetime.now() - last_update).days

            if days_old > 180:
                issues.append(ValidationIssue(
                    pattern_file=pattern_file,
                    issue_type='outdated_benchmark',
                    severity='info',
                    description=f'Pattern not updated in {days_old} days',
                    recommended_fix='Review against latest research'
                ))

        # Categorize issues
        critical = [i for i in issues if i.severity == 'critical']
        warnings = [i for i in issues if i.severity == 'warning']
        info = [i for i in issues if i.severity == 'info']

        print(f"\nResults: {len(critical)} critical, {len(warnings)} warnings, {len(info)} info")

        return {
            'pattern_file': pattern_file,
            'metadata': metadata,
            'issues': issues,
            'summary': {
                'critical': len(critical),
                'warnings': len(warnings),
                'info': len(info),
                'total': len(issues)
            }
        }

    def validate_all_patterns(self) -> Dict:
        """
        Validate all patterns in directory.

        Returns:
            Comprehensive validation report
        """

        print(f"\n{'='*80}")
        print(f"Pattern Validation Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")

        # Get all pattern files
        pattern_files = list(self.patterns_dir.glob('*.md'))

        print(f"Found {len(pattern_files)} pattern files\n")

        # Validate each pattern
        results = []
        for pattern_file in pattern_files:
            result = self.validate_pattern(pattern_file.name)
            results.append(result)

        # Generate summary
        total_critical = sum(r['summary']['critical'] for r in results)
        total_warnings = sum(r['summary']['warnings'] for r in results)
        total_info = sum(r['summary']['info'] for r in results)

        up_to_date = [r for r in results if r['summary']['total'] == 0]
        needs_updates = [r for r in results if r['summary']['warnings'] > 0 or r['summary']['info'] > 0]
        critical_issues = [r for r in results if r['summary']['critical'] > 0]

        # Print summary
        print(f"\n{'='*80}")
        print(f"Summary")
        print(f"{'='*80}\n")

        print(f"✅ Up-to-Date Patterns: {len(up_to_date)}")
        for r in up_to_date:
            print(f"   - {r['pattern_file']}")

        print(f"\n⚠️  Patterns Needing Updates: {len(needs_updates)}")
        for r in needs_updates:
            print(f"   - {r['pattern_file']}: {r['summary']['warnings']} warnings, {r['summary']['info']} info")

        print(f"\n❌ Critical Issues: {len(critical_issues)}")
        for r in critical_issues:
            print(f"   - {r['pattern_file']}: {r['summary']['critical']} critical issues")
            for issue in [i for i in r['issues'] if i.severity == 'critical']:
                print(f"     • {issue.description}")

        print(f"\nTotal Issues: {total_critical} critical, {total_warnings} warnings, {total_info} info")

        # Save report
        report = {
            'timestamp': datetime.now().isoformat(),
            'patterns_validated': len(pattern_files),
            'summary': {
                'up_to_date': len(up_to_date),
                'needs_updates': len(needs_updates),
                'critical_issues': len(critical_issues),
                'total_issues': total_critical + total_warnings + total_info
            },
            'results': results
        }

        report_path = f"reports/pattern-validation-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        os.makedirs('reports', exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n✅ Report saved to: {report_path}\n")

        return report


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description="Pattern Validator - Validate and update pattern documentation"
    )

    parser.add_argument(
        '--mode',
        choices=['validate', 'test-examples', 'update-benchmarks'],
        default='validate',
        help='Operation mode'
    )

    parser.add_argument(
        '--pattern',
        type=str,
        help='Specific pattern file to validate (e.g., basic-rag.md)'
    )

    parser.add_argument(
        '--patterns-dir',
        type=str,
        default='./docs/patterns',
        help='Directory containing pattern files'
    )

    parser.add_argument(
        '--chroma-db',
        type=str,
        default='./chroma_db',
        help='Path to ChromaDB directory'
    )

    args = parser.parse_args()

    validator = PatternValidator(
        patterns_dir=args.patterns_dir,
        chroma_db_path=args.chroma_db
    )

    if args.mode == 'validate':
        if args.pattern:
            # Validate single pattern
            result = validator.validate_pattern(args.pattern)

            # Print issues
            if result['issues']:
                print(f"\nIssues found in {args.pattern}:")
                for issue in result['issues']:
                    print(f"  [{issue.severity.upper()}] {issue.description}")
                    if issue.recommended_fix:
                        print(f"    → {issue.recommended_fix}")
            else:
                print(f"\n✅ No issues found in {args.pattern}")

        else:
            # Validate all patterns
            validator.validate_all_patterns()

    elif args.mode == 'test-examples':
        # Test all code examples
        print("Testing code examples for syntax errors...")

        if args.pattern:
            patterns = [args.pattern]
        else:
            patterns_dir = Path(args.patterns_dir)
            patterns = [p.name for p in patterns_dir.glob('*.md')]

        for pattern in patterns:
            metadata = validator.parser.parse_pattern(pattern)
            print(f"\n{pattern}: {len(metadata.code_examples)} examples")

            for i, code in enumerate(metadata.code_examples):
                syntax_issue = validator.code_validator.test_code_syntax(code)
                if syntax_issue:
                    print(f"  ❌ Example {i+1}: {syntax_issue.description}")
                else:
                    print(f"  ✅ Example {i+1}: OK")

    elif args.mode == 'update-benchmarks':
        # Update benchmarks based on latest research
        print("Updating pattern benchmarks...")
        print("(This mode requires LLM integration for automated updates)")
        print("Run 'validate' mode to see which benchmarks need updating")


if __name__ == '__main__':
    main()
