# Project Constitution

## Project Overview
This project is an **AI Summarization Reference Architecture** - a living, evolving collection of architecture blueprints, patterns, and best practices for building AI-powered summarization systems, with a focus on **healthcare use cases**.

### Important Distinction
- **Project Infrastructure**: This project uses local/Ollama/free LLM tools for the AI assistant that helps build and maintain the architecture documentation
- **Documented Patterns**: The architecture patterns documented here are for **healthcare summarization systems** and support **ALL vendors** (Gemini, Anthropic, GCP, cloud platforms, local models, etc.) - **NO restrictions**
- **Cost-Effective Options**: Cost-effective designs are shown as options but are **NOT constraints** - patterns support enterprise cloud platforms, premium models, and any vendor solution

## Core Principles

### 1. Evolution and Discovery
- This is a **reference architecture** that evolves as new patterns, technologies, and techniques emerge
- New discoveries should be documented and integrated into the architecture patterns
- Patterns should be validated through real-world use cases

### 2. Use Case Driven
- Architecture patterns are organized by use cases
- Each pattern should clearly document when to use it and when not to use it
- Use cases should be practical and grounded in real-world scenarios

### 3. Technology Agnostic with Full Vendor Support
- **No Vendor Restrictions**: Patterns support ALL vendors and platforms:
  - Cloud platforms: Gemini (Google Cloud), Anthropic (Claude), Azure OpenAI, AWS Bedrock
  - Enterprise platforms: GCP Vertex AI, AWS SageMaker, Azure AI Services
  - Frameworks: LangChain, Spring AI, Google ADK, Claude Skills
  - Local/Free options: Ollama, local models (shown as cost-effective alternatives, not requirements)
- **Healthcare Focus**: Patterns are designed for healthcare summarization use cases but applicable broadly
- **Vendor Flexibility**: Document implementations for multiple vendors to enable comparison
- **Cost-Effective Options**: Show cost-effective designs (local models, efficient architectures) as alternatives, not constraints
- **Enterprise Support**: Full support for enterprise cloud platforms and premium models
- **Pattern Abstraction**: Maintain pattern abstraction while documenting vendor-specific implementations

### 4. Pattern Documentation
- Each RAG pattern and architecture pattern should have:
  - Detailed explanation of the pattern
  - When to use it (use cases)
  - When NOT to use it (anti-patterns)
  - Implementation examples across different vendors
  - Performance characteristics
  - Trade-offs and considerations

### 5. Latest Generation Techniques
- Incorporate latest generation techniques and technologies
- Stay current with emerging patterns (RAG variations, agentic patterns, etc.)
- Document cutting-edge approaches with appropriate caveats

### 6. Reference Quality
- Documentation should be clear, comprehensive, and actionable
- Code examples should be production-ready and well-commented
- Architecture diagrams should be clear and maintainable

### 7. Well-Architected Framework Alignment
- All patterns should align with Google Cloud Well-Architected Framework principles
- Document operational excellence, security, reliability, cost, performance, and sustainability considerations
- Include deployment archetype guidance (zonal, regional, multi-regional, hybrid)
- Provide Architecture Decision Records (ADRs) for major decisions
- Reference: [Google Cloud Architecture Framework](https://docs.cloud.google.com/architecture/framework/printable)

## Technology Stack

### AI Vendors & Frameworks (Pattern Support)
Patterns documented support ALL of these vendors (no restrictions):

**Cloud Platforms:**
- **Gemini**: Google Cloud Vertex AI, Gemini models
- **Anthropic**: Claude models and services (all tiers)
- **Azure OpenAI**: Microsoft Azure OpenAI Service
- **AWS Bedrock**: Amazon Bedrock models
- **GCP Vertex AI**: Full Google Cloud AI platform

**Frameworks:**
- **LangChain**: Framework for LLM applications
- **Spring AI**: Java/Spring integration for AI
- **Google ADK**: Google AI Development Kit
- **Claude Skills**: Anthropic's skills/extensions

**Local/Free Options** (shown as cost-effective alternatives):
- **Ollama**: Local LLM platform (cost-effective option)
- **Direct Models**: Direct model access (local or cloud)

**Note**: The project's own infrastructure uses local/Ollama tools for the AI assistant, but documented patterns support all vendors without restriction.

### Documentation Standards
- Markdown for all documentation
- Mermaid diagrams for architecture visualization
- Code examples in multiple languages (Python, Java, TypeScript)
- Clear sectioning and navigation

## Development Guidelines

### Adding New Patterns
1. Identify the use case and problem it solves
2. Document the pattern architecture
3. Provide implementation examples for at least 2 vendors
4. Include performance benchmarks if available
5. Document trade-offs and limitations
6. Add to appropriate use case category

### Updating Existing Patterns
1. Maintain backward compatibility in documentation
2. Clearly mark deprecated approaches
3. Add migration guides when patterns evolve
4. Update all vendor implementations consistently

### Quality Standards
- All code examples must be tested and runnable
- Architecture diagrams must be accurate and up-to-date
- Documentation must be reviewed for clarity and completeness
- Examples should follow best practices for each vendor

### Code Development Principles
- **Extend, Don't Duplicate**: Extend existing scripts and examples rather than creating new ones
- **Unified Testing**: Use existing example scripts as test harnesses, adding test cases incrementally
- **Avoid Test Silos**: Integrate tests into existing workflows and scripts
- **Script Evolution**: Evolve scripts to handle multiple scenarios rather than creating scenario-specific files
- **Reusability First**: Build on existing components and utilities whenever possible

## Project Structure

```
.
├── memory/
│   └── constitution.md (this file)
├── specs/
│   └── [feature-specs]/
├── templates/
│   └── [spec-kit templates]
├── docs/
│   ├── patterns/
│   ├── use-cases/
│   └── vendor-guides/
└── examples/
    └── [implementation examples]
```

## Success Criteria

A successful addition to this reference architecture:
- ✅ Clearly explains the pattern and its purpose
- ✅ Documents when and when not to use it
- ✅ Provides working examples for multiple vendors
- ✅ Includes architecture diagrams
- ✅ Documents performance characteristics
- ✅ Is discoverable through use case navigation
- ✅ Follows documentation standards

