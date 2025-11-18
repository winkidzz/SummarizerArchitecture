"""
Classical Information Retrieval (IR) metrics for RAG system evaluation.

These metrics evaluate the quality of document retrieval, measuring how well the
system ranks and returns relevant documents for a given query.

All metrics require ground truth relevance judgments (which documents are actually
relevant for each query).
"""

import math
from typing import List, Dict, Set, Union


def calculate_precision_at_k(
    retrieved_doc_ids: List[str],
    relevant_doc_ids: Set[str],
    k: int
) -> float:
    """
    Calculate Precision@k - fraction of top-k retrieved docs that are relevant.

    Precision@k = (# of relevant docs in top-k) / k

    Args:
        retrieved_doc_ids: List of retrieved document IDs in ranked order
        relevant_doc_ids: Set of ground truth relevant document IDs
        k: Cutoff position (number of top results to consider)

    Returns:
        Precision@k score (0.0 to 1.0)

    Example:
        retrieved = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']
        relevant = {'doc1', 'doc3', 'doc6'}
        precision_at_3 = calculate_precision_at_k(retrieved, relevant, 3)
        # Returns 2/3 = 0.667 (doc1 and doc3 are relevant in top-3)
    """
    if k <= 0 or not retrieved_doc_ids:
        return 0.0

    top_k = retrieved_doc_ids[:k]
    relevant_in_top_k = sum(1 for doc_id in top_k if doc_id in relevant_doc_ids)

    return relevant_in_top_k / k


def calculate_recall_at_k(
    retrieved_doc_ids: List[str],
    relevant_doc_ids: Set[str],
    k: int
) -> float:
    """
    Calculate Recall@k - fraction of all relevant docs that appear in top-k.

    Recall@k = (# of relevant docs in top-k) / (total # of relevant docs)

    Args:
        retrieved_doc_ids: List of retrieved document IDs in ranked order
        relevant_doc_ids: Set of ground truth relevant document IDs
        k: Cutoff position (number of top results to consider)

    Returns:
        Recall@k score (0.0 to 1.0)

    Example:
        retrieved = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']
        relevant = {'doc1', 'doc3', 'doc6'}
        recall_at_3 = calculate_recall_at_k(retrieved, relevant, 3)
        # Returns 2/3 = 0.667 (found doc1, doc3 but missed doc6)
    """
    if not relevant_doc_ids or k <= 0 or not retrieved_doc_ids:
        return 0.0

    top_k = retrieved_doc_ids[:k]
    relevant_in_top_k = sum(1 for doc_id in top_k if doc_id in relevant_doc_ids)

    return relevant_in_top_k / len(relevant_doc_ids)


def calculate_hit_rate_at_k(
    retrieved_doc_ids: List[str],
    relevant_doc_ids: Set[str],
    k: int
) -> float:
    """
    Calculate Hit Rate@k - binary metric: 1 if ANY relevant doc in top-k, else 0.

    Hit Rate@k = 1 if at least one relevant doc in top-k, else 0

    Args:
        retrieved_doc_ids: List of retrieved document IDs in ranked order
        relevant_doc_ids: Set of ground truth relevant document IDs
        k: Cutoff position (number of top results to consider)

    Returns:
        Hit rate (0.0 or 1.0)

    Example:
        retrieved = ['doc1', 'doc2', 'doc3']
        relevant = {'doc3', 'doc6'}
        hit_rate_at_3 = calculate_hit_rate_at_k(retrieved, relevant, 3)
        # Returns 1.0 (doc3 is in top-3)
    """
    if k <= 0 or not retrieved_doc_ids or not relevant_doc_ids:
        return 0.0

    top_k = retrieved_doc_ids[:k]
    has_relevant = any(doc_id in relevant_doc_ids for doc_id in top_k)

    return 1.0 if has_relevant else 0.0


def calculate_mrr(
    retrieved_doc_ids: List[str],
    relevant_doc_ids: Set[str]
) -> float:
    """
    Calculate Mean Reciprocal Rank (MRR) - reciprocal of rank of first relevant doc.

    MRR = 1 / (position of first relevant document)

    Ranks are 1-indexed (first position = 1, not 0).
    Returns 0.0 if no relevant documents are found.

    Args:
        retrieved_doc_ids: List of retrieved document IDs in ranked order
        relevant_doc_ids: Set of ground truth relevant document IDs

    Returns:
        MRR score (0.0 to 1.0)

    Example:
        retrieved = ['doc1', 'doc2', 'doc3', 'doc4']
        relevant = {'doc3', 'doc6'}
        mrr = calculate_mrr(retrieved, relevant)
        # Returns 1/3 = 0.333 (first relevant doc is at position 3)
    """
    if not retrieved_doc_ids or not relevant_doc_ids:
        return 0.0

    for rank, doc_id in enumerate(retrieved_doc_ids, start=1):
        if doc_id in relevant_doc_ids:
            return 1.0 / rank

    return 0.0


def calculate_map(
    retrieved_doc_ids: List[str],
    relevant_doc_ids: Set[str]
) -> float:
    """
    Calculate Mean Average Precision (MAP) - mean of precision values at each
    relevant document position.

    MAP = (sum of Precision@k for each relevant doc position k) / (# relevant docs)

    Only considers positions where relevant documents appear.

    Args:
        retrieved_doc_ids: List of retrieved document IDs in ranked order
        relevant_doc_ids: Set of ground truth relevant document IDs

    Returns:
        MAP score (0.0 to 1.0)

    Example:
        retrieved = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']
        relevant = {'doc1', 'doc3', 'doc5'}
        # Relevant at positions 1, 3, 5
        # Precision@1 = 1/1, Precision@3 = 2/3, Precision@5 = 3/5
        # MAP = (1.0 + 0.667 + 0.6) / 3 = 0.756
    """
    if not relevant_doc_ids or not retrieved_doc_ids:
        return 0.0

    precision_sum = 0.0
    relevant_found = 0

    for rank, doc_id in enumerate(retrieved_doc_ids, start=1):
        if doc_id in relevant_doc_ids:
            relevant_found += 1
            precision_at_rank = relevant_found / rank
            precision_sum += precision_at_rank

    if relevant_found == 0:
        return 0.0

    return precision_sum / len(relevant_doc_ids)


def calculate_ndcg_at_k(
    retrieved_doc_ids: List[str],
    relevance_scores: Dict[str, float],
    k: int
) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain (NDCG@k).

    NDCG accounts for both relevance and position, with a logarithmic discount
    for lower positions. Normalized to 0-1 range by ideal DCG.

    DCG@k = sum_{i=1}^{k} (relevance_i / log2(i + 1))
    NDCG@k = DCG@k / IDCG@k

    Args:
        retrieved_doc_ids: List of retrieved document IDs in ranked order
        relevance_scores: Dict mapping doc_id to relevance score (0.0 to 1.0 or higher)
                         Higher scores = more relevant
        k: Cutoff position (number of top results to consider)

    Returns:
        NDCG@k score (0.0 to 1.0)

    Example:
        retrieved = ['doc1', 'doc2', 'doc3', 'doc4']
        relevance = {'doc1': 3, 'doc2': 0, 'doc3': 2, 'doc4': 1}
        ndcg_at_3 = calculate_ndcg_at_k(retrieved, relevance, 3)
        # DCG@3 = 3/log2(2) + 0/log2(3) + 2/log2(4) = 3.0 + 0 + 1.0 = 4.0
        # IDCG@3 = 3/log2(2) + 2/log2(3) + 1/log2(4) = 3.0 + 1.26 + 0.5 = 4.76
        # NDCG@3 = 4.0 / 4.76 = 0.840
    """
    if k <= 0 or not retrieved_doc_ids or not relevance_scores:
        return 0.0

    # Calculate DCG@k for retrieved ranking
    dcg = 0.0
    for i, doc_id in enumerate(retrieved_doc_ids[:k], start=1):
        relevance = relevance_scores.get(doc_id, 0.0)
        dcg += relevance / math.log2(i + 1)

    # Calculate ideal DCG@k (best possible ranking)
    # Sort all documents by relevance score (descending)
    all_docs_sorted = sorted(
        relevance_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    idcg = 0.0
    for i, (doc_id, relevance) in enumerate(all_docs_sorted[:k], start=1):
        idcg += relevance / math.log2(i + 1)

    if idcg == 0.0:
        return 0.0

    return dcg / idcg


def evaluate_retrieval_quality(
    retrieved_doc_ids: List[str],
    relevant_doc_ids: Set[str],
    relevance_scores: Dict[str, float] = None,
    k_values: List[int] = None
) -> Dict[str, Union[float, Dict[int, float]]]:
    """
    Comprehensive evaluation of retrieval quality using all IR metrics.

    Calculates all classical IR metrics in one pass for efficiency.

    Args:
        retrieved_doc_ids: List of retrieved document IDs in ranked order
        relevant_doc_ids: Set of ground truth relevant document IDs
        relevance_scores: Optional dict of graded relevance scores for NDCG
                         If not provided, NDCG will use binary relevance (0 or 1)
        k_values: List of k values to evaluate @k metrics (default: [1, 3, 5, 10])

    Returns:
        Dictionary containing all metrics:
        {
            'precision@k': {1: 0.5, 3: 0.67, 5: 0.6, 10: 0.5},
            'recall@k': {1: 0.25, 3: 0.5, 5: 0.75, 10: 1.0},
            'hit_rate@k': {1: 1.0, 3: 1.0, 5: 1.0, 10: 1.0},
            'ndcg@k': {1: 0.8, 3: 0.85, 5: 0.9, 10: 0.95},
            'mrr': 0.333,
            'map': 0.756
        }

    Example:
        retrieved = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']
        relevant = {'doc1', 'doc3', 'doc5'}
        scores = {'doc1': 3, 'doc2': 0, 'doc3': 2, 'doc4': 1, 'doc5': 1}

        metrics = evaluate_retrieval_quality(retrieved, relevant, scores)
        print(f"Precision@3: {metrics['precision@k'][3]}")
        print(f"NDCG@5: {metrics['ndcg@k'][5]}")
        print(f"MRR: {metrics['mrr']}")
    """
    if k_values is None:
        k_values = [1, 3, 5, 10]

    # If no graded relevance scores provided, use binary (0 or 1)
    if relevance_scores is None:
        relevance_scores = {doc_id: 1.0 for doc_id in relevant_doc_ids}

    results = {
        'precision@k': {},
        'recall@k': {},
        'hit_rate@k': {},
        'ndcg@k': {},
        'mrr': 0.0,
        'map': 0.0
    }

    # Calculate @k metrics for each k value
    for k in k_values:
        results['precision@k'][k] = calculate_precision_at_k(
            retrieved_doc_ids, relevant_doc_ids, k
        )
        results['recall@k'][k] = calculate_recall_at_k(
            retrieved_doc_ids, relevant_doc_ids, k
        )
        results['hit_rate@k'][k] = calculate_hit_rate_at_k(
            retrieved_doc_ids, relevant_doc_ids, k
        )
        results['ndcg@k'][k] = calculate_ndcg_at_k(
            retrieved_doc_ids, relevance_scores, k
        )

    # Calculate ranking metrics (don't depend on k)
    results['mrr'] = calculate_mrr(retrieved_doc_ids, relevant_doc_ids)
    results['map'] = calculate_map(retrieved_doc_ids, relevant_doc_ids)

    return results
