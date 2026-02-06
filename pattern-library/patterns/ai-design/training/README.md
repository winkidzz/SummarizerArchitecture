# Training Patterns

Patterns for training, fine-tuning, and aligning AI models — organized by the three phases of the training lifecycle.

---

## Pre-Training
Patterns for the initial training phase where models learn general capabilities from large datasets.

| Pattern | Description | Complexity |
|---------|-------------|------------|
| [Self-Supervised Learning](./self-supervised-learning-pattern.md) | Creates supervisory signals from unlabeled data; foundation for all modern LLMs | High |
| [Data Curation for LLM Training](./data-curation-pattern.md) | Quality, diversity, and deduplication strategies for pre-training data | Medium |

## Fine-Tuning (Mid-Training)
Patterns for adapting pre-trained models to specific tasks, domains, or behaviors.

### General Fine-Tuning
| Pattern | Description | Complexity |
|---------|-------------|------------|
| [Few-Shot Learning](./few-shot-learning-pattern.md) | Learning from 1-10 examples; leveraging in-context learning | Low |
| [Active Learning](./active-learning-pattern.md) | Selectively choosing the most informative examples for annotation | Medium |
| [Curriculum Learning](./curriculum-learning-pattern.md) | Training on progressively harder examples | Medium |
| [Continual Learning](./continual-learning-pattern.md) | Learning from new data without forgetting previous knowledge | High |
| [Meta-Learning](./meta-learning-pattern.md) | Learning to learn; adapting quickly to new tasks | High |
| [Federated Learning](./federated-learning-pattern.md) | Training across distributed datasets without centralizing data | High |

### LLM-Specific Fine-Tuning
| Pattern | Description | Complexity |
|---------|-------------|------------|
| [Supervised Fine-Tuning (SFT)](./sft-pattern.md) | Training LLMs on instruction-response pairs for task-specific behavior | Medium |
| [LoRA & Parameter-Efficient Fine-Tuning](./lora-peft-pattern.md) | Lightweight fine-tuning that trains only a small fraction of parameters | Medium |
| [Instruction Tuning](./instruction-tuning-pattern.md) | Teaching models to follow diverse instructions across many tasks | Medium-High |
| [Synthetic Data Generation](./synthetic-data-pattern.md) | Using LLMs to generate training data for fine-tuning other models | Medium |

## Post-Training (Alignment & Optimization)
Patterns for aligning model behavior with human preferences and optimizing for deployment.

| Pattern | Description | Complexity |
|---------|-------------|------------|
| [RLHF (Reinforcement Learning from Human Feedback)](./rlhf-pattern.md) | Aligning model outputs with human preferences via reward models | High |
| [DPO (Direct Preference Optimization)](./dpo-pattern.md) | Simpler alternative to RLHF that directly optimizes on preference pairs | Medium-High |

### Related Post-Training Patterns (in `performance/`)
These optimization patterns are applied after training to prepare models for deployment:
- [Quantization](../performance/quantization-pattern.md) — Reduce precision for faster, cheaper inference
- [Pruning](../performance/pruning-pattern.md) — Remove unnecessary weights
- [Knowledge Distillation](../performance/knowledge-distillation-pattern.md) — Train smaller student models

---

## Decision Framework: When to Use What

```
Is the pre-trained model good enough for your task?
├── Yes → Use as-is with prompt engineering (see framework/prompt-engineering-guide.md)
├── Close but needs domain adaptation → Fine-tune
│   ├── Small dataset (< 1K examples) → Few-Shot Learning or LoRA
│   ├── Medium dataset (1K-100K) → SFT or LoRA
│   ├── Large dataset (100K+) → Full fine-tuning or Instruction Tuning
│   └── No labeled data → Synthetic Data Generation → SFT
├── Model gives correct but poorly formatted outputs → SFT on format examples
├── Model gives factually correct but tonally wrong outputs → RLHF or DPO
├── Data is distributed across institutions → Federated Learning
└── Need to keep model current over time → Continual Learning
```

## Healthcare Training Considerations
- **Medical data scarcity**: Use synthetic data generation and few-shot learning
- **Multi-institution training**: Federated learning keeps PHI at each institution
- **Clinical accuracy alignment**: RLHF with physician feedback
- **Regulatory**: Document all training data, methods, and evaluation for FDA/HIPAA

## Contributing
When adding new training patterns:
1. Use the [pattern template](../../../templates/pattern-template.md)
2. Classify as Pre-Training, Fine-Tuning, or Post-Training
3. Update this README under the appropriate phase
