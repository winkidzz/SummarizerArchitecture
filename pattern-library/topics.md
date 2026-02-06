# AI/ML/LLM Topic Map

A comprehensive map of every major topic, concept, technique, architecture, and design pattern in the AI/ML/LLM landscape — organized by research area, with coverage status from the current pattern library.

> **Purpose**: This is the pattern library's **table of contents for ideation**. Use it to identify what to research next, spot gaps, and plan new pattern categories.

---

## Coverage Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | **Covered** — dedicated pattern or document exists |
| 🟡 | **Partially covered** — mentioned in other patterns but no dedicated document |
| ❌ | **Not covered** — gap in the library |
| 📁 | Indicates which folder currently houses the content |

---

## 1. Foundation Models & LLM Architecture

> The core building blocks of modern AI systems. Understanding these is prerequisite to everything else.

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| Transformer architecture | ✅ | 📁 `ai-design/model-architecture/` | `transformer-architecture-pattern.md` |
| Attention mechanisms | ✅ | 📁 `ai-design/model-architecture/` | `attention-mechanism-pattern.md` |
| Tokenization (BPE, SentencePiece, tiktoken) | ❌ | — | Fundamental but undocumented |
| Context windows (4K → 2M tokens) | 🟡 | 📁 `patterns/rag/` | `long-context-strategies.md` covers RAG use; no general LLM context guide |
| Model families (GPT, Claude, Gemini, Llama, Mistral) | 🟡 | 📁 `vendor-guides/` | Vendor guides cover Claude, Gemini, Azure OpenAI but not as model architecture comparisons |
| Mixture of Experts (MoE) | ❌ | — | Key architecture for Mixtral, Gemini, DBRX |
| State space models (Mamba, RWKV) | ❌ | — | Emerging alternative to transformers |
| Reasoning models (o1/o3 style, extended thinking) | ❌ | — | Test-time compute, chain-of-thought at inference |
| Diffusion models | ❌ | — | Image generation, emerging for text |
| Encoder vs. decoder vs. encoder-decoder | ❌ | — | BERT vs. GPT vs. T5 architecture choices |
| Position embeddings (RoPE, ALiBi) | ❌ | — | Key to long-context capability |
| Multi-head attention variants | 🟡 | 📁 `ai-design/model-architecture/` | Briefly covered in attention mechanism pattern |
| Model scaling laws (Chinchilla, Kaplan) | ❌ | — | Compute-optimal training decisions |

### Gap Assessment
**Major gap**: No dedicated section for LLM architecture fundamentals. The `ai-design/model-architecture/` folder covers general ML architectures (ensemble, transfer learning) but lacks LLM-specific content like MoE, scaling laws, tokenization, and modern architecture variants.

---

## 2. Training & Fine-Tuning

> How models learn — from pre-training through domain adaptation.

### 2a. General ML Training (Currently in `ai-design/training/`)

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| Transfer learning | ✅ | 📁 `ai-design/model-architecture/` | `transfer-learning-pattern.md` |
| Few-shot learning | ✅ | 📁 `ai-design/training/` | `few-shot-learning-pattern.md` |
| Active learning | ✅ | 📁 `ai-design/training/` | `active-learning-pattern.md` |
| Curriculum learning | ✅ | 📁 `ai-design/training/` | `curriculum-learning-pattern.md` |
| Federated learning | ✅ | 📁 `ai-design/training/` | `federated-learning-pattern.md` |
| Self-supervised learning | ✅ | 📁 `ai-design/training/` | `self-supervised-learning-pattern.md` |
| Meta-learning | ✅ | 📁 `ai-design/training/` | `meta-learning-pattern.md` |
| Continual/lifelong learning | ✅ | 📁 `ai-design/training/` | `continual-learning-pattern.md` |
| Multi-task learning | ✅ | 📁 `ai-design/model-architecture/` | `multi-task-learning-pattern.md` |
| Ensemble methods | ✅ | 📁 `ai-design/model-architecture/` | `ensemble-pattern.md` |

### 2b. LLM-Specific Fine-Tuning

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| Supervised Fine-Tuning (SFT) | ✅ | 📁 `ai-design/training/` | `sft-pattern.md` — HuggingFace + Vertex AI implementations |
| RLHF (Reinforcement Learning from Human Feedback) | ✅ | 📁 `ai-design/training/` | `rlhf-pattern.md` — 3-step process, healthcare annotation |
| DPO (Direct Preference Optimization) | ✅ | 📁 `ai-design/training/` | `dpo-pattern.md` — TRL implementation, preference pairs |
| RLAIF (RL from AI Feedback) | ❌ | — | Constitutional AI, scalable alignment |
| LoRA (Low-Rank Adaptation) | ✅ | 📁 `ai-design/training/` | `lora-peft-pattern.md` — LoRA, QLoRA, adapter comparison |
| QLoRA (Quantized LoRA) | ✅ | 📁 `ai-design/training/` | Covered in `lora-peft-pattern.md` — 70B on 24GB GPU |
| Adapter tuning | 🟡 | 📁 `ai-design/training/` | Mentioned in `lora-peft-pattern.md` PEFT comparison table |
| Instruction tuning | ✅ | 📁 `ai-design/training/` | `instruction-tuning-pattern.md` — FLAN, Medical Meadow datasets |
| Model merging / Model soups | ❌ | — | Combining fine-tuned models |
| Synthetic data generation for training | ✅ | 📁 `ai-design/training/` | `synthetic-data-pattern.md` — Self-Instruct, Evol-Instruct |
| Data curation for LLM training | ✅ | 📁 `ai-design/training/` | `data-curation-pattern.md` — quality, diversity, deduplication |
| Embedding model fine-tuning | 🟡 | 📁 `patterns/rag-pipeline/` | Mentioned in `embedding-model-selection.md` and `vectorization-strategies.md` |
| Reranker fine-tuning | 🟡 | 📁 `patterns/rag/` | Mentioned in `reranking-rag.md` |

### Gap Assessment
**Well covered**: 7 new LLM-specific training patterns now cover the core techniques (SFT, LoRA/QLoRA, RLHF, DPO, instruction tuning, synthetic data, data curation). Organized by training phase: pre-training, fine-tuning (mid-training), post-training (alignment). See `ai-design/training/README.md` for the full lifecycle. Remaining gaps: RLAIF, model merging.

---

## 3. Prompt Engineering & In-Context Learning

> How to effectively communicate with LLMs without changing model weights.

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| Prompt engineering (general) | ✅ | 📁 `framework/` | `prompt-engineering-guide.md` — comprehensive guide with healthcare examples |
| Zero-shot prompting | ✅ | 📁 `framework/` | Covered in `prompt-engineering-guide.md` |
| Few-shot prompting / in-context learning | ✅ | 📁 `framework/` | Covered in `prompt-engineering-guide.md` with clinical examples |
| Chain-of-thought (CoT) prompting | ✅ | 📁 `framework/` | Covered in `prompt-engineering-guide.md` — medical reasoning examples |
| Tree-of-thought (ToT) | ✅ | 📁 `framework/` | Covered in `prompt-engineering-guide.md` — differential diagnosis |
| Self-consistency | ✅ | 📁 `framework/` | Covered in `prompt-engineering-guide.md` — clinical classification |
| ReAct prompting | ✅ | 📁 `framework/`, `patterns/agents/` | Guide + `react-pattern.md` |
| System prompts / persona design | ✅ | 📁 `framework/` | Covered in `prompt-engineering-guide.md` — healthcare system prompt anatomy |
| Prompt templates & chaining | 🟡 | 📁 `framework/` | Templates table in guide; no dedicated chaining pattern |
| Structured output / JSON mode | ✅ | 📁 `framework/` | Covered in `prompt-engineering-guide.md` — JSON, XML techniques |
| Prompt optimization (DSPy, AutoPrompt) | 🟡 | 📁 `framework/` | Mentioned in prompt optimization section |
| Least-to-most prompting | ❌ | — | Decompose and solve progressively |
| Retrieval-augmented prompting | 🟡 | 📁 `patterns/rag/` | Core of all RAG patterns but not isolated as a technique |
| Prompt injection defense | 🟡 | 📁 `framework/glossary.md`, `ai-design/security/` | Mentioned in glossary and adversarial defense |
| Prompt caching | 🟡 | 📁 `vendor-guides/`, `framework/` | Mentioned in Anthropic guide and LLMOps guide |

### Gap Assessment
**Well covered**: New `prompt-engineering-guide.md` covers 10+ techniques with healthcare-specific examples, system prompt design, structured output, and a prompt vs. fine-tune vs. RAG decision framework. Minor gaps: least-to-most prompting, dedicated prompt chaining pattern.

---

## 4. RAG — Retrieval-Augmented Generation

> Retrieval architecture strategies for grounding LLM responses in factual data.

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| Basic RAG | ✅ | 📁 `patterns/rag/` | `basic-rag.md` |
| Advanced RAG (multi-step) | ✅ | 📁 `patterns/rag/` | `advanced-rag.md` |
| Self-RAG (self-reflective) | ✅ | 📁 `patterns/rag/` | `self-rag.md` |
| Hybrid RAG (vector + keyword) | ✅ | 📁 `patterns/rag/` | `hybrid-rag.md` |
| Agentic RAG | ✅ | 📁 `patterns/rag/` | `agentic-rag.md` |
| Adaptive RAG | ✅ | 📁 `patterns/rag/` | `adaptive-rag.md` |
| Graph RAG | ✅ | 📁 `patterns/rag/` | `graph-rag.md` |
| Corrective RAG | ✅ | 📁 `patterns/rag/` | `corrective-rag.md` |
| Multi-Query RAG | ✅ | 📁 `patterns/rag/` | `multi-query-rag.md` |
| Parent-Child RAG | ✅ | 📁 `patterns/rag/` | `parent-child-rag.md` |
| Streaming RAG | ✅ | 📁 `patterns/rag/` | `streaming-rag.md` |
| Reranking RAG | ✅ | 📁 `patterns/rag/` | `reranking-rag.md` |
| HyDE RAG | ✅ | 📁 `patterns/rag/` | `hyde-rag.md` |
| RAPTOR RAG | ✅ | 📁 `patterns/rag/` | `raptor-rag.md` |
| Compressed RAG | ✅ | 📁 `patterns/rag/` | `compressed-rag.md` |
| Modular RAG | ✅ | 📁 `patterns/rag/` | `modular-rag.md` |
| Recursive RAG | ✅ | 📁 `patterns/rag/` | `recursive-rag.md` |
| Small-to-Big RAG | ✅ | 📁 `patterns/rag/` | `small-to-big-rag.md` |
| Contextual Retrieval | ✅ | 📁 `patterns/rag/` | `contextual-retrieval.md` |
| Long Context Strategies | ✅ | 📁 `patterns/rag/` | `long-context-strategies.md` |
| Query Routing | ✅ | 📁 `patterns/rag/` | `query-routing.md` |
| Medical RAG | ✅ | 📁 `patterns/rag/` | `medical-rag.md` |
| Local/Privacy RAG | ✅ | 📁 `patterns/rag/` | `local-rag.md` |
| Multi-Modal RAG | ✅ | 📁 `patterns/rag/` | `multi-modal-rag.md` |

### Gap Assessment
**Well covered** — 24 patterns is comprehensive. Minor gaps: no dedicated pattern for RAG fusion techniques (RRF, CC), no pattern for late-interaction models (ColBERT), no pattern for learned sparse retrieval (SPLADE).

---

## 5. RAG Pipeline Engineering

> The infrastructure that powers RAG retrieval — ingestion through evaluation.

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| Source connectors | ✅ | 📁 `patterns/rag-pipeline/` | `source-connector-patterns.md` |
| Document extraction | ✅ | 📁 `patterns/rag-pipeline/` | `document-extraction-patterns.md` |
| Chunking strategies | ✅ | 📁 `patterns/rag-pipeline/` | `chunking-strategies.md` |
| Embedding model selection | ✅ | 📁 `patterns/rag-pipeline/` | `embedding-model-selection.md` |
| Vectorization strategies | ✅ | 📁 `patterns/rag-pipeline/` | `vectorization-strategies.md` |
| Vector database selection | ✅ | 📁 `patterns/rag-pipeline/` | `vector-database-selection.md` |
| Index architecture (HNSW, IVF) | ✅ | 📁 `patterns/rag-pipeline/` | `index-architecture-patterns.md` |
| Index freshness | ✅ | 📁 `patterns/rag-pipeline/` | `index-freshness-patterns.md` |
| Pipeline orchestration | ✅ | 📁 `patterns/rag-pipeline/` | `pipeline-orchestration-patterns.md` |
| RAG evaluation | ✅ | 📁 `patterns/rag-pipeline/` | `rag-evaluation-patterns.md` |
| RAG-specific fine-tuning (RA-DIT, RETRO) | ❌ | — | Cross-cutting: pipeline + training |
| Metadata enrichment strategies | 🟡 | — | Mentioned in extraction/chunking but no dedicated pattern |
| Query transformation / rewriting | 🟡 | 📁 `patterns/rag/` | Covered in advanced-rag and multi-query-rag, not as pipeline pattern |

### Gap Assessment
**Well covered** — 10 patterns is a solid foundation. Minor gaps: RAG-specific training techniques (RA-DIT, RETRO), metadata enrichment as standalone pattern, query transformation pipeline.

---

## 6. Agents & Agentic AI

> Autonomous AI systems that use tools, plan, and take actions.

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| Tool use / function calling | ✅ | 📁 `patterns/agents/` | `tool-use-pattern.md` — ADK, Anthropic, LangChain implementations |
| ReAct pattern (reason + act) | ✅ | 📁 `patterns/agents/` | `react-pattern.md` — clinical trace example (warfarin+amiodarone) |
| Plan-and-execute agents | ✅ | 📁 `patterns/agents/` | `plan-and-execute-pattern.md` — LangGraph, prior auth use case |
| Multi-agent systems / swarms | ✅ | 📁 `patterns/agents/` | `multi-agent-pattern.md` — supervisor, peer-to-peer, pipeline topologies |
| Agent orchestration frameworks | ✅ | 📁 `patterns/agents/` | `agent-frameworks-pattern.md` — ADK, LangGraph, CrewAI, AutoGen, Claude Agent SDK |
| Agent memory (short/long-term, episodic) | ✅ | 📁 `patterns/agents/` | `agent-memory-pattern.md` — working, conversation, long-term, episodic, semantic |
| Agent evaluation & benchmarks | ✅ | 📁 `patterns/agents/` | `agent-evaluation-pattern.md` — 7 dimensions, SWE-bench, safety metrics |
| Human-in-the-loop patterns | ✅ | 📁 `patterns/agents/` | Covered in `agent-guardrails-pattern.md` — HITL patterns |
| Code execution / interpreter agents | ❌ | — | Running code as an action |
| Browser/computer use agents | ❌ | — | Interacting with UIs |
| Agentic RAG | ✅ | 📁 `patterns/rag/` | `agentic-rag.md` — RAG-specific agent usage |
| Agent guardrails / safety | ✅ | 📁 `patterns/agents/` | `agent-guardrails-pattern.md` — input/action/output/rate layers |
| Agent design patterns (delegation, routing, handoff) | ✅ | 📁 `patterns/agents/` | Covered across multi-agent and frameworks patterns |
| MCP (Model Context Protocol) | 🟡 | 📁 `patterns/agents/` | Mentioned in tool-use and frameworks patterns |

### Gap Assessment
**Well covered**: New `patterns/agents/` folder with 8 dedicated patterns covering core capabilities (tool use, ReAct), orchestration (plan-and-execute, multi-agent, frameworks), memory, guardrails, and evaluation. Minor gaps: dedicated code execution agent pattern, browser/computer use agents, standalone MCP pattern.

---

## 7. Knowledge & Memory Systems

> How AI systems store, retrieve, and reason over knowledge.

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| Knowledge graphs | 🟡 | 📁 `patterns/rag/` | `graph-rag.md` covers graph-based RAG but not KG construction |
| Vector databases | ✅ | 📁 `patterns/rag-pipeline/` | `vector-database-selection.md` |
| Semantic search | ✅ | 📁 `patterns/rag/` | Core of all RAG patterns |
| Entity extraction / NER | ❌ | — | Key for clinical NLP (medications, diagnoses, procedures) |
| Ontologies (SNOMED CT, LOINC, ICD-10) | 🟡 | 📁 `framework/glossary.md` | Defined in glossary, not documented as patterns |
| Conversation memory | ❌ | — | Chat history management |
| Long-term memory persistence | ❌ | — | Cross-session knowledge retention |
| Knowledge graph construction | ❌ | — | Building KGs from unstructured data |
| Taxonomy / classification systems | ❌ | — | Organizing domain knowledge |

### Gap Assessment
**Moderate gap**: Vector databases and semantic search are well covered through RAG. Missing: standalone knowledge graph construction, entity extraction (critical for healthcare NLP), conversation memory management.

---

## 8. Inference Optimization & Model Serving

> Making models fast, cheap, and reliable in production.

### 8a. Model Optimization (Partially in `ai-design/performance/`)

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| Quantization (GPTQ, AWQ, GGUF) | ✅ | 📁 `ai-design/performance/` | `quantization-pattern.md` |
| Pruning | ✅ | 📁 `ai-design/performance/` | `pruning-pattern.md` |
| Knowledge distillation | ✅ | 📁 `ai-design/performance/` | `knowledge-distillation-pattern.md` |
| Model optimization (general) | ✅ | 📁 `ai-design/performance/` | `model-optimization-pattern.md` |
| Caching (general) | ✅ | 📁 `ai-design/performance/` | `caching-pattern.md` |
| Batching | ✅ | 📁 `ai-design/performance/` | `batching-pattern.md` |
| Async processing | ✅ | 📁 `ai-design/performance/` | `async-processing-pattern.md` |

### 8b. LLM-Specific Serving (NOT COVERED)

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| LLM serving frameworks (vLLM, TGI, Triton) | ❌ | — | Core production infrastructure |
| Speculative decoding | ❌ | — | Draft model + verify for speed |
| KV cache optimization | ❌ | — | Memory management for long contexts |
| Continuous batching | ❌ | — | Dynamic batching for throughput |
| Model parallelism (tensor, pipeline, data) | ❌ | — | Distributing large models across GPUs |
| Prompt caching (Anthropic, etc.) | 🟡 | 📁 `vendor-guides/` | Mentioned in vendor guides |
| Semantic caching | ❌ | — | Cache by meaning, not exact match |
| Serverless LLM inference | ❌ | — | Lambda, Cloud Functions for LLM |
| GPU infrastructure (CUDA, ROCm) | ❌ | — | Hardware layer |
| On-device inference (Ollama, llama.cpp) | 🟡 | 📁 `patterns/rag/` | `local-rag.md` covers on-device RAG |
| LLM gateway / proxy (LiteLLM, AI Gateway) | ❌ | — | Multi-model routing and management |

### Gap Assessment
**Major gap**: General ML optimization is well covered (7 patterns), but LLM-specific serving infrastructure is entirely absent. vLLM, speculative decoding, KV cache, and continuous batching are critical for production LLM systems.

---

## 9. Evaluation & Benchmarks

> Measuring whether AI systems work correctly.

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| RAG evaluation (RAGAS, DeepEval) | ✅ | 📁 `patterns/rag-pipeline/` | `rag-evaluation-patterns.md` |
| LLM benchmarks (MMLU, HumanEval, etc.) | ❌ | — | Standard LLM capability measurement |
| LLM-as-judge evaluation | 🟡 | 📁 `patterns/rag-pipeline/` | Mentioned in RAG evaluation |
| Red teaming | ❌ | — | Adversarial testing for safety |
| Bias evaluation | ❌ | — | Fairness and bias measurement |
| Human evaluation protocols | ❌ | — | Systematic human judgment |
| Clinical accuracy evaluation | 🟡 | 📁 `patterns/rag/` | Mentioned in medical-rag but no standalone guide |
| Safety evaluation | ❌ | — | Harm, toxicity, refusal testing |
| Agent evaluation (SWE-bench) | ❌ | — | Measuring agent capabilities |
| Automated evaluation pipelines | 🟡 | 📁 `patterns/rag-pipeline/` | Pipeline evaluation covered |
| A/B testing for AI | ✅ | 📁 `ai-design/deployment/` | `ab-testing-pattern.md` |

### Gap Assessment
**Moderate gap**: RAG evaluation and A/B testing are covered. Missing: general LLM evaluation, red teaming, bias testing, clinical accuracy frameworks. Important for healthcare where accuracy is safety-critical.

---

## 10. Safety, Alignment & Responsible AI

> Ensuring AI systems are safe, aligned, and ethical.

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| Adversarial defense | ✅ | 📁 `ai-design/security/` | `adversarial-defense-pattern.md` |
| Differential privacy | ✅ | 📁 `ai-design/security/` | `differential-privacy-pattern.md` |
| Homomorphic encryption | ✅ | 📁 `ai-design/security/` | `homomorphic-encryption-pattern.md` |
| Privacy-preserving ML | ✅ | 📁 `ai-design/security/` | `privacy-preserving-ml-pattern.md` |
| Secure MPC | ✅ | 📁 `ai-design/security/` | `secure-mpc-pattern.md` |
| Model watermarking | ✅ | 📁 `ai-design/security/` | `model-watermarking-pattern.md` |
| Guardrails / content filtering | ✅ | 📁 `patterns/agents/` | `agent-guardrails-pattern.md` — input/action/output/rate guardrail layers |
| Prompt injection defense | 🟡 | 📁 `framework/glossary.md` | Defined but no dedicated pattern |
| Jailbreak prevention | ❌ | — | Model exploitation defense |
| Bias mitigation | ❌ | — | Fairness in model outputs |
| Toxicity detection | ❌ | — | Harmful content filtering |
| Constitutional AI | ❌ | — | Self-alignment via principles |
| RLHF / alignment techniques | ✅ | 📁 `ai-design/training/` | `rlhf-pattern.md`, `dpo-pattern.md` — See Section 2b |
| AI Act / regulation compliance | ❌ | — | EU AI Act, FDA, regulatory frameworks |
| Responsible AI frameworks | ❌ | — | Ethics, transparency, accountability |
| Hallucination detection & mitigation | 🟡 | 📁 `patterns/rag/` | Core motivation for RAG but no standalone pattern |

### Gap Assessment
**Moderate gap**: Cryptographic security and privacy are well covered (6 patterns). Missing: runtime safety (guardrails, prompt injection, content filtering), alignment, ethics, regulation. For healthcare, hallucination detection and regulatory compliance are critical.

---

## 11. Multimodal AI

> AI systems that process and generate across multiple modalities.

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| Multi-modal RAG | ✅ | 📁 `patterns/rag/` | `multi-modal-rag.md` |
| Vision-language models | 🟡 | 📁 `vendor-guides/` | Mentioned in vendor capabilities |
| Medical imaging AI | 🟡 | 📁 `patterns/rag/` | Mentioned in multi-modal-rag and medical-rag |
| Document understanding / OCR | ✅ | 📁 `patterns/rag-pipeline/` | `document-extraction-patterns.md` |
| Image generation (Stable Diffusion, DALL-E) | ❌ | — | Not relevant to healthcare summarization |
| Audio/speech (Whisper, TTS) | 🟡 | 📁 `patterns/rag-pipeline/` | Mentioned in extraction patterns |
| Video understanding | 🟡 | 📁 `patterns/rag/` | Mentioned in multi-modal-rag |
| Cross-modal retrieval | ❌ | — | Text-to-image, image-to-text search |
| CLIP / vision embeddings | ❌ | — | Vision-language alignment models |

### Gap Assessment
**Acceptable for scope**: Multi-modal RAG and document extraction cover the primary healthcare needs. Image generation and video understanding are less relevant to healthcare summarization. CLIP/vision embeddings could be useful for medical imaging retrieval.

---

## 12. Data Engineering for AI

> Preparing, managing, and governing data for AI systems.

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| Data pipelines | 🟡 | 📁 `patterns/rag-pipeline/` | RAG pipeline covers data flow; no general data engineering |
| Data quality & validation | 🟡 | 📁 `ai-design/monitoring/` | `data-quality-monitoring-pattern.md` monitors but doesn't cover data engineering |
| Data labeling & annotation | ❌ | — | Critical for fine-tuning |
| Synthetic data generation | ❌ | — | LLM-generated training data |
| Data versioning (DVC) | ❌ | — | Listed in AI design README but no pattern file exists |
| Feature stores | ❌ | — | Listed in AI design README but no pattern file exists |
| Data lineage | ❌ | — | Listed in AI design README but no pattern file exists |
| Feature engineering | ❌ | — | Listed in AI design README but no pattern file exists |
| Data augmentation | ❌ | — | Listed in AI design README but no pattern file exists |
| Data governance | 🟡 | 📁 `ai-design/mlops/` | `model-governance-pattern.md` touches on it |
| De-identification / anonymization | 🟡 | 📁 `patterns/rag/`, `framework/` | Mentioned in medical-rag, security best practices |
| Healthcare data standards (FHIR, HL7) | ✅ | 📁 `framework/` | `healthcare-data-patterns.md` |

### Gap Assessment
**Significant gap**: The `ai-design/README.md` lists 7 "Data Patterns" (Feature Store, Data Pipeline, Data Validation, Data Versioning, Data Lineage, Feature Engineering, Data Augmentation) but **none of these pattern files actually exist**. This is the library's biggest case of documented-but-not-implemented content.

---

## 13. MLOps & LLMOps

> Operating ML/LLM systems in production.

### 13a. MLOps (Covered in `ai-design/mlops/`)

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| CI/CD for ML | ✅ | 📁 `ai-design/mlops/` | `cicd-for-ml-pattern.md` |
| Model registry | ✅ | 📁 `ai-design/mlops/` | `model-registry-pattern.md` |
| Experiment tracking | ✅ | 📁 `ai-design/mlops/` | `experiment-tracking-pattern.md` |
| Model monitoring | ✅ | 📁 `ai-design/mlops/` | `model-monitoring-pattern.md` |
| Model retraining | ✅ | 📁 `ai-design/mlops/` | `model-retraining-pattern.md` |
| Pipeline orchestration | ✅ | 📁 `ai-design/mlops/` | `pipeline-orchestration-pattern.md` |
| Model governance | ✅ | 📁 `ai-design/mlops/` | `model-governance-pattern.md` |

### 13b. LLMOps

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| Prompt management / versioning | ✅ | 📁 `framework/` | `llmops-guide.md` — prompt versioning, config format, testing pipeline |
| LLM cost management | ✅ | 📁 `framework/` | `llmops-guide.md` — token economics, model routing, semantic caching |
| LLM observability (LangSmith, Langfuse) | ✅ | 📁 `framework/` | `llmops-guide.md` — observability stack comparison, trace dimensions |
| LLM gateway management (LiteLLM) | ✅ | 📁 `framework/` | `llmops-guide.md` — LiteLLM, Portkey, AI Gateway comparison |
| Fine-tune vs. prompt vs. RAG decision framework | ✅ | 📁 `framework/` | `prompt-engineering-guide.md` — decision tree and comparison table |
| LLM testing patterns | ✅ | 📁 `framework/` | `llmops-guide.md` — 6 test categories, evaluation framework |
| LLM rate limiting & throttling | ✅ | 📁 `framework/` | `llmops-guide.md` — per-provider rate limiting |
| Prompt injection monitoring | 🟡 | 📁 `framework/` | Mentioned in LLMOps healthcare compliance section |

### Gap Assessment
**Well covered**: New `llmops-guide.md` covers prompt management, cost optimization, observability, reliability, testing, CI/CD, and healthcare-specific compliance. Minor gap: dedicated prompt injection monitoring pattern.

---

## 14. Deployment & Infrastructure

> Getting AI systems into production and keeping them there.

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| A/B testing | ✅ | 📁 `ai-design/deployment/` | `ab-testing-pattern.md` |
| Canary deployment | ✅ | 📁 `ai-design/deployment/` | `canary-deployment-pattern.md` |
| Blue-green deployment | ✅ | 📁 `ai-design/deployment/` | `blue-green-deployment-pattern.md` |
| Edge deployment | ✅ | 📁 `ai-design/deployment/` | `edge-deployment-pattern.md` |
| Model serving | ✅ | 📁 `ai-design/deployment/` | `model-serving-pattern.md` |
| Model versioning | ✅ | 📁 `ai-design/deployment/` | `model-versioning-pattern.md` |
| Batch prediction | ✅ | 📁 `ai-design/deployment/` | `batch-prediction-pattern.md` |
| Real-time prediction | ✅ | 📁 `ai-design/deployment/` | `real-time-prediction-pattern.md` |
| Deployment archetypes (zonal, regional, multi) | ✅ | 📁 `framework/` | `deployment-guide.md` |
| GPU infrastructure | ❌ | — | Hardware selection, CUDA, multi-GPU |
| Container orchestration (K8s for AI) | ❌ | — | K8s operators for ML workloads |
| Auto-scaling for AI workloads | ❌ | — | Scaling based on inference load |

### Gap Assessment
**Well covered**: 8 deployment patterns + deployment guide. Minor gaps in GPU infrastructure and AI-specific container orchestration.

---

## 15. Integration & System Design

> Connecting AI into existing systems and architectures.

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| API Gateway | ✅ | 📁 `ai-design/integration/` | `api-gateway-pattern.md` |
| Microservices | ✅ | 📁 `ai-design/integration/` | `microservices-pattern.md` |
| Event-driven | ✅ | 📁 `ai-design/integration/` | `event-driven-pattern.md` |
| Service mesh | ✅ | 📁 `ai-design/integration/` | `service-mesh-pattern.md` |
| API-first | ✅ | 📁 `ai-design/integration/` | `api-first-pattern.md` |
| GraphQL | ✅ | 📁 `ai-design/integration/` | `graphql-pattern.md` |
| EHR integration (FHIR, HL7) | ✅ | 📁 `framework/` | `healthcare-data-patterns.md` |
| Webhook patterns | 🟡 | 📁 `patterns/rag-pipeline/` | Mentioned in source connectors |
| Message queue patterns (Kafka, Pub/Sub) | 🟡 | — | Mentioned in various patterns |

### Gap Assessment
**Well covered**: 6 integration patterns + healthcare data patterns. Solid for current scope.

---

## 16. Monitoring & Observability

> Watching AI systems in production.

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| Drift detection | ✅ | 📁 `ai-design/monitoring/` | `drift-detection-pattern.md` |
| Anomaly detection | ✅ | 📁 `ai-design/monitoring/` | `anomaly-detection-pattern.md` |
| Performance monitoring | ✅ | 📁 `ai-design/monitoring/` | `performance-monitoring-pattern.md` |
| Data quality monitoring | ✅ | 📁 `ai-design/monitoring/` | `data-quality-monitoring-pattern.md` |
| Model performance tracking | ✅ | 📁 `ai-design/monitoring/` | `model-performance-tracking-pattern.md` |
| Alerting | ✅ | 📁 `ai-design/monitoring/` | `alerting-pattern.md` |
| LLM-specific observability | ❌ | — | Token usage, prompt/completion tracing, cost tracking |
| RAG pipeline monitoring | 🟡 | 📁 `patterns/rag-pipeline/` | Mentioned in orchestration and evaluation |

### Gap Assessment
**Well covered** for general ML. Missing LLM-specific observability (token tracing, cost per query, prompt analysis).

---

## 17. Explainability & Interpretability

> Understanding why AI makes the decisions it does.

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| XAI (general) | ✅ | 📁 `ai-design/explainability/` | `xai-pattern.md` |
| SHAP/LIME | ✅ | 📁 `ai-design/explainability/` | `shap-lime-pattern.md` |
| Feature importance | ✅ | 📁 `ai-design/explainability/` | `feature-importance-pattern.md` |
| Attention visualization | ✅ | 📁 `ai-design/explainability/` | `attention-visualization-pattern.md` |
| Model interpretability | ✅ | 📁 `ai-design/explainability/` | `model-interpretability-pattern.md` |
| Counterfactual explanations | ✅ | 📁 `ai-design/explainability/` | `counterfactual-explanation-pattern.md` |
| LLM explanation techniques | ❌ | — | Chain-of-thought as explanation, self-explanation |
| Citation / source attribution for RAG | 🟡 | 📁 `patterns/rag/` | Mentioned in multiple RAG patterns |

### Gap Assessment
**Well covered** for traditional ML. Minor gap in LLM-specific explanation techniques.

---

## 18. Healthcare & Domain-Specific AI

> The primary vertical focus of this library.

| Topic | Coverage | Location | Notes |
|-------|----------|----------|-------|
| Patient record summarization | ✅ | 📁 `use-cases/` | `patient-record-summarization.md` |
| Clinical note generation (SOAP) | ✅ | 📁 `use-cases/` | `clinical-note-generation.md` |
| Real-time clinical monitoring | ✅ | 📁 `use-cases/` | `real-time-clinical-data.md` |
| Medical RAG | ✅ | 📁 `patterns/rag/` | `medical-rag.md` |
| Healthcare data patterns (FHIR, HL7) | ✅ | 📁 `framework/` | `healthcare-data-patterns.md` |
| Healthcare development lifecycle | ✅ | 📁 `framework/` | `healthcare-development-lifecycle.md` |
| HIPAA security | ✅ | 📁 `framework/` | `security-best-practices.md` |
| Vendor selection for healthcare | ✅ | 📁 `framework/` | `vendor-selection-guide.md` |
| Clinical NLP (NER, medical coding) | 🟡 | 📁 `framework/glossary.md` | MedCAT, scispaCy mentioned but no dedicated pattern |
| Medical imaging AI | 🟡 | 📁 `patterns/rag/` | Mentioned in multi-modal-rag |
| Drug interaction / pharmacovigilance | ❌ | — | Safety-critical use case |
| Clinical trial optimization | ❌ | — | Use case for healthcare AI |
| Diagnostic AI / clinical decision support | ❌ | — | Beyond summarization |
| De-identification / PHI masking | 🟡 | 📁 `framework/`, `patterns/rag/` | Mentioned but no standalone pattern |

### Gap Assessment
**Well covered** for summarization use cases. Potential expansion: clinical NLP as standalone pattern, de-identification as standalone pattern, diagnostic AI use cases.

---

## Summary: Gap Priority Matrix

### Tier 1 — Previously Critical Gaps (NOW ADDRESSED ✅)

| Gap | Status | What Was Done |
|-----|--------|---------------|
| **Agents & Agentic AI** | ✅ Covered | `patterns/agents/` — 8 patterns (tool use, ReAct, plan-and-execute, multi-agent, frameworks, memory, guardrails, evaluation) |
| **LLM Fine-Tuning** (SFT, LoRA, RLHF, DPO) | ✅ Covered | `ai-design/training/` expanded — 7 new LLM-specific patterns with pre/mid/post organization |
| **Prompt Engineering** | ✅ Covered | `framework/prompt-engineering-guide.md` — CoT, few-shot, system prompts, structured output, healthcare examples |

### Tier 2 — Significant Gaps (partially addressed)

| Gap | Status | What Was Done / Remaining |
|-----|--------|--------------------------|
| **LLMOps** (prompt management, cost, observability) | ✅ Covered | `framework/llmops-guide.md` — prompt versioning, cost, observability, testing, CI/CD |
| **LLM Serving** (vLLM, speculative decoding, KV cache) | ❌ Not covered | Production inference infrastructure still missing |
| **Data Patterns** (7 patterns listed in README but files don't exist) | ❌ Not covered | Pattern files still need to be created |
| **Safety & Guardrails** (runtime safety, content filtering) | 🟡 Partially | `agent-guardrails-pattern.md` covers agent safety; general LLM guardrails still need dedicated pattern |

### Tier 3 — Nice to Have (depth and completeness)

| Gap | Why It Matters | Suggested Action |
|-----|---------------|-----------------|
| **General LLM Evaluation** (benchmarks, red teaming) | Beyond RAG-specific evaluation | Expand evaluation patterns |
| **Knowledge Graph Construction** | Supports Graph RAG | Add to rag-pipeline or knowledge section |
| **Clinical NLP** (NER, medical coding, de-identification) | Healthcare-specific NLP techniques | Framework guide or use case |
| **LLM Architecture Fundamentals** (tokenization, MoE, scaling) | Foundation knowledge | Framework guide |
| **RLAIF / Constitutional AI** | Scalable alignment without human labels | Add to training patterns |
| **Code execution / browser agents** | Emerging agent capabilities | Add to agent patterns |

---

## Current Structure (Updated)

```
patterns/
├── rag/                    (24 patterns — retrieval strategies)
├── rag-pipeline/           (10 patterns — pipeline engineering)
├── agents/                 (8 patterns — agentic AI)              ✅ NEW
│   ├── tool-use-pattern.md
│   ├── react-pattern.md
│   ├── plan-and-execute-pattern.md
│   ├── multi-agent-pattern.md
│   ├── agent-frameworks-pattern.md
│   ├── agent-memory-pattern.md
│   ├── agent-guardrails-pattern.md
│   └── agent-evaluation-pattern.md
├── ai-design/              (70 patterns — general AI/ML)
│   ├── deployment/         (8 patterns)
│   ├── explainability/     (6 patterns)
│   ├── integration/        (6 patterns)
│   ├── mlops/              (7 patterns)
│   ├── model-architecture/ (7 patterns)
│   ├── monitoring/         (6 patterns)
│   ├── performance/        (7 patterns)
│   ├── security/           (6 patterns)
│   └── training/           (14 patterns — 7 general ML + 7 LLM-specific)  ✅ EXPANDED
│       ├── (existing: federated, few-shot, active, curriculum, etc.)
│       ├── data-curation-pattern.md      (Pre-Training)
│       ├── sft-pattern.md                (Fine-Tuning)
│       ├── lora-peft-pattern.md          (Fine-Tuning)
│       ├── instruction-tuning-pattern.md (Fine-Tuning)
│       ├── synthetic-data-pattern.md     (Fine-Tuning)
│       ├── rlhf-pattern.md              (Post-Training)
│       └── dpo-pattern.md               (Post-Training)

framework/
├── (existing 10 docs)
├── prompt-engineering-guide.md            ✅ NEW
└── llmops-guide.md                        ✅ NEW
```

### Decisions Made

1. **Agents → top-level pattern folder** (like `rag/`), because agents are as foundational as RAG and will grow significantly
2. **LLM fine-tuning → expanded `ai-design/training/`** with LLM-specific files alongside general ML training
3. **Prompt engineering → `framework/` guide** (technique guide, not architecture pattern)
4. **LLMOps → `framework/` guide** (operational guide, not architecture pattern)
5. **Fine-tune vs. prompt vs. RAG decision framework → included in prompt-engineering-guide.md** (section, not separate file)

### Remaining Structural Changes (Not Yet Done)

| Change | Priority | Notes |
|--------|----------|-------|
| Create `ai-design/data/` (7 missing Data Patterns) | Tier 2 | Files listed in README but never created |
| Create `framework/llm-fundamentals.md` | Tier 3 | Tokenization, MoE, scaling laws |
| Add LLM serving patterns to `ai-design/performance/` | Tier 2 | vLLM, speculative decoding, KV cache |
| Create standalone MCP pattern in `patterns/agents/` | Tier 3 | Currently only mentioned |

---

## Research Backlog

Topics worth investigating for future pattern documents, roughly ordered by impact:

1. ~~LoRA/QLoRA for healthcare LLM fine-tuning~~ ✅ Done
2. ~~Agent design patterns (tool use, ReAct, multi-agent)~~ ✅ Done
3. ~~Prompt engineering techniques (CoT, few-shot, system prompts)~~ ✅ Done
4. ~~LLM guardrails and content filtering for healthcare~~ ✅ Done (agent-guardrails)
5. ~~LLMOps and prompt management~~ ✅ Done
6. LLM serving infrastructure (vLLM, speculative decoding, KV cache)
7. Clinical NLP (NER, medical coding, de-identification)
8. ~~Synthetic data generation for healthcare training~~ ✅ Done
9. Knowledge graph construction from clinical data
10. Reasoning models and test-time compute
11. **NEW**: 7 missing Data Patterns (feature store, data pipeline, data validation, etc.)
12. **NEW**: RLAIF / Constitutional AI
13. **NEW**: MCP (Model Context Protocol) dedicated pattern
14. **NEW**: Code execution and browser agents

---

*Last updated: 2026-02-05*
*Coverage: 155+ markdown files across 112 patterns, 3 use cases, 6 vendor guides, 12 framework docs, 5 templates*
