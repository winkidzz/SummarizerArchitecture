"""
Script to create RAG pattern documentation files.
Extends existing pattern template and documentation structure.
"""

from pathlib import Path
import json

# RAG patterns to create (based on common strategies)
RAG_PATTERNS = [
    {
        "name": "multi-query-rag",
        "title": "Multi-Query RAG",
        "description": "Generates multiple query variations and fuses results"
    },
    {
        "name": "parent-child-rag",
        "title": "Parent-Child RAG",
        "description": "Hierarchical document chunking with parent and child relationships"
    },
    {
        "name": "agentic-rag",
        "title": "Agentic RAG",
        "description": "Agent-based retrieval and generation with tool use"
    },
    {
        "name": "adaptive-rag",
        "title": "Adaptive RAG",
        "description": "Adaptively selects retrieval strategy based on query complexity"
    },
    {
        "name": "corrective-rag",
        "title": "Corrective RAG",
        "description": "Self-correcting retrieval with feedback loops"
    },
    {
        "name": "modular-rag",
        "title": "Modular RAG",
        "description": "Composable, modular retrieval components"
    },
    {
        "name": "compressed-rag",
        "title": "Compressed RAG",
        "description": "Compresses retrieved context to fit within token limits"
    },
    {
        "name": "small-to-big-rag",
        "title": "Small-to-Big RAG",
        "description": "Progressive context expansion from small to large chunks"
    },
    {
        "name": "graph-rag",
        "title": "Graph RAG",
        "description": "Graph-based knowledge retrieval using entity relationships"
    },
    {
        "name": "reranking-rag",
        "title": "Reranking RAG",
        "description": "Multi-stage reranking for improved relevance"
    },
    {
        "name": "streaming-rag",
        "title": "Streaming RAG",
        "description": "Real-time streaming RAG for live data"
    },
    {
        "name": "recursive-rag",
        "title": "Recursive RAG",
        "description": "Recursive query decomposition and document processing"
    },
]

def create_pattern_file(pattern_info, template_path, output_dir):
    """Create a pattern documentation file from template."""
    template = Path(template_path).read_text()
    
    # Replace template placeholders
    content = template.replace("[Pattern Name]", pattern_info["title"])
    content = content.replace("Brief description of the pattern and its purpose.", 
                             pattern_info["description"])
    
    # Write to output directory
    output_file = Path(output_dir) / f"{pattern_info['name']}.md"
    output_file.write_text(content)
    print(f"Created: {output_file}")

def main():
    """Create all RAG pattern documentation files."""
    template_path = Path(__file__).parent.parent / "templates" / "pattern-template.md"
    output_dir = Path(__file__).parent.parent / "docs" / "patterns"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating RAG pattern documentation files...")
    print(f"Template: {template_path}")
    print(f"Output: {output_dir}\n")
    
    for pattern in RAG_PATTERNS:
        create_pattern_file(pattern, template_path, output_dir)
    
    print(f"\nCreated {len(RAG_PATTERNS)} pattern files successfully")
    print("Note: Please review and fill in implementation details for each pattern.")

if __name__ == "__main__":
    main()

