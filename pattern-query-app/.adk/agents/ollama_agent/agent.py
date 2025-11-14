"""
Google ADK agent using local Ollama models.

This agent uses Ollama's OpenAI-compatible API to run models locally,
eliminating the need for cloud API keys while querying the architecture patterns.
"""

from __future__ import annotations

import os

from google.adk import Agent
from google.adk.tools import FunctionTool
from google.adk.models.lite_llm import LiteLlm

# Import shared base code
from _shared import (
    DEFAULT_INSTRUCTION,
    query_architecture_patterns,
    get_store_info,
    get_complete_document,
    generate_structured_table,
    generate_structured_list,
    generate_comparison_matrix,
)

# Ollama-specific configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:14b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
AGENT_NAME = os.getenv("ADK_AGENT_NAME", "ollama_pattern_agent")

# Set environment variables for LiteLLM to use Ollama
# LiteLLM uses OPENAI_API_BASE (not OPENAI_BASE_URL) for custom endpoints
os.environ["OPENAI_API_KEY"] = "ollama"  # Ollama doesn't need a real key
os.environ["OPENAI_API_BASE"] = OLLAMA_BASE_URL

# Create LiteLLM instance for Ollama
# LiteLLM supports Ollama via the "openai/" prefix with custom base URL
ollama_llm = LiteLlm(model=f"openai/{OLLAMA_MODEL}")

# Create ADK agent using LiteLLM with Ollama
root_agent = Agent(
    name=AGENT_NAME,
    model=ollama_llm,  # Pass LiteLlm instance directly
    instruction=os.getenv("ADK_INSTRUCTION", DEFAULT_INSTRUCTION),
    description=(
        "Answers architecture-pattern and healthcare summarization questions "
        "by retrieving content from the embedded ChromaDB vector store using "
        f"local Ollama model ({OLLAMA_MODEL} via {OLLAMA_BASE_URL})."
    ),
    tools=[
        FunctionTool(query_architecture_patterns),
        FunctionTool(get_store_info),
        FunctionTool(get_complete_document),
        FunctionTool(generate_structured_table),
        FunctionTool(generate_structured_list),
        FunctionTool(generate_comparison_matrix),
    ],
)

__all__ = ["root_agent"]
