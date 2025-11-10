# LangChain Framework Guide

## Overview

LangChain is a comprehensive framework for building applications with Large Language Models (LLMs). For healthcare AI summarization, LangChain provides vendor-agnostic abstractions, pre-built RAG components, and healthcare-specific integrations that simplify building production-quality systems.

**Key Features**:
- Vendor-agnostic LLM integrations (Anthropic, OpenAI, Google, AWS, etc.)
- Pre-built RAG components (retrievers, vector stores, document loaders)
- Chain abstractions for complex workflows
- Agent framework for autonomous reasoning
- Memory management for conversational AI
- Streaming support for real-time responses
- Production monitoring and tracing (LangSmith)

## Supported Models

LangChain supports **all major LLM providers** through unified interfaces:

### Anthropic (via LangChain-Anthropic)
```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0.0,
    max_tokens=2048
)
```

### OpenAI / Azure OpenAI
```python
from langchain_openai import ChatOpenAI, AzureChatOpenAI

# OpenAI
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.0)

# Azure OpenAI
llm = AzureChatOpenAI(
    azure_deployment="your-deployment",
    api_version="2024-10-21",
    temperature=0.0
)
```

### Google Vertex AI
```python
from langchain_google_vertexai import ChatVertexAI

llm = ChatVertexAI(
    model="gemini-1.5-pro-002",
    temperature=0.0
)
```

### AWS Bedrock
```python
from langchain_aws import ChatBedrock

llm = ChatBedrock(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name="us-east-1"
)
```

## Basic RAG Implementation

```python
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


def setup_langchain_rag():
    """
    Set up basic RAG with LangChain.

    Returns:
        RAG chain ready for queries
    """

    # Initialize embeddings
    embeddings = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    # Initialize vector store
    vectorstore = Chroma(
        collection_name="medical_docs",
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )

    # Create retriever
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    # Initialize LLM
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.0
    )

    # Define prompt template
    prompt = ChatPromptTemplate.from_template("""
Answer the question using the provided context.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:""")

    # Create RAG chain using LCEL (LangChain Expression Language)
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


# Example usage
rag_chain = setup_langchain_rag()
answer = rag_chain.invoke("What are the latest guidelines for heart failure management?")
print(answer)
```

## Healthcare-Specific Features

### Medical Document Loaders

```python
from langchain_community.document_loaders import (
    PDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter


class MedicalDocumentLoader:
    """Load and process medical documents."""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def load_clinical_guidelines(self, file_path: str):
        """
        Load clinical guidelines from various formats.

        Args:
            file_path: Path to clinical guideline file

        Returns:
            List of document chunks
        """

        # Determine file type and use appropriate loader
        if file_path.endswith('.pdf'):
            loader = PDFLoader(file_path)
        elif file_path.endswith('.docx'):
            loader = UnstructuredWordDocumentLoader(file_path)
        elif file_path.endswith('.pptx'):
            loader = UnstructuredPowerPointLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path}")

        # Load documents
        documents = loader.load()

        # Split into chunks
        chunks = self.text_splitter.split_documents(documents)

        # Add metadata
        for chunk in chunks:
            chunk.metadata['source_type'] = 'clinical_guideline'
            chunk.metadata['file_path'] = file_path

        return chunks


# Example usage
doc_loader = MedicalDocumentLoader()
guidelines = doc_loader.load_clinical_guidelines("heart_failure_guidelines.pdf")

# Add to vector store
vectorstore.add_documents(guidelines)
```

### FHIR Integration

```python
from langchain_core.documents import Document
from fhir.resources.patient import Patient
from fhir.resources.condition import Condition
from fhir.resources.medicationstatement import MedicationStatement
import json


class FHIRDocumentLoader:
    """Load FHIR resources as LangChain documents."""

    def load_patient_record(self, patient_id: str, fhir_client) -> list[Document]:
        """
        Load patient FHIR record as documents.

        Args:
            patient_id: Patient ID
            fhir_client: FHIR API client

        Returns:
            List of LangChain documents
        """

        documents = []

        # Load patient demographics
        patient_resource = fhir_client.read('Patient', patient_id)
        patient = Patient(**patient_resource)

        patient_doc = Document(
            page_content=f"Patient: {patient.name[0].given[0]} {patient.name[0].family}\n"
                        f"Gender: {patient.gender}\n"
                        f"Birth Date: {patient.birthDate}",
            metadata={
                'resource_type': 'Patient',
                'patient_id': patient_id,
                'source': 'fhir'
            }
        )
        documents.append(patient_doc)

        # Load conditions
        conditions = fhir_client.search('Condition', {'patient': patient_id})
        for condition_resource in conditions['entry']:
            condition = Condition(**condition_resource['resource'])

            condition_doc = Document(
                page_content=f"Condition: {condition.code.text}\n"
                            f"Clinical Status: {condition.clinicalStatus.coding[0].code}\n"
                            f"Onset: {condition.onsetDateTime or 'Unknown'}",
                metadata={
                    'resource_type': 'Condition',
                    'patient_id': patient_id,
                    'condition_id': condition.id,
                    'source': 'fhir'
                }
            )
            documents.append(condition_doc)

        # Load medications
        medications = fhir_client.search('MedicationStatement', {'patient': patient_id})
        for med_resource in medications.get('entry', []):
            med = MedicationStatement(**med_resource['resource'])

            med_doc = Document(
                page_content=f"Medication: {med.medicationCodeableConcept.text}\n"
                            f"Status: {med.status}\n"
                            f"Dosage: {med.dosage[0].text if med.dosage else 'N/A'}",
                metadata={
                    'resource_type': 'MedicationStatement',
                    'patient_id': patient_id,
                    'medication_id': med.id,
                    'source': 'fhir'
                }
            )
            documents.append(med_doc)

        return documents


# Example usage
fhir_loader = FHIRDocumentLoader()
patient_docs = fhir_loader.load_patient_record('12345', fhir_client)

# Add to vector store for RAG
vectorstore.add_documents(patient_docs)
```

## Advanced RAG Patterns

### Contextual Retrieval (Anthropic Sept 2024)

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.documents import Document


class ContextualRetriever:
    """Implement contextual retrieval with LangChain."""

    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-haiku-20241022",  # Fast model for context generation
            temperature=0.0
        )

    def add_context_to_chunks(
        self,
        document: str,
        chunks: list[Document]
    ) -> list[Document]:
        """
        Add document context to each chunk before embedding.

        Anthropic's contextual retrieval (Sept 2024) reduces errors by 49-67%.

        Args:
            document: Full document text
            chunks: Document chunks

        Returns:
            Chunks with added context
        """

        contextualized_chunks = []

        for chunk in chunks:
            # Generate context for this chunk
            context_prompt = f"""
<document>
{document}
</document>

Here is a chunk from the document:
<chunk>
{chunk.page_content}
</chunk>

Generate a concise context (2-3 sentences) that situates this chunk within the overall document.
"""

            context = self.llm.invoke(context_prompt).content

            # Create new chunk with context prepended
            contextualized_content = f"{context}\n\n{chunk.page_content}"

            contextualized_chunk = Document(
                page_content=contextualized_content,
                metadata={
                    **chunk.metadata,
                    'has_context': True,
                    'original_content': chunk.page_content
                }
            )

            contextualized_chunks.append(contextualized_chunk)

        return contextualized_chunks


# Example usage
retriever = ContextualRetriever()

# Load and chunk document
document_text = "..."  # Full document
chunks = text_splitter.create_documents([document_text])

# Add context to chunks
contextualized_chunks = retriever.add_context_to_chunks(document_text, chunks)

# Add to vector store
vectorstore.add_documents(contextualized_chunks)
```

### Multi-Query RAG

```python
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_anthropic import ChatAnthropic


def setup_multi_query_rag():
    """
    Set up multi-query RAG for improved retrieval.

    Generates multiple query variations to retrieve diverse results.
    """

    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.0)

    # Base retriever
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # Multi-query retriever
    retriever = MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=llm
    )

    # Create RAG chain
    prompt = ChatPromptTemplate.from_template("""
Answer based on the context:

{context}

Question: {question}
Answer:""")

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


# Example usage
multi_query_rag = setup_multi_query_rag()
answer = multi_query_rag.invoke("What are beta-blocker contraindications?")
```

### Reranking with Cross-Encoders

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder


def setup_reranking_rag():
    """
    Set up RAG with cross-encoder reranking.

    Two-stage retrieval:
    1. Fast bi-encoder retrieval (50 candidates)
    2. Accurate cross-encoder reranking (top 5)

    Improves precision by 20-35%.
    """

    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.0)

    # Base retriever (retrieve many candidates)
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 50})

    # Cross-encoder reranker
    cross_encoder = HuggingFaceCrossEncoder(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
    reranker = CrossEncoderReranker(model=cross_encoder, top_n=5)

    # Compression retriever with reranking
    retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=base_retriever
    )

    # RAG chain
    prompt = ChatPromptTemplate.from_template("""
Context: {context}

Question: {question}

Answer:""")

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


# Example usage
reranking_rag = setup_reranking_rag()
answer = reranking_rag.invoke("What are the side effects of ACE inhibitors?")
```

## Structured Outputs

```python
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser


class SOAPNote(BaseModel):
    """SOAP note structure."""
    subjective: str = Field(description="Subjective: Patient's reported symptoms")
    objective: str = Field(description="Objective: Measurable clinical findings")
    assessment: str = Field(description="Assessment: Diagnosis and clinical impression")
    plan: str = Field(description="Plan: Treatment plan and next steps")


def generate_structured_soap_note(clinical_note: str) -> SOAPNote:
    """
    Generate structured SOAP note from clinical note.

    Args:
        clinical_note: Unstructured clinical note

    Returns:
        Structured SOAP note
    """

    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.0)

    # Create parser
    parser = JsonOutputParser(pydantic_object=SOAPNote)

    # Create prompt with format instructions
    prompt = ChatPromptTemplate.from_template("""
Extract a SOAP note from the clinical note.

CLINICAL NOTE:
{clinical_note}

{format_instructions}

SOAP NOTE:""")

    # Create chain
    chain = prompt | llm | parser

    # Generate structured output
    soap_note = chain.invoke({
        "clinical_note": clinical_note,
        "format_instructions": parser.get_format_instructions()
    })

    return SOAPNote(**soap_note)


# Example usage
clinical_note = """
Patient reports chest pain for 2 days. Pain is substernal, 7/10 intensity.
BP 145/90, HR 88, RR 16, O2 sat 98%. Heart sounds normal, lungs clear.
EKG shows ST elevation in leads II, III, aVF.
Likely inferior STEMI. Will start aspirin, heparin, transfer to cath lab.
"""

soap = generate_structured_soap_note(clinical_note)
print(soap.dict())
```

## Agents for Complex Workflows

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import Tool
from langchain_anthropic import ChatAnthropic


def create_clinical_assistant_agent():
    """
    Create agent for clinical assistance with tool use.

    Agent can:
    - Query patient records
    - Search clinical guidelines
    - Calculate medical scores
    """

    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.0)

    # Define tools
    def search_patient_records(query: str) -> str:
        """Search patient records."""
        results = vectorstore.similarity_search(query, k=5, filter={"source": "ehr"})
        return "\n\n".join([doc.page_content for doc in results])

    def search_guidelines(query: str) -> str:
        """Search clinical guidelines."""
        results = vectorstore.similarity_search(query, k=5, filter={"source_type": "clinical_guideline"})
        return "\n\n".join([doc.page_content for doc in results])

    def calculate_chadsvasc(age: int, female: bool, chf: bool, hypertension: bool,
                           stroke_tia: bool, vascular_disease: bool, diabetes: bool) -> str:
        """Calculate CHA2DS2-VASc score for stroke risk."""
        score = 0
        if age >= 75: score += 2
        elif age >= 65: score += 1
        if female: score += 1
        if chf: score += 1
        if hypertension: score += 1
        if stroke_tia: score += 2
        if vascular_disease: score += 1
        if diabetes: score += 1

        return f"CHA2DS2-VASc score: {score}\nRecommendation: {'Anticoagulation recommended' if score >= 2 else 'Consider anticoagulation' if score == 1 else 'No anticoagulation needed'}"

    tools = [
        Tool(
            name="search_patient_records",
            func=search_patient_records,
            description="Search patient medical records for clinical information"
        ),
        Tool(
            name="search_guidelines",
            func=search_guidelines,
            description="Search clinical practice guidelines"
        ),
        Tool(
            name="calculate_chadsvasc",
            func=lambda x: calculate_chadsvasc(**eval(x)),
            description="Calculate CHA2DS2-VASc score. Input as dict: {'age': 70, 'female': True, 'chf': False, ...}"
        )
    ]

    # Create agent
    agent = create_react_agent(llm, tools, prompt_template)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return agent_executor


# Example usage
agent = create_clinical_assistant_agent()

result = agent.invoke({
    "input": "Patient is 72yo female with atrial fibrillation, hypertension, and diabetes. What is her stroke risk and should she be on anticoagulation?"
})

print(result['output'])
```

## Prompt Caching

```python
from langchain_anthropic import ChatAnthropic


def rag_with_prompt_caching(query: str, guidelines_context: str) -> str:
    """
    RAG with prompt caching for cost savings.

    Caching reduces costs by 90% for cached portions.

    Args:
        query: User query
        guidelines_context: Large guidelines (cached)

    Returns:
        Generated answer
    """

    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.0
    )

    # Use cache_control in messages
    # Note: LangChain integration for cache_control may vary by version
    from langchain_core.messages import SystemMessage

    system_message = SystemMessage(
        content=[
            {"type": "text", "text": "You are a clinical decision support assistant."},
            {
                "type": "text",
                "text": f"CLINICAL GUIDELINES:\n{guidelines_context}",
                "cache_control": {"type": "ephemeral"}
            }
        ]
    )

    response = llm.invoke([system_message, ("human", query)])

    return response.content


# Example: Repeated queries against same guidelines (90% cheaper after first)
guidelines = """[Large clinical guidelines...]"""

answer1 = rag_with_prompt_caching("What are beta-blocker contraindications?", guidelines)
answer2 = rag_with_prompt_caching("What are ACE inhibitor contraindications?", guidelines)
```

## Monitoring with LangSmith

```python
import os
from langsmith import Client

# Configure LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"
os.environ["LANGCHAIN_PROJECT"] = "healthcare-rag"

# All LangChain operations are now traced in LangSmith
rag_chain = setup_langchain_rag()
answer = rag_chain.invoke("What are the guidelines for diabetes management?")

# View traces in LangSmith dashboard
# - Token usage
# - Latency
# - Retrieved documents
# - LLM calls
# - Errors
```

## Related Patterns

- [Basic RAG](../patterns/basic-rag.md)
- [Contextual Retrieval](../patterns/contextual-retrieval.md)
- [Reranking RAG](../patterns/reranking-rag.md)
- [Anthropic Claude Guide](./anthropic-claude.md)

## References

- [LangChain Documentation](https://python.langchain.com/)
- [LangChain Anthropic Integration](https://python.langchain.com/docs/integrations/chat/anthropic)
- [LangSmith](https://smith.langchain.com/)

## Version History

- **v1.0** (2025-01-09): Initial LangChain framework guide with RAG patterns, healthcare integrations, structured outputs, and agent workflows
