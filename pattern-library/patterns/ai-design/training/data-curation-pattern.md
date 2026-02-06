# Data Curation for LLM Training Pattern

## Overview
Data curation for LLM training encompasses the strategies for selecting, cleaning, deduplicating, and balancing training data to maximize model quality. Data quality matters more than data quantity — a smaller, well-curated dataset consistently outperforms a larger, noisy one.

## Training Phase
**Pre-Training** — establishing data quality standards before any training begins

## Key Principles

| Principle | Description | Impact |
|-----------|-------------|--------|
| **Quality over quantity** | 1K expert-curated examples > 100K noisy examples | Direct quality improvement |
| **Diversity** | Cover diverse scenarios, formats, and edge cases | Better generalization |
| **Deduplication** | Remove exact and near-duplicate examples | Prevents overfitting |
| **Balance** | Proportional representation across categories | Reduces bias |
| **Recency** | Prioritize current guidelines and practices | Clinical accuracy |

## Healthcare Data Curation

### Data Sources
- De-identified clinical notes (discharge summaries, H&P, progress notes)
- Medical literature (PubMed, clinical guidelines)
- Medical Q&A datasets (MedQA, PubMedQA)
- Synthetic data from teacher models
- Expert physician annotations

### Quality Checks
- **Clinical accuracy**: Verified by domain experts
- **PHI screening**: Automated + manual de-identification verification
- **Completeness**: All required fields present
- **Consistency**: No contradictory examples
- **Recency**: Based on current clinical guidelines

## Related Patterns
- [SFT Pattern](./sft-pattern.md) — Consumes curated data
- [Synthetic Data Generation](./synthetic-data-pattern.md) — One source of curated data
- [Instruction Tuning](./instruction-tuning-pattern.md) — Requires diverse, curated task data

## References
- [Textbooks Are All You Need (Phi-1, 2023)](https://arxiv.org/abs/2306.11644)
- [The RefinedWeb Dataset for Falcon (2023)](https://arxiv.org/abs/2306.01116)

## Version History
- **v1.0** (2026-02-05): Initial version
