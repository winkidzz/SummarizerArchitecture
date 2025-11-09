# Google Vertex AI Vendor Guide

## Overview

Google Vertex AI is Google Cloud's unified AI platform providing access to Gemini models, custom model training, and enterprise AI infrastructure. For healthcare AI summarization, Vertex AI offers HIPAA-compliant services, strong integration with Google Cloud Healthcare API (FHIR), and comprehensive model options.

**Key Features**:
- Gemini 1.5 Pro/Flash models with up to 2M token context window
- HIPAA BAA available for healthcare compliance
- Native integration with Google Cloud Healthcare API (FHIR)
- Multimodal capabilities (text, images, video, audio)
- Enterprise security and compliance (SOC 2, ISO 27001)

## Available Models

### Gemini 1.5 Pro
- **Model ID**: `gemini-1.5-pro-002`
- **Context Window**: 2,000,000 tokens (2M) - longest available
- **Strengths**: Complex reasoning, long document analysis, multimodal understanding
- **Use Cases**: Patient record summarization (entire medical histories), clinical guideline analysis
- **Pricing**: $1.25 per 1M input tokens, $5.00 per 1M output tokens (prompts < 128K tokens)

### Gemini 1.5 Flash
- **Model ID**: `gemini-1.5-flash-002`
- **Context Window**: 1,000,000 tokens (1M)
- **Strengths**: Fast inference, cost-effective, good performance
- **Use Cases**: Real-time clinical alerts, quick summaries, high-volume processing
- **Pricing**: $0.075 per 1M input tokens, $0.30 per 1M output tokens (prompts < 128K tokens)

### Model Selection Guide

| Use Case | Recommended Model | Reasoning |
|----------|------------------|-----------|
| Patient record summarization (10+ years) | Gemini 1.5 Pro | 2M context window handles entire history |
| Real-time clinical data summarization | Gemini 1.5 Flash | Fast, cost-effective |
| Clinical guideline analysis (500+ pages) | Gemini 1.5 Pro | Long context, complex reasoning |
| SOAP note generation | Gemini 1.5 Flash | Fast, structured output |
| Medical image analysis | Gemini 1.5 Pro | Better multimodal understanding |

## Healthcare Compliance

### HIPAA BAA
- **Availability**: Yes, BAA available for Enterprise tier
- **Scope**: Covers Vertex AI, Cloud Healthcare API, Cloud Storage
- **Requirement**: Google Cloud Enterprise Agreement
- **Process**: Request BAA through Google Cloud sales

### Security Features
- **Encryption**: Data encrypted at rest (AES-256) and in transit (TLS 1.2+)
- **IAM**: Fine-grained access control with Cloud IAM
- **Audit Logging**: Cloud Audit Logs for all API calls
- **VPC Service Controls**: Network security perimeter for PHI
- **Customer-Managed Keys**: CMEK support for encryption keys

### Compliance Certifications
- HIPAA (with BAA)
- SOC 2 Type II
- ISO 27001
- ISO 27017 (cloud security)
- ISO 27018 (privacy)

## Basic RAG Implementation

```python
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import aiplatform
from document_store.storage.vector_store import VectorStore

# Initialize Vertex AI
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"  # or your region

vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize model
model = GenerativeModel("gemini-1.5-pro-002")

# Vector store for RAG
vector_store = VectorStore()

def vertex_rag(query: str, n_results: int = 5) -> str:
    """
    Basic RAG with Vertex AI Gemini.

    Args:
        query: User's question
        n_results: Number of documents to retrieve

    Returns:
        Generated answer
    """

    # Retrieve relevant documents
    results = vector_store.query(query, n_results=n_results)
    context = "\n\n".join(results['documents'])

    # Generate with Gemini
    prompt = f"""Answer the question using the provided context.

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""

    response = model.generate_content(prompt)
    return response.text


# Example usage
query = "What are the latest guidelines for heart failure management?"
answer = vertex_rag(query)
print(answer)
```

## Healthcare-Specific Features

### Integration with Cloud Healthcare API (FHIR)

```python
from google.cloud import healthcare_v1
from google.oauth2 import service_account

class VertexHealthcareRAG:
    """RAG with Vertex AI + Cloud Healthcare API integration."""

    def __init__(self, project_id: str, location: str, dataset_id: str, fhir_store_id: str):
        self.project_id = project_id
        self.location = location
        self.dataset_id = dataset_id
        self.fhir_store_id = fhir_store_id

        # Initialize Healthcare API client
        self.fhir_client = healthcare_v1.FhirStoresServiceClient()

        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-1.5-pro-002")

    def get_patient_fhir_data(self, patient_id: str) -> dict:
        """
        Retrieve patient data from FHIR store.

        Args:
            patient_id: Patient ID

        Returns:
            FHIR bundle with patient data
        """

        fhir_store_name = self.fhir_client.fhir_store_path(
            self.project_id,
            self.location,
            self.dataset_id,
            self.fhir_store_id
        )

        # Search for patient resources
        search_url = f"{fhir_store_name}/fhir/Patient/{patient_id}/$everything"

        request = healthcare_v1.SearchResourcesRequest(
            parent=fhir_store_name,
            resource_type="Patient",
        )

        # Execute FHIR search
        # In production, use proper FHIR client library
        patient_bundle = {}  # Placeholder - implement FHIR API call

        return patient_bundle

    def summarize_patient_record(self, patient_id: str) -> str:
        """
        Summarize patient's complete medical record.

        Args:
            patient_id: Patient ID

        Returns:
            Clinical summary
        """

        # Step 1: Retrieve structured FHIR data
        fhir_data = self.get_patient_fhir_data(patient_id)

        # Step 2: Retrieve unstructured clinical notes (from vector store)
        clinical_notes = vector_store.query(
            query=f"Clinical notes for patient {patient_id}",
            filter={"patient_id": patient_id},
            n_results=10
        )

        # Step 3: Combine structured + unstructured data
        structured_summary = self._format_fhir_data(fhir_data)
        unstructured_context = "\n\n".join(clinical_notes['documents'])

        # Step 4: Generate comprehensive summary
        prompt = f"""Generate a comprehensive patient summary.

STRUCTURED DATA (FHIR):
{structured_summary}

CLINICAL NOTES:
{unstructured_context}

Generate a summary including:
1. Active conditions and diagnoses
2. Current medications
3. Recent procedures and encounters
4. Key lab results and vital signs
5. Clinical trajectory and trends

CLINICAL SUMMARY:"""

        response = self.model.generate_content(prompt)
        return response.text

    def _format_fhir_data(self, fhir_bundle: dict) -> str:
        """Format FHIR bundle for LLM consumption."""
        # Implement FHIR resource formatting
        return "Formatted FHIR data..."


# Example usage
healthcare_rag = VertexHealthcareRAG(
    project_id="my-healthcare-project",
    location="us-central1",
    dataset_id="patient-data",
    fhir_store_id="production-fhir"
)

summary = healthcare_rag.summarize_patient_record(patient_id="12345")
print(summary)
```

## Long Context Window Strategies

Gemini 1.5 Pro's 2M token context window enables unique healthcare use cases:

```python
def summarize_longitudinal_record(patient_id: str, years: int = 10) -> str:
    """
    Summarize entire patient history in single prompt.

    With 2M tokens, can fit ~10-15 years of comprehensive medical records.

    Args:
        patient_id: Patient ID
        years: Years of history to include

    Returns:
        Longitudinal summary
    """

    # Retrieve all clinical notes from past N years
    # Gemini 1.5 Pro can handle massive context
    all_notes = vector_store.query(
        query=f"All clinical notes for patient {patient_id}",
        filter={
            "patient_id": patient_id,
            "date_range": {"start": f"{2025 - years}-01-01", "end": "2025-01-09"}
        },
        n_results=1000  # Retrieve all notes
    )

    # Combine all notes (could be 500K-1M tokens)
    full_medical_history = "\n\n---\n\n".join(all_notes['documents'])

    # Generate longitudinal summary
    prompt = f"""Analyze this patient's complete {years}-year medical history.

COMPLETE MEDICAL HISTORY ({years} years):
{full_medical_history}

Provide a longitudinal summary including:
1. Chronic conditions and their progression
2. Medication changes over time
3. Major procedures and hospitalizations
4. Lab trends (e.g., A1c, creatinine, lipids)
5. Overall clinical trajectory
6. Important patterns or concerns

LONGITUDINAL SUMMARY:"""

    model = GenerativeModel("gemini-1.5-pro-002")
    response = model.generate_content(prompt)

    return response.text
```

## Multimodal Healthcare Applications

```python
def analyze_medical_image_with_clinical_context(
    image_path: str,
    clinical_context: str
) -> str:
    """
    Analyze medical image with clinical context.

    Gemini supports multimodal input: images + text.

    Args:
        image_path: Path to medical image (X-ray, CT, MRI, etc.)
        clinical_context: Clinical notes/history

    Returns:
        Image analysis with clinical interpretation
    """

    # Load image
    image_part = Part.from_uri(
        uri=image_path,  # GCS URI: gs://bucket/image.jpg
        mime_type="image/jpeg"
    )

    # Create multimodal prompt
    prompt = f"""Analyze this medical image in the context of the patient's clinical history.

CLINICAL CONTEXT:
{clinical_context}

TASK:
1. Describe key findings in the image
2. Relate findings to clinical context
3. Note any concerning features
4. Suggest differential diagnoses

ANALYSIS:"""

    model = GenerativeModel("gemini-1.5-pro-002")
    response = model.generate_content([prompt, image_part])

    return response.text


# Example usage
clinical_context = """
Patient: 65yo male
History: Smoker, COPD, recent weight loss
Presenting symptom: Persistent cough, hemoptysis
"""

analysis = analyze_medical_image_with_clinical_context(
    image_path="gs://my-bucket/chest-xray-2025-01-09.jpg",
    clinical_context=clinical_context
)
print(analysis)
```

## Cost Optimization

### Caching (Context Caching)

Vertex AI supports context caching to reduce costs for repeated queries:

```python
from vertexai.generative_models import GenerativeModel, caching

# Create cached content (e.g., large clinical guideline)
cached_guideline = caching.CachedContent.create(
    model_name="gemini-1.5-pro-002",
    system_instruction="You are a clinical decision support AI.",
    contents=[
        "CLINICAL GUIDELINE (500 pages): ... [large guideline text] ..."
    ],
    ttl="3600s",  # Cache for 1 hour
)

# Use cached content for multiple queries
model = GenerativeModel.from_cached_content(cached_guideline)

# Subsequent queries use cache (90% cost reduction on cached tokens)
response1 = model.generate_content("What are beta-blocker contraindications?")
response2 = model.generate_content("What are ACE inhibitor contraindications?")

# Both queries reuse cached guideline content
```

### Model Selection for Cost

```python
def adaptive_model_selection(query: str, complexity_threshold: float = 0.7) -> str:
    """
    Route to Gemini Flash (cheap) or Pro (expensive) based on query complexity.

    Args:
        query: User query
        complexity_threshold: Threshold for using Pro vs. Flash

    Returns:
        Generated answer
    """

    # Assess query complexity (simple heuristic)
    complexity_score = assess_complexity(query)

    if complexity_score > complexity_threshold:
        # Complex query → Gemini Pro
        model = GenerativeModel("gemini-1.5-pro-002")
        print("Using Gemini Pro (complex query)")
    else:
        # Simple query → Gemini Flash (10x cheaper)
        model = GenerativeModel("gemini-1.5-flash-002")
        print("Using Gemini Flash (simple query)")

    # Retrieve and generate
    results = vector_store.query(query, n_results=5)
    context = "\n\n".join(results['documents'])

    prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    response = model.generate_content(prompt)

    return response.text


def assess_complexity(query: str) -> float:
    """Simple complexity scoring."""
    factors = {
        'long_query': len(query.split()) > 20,
        'medical_terms': count_medical_terms(query) > 3,
        'multi_part': '?' in query[:-1],  # Multiple questions
    }
    return sum(factors.values()) / len(factors)


def count_medical_terms(text: str) -> int:
    """Count medical terminology."""
    medical_terms = ['diagnosis', 'treatment', 'contraindication', 'adverse', 'comorbidity']
    return sum(1 for term in medical_terms if term in text.lower())
```

## Security Best Practices

### VPC Service Controls for PHI

```python
from google.cloud import resourcemanager_v3

def setup_vpc_service_controls():
    """
    Configure VPC Service Controls for PHI protection.

    Creates security perimeter around Vertex AI and Healthcare API.
    """

    # Define service perimeter
    perimeter_config = {
        "title": "Healthcare PHI Perimeter",
        "resources": [
            f"projects/{PROJECT_ID}",
        ],
        "restricted_services": [
            "aiplatform.googleapis.com",  # Vertex AI
            "healthcare.googleapis.com",   # Healthcare API
            "storage.googleapis.com",      # Cloud Storage (for data)
        ],
        "vpc_accessible_services": {
            "enable_restriction": True,
            "allowed_services": [
                "aiplatform.googleapis.com",
                "healthcare.googleapis.com",
            ]
        }
    }

    # In production: use Access Context Manager API to create perimeter
    print("VPC Service Controls configured for PHI protection")
```

### IAM Best Practices

```python
# Example IAM configuration for healthcare AI system

# Service account for Vertex AI (least privilege)
vertex_ai_service_account = {
    "email": "vertex-ai-sa@my-project.iam.gserviceaccount.com",
    "roles": [
        "roles/aiplatform.user",           # Use Vertex AI models
        "roles/storage.objectViewer",      # Read training data (if needed)
        "roles/healthcare.fhirResourceReader",  # Read FHIR data
    ]
}

# Service account for data scientists (no direct PHI access)
data_scientist_account = {
    "email": "data-scientist@my-project.iam.gserviceaccount.com",
    "roles": [
        "roles/aiplatform.user",           # Use models
        # NO healthcare.fhirResourceReader - no direct PHI access
    ]
}

# Separate service account for Healthcare API access
fhir_access_account = {
    "email": "fhir-access-sa@my-project.iam.gserviceaccount.com",
    "roles": [
        "roles/healthcare.fhirResourceReader",
        "roles/healthcare.datasetViewer",
    ],
    "conditions": {
        "ip_restriction": "Allow only from internal IPs"
    }
}
```

## Performance Optimization

### Batch Processing

```python
import asyncio
from typing import List

async def batch_summarize_patient_records(patient_ids: List[str]) -> List[str]:
    """
    Batch process multiple patient summaries.

    Args:
        patient_ids: List of patient IDs

    Returns:
        List of summaries
    """

    async def summarize_one(patient_id: str) -> str:
        # Retrieve data
        results = vector_store.query(
            query=f"Patient {patient_id} medical record",
            filter={"patient_id": patient_id},
            n_results=10
        )
        context = "\n\n".join(results['documents'])

        # Generate summary
        prompt = f"Summarize patient {patient_id}:\n\n{context}"
        model = GenerativeModel("gemini-1.5-flash-002")  # Fast model for batch
        response = model.generate_content(prompt)

        return response.text

    # Process in parallel
    summaries = await asyncio.gather(*[summarize_one(pid) for pid in patient_ids])

    return summaries


# Example usage
patient_ids = ["12345", "67890", "11111"]
summaries = asyncio.run(batch_summarize_patient_records(patient_ids))
```

## Related Patterns
- [Basic RAG](../patterns/basic-rag.md)
- [Long Context Window Strategies](../patterns/long-context-strategies.md)
- [Multimodal RAG](../patterns/multi-modal-rag.md)

## References
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Gemini Models Overview](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models)
- [Cloud Healthcare API](https://cloud.google.com/healthcare-api/docs)
- [Vertex AI HIPAA Compliance](https://cloud.google.com/security/compliance/hipaa)

## Version History
- **v1.0** (2025-01-09): Initial Vertex AI vendor guide with Gemini models, Healthcare API integration, long context strategies, multimodal capabilities, and security best practices

