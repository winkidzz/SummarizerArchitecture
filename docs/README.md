# Documentation Index

This directory contains the documentation for the AI Summarization Reference Architecture project.

## Core Documentation

### Architecture Framework
- [Architecture Framework](./architecture-framework.md) - Well-Architected Framework principles applied to RAG systems
- [Deployment Guide](./deployment-guide.md) - Deployment archetypes and guidance
- [Testing Guide](./testing-guide.md) - Testing approach and best practices
- [Healthcare Development Lifecycle](./healthcare-development-lifecycle.md) - Complete checklist from ideation to production with RACI matrices
- [Technical Tools & Frameworks](./technical-tools-framework.md) - Comprehensive catalog of tools organized by Well-Architected Framework pillars
- [Project Planning & Delivery](./project-planning-delivery.md) - Project planning, delivery strategies, and resource management by phase

### Patterns and Use Cases
- [RAG Patterns](./patterns/README.md) - Complete RAG pattern library
- [Pattern Index](./patterns/pattern-index.md) - Quick pattern selection guide
- [AI Design Patterns](./ai-design-patterns/README.md) - Comprehensive catalog of AI design patterns (beyond RAG)
- [AI Design Pattern Index](./ai-design-patterns/pattern-index.md) - Quick selection guide for AI design patterns
- [AI Development Techniques](./ai-development-techniques.md) - Comprehensive catalog of AI/ML techniques, methodologies, and frameworks
- [Use Cases](./use-cases/) - Use case-specific guidance
- [Vendor Guides](./vendor-guides/) - Vendor-specific implementation guides

### Setup and Configuration
- [Document Store Setup](./document-store-setup.md) - Document store setup and usage
- [Agent Setup Guide](./agent-setup-guide.md) - Google ADK and Ollama setup

## Documentation Structure

### `patterns/`
Contains detailed documentation for each RAG pattern and architecture blueprint. Each pattern includes:
- Architecture overview
- When to use / when not to use
- Implementation examples for multiple vendors
- Performance characteristics
- Trade-offs and considerations
- Architecture diagrams
- **Well-Architected Framework alignment**
- **Deployment considerations**

### `use-cases/`
Contains use case-specific documentation that helps you:
- Understand requirements for different use cases
- Select the right pattern for your use case
- Compare patterns for your specific needs
- Find implementation examples

### `vendor-guides/`
Contains vendor-specific implementation guides for:
- Gemini (Google)
- Anthropic (Claude)
- LangChain
- Spring AI
- Xariv
- Google ADK
- Claude Skills

## Well-Architected Framework

All patterns and architectures align with the [Google Cloud Well-Architected Framework](https://docs.cloud.google.com/architecture/framework/printable):

1. **Operational Excellence** - Monitoring, automation, continuous improvement
2. **Security, Privacy, and Compliance** - Security by design, AI security, privacy
3. **Reliability** - High availability, graceful degradation, redundancy
4. **Cost Optimization** - Resource optimization, cost monitoring
5. **Performance Optimization** - Modular design, resource planning, monitoring
6. **Sustainability** - Resource efficiency, environmental considerations

See [Architecture Framework](./architecture-framework.md) for detailed guidance.

## Getting Started

1. Start with [Use Cases](./use-cases/) if you know your use case
2. Browse [Patterns](./patterns/) to understand available architectures
3. Check [Vendor Guides](./vendor-guides/) for implementation details
4. Review [Architecture Framework](./architecture-framework.md) for quality principles
5. Consult [Deployment Guide](./deployment-guide.md) for deployment strategies

## Contributing

When adding new documentation:
- Follow the templates in `../templates/`
- Include multi-vendor examples
- Provide clear use case guidance
- Include architecture diagrams
- **Align with Well-Architected Framework pillars**
- **Document deployment considerations**
- Test all code examples
