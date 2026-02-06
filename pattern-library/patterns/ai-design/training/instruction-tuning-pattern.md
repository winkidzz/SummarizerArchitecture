# Instruction Tuning Pattern

## Overview
Instruction tuning trains a pre-trained LLM on a **diverse collection of tasks framed as instructions**, enabling the model to generalize to new, unseen instructions. While SFT focuses on a single task, instruction tuning covers dozens to thousands of task types — making the model a better general-purpose instruction follower.

## Training Phase
**Fine-Tuning (Mid-Training)** — transforms a base model into an instruction-following model

## How It Differs from SFT

| Aspect | SFT | Instruction Tuning |
|--------|-----|-------------------|
| Task scope | Single task or narrow domain | Hundreds to thousands of task types |
| Goal | Task-specific performance | General instruction following |
| Data | Domain-specific examples | Diverse instruction collections |
| Result | Specialist model | Generalist model |

## Key Concepts

### Training Data Format
```json
[
  {"instruction": "Summarize the following clinical note", "input": "...", "output": "..."},
  {"instruction": "Extract all medications from this text", "input": "...", "output": "..."},
  {"instruction": "Classify this condition as acute or chronic", "input": "...", "output": "..."},
  {"instruction": "Generate a differential diagnosis", "input": "...", "output": "..."},
  {"instruction": "Translate this medical term to lay language", "input": "...", "output": "..."}
]
```

### Notable Instruction Datasets
| Dataset | Tasks | Size | Notes |
|---------|-------|------|-------|
| FLAN Collection | 1,800+ tasks | 15M+ examples | Google, most comprehensive |
| Open Assistant | Conversation | 160K+ messages | Community-created |
| Alpaca | General instruction | 52K | Stanford, GPT-4 generated |
| Medical Meadow | Medical tasks | 160K+ | Multi-source medical instructions |
| PMC-LLaMA | Biomedical | 4.8M | PubMed-derived medical data |

## Healthcare Use Case
Instruction-tune a base model to handle diverse clinical tasks:
- Summarize patient records in various formats (SOAP, H&P, discharge)
- Extract structured data (medications, diagnoses, procedures, allergies)
- Answer clinical questions grounded in evidence
- Generate patient-friendly explanations of medical conditions
- Classify clinical documents by type and urgency

## Related Patterns
- [SFT Pattern](./sft-pattern.md) — Single-task version of fine-tuning
- [LoRA & PEFT](./lora-peft-pattern.md) — Efficient method for instruction tuning large models
- [Synthetic Data Generation](./synthetic-data-pattern.md) — Generate diverse instruction data

## References
- [Scaling Instruction-Finetuned Language Models (FLAN, 2022)](https://arxiv.org/abs/2210.11416)
- [Self-Instruct (Wang et al., 2023)](https://arxiv.org/abs/2212.10560)

## Version History
- **v1.0** (2026-02-05): Initial version
