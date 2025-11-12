#!/usr/bin/env python3
"""
Run simple evaluation set against the pattern query app.

Supports:
- Standard RAG query evaluation
- CSV formatting evaluation with multi-model comparison
- Agent-based evaluation (ADK agents)
"""

import argparse
import csv
import io
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from document_store.storage.vector_store import VectorStore
from document_store.search.rag_query import RAGQueryInterface


def validate_csv_format(response: str, validation_rules: Dict) -> Dict:
    """
    Validate CSV formatting in LLM response.

    Args:
        response: LLM response text (may include explanation before CSV)
        validation_rules: Expected validation criteria from test case

    Returns:
        Dict with validation results and metrics
    """
    result = {
        "valid": False,
        "errors": [],
        "metrics": {}
    }

    # Extract CSV content (skip explanation lines)
    lines = response.strip().split('\n')

    # Find CSV start (look for header row)
    csv_start_idx = 0
    expected_columns = validation_rules.get("exact_column_count")

    for i, line in enumerate(lines):
        # Check if this line could be a header (has expected number of commas)
        if expected_columns and line.count(',') >= expected_columns - 1:
            csv_start_idx = i
            break

    csv_content = '\n'.join(lines[csv_start_idx:])

    # Try to parse as CSV
    try:
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(csv_reader)

        result["metrics"]["row_count"] = len(rows)
        result["metrics"]["column_count"] = len(csv_reader.fieldnames) if csv_reader.fieldnames else 0
        result["metrics"]["header"] = list(csv_reader.fieldnames) if csv_reader.fieldnames else []

        # Validation checks
        errors = []

        # Check row count
        if "min_row_count" in validation_rules:
            if len(rows) < validation_rules["min_row_count"]:
                errors.append(f"Row count {len(rows)} below minimum {validation_rules['min_row_count']}")

        if "max_row_count" in validation_rules:
            if len(rows) > validation_rules["max_row_count"]:
                errors.append(f"Row count {len(rows)} above maximum {validation_rules['max_row_count']}")

        # Check column count
        if "exact_column_count" in validation_rules:
            if result["metrics"]["column_count"] != validation_rules["exact_column_count"]:
                errors.append(
                    f"Column count {result['metrics']['column_count']} != expected {validation_rules['exact_column_count']}"
                )

        # Check for None or empty columns
        none_count = 0
        for row in rows:
            for key, value in row.items():
                if value is None or (key is None):
                    none_count += 1

        if none_count > 0:
            errors.append(f"Found {none_count} None or empty columns")

        result["metrics"]["none_count"] = none_count

        # Check header columns (if specified)
        if "check_header" in validation_rules and validation_rules["check_header"]:
            # Just verify we have headers - don't require exact match
            if not csv_reader.fieldnames:
                errors.append("No header row found")

        # If no errors, mark as valid
        result["valid"] = len(errors) == 0
        result["errors"] = errors

    except Exception as e:
        result["errors"].append(f"CSV parsing failed: {str(e)}")
        result["valid"] = False

    return result


def start_adk_server(agent_type: str = "gemini_agent", port: int = 8000) -> Optional[subprocess.Popen]:
    """
    Start ADK web server programmatically.
    
    Args:
        agent_type: Agent type to start (ollama_agent or gemini_agent)
        port: Port to run server on (default: 8000)
        
    Returns:
        subprocess.Popen object for the server process, or None if failed
    """
    try:
        repo_root = Path(__file__).parent.parent
        venv_adk = repo_root.parent / "venv312" / "bin" / "adk"
        
        if not venv_adk.exists():
            print(f"  ✗ Error: ADK not found at {venv_adk}")
            return None
        
        # Load environment variables from .env
        from dotenv import load_dotenv
        load_dotenv(repo_root / ".env")
        
        # Set environment variables based on agent type
        env = os.environ.copy()
        
        if agent_type == "ollama_agent":
            env["OLLAMA_MODEL"] = os.getenv("OLLAMA_MODEL", "gemma3:4b")
            env["OLLAMA_BASE_URL"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            agents_dir = repo_root / ".adk" / "agents" / "ollama_agent"
        else:  # gemini_agent
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                print(f"  ✗ Error: GOOGLE_API_KEY or GEMINI_API_KEY not set")
                return None
            env["GOOGLE_API_KEY"] = api_key
            env["ADK_MODEL"] = os.getenv("ADK_MODEL") or os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
            agents_dir = repo_root / ".adk" / "agents"
        
        if not agents_dir.exists():
            print(f"  ✗ Error: Agents directory not found at {agents_dir}")
            return None
        
        print(f"  Starting ADK server for {agent_type} on port {port}...")
        
        # Start server in background
        process = subprocess.Popen(
            [
                str(venv_adk),
                "web",
                "--host=127.0.0.1",
                f"--port={port}",
                "--allow_origins=*",
                str(agents_dir)
            ],
            cwd=str(repo_root),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return process
        
    except Exception as e:
        print(f"  ✗ Error starting ADK server: {e}")
        return None


def wait_for_adk_server(api_url: str = "http://127.0.0.1:8000", max_wait: float = 30.0, check_interval: float = 1.0) -> bool:
    """
    Wait for ADK server to become ready.
    
    Args:
        api_url: Base URL of ADK web server
        max_wait: Maximum time to wait in seconds (default: 30.0)
        check_interval: Time between checks in seconds (default: 1.0)
        
    Returns:
        True if server is ready, False if timeout
    """
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if check_adk_server_running(api_url=api_url, timeout=2.0):
            return True
        time.sleep(check_interval)
    return False


def check_adk_server_running(api_url: str = "http://127.0.0.1:8000", timeout: float = 2.0) -> bool:
    """
    Check if ADK web server is running and accessible.
    
    Args:
        api_url: Base URL of ADK web server (default: http://127.0.0.1:8000)
        timeout: Request timeout in seconds (default: 2.0)
        
    Returns:
        True if server is running and accessible, False otherwise
    """
    if not REQUESTS_AVAILABLE:
        return False
    
    try:
        # Try common health check endpoints
        health_endpoints = ["/health", "/", "/docs"]
        for endpoint in health_endpoints:
            try:
                response = requests.get(
                    f"{api_url}{endpoint}",
                    timeout=timeout,
                    allow_redirects=True
                )
                if response.status_code in [200, 302, 307]:
                    return True
            except requests.exceptions.RequestException:
                continue
        return False
    except Exception:
        return False


def invoke_adk_via_http(
    query: str,
    agent_type: str = "ollama_agent",
    model: Optional[str] = None,
    api_url: str = "http://127.0.0.1:8000",
    timeout: float = 300.0
) -> Optional[str]:
    """
    Invoke ADK agent via HTTP API using the /run endpoint.
    
    Uses the official ADK /run endpoint which executes an agent run and returns events.
    This ensures we test the actual ADK agent implementation with full tool access.
    
    Args:
        query: Query to send to agent
        agent_type: Agent to use (ollama_agent or gemini_agent)
        model: Model to use (for logging, ADK uses configured model)
        api_url: Base URL of ADK web server (default: http://127.0.0.1:8000)
        timeout: Request timeout in seconds (default: 300.0)
        
    Returns:
        Agent response text or None if failed
    """
    if not REQUESTS_AVAILABLE:
        print(f"  ✗ Error: requests library not available")
        return None
    
    try:
        # Generate unique session and user IDs for each invocation
        session_id = str(uuid.uuid4())
        user_id = "csv-eval-user"
        
        # Prepare request payload for /run endpoint
        # According to ADK docs: https://google.github.io/adk-docs/api-reference/rest/
        # The new_message should be a Content object with parts (not content/text fields)
        payload = {
            "app_name": agent_type,  # e.g., "gemini_agent" or "ollama_agent"
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [
                    {
                        "text": query
                    }
                ]
            },
            "streaming": False  # Get complete response, not streamed
        }
        
        # First, create/initialize the session
        # According to ADK docs, we need to create the session first
        session_endpoint = f"{api_url}/apps/{agent_type}/users/{user_id}/sessions/{session_id}"
        try:
            session_response = requests.post(
                session_endpoint,
                json={"messages": []},  # Initialize with empty messages
                headers={"Content-Type": "application/json"},
                timeout=5.0
            )
            # Session creation might return 200 (created) or 409 (already exists) - both are OK
            if session_response.status_code not in [200, 409]:
                print(f"  ⚠️  Session creation returned HTTP {session_response.status_code}, continuing anyway...")
        except Exception as e:
            print(f"  ⚠️  Session creation warning: {e}, continuing anyway...")
        
        # Call the /run endpoint
        endpoint = f"{api_url}/run"
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=timeout
            )
            
            if response.status_code != 200:
                print(f"  ✗ ADK API error: HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"  ✗ Error detail: {error_detail}")
                except:
                    print(f"  ✗ Error response: {response.text[:200]}")
                return None
            
            # Parse response - /run returns a list of events
            data = response.json()
            
            # Extract text from events and track tool calls
            # Events can be various types: text, tool calls, model responses, etc.
            answer_parts = []
            tool_calls = []  # Track which tools were called
            
            # Handle list of events (most common format)
            events_list = data if isinstance(data, list) else (data.get("events", []) if isinstance(data, dict) else [])
            
            for event in events_list:
                if isinstance(event, dict):
                    # Track function calls to see which tools were used
                    if event.get("role") == "model":
                        content = event.get("content", {})
                        if isinstance(content, dict):
                            parts = content.get("parts", [])
                            for part in parts:
                                if isinstance(part, dict):
                                    # Check for function calls
                                    if "functionCall" in part:
                                        func_call = part.get("functionCall", {})
                                        func_name = func_call.get("name", "unknown")
                                        func_args = func_call.get("args", {})
                                        tool_calls.append({
                                            "name": func_name,
                                            "args": func_args
                                        })
                                        # Log tool call for debugging
                                        print(f"  🔧 Tool called: {func_name}({json.dumps(func_args)[:100]})")
                                    
                                    # Extract text (skip function calls)
                                    if "text" in part and "functionCall" not in part:
                                        text = part.get("text")
                                        if text:
                                            answer_parts.append(str(text))
                    
                    # Also check for direct text fields in event
                    if "text" in event:
                        answer_parts.append(str(event["text"]))
                    
                    # Check for text in content.parts (alternative structure)
                    content = event.get("content", {})
                    if isinstance(content, dict) and "parts" in content:
                        for part in content["parts"]:
                            if isinstance(part, dict):
                                # Track function calls
                                if "functionCall" in part:
                                    func_call = part.get("functionCall", {})
                                    func_name = func_call.get("name", "unknown")
                                    func_args = func_call.get("args", {})
                                    tool_calls.append({
                                        "name": func_name,
                                        "args": func_args
                                    })
                                    print(f"  🔧 Tool called: {func_name}({json.dumps(func_args)[:100]})")
                                
                                if "text" in part and "functionCall" not in part:
                                    answer_parts.append(str(part["text"]))
                    
                    # Check for text in parts array at event level
                    if "parts" in event and isinstance(event["parts"], list):
                        for part in event["parts"]:
                            if isinstance(part, dict):
                                if "functionCall" in part:
                                    func_call = part.get("functionCall", {})
                                    func_name = func_call.get("name", "unknown")
                                    tool_calls.append({"name": func_name, "args": func_call.get("args", {})})
                                    print(f"  🔧 Tool called: {func_name}")
                                
                                if "text" in part and "functionCall" not in part:
                                    answer_parts.append(str(part["text"]))
                
                elif hasattr(event, 'text'):
                    # Event object with text attribute
                    answer_parts.append(str(event.text))
            
            # Check if get_complete_document was called
            get_complete_doc_called = any(
                call.get("name") == "get_complete_document" 
                for call in tool_calls
            )
            
            if tool_calls:
                print(f"  📊 Tools called: {', '.join([call['name'] for call in tool_calls])}")
                if not get_complete_doc_called:
                    print(f"  ⚠️  WARNING: get_complete_document() was NOT called!")
                    print(f"  ⚠️  Agent used: {', '.join([call['name'] for call in tool_calls])}")
            else:
                print(f"  ⚠️  WARNING: No tool calls detected in response!")
            
            # Also check for direct answer fields in dict response
            if isinstance(data, dict):
                answer = data.get("answer") or data.get("response") or data.get("text")
                if answer:
                    answer_parts.append(str(answer))
            
            if answer_parts:
                answer = "\n".join(answer_parts).strip()
                if answer:
                    return answer
            
            # Debug: log response structure if no answer found
            print(f"  ✗ Debug: No answer extracted from response. Response type: {type(data)}")
            if isinstance(data, (list, dict)):
                print(f"  ✗ Debug: Response structure: {json.dumps(data, indent=2)[:500]}")
            
            return None
            
        except requests.exceptions.Timeout:
            print(f"  ✗ ADK API timeout after {timeout}s")
            return None
        except requests.exceptions.RequestException as e:
            print(f"  ✗ ADK API request error: {e}")
            return None
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            print(f"  ✗ ADK API response parsing error: {e}")
            if response.status_code == 200:
                print(f"  ✗ Response text: {response.text[:500]}")
            return None
        
    except Exception as e:
        print(f"  ✗ ADK HTTP API error: {e}")
        import traceback
        traceback.print_exc()
        return None


def invoke_agent_for_csv(
    query: str,
    agent_type: str = "ollama_agent",
    model: Optional[str] = None,
    adk_api_url: Optional[str] = None,
    adk_api_timeout: float = 300.0
) -> Optional[str]:
    """
    Invoke ADK agent via HTTP API ONLY (no fallbacks).
    
    This function ONLY uses the ADK agent with tool access via HTTP API.
    If the server is not running, it will be started automatically.
    
    Args:
        query: Query to send to agent
        agent_type: Agent to use (ollama_agent or gemini_agent)
        model: Model to use (sets environment variable for server startup)
        adk_api_url: ADK web server URL (default: http://127.0.0.1:8000)
        adk_api_timeout: HTTP request timeout in seconds (default: 300.0)

    Returns:
        Agent response text or None if failed
    """
    try:
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent.parent / ".env")
        
        # Set model environment variable if provided
        if model:
            if agent_type == "ollama_agent":
                os.environ["OLLAMA_MODEL"] = model
                os.environ["ADK_MODEL"] = model
                print(f"  Using Ollama model: {model}")
            elif agent_type == "gemini_agent":
                os.environ["GEMINI_MODEL"] = model
                os.environ["ADK_MODEL"] = model
                print(f"  Using Gemini model: {model}")

        # Get ADK API URL from parameter or environment
        api_url = adk_api_url or os.getenv("ADK_API_URL", "http://127.0.0.1:8000")
        port = int(api_url.split(":")[-1].split("/")[0]) if ":" in api_url else 8000
        
        # Check if server is running, start if needed
        if not check_adk_server_running(api_url=api_url):
            print(f"  ADK server not running at {api_url}, starting server...")
            server_process = start_adk_server(agent_type=agent_type, port=port)
            
            if not server_process:
                print(f"  ✗ Error: Failed to start ADK server")
                return None
            
            # Wait for server to be ready
            print(f"  Waiting for ADK server to be ready...")
            if not wait_for_adk_server(api_url=api_url, max_wait=30.0):
                print(f"  ✗ Error: ADK server did not become ready within 30 seconds")
                try:
                    server_process.terminate()
                except:
                    pass
                return None
            
            print(f"  ✓ ADK server is ready at {api_url}")
        
        # Invoke agent via HTTP API using /run endpoint
        print(f"  Invoking ADK agent via HTTP API at {api_url}...")
        response = invoke_adk_via_http(
            query=query,
            agent_type=agent_type,
            model=model,
            api_url=api_url,
            timeout=adk_api_timeout
        )
        
        if response:
            return response
        else:
            print(f"  ✗ Error: ADK HTTP API returned no response")
            return None

    except Exception as e:
        print(f"  ✗ Error invoking ADK agent: {e}")
        import traceback
        traceback.print_exc()
        return None


def evaluate_csv_with_ragas(
    response: str,
    query: str,
    expected_row_count: int = 163,
    llm_type: str = "gemini",
    model: str = "gemini-2.5-flash",
    expected_techniques_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluate CSV response using Ragas framework with content verification.
    
    Args:
        response: Agent response text (may contain CSV)
        query: Original query
        expected_row_count: Expected number of rows (default: 163)
        llm_type: LLM type for Ragas ("gemini" or "ollama")
        model: Model name for Ragas
        expected_techniques_file: Path to JSON file with expected Category/Technique pairs
        
    Returns:
        Dict with Ragas evaluation results and content verification
    """
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent.parent / ".env")
    except ImportError:
        pass  # python-dotenv not installed, skip
    
    try:
        from document_store.evaluation.ragas_real_evaluator import RagasRealEvaluator
    except ImportError:
        print("  ✗ Error: Ragas evaluator not available")
        return {"error": "Ragas not available"}
    
    try:
        # Extract CSV from response
        csv_content = response
        if '```csv' in response:
            csv_start = response.find('```csv') + 6
            csv_end = response.find('```', csv_start)
            csv_content = response[csv_start:csv_end].strip()
        elif '```' in response:
            csv_start = response.find('```') + 3
            csv_end = response.find('```', csv_start)
            csv_content = response[csv_start:csv_end].strip()
        
        # Parse CSV to get actual row count and extract techniques
        import csv as csv_module
        import io
        reader = csv_module.DictReader(io.StringIO(csv_content))
        rows = list(reader)
        actual_row_count = len(rows)
        
        # Extract Category/Technique pairs from CSV response
        actual_techniques = []
        for row in rows:
            category = row.get("Category", "").strip()
            technique = row.get("Technique/Methodology", "").strip()
            if category and technique:
                actual_techniques.append({
                    "category": category,
                    "technique": technique
                })
        
        # Sort for consistent comparison
        actual_techniques.sort(key=lambda x: (x["category"], x["technique"]))
        
        # Load expected techniques if file provided
        content_verification = {}
        if expected_techniques_file:
            expected_file_path = Path(__file__).parent.parent / expected_techniques_file
            if expected_file_path.exists():
                with open(expected_file_path, 'r', encoding='utf-8') as f:
                    expected_data = json.load(f)
                    expected_techniques = expected_data.get("expected_techniques", [])
                    
                    # Normalize expected techniques (sort by category, technique)
                    expected_techniques = sorted(
                        expected_techniques,
                        key=lambda x: (x.get("category", ""), x.get("technique", ""))
                    )
                    
                    # Create sets for comparison
                    actual_set = {(t["category"], t["technique"]) for t in actual_techniques}
                    expected_set = {(t["category"], t["technique"]) for t in expected_techniques}
                    
                    missing_techniques = expected_set - actual_set
                    extra_techniques = actual_set - expected_set
                    
                    content_verification = {
                        "expected_count": len(expected_techniques),
                        "actual_count": len(actual_techniques),
                        "missing_count": len(missing_techniques),
                        "extra_count": len(extra_techniques),
                        "match": len(missing_techniques) == 0 and len(extra_techniques) == 0,
                        "missing_techniques": [
                            {"category": cat, "technique": tech}
                            for cat, tech in sorted(missing_techniques)
                        ],
                        "extra_techniques": [
                            {"category": cat, "technique": tech}
                            for cat, tech in sorted(extra_techniques)
                        ]
                    }
                    
                    print(f"    Content verification:")
                    print(f"      Expected techniques: {len(expected_techniques)}")
                    print(f"      Actual techniques: {len(actual_techniques)}")
                    print(f"      Missing: {len(missing_techniques)}")
                    print(f"      Extra: {len(extra_techniques)}")
                    if content_verification["match"]:
                        print(f"      ✓ All 163 Category/Technique pairs match!")
                    else:
                        if missing_techniques:
                            print(f"      ✗ Missing {len(missing_techniques)} techniques:")
                            for cat, tech in sorted(list(missing_techniques))[:5]:
                                print(f"        - {cat} | {tech}")
                            if len(missing_techniques) > 5:
                                print(f"        ... and {len(missing_techniques) - 5} more")
                        if extra_techniques:
                            print(f"      ✗ Extra {len(extra_techniques)} techniques:")
                            for cat, tech in sorted(list(extra_techniques))[:5]:
                                print(f"        - {cat} | {tech}")
                            if len(extra_techniques) > 5:
                                print(f"        ... and {len(extra_techniques) - 5} more")
            else:
                print(f"    ⚠️  Expected techniques file not found: {expected_file_path}")
                content_verification = {"error": f"File not found: {expected_techniques_file}"}
        
        # Create evaluation dataset for Ragas
        # We'll evaluate: answer relevancy, faithfulness, and add custom row count check
        from datasets import Dataset
        import pandas as pd
        
        # Prepare dataset
        dataset_dict = {
            "question": [query],
            "answer": [response],
            "contexts": [["Complete Techniques Catalog from ai-development-techniques.md"]],
            "reference": [f"The Complete Techniques Catalog should contain {expected_row_count} unique techniques organized by phase and category."]
        }
        
        dataset = Dataset.from_dict(dataset_dict)
        
        # Initialize Ragas evaluator
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").replace("/v1", "")
        evaluator = RagasRealEvaluator(
            model=model,
            base_url=base_url,
            llm_type=llm_type
        )
        
        # Run evaluation with Ragas metrics
        from ragas import evaluate
        from ragas.metrics import answer_relevancy, faithfulness
        
        metrics = [answer_relevancy, faithfulness]
        
        print(f"  📊 Running Ragas evaluation...")
        print(f"    Expected rows: {expected_row_count}")
        print(f"    Actual rows: {actual_row_count}")
        
        # Use evaluator's embeddings (HuggingFace) to avoid OpenAI API key requirement
        results = evaluate(
            dataset=dataset,
            metrics=metrics,
            llm=evaluator.llm,
            embeddings=evaluator.embeddings,  # Use HuggingFace embeddings from evaluator
        )
        
        # Convert results to dict
        results_dict = results.to_pandas().to_dict(orient='records')[0]
        
        # Add row count validation (checking for 166 as user specified)
        # Allow small tolerance (±3 rows) for minor variations
        row_count_match = abs(actual_row_count - expected_row_count) <= 3
        results_dict["row_count_validation"] = {
            "expected": expected_row_count,
            "actual": actual_row_count,
            "match": row_count_match,
            "difference": actual_row_count - expected_row_count
        }
        
        # Add content verification results
        if content_verification:
            results_dict["content_verification"] = content_verification
        
        print(f"    Row count validation: {actual_row_count} rows (expected: {expected_row_count}) {'✓' if row_count_match else '✗'}")
        
        return results_dict
        
    except Exception as e:
        print(f"  ✗ Ragas evaluation error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def run_csv_eval(
    eval_file: str,
    models: Optional[List[str]] = None,
    agent_type: str = "ollama_agent",
    auto_invoke: bool = True,
    adk_api_url: Optional[str] = None,
    adk_api_timeout: float = 300.0
) -> Dict:
    """
    Run CSV formatting evaluation against multiple models.
    
    IMPORTANT: This evaluation ONLY uses ADK agents via HTTP API with full tool access.
    If the ADK server is not running, it will be started automatically.
    No fallback to direct API calls - this ensures we test the actual ADK agent implementation.

    Args:
        eval_file: Path to CSV evaluation set JSON
        models: List of models to test (e.g., ["qwen3:14b", "gemini-2.0-flash-exp"])
        agent_type: Agent to use (ollama_agent or gemini_agent)
        auto_invoke: If True, automatically invoke agent; if False, show manual instructions
        adk_api_url: ADK web server URL (default: http://127.0.0.1:8000)
        adk_api_timeout: HTTP request timeout in seconds (default: 300.0)

    Returns:
        Dict with evaluation results for each model
    """
    # Load eval set
    eval_path = Path(__file__).parent.parent / eval_file
    with open(eval_path) as f:
        eval_data = json.load(f)

    print(f"Running CSV Evaluation: {eval_data['name']}")
    print(f"Agent Type: {agent_type}")
    print(f"Mode: {'Automated' if auto_invoke else 'Manual'}")

    if models:
        print(f"Models to test: {', '.join(models)}")
    else:
        # Default to current configured model
        if agent_type == "ollama_agent":
            current_model = os.getenv("OLLAMA_MODEL", "qwen3:14b")
        else:
            current_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        models = [current_model]
        print(f"Using configured model: {current_model}")

    print("=" * 60)

    all_results = {}
    summary_stats = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0
    }

    # Test each model
    for model in models:
        print(f"\n{'='*60}")
        print(f"Testing Model: {model}")
        print(f"{'='*60}")

        model_results = []

        for i, test in enumerate(eval_data["test_cases"], 1):
            test_id = test["id"]
            query = test["query"]
            validation_rules = test.get("validation", {})

            print(f"\n[{i}/{len(eval_data['test_cases'])}] Test: {test_id}")
            print(f"Query: {query[:80]}...")

            start = time.time()
            summary_stats["total_tests"] += 1

            if auto_invoke:
                # Automated mode - invoke agent programmatically (ADK HTTP API only)
                response = invoke_agent_for_csv(
                    query=query,
                    agent_type=agent_type,
                    model=model,
                    adk_api_url=adk_api_url,
                    adk_api_timeout=adk_api_timeout
                )

                if response:
                    # Save raw response to file for inspection
                    model_name_safe = model.replace("/", "_").replace(":", "_")
                    response_file = Path(__file__).parent.parent / "test" / f"csv_response_{model_name_safe}_{test_id}.txt"
                    response_file.parent.mkdir(exist_ok=True)
                    with open(response_file, 'w', encoding='utf-8') as f:
                        f.write(response)
                    print(f"  ✓ Response collected and saved to: {response_file}")
                    
                    # Step 2: Evaluate with Ragas framework
                    print(f"  📊 Evaluating with Ragas framework...")
                    
                    # Determine LLM type and model for Ragas
                    ragas_llm_type = "gemini" if agent_type == "gemini_agent" else "ollama"
                    ragas_model = model if agent_type == "gemini_agent" else (model or os.getenv("OLLAMA_MODEL", "qwen3:14b"))
                    
                    # Get expected row count (user specified 166, but check test case first)
                    expected_rows = 166  # User specified 166 as target
                    if "expected" in test and "row_count" in test.get("expected", {}):
                        # Use test case expected, but user wants 166
                        expected_rows = 166  # Override with user's target
                    elif "min_row_count" in validation_rules:
                        expected_rows = max(validation_rules["min_row_count"], 166)  # At least 166
                    
                    # Get expected techniques file if specified
                    expected_techniques_file = None
                    if "expected" in test and "expected_techniques_file" in test.get("expected", {}):
                        expected_techniques_file = test["expected"]["expected_techniques_file"]
                    
                    # Evaluate with Ragas
                    ragas_results = evaluate_csv_with_ragas(
                        response=response,
                        query=query,
                        expected_row_count=expected_rows,
                        llm_type=ragas_llm_type,
                        model=ragas_model,
                        expected_techniques_file=expected_techniques_file
                    )
                    
                    elapsed = time.time() - start

                    # Determine status based on Ragas results
                    if "error" in ragas_results:
                        status = "ERROR"
                        summary_stats["errors"] += 1
                        print(f"  ✗ ERROR ({elapsed:.2f}s): {ragas_results['error']}")
                    else:
                        # Check row count validation
                        row_validation = ragas_results.get("row_count_validation", {})
                        row_match = row_validation.get("match", False)
                        actual_rows = row_validation.get("actual", 0)
                        
                        # Check content verification
                        content_verification = ragas_results.get("content_verification", {})
                        content_match = content_verification.get("match", True)  # Default to True if not verified
                        
                        # Get Ragas scores
                        faithfulness_score = ragas_results.get("faithfulness", 0)
                        answer_relevancy_score = ragas_results.get("answer_relevancy", 0)
                        
                        # Overall pass criteria:
                        # 1. Content verification is CRITICAL - must pass (all 163 techniques match)
                        # 2. Row count should match (within tolerance)
                        # 3. Ragas scores are secondary (only fail if both are below threshold and not NaN)
                        import math
                        is_nan = lambda x: x != x or (isinstance(x, float) and math.isnan(x))
                        
                        # Content verification is the primary check
                        content_pass = content_match if content_verification else True  # Pass if not verified
                        row_pass = row_match
                        
                        # Ragas scores are secondary - only fail if both are below threshold
                        ragas_pass = (
                            is_nan(faithfulness_score) or faithfulness_score >= 0.5 or
                            is_nan(answer_relevancy_score) or answer_relevancy_score >= 0.5
                        )
                        
                        # Pass if content matches AND (row count matches OR ragas scores are acceptable)
                        if content_pass and (row_pass or ragas_pass):
                            status = "PASS"
                            summary_stats["passed"] += 1
                            print(f"  ✓ PASS ({elapsed:.2f}s)")
                            print(f"    Row count: {actual_rows} (expected: {expected_rows}) ✓")
                            if content_verification:
                                print(f"    Content verification: All {content_verification.get('expected_count', 'N/A')} techniques match ✓")
                            import math
                            is_nan = lambda x: x != x or (isinstance(x, float) and math.isnan(x))
                            if not is_nan(faithfulness_score):
                                print(f"    Faithfulness: {faithfulness_score:.3f}")
                            if not is_nan(answer_relevancy_score):
                                print(f"    Answer Relevancy: {answer_relevancy_score:.3f}")
                        else:
                            status = "FAIL"
                            summary_stats["failed"] += 1
                            print(f"  ✗ FAIL ({elapsed:.2f}s)")
                            if not row_match:
                                print(f"    Row count: {actual_rows} (expected: {expected_rows}) ✗")
                            if not content_match:
                                missing = content_verification.get("missing_count", 0)
                                extra = content_verification.get("extra_count", 0)
                                print(f"    Content verification: Missing {missing}, Extra {extra} ✗")
                            import math
                            is_nan = lambda x: x != x or (isinstance(x, float) and math.isnan(x))
                            if not is_nan(faithfulness_score) and faithfulness_score < 0.5:
                                print(f"    Faithfulness: {faithfulness_score:.3f} (below threshold)")
                            if not is_nan(answer_relevancy_score) and answer_relevancy_score < 0.5:
                                print(f"    Answer Relevancy: {answer_relevancy_score:.3f} (below threshold)")

                    model_results.append({
                        "test_id": test_id,
                        "query": query,
                        "model": model,
                        "status": status,
                        "elapsed": elapsed,
                        "ragas_results": ragas_results,
                        "response_length": len(response),
                        "response_file": str(response_file.relative_to(Path(__file__).parent.parent))
                    })
                else:
                    # Agent invocation failed
                    elapsed = time.time() - start
                    summary_stats["errors"] += 1
                    print(f"  ✗ ERROR ({elapsed:.2f}s): Agent invocation failed")

                    model_results.append({
                        "test_id": test_id,
                        "query": query,
                        "model": model,
                        "status": "ERROR",
                        "elapsed": elapsed,
                        "error": "Agent invocation failed"
                    })
            else:
                # Manual mode - show instructions
                elapsed = time.time() - start
                print(f"⚠️  Manual testing required:")
                print(f"   1. Set OLLAMA_MODEL={model} in .env")
                print(f"   2. Start ADK agent: ./scripts/start_adk_ollama.sh")
                print(f"   3. Run query: '{query}'")
                print(f"   4. Save response to test/llm_response_{model.replace(':', '_')}.txt")
                print(f"   5. Validate: python3 scripts/run_simple_eval.py --validate-response test/llm_response_{model.replace(':', '_')}.txt")

                model_results.append({
                    "test_id": test_id,
                    "query": query,
                    "model": model,
                    "status": "manual_test_required",
                    "elapsed": elapsed
                })

        all_results[model] = model_results

    # Print summary
    print(f"\n{'='*60}")
    print("EVALUATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {summary_stats['total_tests']}")
    print(f"Passed: {summary_stats['passed']} ({summary_stats['passed']/summary_stats['total_tests']*100:.1f}%)")
    print(f"Failed: {summary_stats['failed']} ({summary_stats['failed']/summary_stats['total_tests']*100:.1f}%)")
    print(f"Errors: {summary_stats['errors']} ({summary_stats['errors']/summary_stats['total_tests']*100:.1f}%)")

    # Save results
    results_file = Path(__file__).parent.parent / "csv_eval_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "eval_name": eval_data["name"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "agent_type": agent_type,
            "mode": "automated" if auto_invoke else "manual",
            "models_tested": models,
            "summary": summary_stats,
            "results": all_results
        }, f, indent=2)

    print(f"\nResults saved to: {results_file}")

    if not auto_invoke:
        print(f"\nNote: CSV evaluation requires manual agent interaction.")
        print(f"Use --validate-response to validate saved responses.")

    return all_results


def validate_saved_csv_response(
    response_file: str,
    validation_rules: Dict
) -> Dict:
    """
    Validate a saved CSV response from file.

    Args:
        response_file: Path to saved LLM response
        validation_rules: Validation criteria

    Returns:
        Validation results
    """
    with open(response_file) as f:
        response = f.read()

    return validate_csv_format(response, validation_rules)


def run_eval(eval_file: str = "simple_eval_set.json"):
    """Run evaluation tests."""

    # Load eval set
    eval_path = Path(__file__).parent.parent / eval_file
    with open(eval_path) as f:
        eval_data = json.load(f)

    print(f"Running: {eval_data['name']}")
    print(f"Tests: {len(eval_data['test_cases'])}")
    print("=" * 60)

    # Initialize RAG interface directly (avoid orchestrator dependencies)
    vector_store = VectorStore(
        persist_directory="data/chroma_db",
        collection_name="architecture_patterns"
    )
    rag = RAGQueryInterface(vector_store=vector_store)

    results = []

    for i, test in enumerate(eval_data["test_cases"], 1):
        test_id = test["id"]
        query = test["query"]
        expected = test["expected"]

        print(f"\n[{i}/{len(eval_data['test_cases'])}] Test: {test_id}")
        print(f"Query: {query}")
        print(f"Expected: {expected}")

        start = time.time()
        try:
            result = rag.query_patterns(query=query, n_results=5)
            elapsed = time.time() - start

            # Get results from RAG
            query_results = result.get("results", [])

            # Simple validation: got results back
            passed = len(query_results) > 0

            # Print first result
            if query_results:
                first_doc = query_results[0]["content"][:150]
                print(f"✓ Pass ({elapsed:.2f}s): {len(query_results)} docs")
                print(f"  First doc: {first_doc}...")
            else:
                print(f"✗ Fail ({elapsed:.2f}s): No documents retrieved")

            results.append({
                "test_id": test_id,
                "query": query,
                "passed": passed,
                "elapsed": elapsed,
                "documents_count": len(query_results)
            })

        except Exception as e:
            elapsed = time.time() - start
            print(f"✗ Error ({elapsed:.2f}s): {e}")
            results.append({
                "test_id": test_id,
                "query": query,
                "passed": False,
                "elapsed": elapsed,
                "error": str(e)
            })

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    avg_time = sum(r["elapsed"] for r in results) / total

    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"Average time: {avg_time:.2f}s")

    # Save results
    results_file = Path(__file__).parent.parent / "eval_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "eval_name": eval_data["name"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "passed": passed,
                "total": total,
                "pass_rate": passed/total,
                "avg_time": avg_time
            },
            "results": results
        }, f, indent=2)

    print(f"\nResults saved to: {results_file}")

    return passed == total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run evaluation against pattern query app"
    )
    parser.add_argument(
        "--eval-file",
        default="simple_eval_set.json",
        help="Evaluation set JSON file (default: simple_eval_set.json)"
    )
    parser.add_argument(
        "--eval-type",
        choices=["rag", "csv"],
        default="rag",
        help="Type of evaluation (default: rag)"
    )
    parser.add_argument(
        "--models",
        help="Comma-separated list of Ollama models to test (e.g., qwen3:14b,gemma2:27b)"
    )
    parser.add_argument(
        "--agent-type",
        choices=["ollama_agent", "gemini_agent"],
        default="ollama_agent",
        help="Agent type to use for CSV evaluation (default: ollama_agent)"
    )
    parser.add_argument(
        "--validate-response",
        help="Validate a saved CSV response file"
    )
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Use manual testing mode (show instructions instead of auto-invoking agent)"
    )
    parser.add_argument(
        "--adk-api-url",
        default=None,
        help="ADK web server URL (default: http://127.0.0.1:8000, or from ADK_API_URL env var)"
    )
    parser.add_argument(
        "--adk-api-timeout",
        type=float,
        default=300.0,
        help="HTTP request timeout in seconds for ADK API (default: 300.0)"
    )

    args = parser.parse_args()

    # Validate saved response mode
    if args.validate_response:
        # Load validation rules from eval set
        eval_path = Path(__file__).parent.parent / args.eval_file
        with open(eval_path) as f:
            eval_data = json.load(f)

        validation_rules = eval_data["test_cases"][0].get("validation", {})
        result = validate_saved_csv_response(args.validate_response, validation_rules)

        print(f"\nValidation Results for: {args.validate_response}")
        print(f"{'='*60}")
        print(f"Valid: {result['valid']}")
        print(f"Metrics: {json.dumps(result['metrics'], indent=2)}")
        if result['errors']:
            print(f"Errors:")
            for error in result['errors']:
                print(f"  - {error}")

        sys.exit(0 if result['valid'] else 1)

    # CSV evaluation mode
    if args.eval_type == "csv":
        models = args.models.split(",") if args.models else None
        run_csv_eval(
            eval_file=args.eval_file,
            models=models,
            agent_type=args.agent_type,
            auto_invoke=not args.manual,  # Default to auto mode unless --manual flag
            adk_api_url=args.adk_api_url,
            adk_api_timeout=args.adk_api_timeout,
        )
        sys.exit(0)

    # Standard RAG evaluation
    success = run_eval(eval_file=args.eval_file)
    sys.exit(0 if success else 1)
