# Pattern Validator Skill

Validate and update existing RAG patterns based on latest research and benchmarks.

## Trigger
When user asks to:
- "validate patterns"
- "check pattern accuracy"
- "update pattern benchmarks"
- "verify pattern performance claims"
- Automatically: After research-monitor finds new papers

## Execution Steps

1. **Review Pattern Documentation**
   - Read all files in `docs/patterns/`
   - Extract performance claims (e.g., "+20% accuracy")
   - Identify citations and references
   - Check last update dates

2. **Compare Against Latest Research**
   - Query ChromaDB for relevant papers
   - Check if newer benchmarks exist
   - Validate performance claims
   - Identify contradictions or improvements

3. **Test Implementation Examples**
   - Verify code examples are runnable
   - Check API versions are current
   - Validate model names (e.g., claude-3-5-sonnet-20241022)
   - Ensure dependencies are available

4. **Update Outdated Content**
   - Refresh performance benchmarks
   - Update model versions
   - Add new implementation approaches
   - Include latest research references

5. **Flag Issues**
   - Outdated benchmarks
   - Deprecated APIs
   - Missing recent innovations
   - Inconsistent claims across patterns

6. **Generate Validation Report**
   - Patterns validated
   - Updates made
   - Issues requiring manual review
   - Recommended improvements

## Example Usage

```python
# Automatic trigger after research-monitor
1. New paper found: "Contextual Retrieval improves accuracy by 49%"
2. Scan patterns for "contextual" or "retrieval"
3. Find: basic-rag.md mentions "standard chunking"
4. Update: Add section on contextual retrieval as improvement
5. Add reference to Anthropic paper (Sept 2024)
6. Report: "Updated basic-rag.md with contextual retrieval option"
```

## Validation Checks

### Code Examples
- [ ] All imports are valid and available
- [ ] Model names are current (not deprecated)
- [ ] API versions are latest stable
- [ ] Code follows best practices
- [ ] Examples are runnable without errors

### Performance Claims
- [ ] Benchmarks cite sources
- [ ] Claims match latest research
- [ ] Comparisons are fair and accurate
- [ ] Improvements are quantified with ranges

### References
- [ ] arXiv links are valid
- [ ] Papers are from reputable sources
- [ ] Citations are properly formatted
- [ ] Research is recent (< 2 years preferred)

### Healthcare Compliance
- [ ] HIPAA considerations mentioned where relevant
- [ ] PHI handling is addressed
- [ ] BAA requirements documented
- [ ] Security best practices included

## Output Format

```markdown
## Pattern Validation Report - [Date]

### Patterns Validated: [N]

#### ✅ Up-to-Date Patterns: [N]
- basic-rag.md: All claims verified, code current
- contextual-retrieval.md: Matches Sept 2024 Anthropic research

#### ⚠️ Patterns Needing Updates: [N]
- hyde-rag.md:
  - Issue: Performance claim "+15%" vs latest research "+25%"
  - Action: Updated benchmark to 15-30% range
  - Source: arXiv:2024.xxxxx

- raptor-rag.md:
  - Issue: Code example uses deprecated API
  - Action: Updated to latest sklearn API
  - Source: sklearn 1.4 documentation

#### ❌ Critical Issues: [N]
- [pattern-name.md]:
  - Issue: Major contradiction with latest research
  - Recommendation: Manual review required
  - Details: [explanation]

### Code Examples Tested: [N/N] passed

### References Updated: [N]
- Added [N] new arXiv citations
- Removed [N] broken links
- Updated [N] outdated references

### Recommendations
- [ ] Add new pattern for [technique] from recent research
- [ ] Deprecate [old approach] in favor of [new approach]
- [ ] Benchmark [pattern] against latest baselines
```

## Implementation

See: `scripts/pattern_validator.py`
