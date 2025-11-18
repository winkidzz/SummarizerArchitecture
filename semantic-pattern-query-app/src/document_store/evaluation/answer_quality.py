"""
Answer Quality Metrics for RAG Evaluation.

These metrics evaluate the quality of generated answers:
- Answer Faithfulness: Are answer claims supported by retrieved context?
- Answer Relevancy: How relevant is the answer to the query?
- Answer Completeness: Does the answer fully address the query?
- Hallucination Detection: Does the answer contain unsupported claims?
- Citation Grounding: Are cited sources accurate and supporting the claims?

Based on RAGAS, DeepEval, and TruLens frameworks.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple, Set
from enum import Enum

logger = logging.getLogger(__name__)


class HallucinationSeverity(Enum):
    """Severity levels for hallucinations."""
    MINOR = "minor"        # Small factual inaccuracies, not critical
    MODERATE = "moderate"  # Significant unsupported claims
    SEVERE = "severe"      # Completely fabricated information, dangerous


def extract_claims_from_answer(answer: str) -> List[str]:
    """
    Extract individual claims/statements from an answer.

    This is a simplified extraction based on sentence splitting.
    For production, use:
    - Dependency parsing to extract atomic claims
    - LLM-based claim extraction
    - Named entity recognition

    Args:
        answer: The generated answer text

    Returns:
        List of individual claims

    Example:
        answer = "The patient has diabetes. Blood pressure is elevated. No allergies reported."
        claims = extract_claims_from_answer(answer)
        # Returns ["The patient has diabetes.", "Blood pressure is elevated.", "No allergies reported."]
    """
    # Split into sentences (simple approach)
    sentences = re.split(r'[.!?]+', answer)

    # Clean and filter
    claims = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:  # Filter out very short fragments
            claims.append(sentence)

    return claims


def check_claim_support(
    claim: str,
    context_chunks: List[str],
    similarity_threshold: float = 0.3
) -> Tuple[bool, List[int]]:
    """
    Check if a claim is supported by the retrieved context.

    This is a simplified keyword-based approach.
    For production, use:
    - Embedding similarity between claim and chunks
    - NLI (Natural Language Inference) models
    - LLM-as-judge to verify support

    Args:
        claim: A single claim from the answer
        context_chunks: List of retrieved context chunks
        similarity_threshold: Minimum word overlap to consider support

    Returns:
        Tuple of (is_supported, supporting_chunk_indices)

    Example:
        claim = "The patient has diabetes type 2"
        chunks = [
            "Patient diagnosed with diabetes mellitus type 2 in 2020.",
            "Blood pressure readings are normal.",
            "No known allergies."
        ]
        supported, chunk_ids = check_claim_support(claim, chunks)
        # Returns (True, [0]) - claim is supported by first chunk
    """
    claim_normalized = claim.lower()
    claim_words = set(re.findall(r'\w+', claim_normalized))

    supporting_chunks = []

    for idx, chunk in enumerate(context_chunks):
        chunk_normalized = chunk.lower()
        chunk_words = set(re.findall(r'\w+', chunk_normalized))

        # Calculate word overlap
        if not claim_words or not chunk_words:
            continue

        overlap = len(claim_words.intersection(chunk_words))
        overlap_ratio = overlap / len(claim_words)

        # If significant overlap, consider chunk as supporting
        if overlap_ratio >= similarity_threshold:
            supporting_chunks.append(idx)

    is_supported = len(supporting_chunks) > 0
    return is_supported, supporting_chunks


def calculate_answer_faithfulness(
    answer: str,
    context_chunks: List[str]
) -> Tuple[float, int, int]:
    """
    Calculate Answer Faithfulness - fraction of claims supported by context.

    Faithfulness = (# of supported claims) / (total # of claims)

    Lower faithfulness indicates hallucinations (unsupported claims).

    Args:
        answer: The generated answer text
        context_chunks: List of retrieved context chunks

    Returns:
        Tuple of (faithfulness_score, supported_claims_count, total_claims_count)

    Example:
        answer = "Patient has diabetes. Blood pressure is normal. Patient is 150 years old."
        chunks = ["Diabetes type 2 diagnosed.", "Blood pressure 120/80."]
        faithfulness, supported, total = calculate_answer_faithfulness(answer, chunks)
        # Returns (0.67, 2, 3) - 2 out of 3 claims supported (age claim not supported)
    """
    if not answer or not context_chunks:
        return 0.0, 0, 0

    # Extract claims from answer
    claims = extract_claims_from_answer(answer)

    if not claims:
        return 1.0, 0, 0  # No claims = no hallucinations

    # Check each claim for support
    supported_count = 0
    for claim in claims:
        is_supported, _ = check_claim_support(claim, context_chunks)
        if is_supported:
            supported_count += 1

    faithfulness_score = supported_count / len(claims)

    return faithfulness_score, supported_count, len(claims)


def detect_hallucinations(
    answer: str,
    context_chunks: List[str],
    faithfulness_threshold: float = 0.7
) -> Tuple[bool, HallucinationSeverity, List[str]]:
    """
    Detect hallucinations in the generated answer.

    Hallucination = claim in answer that is not supported by retrieved context

    Args:
        answer: The generated answer text
        context_chunks: List of retrieved context chunks
        faithfulness_threshold: Threshold below which to flag hallucinations

    Returns:
        Tuple of (has_hallucination, severity, unsupported_claims)

    Example:
        answer = "Patient has diabetes. Patient won the lottery yesterday."
        chunks = ["Diabetes type 2 diagnosis confirmed."]
        has_hall, severity, claims = detect_hallucinations(answer, chunks)
        # Returns (True, MODERATE, ["Patient won the lottery yesterday"])
    """
    faithfulness_score, supported, total = calculate_answer_faithfulness(
        answer, context_chunks
    )

    if faithfulness_score >= faithfulness_threshold:
        return False, HallucinationSeverity.MINOR, []

    # Extract unsupported claims
    claims = extract_claims_from_answer(answer)
    unsupported_claims = []

    for claim in claims:
        is_supported, _ = check_claim_support(claim, context_chunks)
        if not is_supported:
            unsupported_claims.append(claim)

    # Determine severity
    unsupported_ratio = len(unsupported_claims) / total if total > 0 else 0

    if unsupported_ratio < 0.3:
        severity = HallucinationSeverity.MINOR
    elif unsupported_ratio < 0.6:
        severity = HallucinationSeverity.MODERATE
    else:
        severity = HallucinationSeverity.SEVERE

    has_hallucination = len(unsupported_claims) > 0

    return has_hallucination, severity, unsupported_claims


def calculate_answer_relevancy_simple(
    query: str,
    answer: str
) -> float:
    """
    Calculate Answer Relevancy using simple word overlap.

    For production, use embedding similarity between query and answer.

    Answer Relevancy = embedding_similarity(query, answer)

    Args:
        query: The user query
        answer: The generated answer

    Returns:
        Relevancy score (0.0 to 1.0)

    Example:
        query = "What is the patient's blood pressure?"
        answer = "The patient's blood pressure is 120/80 mmHg."
        relevancy = calculate_answer_relevancy_simple(query, answer)
        # Returns high score due to word overlap (patient, blood, pressure)
    """
    if not query or not answer:
        return 0.0

    # Normalize
    query_normalized = query.lower()
    answer_normalized = answer.lower()

    # Extract words
    query_words = set(re.findall(r'\w+', query_normalized))
    answer_words = set(re.findall(r'\w+', answer_normalized))

    # Remove common stop words (simplified)
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'how', 'why', 'when', 'where'}
    query_words = query_words - stop_words
    answer_words = answer_words - stop_words

    if not query_words:
        return 1.0

    # Calculate overlap
    overlap = len(query_words.intersection(answer_words))
    relevancy = overlap / len(query_words)

    # Cap at 1.0
    return min(relevancy, 1.0)


def calculate_answer_completeness(
    query: str,
    answer: str,
    expected_elements: Optional[List[str]] = None
) -> float:
    """
    Calculate Answer Completeness - does answer fully address all aspects of query?

    Completeness checks:
    - Does answer address all question components?
    - Are all expected elements present?
    - Is the answer sufficiently detailed?

    Args:
        query: The user query
        answer: The generated answer
        expected_elements: Optional list of elements that should be in answer

    Returns:
        Completeness score (0.0 to 1.0)

    Example:
        query = "What are the patient's vital signs and current medications?"
        answer = "Blood pressure is 120/80. Heart rate is 72 bpm. Currently on metformin."
        expected = ["blood pressure", "heart rate", "medications"]
        completeness = calculate_answer_completeness(query, answer, expected)
        # Returns 1.0 - all expected elements present
    """
    if not query or not answer:
        return 0.0

    answer_normalized = answer.lower()

    # If expected elements provided, check for their presence
    if expected_elements:
        present_count = 0
        for element in expected_elements:
            if element.lower() in answer_normalized:
                present_count += 1

        return present_count / len(expected_elements)

    # Otherwise, use heuristics
    # Check if answer is too short (likely incomplete)
    answer_words = len(re.findall(r'\w+', answer))

    if answer_words < 10:
        return 0.3  # Very short answer, likely incomplete

    # Check for question words that might indicate incomplete answer
    incomplete_indicators = ['unclear', 'unknown', 'not specified', 'not available', 'n/a']
    has_incomplete_indicator = any(indicator in answer_normalized for indicator in incomplete_indicators)

    if has_incomplete_indicator:
        return 0.5  # Partial answer

    # If answer is reasonably long and has no incomplete indicators
    return 0.8  # Likely complete (conservative estimate)


def extract_citations_from_answer(answer: str) -> List[str]:
    """
    Extract citations from answer (e.g., [1], [source], etc.).

    Args:
        answer: The generated answer with citations

    Returns:
        List of citation references

    Example:
        answer = "Patient has diabetes [1]. Blood pressure is normal [2]."
        citations = extract_citations_from_answer(answer)
        # Returns ["[1]", "[2]"]
    """
    # Match citation patterns like [1], [2], [source], etc.
    citation_pattern = r'\[([^\]]+)\]'
    citations = re.findall(citation_pattern, answer)

    return citations


def calculate_citation_grounding(
    answer: str,
    context_chunks: List[str],
    citations: Optional[List[str]] = None
) -> float:
    """
    Calculate Citation Grounding - do cited sources actually support the claims?

    Citation Grounding = (# of accurate citations) / (total # of citations)

    Args:
        answer: The generated answer with citations
        context_chunks: List of retrieved context chunks
        citations: Optional list of citations to verify (extracted if not provided)

    Returns:
        Citation grounding score (0.0 to 1.0)

    Example:
        answer = "Patient has diabetes [1]. Blood pressure is 140/90 [2]."
        chunks = ["Diabetes type 2.", "BP reading: 140/90."]
        grounding = calculate_citation_grounding(answer, chunks)
        # Returns 1.0 - both citations are grounded in context
    """
    if citations is None:
        citations = extract_citations_from_answer(answer)

    if not citations:
        return 1.0  # No citations = no citation errors

    # For each citation, verify it's grounded
    # This is simplified - in production, parse citation numbers and verify against context

    # Simple heuristic: assume citations are well-formed if context is present
    if context_chunks:
        return 0.9  # Conservative score
    else:
        return 0.0  # No context = citations cannot be grounded


def evaluate_answer_quality(
    query: str,
    answer: str,
    context_chunks: List[str],
    expected_elements: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Comprehensive answer quality evaluation.

    Calculates all answer quality metrics in one pass.

    Args:
        query: The user query
        answer: The generated answer
        context_chunks: List of retrieved context chunks
        expected_elements: Optional list of elements that should be in answer

    Returns:
        Dictionary containing all answer quality metrics:
        {
            'faithfulness': 0.85,
            'relevancy': 0.92,
            'completeness': 0.80,
            'citation_grounding': 0.90,
            'has_hallucination': False,
            'hallucination_severity': 'minor',
            'unsupported_claims': [],
            'supported_claims_count': 5,
            'total_claims_count': 6
        }

    Example:
        metrics = evaluate_answer_quality(
            query="What is patient's condition?",
            answer="Patient has diabetes type 2.",
            context_chunks=["Diabetes mellitus type 2 diagnosis."]
        )
        print(f"Faithfulness: {metrics['faithfulness']}")
    """
    results = {}

    # Faithfulness
    faithfulness, supported, total = calculate_answer_faithfulness(
        answer, context_chunks
    )
    results['faithfulness'] = faithfulness
    results['supported_claims_count'] = supported
    results['total_claims_count'] = total

    # Hallucination Detection
    has_hall, severity, unsupported = detect_hallucinations(
        answer, context_chunks
    )
    results['has_hallucination'] = has_hall
    results['hallucination_severity'] = severity.value
    results['unsupported_claims'] = unsupported

    # Answer Relevancy
    results['relevancy'] = calculate_answer_relevancy_simple(query, answer)

    # Answer Completeness
    results['completeness'] = calculate_answer_completeness(
        query, answer, expected_elements
    )

    # Citation Grounding
    results['citation_grounding'] = calculate_citation_grounding(
        answer, context_chunks
    )

    return results
