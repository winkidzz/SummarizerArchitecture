# AI Summarization Reference Architecture

## Overview

This specification defines the architecture and structure for an evolving reference architecture project focused on **AI-powered summarization systems for healthcare use cases**. The project serves as a comprehensive guide for architects and developers building healthcare summarization solutions.

### Project Dual Goals

This project has **two interconnected goals** that work together to create a self-maintaining, always-current reference architecture:

**Goal 1: Pattern Documentation** - Research and develop AI strategies, patterns, and blueprints for healthcare summarization
- Create comprehensive RAG pattern library
- Document use cases and implementation guidance
- Provide multi-vendor support (Anthropic, Google, Azure, AWS, etc.)
- Maintain production-quality examples and architecture diagrams

**Goal 2: Self-Updating Research System** - Agentic AI that monitors research sources and automatically keeps Goal 1 documentation current
- Monitor arXiv for latest AI/RAG research papers
- Track Anthropic, Google AI, Microsoft, AWS research blogs
- Ingest research into ChromaDB knowledge base
- Validate patterns against latest research
- Generate update recommendations
- Keep documentation current with latest techniques

**How They Work Together**: Goal 2's agentic system continuously monitors research sources (arXiv, industry blogs) and updates the ChromaDB knowledge base. It then validates Goal 1's pattern documentation against this research, ensuring the architecture patterns remain current with the latest AI innovations.

### Project Scope Clarification

**Project Infrastructure** (this project's tools):
- Uses local/Ollama/free LLM tools for the AI assistant that helps build and maintain documentation
- Document store uses local/embedded tools (ChromaDB, Docling) for managing architecture patterns
- Claude Skills for automated research monitoring and pattern validation
- arXiv API integration for latest AI research
- Web scraping for industry blog monitoring

**Documented Patterns** (what this project documents):
- **Healthcare summarization architecture patterns** that support **ALL vendors and platforms**
- **No restrictions**: Patterns support Gemini, Anthropic, GCP, Azure, AWS, enterprise platforms
- **Cost-effective options shown**: Local models and efficient designs are documented as alternatives, not requirements
- **Enterprise support**: Full support for premium cloud platforms, enterprise models, and commercial solutions

## Goals

1. **Pattern Library (Goal 1)**: Create a comprehensive library of RAG (Retrieval-Augmented Generation) patterns and summarization architectures
2. **Use Case Documentation (Goal 1)**: Document when to use each pattern for specific use cases
3. **Multi-Vendor Support (Goal 1)**: Provide implementation guidance for Gemini, Anthropic, Azure OpenAI, AWS Bedrock, LangChain, Spring AI, Google ADK, and Claude Skills
4. **Self-Updating System (Goal 2)**: Agentic AI that monitors arXiv and research sources to keep documentation current
5. **Automated Validation (Goal 2)**: Pattern validation against latest research in ChromaDB knowledge base
6. **Evolving Architecture (Goal 1 + 2)**: Continuously update with new patterns and techniques as they emerge
7. **Reference Quality (Goal 1)**: Maintain production-quality documentation with working examples

## Scope

### In Scope
- RAG pattern documentation and architecture blueprints
- Use case-driven pattern selection guidance
- Multi-vendor implementation examples
- Architecture diagrams and visualizations
- Performance characteristics and trade-offs
- Latest generation techniques integration
- Pattern evolution and versioning

### Out of Scope
- Production deployment configurations (unless part of pattern)
- Vendor-specific pricing or commercial considerations
- End-user applications (this is a reference architecture)
- Training data preparation (unless part of pattern)

## Key Components

### 1. Document Store and Knowledge Base
**Note**: This is the project's infrastructure for managing architecture documentation, not the patterns themselves.

- **Docling Integration**: Document processing framework to convert various formats (PDF, DOCX, PPTX, etc.) into structured data
- **Embedded File-Based Document Store**: Local, file-based vector database (e.g., ChromaDB) for storing processed architecture patterns and documentation
- **Google ADK Agent Library**: Querying interface for the project's AI assistant (not a constraint for documented patterns)
- **Ollama Integration**: Local LLM support for the project's AI assistant (cost-effective tool for this project)
- **RAG Query Interface**: Enable querying of architecture patterns from the knowledge base
- **Web Search Integration**: Python-based web search tool to dynamically fetch relevant content and update the knowledge base

**Important**: The patterns documented in this project support ALL vendors and platforms - the project's own infrastructure choices do not constrain the documented patterns.

### 1.1 Healthcare Data Integration
Patterns support integration with healthcare data sources:
- **FHIR API**: Standard healthcare data access
- **Proprietary EHR APIs**: Vendor-specific EHR integration
- **Real-Time Streaming**: ADT events, EHR datastore streaming through Snowflake/Streamlit
- **Data Processing**: BigQuery for real-time processing, cleaning, sanitization, standardization
- **Data Storage**: BigQuery (processed data), Spanner (analytical/reporting)
- **Data Access**: Multiple access patterns (BigQuery, FHIR, APIs, Pub/Sub, connectors, microservices, GraphQL)

See [Healthcare Data Access Patterns](./docs/healthcare-data-patterns.md) for detailed documentation.

### 2. Pattern Library
- **Basic RAG**: Standard retrieval-augmented generation
- **Advanced RAG**: Multi-step retrieval, query decomposition
- **Agentic RAG**: Agent-based retrieval and generation
- **Hybrid RAG**: Combining multiple retrieval strategies
- **Streaming RAG**: Real-time summarization patterns
- **Custom Patterns**: Domain-specific patterns as discovered

### 3. Use Case Categories (Healthcare Focus)
- **Medical Document Summarization**: Patient records, clinical notes, research papers
- **Clinical Conversation Summarization**: Doctor-patient interactions, medical consultations
- **Multi-Document Medical Summarization**: Cross-patient analysis, research synthesis
- **Real-Time Medical Summarization**: Live clinical data, streaming patient information
- **Healthcare-Specific**: Medical imaging reports, lab results, treatment plans
- **Regulatory Compliance**: HIPAA-compliant summarization patterns
- **Custom Healthcare Use Cases**: As patterns emerge in healthcare domain

### 3.1 Healthcare Data Access Patterns
- **FHIR API**: Standard healthcare data exchange (HL7 FHIR)
- **Proprietary EHR APIs**: Vendor-specific APIs (Epic, Cerner, Allscripts, etc.)
- **Real-Time ADT Streaming**: Admission, Discharge, Transfer events from EHR
- **EHR Datastore Streaming**: Real-time streaming through Snowflake/Streamlit to BigQuery
- **Data Processing Pipeline**: Real-time processing → Cleaning/Sanitization → Standardization → BigQuery → Spanner
- **Data Access Methods**:
  - Direct BigQuery access
  - FHIR API access
  - Proprietary API access
  - Real-time events via Pub/Sub (from BigQuery/Spanner)
  - Direct query using connectors
  - Microservices on top of BigQuery
  - GraphQL on BigQuery or Spanner DB

### 4. Self-Updating Research System (Goal 2)

The project includes an **agentic AI system** that automatically monitors research sources and keeps pattern documentation current.

#### 4.1 Research Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Research Sources                          │
├─────────────────────────────────────────────────────────────┤
│  • arXiv (cs.CL, cs.AI, cs.LG, cs.IR)                       │
│  • Anthropic Blog & Research                                │
│  • Google AI Blog                                           │
│  • Microsoft Research AI                                    │
│  • AWS Machine Learning Blog                               │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Research Monitor (Claude Skill)                 │
├─────────────────────────────────────────────────────────────┤
│  • Search arXiv API for papers (weekly)                     │
│  • Monitor blog RSS feeds                                   │
│  • Evaluate paper quality & relevance                       │
│  • Extract key insights                                     │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  ChromaDB Knowledge Base                     │
├─────────────────────────────────────────────────────────────┤
│  Collection: research_papers                                │
│  • Paper abstracts + metadata                               │
│  • arXiv IDs, authors, dates                                │
│  • Categories, relevance scores                             │
│  • Sentence-transformer embeddings                          │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│             Pattern Validator (Claude Skill)                 │
├─────────────────────────────────────────────────────────────┤
│  • Parse pattern documentation                              │
│  • Validate performance claims vs ChromaDB                  │
│  • Test code examples                                       │
│  • Check for deprecated APIs                                │
│  • Generate update recommendations                          │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Validation Reports                          │
├─────────────────────────────────────────────────────────────┤
│  • Outdated benchmarks flagged                              │
│  • Deprecated API warnings                                  │
│  • Missing research citations                               │
│  • Pattern update recommendations                           │
└─────────────────────────────────────────────────────────────┘
```

#### 4.2 Claude Skills

Located in [`.claude/skills/`](../../.claude/skills/):

**research-monitor** - Automated research monitoring
- Searches arXiv for RAG, LLM, healthcare AI papers
- Monitors industry blogs (Anthropic, Google, Microsoft, AWS)
- Evaluates research quality and relevance
- Ingests into ChromaDB with metadata
- Runs weekly (automated via GitHub Actions/cron)

**pattern-validator** - Pattern documentation validation
- Validates performance claims against latest research
- Tests code examples for correctness
- Checks for deprecated model versions and APIs
- Generates validation reports
- Triggers after research monitor finds new papers

#### 4.3 Implementation Scripts

Located in [`scripts/`](../../scripts/):

- **`research_monitor.py`** - Research monitoring implementation
- **`pattern_validator.py`** - Pattern validation implementation

See [Claude Skills README](../../.claude/skills/README.md) for usage documentation.

#### 4.4 Automation

**Weekly Research Cycle**:
1. Monday 9 AM: Research monitor searches arXiv (last 7 days)
2. Ingest papers into ChromaDB (quality score >= 0.5)
3. Pattern validator runs against updated research
4. Validation report generated with update recommendations
5. (Future) LLM-powered automatic pattern updates

### 5. Vendor Implementations (No Restrictions)
Each pattern should include implementations for multiple vendors. **All vendors are supported** - no restrictions:

**Cloud Platforms:**
- **Gemini**: Google Cloud Vertex AI, Gemini models (all tiers)
- **Anthropic**: Claude models and services (all tiers including enterprise)
- **Azure OpenAI**: Microsoft Azure OpenAI Service
- **AWS Bedrock**: Amazon Bedrock models
- **GCP Vertex AI**: Full Google Cloud AI platform

**Frameworks:**
- **LangChain**: Framework for LLM applications
- **Spring AI**: Java/Spring integration for AI
- **Google ADK**: Google AI Development Kit
- **Claude Skills**: Anthropic's skills/extensions (including this project's research monitoring skills)

**Cost-Effective Options** (shown as alternatives, not requirements):
- **Ollama**: Local LLM support (cost-effective option for development/testing)
- **Direct Models**: Direct access to models (local or cloud)
- **Free Tier Options**: Document free tier options where available

**Note**: Patterns should prioritize enterprise cloud platforms and premium models for healthcare production use, while showing cost-effective alternatives for development, testing, or budget-constrained scenarios.

### 5. Documentation Structure
- Pattern overview and architecture
- When to use / when not to use
- Implementation examples (multi-vendor)
- Performance characteristics
- Trade-offs and considerations
- Architecture diagrams (Mermaid)
- **Well-Architected Framework Alignment**: How pattern aligns with framework pillars
- **Architecture Decision Records (ADRs)**: Decision rationale and alternatives
- **Deployment Considerations**: Zonal, regional, multi-regional guidance

## Success Criteria

- [ ] At least 5 distinct RAG patterns documented
- [ ] Each pattern has implementations for at least 2 vendors
- [ ] Clear use case guidance for each pattern
- [ ] Working code examples for each pattern
- [ ] Architecture diagrams for each pattern
- [ ] Performance benchmarks where applicable
- [ ] Clear documentation on pattern selection

## Non-Functional Requirements

- **Maintainability**: Documentation should be easy to update
- **Discoverability**: Patterns should be easily found by use case
- **Clarity**: Documentation should be accessible to different skill levels
- **Completeness**: Each pattern should be fully documented
- **Accuracy**: All code examples should be tested and working

## Architecture Quality Framework

This architecture follows the [Google Cloud Well-Architected Framework](https://docs.cloud.google.com/architecture/framework/printable) principles:

### Operational Excellence
- Comprehensive monitoring and observability for RAG systems
- Automated testing and deployment (extending existing scripts)
- Continuous improvement through metrics and feedback
- Incident management and runbooks

### Security, Privacy, and Compliance
- Security by design with zero trust principles
- AI-specific security (Model Armor, prompt injection protection)
- Privacy considerations (local processing with Ollama)
- Compliance support (GDPR, data retention policies)

### Reliability
- High availability through redundancy and failover
- Graceful degradation strategies
- Defined reliability targets per pattern
- Circuit breakers and retry logic

### Cost Optimization
- Pattern selection based on cost-effectiveness
- Resource right-sizing and usage monitoring
- Embedding caching and batch processing
- Cost characteristics documented per pattern

### Performance Optimization
- Modular design for flexible scaling
- Resource allocation planning
- Continuous performance monitoring
- Performance targets per pattern

### Sustainability
- Resource efficiency and model selection
- Local processing options (Ollama)
- Batch optimization strategies

See [Architecture Framework Documentation](./docs/architecture-framework.md) for detailed guidance.

## Development and Testing Guidelines

### Code Reusability and Extension
- **Extend Existing Scripts**: Do not create separate test files for every question or feature
- **Build on Existing Components**: Use and extend existing scripts, examples, and utilities as much as possible
- **Avoid Silo Test Runs**: Integrate tests into existing workflows rather than creating isolated test suites
- **Incremental Enhancement**: Add functionality to existing scripts rather than creating new ones
- **Unified Testing**: Use existing example scripts as test harnesses, extending them with new test cases
- **Script Evolution**: Evolve existing scripts to handle multiple scenarios rather than creating scenario-specific files

## Dependencies

- Markdown documentation system
- Mermaid diagram support
- Code example repositories
- Multi-vendor SDK access (for examples)
- **Docling**: Document processing framework for converting documents to structured data
- **Embedded Vector Database**: File-based vector store (e.g., ChromaDB) for document storage and retrieval
- **Google ADK Agent Library**: Google's Agent Development Kit for agent-based querying and interaction
- **Ollama**: Local LLM platform for running models locally (privacy, customization, specialized tasks)
- **Web Search Tool**: Python library for dynamic web content retrieval
- **Embedding Models**: For vectorizing documents and queries (via Ollama or sentence-transformers)

## Risks and Mitigations

- **Rapid Technology Changes**: Mitigate by designing for evolution and versioning
- **Vendor API Changes**: Mitigate by abstracting patterns and documenting versions
- **Pattern Overlap**: Mitigate by clear use case guidance and decision trees
- **Maintenance Burden**: Mitigate by clear structure and contribution guidelines

## Technology Guidelines

### Vendor Selection for Healthcare Patterns
**No Restrictions**: Patterns support all vendors and platforms. Selection should be based on:
- **Use Case Requirements**: Healthcare compliance, accuracy, latency needs
- **Budget Considerations**: Cost-effective options shown but not required
- **Enterprise Needs**: Full support for enterprise cloud platforms
- **Privacy Requirements**: HIPAA compliance, data residency needs

### Cloud Platform Support
- **Google Cloud**: Vertex AI, Gemini models, GCP services
- **AWS**: Bedrock, SageMaker, AWS AI services
- **Azure**: OpenAI Service, Azure AI services
- **Anthropic**: Claude models (all tiers including enterprise)
- **Multi-Cloud**: Patterns support multi-cloud deployments

### Cost-Effective Options (Alternatives, Not Requirements)
- **Local Models (Ollama)**: Shown as cost-effective option for:
  - Development and testing
  - Budget-constrained scenarios
  - Privacy-sensitive development
  - Not a constraint for production patterns
- **Free Tiers**: Document free tier options where available
- **Efficient Architectures**: Show cost-optimized designs as alternatives

### Model Selection Strategy for Healthcare
1. **Production Healthcare**: Enterprise cloud platforms (Vertex AI, Azure OpenAI, AWS Bedrock)
2. **Development/Testing**: Cost-effective options (Ollama, free tiers) shown as alternatives
3. **Embeddings**: Cloud embedding services or local models (based on requirements)
4. **Specialized Tasks**: Any vendor/model based on use case needs
5. **Pattern Flexibility**: All patterns support any vendor - choose based on requirements

### Healthcare-Specific Considerations
- **HIPAA Compliance**: Document compliance patterns for all vendors
- **Data Residency**: Support for on-premises, hybrid, and cloud deployments
- **Accuracy Requirements**: Healthcare patterns prioritize accuracy over cost
- **Enterprise Integration**: Full support for enterprise healthcare platforms

## Future Considerations

- Integration with AI model registry
- Automated pattern testing
- Community contributions
- Pattern marketplace/registry
- Version control for patterns
- Ollama model registry integration
- Google ADK plugin ecosystem expansion

