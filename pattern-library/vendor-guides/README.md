# Vendor Implementation Guides

This directory contains vendor-specific implementation guides for healthcare summarization patterns.

## Available Guides

### Cloud Platforms
- [Google Cloud Vertex AI](./vertex-ai-guide.md) - Gemini models, Vertex AI
- [Azure OpenAI](./azure-openai-guide.md) - GPT-4, Azure AI services
- [AWS Bedrock](./aws-bedrock-guide.md) - Claude, Titan, Bedrock models
- [Anthropic Claude](./anthropic-guide.md) - Claude models (all tiers)

### Frameworks
- [LangChain](./langchain-guide.md) - Multi-vendor framework
- [Spring AI](./spring-ai-guide.md) - Java/Spring integration
- [Google ADK](./google-adk.md) - Agent Development Kit

### Cost-Effective Options
- [Ollama](./ollama-guide.md) - Local LLM platform
- [Direct Models](./direct-models-guide.md) - Direct model access

## Guide Structure

Each vendor guide includes:
- **Overview**: Vendor capabilities and strengths
- **Setup**: Installation and configuration
- **Pattern Implementations**: Code examples for each RAG pattern
- **Best Practices**: Vendor-specific recommendations
- **Healthcare Considerations**: HIPAA compliance, data residency
- **Cost Information**: Pricing models and optimization
- **Troubleshooting**: Common issues and solutions

## Vendor Selection

See [Vendor Selection Guide](../vendor-selection-guide.md) for help choosing the right vendor.

## Quick Reference

| Vendor | Best For | Healthcare Support | Cost |
|--------|----------|-------------------|------|
| **Vertex AI** | GCP ecosystems, enterprise | ✅ Full HIPAA support | Enterprise |
| **Azure OpenAI** | Azure ecosystems, enterprise | ✅ Full HIPAA support | Enterprise |
| **AWS Bedrock** | AWS ecosystems, enterprise | ✅ Full HIPAA support | Enterprise |
| **Anthropic** | High accuracy, long context | ✅ Enterprise tiers | Enterprise |
| **LangChain** | Multi-vendor, flexibility | ✅ Via underlying models | Variable |
| **Spring AI** | Java/Spring applications | ✅ Via underlying models | Variable |
| **Ollama** | Development, local processing | ⚠️ Development only | Free |
| **Direct Models** | Custom workflows | ⚠️ Depends on model | Variable |

## Related Documentation

- [Vendor Selection Guide](../vendor-selection-guide.md): How to choose vendors
- [Healthcare Focus](../healthcare-focus.md): Healthcare-specific considerations
- [RAG Patterns](../patterns/README.md): Pattern implementations
- [Architecture Framework](../architecture-framework.md): Well-Architected principles

## Contributing

When adding vendor guides:
1. Follow the vendor guide template
2. Include code examples for all major patterns
3. Document healthcare-specific features
4. Provide troubleshooting guidance
5. Keep examples current with latest APIs
