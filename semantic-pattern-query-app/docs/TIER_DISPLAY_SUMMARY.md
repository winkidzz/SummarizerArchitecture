# Tier Display Summary - UI Enhancement

## What Was Done

Enhanced the web UI to display **3-tier retrieval breakdown** with visual indicators, making it crystal clear which tiers contributed to each query result.

## The Problem

When you queried "What is RAG" and noted "i dont think it did the web search", the system WAS actually using web sources (Tier 2 - Web KB Cache), but this wasn't visible in the UI. The lack of transparency caused confusion about whether web search was working.

## The Solution

Added three new visual features to the UI:

### 1. Tier Breakdown Section

The Answer Card now shows a breakdown of results by tier:

```
3-Tier Retrieval Breakdown
┌─────────────────────────────┬─────────────────────────────┬─────────────────────────────┐
│ Tier 1 (Pattern Library)    │ Tier 2 (Web KB Cache)       │ Tier 3 (Live Web)           │
│ 8                            │ 2                           │ 0                           │
└─────────────────────────────┴─────────────────────────────┴─────────────────────────────┘
```

**This tells you**:
- 8 results from Pattern Library (your curated patterns)
- 2 results from Web KB Cache (previously fetched web results)
- 0 results from Live Web (fresh search was skipped because cached results were good)

### 2. Source Badges

Each source in the "Supporting documents" list now has a colored badge:

- **[T1]** Green - Pattern Library (most trusted)
- **[T2]** Blue - Web KB Cache (web-sourced, cached)
- **[T3]** Purple - Live Web Search (fresh web results)

### 3. Comprehensive Documentation

Created [UI_TIER_DISPLAY.md](UI_TIER_DISPLAY.md) explaining:
- How to interpret the tier breakdown
- When Tier 3 = 0 is normal and expected
- Difference between web search modes
- How to verify web search is working via logs

## Example Queries

### Query 1: "How does contextual retrieval reduce hallucinations?"

**Your observation**: "i dont think it did the web search"

**What actually happened**:
```
Tier 1 (Pattern Library): 8 results (avg score: 0.75)
Tier 2 (Web KB Cache):    2 results (avg score: 0.826) ← WEB SEARCH DID HAPPEN!
Tier 3 (Live Web):        0 results (skipped - T2 had excellent results)
```

**Why T3 = 0**: The system used "on_low_confidence" mode and found 2 high-quality cached web results in Tier 2 (0.826 avg score). Since the cache had good results, it didn't need to do a live web search (Tier 3), saving ~7 seconds of latency.

**New UI shows**: You'll now see 2 sources with blue **[T2]** badges, making it clear that web-sourced information WAS used.

### Query 2: "latest quantum computing breakthroughs 2025"

**Expected result**:
```
Tier 1 (Pattern Library): 2 results (not much in local patterns)
Tier 2 (Web KB Cache):    0 results (new topic, no cache)
Tier 3 (Live Web):        10 results ← FRESH WEB SEARCH!
```

**New UI shows**: You'll see 10 sources with purple **[T3]** badges, making it clear that fresh web search happened.

## Files Modified

### Frontend
1. **web-ui/src/lib/api.ts**
   - Added `RetrievalStats` interface
   - Extended `QueryResponse` to include `retrieval_stats`

2. **web-ui/src/components/AnswerCard.tsx**
   - Added tier breakdown section
   - Shows T1/T2/T3 counts only when tier data available

3. **web-ui/src/components/SourcesList.tsx**
   - Added colored tier badges (T1/T2/T3)
   - Green/Blue/Purple color scheme
   - Uses `source_type` or `layer` metadata

### Documentation
4. **docs/UI_TIER_DISPLAY.md**
   - Complete guide to understanding tier display
   - Examples and troubleshooting

5. **docs/TIER_DISPLAY_SUMMARY.md** (this file)
   - High-level summary of changes

## How to See It

1. Open the UI at http://localhost:5173
2. Query "How does contextual retrieval reduce hallucinations?"
3. Look for:
   - **Tier breakdown section** below "Documents retrieved" stats
   - **Colored badges** ([T1], [T2], [T3]) on each source

## Key Takeaways

1. **Tier 2 = 0 and Tier 3 = 0 is OK** - If Tier 1 (Pattern Library) has excellent results
2. **Tier 2 > 0 means web search happened** - Just using cached results instead of fresh search
3. **Tier 3 > 0 means live web search** - Fresh results from DuckDuckGo
4. **Use "parallel" mode to force Tier 3** - If you want fresh web results every time

## Benefits

### Before
- No visibility into which tiers contributed
- Confusion about whether web search worked
- Had to check logs to understand behavior

### After
- Clear tier breakdown in every response
- Visual badges show source reliability
- Easy to understand when/why live web search skipped
- No need to check logs for basic understanding

## Testing the Changes

The UI uses Vite's hot module replacement, so the changes should be live immediately. Just refresh the page if needed.

Try these queries to see different tier patterns:

1. **Mostly T1 (Pattern Library)**:
   - "What is RAPTOR RAG?"
   - "How does contextual retrieval work?"

2. **Mix of T1 and T2 (with web cache)**:
   - "What is Contextual Retrieval from Anthropic?"
   - "How does reranking improve RAG?"

3. **With T3 (live web)** - Switch to "parallel" mode:
   - "latest AI breakthroughs 2025"
   - "recent developments in RAG systems"

## Related Documentation

- [WEB_SEARCH_FIX_GUIDE.md](WEB_SEARCH_FIX_GUIDE.md) - Web search troubleshooting
- [UI_TIER_DISPLAY.md](UI_TIER_DISPLAY.md) - Detailed tier display guide
- [guides/WEB_SEARCH_GUIDE.md](guides/WEB_SEARCH_GUIDE.md) - Web search configuration
