# UI Tier Display Guide

## Overview

The web UI now displays **3-tier retrieval breakdown** to help you understand which sources contributed to each query result.

## Visual Indicators

### Tier Breakdown Section

When you submit a query with web search enabled, the Answer Card now shows a "3-Tier Retrieval Breakdown" section with:

```
3-Tier Retrieval Breakdown
┌─────────────────────────────┬─────────────────────────────┬─────────────────────────────┐
│ Tier 1 (Pattern Library)    │ Tier 2 (Web KB Cache)       │ Tier 3 (Live Web)           │
│ 8                            │ 2                           │ 0                           │
└─────────────────────────────┴─────────────────────────────┴─────────────────────────────┘
```

**Interpretation**:
- **Tier 1**: Number of results from your local Pattern Library (curated, trusted content)
- **Tier 2**: Number of results from Web Knowledge Base cache (previously fetched web results)
- **Tier 3**: Number of results from live web search (fresh web results)

### Source List Badges

Each source in the "Supporting documents" section now has a colored badge:

- **T1** (Green `#10b981`): Pattern Library source - Trusted, curated content
- **T2** (Blue `#3b82f6`): Web KB Cache - Previously fetched web results
- **T3** (Purple `#8b5cf6`): Live Web - Fresh web search results

Example:
```
[T1] docs/patterns/contextual_retrieval.md
     pattern | Score: 0.847

[T2] https://www.anthropic.com/news/contextual-retrieval
     web_knowledge_base | Score: 0.826

[T3] https://arxiv.org/abs/2409.12345
     web_search | Score: 0.731
```

## Understanding the Results

### When Tier 3 = 0 (No Live Web Results)

This is **normal** and can happen for several reasons:

1. **Web KB has good cached results** (most common)
   - In "on_low_confidence" mode, if Tier 2 has ≥3 results with avg score ≥0.5, live web search is skipped
   - This saves ~7 seconds of latency while still providing web-sourced information

2. **Pattern Library has excellent results**
   - Weighted RRF fusion prioritizes Pattern Library (weight 1.0) over web results (weight 0.7)
   - High-quality Pattern Library results naturally outrank web results during top-k selection

3. **Web content extraction failed**
   - Trafilatura couldn't extract meaningful content from some URLs
   - Short content was filtered out by Web KB

### When to Expect Tier 3 Results

You'll see Tier 3 (live web) results when:

1. **Using "parallel" mode**
   - Always searches all 3 tiers simultaneously
   - Good for queries needing fresh information

2. **Query not in Pattern Library or Web KB**
   - New topics not covered in local patterns
   - Recent news or events

3. **Query with temporal keywords**
   - "latest", "recent", "2025", etc.
   - System detects need for fresh information

4. **Pattern Library + Web KB have low confidence**
   - Few results (<3 across tiers)
   - Low similarity scores (<0.5)

## Web Search Modes

### On Low Confidence (Recommended)

- **Default mode** in the UI
- Only triggers live web search when needed
- Smart about using cached results
- Lower latency for most queries

**Example behavior**:
```
Query: "How does contextual retrieval reduce hallucinations?"

Pattern Library (T1): 8 results, avg 0.75
Web KB Cache (T2):    2 results, avg 0.826
Live Web (T3):        SKIPPED (T2 has good results)

Final top-5: 3×T1, 2×T2
```

### Parallel (Always Search All Tiers)

- Always searches all 3 tiers
- Good for fresh information needs
- Higher latency (~7-10 seconds)

**Example behavior**:
```
Query: "latest quantum computing breakthroughs 2025"

Pattern Library (T1): 2 results, avg 0.62
Web KB Cache (T2):    0 results (new topic)
Live Web (T3):        10 results, avg 0.71

Final top-15: 2×T1, 10×T3
```

## Checking Logs for Debugging

If you want to verify what happened behind the scenes, check the API logs:

```bash
tail -f /tmp/api_server.log | grep "Web search"
```

**Example logs**:

**Tier 2 (Web KB) hit, Tier 3 skipped**:
```
INFO: Web KB search returned 15 results for: "How does contextual retrieval..."
INFO: Web search check - enable_web_search=True, has_provider=True, mode=on_low_confidence
INFO: Web KB (Tier 2) has good results (0.826), skipping live web search (Tier 3)
INFO: Web search trigger decision: False (mode=on_low_confidence)
```

**Tier 3 (Live Web) triggered**:
```
INFO: Web KB search returned 0 results for: "latest quantum computing..."
INFO: Web search check - enable_web_search=True, has_provider=True, mode=parallel
INFO: Web search trigger decision: True (mode=parallel)
INFO: DuckDuckGo search returned 10 results for query: latest quantum computing...
INFO: Web search returned 10 results (mode: parallel, duration: 6.86s)
```

## API Response Structure

The tier breakdown comes from the `retrieval_stats` field in the API response:

```json
{
  "answer": "...",
  "sources": [...],
  "retrieved_docs": 10,
  "retrieval_stats": {
    "tier_1_results": 8,
    "tier_2_results": 2,
    "tier_3_results": 0,
    "cache_hit": true
  }
}
```

## Tips for Using Tier Display

1. **Check tier breakdown first** - Understand which sources contributed before reading the answer

2. **Look for T2/T3 badges** - If you see blue or purple badges, you're getting web-sourced information

3. **Switch to parallel mode for fresh info** - If you need the latest information, use parallel mode to force live web search

4. **Tier 3 = 0 is normal** - This usually means you're getting cached web results (T2) or high-quality pattern results (T1)

5. **Increase top_k for more variety** - If you want to see more web results, increase top_k to 15-20

## Files Modified

- `web-ui/src/lib/api.ts` - Added `RetrievalStats` interface and `retrieval_stats` to `QueryResponse`
- `web-ui/src/components/AnswerCard.tsx` - Added tier breakdown display
- `web-ui/src/components/SourcesList.tsx` - Added colored tier badges (T1/T2/T3) to sources

## Related Documentation

- [WEB_SEARCH_FIX_GUIDE.md](WEB_SEARCH_FIX_GUIDE.md) - Web search troubleshooting
- [guides/WEB_SEARCH_GUIDE.md](guides/WEB_SEARCH_GUIDE.md) - Web search configuration
- [implementation/web_enhancements.md](implementation/web_enhancements.md) - Technical details
