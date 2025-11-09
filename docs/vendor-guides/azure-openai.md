# Azure OpenAI Vendor Guide

## Overview

Azure OpenAI Service provides access to OpenAI's GPT-4 and other models through Microsoft Azure's enterprise cloud platform. For healthcare AI, Azure OpenAI offers HIPAA BAA compliance, integration with Azure Health Data Services (FHIR), and enterprise-grade security within the Microsoft ecosystem.

**Key Features**:
- GPT-4 Turbo with 128K context window
- HIPAA BAA available for healthcare compliance
- Integration with Azure Health Data Services (FHIR)
- Enterprise security and Microsoft ecosystem integration
- Content filtering and responsible AI features
- Azure Active Directory (AAD) authentication

## Available Models

### GPT-4 Turbo (Latest)
- **Deployment Name**: Custom (you choose)
- **Model Version**: `gpt-4` (1106-preview or later)
- **Context Window**: 128,000 tokens
- **Strengths**: Best reasoning, complex tasks, long documents
- **Use Cases**: Patient record analysis, clinical decision support
- **Pricing**: ~$10 per 1M input tokens, ~$30 per 1M output tokens

### GPT-4
- **Deployment Name**: Custom
- **Model Version**: `gpt-4` (0613 or later)
- **Context Window**: 8,192 tokens
- **Strengths**: High quality, reliable
- **Use Cases**: General healthcare summarization
- **Pricing**: ~$30 per 1M input tokens, ~$60 per 1M output tokens

### GPT-3.5 Turbo
- **Deployment Name**: Custom
- **Model Version**: `gpt-35-turbo` (1106)
- **Context Window**: 16,385 tokens
- **Strengths**: Fast, cost-effective
- **Use Cases**: High-volume processing, simple summaries
- **Pricing**: ~$0.50 per 1M input tokens, ~$1.50 per 1M output tokens

### Model Selection Guide

| Use Case | Recommended Model | Reasoning |
|----------|------------------|-----------|
| Complex patient record analysis | GPT-4 Turbo | Best reasoning, 128K context |
| SOAP note generation | GPT-3.5 Turbo | Fast, cost-effective, structured |
| Clinical guideline Q&A | GPT-4 Turbo | Long context, complex reasoning |
| Real-time alerts | GPT-3.5 Turbo | Low latency, affordable at scale |
| Medical coding assistance | GPT-4 | High accuracy required |

## Healthcare Compliance

### HIPAA BAA
- **Availability**: Yes, BAA available
- **Scope**: Covers Azure OpenAI Service, Azure Health Data Services
- **Requirement**: Enterprise Agreement with Microsoft
- **Process**: Request BAA through Microsoft account team
- **Documentation**: [Azure HIPAA Compliance](https://azure.microsoft.com/en-us/resources/microsoft-azure-compliance-offerings/)

### Security Features
- **Encryption**: Data encrypted at rest (AES-256) and in transit (TLS 1.2+)
- **AAD Authentication**: Azure Active Directory integration
- **RBAC**: Role-based access control
- **Private Endpoints**: VNet integration for network isolation
- **Customer-Managed Keys**: Bring your own key (BYOK)
- **Audit Logging**: Azure Monitor and Log Analytics

### Compliance Certifications
- HIPAA (with BAA)
- SOC 2 Type II
- ISO 27001
- ISO 27018 (privacy)
- FedRAMP (US government)

## Basic RAG Implementation

```python
from openai import AzureOpenAI
import os
from document_store.storage.vector_store import VectorStore

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-10-21",  # Latest stable version
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")  # e.g., https://your-resource.openai.azure.com/
)

# Vector store for RAG
vector_store = VectorStore()

def azure_openai_rag(query: str, deployment_name: str = "gpt-4-turbo", n_results: int = 5) -> str:
    """
    Basic RAG with Azure OpenAI.

    Args:
        query: User's question
        deployment_name: Azure deployment name (you created this in Azure portal)
        n_results: Number of documents to retrieve

    Returns:
        Generated answer
    """

    # Retrieve relevant documents
    results = vector_store.query(query, n_results=n_results)
    context = "\n\n".join(results['documents'])

    # Generate with Azure OpenAI
    response = client.chat.completions.create(
        model=deployment_name,  # Your deployment name, not model name
        messages=[
            {"role": "system", "content": "You are a healthcare AI assistant. Provide accurate, evidence-based answers."},
            {"role": "user", "content": f"""Answer the question using the provided context.

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""}
        ],
        temperature=0.1,  # Low temperature for healthcare accuracy
        max_tokens=2048
    )

    return response.choices[0].message.content


# Example usage
query = "What are the contraindications for ACE inhibitors?"
answer = azure_openai_rag(query, deployment_name="my-gpt4-deployment")
print(answer)
```

## Integration with Azure Health Data Services (FHIR)

```python
from azure.identity import DefaultAzureCredential
from azure.healthdataaiservices.fhir import FhirService
import json

class AzureHealthcareRAG:
    """RAG with Azure OpenAI + Azure Health Data Services integration."""

    def __init__(
        self,
        openai_endpoint: str,
        openai_deployment: str,
        fhir_endpoint: str
    ):
        # Azure OpenAI client
        self.openai_client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-10-21",
            azure_endpoint=openai_endpoint
        )
        self.deployment = openai_deployment

        # FHIR client with AAD authentication
        credential = DefaultAzureCredential()
        self.fhir_client = FhirService(
            endpoint=fhir_endpoint,
            credential=credential
        )

    def get_patient_fhir_data(self, patient_id: str) -> dict:
        """
        Retrieve patient data from Azure FHIR service.

        Args:
            patient_id: Patient ID

        Returns:
            FHIR bundle with patient data
        """

        # Search for patient resources using $everything operation
        response = self.fhir_client.resources.read(
            resource_type="Patient",
            resource_id=patient_id,
            operation="$everything"
        )

        return response.as_dict()

    def summarize_patient_record(self, patient_id: str) -> str:
        """
        Summarize patient's complete medical record from Azure FHIR.

        Args:
            patient_id: Patient ID

        Returns:
            Clinical summary
        """

        # Step 1: Retrieve structured FHIR data
        fhir_bundle = self.get_patient_fhir_data(patient_id)

        # Step 2: Extract key FHIR resources
        conditions = self._extract_conditions(fhir_bundle)
        medications = self._extract_medications(fhir_bundle)
        observations = self._extract_observations(fhir_bundle)

        # Step 3: Retrieve unstructured clinical notes (from vector store)
        clinical_notes = vector_store.query(
            query=f"Clinical notes for patient {patient_id}",
            filter={"patient_id": patient_id},
            n_results=10
        )

        # Step 4: Combine structured + unstructured
        structured_summary = f"""
ACTIVE CONDITIONS: {json.dumps(conditions, indent=2)}

CURRENT MEDICATIONS: {json.dumps(medications, indent=2)}

RECENT OBSERVATIONS: {json.dumps(observations, indent=2)}
"""
        unstructured_context = "\n\n".join(clinical_notes['documents'])

        # Step 5: Generate comprehensive summary
        response = self.openai_client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": "You are a clinical AI assistant. Summarize patient data accurately."},
                {"role": "user", "content": f"""Generate a comprehensive patient summary.

STRUCTURED DATA (FHIR):
{structured_summary}

CLINICAL NOTES:
{unstructured_context}

Generate a summary including:
1. Active diagnoses and conditions
2. Current medication regimen
3. Recent vital signs and lab results
4. Clinical trajectory
5. Important alerts or concerns

CLINICAL SUMMARY:"""}
            ],
            temperature=0.0,  # Deterministic for clinical accuracy
            max_tokens=2048
        )

        return response.choices[0].message.content

    def _extract_conditions(self, fhir_bundle: dict) -> list:
        """Extract active conditions from FHIR bundle."""
        conditions = []
        for entry in fhir_bundle.get('entry', []):
            resource = entry.get('resource', {})
            if resource.get('resourceType') == 'Condition':
                if resource.get('clinicalStatus', {}).get('coding', [{}])[0].get('code') == 'active':
                    conditions.append({
                        'condition': resource.get('code', {}).get('text', 'Unknown'),
                        'onset': resource.get('onsetDateTime', 'Unknown'),
                    })
        return conditions

    def _extract_medications(self, fhir_bundle: dict) -> list:
        """Extract active medications from FHIR bundle."""
        medications = []
        for entry in fhir_bundle.get('entry', []):
            resource = entry.get('resource', {})
            if resource.get('resourceType') == 'MedicationRequest':
                if resource.get('status') == 'active':
                    medications.append({
                        'medication': resource.get('medicationCodeableConcept', {}).get('text', 'Unknown'),
                        'dosage': resource.get('dosageInstruction', [{}])[0].get('text', 'Unknown'),
                    })
        return medications

    def _extract_observations(self, fhir_bundle: dict) -> list:
        """Extract recent observations from FHIR bundle."""
        observations = []
        for entry in fhir_bundle.get('entry', []):
            resource = entry.get('resource', {})
            if resource.get('resourceType') == 'Observation':
                observations.append({
                    'type': resource.get('code', {}).get('text', 'Unknown'),
                    'value': resource.get('valueQuantity', {}).get('value', 'N/A'),
                    'unit': resource.get('valueQuantity', {}).get('unit', ''),
                    'date': resource.get('effectiveDateTime', 'Unknown'),
                })
        return observations[:10]  # Limit to most recent 10


# Example usage
healthcare_rag = AzureHealthcareRAG(
    openai_endpoint="https://my-openai.openai.azure.com/",
    openai_deployment="gpt-4-turbo",
    fhir_endpoint="https://my-fhir.azurehealthcareapis.com"
)

summary = healthcare_rag.summarize_patient_record(patient_id="12345")
print(summary)
```

## Content Filtering for Healthcare

Azure OpenAI includes content filtering that may block medical terminology. Configure appropriately for healthcare:

```python
def configure_content_filtering(query: str, deployment_name: str) -> str:
    """
    Configure content filtering for healthcare use.

    Azure allows requesting modifications for healthcare applications.
    """

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": "You are a healthcare AI assistant."},
            {"role": "user", "content": query}
        ],
        temperature=0.1,
        # Note: Content filter configuration is done at deployment level in Azure portal
        # For healthcare, request exemptions through Azure support
    )

    # Handle content filtering responses
    if hasattr(response.choices[0], 'content_filter_results'):
        filter_results = response.choices[0].content_filter_results
        if any(filter_results.values()):
            print(f"Content filtering triggered: {filter_results}")
            # Log and handle appropriately for healthcare context

    return response.choices[0].message.content
```

## Structured Outputs with Function Calling

```python
def generate_structured_soap_note(encounter_data: str, deployment_name: str) -> dict:
    """
    Generate SOAP note with structured output using function calling.

    Args:
        encounter_data: Raw encounter information
        deployment_name: Azure deployment name

    Returns:
        Structured SOAP note as dictionary
    """

    # Define SOAP note schema as a function
    soap_function = {
        "name": "create_soap_note",
        "description": "Create a structured SOAP note from encounter data",
        "parameters": {
            "type": "object",
            "properties": {
                "subjective": {
                    "type": "string",
                    "description": "Subjective findings (patient's complaints, history)"
                },
                "objective": {
                    "type": "object",
                    "properties": {
                        "vital_signs": {"type": "string"},
                        "physical_exam": {"type": "string"},
                        "lab_results": {"type": "string"}
                    }
                },
                "assessment": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "diagnosis": {"type": "string"},
                            "icd10_code": {"type": "string"}
                        }
                    }
                },
                "plan": {
                    "type": "object",
                    "properties": {
                        "medications": {"type": "array", "items": {"type": "string"}},
                        "procedures": {"type": "array", "items": {"type": "string"}},
                        "follow_up": {"type": "string"}
                    }
                }
            },
            "required": ["subjective", "objective", "assessment", "plan"]
        }
    }

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": "You are a medical scribe AI. Generate accurate SOAP notes."},
            {"role": "user", "content": f"Create a SOAP note from this encounter:\n\n{encounter_data}"}
        ],
        functions=[soap_function],
        function_call={"name": "create_soap_note"},
        temperature=0.1
    )

    # Extract structured SOAP note
    import json
    function_call = response.choices[0].message.function_call
    soap_note = json.loads(function_call.arguments)

    return soap_note


# Example usage
encounter = """
65yo male presents with chest pain. Pain started 2 hours ago, 7/10 severity, radiating to left arm.
BP 145/92, HR 88, RR 18, SpO2 97% on RA.
ECG shows ST elevation in leads II, III, aVF.
"""

soap_note = generate_structured_soap_note(encounter, deployment_name="gpt-4")
print(json.dumps(soap_note, indent=2))
```

## Cost Optimization

### Deployment Management

```python
class AzureCostOptimizer:
    """Optimize Azure OpenAI costs through smart deployment selection."""

    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-10-21",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

        # Multiple deployments for different use cases
        self.deployments = {
            "simple": "gpt-35-turbo",      # $0.50/$1.50 per 1M tokens
            "standard": "gpt-4",            # $30/$60 per 1M tokens
            "complex": "gpt-4-turbo",       # $10/$30 per 1M tokens
        }

    def adaptive_query(self, query: str, context: str) -> str:
        """Route to appropriate deployment based on complexity."""

        # Assess query complexity
        complexity = self._assess_complexity(query)

        if complexity == "simple":
            deployment = self.deployments["simple"]
            print(f"Using GPT-3.5 Turbo (simple query) - Low cost")
        elif complexity == "complex":
            deployment = self.deployments["complex"]
            print(f"Using GPT-4 Turbo (complex query) - Moderate cost")
        else:
            deployment = self.deployments["standard"]
            print(f"Using GPT-4 (standard query) - High cost")

        response = self.client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a healthcare AI assistant."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ],
            temperature=0.1,
            max_tokens=2048
        )

        return response.choices[0].message.content

    def _assess_complexity(self, query: str) -> str:
        """Simple heuristic for query complexity."""
        if len(query.split()) < 15 and '?' not in query[:-1]:
            return "simple"
        elif any(term in query.lower() for term in ['complex', 'multi', 'differential', 'compare']):
            return "complex"
        else:
            return "standard"
```

### Token Usage Tracking

```python
def track_azure_openai_usage(response) -> dict:
    """
    Track token usage and cost for Azure OpenAI calls.

    Args:
        response: Azure OpenAI API response

    Returns:
        Usage metrics and estimated cost
    """

    usage = response.usage

    # Pricing (example - check Azure pricing for current rates)
    pricing = {
        "gpt-35-turbo": {"input": 0.0005, "output": 0.0015},  # per 1K tokens
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    }

    model = response.model  # Deployment name
    input_cost = (usage.prompt_tokens / 1000) * pricing.get(model, {}).get("input", 0)
    output_cost = (usage.completion_tokens / 1000) * pricing.get(model, {}).get("output", 0)

    return {
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
        "input_cost": f"${input_cost:.4f}",
        "output_cost": f"${output_cost:.4f}",
        "total_cost": f"${input_cost + output_cost:.4f}",
    }


# Example usage
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": "What is diabetes?"}],
    max_tokens=500
)

usage_metrics = track_azure_openai_usage(response)
print(f"Usage: {usage_metrics}")
```

## Security Best Practices

### Private Endpoints and VNet Integration

```python
# Example configuration for Private Endpoint (infrastructure as code)
# Deploy via Azure CLI or Terraform

# Azure CLI example:
"""
# Create private endpoint
az network private-endpoint create \
    --resource-group my-rg \
    --name my-openai-private-endpoint \
    --vnet-name my-vnet \
    --subnet my-subnet \
    --private-connection-resource-id /subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account-name} \
    --group-id account \
    --connection-name my-openai-connection

# Disable public network access
az cognitiveservices account update \
    --name my-openai-account \
    --resource-group my-rg \
    --public-network-access Disabled
"""
```

### Managed Identity Authentication

```python
from azure.identity import ManagedIdentityCredential

def use_managed_identity():
    """
    Use Azure Managed Identity instead of API keys (best practice).

    Requires:
    1. Enable Managed Identity on Azure resource (VM, App Service, etc.)
    2. Grant Cognitive Services User role to Managed Identity
    """

    # Authenticate with Managed Identity
    credential = ManagedIdentityCredential()

    # Get token for Azure OpenAI
    token = credential.get_token("https://cognitiveservices.azure.com/.default")

    # Use token with Azure OpenAI
    client = AzureOpenAI(
        azure_ad_token=token.token,
        api_version="2024-10-21",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    # Now use client as normal (no API key needed!)
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": "Test query"}]
    )

    return response.choices[0].message.content
```

## Performance Optimization

### Batch Processing with Async

```python
import asyncio
from openai import AsyncAzureOpenAI

async_client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-10-21",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

async def summarize_one_record(patient_id: str, deployment: str) -> str:
    """Summarize one patient record asynchronously."""

    # Retrieve data
    results = vector_store.query(
        query=f"Patient {patient_id} medical record",
        filter={"patient_id": patient_id},
        n_results=5
    )
    context = "\n\n".join(results['documents'])

    # Generate summary
    response = await async_client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "Summarize patient record concisely."},
            {"role": "user", "content": f"Patient {patient_id}:\n\n{context}"}
        ],
        temperature=0.0,
        max_tokens=1024
    )

    return response.choices[0].message.content


async def batch_summarize(patient_ids: list[str], deployment: str = "gpt-35-turbo") -> list[str]:
    """Batch process multiple patient summaries in parallel."""

    tasks = [summarize_one_record(pid, deployment) for pid in patient_ids]
    summaries = await asyncio.gather(*tasks)

    return summaries


# Example usage
patient_ids = ["12345", "67890", "11111", "22222", "33333"]
summaries = asyncio.run(batch_summarize(patient_ids))
print(f"Summarized {len(summaries)} records")
```

## Related Patterns
- [Basic RAG](../patterns/basic-rag.md)
- [Structured Outputs](../patterns/structured-outputs.md)
- [Cost Optimization Strategies](../patterns/cost-optimization.md)

## References
- [Azure OpenAI Service Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure Health Data Services](https://learn.microsoft.com/en-us/azure/healthcare-apis/)
- [Azure OpenAI HIPAA Compliance](https://learn.microsoft.com/en-us/azure/compliance/offerings/offering-hipaa-us)
- [Azure OpenAI Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/)

## Version History
- **v1.0** (2025-01-09): Initial Azure OpenAI vendor guide with GPT-4/3.5 models, Azure Health Data Services integration, structured outputs, security best practices, and cost optimization

