"""
Context Quality Metrics for RAG Evaluation.

These metrics evaluate the quality of retrieved context before answer generation:
- Context Precision: How relevant is the retrieved context to the query?
- Context Recall: Does retrieved context contain all necessary information?
- Context Relevancy: Overall relevance of context chunks
- Context Utilization: How much of retrieved context is actually used in answer?

Based on RAGAS and DeepEval frameworks.
"""

import logging
from typing import List, Dict, Any, Optional, Set
import re

logger = logging.getLogger(__name__)


def calculate_context_precision(
    retrieved_chunks: List[str],
    relevant_chunk_indices: Set[int]
) -> float:
    """
    Calculate Context Precision - fraction of retrieved chunks that are relevant.

    Context Precision = (# of relevant chunks) / (total # of retrieved chunks)

    Args:
        retrieved_chunks: List of retrieved context chunks
        relevant_chunk_indices: Set of indices (0-based) of chunks that are relevant

    Returns:
        Context precision score (0.0 to 1.0)

    Example:
        chunks = ["chunk1", "chunk2", "chunk3", "chunk4", "chunk5"]
        relevant_indices = {0, 2, 4}  # chunks 1, 3, 5 are relevant
        precision = calculate_context_precision(chunks, relevant_indices)
        # Returns 3/5 = 0.6
    """
    if not retrieved_chunks:
        return 0.0

    relevant_count = len(relevant_chunk_indices)
    total_count = len(retrieved_chunks)

    return relevant_count / total_count


def calculate_context_recall(
    retrieved_chunks: List[str],
    ground_truth_facts: Set[str],
    extracted_facts_from_chunks: Set[str]
) -> float:
    """
    Calculate Context Recall - whether retrieved context covers all necessary facts.

    Context Recall = (# of ground truth facts in retrieved context) / (total # of ground truth facts)

    This requires extracting facts from retrieved chunks and comparing to ground truth.

    Args:
        retrieved_chunks: List of retrieved context chunks
        ground_truth_facts: Set of facts that should be covered
        extracted_facts_from_chunks: Set of facts extracted from retrieved chunks

    Returns:
        Context recall score (0.0 to 1.0)

    Example:
        ground_truth = {"fact1", "fact2", "fact3"}
        extracted = {"fact1", "fact2", "fact4"}  # missing fact3, has irrelevant fact4
        recall = calculate_context_recall(chunks, ground_truth, extracted)
        # Returns 2/3 = 0.667 (found 2 out of 3 required facts)
    """
    if not ground_truth_facts:
        return 1.0  # If no facts required, perfect recall

    if not retrieved_chunks or not extracted_facts_from_chunks:
        return 0.0

    # Count how many ground truth facts are covered
    covered_facts = ground_truth_facts.intersection(extracted_facts_from_chunks)

    return len(covered_facts) / len(ground_truth_facts)


def calculate_context_relevancy(
    query: str,
    retrieved_chunks: List[str],
    chunk_relevance_scores: List[float]
) -> float:
    """
    Calculate Context Relevancy - average relevance of all chunks to the query.

    Context Relevancy = average(relevance_score for each chunk)

    Relevance scores typically come from:
    - Embedding similarity between query and chunk
    - LLM-based relevance judgment
    - BM25 scores

    Args:
        query: The user query
        retrieved_chunks: List of retrieved context chunks
        chunk_relevance_scores: List of relevance scores (0.0 to 1.0) for each chunk

    Returns:
        Average context relevancy score (0.0 to 1.0)

    Example:
        chunks = ["chunk1", "chunk2", "chunk3"]
        scores = [0.9, 0.7, 0.5]
        relevancy = calculate_context_relevancy(query, chunks, scores)
        # Returns (0.9 + 0.7 + 0.5) / 3 = 0.7
    """
    if not retrieved_chunks or not chunk_relevance_scores:
        return 0.0

    if len(retrieved_chunks) != len(chunk_relevance_scores):
        logger.warning(
            f"Mismatch: {len(retrieved_chunks)} chunks but {len(chunk_relevance_scores)} scores"
        )
        return 0.0

    return sum(chunk_relevance_scores) / len(chunk_relevance_scores)


def calculate_context_utilization(
    retrieved_chunks: List[str],
    generated_answer: str,
    chunks_used_in_answer: Set[int]
) -> float:
    """
    Calculate Context Utilization - fraction of retrieved context used in answer.

    Context Utilization = (# of chunks used in answer) / (total # of retrieved chunks)

    Lower utilization might indicate over-retrieval (retrieving too many irrelevant chunks).

    Args:
        retrieved_chunks: List of retrieved context chunks
        generated_answer: The generated answer text
        chunks_used_in_answer: Set of indices (0-based) of chunks actually used

    Returns:
        Context utilization score (0.0 to 1.0)

    Example:
        chunks = ["chunk1", "chunk2", "chunk3", "chunk4", "chunk5"]
        chunks_used = {0, 2, 4}  # Only chunks 1, 3, 5 were used
        utilization = calculate_context_utilization(chunks, answer, chunks_used)
        # Returns 3/5 = 0.6
    """
    if not retrieved_chunks:
        return 0.0

    used_count = len(chunks_used_in_answer)
    total_count = len(retrieved_chunks)

    return used_count / total_count


def estimate_chunk_usage_from_answer(
    retrieved_chunks: List[str],
    generated_answer: str,
    similarity_threshold: float = 0.3
) -> Set[int]:
    """
    Estimate which chunks were used in the answer based on text overlap.

    This is a simplified heuristic approach. For production, use:
    - Attention weights from the model
    - Citation tracking
    - Embedding similarity between chunks and answer sentences

    Args:
        retrieved_chunks: List of retrieved context chunks
        generated_answer: The generated answer text
        similarity_threshold: Minimum overlap ratio to consider chunk "used"

    Returns:
        Set of chunk indices that appear to be used in the answer

    Example:
        chunks = [
            "The patient has diabetes type 2.",
            "Blood pressure is 140/90.",
            "Patient is allergic to penicillin."
        ]
        answer = "The patient has diabetes and high blood pressure."
        used = estimate_chunk_usage_from_answer(chunks, answer)
        # Returns {0, 1} (chunks about diabetes and BP were used)
    """
    chunks_used = set()

    # Normalize answer for comparison
    answer_normalized = generated_answer.lower()
    answer_words = set(re.findall(r'\w+', answer_normalized))

    for idx, chunk in enumerate(retrieved_chunks):
        # Normalize chunk
        chunk_normalized = chunk.lower()
        chunk_words = set(re.findall(r'\w+', chunk_normalized))

        # Calculate word overlap
        if not chunk_words:
            continue

        overlap = len(answer_words.intersection(chunk_words))
        overlap_ratio = overlap / len(chunk_words)

        # If significant overlap, consider chunk as used
        if overlap_ratio >= similarity_threshold:
            chunks_used.add(idx)

    return chunks_used


def evaluate_context_quality(
    query: str,
    retrieved_chunks: List[str],
    generated_answer: str,
    chunk_relevance_scores: List[float],
    relevant_chunk_indices: Optional[Set[int]] = None,
    ground_truth_facts: Optional[Set[str]] = None,
    extracted_facts: Optional[Set[str]] = None,
    chunks_used_in_answer: Optional[Set[int]] = None
) -> Dict[str, float]:
    """
    Comprehensive context quality evaluation.

    Calculates all context quality metrics in one pass.

    Args:
        query: The user query
        retrieved_chunks: List of retrieved context chunks
        generated_answer: The generated answer text
        chunk_relevance_scores: Relevance scores for each chunk
        relevant_chunk_indices: Optional ground truth relevant chunk indices
        ground_truth_facts: Optional set of facts that should be covered
        extracted_facts: Optional set of facts extracted from chunks
        chunks_used_in_answer: Optional set of chunk indices used in answer
                               If not provided, will estimate from text overlap

    Returns:
        Dictionary containing all context quality metrics:
        {
            'context_precision': 0.75,
            'context_recall': 0.67,
            'context_relevancy': 0.82,
            'context_utilization': 0.60
        }

    Example:
        metrics = evaluate_context_quality(
            query="What is the patient's blood pressure?",
            retrieved_chunks=chunks,
            generated_answer=answer,
            chunk_relevance_scores=[0.9, 0.7, 0.5],
            relevant_chunk_indices={0, 1}
        )
        print(f"Context Precision: {metrics['context_precision']}")
    """
    results = {
        'context_precision': 0.0,
        'context_recall': 0.0,
        'context_relevancy': 0.0,
        'context_utilization': 0.0
    }

    # Context Precision (requires ground truth)
    if relevant_chunk_indices is not None:
        results['context_precision'] = calculate_context_precision(
            retrieved_chunks,
            relevant_chunk_indices
        )

    # Context Recall (requires ground truth facts)
    if ground_truth_facts is not None and extracted_facts is not None:
        results['context_recall'] = calculate_context_recall(
            retrieved_chunks,
            ground_truth_facts,
            extracted_facts
        )

    # Context Relevancy (always calculable if scores provided)
    if chunk_relevance_scores:
        results['context_relevancy'] = calculate_context_relevancy(
            query,
            retrieved_chunks,
            chunk_relevance_scores
        )

    # Context Utilization
    if chunks_used_in_answer is None:
        # Estimate from text overlap
        chunks_used_in_answer = estimate_chunk_usage_from_answer(
            retrieved_chunks,
            generated_answer
        )

    results['context_utilization'] = calculate_context_utilization(
        retrieved_chunks,
        generated_answer,
        chunks_used_in_answer
    )

    return results
