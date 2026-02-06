# Agent Pattern Index

Complete index of all agentic AI patterns documented in this reference architecture.

## Core Agent Patterns

| Pattern | Description | Complexity | Key Frameworks |
|---------|-------------|------------|----------------|
| [Tool Use & Function Calling](./tool-use-pattern.md) | Agents invoking external tools via structured API calls | Medium | ADK, LangChain, OpenAI Functions |
| [ReAct Pattern](./react-pattern.md) | Interleaved reasoning and acting loops | Medium | LangChain, ADK, LlamaIndex |
| [Plan-and-Execute Pattern](./plan-and-execute-pattern.md) | Decompose into plan, then execute steps | High | LangGraph, ADK, AutoGen |

## Orchestration Patterns

| Pattern | Description | Complexity | Key Frameworks |
|---------|-------------|------------|----------------|
| [Multi-Agent Systems](./multi-agent-pattern.md) | Multiple specialized agents collaborating | High | CrewAI, AutoGen, LangGraph, ADK |
| [Agent Orchestration Frameworks](./agent-frameworks-pattern.md) | Framework comparison and selection guide | Medium | ADK, LangGraph, CrewAI, AutoGen |

## Memory Patterns

| Pattern | Description | Complexity | Key Frameworks |
|---------|-------------|------------|----------------|
| [Agent Memory Systems](./agent-memory-pattern.md) | Conversation, working, long-term, and episodic memory | High | LangGraph, Mem0, Zep, custom |

## Safety & Evaluation Patterns

| Pattern | Description | Complexity | Key Frameworks |
|---------|-------------|------------|----------------|
| [Agent Guardrails & Safety](./agent-guardrails-pattern.md) | Action constraints, content filtering, HITL | High | Guardrails AI, NeMo, Model Armor |
| [Agent Evaluation](./agent-evaluation-pattern.md) | Benchmarks, task completion, safety testing | High | SWE-bench, AgentBench, custom |

---

## Quick Selection Guide

### By Agent Complexity
- **Simple** (single tool, single turn): [Tool Use](./tool-use-pattern.md)
- **Moderate** (multi-step, single agent): [ReAct](./react-pattern.md) or [Plan-and-Execute](./plan-and-execute-pattern.md)
- **Complex** (multi-agent, long-running): [Multi-Agent Systems](./multi-agent-pattern.md)

### By Requirement
- **API integration** → [Tool Use](./tool-use-pattern.md)
- **Complex reasoning** → [ReAct](./react-pattern.md)
- **Task decomposition** → [Plan-and-Execute](./plan-and-execute-pattern.md)
- **Team of specialists** → [Multi-Agent Systems](./multi-agent-pattern.md)
- **Framework selection** → [Agent Frameworks](./agent-frameworks-pattern.md)
- **Cross-session state** → [Agent Memory](./agent-memory-pattern.md)
- **Safety-critical** → [Agent Guardrails](./agent-guardrails-pattern.md)
- **Quality measurement** → [Agent Evaluation](./agent-evaluation-pattern.md)

---

## Contributing

When adding new agent patterns:
1. Use the [pattern template](../../templates/pattern-template.md)
2. Add to this index under the appropriate category
3. Update the [README](./README.md)
4. Include healthcare agent use cases
