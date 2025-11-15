#!/usr/bin/env python3
"""
Make API call through ADK agent and save the CSV response.
Uses the proper ADK REST API endpoints.
"""

import requests
import json
import time
from pathlib import Path

# ADK server configuration
ADK_URL = "http://127.0.0.1:8090"
APP_NAME = "gemini_agent"
USER_ID = "user"

def create_session():
    """Create a new session."""
    url = f"{ADK_URL}/apps/{APP_NAME}/users/{USER_ID}/sessions"
    response = requests.post(url)
    response.raise_for_status()
    session_data = response.json()
    session_id = session_data["id"]
    print(f"✅ Created session: {session_id}")
    return session_id

def send_message_sse(session_id: str, message: str):
    """Send a message using the /run_sse endpoint."""
    url = f"{ADK_URL}/run_sse"

    payload = {
        "app_name": APP_NAME,
        "user_id": USER_ID,
        "session_id": session_id,
        "content": message
    }

    print(f"📤 Sending message: {message}")

    # The /run_sse endpoint uses Server-Sent Events (SSE)
    response = requests.post(url, json=payload, stream=True)
    response.raise_for_status()

    # Collect SSE events
    events = []
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            print(f"  SSE: {decoded_line[:100]}...")
            if decoded_line.startswith('data: '):
                data = decoded_line[6:]  # Remove 'data: ' prefix
                if data and data != '[DONE]':
                    try:
                        events.append(json.loads(data))
                    except json.JSONDecodeError:
                        pass

    return events

def get_session_data(session_id: str):
    """Get the full session data including all events."""
    url = f"{ADK_URL}/apps/{APP_NAME}/users/{USER_ID}/sessions/{session_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def main():
    output_dir = Path(__file__).parent.parent

    # Create a new session
    session_id = create_session()

    # Send the CSV generation request
    message = "List the Complete Techniques Catalog as CSV"
    sse_events = send_message_sse(session_id, message)

    # Save SSE events
    sse_file = output_dir / "adk_sse_events.json"
    with open(sse_file, 'w') as f:
        json.dump(sse_events, f, indent=2, default=str)
    print(f"✅ SSE events saved to: {sse_file}")

    # Wait a bit for processing to complete
    print("⏳ Waiting for processing...")
    time.sleep(3)

    # Get the full session data
    session_data = get_session_data(session_id)

    # Save session data
    session_file = output_dir / "adk_session_response.json"
    with open(session_file, 'w') as f:
        json.dump(session_data, f, indent=2, default=str)
    print(f"✅ Session data saved to: {session_file}")
    print(f"📊 Session has {len(session_data.get('events', []))} events")

    # Extract and display the CSV output if present
    events = session_data.get('events', [])
    if events:
        last_event = events[-1]
        print(f"\n📋 Last event type: {last_event.get('type', 'unknown')}")

        # Look for CSV in the content or data field
        content = last_event.get('content', '')
        if isinstance(content, str) and len(content) > 0:
            # Check if it's CSV (has commas and quotes)
            if ',' in content[:200] and '"' in content[:200]:
                # Save CSV to file
                csv_file = output_dir / "adk_generated_output.csv"
                with open(csv_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                # Count lines
                lines = content.count('\n')
                size = len(content)

                print(f"\n✅ CSV output extracted:")
                print(f"   📄 File: {csv_file}")
                print(f"   📏 Size: {size} bytes")
                print(f"   📊 Lines: {lines}")
                print(f"\n   First 300 chars:\n{repr(content[:300])}")

                # Verify line breaks
                if '\r\n' in content:
                    print(f"   ✅ Contains Windows-style line breaks (\\r\\n)")
                elif '\n' in content:
                    print(f"   ✅ Contains Unix-style line breaks (\\n)")
                else:
                    print(f"   ⚠️  No line breaks detected!")
            else:
                print(f"\n   Content (first 500 chars): {content[:500]}")

    print(f"\n📁 Session ID: {session_id}")
    print(f"🔗 View in UI: {ADK_URL}/dev-ui/")

if __name__ == "__main__":
    main()
