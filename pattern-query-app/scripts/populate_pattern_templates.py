"""
Populate AI Design Pattern Templates

This script populates the first 3 sections (Overview, When to Use, When Not to Use)
for all 70 AI design pattern template files.
"""

import os
from pathlib import Path

# Pattern content definitions
PATTERN_CONTENT = {
    # Model Architecture patterns
    "transfer-learning-pattern.md": {
        "overview": "Transfer Learning leverages knowledge from pre-trained models to accelerate learning on new, related tasks. Instead of training from scratch, this pattern fine-tunes models trained on large general datasets for specific healthcare domains. Foundation models like Claude, GPT-4, and Gemini use transfer learning principles, where general language understanding is adapted to medical summarization through prompt engineering or fine-tuning.",
        "when_to_use": [
            "**Limited labeled data**: Healthcare datasets are often small due to privacy constraints",
            "**Domain adaptation**: Adapting general language models to medical terminology and clinical workflows",
            "**Fast development**: Leveraging pre-trained models reduces training time from months to hours/days",
            "**Cost optimization**: Fine-tuning is cheaper than training large models from scratch",
            "**Proven architecture**: Using battle-tested model architectures (Transformers, BERT, GPT)"
        ],
        "when_not_to_use": [
            "**Highly specialized domains**: When source and target domains are too different (rare in healthcare AI)",
            "**Privacy concerns**: Pre-trained models may have seen sensitive training data",
            "**Performance critical**: Sometimes domain-specific models outperform transferred models",
            "**Complete control needed**: When you need to understand every aspect of model behavior",
            "**Regulatory requirements**: Some healthcare regulations may require training provenance"
        ]
    },

    "multi-task-learning-pattern.md": {
        "overview": "Multi-Task Learning trains a single model to perform multiple related tasks simultaneously, sharing representations across tasks. In healthcare AI, this could mean a model that extracts diagnoses, medications, and procedures from clinical notes in one pass, improving efficiency and leveraging shared medical knowledge across tasks.",
        "when_to_use": [
            "**Related tasks**: Multiple tasks share common underlying structure (e.g., extracting different medical entities)",
            "**Limited data per task**: Tasks have small datasets individually but benefit from shared learning",
            "**Resource constraints**: Single model is more efficient than multiple specialized models",
            "**Improved generalization**: Shared representations can improve performance on all tasks",
            "**Consistent outputs**: Need synchronized predictions across related tasks"
        ],
        "when_not_to_use": [
            "**Unrelated tasks**: Tasks don't share meaningful structure or knowledge",
            "**Conflicting objectives**: Task requirements work against each other",
            "**Different scales**: Tasks operate on vastly different data scales or distributions",
            "**Specialized performance**: Need maximum accuracy on a single primary task",
            "**Independent deployment**: Tasks need to be deployed or updated separately"
        ]
    },

    "modular-architecture-pattern.md": {
        "overview": "Modular Architecture decomposes the AI system into independent, interchangeable components with well-defined interfaces. Each module handles a specific function (e.g., document loading, chunking, embedding, retrieval, generation), enabling flexible composition, testing, and replacement of individual components without affecting the entire system.",
        "when_to_use": [
            "**Complex systems**: Large AI pipelines with multiple distinct stages",
            "**Team collaboration**: Different teams can work on separate modules independently",
            "**Flexibility needed**: Ability to swap components (e.g., change embedding model without rewriting retrieval logic)",
            "**Testing requirements**: Each module can be tested in isolation",
            "**Vendor flexibility**: Ability to switch between different LLM providers or vector databases"
        ],
        "when_not_to_use": [
            "**Simple applications**: Single-purpose tools don't benefit from modularity overhead",
            "**Tight coupling required**: Components need deep integration for performance",
            "**Rapid prototyping**: Early-stage development where architecture isn't stable",
            "**Performance critical**: Module boundaries can add latency",
            "**Small team**: Overhead of defining and maintaining interfaces isn't justified"
        ]
    },

    "hierarchical-model-pattern.md": {
        "overview": "Hierarchical Model Pattern organizes models in layers where higher-level models aggregate and refine outputs from lower-level models. In medical summarization, this could involve document-level models feeding into patient-level models, which inform population-level insights, creating a hierarchy of abstraction and aggregation.",
        "when_to_use": [
            "**Multi-scale analysis**: Need to operate at different levels of abstraction (note → patient → cohort)",
            "**Progressive refinement**: Each level adds context and refinement to lower levels",
            "**Divide and conquer**: Complex problem naturally decomposes into hierarchical sub-problems",
            "**Scalability**: Process large volumes by hierarchical aggregation",
            "**Explainability**: Trace decisions through hierarchical levels"
        ],
        "when_not_to_use": [
            "**Flat structure**: Problem doesn't have natural hierarchical organization",
            "**Latency sensitive**: Multiple model layers increase inference time",
            "**Simple aggregation**: Basic averaging or voting suffices",
            "**Single-level output**: Only need results at one level of abstraction",
            "**Error propagation**: Mistakes at lower levels compound at higher levels"
        ]
    },

    "attention-mechanism-pattern.md": {
        "overview": "Attention Mechanism enables models to dynamically focus on relevant parts of input when generating outputs. In healthcare summarization, attention helps models identify and weight important clinical findings, diagnoses, or temporal patterns in patient records, improving both accuracy and interpretability by showing which parts of input influenced the summary.",
        "when_to_use": [
            "**Long documents**: Patient records with hundreds of notes where only some are relevant",
            "**Variable importance**: Different input parts have different relevance to the task",
            "**Interpretability**: Need to explain which inputs influenced model decisions",
            "**Context integration**: Combining information from multiple document sections",
            "**Sequence modeling**: Tasks involving temporal or sequential relationships"
        ],
        "when_not_to_use": [
            "**Short inputs**: Attention overhead not justified for small inputs",
            "**Uniform importance**: All input parts equally relevant",
            "**Computational constraints**: Attention adds significant compute (O(n²) for self-attention)",
            "**Fixed-size inputs**: CNNs or simpler architectures may suffice",
            "**Black-box acceptable**: Don't need to explain model focus"
        ]
    },

    "transformer-architecture-pattern.md": {
        "overview": "Transformer Architecture uses self-attention mechanisms to process sequences in parallel, enabling models to capture long-range dependencies efficiently. Modern LLMs (Claude, GPT-4, Gemini) are built on Transformer architecture, making this the foundation for healthcare AI summarization. Transformers excel at understanding context across entire documents and generating coherent summaries.",
        "when_to_use": [
            "**Language understanding**: Transformers power all modern LLMs for medical text processing",
            "**Long-range dependencies**: Connecting information across documents (e.g., linking diagnosis to treatment outcome)",
            "**Parallel processing**: Need fast training/inference on long sequences",
            "**State-of-the-art performance**: Transformers currently dominate NLP benchmarks",
            "**Pre-trained models**: Leverage foundation models like Claude, GPT-4, Gemini"
        ],
        "when_not_to_use": [
            "**Extremely long sequences**: Context windows have limits (though 200K-2M tokens now available)",
            "**Resource constraints**: Transformers require significant compute and memory",
            "**Simple tasks**: Traditional ML may suffice for basic classification",
            "**Real-time embedded**: Edge devices may not support large Transformer models",
            "**Cost sensitive**: Transformer inference can be expensive at scale"
        ]
    },
}

def populate_pattern(file_path: Path, content: dict):
    """Populate a single pattern file with content."""

    with open(file_path, 'r', encoding='utf-8') as f:
        current_content = f.read()

    # Build the replacement content
    overview_section = f"""## Overview

{content['overview']}"""

    when_to_use_items = '\n'.join([f"- {item}" for item in content['when_to_use']])
    when_to_use_section = f"""## When to Use

{when_to_use_items}"""

    when_not_to_use_items = '\n'.join([f"- {item}" for item in content['when_not_to_use']])
    when_not_to_use_section = f"""## When Not to Use

{when_not_to_use_items}"""

    # Replace template placeholders
    new_content = current_content.replace(
        """## Overview

[Brief description of the pattern, its purpose, and when it's commonly used]

## When to Use

- [Use case 1]
- [Use case 2]
- [Use case 3]

## When Not to Use

- [Anti-pattern or alternative scenario 1]
- [Anti-pattern or alternative scenario 2]
- [Anti-pattern or alternative scenario 3]""",
        f"""{overview_section}

{when_to_use_section}

{when_not_to_use_section}"""
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✓ Updated: {file_path.name}")

def main():
    """Main execution."""
    base_path = Path(__file__).parent.parent / "docs" / "ai-design-patterns"

    # Process Model Architecture patterns
    model_arch_path = base_path / "model-architecture"

    for filename, content in PATTERN_CONTENT.items():
        file_path = model_arch_path / filename
        if file_path.exists():
            populate_pattern(file_path, content)
        else:
            print(f"✗ Not found: {filename}")

    print(f"\nCompleted Model Architecture patterns (6/7)")
    print("Note: ensemble-pattern.md already updated manually")

if __name__ == "__main__":
    main()
