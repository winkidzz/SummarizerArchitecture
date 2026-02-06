# Claude AI Assistant Configuration

## Project Context

You are working on the **AI Summarization Reference Architecture** project - a comprehensive, evolving collection of architecture blueprints and patterns for building AI-powered summarization systems, with a **focus on healthcare use cases**.

### Important Clarification

**Project Infrastructure** (this project's tools):
- Uses local/Ollama/free LLM tools for the AI assistant
- Document store uses local/embedded tools for managing architecture patterns

**Documented Patterns** (what you document):
- **Healthcare summarization architecture patterns**
- Support **ALL vendors** (Gemini, Anthropic, GCP, Azure, AWS, enterprise platforms) - **NO restrictions**
- Cost-effective options (local models, free tiers) are shown as **alternatives**, not requirements
- Enterprise cloud platforms and premium models are fully supported and recommended for production healthcare use

## Project Goals

1. **Create Healthcare Architecture Blueprints**: Document detailed architecture patterns for healthcare summarization use cases
2. **RAG Pattern Library**: Build a comprehensive library of RAG patterns with detailed explanations
2b. **RAG Pipeline Engineering**: Document pipeline building patterns (ingestion, chunking, embedding, indexing, freshness, evaluation) that power RAG retrieval strategies
2c. **Agentic AI Patterns**: Document agent design patterns (tool use, ReAct, plan-and-execute, multi-agent, memory, guardrails, evaluation)
2d. **LLM Training & Fine-Tuning**: Document the full training lifecycle — pre-training (data curation), fine-tuning (SFT, LoRA, instruction tuning, synthetic data), and post-training alignment (RLHF, DPO)
3. **Full Vendor Support**: Document patterns that support ALL vendors (Gemini, Anthropic, GCP, Azure, AWS, enterprise platforms, local models) - NO restrictions
4. **Cost-Effective Options**: Show cost-effective designs (local models, efficient architectures) as alternatives, not constraints
5. **Healthcare Use Case Guidance**: Provide clear guidance for healthcare summarization scenarios
6. **Enterprise Support**: Full support for enterprise cloud platforms and premium models for production healthcare
7. **Evolving Documentation**: Continuously update and expand as new patterns and technologies emerge

## Key Technologies

**All Vendors Supported** (no restrictions):
- **Cloud Platforms**: Gemini (Vertex AI), Anthropic (Claude), Azure OpenAI, AWS Bedrock, GCP Vertex AI
- **Frameworks**: LangChain, Spring AI, Google ADK, Claude Skills
- **Cost-Effective Options**: Ollama, local models (shown as alternatives)
- **Techniques**: RAG patterns, agentic AI, latest generation techniques
- **Healthcare Focus**: Medical document summarization, clinical notes, patient records
- **Documentation**: Markdown, Mermaid diagrams, code examples

## Your Role

When working on this project:

1. **Follow the Constitution**: Always adhere to the principles in `memory/constitution.md`
2. **Pattern-First Thinking**: Focus on documenting reusable patterns, not one-off solutions
3. **Multi-Vendor Support**: When documenting a pattern, consider how it would be implemented across different vendors
4. **Use Case Clarity**: Always document when to use a pattern and when not to use it
5. **Quality Standards**: Ensure all code examples are production-ready and well-documented
6. **Evolution Mindset**: Design documentation to be easily updated as new patterns emerge

## Common Tasks

### Adding a New RAG Pattern
- Create a new spec in `specs/` directory
- Document the pattern architecture
- Provide implementation examples for **multiple vendors** (cloud platforms, enterprise solutions)
- Include **cost-effective alternatives** (local models, free tiers) as options, not requirements
- Focus on **healthcare use cases** but make patterns broadly applicable
- Include use case guidance
- Add architecture diagrams
- Show enterprise cloud platform implementations as primary examples

### Adding a New RAG Pipeline Pattern
- Use the dedicated template at `pattern-library/templates/rag-pipeline-template.md`
- Place new patterns in `pattern-library/patterns/rag-pipeline/`
- Indicate which pipeline stage(s) the pattern covers (ingestion, chunking, embedding, indexing, freshness, orchestration, evaluation)
- Include data flow diagrams showing input → transformation → output
- Document configuration parameters and their impact on quality
- Provide cost-per-document estimates
- Include healthcare-specific considerations (HIPAA, PHI, clinical data formats)
- Update the pattern index at `pattern-library/patterns/rag-pipeline/pattern-index.md`
- **Key distinction**: RAG patterns (`patterns/rag/`) cover retrieval *strategies*; RAG pipeline patterns (`patterns/rag-pipeline/`) cover pipeline *engineering infrastructure*

### Adding a New Agent Pattern
- Place new patterns in `pattern-library/patterns/agents/`
- Follow the existing structure: Overview, Architecture (Mermaid), Key Concepts, Implementation (multi-framework), Healthcare Use Case, Related Patterns
- Include implementations for major frameworks (ADK, LangGraph, CrewAI, Claude Agent SDK)
- Document agent safety considerations (guardrails, HITL, scope boundaries)
- Include healthcare-specific agent scenarios
- Update the pattern index at `pattern-library/patterns/agents/pattern-index.md`
- Categories: Core (tool use, ReAct), Orchestration (plan-and-execute, multi-agent), Memory, Safety

### Adding a New Training Pattern
- Place new patterns in `pattern-library/patterns/ai-design/training/`
- Indicate which training phase the pattern covers: **Pre-Training**, **Fine-Tuning (Mid-Training)**, or **Post-Training (Alignment)**
- Include code examples using standard frameworks (HuggingFace Transformers, TRL, Vertex AI)
- Document compute requirements and cost estimates
- Include healthcare-specific training data considerations
- Update the training README at `pattern-library/patterns/ai-design/training/README.md`
- **Key distinction**: General ML training patterns (federated, few-shot, active learning) vs. LLM-specific patterns (SFT, LoRA, RLHF, DPO)

### Updating Existing Patterns
- Maintain backward compatibility
- Clearly mark deprecated approaches
- Update all vendor implementations
- Add migration notes if needed

### Researching New Techniques
- Document the technique clearly
- Explain how it fits into existing patterns
- Provide implementation guidance
- Note any vendor-specific considerations

## File Organization

- `memory/constitution.md`: Project principles and guidelines
- `specs/[feature-name]/`: Feature specifications and implementation details
- `docs/patterns/`: Pattern documentation
- `docs/use-cases/`: Use case documentation
- `examples/`: Working code examples
- `pattern-library/patterns/rag/`: RAG retrieval architecture patterns (24 patterns)
- `pattern-library/patterns/rag-pipeline/`: RAG pipeline engineering patterns (10 patterns)
- `pattern-library/patterns/agents/`: Agentic AI patterns (8 patterns — tool use, ReAct, multi-agent, memory, guardrails)
- `pattern-library/patterns/ai-design/`: AI design patterns (70 patterns — deployment, training, security, etc.)
- `pattern-library/patterns/ai-design/training/`: Training patterns with pre/mid/post lifecycle (14 patterns — general ML + LLM-specific)
- `pattern-library/templates/`: Documentation templates (pattern, RAG pipeline, ADR, research, use case)
- `pattern-library/framework/`: Architecture framework, prompt engineering guide, LLMOps guide, and other guidance documents
- `pattern-library/vendor-guides/`: Vendor-specific implementation guides
- `pattern-library/topics.md`: Comprehensive topic map with coverage status and gap analysis

## Communication Style

- Be clear and concise
- Use technical terminology appropriately
- Provide context for architectural decisions
- Explain trade-offs and considerations
- Make documentation accessible to different skill levels

## Important Notes

- This is a **reference architecture** project - focus on patterns and blueprints
- Documentation should be production-quality and actionable
- Code examples should be runnable and tested
- Always consider multiple vendor implementations
- Keep documentation current with latest techniques

