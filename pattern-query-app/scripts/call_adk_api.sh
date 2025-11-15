#!/bin/bash
# Call ADK API to generate CSV and save response

OUTPUT_FILE="/Users/sanantha/SummarizerArchitecture/pattern-query-app/adk_api_response.json"

echo "Creating new session..."

# Create a new session
SESSION_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8090/apps/gemini_agent/users/user/sessions" \
  -H "Content-Type: application/json")

echo "$SESSION_RESPONSE" | python3 -m json.tool > "${OUTPUT_FILE}.session_create"

# Extract session ID
SESSION_ID=$(echo "$SESSION_RESPONSE" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('id',''))")

if [ -z "$SESSION_ID" ]; then
  echo "❌ Failed to create session"
  exit 1
fi

echo "✅ Created session: $SESSION_ID"
echo "Sending request to ADK agent..."

# Send the message to generate CSV
curl -s -X POST "http://127.0.0.1:8090/apps/gemini_agent/users/user/sessions/${SESSION_ID}/events" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "List the Complete Techniques Catalog as CSV",
    "type": "user_message"
  }' | python3 -m json.tool > "${OUTPUT_FILE}.event"

echo "Event created. Waiting for response..."
sleep 5

# Get the session to see events
curl -s "http://127.0.0.1:8090/apps/gemini_agent/users/user/sessions/${SESSION_ID}" \
  | python3 -m json.tool > "${OUTPUT_FILE}"

echo "✅ Response saved to: ${OUTPUT_FILE}"
echo "📊 File size: $(ls -lh ${OUTPUT_FILE} | awk '{print $5}')"

# Extract event ID from the response for trace
EVENT_ID=$(python3 -c "import json; data=json.load(open('${OUTPUT_FILE}')); events=data.get('events',[]); print(events[-1]['id'] if events else '')")

if [ -n "$EVENT_ID" ]; then
  echo "📝 Event ID: $EVENT_ID"
  echo "Getting trace..."
  curl -s "http://127.0.0.1:8090/debug/trace/${EVENT_ID}" \
    | python3 -m json.tool > "${OUTPUT_FILE}.trace"
  echo "✅ Trace saved to: ${OUTPUT_FILE}.trace"
fi

# Extract CSV output from the last event
echo "Extracting CSV output..."
python3 << 'PYTHON_SCRIPT'
import json
import sys
from pathlib import Path

output_file = Path("/Users/sanantha/SummarizerArchitecture/pattern-query-app/adk_api_response.json")
csv_output_file = Path("/Users/sanantha/SummarizerArchitecture/pattern-query-app/adk_api_csv_output.csv")

try:
    with open(output_file, 'r') as f:
        session_data = json.load(f)

    events = session_data.get('events', [])
    if not events:
        print("⚠️  No events found in session")
        sys.exit(0)

    # Look for CSV in the last few events (agent response)
    for event in reversed(events):
        content = event.get('content', '')
        event_type = event.get('type', '')

        if isinstance(content, str) and len(content) > 100:
            # Check if it looks like CSV
            if ',' in content[:200] and ('\n' in content or '\r\n' in content):
                with open(csv_output_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                lines = content.count('\n')
                size = len(content)
                has_rn = '\r\n' in content
                has_n = '\n' in content

                print(f"✅ CSV extracted from event (type: {event_type})")
                print(f"   📄 File: {csv_output_file}")
                print(f"   📏 Size: {size:,} bytes")
                print(f"   📊 Lines: {lines}")
                if has_rn:
                    rn_count = content.count('\r\n')
                    print(f"   ✅ Windows-style line breaks (\\r\\n): {rn_count}")
                elif has_n:
                    n_count = content.count('\n')
                    print(f"   ✅ Unix-style line breaks (\\n): {n_count}")

                print(f"\n   First 300 chars:")
                print(f"   {repr(content[:300])}")
                sys.exit(0)

    print("⚠️  No CSV content found in events")
    print(f"   Found {len(events)} events")
    for i, event in enumerate(events):
        print(f"   Event {i+1}: type={event.get('type')}, content length={len(str(event.get('content', '')))}")

except Exception as e:
    print(f"❌ Error extracting CSV: {e}")
    sys.exit(1)
PYTHON_SCRIPT

echo ""
echo "📁 Session ID: $SESSION_ID"
