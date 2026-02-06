# Agentic AI Patterns

This directory contains patterns for building **autonomous AI agents** — systems that use tools, plan actions, maintain memory, collaborate with other agents, and operate within safety guardrails.

> **How this differs from other pattern folders**:
> - [`patterns/rag/`](../rag/) covers *retrieval strategies* for grounding LLM responses
> - [`patterns/rag-pipeline/`](../rag-pipeline/) covers *pipeline infrastructure* for data ingestion through indexing
> - [`patterns/agents/`](./) covers *autonomous AI agent architectures* — tool use, planning, memory, multi-agent coordination, and safety

---

## What Are AI Agents?

AI agents are LLM-powered systems that go beyond single-turn question answering. They can:

1. **Use tools** — call APIs, search databases, execute code, interact with external systems
2. **Plan and reason** — decompose complex tasks into steps, decide which actions to take
3. **Maintain memory** — remember conversation history, persist knowledge across sessions
4. **Collaborate** — multiple agents working together on complex workflows
5. **Self-correct** — evaluate their own outputs and retry or adjust approach

```
┌─────────────────────────────────────────────────────┐
│                    Agent System                       │
│                                                       │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────┐ │
│  │  Planner  │──▶│ Executor │──▶│  Tool Interface  │ │
│  │  (LLM)   │   │  (LLM)   │   │  (APIs, Code,    │ │
│  └──────────┘   └──────────┘   │   Search, RAG)   │ │
│       │              │          └──────────────────┘ │
│       ▼              ▼                               │
│  ┌──────────┐   ┌──────────┐                        │
│  │  Memory  │   │ Guardrails│                        │
│  │ (Short+  │   │ (Safety,  │                        │
│  │  Long)   │   │  HITL)    │                        │
│  └──────────┘   └──────────┘                        │
└─────────────────────────────────────────────────────┘
```

---

## Pattern Categories

### Core Agent Patterns
Foundational patterns for building individual agents.

1. [Tool Use & Function Calling](./tool-use-pattern.md) — How agents invoke external tools (APIs, databases, code execution)
2. [ReAct Pattern](./react-pattern.md) — Interleaved reasoning and acting (think → act → observe → repeat)
3. [Plan-and-Execute Pattern](./plan-and-execute-pattern.md) — Decompose task into plan, then execute steps

### Orchestration Patterns
Patterns for coordinating multiple agents and complex workflows.

4. [Multi-Agent Systems](./multi-agent-pattern.md) — Multiple specialized agents collaborating on tasks
5. [Agent Orchestration Frameworks](./agent-frameworks-pattern.md) — ADK, LangGraph, CrewAI, AutoGen comparison

### Memory Patterns
Patterns for how agents remember and learn.

6. [Agent Memory Systems](./agent-memory-pattern.md) — Conversation history, working memory, long-term persistence, episodic memory

### Safety & Evaluation Patterns
Patterns for keeping agents safe and measuring their effectiveness.

7. [Agent Guardrails & Safety](./agent-guardrails-pattern.md) — Constraining agent actions, content filtering, human-in-the-loop
8. [Agent Evaluation](./agent-evaluation-pattern.md) — Benchmarking agent capabilities, measuring task completion, safety testing

---

## Pattern Selection Guide

| Your Need | Start Here |
|-----------|------------|
| "I need my LLM to call APIs" | [Tool Use & Function Calling](./tool-use-pattern.md) |
| "I need step-by-step reasoning" | [ReAct Pattern](./react-pattern.md) |
| "I need to break down complex tasks" | [Plan-and-Execute Pattern](./plan-and-execute-pattern.md) |
| "I need multiple agents working together" | [Multi-Agent Systems](./multi-agent-pattern.md) |
| "Which agent framework should I use?" | [Agent Orchestration Frameworks](./agent-frameworks-pattern.md) |
| "My agent needs to remember things" | [Agent Memory Systems](./agent-memory-pattern.md) |
| "How do I keep my agent safe?" | [Agent Guardrails & Safety](./agent-guardrails-pattern.md) |
| "How do I measure agent performance?" | [Agent Evaluation](./agent-evaluation-pattern.md) |

---

## Relationship to Other Pattern Categories

| Pattern Category | How Agents Use It |
|-----------------|-------------------|
| [RAG Patterns](../rag/) | Agents use RAG as a retrieval tool — [Agentic RAG](../rag/agentic-rag.md) is the bridge |
| [RAG Pipeline](../rag-pipeline/) | Agents depend on well-built pipelines for knowledge retrieval |
| [AI Design — Deployment](../ai-design/deployment/) | Agent systems need serving, versioning, and A/B testing |
| [AI Design — Security](../ai-design/security/) | Agent safety builds on adversarial defense and privacy patterns |
| [AI Design — Monitoring](../ai-design/monitoring/) | Agent observability extends general monitoring patterns |

---

## Healthcare Agent Use Cases

- **Clinical Decision Support Agent**: Retrieves patient data, consults guidelines, recommends actions
- **Medical Documentation Agent**: Listens to patient encounters, generates SOAP notes, codes diagnoses
- **Prior Authorization Agent**: Checks insurance rules, gathers supporting evidence, files authorization
- **Clinical Trial Matching Agent**: Screens patients against trial criteria, ranks matches
- **Medication Reconciliation Agent**: Cross-references medication lists across systems, flags interactions

---

## Pattern Index

See [Pattern Index](./pattern-index.md) for the complete table of all agent patterns.

## Contributing

When adding new agent patterns:
1. Use the [pattern template](../../templates/pattern-template.md)
2. Include multi-vendor implementations (ADK, LangGraph, LangChain, etc.)
3. Include healthcare-specific agent use cases
4. Document safety considerations and guardrails
5. Provide agent evaluation guidance
