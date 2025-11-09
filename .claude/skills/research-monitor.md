# Research Monitor Skill

Monitor arXiv and other reputable sources for latest AI/RAG research and update the pattern library.

## Trigger
When user asks to:
- "update research"
- "check for new RAG patterns"
- "monitor latest AI papers"
- "search arXiv for [topic]"
- Automatically: Run weekly to stay current

## Execution Steps

1. **Search arXiv for Latest Research**
   - Query arXiv API for papers on: RAG, LLM, healthcare AI, medical NLP
   - Filter papers from last 30 days
   - Focus on highly-cited or influential authors

2. **Search Additional Sources**
   - Anthropic blog (Claude updates, new features)
   - Google AI blog (Gemini, Vertex AI updates)
   - Microsoft Research (Azure OpenAI)
   - AWS Machine Learning blog (Bedrock)
   - Papers with Code (implementation benchmarks)

3. **Evaluate Research Quality**
   - Check citation count
   - Verify author credibility
   - Assess relevance to healthcare AI
   - Validate methodology

4. **Extract Key Insights**
   - New RAG patterns or improvements
   - Performance benchmarks
   - Healthcare-specific applications
   - Implementation details

5. **Update Pattern Library**
   - Add new patterns to `docs/patterns/`
   - Update existing patterns with new research
   - Add references to arXiv papers
   - Update performance characteristics with latest benchmarks

6. **Ingest into ChromaDB**
   - Chunk research papers
   - Add metadata (authors, date, citations, topic)
   - Embed and store in vector database
   - Make searchable for future queries

7. **Generate Update Report**
   - Summary of new research found
   - Patterns that need updating
   - Recommended changes to documentation
   - Action items for implementation

## Example Usage

```python
# User query
"Check arXiv for latest RAG research from past month"

# Skill execution
1. Search arXiv: "RAG OR retrieval-augmented generation" (last 30 days)
2. Found 15 papers
3. Extract: "Contextual Retrieval reduces errors by 49%" (Anthropic, Sept 2024)
4. Update: docs/patterns/contextual-retrieval.md
5. Ingest paper into ChromaDB
6. Report: "Added Contextual Retrieval pattern based on latest research"
```

## Output Format

```markdown
## Research Update Report - [Date]

### New Papers Found: [N]
1. [Paper Title] - [Authors] - arXiv:[ID]
   - Key Finding: [summary]
   - Relevance: [healthcare/RAG/LLM]
   - Action: [add pattern/update existing/reference only]

### Patterns Updated: [N]
- [pattern-name.md]: Added benchmarks from [paper]
- [pattern-name.md]: Updated implementation based on [paper]

### New Patterns Added: [N]
- [new-pattern.md]: Based on [paper]

### Ingested into ChromaDB: [N] papers
- Collection: research-papers
- Metadata: authors, date, topic, citations

### Recommendations
- [ ] Review [pattern] for potential improvements
- [ ] Add [technique] to vendor guides
- [ ] Benchmark [approach] against existing patterns
```

## Configuration

```yaml
sources:
  - name: arXiv
    url: http://export.arxiv.org/api/query
    topics:
      - "RAG"
      - "retrieval-augmented generation"
      - "medical NLP"
      - "healthcare AI"
      - "clinical decision support"
    update_frequency: weekly

  - name: Anthropic Blog
    url: https://www.anthropic.com/research
    check_frequency: weekly

  - name: Google AI Blog
    url: https://ai.googleblog.com
    check_frequency: weekly

  - name: Papers with Code
    url: https://paperswithcode.com
    topics:
      - "question-answering"
      - "information-retrieval"
    check_frequency: weekly

quality_filters:
  min_citations: 5  # For papers older than 3 months
  trusted_authors: [list of known researchers]
  min_relevance_score: 0.7  # Semantic similarity to healthcare AI

chromadb:
  collection: "research-papers"
  embedding_model: "all-MiniLM-L6-v2"
  metadata_fields:
    - authors
    - publish_date
    - arxiv_id
    - citations
    - topic
    - relevance_score
```

## Implementation

See: `scripts/research_monitor.py`
