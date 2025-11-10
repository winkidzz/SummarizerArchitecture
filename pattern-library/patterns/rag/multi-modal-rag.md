# Multi-Modal RAG Pattern

## Overview

Multi-modal RAG extends traditional text-based RAG to incorporate images, medical scans, diagrams, charts, and other visual content alongside textual information. For healthcare AI, this enables comprehensive analysis of patient records that include radiology images, pathology slides, ECGs, charts, and clinical photographs.

**Supported Modalities**:
- **Text**: Clinical notes, lab reports, guidelines
- **Images**: X-rays, CT scans, MRIs, pathology slides
- **Charts**: ECGs, vital sign trends, lab result graphs
- **Diagrams**: Anatomical diagrams, surgical plans
- **Documents**: PDFs with embedded images and tables

**Key Models with Vision**:
- **Claude 3.5 Sonnet**: Best-in-class vision, 200K context
- **GPT-4 Vision (GPT-4V)**: Strong vision capabilities
- **Gemini 1.5 Pro**: 2M context, multimodal from the ground up
- **Claude 3 Opus**: High-quality image understanding

## When to Use Multi-Modal RAG

### Use Multi-Modal RAG When:
- **Medical imaging analysis** - Radiology reports with images
- **Pathology review** - Histology slides with clinical context
- **Surgical planning** - Anatomical images with procedure notes
- **Patient education** - Explaining conditions using diagrams
- **Chart review** - Analyzing ECGs, vital trends, lab graphs
- **Comprehensive records** - Documents mixing text and images

### Use Text-Only RAG When:
- **Pure textual data** - No images involved
- **Cost-sensitive** - Vision models cost more
- **Latency-critical** - Image processing adds overhead

## Healthcare Use Cases

### Medical Imaging Analysis with Clinical Context

```python
import anthropic
import base64
from pathlib import Path


class MedicalImagingRAG:
    """Multi-modal RAG for medical imaging with clinical context."""

    def __init__(self):
        self.client = anthropic.Anthropic()

    def encode_image(self, image_path: str) -> tuple[str, str]:
        """
        Encode image to base64.

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (base64_data, media_type)
        """
        path = Path(image_path)

        # Determine media type
        media_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }

        media_type = media_types.get(path.suffix.lower(), 'image/jpeg')

        # Read and encode
        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')

        return image_data, media_type

    def analyze_chest_xray(
        self,
        xray_path: str,
        clinical_context: str,
        patient_history: str
    ) -> dict:
        """
        Analyze chest X-ray with clinical context.

        Args:
            xray_path: Path to chest X-ray image
            clinical_context: Clinical presentation (symptoms, vitals)
            patient_history: Patient medical history

        Returns:
            Analysis including findings, impressions, recommendations
        """

        # Encode image
        image_data, media_type = self.encode_image(xray_path)

        # Create multi-modal prompt
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            temperature=0.0,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""Analyze this chest X-ray in the context of the patient's clinical presentation.

CLINICAL CONTEXT:
{clinical_context}

PATIENT HISTORY:
{patient_history}

Please provide:
1. **Image Quality Assessment**: Adequacy for diagnosis
2. **Key Findings**: Describe abnormalities or normal findings
3. **Differential Diagnosis**: Based on imaging + clinical context
4. **Comparison to History**: Relevant to patient's conditions
5. **Recommendations**: Additional imaging, urgent actions, follow-up

Be specific about anatomical locations and use standard radiology terminology.

ANALYSIS:"""
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    }
                ]
            }]
        )

        analysis_text = message.content[0].text

        return {
            'analysis': analysis_text,
            'usage': {
                'input_tokens': message.usage.input_tokens,
                'output_tokens': message.usage.output_tokens
            }
        }


# Example usage
imaging_rag = MedicalImagingRAG()

clinical_context = """
Patient: 65yo male
Presenting complaint: Shortness of breath, productive cough x 5 days
Vital signs: Temp 38.5C, HR 95, BP 140/85, RR 22, O2 sat 92% on room air
Physical exam: Decreased breath sounds right lower lobe, dullness to percussion
"""

patient_history = """
Past medical history:
- COPD (on inhalers)
- Type 2 diabetes
- Hypertension
- Former smoker (40 pack-years, quit 5 years ago)

Current medications:
- Albuterol inhaler
- Tiotropium
- Metformin
- Lisinopril
"""

result = imaging_rag.analyze_chest_xray(
    xray_path="patient_chest_xray.jpg",
    clinical_context=clinical_context,
    patient_history=patient_history
)

print(result['analysis'])
```

### Pathology Slide Analysis

```python
class PathologyRAG:
    """Multi-modal RAG for pathology slide analysis."""

    def __init__(self):
        self.client = anthropic.Anthropic()

    def analyze_histology_slide(
        self,
        slide_path: str,
        tissue_type: str,
        clinical_indication: str,
        stain_type: str = "H&E"
    ) -> dict:
        """
        Analyze histology slide with clinical context.

        Args:
            slide_path: Path to slide image
            tissue_type: Type of tissue (e.g., "breast biopsy")
            clinical_indication: Reason for biopsy
            stain_type: Stain used (e.g., "H&E", "IHC")

        Returns:
            Pathology analysis
        """

        # Encode image
        with open(slide_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            temperature=0.0,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""Analyze this {stain_type}-stained histology slide.

SPECIMEN: {tissue_type}
CLINICAL INDICATION: {clinical_indication}
STAIN: {stain_type}

Provide a pathology report including:

1. **Specimen Adequacy**: Is the sample adequate for diagnosis?

2. **Histologic Findings**:
   - Cellular architecture
   - Nuclear features (size, shape, chromatin pattern)
   - Mitotic activity
   - Necrosis, inflammation, or other features

3. **Diagnostic Impression**:
   - Primary diagnosis
   - Grade/stage if applicable

4. **Differential Diagnosis**: Other considerations

5. **Recommendations**: Additional stains, molecular testing, clinical correlation

Note: This is for educational/reference purposes. Actual diagnostic decisions require board-certified pathologist review.

PATHOLOGY ANALYSIS:"""
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_data
                        }
                    }
                ]
            }]
        )

        return {
            'pathology_report': message.content[0].text,
            'usage': message.usage
        }


# Example usage
pathology_rag = PathologyRAG()

result = pathology_rag.analyze_histology_slide(
    slide_path="breast_biopsy_he.jpg",
    tissue_type="Breast core needle biopsy",
    clinical_indication="Palpable mass, suspicious mammogram",
    stain_type="H&E"
)

print(result['pathology_report'])
```

### ECG Analysis with Clinical Context

```python
class ECGAnalysisRAG:
    """Multi-modal RAG for ECG interpretation."""

    def __init__(self):
        self.client = anthropic.Anthropic()

    def interpret_ecg(
        self,
        ecg_image_path: str,
        patient_info: dict,
        clinical_context: str
    ) -> dict:
        """
        Interpret ECG with clinical context.

        Args:
            ecg_image_path: Path to ECG image (12-lead)
            patient_info: Patient demographics and vitals
            clinical_context: Presenting symptoms and history

        Returns:
            ECG interpretation
        """

        # Encode ECG image
        with open(ecg_image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')

        patient_summary = f"""
Age: {patient_info.get('age')}
Sex: {patient_info.get('sex')}
HR: {patient_info.get('heart_rate')} bpm
BP: {patient_info.get('blood_pressure')}
"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            temperature=0.0,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""Interpret this 12-lead ECG in clinical context.

PATIENT INFORMATION:
{patient_summary}

CLINICAL CONTEXT:
{clinical_context}

Provide a systematic ECG interpretation:

1. **Rate**: Ventricular rate (bpm)

2. **Rhythm**:
   - Sinus rhythm, atrial fibrillation, etc.
   - Regular or irregular

3. **Axis**: QRS axis (normal, left deviation, right deviation)

4. **Intervals**:
   - PR interval (ms)
   - QRS duration (ms)
   - QT/QTc interval (ms)

5. **Morphology**:
   - P waves
   - QRS complexes
   - ST segments
   - T waves

6. **Abnormalities**:
   - ST elevation/depression
   - Q waves
   - T wave inversions
   - Bundle branch blocks
   - Hypertrophy patterns
   - Arrhythmias

7. **Clinical Interpretation**:
   - Diagnosis
   - Comparison to patient's clinical presentation
   - Urgency level (emergent, urgent, routine)

8. **Recommendations**:
   - Immediate actions if needed
   - Follow-up ECGs
   - Additional testing (troponin, echo, etc.)

ECG INTERPRETATION:"""
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_data
                        }
                    }
                ]
            }]
        )

        return {
            'interpretation': message.content[0].text,
            'usage': message.usage
        }


# Example usage
ecg_rag = ECGAnalysisRAG()

patient_info = {
    'age': 58,
    'sex': 'Male',
    'heart_rate': 92,
    'blood_pressure': '155/95'
}

clinical_context = """
Presenting complaint: Chest pain for 2 hours, substernal, 8/10 intensity, radiating to left arm
Associated symptoms: Diaphoresis, nausea
Risk factors: Hypertension, hyperlipidemia, family history of CAD, active smoker
"""

result = ecg_rag.interpret_ecg(
    ecg_image_path="patient_ecg_12lead.jpg",
    patient_info=patient_info,
    clinical_context=clinical_context
)

print(result['interpretation'])
```

## Multi-Modal Vector Store

### Embedding Images with CLIP

```python
from sentence_transformers import SentenceTransformer
import chromadb
from PIL import Image
import numpy as np


class MultiModalVectorStore:
    """Vector store supporting both text and images."""

    def __init__(self, collection_name: str = "multimodal_medical"):
        """
        Initialize multi-modal vector store.

        Uses CLIP for unified text-image embeddings.

        Args:
            collection_name: ChromaDB collection name
        """

        # Initialize CLIP model (text + image embeddings)
        self.clip_model = SentenceTransformer('clip-ViT-B-32')

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Multi-modal medical data"}
        )

    def add_text_document(self, text: str, metadata: dict) -> str:
        """
        Add text document to vector store.

        Args:
            text: Document text
            metadata: Document metadata

        Returns:
            Document ID
        """

        # Generate embedding
        embedding = self.clip_model.encode(text).tolist()

        # Generate ID
        doc_id = f"text_{hash(text)}"

        # Add to collection
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{**metadata, 'modality': 'text'}]
        )

        return doc_id

    def add_image_document(
        self,
        image_path: str,
        caption: str,
        metadata: dict
    ) -> str:
        """
        Add image document to vector store.

        Args:
            image_path: Path to image
            caption: Image caption/description
            metadata: Image metadata

        Returns:
            Document ID
        """

        # Load image
        image = Image.open(image_path)

        # Generate image embedding with CLIP
        image_embedding = self.clip_model.encode(image).tolist()

        # Generate ID
        doc_id = f"image_{hash(image_path)}"

        # Add to collection
        self.collection.add(
            ids=[doc_id],
            embeddings=[image_embedding],
            documents=[caption],  # Store caption as document text
            metadatas=[{
                **metadata,
                'modality': 'image',
                'image_path': image_path
            }]
        )

        return doc_id

    def search(self, query: str, n_results: int = 5, modality: str = None):
        """
        Search for text or images using text query.

        CLIP embeddings allow text queries to match images!

        Args:
            query: Text query
            n_results: Number of results
            modality: Filter by 'text', 'image', or None for both

        Returns:
            Search results
        """

        # Generate query embedding
        query_embedding = self.clip_model.encode(query).tolist()

        # Build where filter
        where_filter = {}
        if modality:
            where_filter = {"modality": modality}

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter if where_filter else None
        )

        return results


# Example usage
vector_store = MultiModalVectorStore()

# Add text documents
vector_store.add_text_document(
    text="Patient with right lower lobe pneumonia, consolidation visible on chest X-ray",
    metadata={'patient_id': '12345', 'doc_type': 'radiology_report'}
)

# Add images
vector_store.add_image_document(
    image_path="chest_xray_pneumonia.jpg",
    caption="Chest X-ray showing right lower lobe consolidation consistent with pneumonia",
    metadata={'patient_id': '12345', 'study_type': 'chest_xray'}
)

# Search with text query - finds both text and images!
results = vector_store.search("pneumonia chest X-ray", n_results=5)

print("Found both text reports and images:")
for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
    print(f"- {metadata['modality']}: {doc[:100]}...")
```

## Complete Multi-Modal RAG System

```python
class ComprehensiveMultiModalRAG:
    """Complete multi-modal RAG for healthcare."""

    def __init__(self):
        self.anthropic_client = anthropic.Anthropic()
        self.vector_store = MultiModalVectorStore()

    def query_with_multimodal_context(
        self,
        query: str,
        include_images: bool = True
    ) -> dict:
        """
        Query with both text and image context.

        Args:
            query: User query
            include_images: Whether to include images in context

        Returns:
            Response with text and images
        """

        # Search vector store for relevant text and images
        text_results = self.vector_store.search(query, n_results=3, modality='text')
        image_results = self.vector_store.search(query, n_results=2, modality='image') if include_images else None

        # Build multi-modal context
        content = [{
            "type": "text",
            "text": f"""Answer the question using the provided context.

TEXTUAL CONTEXT:
{chr(10).join(text_results['documents'][0])}

QUESTION: {query}

ANSWER:"""
        }]

        # Add images to context
        if include_images and image_results and image_results['metadatas'][0]:
            for metadata in image_results['metadatas'][0]:
                image_path = metadata.get('image_path')
                if image_path:
                    # Load and encode image
                    with open(image_path, 'rb') as f:
                        image_data = base64.standard_b64encode(f.read()).decode('utf-8')

                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_data
                        }
                    })

        # Generate response
        message = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            temperature=0.0,
            messages=[{
                "role": "user",
                "content": content
            }]
        )

        return {
            'answer': message.content[0].text,
            'text_sources': len(text_results['documents'][0]),
            'image_sources': len(image_results['metadatas'][0]) if image_results else 0,
            'usage': message.usage
        }


# Example usage
rag = ComprehensiveMultiModalRAG()

# Ingest medical data (text + images)
rag.vector_store.add_text_document(
    "Patient diagnosed with community-acquired pneumonia, treated with antibiotics",
    metadata={'patient_id': '12345', 'type': 'clinical_note'}
)

rag.vector_store.add_image_document(
    "chest_xray.jpg",
    "Chest X-ray showing right lower lobe infiltrate",
    metadata={'patient_id': '12345', 'type': 'imaging'}
)

# Query with multi-modal context
result = rag.query_with_multimodal_context(
    query="What does the imaging show for this pneumonia case?",
    include_images=True
)

print(result['answer'])
print(f"Sources: {result['text_sources']} text, {result['image_sources']} images")
```

## Cost and Performance Considerations

### Vision Model Pricing

**Claude 3.5 Sonnet** (per image):
- Images up to 200 tokens: $3.00 per 1M input tokens
- Larger images cost more based on token count

**Cost Calculation**:
```python
def estimate_vision_cost(num_images: int, avg_tokens_per_image: int = 150):
    """
    Estimate cost for vision analysis.

    Args:
        num_images: Number of images
        avg_tokens_per_image: Average tokens per image

    Returns:
        Estimated cost in USD
    """

    # Claude 3.5 Sonnet pricing
    cost_per_1m_tokens = 3.00

    total_tokens = num_images * avg_tokens_per_image
    cost = (total_tokens / 1_000_000) * cost_per_1m_tokens

    print(f"Images: {num_images}")
    print(f"Total tokens: ~{total_tokens}")
    print(f"Estimated cost: ${cost:.4f}")

    return cost


# Example
estimate_vision_cost(num_images=10, avg_tokens_per_image=150)
# Output: $0.0045 for 10 images
```

## Limitations and Best Practices

### Image Quality Requirements

1. **Resolution**: High enough to see relevant details
2. **Format**: JPEG, PNG, GIF, WebP (under 5MB per image)
3. **Contrast**: Sufficient for model to distinguish features
4. **Orientation**: Correct orientation (not upside-down)

### Best Practices

- **Caption images**: Provide descriptive captions for better retrieval
- **Combine modalities**: Use text + images together for best results
- **Pre-process images**: Crop to relevant region, adjust contrast
- **Batch processing**: Process multiple images in single request when possible
- **Cache prompts**: Use prompt caching for repeated analyses

### Healthcare-Specific Considerations

- **Never replace clinical judgment**: Models assist, don't diagnose
- **HIPAA compliance**: Ensure BAA with model provider
- **Image anonymization**: Remove PHI from images before upload
- **Quality assurance**: Human expert review required for clinical decisions

## Related Patterns

- [Basic RAG](./basic-rag.md)
- [Long Context Window Strategies](./long-context-strategies.md)
- [Anthropic Claude Guide](../vendor-guides/anthropic-claude.md)

## References

- [Claude Vision](https://docs.anthropic.com/en/docs/vision)
- [GPT-4 Vision](https://platform.openai.com/docs/guides/vision)
- [CLIP: Connecting Text and Images](https://openai.com/research/clip)

## Version History

- **v1.0** (2025-01-09): Initial multi-modal RAG pattern with medical imaging, pathology, ECG analysis, CLIP embeddings, and best practices
