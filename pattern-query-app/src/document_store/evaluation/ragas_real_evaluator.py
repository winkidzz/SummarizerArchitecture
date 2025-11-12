"""
Real Ragas framework integration for RAG evaluation.

Uses the official Ragas library with Ollama or Gemini LLM support via LangChain.
"""

import logging
import os
from typing import List, Dict, Any, Optional
import pandas as pd

try:
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )
    from ragas.llms import LangchainLLMWrapper
    from ragas import RunConfig
    try:
        from langchain_ollama import OllamaLLM as Ollama
    except ImportError:
        # Fallback to deprecated import
        from langchain_community.llms import Ollama
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError:
        ChatGoogleGenerativeAI = None
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
    except ImportError:
        # Fallback to community package
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
        except ImportError:
            HuggingFaceEmbeddings = None
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False
    Dataset = None
    evaluate = None
    faithfulness = None
    answer_relevancy = None
    context_precision = None
    context_recall = None
    LangchainLLMWrapper = None
    RunConfig = None
    Ollama = None
    ChatGoogleGenerativeAI = None
    HuggingFaceEmbeddings = None

logger = logging.getLogger(__name__)


class RagasRealEvaluator:
    """
    Real Ragas framework evaluator using official Ragas library.
    
    Uses Ragas's built-in metrics and evaluation framework with
    Ollama or Gemini LLMs via LangChain integration.
    """

    def __init__(
        self,
        model: str = "gpt-oss:latest",
        base_url: Optional[str] = None,
        llm_type: str = "auto",  # "auto", "ollama", "gemini"
    ):
        """
        Initialize Ragas evaluator.
        
        Args:
            model: Model name (Ollama model name or Gemini model like "gemini-2.5-flash")
            base_url: Ollama API base URL (required for Ollama, ignored for Gemini)
            llm_type: Type of LLM - "auto" (detect from model name), "ollama", or "gemini"
        """
        if not RAGAS_AVAILABLE:
            raise ImportError(
                "ragas is not installed. Install it with: pip install ragas datasets langchain-community"
            )
        
        self.model = model
        self.base_url = base_url or "http://localhost:11434"
        self.llm_type = llm_type
        
        # Auto-detect LLM type if not specified
        if llm_type == "auto":
            if model.startswith("gemini") or model.startswith("gemini-"):
                llm_type = "gemini"
            else:
                llm_type = "ollama"
        
        self.llm_type = llm_type  # Store detected type
        
        # Initialize LLM based on type
        if llm_type == "gemini":
            if not ChatGoogleGenerativeAI:
                raise ImportError(
                    "langchain-google-genai is not installed. "
                    "Install it with: pip install langchain-google-genai"
                )
            
            # Check for API key
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "GOOGLE_API_KEY environment variable is required for Gemini models. "
                    "Set it with: export GOOGLE_API_KEY='your-key-here'"
                )
            
            # Initialize Gemini LLM
            # Model names: gemini-2.5-flash, gemini-2.5-pro, gemini-1.5-pro, etc.
            gemini_llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=api_key,
                temperature=0.1,  # Low temperature for consistency
            )
            
            # Wrap LangChain LLM with Ragas wrapper
            self.llm = LangchainLLMWrapper(gemini_llm)
            logger.info(f"Wrapped Gemini LLM ({model}) with LangchainLLMWrapper")
            
        else:  # ollama
            if not Ollama:
                raise ImportError(
                    "langchain-ollama or langchain-community is not installed. "
                    "Install it with: pip install langchain-ollama"
                )
            
            # Initialize Ollama LLM for Ragas
            try:
                # Try new langchain-ollama API
                ollama_llm = Ollama(
                    model=model,
                    base_url=self.base_url,
                    temperature=0.1,  # Low temperature for consistency
                )
            except TypeError:
                # Fallback for deprecated API
                ollama_llm = Ollama(
                    model=model,
                    base_url=self.base_url,
                )
            
            # Wrap LangChain LLM with Ragas wrapper for proper integration
            self.llm = LangchainLLMWrapper(ollama_llm)
            logger.info(f"Wrapped Ollama LLM ({model}) with LangchainLLMWrapper")
        
        # Initialize embeddings (use sentence-transformers, same as our vector store)
        # This avoids requiring OpenAI API key
        if HuggingFaceEmbeddings:
            try:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
                logger.info("Using Huggingface embeddings (all-MiniLM-L6-v2)")
            except Exception as e:
                logger.warning(f"Could not initialize Huggingface embeddings: {e}. Will use default.")
                self.embeddings = None
        else:
            logger.warning("HuggingFaceEmbeddings not available. Ragas will try to use default embeddings.")
            self.embeddings = None
        
        logger.info(f"RagasRealEvaluator initialized with model: {model}")

    def evaluate(
        self,
        query: str,
        response: str,
        retrieved_contexts: List[str],
        reference_answer: Optional[str] = None,
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate a single RAG query-response pair using Ragas.
        
        Args:
            query: User's question
            response: RAG system's response
            retrieved_contexts: List of retrieved document chunks
            reference_answer: Optional ground truth answer
            metrics: List of metrics to compute (default: all)
            
        Returns:
            Dict with scores for each metric and overall score
        """
        # Prepare dataset in Ragas format
        # Ragas uses 'reference' (not 'ground_truths') for context_precision
        data = {
            "question": [query],
            "answer": [response],
            "contexts": [[ctx for ctx in retrieved_contexts]],
        }
        
        # Add reference if provided (required for context_precision)
        # Ragas expects reference as a string, not a list
        if reference_answer:
            data["reference"] = [reference_answer]
        else:
            # Provide empty reference if not available
            data["reference"] = [""]
        
        dataset = Dataset.from_dict(data)
        
        # Select metrics
        if metrics is None:
            selected_metrics = [
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall,
            ]
        else:
            metric_map = {
                "faithfulness": faithfulness,
                "answer_relevancy": answer_relevancy,
                "context_precision": context_precision,
                "context_recall": context_recall,
            }
            selected_metrics = [metric_map[m] for m in metrics if m in metric_map]
        
        # Run Ragas evaluation with appropriate timeout
        # Gemini (cloud) is faster, Ollama (remote) may be slower
        if self.llm_type == "gemini":
            # Cloud service - shorter timeout is sufficient
            run_config = RunConfig(timeout=300, max_retries=3, max_workers=8) if RunConfig else None
        else:
            # Remote Ollama - longer timeout for slow instances
            run_config = RunConfig(timeout=1800, max_retries=2, max_workers=4) if RunConfig else None
        
        try:
            eval_kwargs = {
                "dataset": dataset,
                "metrics": selected_metrics,
                "llm": self.llm,
                "embeddings": self.embeddings,  # Use custom embeddings
            }
            if run_config:
                eval_kwargs["run_config"] = run_config
            
            result = evaluate(**eval_kwargs)
            
            # Extract scores from Ragas result
            # Ragas returns a ScoreDict or can be converted to pandas
            scores = {}
            if hasattr(result, 'to_pandas'):
                df = result.to_pandas()
                # Ragas uses metric names as column names
                for col in df.columns:
                    if col not in ['question', 'answer', 'contexts', 'reference', 'ground_truths']:
                        scores[col] = float(df[col].iloc[0])
            elif isinstance(result, dict):
                # Direct dict format
                for key, value in result.items():
                    if key not in ['question', 'answer', 'contexts', 'reference', 'ground_truths']:
                        scores[key] = float(value[0] if isinstance(value, list) else value)
            
            # Compute overall score (average of all scores)
            valid_scores = [s for s in scores.values() if s is not None]
            overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
            
            return {
                "scores": scores,
                "overall_score": overall_score,
                "query": query,
                "response": response[:200] + "..." if len(response) > 200 else response,
                "ragas_result": result,
            }
            
        except Exception as e:
            logger.error(f"Ragas evaluation failed: {e}")
            import traceback
            traceback.print_exc()
            # Return default scores on error
            return {
                "scores": {m: 0.5 for m in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]},
                "overall_score": 0.5,
                "query": query,
                "response": response[:200] + "..." if len(response) > 200 else response,
                "error": str(e),
            }


def evaluate_batch(
    evaluator: RagasRealEvaluator,
    test_cases: List[Dict[str, Any]],
    metrics: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Evaluate multiple test cases in batch using Ragas.
    
    Args:
        evaluator: RagasRealEvaluator instance
        test_cases: List of dicts with keys: query, response, contexts, reference
        metrics: Metrics to compute
        
    Returns:
        Dict with per-case results and aggregate statistics
    """
    if not RAGAS_AVAILABLE:
        raise ImportError("ragas is not installed")
    
    # Prepare batch dataset for Ragas
    # Ragas uses 'reference' (not 'ground_truths') for context_precision
    data = {
        "question": [case["query"] for case in test_cases],
        "answer": [case["response"] for case in test_cases],
        "contexts": [[ctx for ctx in case["contexts"]] for case in test_cases],
    }
    
    # Add reference (required for context_precision metric)
    # Ragas expects reference as a string, not a list
    data["reference"] = [
        case.get("reference") if case.get("reference") else ""
        for case in test_cases
    ]
    
    dataset = Dataset.from_dict(data)
    
    # Select metrics
    if metrics is None:
        selected_metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ]
    else:
        metric_map = {
            "faithfulness": faithfulness,
            "answer_relevancy": answer_relevancy,
            "context_precision": context_precision,
            "context_recall": context_recall,
        }
        selected_metrics = [metric_map[m] for m in metrics if m in metric_map]
    
    # Run Ragas batch evaluation with appropriate timeout
    # Gemini (cloud) is faster, Ollama (remote) may be slower
    llm_type = evaluator.llm_type
    if llm_type == "gemini":
        # Cloud service - shorter timeout is sufficient
        run_config = RunConfig(timeout=300, max_retries=3, max_workers=8) if RunConfig else None
    else:
        # Remote Ollama - longer timeout for slow instances
        run_config = RunConfig(timeout=1800, max_retries=2, max_workers=4) if RunConfig else None
    
    try:
        eval_kwargs = {
            "dataset": dataset,
            "metrics": selected_metrics,
            "llm": evaluator.llm,
            "embeddings": evaluator.embeddings,  # Use custom embeddings
        }
        if run_config:
            eval_kwargs["run_config"] = run_config
        
        result = evaluate(**eval_kwargs)
        
        # Convert Ragas result to our format
        df = result.to_pandas()
        
        # Extract per-case results
        results = []
        for i, case in enumerate(test_cases):
            case_result = {
                "test_id": case.get("id", f"test_{i}"),
                "query": case["query"],
                "response": case["response"][:200] + "..." if len(case["response"]) > 200 else case["response"],
                "scores": {},
                "overall_score": 0.0,
            }
            
            # Extract scores for this case
            # Ragas uses metric names as column names (e.g., 'faithfulness', 'answer_relevancy')
            valid_scores = []
            metric_columns = ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']
            for col in df.columns:
                # Only process known metric columns and skip non-metric columns
                if col in metric_columns:
                    try:
                        value = df[col].iloc[i]
                        # Handle NaN or None values
                        if pd.isna(value) or value is None:
                            continue
                        # Try to convert to float
                        score = float(value)
                        case_result["scores"][col] = score
                        valid_scores.append(score)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Could not convert {col} value '{value}' to float for case {i}: {e}")
                        continue
            
            # Compute overall score
            case_result["overall_score"] = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
            results.append(case_result)
        
        # Compute aggregate statistics
        aggregate = {}
        metric_columns = ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']
        for col in df.columns:
            # Only process known metric columns
            if col in metric_columns:
                try:
                    # Convert to numeric, ignoring errors
                    numeric_col = pd.to_numeric(df[col], errors='coerce')
                    mean_score = numeric_col.mean()
                    if not pd.isna(mean_score):
                        aggregate[col] = float(mean_score)
                except Exception as e:
                    logger.warning(f"Could not compute aggregate for {col}: {e}")
        
        # Overall average
        overall_scores = [r["overall_score"] for r in results]
        aggregate["overall"] = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
        
        return {
            "results": results,
            "aggregate": aggregate,
            "num_cases": len(test_cases),
        }
        
    except Exception as e:
        logger.error(f"Ragas batch evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        raise

