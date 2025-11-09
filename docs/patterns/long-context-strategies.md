# Long Context Window Strategies

## Overview

Modern LLMs support increasingly large context windows (200K-2M tokens), enabling new approaches to document processing and summarization. This pattern documents strategies for effectively leveraging long context windows in healthcare AI summarization.

**Context Window Sizes**:
- **Claude 3.5 Sonnet/Haiku**: 200,000 tokens (~150,000 words)
- **Gemini 1.5 Pro**: 2,000,000 tokens (~1.5M words)
- **GPT-4 Turbo**: 128,000 tokens (~96,000 words)
- **Claude 3 Opus**: 200,000 tokens

**Key Insight**: Long context windows can eliminate or simplify RAG for many use cases, but require different strategies than traditional retrieval approaches.

## When to Use Long Context

### Use Long Context When:
- **Complete patient history needed** - Entire medical record fits in context
- **Multi-document analysis** - Need to reason across full documents simultaneously
- **Complex clinical guidelines** - 500+ page guidelines that must be referenced holistically
- **Longitudinal analysis** - Tracking patient trajectory over years
- **Few documents** - 2-10 documents that fit in context
- **No retrieval infrastructure** - Simpler than building vector store

### Use RAG When:
- **Large document corpus** - Thousands of documents
- **Frequent updates** - Content changes regularly
- **Cost-sensitive** - RAG retrieves only relevant portions
- **Low latency required** - Smaller context = faster response
- **Needle-in-haystack** - Specific fact retrieval from large corpus

## Healthcare Use Cases

### Patient Record Summarization (10+ Years)

```python
import anthropic

client = anthropic.Anthropic()


def summarize_complete_patient_history(patient_id: str) -> str:
    """
    Summarize entire patient history using long context window.

    With 200K tokens, can fit:
    - 10-15 years of comprehensive medical records
    - All clinical notes, lab results, procedures
    - No need for RAG retrieval

    Args:
        patient_id: Patient ID

    Returns:
        Comprehensive longitudinal summary
    """

    # Retrieve ALL patient clinical notes (e.g., from EHR/FHIR)
    all_clinical_notes = retrieve_all_patient_notes(patient_id)

    # Compile into single context
    full_medical_history = ""
    for note in sorted(all_clinical_notes, key=lambda x: x['date']):
        full_medical_history += f"\n\n--- {note['date']} - {note['type']} ---\n"
        full_medical_history += note['content']

    # Check token count (Claude: ~4 chars per token)
    estimated_tokens = len(full_medical_history) // 4
    print(f"Estimated input tokens: {estimated_tokens}")

    if estimated_tokens > 180000:  # Leave room for output
        print("Warning: May exceed context window, consider chunking")

    # Generate longitudinal summary
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        temperature=0.0,
        messages=[{
            "role": "user",
            "content": f"""Analyze this patient's complete {len(all_clinical_notes)}-note medical history spanning 10+ years.

COMPLETE MEDICAL HISTORY:
{full_medical_history}

Provide a comprehensive longitudinal summary including:

1. **Chronic Conditions & Progression**
   - Major diagnoses and how they've evolved
   - New conditions that developed over time

2. **Medication History**
   - Long-term medications
   - Changes, additions, discontinuations
   - Reasons for changes

3. **Major Events**
   - Hospitalizations
   - Surgeries/procedures
   - Emergency visits

4. **Lab Trends**
   - A1c trends (if diabetic)
   - Creatinine/eGFR trends (kidney function)
   - Lipid trends
   - Other relevant labs

5. **Clinical Trajectory**
   - Overall health trend (improving, stable, declining)
   - Key inflection points
   - Current status

6. **Care Gaps & Recommendations**
   - Overdue screenings
   - Medication adherence issues
   - Follow-up recommendations

LONGITUDINAL SUMMARY:"""
        }]
    )

    return message.content[0].text


# Example usage
patient_id = "12345"
summary = summarize_complete_patient_history(patient_id)
print(summary)
```

### Clinical Guideline Analysis (500+ Pages)

```python
def analyze_clinical_guideline(
    guideline_pdf_path: str,
    clinical_question: str
) -> str:
    """
    Analyze entire clinical guideline in single context.

    With Gemini 1.5 Pro (2M tokens), can fit:
    - 500-1000 page guidelines
    - Multiple guidelines simultaneously
    - All appendices, references, tables

    Args:
        guideline_pdf_path: Path to guideline PDF
        clinical_question: Specific clinical question

    Returns:
        Answer with guideline citations
    """

    # Extract text from PDF (using docling or pypdf)
    from docling.document_converter import DocumentConverter

    converter = DocumentConverter()
    result = converter.convert(guideline_pdf_path)
    guideline_text = result.document.export_to_markdown()

    # Check size
    estimated_tokens = len(guideline_text) // 4
    print(f"Guideline size: ~{estimated_tokens} tokens")

    # Use Gemini 1.5 Pro for very long guidelines (2M tokens)
    import vertexai
    from vertexai.generative_models import GenerativeModel

    vertexai.init(project="your-project", location="us-central1")

    model = GenerativeModel("gemini-1.5-pro-002")

    prompt = f"""You are analyzing the complete clinical practice guideline provided below.

COMPLETE GUIDELINE:
{guideline_text}

CLINICAL QUESTION: {clinical_question}

Provide a comprehensive answer:
1. Direct answer to the question
2. Relevant guideline recommendations
3. Strength of evidence (if specified)
4. Page/section citations from the guideline

ANSWER:"""

    response = model.generate_content(prompt)

    return response.text


# Example usage
answer = analyze_clinical_guideline(
    guideline_pdf_path="heart_failure_guidelines_2024.pdf",
    clinical_question="What are the indications for SGLT2 inhibitors in heart failure with preserved ejection fraction?"
)
print(answer)
```

## Strategies for Long Context

### 1. Document Ordering Strategy

```python
def order_documents_by_relevance(
    documents: list[dict],
    query: str
) -> list[dict]:
    """
    Order documents by relevance before adding to long context.

    Research shows:
    - Models attend more to beginning and end of context
    - Middle content may be "lost" in very long contexts

    Strategy: Put most relevant docs at beginning and end.

    Args:
        documents: List of documents with relevance scores
        query: User query

    Returns:
        Optimally ordered documents
    """

    # Sort by relevance
    sorted_docs = sorted(documents, key=lambda x: x['relevance_score'], reverse=True)

    # Reorder: high relevance at start and end, lower in middle
    # Research: "Lost in the Middle" phenomenon
    n = len(sorted_docs)

    if n <= 3:
        return sorted_docs  # Too few to reorder

    # Take top 40% and bottom 40% most relevant, put at edges
    top_n = int(n * 0.4)

    ordered = []
    ordered.extend(sorted_docs[:top_n])  # Most relevant at beginning
    ordered.extend(sorted_docs[top_n:-top_n])  # Less relevant in middle
    ordered.extend(sorted_docs[-top_n:])  # Important docs at end too

    return ordered


# Example usage
documents = [
    {"content": "...", "relevance_score": 0.95},
    {"content": "...", "relevance_score": 0.82},
    # ...
]

ordered_docs = order_documents_by_relevance(documents, query="heart failure treatment")

# Build context
context = "\n\n---\n\n".join([doc['content'] for doc in ordered_docs])
```

### 2. Hierarchical Summarization Strategy

```python
def hierarchical_long_context_summary(
    documents: list[str],
    max_tokens_per_batch: int = 150000
) -> str:
    """
    Use hierarchical summarization for documents exceeding context window.

    Strategy:
    1. Split documents into batches that fit in context
    2. Summarize each batch
    3. Combine summaries into final summary

    Args:
        documents: List of document texts
        max_tokens_per_batch: Max tokens per batch

    Returns:
        Final comprehensive summary
    """

    client = anthropic.Anthropic()

    # Estimate tokens and create batches
    def estimate_tokens(text: str) -> int:
        return len(text) // 4

    batches = []
    current_batch = []
    current_tokens = 0

    for doc in documents:
        doc_tokens = estimate_tokens(doc)

        if current_tokens + doc_tokens > max_tokens_per_batch:
            if current_batch:
                batches.append(current_batch)
            current_batch = [doc]
            current_tokens = doc_tokens
        else:
            current_batch.append(doc)
            current_tokens += doc_tokens

    if current_batch:
        batches.append(current_batch)

    print(f"Created {len(batches)} batches")

    # Phase 1: Summarize each batch
    batch_summaries = []

    for i, batch in enumerate(batches):
        print(f"Summarizing batch {i+1}/{len(batches)}...")

        batch_content = "\n\n---\n\n".join(batch)

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=0.0,
            messages=[{
                "role": "user",
                "content": f"""Summarize the following medical documents comprehensively:

{batch_content}

Provide a detailed summary covering:
- Key clinical findings
- Diagnoses and conditions
- Treatments and medications
- Important test results
- Clinical trajectory

SUMMARY:"""
            }]
        )

        batch_summaries.append(message.content[0].text)

    # Phase 2: Combine batch summaries into final summary
    combined_summaries = "\n\n---\n\n".join([
        f"BATCH {i+1} SUMMARY:\n{summary}"
        for i, summary in enumerate(batch_summaries)
    ])

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        temperature=0.0,
        messages=[{
            "role": "user",
            "content": f"""Synthesize the following batch summaries into a single comprehensive summary:

{combined_summaries}

Create a unified summary that:
- Integrates information across all batches
- Identifies patterns and trends
- Highlights key findings
- Organizes information coherently

FINAL SUMMARY:"""
        }]
    )

    return message.content[0].text


# Example usage
documents = [...]  # Large list of clinical notes
final_summary = hierarchical_long_context_summary(documents)
```

### 3. Prompt Caching for Repeated Queries

```python
def long_context_with_caching(
    clinical_guidelines: str,
    query: str
) -> str:
    """
    Use prompt caching for repeated queries against long context.

    With 200K token guidelines:
    - First query: Full price
    - Subsequent queries: 90% cheaper (cached)

    Perfect for:
    - Clinical decision support (same guidelines, many queries)
    - Patient record Q&A (same record, many questions)

    Args:
        clinical_guidelines: Large clinical guidelines (cached)
        query: Specific query

    Returns:
        Answer
    """

    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        temperature=0.0,
        system=[
            {
                "type": "text",
                "text": "You are a clinical decision support assistant."
            },
            {
                "type": "text",
                "text": f"CLINICAL GUIDELINES:\n{clinical_guidelines}",
                "cache_control": {"type": "ephemeral"}  # Cache this!
            }
        ],
        messages=[{
            "role": "user",
            "content": query
        }]
    )

    # Check cache usage
    usage = message.usage
    print(f"Cache read tokens: {usage.cache_read_input_tokens}")
    print(f"Cache creation tokens: {usage.cache_creation_input_tokens}")
    print(f"Input tokens: {usage.input_tokens}")

    return message.content[0].text


# Example: Multiple queries against same guidelines
guidelines_text = "[200K token clinical guidelines...]"

# First query: Creates cache
answer1 = long_context_with_caching(guidelines_text, "Beta-blocker contraindications?")

# Subsequent queries: Use cache (90% cheaper)
answer2 = long_context_with_caching(guidelines_text, "ACE inhibitor contraindications?")
answer3 = long_context_with_caching(guidelines_text, "SGLT2 inhibitor indications?")
```

### 4. Sliding Window Strategy

```python
def sliding_window_processing(
    long_document: str,
    window_size: int = 150000,  # tokens
    overlap: int = 10000  # tokens
) -> list[str]:
    """
    Process very long documents using sliding window.

    When document exceeds context window:
    - Break into overlapping windows
    - Process each window
    - Combine results

    Args:
        long_document: Very long document text
        window_size: Window size in tokens
        overlap: Overlap between windows

    Returns:
        List of window summaries
    """

    # Convert tokens to characters (rough: 1 token = 4 chars)
    window_chars = window_size * 4
    overlap_chars = overlap * 4

    windows = []
    start = 0

    while start < len(long_document):
        end = start + window_chars
        window_text = long_document[start:end]
        windows.append(window_text)

        # Move forward by (window_size - overlap)
        start += (window_chars - overlap_chars)

    print(f"Created {len(windows)} windows")

    # Process each window
    summaries = []

    for i, window in enumerate(windows):
        print(f"Processing window {i+1}/{len(windows)}...")

        summary = summarize_window(window, window_index=i)
        summaries.append(summary)

    return summaries


def summarize_window(window_text: str, window_index: int) -> str:
    """Summarize a single window."""

    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        temperature=0.0,
        messages=[{
            "role": "user",
            "content": f"""Summarize this section of a longer medical document (Window {window_index + 1}):

{window_text}

SUMMARY:"""
        }]
    )

    return message.content[0].text
```

## Cost Optimization

### Cost Comparison: Long Context vs RAG

```python
def compare_cost_long_context_vs_rag(
    num_documents: int,
    avg_doc_tokens: int,
    num_queries: int
):
    """
    Compare costs: long context vs RAG.

    Claude 3.5 Sonnet pricing:
    - Input: $3 per 1M tokens
    - Output: $15 per 1M tokens
    - Cache read: $0.30 per 1M tokens (90% discount)
    - Cache write: $3.75 per 1M tokens
    """

    # Long Context Approach
    total_tokens_long_context = num_documents * avg_doc_tokens

    # First query: Full cost
    first_query_cost = (total_tokens_long_context / 1_000_000) * 3  # Input cost

    # Subsequent queries: Cache cost
    subsequent_query_cost = (total_tokens_long_context / 1_000_000) * 0.30  # Cache read

    total_long_context_cost = first_query_cost + (num_queries - 1) * subsequent_query_cost

    # RAG Approach
    # Assume retrieve 5 documents per query
    docs_per_query = 5
    total_tokens_rag = num_queries * docs_per_query * avg_doc_tokens

    total_rag_cost = (total_tokens_rag / 1_000_000) * 3  # Input cost

    print(f"\n{'='*60}")
    print(f"Cost Comparison: {num_documents} documents, {num_queries} queries")
    print(f"{'='*60}")
    print(f"\nLong Context Approach:")
    print(f"  First query: ${first_query_cost:.2f}")
    print(f"  Subsequent queries: ${subsequent_query_cost:.2f} each")
    print(f"  Total cost: ${total_long_context_cost:.2f}")
    print(f"\nRAG Approach:")
    print(f"  Cost per query: ${(total_rag_cost / num_queries):.2f}")
    print(f"  Total cost: ${total_rag_cost:.2f}")
    print(f"\nWinner: {'Long Context' if total_long_context_cost < total_rag_cost else 'RAG'}")
    print(f"Savings: ${abs(total_long_context_cost - total_rag_cost):.2f}")


# Example scenarios
compare_cost_long_context_vs_rag(
    num_documents=50,
    avg_doc_tokens=2000,
    num_queries=20
)

# Output:
# Winner: Long Context (with caching)
# Savings: $... (especially for repeated queries)
```

## Limitations and Considerations

### Context Window Limitations

1. **Lost in the Middle**: Models may not attend equally to all parts of long context
   - **Solution**: Order documents by relevance (most important at start/end)

2. **Latency**: Longer context = slower response
   - **Mitigation**: Use faster models (Haiku, Flash) for long context when possible

3. **Cost**: Long context is expensive without caching
   - **Solution**: Use prompt caching for repeated queries

4. **Attention Dilution**: Too much irrelevant content reduces accuracy
   - **Solution**: Pre-filter documents for relevance before adding to context

### When NOT to Use Long Context

- **Dynamic corpus**: Frequent content updates (RAG is better)
- **Large corpus**: Thousands of documents (RAG scales better)
- **Low latency required**: Long context processing is slower
- **Cost-sensitive, varied queries**: RAG retrieves only what's needed

## Related Patterns

- [Basic RAG](./basic-rag.md)
- [Contextual Retrieval](./contextual-retrieval.md)
- [RAPTOR RAG](./raptor-rag.md)
- [Anthropic Claude Guide](../vendor-guides/anthropic-claude.md)
- [Google Vertex AI Guide](../vendor-guides/google-vertex-ai.md)

## References

- [Anthropic: Prompt Caching](https://docs.anthropic.com/en/docs/prompt-caching)
- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
- [Google: Long Context Windows in Gemini](https://ai.google.dev/gemini-api/docs/long-context)

## Version History

- **v1.0** (2025-01-09): Initial long context window strategies pattern with healthcare use cases, ordering strategies, caching, and cost analysis
