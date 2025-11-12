"""
Real Ragas integration with support for both Gemini and Ollama models.

Uses the official Ragas library (v0.3.9+) for RAG evaluation with proper LLM integration.
"""

import logging
import os
from typing import List, Dict, Any, Optional

try:
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )
    from datasets import Dataset
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False
    evaluate = None
    faithfulness = None
    answer_relevancy = None
    context_precision = None
    context_recall = None
    Dataset = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    ChatGoogleGenerativeAI = None
    GoogleGenerativeAIEmbeddings = None

logger = logging.getLogger(__name__)


class RagasRealEvaluator:
    """
    Real Ragas evaluator using official Ragas library.

    Supports both Gemini and Ollama models for evaluation.
    """

    def __init__(
        self,
        model: str = "gemini-2.0-flash-exp",
        llm_type: str = "auto",
        api_key: Optional[str] = None,
    ):
        """
        Initialize Real Ragas evaluator.

        Args:
            model: Model name (e.g., "gemini-2.0-flash-exp", "qwen3:14b")
            llm_type: "auto", "gemini", or "ollama"
            api_key: API key for Gemini (reads from GEMINI_API_KEY if not provided)
        """
        if not RAGAS_AVAILABLE:
            raise ImportError(
                "Ragas is not installed. Install with: pip install ragas"
            )

        self.model_name = model
        self.llm_type = llm_type

        # Auto-detect LLM type if needed
        if self.llm_type == "auto":
            if model.startswith("gemini"):
                self.llm_type = "gemini"
            else:
                self.llm_type = "ollama"

        # Initialize LLM and embeddings
        if self.llm_type == "gemini":
            if not GEMINI_AVAILABLE:
                raise ImportError(
                    "LangChain Google GenAI not available. "
                    "Install with: pip install langchain-google-genai"
                )

            self.api_key = api_key or os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")

            # Initialize Gemini LLM and embeddings
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=0.1,
            )
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=self.api_key,
            )

            logger.info(f"Initialized Real Ragas with Gemini: {model}")

        else:  # ollama
            raise NotImplementedError(
                "Real Ragas with Ollama not yet implemented. "
                "Use llm_type='gemini' or the custom OllamaEvaluator."
            )

    def evaluate_batch(
        self,
        queries: List[str],
        responses: List[str],
        contexts: List[List[str]],
        reference_answers: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate multiple test cases using Real Ragas.

        Args:
            queries: List of user queries
            responses: List of RAG system responses
            contexts: List of retrieved context lists
            reference_answers: Optional list of ground truth answers
            metrics: List of metric names to compute

        Returns:
            Dict with results and scores
        """
        if metrics is None:
            metrics = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]

        # Convert to Ragas dataset format
        dataset_dict = {
            "question": queries,
            "answer": responses,
            "contexts": contexts,
        }

        if reference_answers:
            dataset_dict["ground_truth"] = reference_answers

        dataset = Dataset.from_dict(dataset_dict)

        # Select metrics
        metric_objects = []
        for metric_name in metrics:
            if metric_name == "faithfulness" and faithfulness:
                metric_objects.append(faithfulness)
            elif metric_name == "answer_relevancy" and answer_relevancy:
                metric_objects.append(answer_relevancy)
            elif metric_name == "context_precision" and context_precision:
                if reference_answers:  # context_precision needs ground truth
                    metric_objects.append(context_precision)
            elif metric_name == "context_recall" and context_recall:
                if reference_answers:  # context_recall needs ground truth
                    metric_objects.append(context_recall)

        if not metric_objects:
            raise ValueError("No valid metrics selected")

        # Run evaluation
        logger.info(f"Running Real Ragas evaluation with {len(metric_objects)} metrics...")

        try:
            result = evaluate(
                dataset=dataset,
                metrics=metric_objects,
                llm=self.llm,
                embeddings=self.embeddings,
            )

            # Convert to our format
            results = {
                "results": [],
                "aggregate": {},
                "num_cases": len(queries),
            }

            # Extract scores for each test case
            for i in range(len(queries)):
                case_scores = {}
                for metric_name in metrics:
                    if metric_name in result:
                        # Ragas returns a list of scores
                        case_scores[metric_name] = float(result[metric_name][i]) if i < len(result[metric_name]) else None
                    else:
                        case_scores[metric_name] = None

                # Calculate overall score
                valid_scores = [s for s in case_scores.values() if s is not None]
                overall = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

                results["results"].append({
                    "test_id": f"test_{i}",
                    "query": queries[i],
                    "response": responses[i][:200] + "..." if len(responses[i]) > 200 else responses[i],
                    "scores": case_scores,
                    "overall_score": overall,
                })

            # Calculate aggregate statistics
            for metric_name in metrics:
                if metric_name in result:
                    scores = [float(s) for s in result[metric_name] if s is not None]
                    if scores:
                        results["aggregate"][metric_name] = sum(scores) / len(scores)

            # Overall average
            all_overall = [r["overall_score"] for r in results["results"]]
            results["aggregate"]["overall"] = sum(all_overall) / len(all_overall) if all_overall else 0.0

            return results

        except Exception as e:
            logger.error(f"Real Ragas evaluation failed: {e}")
            raise


def evaluate_batch(
    evaluator: RagasRealEvaluator,
    test_cases: List[Dict[str, Any]],
    metrics: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Helper function to evaluate batch in the same format as other evaluators.

    Args:
        evaluator: RagasRealEvaluator instance
        test_cases: List of dicts with keys: query, response, contexts, reference
        metrics: Metrics to compute

    Returns:
        Dict with per-case results and aggregate statistics
    """
    queries = [case["query"] for case in test_cases]
    responses = [case["response"] for case in test_cases]
    contexts = [case["contexts"] for case in test_cases]
    references = [case.get("reference") for case in test_cases]

    # Only pass references if at least one is provided
    has_references = any(ref is not None for ref in references)

    result = evaluator.evaluate_batch(
        queries=queries,
        responses=responses,
        contexts=contexts,
        reference_answers=references if has_references else None,
        metrics=metrics,
    )

    # Add test IDs from original test cases
    for i, case in enumerate(test_cases):
        if i < len(result["results"]):
            result["results"][i]["test_id"] = case.get("id", f"test_{i}")

    return result
