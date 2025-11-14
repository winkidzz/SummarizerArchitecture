"""
Google ADK agent using Google Gemini cloud models.

This agent uses Google's Gemini API for high-quality responses
while querying the architecture patterns from ChromaDB.
"""

from __future__ import annotations

import os

from google.adk import Agent
from google.adk.tools import FunctionTool

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

# Gemini-specific configuration
DEFAULT_MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")
AGENT_NAME = os.getenv("ADK_AGENT_NAME", "gemini_pattern_agent")

# Create ADK agent using Google Gemini
root_agent = Agent(
    name=AGENT_NAME,
    model=DEFAULT_MODEL,
    instruction=os.getenv("ADK_INSTRUCTION", DEFAULT_INSTRUCTION),
    description=(
        "Answers architecture-pattern and healthcare summarization questions "
        "by retrieving content from the embedded ChromaDB vector store using "
        f"Google Gemini ({DEFAULT_MODEL})."
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
