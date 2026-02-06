# DPO (Direct Preference Optimization) Pattern

## Overview
DPO is a simpler, more stable alternative to RLHF that achieves alignment **without training a separate reward model or using reinforcement learning**. Instead, DPO directly optimizes the LLM on preference pairs (chosen vs. rejected responses) using a modified cross-entropy loss. It produces comparable results to RLHF at a fraction of the complexity and cost.

## Training Phase
**Post-Training (Alignment)** — applied after SFT to align with preferences

## How It Differs from RLHF

| Aspect | RLHF | DPO |
|--------|------|-----|
| Reward model | Separate model required | No reward model needed |
| RL training | PPO (complex, unstable) | Standard supervised training |
| Complexity | High (3-stage pipeline) | Low (single training stage) |
| Stability | Can be unstable, sensitive to hyperparameters | Stable, standard training dynamics |
| Cost | 3-5x SFT cost | 1.5-2x SFT cost |
| Quality | Slightly better for complex alignment | Comparable for most tasks |

## Training Data Format
```json
[
  {
    "prompt": "What medication should I take for a headache?",
    "chosen": "For mild headaches, over-the-counter options like acetaminophen or ibuprofen are commonly recommended. However, I'd suggest consulting your healthcare provider, especially if headaches are frequent or severe.",
    "rejected": "Take 800mg of ibuprofen every 4 hours. You can also try mixing aspirin with acetaminophen for maximum effect."
  }
]
```

## Implementation Examples

### TRL (Transformer Reinforcement Learning)
```python
from trl import DPOTrainer, DPOConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("clinical-sft-model")
ref_model = AutoModelForCausalLM.from_pretrained("clinical-sft-model")  # Frozen reference

dpo_config = DPOConfig(
    beta=0.1,  # KL divergence weight (lower = more change from reference)
    learning_rate=5e-7,
    num_train_epochs=1,
    per_device_train_batch_size=4,
    bf16=True,
)

trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=dpo_config,
    train_dataset=preference_dataset,
    tokenizer=tokenizer,
)
trainer.train()
```

## Healthcare Use Case
- Physicians create preference pairs: safe vs. unsafe medical responses
- Align model to always recommend physician consultation for serious symptoms
- Prefer cautious, hedged language over overconfident assertions
- Align with institutional treatment protocols

## Related Patterns
- [RLHF](./rlhf-pattern.md) — More complex alternative
- [SFT Pattern](./sft-pattern.md) — Prerequisite step before DPO
- [LoRA & PEFT](./lora-peft-pattern.md) — Can combine DPO with LoRA for efficient alignment

## References
- [Direct Preference Optimization: Your Language Model is Secretly a Reward Model (Rafailov et al., 2023)](https://arxiv.org/abs/2305.18290)
- [TRL DPO Trainer](https://huggingface.co/docs/trl/dpo_trainer)

## Version History
- **v1.0** (2026-02-05): Initial version
