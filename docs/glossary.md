# Glossary

Comprehensive terminology for the AI Summarization Reference Architecture project.

## A

**ADK (Agent Development Kit)**: Google's Agent Development Kit for building agent-based AI applications. Used as the primary querying interface in this project.

**ADT (Admission, Discharge, Transfer)**: Healthcare events that track patient movement through healthcare facilities. Used in real-time healthcare data streaming.

**Advanced RAG**: Multi-step retrieval pattern that decomposes complex queries and performs multiple retrieval passes.

**Agentic RAG**: RAG pattern that uses AI agents to orchestrate retrieval and generation tasks.

**Anthropic**: AI company providing Claude models and services. Fully supported in all patterns.

**arXiv**: Open-access repository of electronic preprints of scientific papers (arxiv.org). Primary source for monitoring latest AI/RAG research in this project's self-updating system. Covers computer science (cs.AI, cs.CL, cs.LG, cs.IR), quantitative biology, and other scientific domains.

## B

**Basic RAG**: Foundational RAG pattern with single-step retrieval and generation.

**BigQuery**: Google Cloud's data warehouse service. Used for healthcare data processing and storage.

**BAA (Business Associate Agreement)**: HIPAA-required agreement between healthcare entities and vendors handling PHI.

## C

**Cache (Prompt Caching)**: Anthropic feature that caches frequently used prompt content, reducing costs by 90% for cached tokens.

**ChromaDB**: Embedded vector database used for storing document embeddings in this project.

**Claude**: Anthropic's family of AI models. All tiers supported (Opus, Sonnet, Haiku).

**Clinical Note**: Unstructured text documentation of patient encounters, procedures, and observations by healthcare providers.

**Clustering**: Algorithm for grouping similar items together. Used in RAPTOR RAG for hierarchical summarization.

**CMS (Centers for Medicare & Medicaid Services)**: US federal agency that administers healthcare programs and sets standards.

**Compressed RAG**: RAG pattern that compresses retrieved context to fit within token limits.

**Context Window**: Maximum number of tokens an LLM can process in a single request. Claude 3.5 supports up to 200K tokens.

**Contextual Retrieval**: Anthropic's pattern (Sept 2024) that adds document context to chunks before embedding, reducing retrieval errors by 49-67%.

**Corrective RAG**: Self-correcting RAG pattern that validates and corrects retrieval results.

**CPT (Current Procedural Terminology)**: Medical coding system for procedures and services.

**Cross-Encoder**: Re-ranking model that scores query-document pairs for relevance. More accurate than bi-encoders but slower.

## D

**Docling**: Document processing framework for converting various formats (PDF, DOCX, PPTX) into structured data.

**Drift Detection**: Monitoring pattern to detect data or concept drift in production models.

## E

**EHR (Electronic Health Record)**: Digital version of patient medical records. Patterns support various EHR systems.

**Embedding**: Vector representation of text used for semantic search in vector stores.

**Ensemble Pattern**: AI design pattern combining multiple models for improved accuracy.

## F

**FHIR (Fast Healthcare Interoperability Resources)**: HL7 standard for healthcare data exchange. Supported in all healthcare patterns.

**Feature Store**: Centralized repository for storing and serving ML features.

## G

**Gemini**: Google's family of AI models. Available through Vertex AI.

**Graph RAG**: RAG pattern using knowledge graphs for retrieval.

**GraphQL**: Query language for APIs. Supported as data access pattern for BigQuery/Spanner.

## H

**Hallucination**: When an LLM generates false or unsupported information. Critical concern in healthcare AI requiring validation techniques.

**HDBSCAN**: Hierarchical Density-Based Spatial Clustering algorithm. Used in RAPTOR for clustering document chunks.

**HIPAA (Health Insurance Portability and Accountability Act)**: US healthcare privacy and security law. All healthcare patterns must comply.

**HL7 (Health Level 7)**: Healthcare data exchange standards, including v2.x messaging and FHIR.

**Hybrid RAG**: RAG pattern combining multiple retrieval strategies (vector, keyword, semantic).

**HyDE (Hypothetical Document Embeddings)**: RAG pattern that generates hypothetical answers before retrieval, improving accuracy by 15-30%.

## I

**ICD-10 (International Classification of Diseases, 10th Revision)**: Medical coding system for diagnoses and conditions.

**ICU (Intensive Care Unit)**: Critical care hospital unit requiring real-time patient monitoring.

## K

**K-Means**: Clustering algorithm that partitions data into k clusters. Used in RAPTOR for hierarchical summarization.

**Knowledge Graph**: Structured representation of entities and relationships. Used in Graph RAG patterns.

## L

**LangChain**: Framework for building LLM applications. Supported across all patterns.

**LLM (Large Language Model)**: AI models capable of understanding and generating text.

**LOINC (Logical Observation Identifiers Names and Codes)**: Standard for laboratory and clinical observations.

**Long Context Window**: LLM capability to process large amounts of text (e.g., 200K tokens for Claude 3.5).

## M

**MedCAT (Medical Concept Annotation Tool)**: NLP library for extracting medical concepts from clinical text.

**Medical NLP**: Natural Language Processing specialized for medical and clinical text.

**MRN (Medical Record Number)**: Unique patient identifier used within a healthcare organization.

**Modular RAG**: RAG pattern with composable, reusable retrieval components.

**Multi-Modal AI**: AI systems that process multiple data types (text, images, audio). Claude 3.5 supports vision.

**Multi-Query RAG**: RAG pattern generating multiple query variations for better retrieval.

## O

**Ollama**: Local LLM platform. Used in project infrastructure and shown as cost-effective alternative.

**Operational Excellence**: Well-Architected Framework pillar focusing on operations and monitoring.

## P

**Parent-Child RAG**: Hierarchical RAG pattern for large documents with parent and child chunks.

**PHI (Protected Health Information)**: Healthcare data protected under HIPAA.

**Prompt Engineering**: Technique of crafting effective prompts to guide LLM behavior and output.

**Prompt Injection**: Security attack where malicious instructions are embedded in user input to manipulate LLM behavior.

**Pub/Sub**: Google Cloud Pub/Sub for real-time event streaming. Used in healthcare data patterns.

## Q

**Query Routing**: Pattern that dynamically selects optimal retrieval strategy based on query characteristics. Also called Adaptive RAG.

## R

**RAG (Retrieval-Augmented Generation)**: Pattern combining information retrieval with language model generation.

**RAPTOR (Recursive Abstractive Processing for Tree-Organized Retrieval)**: Hierarchical RAG pattern that builds tree of summaries, reducing errors by 25-40% for complex queries.

**Recursive RAG**: RAG pattern with recursive query decomposition.

**Reranking RAG**: Multi-stage RAG pattern with reranking of retrieved documents.

**RBAC (Role-Based Access Control)**: Security model that restricts access based on user roles.

## S

**scispaCy**: Medical/scientific NLP library built on spaCy, specialized for biomedical text processing.

**Self-RAG**: Self-reflective RAG pattern with built-in quality assessment.

**Semantic Search**: Search based on meaning rather than keywords. Uses embeddings to find conceptually similar content.

**Sliding Window**: Technique for processing text that exceeds context window by moving through document in overlapping segments.

**Small-to-Big RAG**: Progressive RAG pattern expanding context from small to large chunks.

**SMART on FHIR**: Framework for integrating third-party applications with EHR systems using FHIR and OAuth 2.0.

**SNOMED CT (Systematized Nomenclature of Medicine - Clinical Terms)**: Comprehensive clinical terminology system.

**SOAP Note (Subjective, Objective, Assessment, Plan)**: Standard clinical documentation format.

**Spanner**: Google Cloud's globally distributed database. Used for analytical/reporting in healthcare patterns.

**Spring AI**: Java/Spring framework for AI applications. Supported in patterns.

**Streaming RAG**: Real-time RAG pattern for live data summarization.

**Structured Output**: LLM capability to generate responses in specific formats (JSON, XML). Supported by Claude 3.5 via tool use.

## T

**Temperature**: LLM parameter controlling randomness (0 = deterministic, 1 = creative). Healthcare typically uses 0.0-0.2 for accuracy.

**Token**: Unit of text processed by LLMs (roughly 4 characters or 0.75 words).

**Transfer Learning**: AI pattern adapting pre-trained models to new tasks.

## V

**Vector Database**: Specialized database optimized for storing and querying high-dimensional vectors (embeddings).

**Vector Store**: Database storing document embeddings for semantic search (e.g., ChromaDB).

**Vertex AI**: Google Cloud's AI platform. Fully supported for production healthcare.

**Vision AI**: AI capability to process and understand images. Claude 3.5 supports medical image analysis.

## W

**Well-Architected Framework**: Google Cloud's framework with six pillars: Operational Excellence, Security, Reliability, Cost Optimization, Performance, Sustainability.

## Z

**Zero Trust**: Security model assuming no implicit trust, requiring verification for every access request.

## Acronyms Quick Reference

### Healthcare
- **ADT**: Admission, Discharge, Transfer
- **BAA**: Business Associate Agreement
- **CMS**: Centers for Medicare & Medicaid Services
- **CPT**: Current Procedural Terminology
- **EHR**: Electronic Health Record
- **FHIR**: Fast Healthcare Interoperability Resources
- **HIPAA**: Health Insurance Portability and Accountability Act
- **HL7**: Health Level 7
- **ICD-10**: International Classification of Diseases, 10th Revision
- **ICU**: Intensive Care Unit
- **LOINC**: Logical Observation Identifiers Names and Codes
- **MRN**: Medical Record Number
- **PHI**: Protected Health Information
- **SNOMED CT**: Systematized Nomenclature of Medicine - Clinical Terms
- **SOAP**: Subjective, Objective, Assessment, Plan

### AI & Technical
- **ADK**: Agent Development Kit
- **BAA**: Business Associate Agreement
- **HyDE**: Hypothetical Document Embeddings
- **LLM**: Large Language Model
- **NLP**: Natural Language Processing
- **RAG**: Retrieval-Augmented Generation
- **RAPTOR**: Recursive Abstractive Processing for Tree-Organized Retrieval
- **RBAC**: Role-Based Access Control

## Version History

- **v1.0** (2025-11-08): Initial glossary
- **v1.1** (2025-01-09): Expanded with comprehensive healthcare and AI terminology, added 50+ new terms and acronyms section

