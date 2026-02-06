# LoRA & Parameter-Efficient Fine-Tuning (PEFT) Pattern

## Overview
LoRA (Low-Rank Adaptation) and other PEFT methods fine-tune LLMs by training only a **small fraction of parameters** (0.1-5%) while freezing the rest. This dramatically reduces GPU memory requirements and training cost, making it possible to fine-tune large models on consumer hardware. LoRA is the **most popular fine-tuning method** in practice.

## Training Phase
**Fine-Tuning (Mid-Training)** — applied to a pre-trained or instruction-tuned model

## How LoRA Works

Instead of updating all model weights (billions of parameters), LoRA adds small trainable matrices (adapters) alongside the frozen original weights:

```
Original: W (frozen, billions of params)
LoRA:     W + BA (trainable, millions of params)
          where B is (d × r) and A is (r × d), r << d
```

- `r` (rank) is typically 8-64, compared to dimensions of 4096+
- Only B and A matrices are trained — the original model is unchanged
- At inference, adapters merge with original weights (zero additional latency)

## Key PEFT Methods

| Method | Trainable Params | Memory Reduction | Best For |
|--------|-----------------|------------------|----------|
| **LoRA** | 0.1-1% | 60-80% | General-purpose fine-tuning |
| **QLoRA** | 0.1-1% | 80-95% | Fine-tuning on consumer GPUs (4-bit base model) |
| **Prefix Tuning** | < 0.1% | 90%+ | Soft prompt optimization |
| **Adapters** | 1-5% | 50-70% | Modular task-specific adapters |
| **IA3** | < 0.01% | 95%+ | Extreme parameter efficiency |

## Key Parameters

| Parameter | Typical Range | Impact |
|-----------|--------------|--------|
| `r` (rank) | 8-64 | Higher = more capacity but more params |
| `alpha` | 16-128 | Scaling factor; usually 2× rank |
| `target_modules` | q_proj, v_proj | Which layers get LoRA adapters |
| `dropout` | 0.05-0.1 | Regularization for small datasets |

## Implementation Examples

### QLoRA with Hugging Face (Consumer GPU)
```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

# 4-bit quantized base model (fits on 24GB GPU)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="bfloat16",
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    quantization_config=bnb_config,
)
model = prepare_model_for_kbit_training(model)

# LoRA configuration
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
print(f"Trainable params: {model.print_trainable_parameters()}")
# Output: trainable params: 6,553,600 || all params: 8,030,261,248 || trainable%: 0.082%

trainer = SFTTrainer(
    model=model,
    train_dataset=clinical_dataset,
    max_seq_length=2048,
    args=training_args,
)
trainer.train()

# Save adapter (small file, ~25MB)
model.save_pretrained("clinical-lora-adapter")
```

## Performance Characteristics

| Model Size | Method | GPU Required | Training Time (10K examples) | Adapter Size |
|------------|--------|-------------|------------------------------|-------------|
| 7-8B | QLoRA | 1x RTX 4090 (24GB) | 1-3 hours | 20-50 MB |
| 13B | QLoRA | 1x A100 (40GB) | 2-6 hours | 30-80 MB |
| 70B | QLoRA | 1x A100 (80GB) | 8-24 hours | 100-300 MB |

## Healthcare Considerations

### Multi-Specialty Adapters
LoRA adapters are small and modular — train separate adapters for different specialties:
- `cardiology-adapter` — trained on cardiology notes and guidelines
- `oncology-adapter` — trained on oncology protocols
- `emergency-adapter` — trained on emergency department workflows
- Swap adapters at inference time based on clinical context

### HIPAA & Data Privacy
- LoRA adapters are small enough to train on-premises
- Base model stays unchanged — no risk of PHI leaking into base weights
- QLoRA makes training feasible on HIPAA-compliant workstations

## Related Patterns
- [SFT Pattern](./sft-pattern.md) — Full fine-tuning that LoRA replaces for efficiency
- [Instruction Tuning](./instruction-tuning-pattern.md) — Can use LoRA for efficient multi-task tuning
- [Federated Learning](./federated-learning-pattern.md) — LoRA adapters enable federated fine-tuning (share adapter weights, not data)

## References
- [LoRA: Low-Rank Adaptation of Large Language Models (Hu et al., 2021)](https://arxiv.org/abs/2106.09685)
- [QLoRA: Efficient Finetuning of Quantized LLMs (Dettmers et al., 2023)](https://arxiv.org/abs/2305.14314)
- [PEFT Library](https://huggingface.co/docs/peft/)

## Version History
- **v1.0** (2026-02-05): Initial version
