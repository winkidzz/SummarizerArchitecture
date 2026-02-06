# Agent Orchestration Frameworks

## Overview
Agent orchestration frameworks provide the scaffolding for building, deploying, and managing AI agents. Choosing the right framework determines your agent's capabilities, how easily it integrates with tools and other agents, and how observable and debuggable it is in production.

## Framework Comparison

| Framework | Provider | Multi-Agent | Graph-Based | Tool Ecosystem | Observability | Best For |
|-----------|----------|-------------|-------------|----------------|---------------|----------|
| **Google ADK** | Google | Yes (sub-agents) | No (hierarchical) | Built-in tools + custom | Built-in tracing | Google Cloud, Gemini, production agents |
| **LangGraph** | LangChain | Yes (nodes) | Yes (state graphs) | LangChain ecosystem | LangSmith | Complex stateful workflows, custom graphs |
| **CrewAI** | CrewAI | Yes (crews) | No (role-based) | LangChain tools | Built-in | Multi-agent teams, simple setup |
| **AutoGen** | Microsoft | Yes (conversation) | No (chat-based) | Custom | Limited | Research, conversation-based agents |
| **LlamaIndex Workflows** | LlamaIndex | Limited | Yes (event-driven) | LlamaIndex ecosystem | Built-in | Data-centric agents, RAG-first |
| **Semantic Kernel** | Microsoft | Plugins | No (pipeline) | Plugins + OpenAPI | .NET ecosystem | Enterprise .NET, Azure integration |
| **Claude Agent SDK** | Anthropic | Yes | No | MCP + custom | Built-in | Claude-powered agents, MCP ecosystem |

## Selection Guide

| Your Requirement | Recommended Framework | Why |
|-----------------|----------------------|-----|
| Google Cloud ecosystem | **Google ADK** | Native Vertex AI, Gemini, Healthcare API integration |
| Complex stateful workflows | **LangGraph** | Graph-based state machines, fine-grained control |
| Quick multi-agent prototype | **CrewAI** | Simplest multi-agent setup, role-based |
| Research / experimentation | **AutoGen** | Conversation-based, easy to experiment |
| Data-heavy RAG agents | **LlamaIndex Workflows** | Built for data ingestion and retrieval |
| Enterprise .NET / Azure | **Semantic Kernel** | Microsoft ecosystem integration |
| Claude-first development | **Claude Agent SDK** | Native tool use, MCP, Anthropic ecosystem |
| Vendor-agnostic | **LangGraph** or **LangChain** | Supports multiple LLM providers |

## Healthcare-Specific Considerations

| Framework | HIPAA Support | Healthcare APIs | Audit Logging |
|-----------|---------------|-----------------|---------------|
| Google ADK | Yes (Vertex AI BAA) | Healthcare API, FHIR | Built-in tracing |
| LangGraph | Depends on LLM provider | Via LangChain integrations | LangSmith (check BAA) |
| CrewAI | Depends on LLM provider | Via tool integrations | Limited |
| Claude Agent SDK | Yes (Anthropic BAA) | Via MCP servers | Built-in |

## MCP (Model Context Protocol)

MCP is Anthropic's open protocol for connecting LLMs to external data and tools. Key for healthcare agent development:
- **MCP Servers**: Provide tools and data sources to agents
- **Standardized interface**: Any MCP-compatible agent can use any MCP server
- **Healthcare potential**: FHIR MCP servers, EHR MCP servers, drug database MCP servers

## Related Patterns
- [Tool Use & Function Calling](./tool-use-pattern.md) — Fundamental capability all frameworks provide
- [Multi-Agent Systems](./multi-agent-pattern.md) — Multi-agent architectures implemented via frameworks
- [Agent Evaluation](./agent-evaluation-pattern.md) — Evaluating agents built with these frameworks

## References
- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## Version History
- **v1.0** (2026-02-05): Initial version
