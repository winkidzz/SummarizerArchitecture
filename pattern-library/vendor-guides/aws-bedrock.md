# AWS Bedrock Vendor Guide

## Overview

Amazon Bedrock is AWS's fully managed service providing access to foundation models from leading AI companies through a unified API. For healthcare AI summarization, Bedrock offers HIPAA-eligible services, comprehensive model selection, and deep integration with AWS healthcare and data services.

**Key Features**:
- Access to multiple foundation models (Claude, Llama, Titan, Cohere, Mistral)
- HIPAA-eligible with Business Associate Agreement (BAA)
- Native integration with AWS HealthLake (FHIR), S3, Lambda, Step Functions
- Agents for complex orchestration
- Knowledge Bases for managed RAG
- Model evaluation and customization

## Available Models

### Claude 3.5 (Anthropic via Bedrock)

**Claude 3.5 Sonnet**
- **Model ID**: `anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Context Window**: 200,000 tokens
- **Strengths**: Complex reasoning, long documents, code generation, vision
- **Use Cases**: Patient record summarization, clinical guideline analysis, multi-document synthesis
- **Pricing**: $3.00 per 1M input tokens, $15.00 per 1M output tokens

**Claude 3.5 Haiku**
- **Model ID**: `anthropic.claude-3-5-haiku-20241022-v1:0`
- **Context Window**: 200,000 tokens
- **Strengths**: Fast inference, cost-effective, good performance
- **Use Cases**: Real-time clinical alerts, SOAP note generation, high-volume processing
- **Pricing**: $0.80 per 1M input tokens, $4.00 per 1M output tokens

### Amazon Titan (AWS Native)

**Titan Text Premier**
- **Model ID**: `amazon.titan-text-premier-v1:0`
- **Context Window**: 32,000 tokens
- **Strengths**: AWS-native, optimized for enterprise, cost-effective
- **Use Cases**: Medical document summarization, structured data extraction
- **Pricing**: $0.50 per 1M input tokens, $1.50 per 1M output tokens

### Meta Llama 3.2 (via Bedrock)

**Llama 3.2 90B Instruct**
- **Model ID**: `meta.llama3-2-90b-instruct-v1:0`
- **Context Window**: 128,000 tokens
- **Strengths**: Open-source lineage, strong performance
- **Use Cases**: General medical summarization, clinical note generation
- **Pricing**: $2.65 per 1M input tokens, $3.50 per 1M output tokens

### Model Selection Guide

| Use Case | Recommended Model | Reasoning |
|----------|------------------|-----------|
| Patient record summarization (complex) | Claude 3.5 Sonnet | 200K context, superior reasoning |
| Real-time clinical data summarization | Claude 3.5 Haiku | Fast, cost-effective |
| SOAP note generation | Claude 3.5 Haiku | Structured output, fast |
| Clinical guideline analysis (long) | Claude 3.5 Sonnet | Long context, complex reasoning |
| High-volume document processing | Titan Text Premier | Cost-effective, AWS-native |
| Medical image analysis | Claude 3.5 Sonnet | Vision capabilities |

## Healthcare Compliance

### HIPAA Eligibility

- **Availability**: Yes, HIPAA-eligible with BAA
- **Scope**: Covers Bedrock models, Knowledge Bases, Agents
- **Requirement**: AWS Business Associate Addendum must be signed
- **Process**: Contact AWS Support or Account Manager to execute BAA

### Security Features

- **Encryption**: Data encrypted at rest (AES-256) and in transit (TLS 1.2+)
- **IAM**: Fine-grained access control with AWS IAM policies
- **VPC**: Deploy within VPC for network isolation
- **CloudTrail**: Audit logging for all API calls
- **CloudWatch**: Monitoring and alerting
- **KMS**: Customer-managed encryption keys

### Compliance Certifications

- HIPAA (with BAA)
- SOC 1, 2, 3
- ISO 27001, 27017, 27018
- PCI DSS Level 1
- FedRAMP Moderate (selected regions)

## Basic RAG Implementation

```python
import boto3
import json
from typing import List, Dict

# Initialize Bedrock client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

# Vector store (example using local ChromaDB)
from chromadb import Client
chroma_client = Client()
vector_store = chroma_client.get_or_create_collection(name="medical_docs")


def bedrock_rag(query: str, n_results: int = 5) -> str:
    """
    Basic RAG with AWS Bedrock (Claude 3.5 Sonnet).

    Args:
        query: User's question
        n_results: Number of documents to retrieve

    Returns:
        Generated answer
    """

    # Retrieve relevant documents
    results = vector_store.query(
        query_texts=[query],
        n_results=n_results
    )
    context = "\n\n".join(results['documents'][0])

    # Generate with Claude via Bedrock
    prompt = f"""Answer the question using the provided context.

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""

    # Bedrock API request
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.0,  # Deterministic for healthcare
        "top_p": 1.0
    }

    response = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps(request_body)
    )

    response_body = json.loads(response['body'].read())
    answer = response_body['content'][0]['text']

    return answer


# Example usage
query = "What are the latest guidelines for heart failure management?"
answer = bedrock_rag(query)
print(answer)
```

## Bedrock Knowledge Bases (Managed RAG)

AWS Bedrock provides **Knowledge Bases** - a fully managed RAG solution:

```python
import boto3

bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')


class BedrockKnowledgeBaseRAG:
    """RAG using Bedrock Knowledge Bases (fully managed)."""

    def __init__(self, knowledge_base_id: str, model_arn: str):
        """
        Initialize Bedrock Knowledge Base RAG.

        Args:
            knowledge_base_id: Knowledge Base ID from AWS Console
            model_arn: Model ARN (e.g., Claude 3.5 Sonnet)
        """
        self.knowledge_base_id = knowledge_base_id
        self.model_arn = model_arn
        self.client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

    def query(self, query: str, n_results: int = 5) -> Dict:
        """
        Query knowledge base with fully managed RAG.

        Args:
            query: User query
            n_results: Number of results to retrieve

        Returns:
            Response with answer and citations
        """

        response = self.client.retrieve_and_generate(
            input={
                'text': query
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': self.knowledge_base_id,
                    'modelArn': self.model_arn,
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'numberOfResults': n_results
                        }
                    }
                }
            }
        )

        return {
            'answer': response['output']['text'],
            'citations': response.get('citations', []),
            'session_id': response.get('sessionId')
        }


# Example usage
kb_rag = BedrockKnowledgeBaseRAG(
    knowledge_base_id='YOUR_KB_ID',
    model_arn='arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0'
)

result = kb_rag.query("What are the contraindications for beta-blockers?")
print(f"Answer: {result['answer']}")
print(f"Citations: {result['citations']}")
```

## Healthcare-Specific Features

### Integration with AWS HealthLake (FHIR)

```python
import boto3
from datetime import datetime


class BedrockHealthLakeRAG:
    """RAG with Bedrock + AWS HealthLake integration."""

    def __init__(
        self,
        datastore_id: str,
        bedrock_model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    ):
        """
        Initialize Bedrock + HealthLake RAG.

        Args:
            datastore_id: HealthLake data store ID
            bedrock_model_id: Bedrock model ID
        """
        self.datastore_id = datastore_id
        self.model_id = bedrock_model_id

        self.healthlake = boto3.client('healthlake', region_name='us-east-1')
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

    def get_patient_fhir_data(self, patient_id: str) -> Dict:
        """
        Retrieve patient data from HealthLake.

        Args:
            patient_id: Patient ID

        Returns:
            FHIR bundle with patient data
        """

        # Search for patient resources
        # Note: Actual implementation requires proper FHIR query construction
        search_params = {
            'DatastoreId': self.datastore_id,
            'ResourceType': 'Patient',
            'SearchQuery': f'_id={patient_id}'
        }

        # In production, use proper FHIR search API
        # This is a simplified example
        patient_bundle = {
            'resourceType': 'Bundle',
            'entry': []
        }

        return patient_bundle

    def summarize_patient_record(self, patient_id: str) -> str:
        """
        Summarize patient's medical record from HealthLake.

        Args:
            patient_id: Patient ID

        Returns:
            Clinical summary
        """

        # Step 1: Retrieve structured FHIR data from HealthLake
        fhir_data = self.get_patient_fhir_data(patient_id)

        # Step 2: Format FHIR data for LLM
        formatted_data = self._format_fhir_bundle(fhir_data)

        # Step 3: Generate summary with Bedrock
        prompt = f"""Generate a comprehensive patient summary from the FHIR data.

FHIR DATA:
{formatted_data}

Generate a summary including:
1. Active conditions and diagnoses
2. Current medications
3. Recent procedures and encounters
4. Key lab results and vital signs
5. Clinical trajectory

CLINICAL SUMMARY:"""

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0
        }

        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body)
        )

        response_body = json.loads(response['body'].read())
        summary = response_body['content'][0]['text']

        return summary

    def _format_fhir_bundle(self, bundle: Dict) -> str:
        """Format FHIR bundle for LLM consumption."""
        # Implement FHIR resource formatting
        return json.dumps(bundle, indent=2)


# Example usage
healthlake_rag = BedrockHealthLakeRAG(
    datastore_id='YOUR_DATASTORE_ID'
)

summary = healthlake_rag.summarize_patient_record(patient_id='12345')
print(summary)
```

## Bedrock Agents for Complex Workflows

Bedrock Agents enable agentic RAG with multi-step reasoning:

```python
import boto3


def create_clinical_assistant_agent():
    """
    Create Bedrock Agent for clinical assistance.

    Agents can orchestrate multiple steps:
    1. Query Knowledge Base
    2. Call Lambda functions
    3. Make decisions
    4. Return structured responses
    """

    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')

    # Define agent
    agent_config = {
        'agentName': 'ClinicalAssistantAgent',
        'foundationModel': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
        'instruction': """You are a clinical assistant helping healthcare providers
        summarize patient information and answer clinical questions. Always cite sources
        and flag when information may require clinical judgment.""",
        'agentResourceRoleArn': 'arn:aws:iam::ACCOUNT_ID:role/BedrockAgentRole'
    }

    # Create agent
    response = bedrock_agent.create_agent(**agent_config)

    agent_id = response['agent']['agentId']

    print(f"Created agent: {agent_id}")

    return agent_id


def query_clinical_agent(agent_id: str, query: str) -> str:
    """Query the clinical assistant agent."""

    bedrock_agent_runtime = boto3.client(
        'bedrock-agent-runtime',
        region_name='us-east-1'
    )

    response = bedrock_agent_runtime.invoke_agent(
        agentId=agent_id,
        agentAliasId='TSTALIASID',  # Use actual alias ID
        sessionId='unique-session-id',
        inputText=query
    )

    # Process streaming response
    answer = ""
    for event in response['completion']:
        if 'chunk' in event:
            chunk = event['chunk']
            answer += chunk['bytes'].decode('utf-8')

    return answer
```

## Prompt Caching (Claude via Bedrock)

Bedrock supports Claude's prompt caching for cost savings:

```python
def bedrock_rag_with_caching(query: str, guidelines_context: str) -> str:
    """
    RAG with prompt caching for repeated queries against same guidelines.

    Caching reduces costs by 90% for cached prompt portions.

    Args:
        query: User query
        guidelines_context: Large clinical guidelines (cached)

    Returns:
        Generated answer
    """

    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

    # System prompt with cache control
    system = [
        {
            "type": "text",
            "text": "You are a clinical decision support assistant."
        },
        {
            "type": "text",
            "text": f"CLINICAL GUIDELINES:\n{guidelines_context}",
            "cache_control": {"type": "ephemeral"}  # Cache this portion
        }
    ]

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "system": system,
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ],
        "temperature": 0.0
    }

    response = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps(request_body)
    )

    response_body = json.loads(response['body'].read())

    # Check cache usage
    usage = response_body.get('usage', {})
    print(f"Cache read tokens: {usage.get('cache_read_input_tokens', 0)}")
    print(f"Cache creation tokens: {usage.get('cache_creation_input_tokens', 0)}")

    return response_body['content'][0]['text']


# Example: Query against large guidelines (cached after first call)
guidelines = """[500-page clinical guidelines for heart failure management...]"""

query1 = "What are beta-blocker contraindications?"
answer1 = bedrock_rag_with_caching(query1, guidelines)  # Creates cache

query2 = "What are ACE inhibitor contraindications?"
answer2 = bedrock_rag_with_caching(query2, guidelines)  # Uses cache (90% cheaper)
```

## Cost Optimization

### Model Selection for Cost

```python
def adaptive_model_routing(query: str, complexity_threshold: float = 0.7) -> str:
    """
    Route to Claude Haiku (cheap) or Sonnet (expensive) based on complexity.

    Args:
        query: User query
        complexity_threshold: Threshold for Sonnet vs Haiku

    Returns:
        Generated answer
    """

    # Assess query complexity
    complexity = assess_complexity(query)

    if complexity > complexity_threshold:
        model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
        print("Using Claude 3.5 Sonnet (complex query)")
    else:
        model_id = "anthropic.claude-3-5-haiku-20241022-v1:0"
        print("Using Claude 3.5 Haiku (simple query) - 4x cheaper")

    # Retrieve and generate
    results = vector_store.query(query_texts=[query], n_results=5)
    context = "\n\n".join(results['documents'][0])

    prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0
    }

    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(request_body)
    )

    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']


def assess_complexity(query: str) -> float:
    """Simple complexity scoring."""
    factors = {
        'long_query': len(query.split()) > 20,
        'medical_terms': count_medical_terms(query) > 3,
        'multi_part': '?' in query[:-1]
    }
    return sum(factors.values()) / len(factors)
```

## Security Best Practices

### IAM Policies for Bedrock

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockInvokeModel",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-haiku-20241022-v1:0"
      ]
    },
    {
      "Sid": "BedrockKnowledgeBase",
      "Effect": "Allow",
      "Action": [
        "bedrock:RetrieveAndGenerate",
        "bedrock:Retrieve"
      ],
      "Resource": "arn:aws:bedrock:us-east-1:ACCOUNT_ID:knowledge-base/*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    },
    {
      "Sid": "DenyPHILogging",
      "Effect": "Deny",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*",
      "Condition": {
        "StringLike": {
          "aws:RequestTag/PHI": "true"
        }
      }
    }
  ]
}
```

### VPC Endpoints for Private Access

```python
# Example: Use VPC endpoint for Bedrock (no internet gateway required)

import boto3
from botocore.config import Config

# Configure client to use VPC endpoint
config = Config(
    region_name='us-east-1',
    retries={'max_attempts': 3, 'mode': 'standard'}
)

# Bedrock accessed via VPC endpoint (no public internet)
bedrock = boto3.client(
    'bedrock-runtime',
    config=config,
    endpoint_url='https://vpce-XXXXX.bedrock-runtime.us-east-1.vpce.amazonaws.com'
)
```

## Performance Optimization

### Streaming Responses

```python
def stream_bedrock_response(query: str, context: str):
    """
    Stream Bedrock response for real-time display.

    Args:
        query: User query
        context: Retrieved context
    """

    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

    prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0
    }

    response = bedrock.invoke_model_with_response_stream(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps(request_body)
    )

    # Stream response chunks
    stream = response['body']
    full_response = ""

    for event in stream:
        chunk = event.get('chunk')
        if chunk:
            chunk_data = json.loads(chunk['bytes'].decode())

            if chunk_data['type'] == 'content_block_delta':
                delta = chunk_data['delta']
                if delta['type'] == 'text_delta':
                    text = delta['text']
                    print(text, end='', flush=True)
                    full_response += text

    return full_response
```

## Related Patterns

- [Basic RAG](../patterns/basic-rag.md)
- [Contextual Retrieval](../patterns/contextual-retrieval.md)
- [Anthropic Claude Vendor Guide](./anthropic-claude.md)

## References

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Bedrock Models](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)
- [AWS HealthLake](https://docs.aws.amazon.com/healthlake/)
- [Bedrock HIPAA Compliance](https://aws.amazon.com/compliance/hipaa-compliance/)

## Version History

- **v1.0** (2025-01-09): Initial AWS Bedrock vendor guide with Claude models, Knowledge Bases, HealthLake integration, Agents, and security best practices
