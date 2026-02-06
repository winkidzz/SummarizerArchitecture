# Prompt Engineering Guide

A practical reference for designing effective prompts across LLM providers — with healthcare-specific techniques and examples.

> **Scope**: This guide covers prompting techniques (no model weight changes). For fine-tuning approaches, see [Training Patterns](../patterns/ai-design/training/README.md). For the decision of when to prompt vs. fine-tune vs. RAG, see the [Decision Framework](#prompt-vs-fine-tune-vs-rag) section below.

---

## Prompt Engineering Fundamentals

### What Is Prompt Engineering?

Prompt engineering is the practice of designing inputs to LLMs that reliably produce desired outputs — without modifying model weights. It is the **most cost-effective and fastest** way to customize LLM behavior for your use case.

### Why It Matters for Healthcare

- **Clinical accuracy**: Poorly prompted models hallucinate medical facts
- **Safety**: Prompts must enforce appropriate hedging and disclaimers
- **Consistency**: Clinical workflows require reproducible outputs
- **Compliance**: System prompts can enforce HIPAA-aware behavior
- **Cost**: Good prompts reduce the need for expensive fine-tuning

---

## Core Techniques

### 1. Zero-Shot Prompting

Ask the model to perform a task with no examples. Works best for well-known tasks on strong models (GPT-4, Claude, Gemini Pro).

```
Summarize this discharge note in SOAP format:

{note_text}
```

**When to use**: Simple, well-defined tasks where the model already has strong domain knowledge.

**When NOT to use**: Specialized output formats, domain-specific terminology, or when consistency matters.

### 2. Few-Shot Prompting (In-Context Learning)

Provide examples of desired input-output pairs before the actual task.

```
Extract medications from the following clinical notes.

Example 1:
Note: "Patient was started on metformin 500mg BID for type 2 diabetes."
Medications: [{"name": "metformin", "dose": "500mg", "frequency": "BID", "indication": "type 2 diabetes"}]

Example 2:
Note: "Continue lisinopril 10mg daily. Added amlodipine 5mg daily for uncontrolled HTN."
Medications: [{"name": "lisinopril", "dose": "10mg", "frequency": "daily", "indication": "HTN"}, {"name": "amlodipine", "dose": "5mg", "frequency": "daily", "indication": "uncontrolled HTN"}]

Now extract medications from this note:
Note: "{note_text}"
Medications:
```

**When to use**: When you need consistent output format, domain-specific behavior, or the task isn't well-known.

**Tip**: 3-5 examples is typically optimal. More examples improve consistency but increase cost and latency.

### 3. Chain-of-Thought (CoT) Prompting

Ask the model to reason step-by-step before giving a final answer. Critical for medical reasoning where the reasoning chain matters as much as the answer.

```
A 68-year-old male presents with acute onset chest pain, diaphoresis, and left arm numbness.
ECG shows ST elevation in leads II, III, and aVF. Troponin is elevated.

Think through this step by step:
1. What are the key findings?
2. What is the most likely diagnosis?
3. What immediate interventions are indicated?
4. What are the critical contraindications to check?

Provide your reasoning for each step, then give your final assessment.
```

**When to use**: Complex medical reasoning, differential diagnosis, multi-step clinical decisions.

**Variants**:
- **Zero-shot CoT**: Simply append "Let's think step by step" to any prompt
- **Manual CoT**: Provide worked examples with reasoning chains
- **Auto-CoT**: Let the model generate its own reasoning demonstrations

### 4. Self-Consistency

Generate multiple reasoning paths and take the majority answer. Reduces errors in medical reasoning by ~15-30%.

```python
# Pseudocode: Self-consistency for clinical classification
responses = []
for i in range(5):
    response = llm.generate(
        prompt=f"Classify this condition as acute or chronic. Think step by step.\n\n{condition_text}",
        temperature=0.7  # Higher temperature for diverse reasoning paths
    )
    responses.append(extract_classification(response))

final_answer = majority_vote(responses)
```

**When to use**: Safety-critical classifications, when a single response isn't reliable enough.

**Trade-off**: 3-5x cost increase for improved accuracy.

### 5. Tree-of-Thought (ToT)

Explore multiple reasoning branches, evaluate each, and select the best path. Useful for complex differential diagnosis.

```
Patient presents with: fatigue, weight gain, cold intolerance, dry skin, constipation.

Consider three possible diagnostic paths:
Path A: Endocrine disorder
Path B: Nutritional deficiency
Path C: Autoimmune condition

For each path:
1. List supporting evidence from the symptoms
2. List contradicting evidence
3. Suggest one confirmatory test
4. Rate likelihood (high/medium/low)

Then select the most likely diagnosis with your reasoning.
```

**When to use**: Complex diagnostic scenarios with multiple plausible explanations.

### 6. ReAct Prompting (Reasoning + Acting)

Combine reasoning with tool use. The model thinks, acts (calls a tool), observes the result, and repeats.

```
You are a clinical pharmacist assistant with access to these tools:
- drug_interactions(drug1, drug2): Check for interactions
- dosing_guidelines(drug, condition): Get dosing recommendations
- patient_allergies(patient_id): Check allergy list

Question: Is it safe to prescribe amoxicillin 500mg TID to patient #12345 for a UTI?

Think through your reasoning, use tools as needed, and provide a recommendation.

Thought: I need to check the patient's allergies first, then verify the drug is appropriate for UTI, and check dosing.
Action: patient_allergies("12345")
Observation: [Penicillin - severe anaphylaxis]
Thought: The patient has a severe penicillin allergy. Amoxicillin is a penicillin-class antibiotic and is contraindicated.
Action: ...
```

**When to use**: Agent workflows, multi-step clinical processes. See [ReAct Pattern](../patterns/agents/react-pattern.md).

---

## System Prompt Design

System prompts define the model's persona, constraints, and behavioral guardrails. For healthcare, they are critical.

### Anatomy of a Healthcare System Prompt

```
You are a clinical decision support assistant for [institution name].

## Role and Scope
- You assist healthcare professionals with clinical documentation and information retrieval
- You do NOT provide direct patient care recommendations
- You always recommend consulting the treating physician for clinical decisions

## Clinical Guidelines
- Follow [specific guideline set, e.g., UpToDate, AHA/ACC guidelines]
- When evidence is uncertain, explicitly state the level of evidence
- Always note when a recommendation is off-label

## Safety Requirements
- Never recommend specific medications without noting that physician review is required
- Flag potential drug interactions with a warning prefix: "⚠️ INTERACTION:"
- If the query involves a life-threatening condition, begin with: "🚨 URGENT:"
- Do not provide information about controlled substance dosing without clinical context

## Output Format
- Use structured formats (SOAP, bullet points) for clinical summaries
- Include ICD-10 codes when documenting diagnoses
- Cite sources when referencing clinical guidelines

## Privacy
- Never include patient identifiers in your responses
- If PHI is detected in the input, flag it and proceed without echoing it
```

### Key Principles

| Principle | Description | Example |
|-----------|-------------|---------|
| **Be specific** | Vague instructions produce vague outputs | "Summarize in SOAP format" vs. "Summarize" |
| **Define boundaries** | What the model should NOT do | "Do not recommend specific dosages" |
| **Set safety rails** | Enforce appropriate hedging | "Always recommend physician consultation for..." |
| **Specify format** | Define exact output structure | JSON schema, SOAP sections, bullet points |
| **Provide context** | Institution-specific guidelines | "Follow Mayo Clinic protocols for..." |

---

## Structured Output Techniques

### JSON Mode

Force structured output for downstream processing.

```
Extract the following information from this clinical note and return as JSON:

{
  "patient_age": <integer>,
  "chief_complaint": "<string>",
  "diagnoses": [{"code": "<ICD-10>", "description": "<string>", "status": "active|resolved"}],
  "medications": [{"name": "<string>", "dose": "<string>", "frequency": "<string>"}],
  "follow_up": "<string>"
}

Clinical note:
{note_text}
```

**Vendor support**:
- **Anthropic Claude**: Tool use with JSON schema, or `response_format` in newer APIs
- **Google Gemini**: `response_mime_type: "application/json"` with `response_schema`
- **OpenAI GPT-4**: `response_format: { type: "json_object" }` or structured outputs

### XML Tags (Anthropic Claude)

Claude performs well with XML-tagged prompts for clear section delineation.

```xml
<task>Extract medications from the clinical note</task>

<format>
Return each medication as a structured entry with name, dose, route, and frequency.
</format>

<clinical_note>
{note_text}
</clinical_note>

<guidelines>
- Include only active medications (not discontinued)
- Normalize frequency to standard abbreviations (QD, BID, TID, QID, PRN)
- If dose is unclear, note "dose not specified"
</guidelines>
```

---

## Prompt vs. Fine-Tune vs. RAG

### Decision Framework

```
Is the knowledge already in the model?
├── YES → Is the output format/behavior what you need?
│   ├── YES → ✅ Zero-shot prompting (done!)
│   └── NO → Is few-shot prompting sufficient?
│       ├── YES → ✅ Few-shot prompting
│       └── NO → Is the behavior change complex?
│           ├── Simple format/style → ✅ System prompt + examples
│           └── Deep behavior change → ✅ Fine-tuning (SFT/LoRA)
└── NO → Is the knowledge static or dynamic?
    ├── Static (guidelines, protocols) → ✅ RAG
    ├── Dynamic (patient data, real-time) → ✅ RAG with live retrieval
    └── Both → ✅ RAG + fine-tuning
```

### Comparison

| Approach | Latency to Deploy | Cost | Best For |
|----------|-------------------|------|----------|
| **Prompt engineering** | Minutes | Lowest | Format changes, persona, simple tasks |
| **Few-shot prompting** | Minutes | Low (token cost) | Consistent output format, edge cases |
| **RAG** | Hours–days | Medium | External knowledge, citations, freshness |
| **Fine-tuning (LoRA)** | Days–weeks | High | Deep behavioral change, specialized domain |
| **Full fine-tuning** | Weeks | Very high | Fundamental capability changes |

**Rule of thumb**: Always try prompt engineering first. Only fine-tune when prompting demonstrably fails.

---

## Healthcare-Specific Patterns

### Clinical Summarization Prompt

```
You are a clinical documentation assistant. Summarize the following patient encounter
in SOAP format.

## Requirements
- **Subjective**: Patient's reported symptoms, history, and concerns
- **Objective**: Vital signs, exam findings, lab results, imaging
- **Assessment**: Clinical impression with ICD-10 codes
- **Plan**: Treatment plan, medications, follow-up, referrals

## Constraints
- Use standard medical abbreviations
- Include all mentioned medications with doses
- Flag any critical lab values (prefix with "CRITICAL:")
- Do not infer information not present in the source note
- If information for a SOAP section is missing, write "Not documented"

## Source Note
{encounter_note}
```

### Medical Q&A with Safety

```
Answer the following clinical question based on current evidence-based guidelines.

## Rules
1. If you are uncertain, say "Evidence is limited" and explain why
2. Always cite the guideline or source for your recommendation
3. For medication recommendations, include: drug, dose range, contraindications
4. End every response with: "This information is for clinical decision support.
   Final treatment decisions should be made by the treating physician."

## Question
{clinical_question}
```

---

## Prompt Optimization

### Manual Optimization Checklist

1. **Start simple** — zero-shot first, add complexity only as needed
2. **Test edge cases** — unusual inputs, ambiguous cases, adversarial inputs
3. **Measure** — track accuracy, consistency, and cost across prompt versions
4. **Version control** — treat prompts as code; track changes in git
5. **A/B test** — compare prompt variants on the same evaluation set

### Automated Optimization Tools

| Tool | Approach | Best For |
|------|----------|----------|
| **DSPy** | Compile natural language programs into optimized prompts | Complex multi-step pipelines |
| **AutoPrompt** | Gradient-based prompt search | Finding optimal token sequences |
| **PromptBench** | Systematic prompt evaluation | Benchmarking prompt robustness |
| **LangSmith** | Trace and evaluate prompt performance | Production observability |

---

## Prompt Templates for Common Healthcare Tasks

| Task | Technique | Key Elements |
|------|-----------|--------------|
| Clinical summarization | System prompt + format spec | SOAP structure, ICD-10, abbreviations |
| Medication extraction | Few-shot + JSON mode | 3-5 examples, schema definition |
| Differential diagnosis | Chain-of-thought | Step-by-step reasoning, evidence listing |
| Patient education | System prompt + persona | Reading level, cultural sensitivity |
| Clinical coding (ICD-10, CPT) | Few-shot + structured output | Code-description pairs, guidelines |
| Triage classification | Few-shot + self-consistency | Multiple reasoning paths, majority vote |
| Drug interaction check | ReAct + tool use | External API calls, structured warnings |

---

## Related Resources

- [Training Patterns](../patterns/ai-design/training/README.md) — When prompting isn't enough
- [Agent Patterns](../patterns/agents/) — ReAct, tool use, and agentic prompting
- [RAG Patterns](../patterns/rag/) — Grounding prompts with retrieved knowledge
- [Vendor Guides](../vendor-guides/) — Provider-specific prompting features
- [LLMOps Guide](./llmops-guide.md) — Prompt versioning and management in production

## References

- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering)
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Google Gemini Prompting Strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- [Chain-of-Thought Prompting (Wei et al., 2022)](https://arxiv.org/abs/2201.11903)
- [Tree of Thoughts (Yao et al., 2023)](https://arxiv.org/abs/2305.10601)
- [DSPy: Compiling Declarative Language Model Calls (2023)](https://arxiv.org/abs/2310.03714)

## Version History

- **v1.0** (2026-02-05): Initial version
