RAG Pipeline Metrics Overview

This document outlines the metrics that can be collected across all stages of a Retrieval‑Augmented Generation (RAG) pipeline, drawing from the project’s existing telemetry implementation and best‑practice observability recommendations.

1. Query‑Level Metrics
	•	rag_queries_total – Counter of total queries processed, labeled by embedder type, status (success/failure), and cache status. Useful for tracking usage patterns and failure rates.
	•	rag_query_duration_seconds – Histogram measuring end‑to‑end query latency. Enables computation of latency percentiles (p50, p95, p99).
	•	rag_query_tokens – Histogram tracking the number of tokens involved in each query (both prompt and completion). Helps estimate cost and detect outliers in token usage.
	•	Request metadata – OpenTelemetry spans can record model parameters such as temperature, top‑p, top‑k, model name/version, prompt length, and any other context about the query ￼.

2. Embedding Metrics
	•	rag_embedding_duration_seconds – Histogram for embedding generation latency, capturing how long it takes to create embeddings from user queries or documents.
	•	rag_embedding_requests_total – Counter of total embedding requests (useful for capacity planning).
	•	rag_embedder_usage_total – Counter that tracks which embedding models or services are being used (e.g., OpenAI vs. Hugging Face), and how often.

3. Retrieval Metrics
	•	rag_retrieval_docs – Histogram for the number of documents (or chunks) retrieved per query. Provides insight into how many documents are being loaded for the context.
	•	rag_retrieval_duration_seconds – Histogram measuring the time taken by retrieval operations from vector stores or other storage layers.
	•	rag_retrieval_scores – Histogram capturing similarity scores or other ranking metrics assigned to retrieved documents.
	•	rag_retrieval_quality_score – Custom gauge or histogram measuring retrieval performance (e.g., aggregated precision/recall metrics).

Classical IR metrics

When ground truth is available, the following metrics are useful:
	•	Precision/Recall – Precision measures the fraction of retrieved documents that are relevant, while recall measures the fraction of relevant documents that are retrieved ￼.
	•	Hit Rate@k – Whether at least one relevant document appears in the top‑k retrieved items.
	•	Precision@k/Recall@k – Precision and recall computed only on the top‑k results ￼.
	•	Mean Reciprocal Rank (MRR) – Average reciprocal of the rank of the first relevant document ￼.
	•	Mean Average Precision (MAP) – Average of precision values at each relevant document position.
	•	Normalized Discounted Cumulative Gain (NDCG) – Measures ranking quality by giving higher weight to relevant documents appearing earlier in the results ￼.

Context‑oriented metrics
	•	Context precision (context relevance) – Fraction of retrieved context statements that are relevant to the query. Computed in RAG evaluation frameworks by identifying relevant/irrelevant snippets ￼.
	•	Context recall (context sufficiency) – Whether the retrieved context covers all the facts needed to answer the query. RAGAS defines it by checking if all claims in the reference answer are present in the retrieved context ￼.
	•	Contextual relevancy – Proportion of retrieved context that is relevant to the query, irrespective of rank ￼.
	•	Context utilization – Ratio of retrieved context that is actually used in the final answer ￼.

4. Generation Metrics
	•	rag_generation_duration_seconds – Histogram for the time spent generating the answer (LLM completion). Useful for tracking slow generation.
	•	rag_generation_tokens – Histogram of the number of tokens generated. Important for cost and latency analysis.
	•	rag_generation_errors_total – Counter of generation errors, categorized by type (e.g., API error, timeout, rate‑limit).
	•	rag_answer_length – Histogram of answer lengths (characters or tokens). Helps enforce answer length policies.
	•	rag_citation_count – Histogram counting how many citations (sources) are included in each answer.

Quality metrics
	•	Answer relevancy – Measures whether the generated answer directly addresses the user’s query. Frameworks compute this by comparing embedding similarity between the question and the answer ￼.
	•	Faithfulness/hallucination – Determines whether all claims in the answer are supported by the retrieved context. If the answer includes unsupported statements, it is considered a hallucination ￼.
	•	Answer correctness – Compares the generated answer to a ground truth (if available) to check factual accuracy. Distinct from faithfulness, which only checks against the retrieved context ￼.
	•	Completeness – Evaluates whether the answer includes all relevant information. Useful for multi‑fact questions ￼.
	•	Conciseness/Fluency – Assesses brevity and natural language flow. These metrics help ensure the answer is readable and not overly verbose ￼.
	•	Citation accuracy and grounding score – Validates whether cited sources actually support the claims made ￼.

5. Cache Metrics
	•	rag_cache_hits_total – Counter of cache hits, indicating how many queries were served from cache.
	•	rag_cache_misses_total – Counter of cache misses, showing how many queries required new retrieval/generation.
	•	rag_cache_size – Gauge representing the current size of the cache (e.g., number of items or memory usage).
	•	rag_cache_operations_total – Counter for the total number of cache operations, including read and write events.

6. System/Operational Metrics
	•	Request volume – Gauge or counter of queries per minute/hour to monitor load ￼.
	•	Latency percentiles – Derived from latency histograms to capture p50/p95/p99 latencies for each stage.
	•	Resource usage – CPU and memory usage of the RAG service. Track via Prometheus Node Exporter or custom instrumentation.
	•	Token and cost counters – Custom counters that multiply token counts by API costs, providing insights into spending ￼.
	•	Error counters – Counters for different error categories (e.g., API failures, token errors, timeouts) ￼.
	•	Queue depth/concurrency – Gauge to monitor pending requests or active worker threads, helping maintain throughput.

7. Evaluation Frameworks and Recommendations
	•	RAGAS – Offers metrics for context precision, context recall, answer relevancy and faithfulness ￼.
	•	DeepEval (Confident AI) – Provides contextual precision, recall, relevancy, and answer‑level metrics; supports custom metrics ￼.
	•	LlamaIndex Evaluators – Calculates classical IR metrics (precision, recall, MRR, NDCG) and more ￼.
	•	TruLens – Focuses on context relevance/sufficiency and answer correctness/hallucination ￼.
	•	UpTrain – Adds task understanding and language quality metrics (e.g., response relevancy, completeness, conciseness) along with safety checks like prompt injection detection ￼.
	•	Patronus AI/Evidently AI – Provide UI and programmatic evaluations for context relevance/sufficiency and answer quality, as well as stress and adversarial testing ￼ ￼.

By incorporating these metrics and evaluation frameworks into your RAG pipeline, you can gain comprehensive visibility into retrieval performance, generation quality, and system health, enabling continuous improvement and robust monitoring.