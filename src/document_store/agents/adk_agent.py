"""
Google ADK Agent Library integration for querying architecture patterns.

This module provides agent-based querying using Google's Agent Development Kit
as the primary interface for interacting with the architecture pattern knowledge base.
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from typing import Any, Dict, List, Optional

try:
    from google.adk import Agent as GoogleADKAgent
    from google.adk.runners import InMemoryRunner
    from google.adk.tools import FunctionTool
    from google.genai import types as genai_types

    GOOGLE_ADK_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    GoogleADKAgent = None
    InMemoryRunner = None
    FunctionTool = None
    genai_types = None
    GOOGLE_ADK_AVAILABLE = False

from ..search.rag_query import RAGQueryInterface
from ..storage.vector_store import VectorStore

logger = logging.getLogger(__name__)

_DEFAULT_AGENT_INSTRUCTION = (
    "You are the Google ADK front-door for the AI Summarization Reference "
    "Architecture. Use the available `query_architecture_patterns` tool as "
    "soon as you receive a user question so you can cite the canonical ID and "
    "metadata for every recommendation. Summaries should highlight why the "
    "pattern fits the question and reference the supporting sources."
)


class ADKAgentQuery:
    """
    Google ADK Agent-based query interface for architecture patterns.
    
    Uses Google's Agent Development Kit to provide intelligent,
    agent-based querying of the architecture pattern knowledge base.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        agent_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the ADK agent query interface.
        
        Args:
            vector_store: Initialized VectorStore instance
            agent_config: Optional configuration for ADK agent
        """
        self.vector_store = vector_store
        self.rag_interface = RAGQueryInterface(vector_store)
        self.agent_config = agent_config or {}
        
        # Initialize ADK agent when available
        self.agent = self._initialize_agent()
        self._agent_name = self.agent_config.get("name", "document_store_adk_agent")
        
        logger.info("ADKAgentQuery initialized")

    def _initialize_agent(self):
        """
        Initialize the Google ADK agent.
        
        Returns:
            Initialized ADK agent instance
        """
        if not GOOGLE_ADK_AVAILABLE:
            logger.warning(
                "Google ADK not installed. Install with: pip install google-adk. "
                "Using fallback RAG interface."
            )
            return None

        try:
            config = dict(self.agent_config)
            instruction = config.pop("instruction", None) or os.getenv(
                "ADK_INSTRUCTION",
                _DEFAULT_AGENT_INSTRUCTION,
            )
            model_name = config.pop("model", None) or os.getenv(
                "ADK_MODEL",
                "gemini-2.5-flash",
            )
            tools = list(config.pop("tools", []))
            tools.append(FunctionTool(self._query_patterns_tool_function))
            config.setdefault("name", "document_store_adk_agent")
            config.setdefault(
                "description",
                "Answers architecture-pattern questions using the embedded ChromaDB knowledge base.",
            )

            config["instruction"] = instruction
            config["model"] = model_name
            config["tools"] = tools

            agent = GoogleADKAgent(**config)
            self._agent_name = getattr(agent, "name", config["name"])
            logger.info("ADK agent initialized with model %s", model_name)
            return agent
        except Exception as e:  # pragma: no cover - depends on external package
            logger.error(f"Error initializing ADK agent: {str(e)}")
            return None

    def _create_pattern_query_tool(self):
        """
        Create ADK tool for querying patterns.
        
        Returns:
            ADK Tool instance
        """
        if not GOOGLE_ADK_AVAILABLE:
            return None
        return FunctionTool(self._query_patterns_tool_function)

    def _query_patterns_tool_function(
        self,
        query: str,
        pattern_type: Optional[str] = None,
        vendor: Optional[str] = None,
        n_results: int = 5,
    ) -> Dict[str, Any]:
        """
        Tool function for ADK agent to query patterns.
        
        Args:
            query: Search query
            pattern_type: Optional pattern type filter
            vendor: Optional vendor filter
            n_results: Number of results
            
        Returns:
            Query results
        """
        rag_results = self.rag_interface.query_patterns(
            query=query,
            n_results=n_results,
            pattern_type=pattern_type,
            vendor=vendor,
        )
        return rag_results

    def query(
        self,
        query: str,
        pattern_type: Optional[str] = None,
        vendor: Optional[str] = None,
        n_results: int = 5,
        use_agent: bool = True,
    ) -> Dict[str, Any]:
        """
        Query architecture patterns using ADK agent.
        
        Args:
            query: Natural language query
            pattern_type: Optional pattern type filter
            vendor: Optional vendor filter
            n_results: Number of results to return
            use_agent: Whether to use ADK agent (fallback to direct query if False)
            
        Returns:
            Query results with agent reasoning if available
        """
        rag_payload = self.rag_interface.query_patterns(
            query=query,
            n_results=n_results,
            pattern_type=pattern_type,
            vendor=vendor,
        )

        if use_agent and self.agent is not None:
            agent_response = self._invoke_agent(
                query=query,
                pattern_type=pattern_type,
                vendor=vendor,
                n_results=n_results,
            )
            if agent_response:
                rag_payload["agent_response"] = agent_response
                return rag_payload

        # Fallback to direct RAG query only
        return rag_payload

    def agent_chat(
        self,
        messages: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Chat with ADK agent about architecture patterns.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            context: Optional context for the conversation
            
        Returns:
            Agent response with reasoning
        """
        if self.agent is None:
            raise ValueError("ADK agent not initialized. Install google-adk package.")
        
        try:
            return self._invoke_agent_chat(messages, context)
        except Exception as e:
            logger.error(f"Error in agent chat: {str(e)}")
            raise

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the ADK agent.
        
        Returns:
            Agent information dictionary
        """
        return {
            "agent_available": self.agent is not None,
            "agent_config": self.agent_config,
            "vector_store_info": self.vector_store.get_collection_info(),
        }

    def _invoke_agent(
        self,
        query: str,
        pattern_type: Optional[str],
        vendor: Optional[str],
        n_results: int,
    ) -> Optional[Dict[str, Any]]:
        if not (GOOGLE_ADK_AVAILABLE and self.agent and genai_types and InMemoryRunner):
            return None

        prompt = self._build_prompt(query, pattern_type, vendor, n_results)
        user_message = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=prompt)],
        )
        session_id = str(uuid.uuid4())

        try:
            runner = InMemoryRunner(agent=self.agent)
            events = list(
                runner.run(
                    user_id=self.agent_config.get("user_id", "architecture-docs"),
                    session_id=session_id,
                    new_message=user_message,
                    run_config=self.agent_config.get("run_config"),
                )
            )
            self._close_runner(runner)
        except Exception as exc:  # pragma: no cover - depends on external runtime
            logger.warning("ADK agent query failed: %s", exc)
            return None

        answer = self._extract_agent_answer(events)
        if not answer.strip():
            return None

        return {
            "answer": answer.strip(),
            "model": getattr(self.agent, "model", None),
            "session_id": session_id,
        }

    def _invoke_agent_chat(
        self,
        messages: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not (GOOGLE_ADK_AVAILABLE and self.agent and genai_types and InMemoryRunner):
            raise RuntimeError("Google ADK is not available in this environment.")

        session_id = str(uuid.uuid4())
        runner = InMemoryRunner(agent=self.agent)
        try:
            events: List[Any] = []
            for message in messages:
                role = message.get("role", "user")
                parts = [genai_types.Part(text=message.get("content", ""))]
                content = genai_types.Content(role=role, parts=parts)
                user_id = "architecture-docs"
                if context and isinstance(context, dict):
                    user_id = context.get("user_id", user_id)
                for event in runner.run(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=content,
                    run_config=self.agent_config.get("run_config"),
                ):
                    events.append(event)
            self._close_runner(runner)
        except Exception:
            self._close_runner(runner)
            raise

        return {
            "session_id": session_id,
            "answer": self._extract_agent_answer(events).strip(),
            "events": [self._event_to_text(event) for event in events],
        }

    def _build_prompt(
        self,
        query: str,
        pattern_type: Optional[str],
        vendor: Optional[str],
        n_results: int,
    ) -> str:
        filters = []
        filters.append(f"pattern_type: {pattern_type or 'none'}")
        filters.append(f"vendor: {vendor or 'none'}")
        filters.append(f"max_results: {n_results}")
        return (
            "Answer the user's architecture-pattern question. "
            "Use the `query_architecture_patterns` tool to retrieve context "
            "before responding and cite the ids of supporting documents.\n\n"
            f"User question:\n{query}\n\nFilters:\n- "
            + "\n- ".join(filters)
        )

    def _extract_agent_answer(self, events: List[Any]) -> str:
        if not events:
            return ""
        chunks: List[str] = []
        agent_name = getattr(self.agent, "name", self._agent_name)

        for event in events:
            if getattr(event, "author", None) != agent_name:
                continue
            if hasattr(event, "content") and event.content and getattr(event.content, "parts", None):
                if hasattr(event, "is_final_response") and event.is_final_response():
                    for part in event.content.parts:
                        text = getattr(part, "text", "")
                        if text:
                            chunks.append(text)
        return "\n".join(chunk.strip() for chunk in chunks if chunk).strip()

    def _event_to_text(self, event: Any) -> Dict[str, Any]:
        """Return a lightweight representation of an ADK event for debugging."""
        parts: List[str] = []
        if getattr(event, "content", None) and getattr(event.content, "parts", None):
            for part in event.content.parts:
                if getattr(part, "text", None):
                    parts.append(part.text)
        return {
            "author": getattr(event, "author", ""),
            "branch": getattr(event, "branch", None),
            "text": "\n".join(parts).strip(),
        }

    def _close_runner(self, runner: Any) -> None:
        if not runner:
            return

        async def _close():
            await runner.close()

        try:
            asyncio.run(_close())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(_close())
            finally:
                loop.close()
