#!/usr/bin/env python3
"""
Call ADK agent using the Python SDK Client and save CSV response.
"""

import sys
import os
import json
from pathlib import Path

# Add ADK agents to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".adk" / "agents"))

# Set environment
os.environ["GEMINI_API_KEY"] = "AIzaSyBneZu4ShIXR6mXiSAfD5FPJcnbx-vLpoc"
os.environ["GEMINI_MODEL"] = "gemini-2.5-flash"
os.environ["USE_OLLAMA_EVAL"] = "false"

from google.adk.app_client import Client

def main():
    output_dir = Path(__file__).parent.parent

    print("🔗 Connecting to ADK agent...")

    # Create client
    client = Client(
        url="http://127.0.0.1:8090",
        app_name="gemini_agent",
        user_id="user"
    )

    # Create a new session
    session = client.create_session()
    session_id = session.id
    print(f"✅ Created session: {session_id}")

    # Send the message
    message = "List the Complete Techniques Catalog as CSV"
    print(f"📤 Sending message: {message}")

    # Run the agent and collect all responses
    all_responses = []
    for response in client.run(content=message, session_id=session_id):
        print(f"  📨 Response chunk received (type: {type(response).__name__})")
        all_responses.append(response)

    print(f"✅ Received {len(all_responses)} response chunks")

    # Save all responses
    responses_file = output_dir / "adk_sdk_responses.json"
    with open(responses_file, 'w') as f:
        # Convert responses to dict for JSON serialization
        responses_data = []
        for r in all_responses:
            if hasattr(r, '__dict__'):
                responses_data.append(vars(r))
            else:
                responses_data.append(str(r))
        json.dump(responses_data, f, indent=2, default=str)
    print(f"✅ Responses saved to: {responses_file}")

    # Get the session to see all events
    session_data = client.get_session(session_id)
    print(f"📊 Session has {len(session_data.events)} events")

    # Save session data
    session_file = output_dir / "adk_sdk_session.json"
    with open(session_file, 'w') as f:
        # Convert session to dict
        if hasattr(session_data, '__dict__'):
            session_dict = vars(session_data)
        else:
            session_dict = {"session": str(session_data)}
        json.dump(session_dict, f, indent=2, default=str)
    print(f"✅ Session data saved to: {session_file}")

    # Extract CSV output from the last response
    if all_responses:
        last_response = all_responses[-1]
        content = None

        # Try to extract content from response
        if hasattr(last_response, 'content'):
            content = last_response.content
        elif hasattr(last_response, 'text'):
            content = last_response.text
        elif hasattr(last_response, 'message'):
            content = last_response.message

        if content and isinstance(content, str):
            # Check if it looks like CSV
            if ',' in content[:200] and ('"' in content[:200] or '\n' in content[:200]):
                csv_file = output_dir / "adk_sdk_generated.csv"
                with open(csv_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                lines = content.count('\n')
                size = len(content)

                print(f"\n✅ CSV output extracted:")
                print(f"   📄 File: {csv_file}")
                print(f"   📏 Size: {size:,} bytes")
                print(f"   📊 Lines: {lines}")
                print(f"\n   First 300 chars:\n{repr(content[:300])}")

                # Verify line breaks
                if '\r\n' in content:
                    print(f"   ✅ Contains Windows-style line breaks (\\r\\n)")
                    rn_count = content.count('\r\n')
                    print(f"   📊 Total \\r\\n line breaks: {rn_count}")
                elif '\n' in content:
                    print(f"   ✅ Contains Unix-style line breaks (\\n)")
                    n_count = content.count('\n')
                    print(f"   📊 Total \\n line breaks: {n_count}")
                else:
                    print(f"   ⚠️  No line breaks detected!")
            else:
                print(f"\n   Response content (first 500 chars): {content[:500]}")
        else:
            print(f"\n   Could not extract content from response")
            print(f"   Response type: {type(last_response)}")
            print(f"   Response attributes: {dir(last_response)}")

    print(f"\n📁 Session ID: {session_id}")
    print(f"🔗 View in UI: http://127.0.0.1:8090/dev-ui/")

if __name__ == "__main__":
    main()
