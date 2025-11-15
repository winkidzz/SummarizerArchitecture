"""
Ragas-style evaluation using Google Gemini API.

Similar to ragas_evaluator.py but uses Gemini instead of local Ollama models.
Much faster and more reliable for structured output parsing.
"""

import json
import logging
import os
import re
import time
from typing import List, Dict, Any, Optional

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class RagasMetrics:
    """Available Ragas metrics."""
    FAITHFULNESS = "faithfulness"
    ANSWER_RELEVANCY = "answer_relevancy"
    CONTEXT_PRECISION = "context_precision"
    CONTEXT_RECALL = "context_recall"


class GeminiEvaluator:
    """
    Ragas-style RAG evaluator using Google Gemini API.

    Much faster and more reliable than local Ollama models for evaluation tasks.
    Requires GEMINI_API_KEY environment variable.
    """

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        api_key: Optional[str] = None
    ):
        """
        Initialize Gemini evaluator.

        Args:
            model: Gemini model to use (default: gemini-2.5-flash)
            api_key: Gemini API key (reads from GEMINI_API_KEY env var if not provided)
        """
        if not GENAI_AVAILABLE:
            raise ImportError(
                "google-generativeai is not installed. "
                "Install with: pip install google-generativeai"
            )

        self.model_name = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Set it in your .env file or pass as api_key parameter."
            )

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name=self.model_name)

        logger.info(f"GeminiEvaluator initialized with model: {model}")

    def evaluate(
        self,
        query: str,
        response: str,
        retrieved_contexts: List[str],
        reference_answer: Optional[str] = None,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a single RAG query-response pair.

        Args:
            query: User's question
            response: RAG system's response
            retrieved_contexts: List of retrieved document chunks
            reference_answer: Optional ground truth answer
            metrics: List of metrics to compute (default: all)

        Returns:
            Dict with scores for each metric and overall score
        """
        if metrics is None:
            metrics = [
                RagasMetrics.FAITHFULNESS,
                RagasMetrics.ANSWER_RELEVANCY,
                RagasMetrics.CONTEXT_PRECISION,
                RagasMetrics.CONTEXT_RECALL
            ]

        scores = {}

        # Faithfulness
        if RagasMetrics.FAITHFULNESS in metrics:
            scores[RagasMetrics.FAITHFULNESS] = self._evaluate_faithfulness(
                response, retrieved_contexts
            )

        # Answer Relevancy
        if RagasMetrics.ANSWER_RELEVANCY in metrics:
            scores[RagasMetrics.ANSWER_RELEVANCY] = self._evaluate_answer_relevancy(
                query, response
            )

        # Context Precision
        if RagasMetrics.CONTEXT_PRECISION in metrics:
            scores[RagasMetrics.CONTEXT_PRECISION] = self._evaluate_context_precision(
                query, retrieved_contexts, reference_answer
            )

        # Context Recall
        if RagasMetrics.CONTEXT_RECALL in metrics:
            if reference_answer:
                scores[RagasMetrics.CONTEXT_RECALL] = self._evaluate_context_recall(
                    query, reference_answer, retrieved_contexts
                )
            else:
                scores[RagasMetrics.CONTEXT_RECALL] = None

        # Compute overall score (average of non-None scores)
        valid_scores = [s for s in scores.values() if s is not None]
        overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

        return {
            "scores": scores,
            "overall_score": overall_score,
            "query": query,
            "response": response[:200] + "..." if len(response) > 200 else response
        }

    def _evaluate_faithfulness(
        self,
        response: str,
        contexts: List[str]
    ) -> float:
        """
        Evaluate if response is grounded in retrieved contexts.

        Returns:
            Score 0-1 (1 = fully grounded, 0 = not grounded)
        """
        prompt = f"""Evaluate if the RESPONSE is grounded in the CONTEXTS.

RESPONSE:
{response}

CONTEXTS:
{self._format_contexts(contexts)}

Question: Is each statement in the response supported by the contexts?

Provide your answer in this EXACT format:
SCORE: <number between 0 and 1>
REASONING: <explanation>

Example:
SCORE: 0.85
REASONING: Most statements are supported by the contexts, but one claim lacks evidence.
"""

        score, reasoning = self._call_judge_and_parse(prompt)
        logger.debug(f"Faithfulness: {score} - {reasoning}")
        return score

    def _evaluate_answer_relevancy(
        self,
        query: str,
        response: str
    ) -> float:
        """
        Evaluate if response is relevant to the query.

        Returns:
            Score 0-1 (1 = highly relevant, 0 = not relevant)
        """
        prompt = f"""Evaluate if the RESPONSE is relevant to the QUERY.

QUERY:
{query}

RESPONSE:
{response}

Question: How well does the response answer the query?

Provide your answer in this EXACT format:
SCORE: <number between 0 and 1>
REASONING: <explanation>

Example:
SCORE: 0.90
REASONING: The response directly answers the query with relevant details.
"""

        score, reasoning = self._call_judge_and_parse(prompt)
        logger.debug(f"Answer Relevancy: {score} - {reasoning}")
        return score

    def _evaluate_context_precision(
        self,
        query: str,
        contexts: List[str],
        reference_answer: Optional[str] = None
    ) -> float:
        """
        Evaluate if retrieved contexts are relevant to the query.

        Returns:
            Score 0-1 (1 = all contexts relevant, 0 = none relevant)
        """
        if not contexts:
            return 0.0

        reference_section = ""
        if reference_answer:
            reference_section = f"\nEXPECTED ANSWER:\n{reference_answer}\n"

        prompt = f"""Evaluate if the CONTEXTS are relevant to the QUERY.

QUERY:
{query}
{reference_section}

CONTEXTS:
{self._format_contexts(contexts)}

Question: What fraction of the contexts are relevant to answering the query?

Provide your answer in this EXACT format:
SCORE: <number between 0 and 1>
REASONING: <explanation>

Example:
SCORE: 0.80
REASONING: 4 out of 5 contexts contain relevant information for answering the query.
"""

        score, reasoning = self._call_judge_and_parse(prompt)
        logger.debug(f"Context Precision: {score} - {reasoning}")
        return score

    def _evaluate_context_recall(
        self,
        query: str,
        reference_answer: str,
        contexts: List[str]
    ) -> float:
        """
        Evaluate if all necessary information was retrieved.

        Returns:
            Score 0-1 (1 = all info retrieved, 0 = missing info)
        """
        prompt = f"""Evaluate if the CONTEXTS contain all information needed to answer the QUERY.

QUERY:
{query}

EXPECTED ANSWER:
{reference_answer}

RETRIEVED CONTEXTS:
{self._format_contexts(contexts)}

Question: Can the expected answer be fully derived from the retrieved contexts?

Provide your answer in this EXACT format:
SCORE: <number between 0 and 1>
REASONING: <explanation>

Example:
SCORE: 0.75
REASONING: Most information is present, but one key detail is missing from the contexts.
"""

        score, reasoning = self._call_judge_and_parse(prompt)
        logger.debug(f"Context Recall: {score} - {reasoning}")
        return score

    def _call_judge_and_parse(self, prompt: str) -> tuple[float, str]:
        """
        Call Gemini judge and parse response.

        Returns:
            (score, reasoning)
        """
        try:
            response = self._call_gemini(prompt)
            score, reasoning = self._parse_score_response(response)
            return score, reasoning
        except Exception as e:
            logger.error(f"Judge call failed: {e}")
            return 0.5, f"Error: {str(e)}"

    def _call_gemini(self, prompt: str, max_retries: int = 3) -> str:
        """Call Gemini API with retries."""
        for attempt in range(max_retries):
            try:
                # Generate response
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,  # Low temperature for consistency
                        max_output_tokens=500,  # Longer than Ollama for reasoning
                    )
                )

                return response.text

            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Gemini call failed (attempt {attempt + 1}): {e}")
                time.sleep(1)

    def _parse_score_response(self, response: str) -> tuple[float, str]:
        """
        Parse score and reasoning from judge response.

        Expected format:
        SCORE: 0.85
        REASONING: explanation here
        """
        lines = response.strip().split("\n")

        score = 0.5  # default
        reasoning = "Unable to parse judge response"

        for i, line in enumerate(lines):
            line = line.strip()

            # Try to find SCORE line
            if line.upper().startswith("SCORE:"):
                try:
                    score_text = line.split(":", 1)[1].strip()
                    # Extract number (handle various formats)
                    score_match = re.search(r"(\d+\.?\d*)", score_text)
                    if score_match:
                        score = float(score_match.group(1))
                        # Ensure score is 0-1
                        if score > 1.0:
                            score = score / 10.0  # Handle if judge used 0-10 scale
                        score = max(0.0, min(1.0, score))
                except Exception as e:
                    logger.warning(f"Failed to parse score: {e}")

            # Try to find REASONING line
            elif line.upper().startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()
                # Get rest of lines too
                if i + 1 < len(lines):
                    reasoning += " " + " ".join(lines[i+1:]).strip()
                break

        return score, reasoning

    def _format_contexts(self, contexts: List[str], max_len: int = 500) -> str:
        """Format contexts for judge prompt."""
        formatted = []
        for i, ctx in enumerate(contexts[:5]):  # Limit to 5 contexts
            truncated = ctx[:max_len] + "..." if len(ctx) > max_len else ctx
            formatted.append(f"[Context {i+1}]\n{truncated}")
        return "\n\n".join(formatted)


def evaluate_batch(
    evaluator: GeminiEvaluator,
    test_cases: List[Dict[str, Any]],
    metrics: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Evaluate multiple test cases in batch.

    Args:
        evaluator: GeminiEvaluator instance
        test_cases: List of dicts with keys: query, response, contexts, reference
        metrics: Metrics to compute

    Returns:
        Dict with per-case results and aggregate statistics
    """
    results = []

    for i, case in enumerate(test_cases):
        logger.info(f"Evaluating case {i+1}/{len(test_cases)}: {case.get('id', i)}")

        result = evaluator.evaluate(
            query=case["query"],
            response=case["response"],
            retrieved_contexts=case["contexts"],
            reference_answer=case.get("reference"),
            metrics=metrics
        )

        result["test_id"] = case.get("id", f"test_{i}")
        results.append(result)

    # Compute aggregate stats
    aggregate = _compute_aggregate_stats(results, metrics)

    return {
        "results": results,
        "aggregate": aggregate,
        "num_cases": len(test_cases)
    }


def _compute_aggregate_stats(
    results: List[Dict[str, Any]],
    metrics: Optional[List[str]] = None
) -> Dict[str, float]:
    """Compute aggregate statistics across all results."""
    if not results:
        return {}

    if metrics is None:
        metrics = [
            RagasMetrics.FAITHFULNESS,
            RagasMetrics.ANSWER_RELEVANCY,
            RagasMetrics.CONTEXT_PRECISION,
            RagasMetrics.CONTEXT_RECALL
        ]

    aggregate = {}

    for metric in metrics:
        scores = [
            r["scores"][metric]
            for r in results
            if metric in r["scores"] and r["scores"][metric] is not None
        ]
        if scores:
            aggregate[metric] = sum(scores) / len(scores)

    # Overall average
    overall_scores = [r["overall_score"] for r in results]
    aggregate["overall"] = sum(overall_scores) / len(overall_scores)

    return aggregate
