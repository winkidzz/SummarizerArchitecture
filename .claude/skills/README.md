# Claude Skills - Self-Updating Research System

This directory contains Claude Skills that implement the **self-updating research system** (Goal 2 of the AI Summarization Reference Architecture project).

## Project Dual Goals

This project has two interconnected goals:

**Goal 1: Documentation** - Research and develop AI strategies, patterns, and blueprints for healthcare summarization

**Goal 2: Self-Updating System** - Agentic AI that monitors research sources (arXiv, blogs, etc.) and automatically keeps Goal 1 documentation current

## Claude Skills Overview

Claude Skills are specialized agents that autonomously perform complex tasks. This project implements three core skills:

### 1. Research Monitor (`research-monitor.md`)

**Purpose**: Monitor arXiv and reputable sources for latest AI/RAG research

**What it does**:
- Searches arXiv API for papers on RAG, LLM, healthcare AI
- Monitors Anthropic, Google AI, Microsoft, AWS blogs
- Evaluates research quality (citations, authors, relevance)
- Extracts key insights and new patterns
- Updates pattern library automatically
- Ingests papers into ChromaDB with metadata
- Generates weekly update reports

**Implementation**: [scripts/research_monitor.py](../../scripts/research_monitor.py)

**Triggers**:
- Weekly automated runs
- Manual trigger: "monitor research"
- After new pattern is created

### 2. Pattern Validator (`pattern-validator.md`)

**Purpose**: Validate and update existing patterns based on latest research

**What it does**:
- Reviews all pattern documentation
- Compares performance claims against latest research in ChromaDB
- Tests code examples for correctness and syntax
- Updates outdated model versions and API references
- Flags issues requiring manual review
- Generates validation reports

**Implementation**: [scripts/pattern_validator.py](../../scripts/pattern_validator.py)

**Triggers**:
- After research-monitor finds new papers
- Manual trigger: "validate patterns"
- Before major releases

### 3. Web Search (Future)

**Purpose**: Search beyond arXiv for latest industry updates

**Status**: Planned

## Installation

### 1. Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Install Playwright browsers (for web scraping)
playwright install
```

### 2. Configure Environment

Create a `.env` file:

```bash
# Optional: API keys for LLM-powered analysis
ANTHROPIC_API_KEY=your_api_key_here

# Optional: arXiv API (no key required, but rate-limited)
ARXIV_EMAIL=your_email@example.com  # For polite usage
```

### 3. Initialize ChromaDB

The first run will automatically create the ChromaDB database:

```bash
# Run initial research monitor to populate database
python scripts/research_monitor.py --mode monitor --days-back 30
```

## Usage

### Research Monitor

**Monitor arXiv for new papers** (recommended weekly):

```bash
python scripts/research_monitor.py --mode monitor
```

**Search ChromaDB for specific topics**:

```bash
python scripts/research_monitor.py --mode search --query "contextual retrieval"
```

**Ingest a specific arXiv paper**:

```bash
python scripts/research_monitor.py --mode ingest --arxiv-id 2401.12345
```

**Customize monitoring**:

```bash
# Last 14 days
python scripts/research_monitor.py --mode monitor --days-back 14

# Specify ChromaDB path
python scripts/research_monitor.py --mode monitor --chroma-db ./my_db
```

### Pattern Validator

**Validate all patterns**:

```bash
python scripts/pattern_validator.py --mode validate
```

**Validate specific pattern**:

```bash
python scripts/pattern_validator.py --mode validate --pattern basic-rag.md
```

**Test all code examples**:

```bash
python scripts/pattern_validator.py --mode test-examples
```

**Update benchmarks** (requires LLM integration):

```bash
python scripts/pattern_validator.py --mode update-benchmarks
```

## Reports

Both scripts generate detailed JSON reports in the `reports/` directory:

- `reports/research-monitor-YYYYMMDD-HHMMSS.json` - Research monitoring results
- `reports/pattern-validation-YYYYMMDD-HHMMSS.json` - Pattern validation results

## How the Self-Updating System Works

```
┌─────────────────────────────────────────────────────────────┐
│                    Weekly Research Cycle                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Research Monitor                                         │
│     - Search arXiv for papers (last 7 days)                 │
│     - Monitor Anthropic/Google/Microsoft/AWS blogs          │
│     - Evaluate paper quality and relevance                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Ingest into ChromaDB                                    │
│     - Extract metadata (title, authors, date, categories)   │
│     - Generate embeddings (sentence-transformers)           │
│     - Store in research_papers collection                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Pattern Analysis                                        │
│     - Identify affected patterns (keyword matching)         │
│     - Extract key insights from abstracts                   │
│     - Generate update recommendations                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Pattern Validator                                       │
│     - Parse pattern documentation                           │
│     - Validate performance claims against ChromaDB          │
│     - Test code examples for errors                         │
│     - Check for deprecated APIs                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Update Recommendations                                  │
│     - Generate validation report                            │
│     - Flag outdated benchmarks                              │
│     - Suggest pattern improvements                          │
│     - (Optional) Auto-update with LLM                       │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### ChromaDB Schema

**Collection**: `research_papers`

**Document**: Paper title + abstract

**Metadata**:
- `arxiv_id`: arXiv identifier (e.g., "2401.12345")
- `title`: Paper title
- `authors`: Comma-separated author names
- `publish_date`: Publication date (YYYY-MM-DD)
- `url`: arXiv URL
- `categories`: arXiv categories (e.g., "cs.CL, cs.AI")
- `relevance_score`: Quality score (0.0 to 1.0)
- `ingested_at`: Timestamp when added to database

### Research Quality Scoring

Papers are scored on multiple dimensions:

1. **Category Relevance** (0-0.3): cs.CL, cs.AI, cs.LG, cs.IR preferred
2. **Healthcare Relevance** (0-0.2): Keywords like "medical", "clinical", "healthcare"
3. **Query Relevance** (0-0.3): Matching terms in title/abstract
4. **Recency** (0-0.2): Papers from last 6 months scored higher

**Threshold**: Papers with score >= 0.5 are ingested into ChromaDB

## Automation

### GitHub Actions (Recommended)

Create `.github/workflows/research-monitor.yml`:

```yaml
name: Weekly Research Monitor

on:
  schedule:
    # Run every Monday at 9 AM UTC
    - cron: '0 9 * * 1'
  workflow_dispatch:  # Manual trigger

jobs:
  monitor:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install

      - name: Run research monitor
        run: |
          python scripts/research_monitor.py --mode monitor

      - name: Run pattern validator
        run: |
          python scripts/pattern_validator.py --mode validate

      - name: Upload reports
        uses: actions/upload-artifact@v4
        with:
          name: research-reports
          path: reports/
```

### Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add weekly Monday 9 AM run
0 9 * * 1 cd /path/to/SummarizerArchitecture && python scripts/research_monitor.py --mode monitor
```

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task: "Weekly Research Monitor"
3. Trigger: Weekly, Monday 9:00 AM
4. Action: Start a program
   - Program: `python`
   - Arguments: `scripts/research_monitor.py --mode monitor`
   - Start in: `C:\path\to\SummarizerArchitecture`

## Extending the System

### Adding New Research Sources

Edit `scripts/research_monitor.py`:

```python
class WebSourceMonitor:
    SOURCES = {
        'anthropic': {...},
        'google_ai': {...},

        # Add new source
        'new_source': {
            'name': 'New Research Blog',
            'url': 'https://example.com/research',
            'topics': ['RAG', 'LLM'],
        }
    }
```

### Adding New Search Topics

```python
monitor.monitor_arxiv(
    topics=[
        "retrieval augmented generation",
        "RAG",
        # Add your topics
        "prompt engineering",
        "agentic AI",
    ],
    days_back=7
)
```

### Customizing Quality Evaluation

Edit `ResearchQualityEvaluator` in `research_monitor.py`:

```python
def evaluate_paper(self, paper: ResearchPaper, query: str) -> float:
    score = 0.0

    # Add your custom scoring logic
    if 'your_keyword' in paper.title.lower():
        score += 0.3

    return score
```

## LLM-Powered Enhancements (Future)

The current implementation uses rule-based analysis. Future enhancements with LLM integration:

1. **Insight Extraction**: Use Claude to extract key insights from papers
2. **Pattern Updates**: Automatically update pattern documentation
3. **Citation Generation**: Generate proper citations for new research
4. **Contradiction Detection**: Identify conflicting research
5. **Trend Analysis**: Summarize research trends over time

### Example LLM Integration

```python
import anthropic

client = anthropic.Anthropic()

def extract_insights_with_llm(paper: ResearchPaper) -> List[str]:
    """Extract key insights using Claude."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Analyze this research paper and extract 3-5 key insights
relevant to RAG (Retrieval-Augmented Generation) systems:

Title: {paper.title}

Abstract: {paper.abstract}

Focus on:
1. Novel techniques or approaches
2. Performance improvements
3. Implementation considerations
4. Relevance to healthcare AI

Provide insights as a bulleted list."""
        }]
    )

    insights_text = message.content[0].text
    insights = [line.strip('- ') for line in insights_text.split('\n') if line.strip().startswith('-')]

    return insights
```

## Troubleshooting

### ChromaDB Issues

**Error**: `Collection not found`

```bash
# Initialize database
python scripts/research_monitor.py --mode monitor
```

**Error**: `Embedding function mismatch`

```bash
# Delete and recreate ChromaDB
rm -rf chroma_db/
python scripts/research_monitor.py --mode monitor
```

### arXiv Rate Limiting

arXiv API limits: 1 request every 3 seconds

```python
# The script includes automatic rate limiting
time.sleep(3)  # Between requests
```

If you get rate-limited:
- Reduce `max_results` parameter
- Increase `time.sleep()` duration
- Add `ARXIV_EMAIL` to `.env` for polite usage

### Playwright Installation

```bash
# Install browsers
playwright install

# Specific browser
playwright install chromium
```

## Performance

### Typical Run Times

- **Research Monitor** (7 days, 5 topics): ~2-3 minutes
- **Pattern Validator** (10 patterns): ~30-60 seconds
- **ChromaDB Query**: <100ms

### Storage

- **ChromaDB**: ~1-5 MB per 100 papers
- **Reports**: ~10-50 KB per report

## Security

### API Keys

- Store in `.env` file (never commit to git)
- Use environment variables
- Rotate keys regularly

### Web Scraping

- Respect `robots.txt`
- Rate limiting implemented (3 seconds between requests)
- User-agent headers included

### PHI/HIPAA

- Research papers are public domain
- No PHI stored in ChromaDB
- Pattern examples use synthetic data

## Contributing

When adding new skills:

1. Create skill definition in `.claude/skills/[name].md`
2. Implement in `scripts/[name].py`
3. Add dependencies to `requirements.txt`
4. Update this README
5. Add tests in `tests/`

## Version History

- **v1.0** (2025-01-09): Initial Claude Skills implementation with research monitor and pattern validator

## References

- [Claude Skills Documentation](https://docs.anthropic.com/claude/docs/skills)
- [arXiv API Documentation](https://arxiv.org/help/api)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
